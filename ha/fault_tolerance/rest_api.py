import json
import signal
import ssl
import time
from abc import ABC
import traceback
from aiohttp import web, web_exceptions
import asyncio
from aiohttp.client_exceptions import ServerDisconnectedError, ClientConnectorError, ClientOSError
from asyncio import CancelledError as AsyncioCancelledError
from concurrent.futures import CancelledError as ConcurrentCancelledError, TimeoutError as ConcurrentTimeoutError

from cortx.utils.log import Log
from cortx.utils.conf_store import Conf
from ha import const
from ha.fault_tolerance.const import ERROR_CODES, SUCCESS_CODE
from ha.fault_tolerance.rest_api_errors import (CcError, CcNotFoundError, CcPermissionDenied,
                                                CcInternalError, InvalidRequest, CcNotImplemented,
                                                CcGatewayTimeout)


class Response(object):
    """Represents a response after processing of a request, Used for raising the error."""

    def __init__(self, rc=0, output=''):
        """Instantiation Method for Response class."""
        self._rc = int(rc)
        self._output = output

    def output(self):
        return self._output

    def rc(self):
        return self._rc

    def __str__(self):
        """Returns the string representation of the object."""
        return '%d: %s' % (self._rc, self._output)

class CcRestApi(ABC):

    _app = None
    _loop = None
    _site = None
    __is_shutting_down = False
    _handle_signals = True
    _signals = ('SIGINT', 'SIGTERM')

    # Test function just to check whether CC REST API server is alive
    # TODO: to be removed CORTX-30932
    @staticmethod
    async def handler_check_alive(request):
        """
        Test Handler function is added for testing purpose.
        it returns test "CORTX CC REST API server is alive."

        Args:
            request (web.Request): Request object
        Returns:
            web.Response: response object that to be sent to client
        """
        text="CORTX CC REST API server is alive."

        return Response(rc=200, output=text)

    @staticmethod
    def init(handle_signals=True) -> None:
        """
        Initialize web application and set supported routes, middlewares, etc.
        Args:
            handle_signals (bool, optional): Defaults to True.
            If handle_signals is True then signal handler will be set.
            if it is false then caller should handle the signals.
            and needs to call CcRestApi.stop() before application terminates
        """

        CcRestApi._handle_signals = handle_signals

        # Create Rest Application object and set middleware coroutine to it.
        # A middleware is a coroutine that can modify either the request or response.
        CcRestApi._app = web.Application(middlewares=[CcRestApi.rest_middleware])

        # TODO: CORTX-30932 Add routs using view classes and remove below placeholder
        # Note: Adding route '/' just to test
        CcRestApi._app.router.add_get('/', CcRestApi.handler_check_alive)

        CcRestApi._app.on_startup.append(CcRestApi._on_startup)
        CcRestApi._app.on_shutdown.append(CcRestApi._on_shutdown)

    @classmethod
    async def check_for_unsupported_endpoint(cls, request):
        """
        Check unsupported endpoints.
        Note: this function is expected to be call from middleware.
        Args:
            request (web.Request): Request object
        """
        # TODO: Add check for unsupported endpoints
        pass

    @staticmethod
    def error_response(err: Exception, **kwargs):
        """
        Create response object from input exception object.
        Args:
            err (Exception): exception object for that error response sent to be client.
        """
        resp = {
            "error_id": None,
            "error_message": None
        }

        if isinstance(err, CcError):
            resp["error_id"] = err.message_id()
            resp["error_message"] = err.error()
        elif isinstance(err, web_exceptions.HTTPError):
            resp["error_id"] = ERROR_CODES.HTTP_ERROR.value
            resp["error_message"] = str(err.reason)
        else:
            resp["error_id"] = ERROR_CODES.UNKNOWN_ERROR.value
            resp["error_message"] = f'{str(err)}'
        return resp

    @staticmethod
    def json_serializer(*args, **kwargs):
        kwargs['default'] = str
        return json.dumps(*args, **kwargs)

    @staticmethod
    def json_response(resp_obj, status=200):
        """
        Returns the the provided response object to client.
        Args:
            resp_obj (web.Response): Response object that to be sent to client.
            status (int, optional): HTTP status code. Defaults to 200.
        """
        return web.json_response(
            resp_obj, status=status, dumps=CcRestApi.json_serializer)

    @staticmethod
    @web.middleware
    async def rest_middleware(request, handler):
        """
        The 'middleware' coroutine which get called when Request is received to the server.
        Args:
            request (web.Request): Request object
            handler (handler): handler coroutine
        Returns:
            Json object: return json object that to be sent to client, ref: CcRestApi.json_response
        """
        Log.debug(f"Rest middleware is called: request = {request} handler = {handler}")
        if CcRestApi.__is_shutting_down:
            return CcRestApi.json_response("CC REST Server is shutting down", status=503)
        try:
            request_id = int(time.time())

            try:
                await CcRestApi.check_for_unsupported_endpoint(request)
            except Exception as e:
                Log.warn(f"Exception: {e}")
                CcRestApi.error_response(Exception("Invalid endpoint."))

            resp = await handler(request)

            if isinstance(resp, web.StreamResponse):
                return resp

            status = SUCCESS_CODE
            if isinstance(resp, Response):
                status = resp.rc()
                resp_obj = {'response_body': resp.output(), 'status_code': status}
                Log.info(f"Response = {resp_obj}")

                if not 200 <= status <= 299:
                    Log.error(f"Error: ({status}):{resp_obj['response_body']}")
            else:
                resp_obj = resp
                Log.info(f"Response = {resp_obj}")

            return CcRestApi.json_response(resp_obj, status)

        except (ConcurrentCancelledError, AsyncioCancelledError) as e:
            Log.warn(f"Client cancelled call for {request.method} {request.path}. Error : {e}")
            return CcRestApi.json_response(CcRestApi.error_response(Exception("Call cancelled by client"),
                                            request = request, request_id = request_id), status=499)
        # TODO : Add common REST API error structure in view.py
        except web.HTTPException as e:
            Log.error(f'HTTP Exception {e.status}: {e.reason}')
            return CcRestApi.json_response(CcRestApi.error_response(e, request = request, request_id = request_id), status=e.status)
        except InvalidRequest as e:
            Log.error(f"Error: {e} \n {traceback.format_exc()}")
            return CcRestApi.json_response(CcRestApi.error_response(e, request = request, request_id = request_id), status=400)
        except CcNotFoundError as e:
            return CcRestApi.json_response(CcRestApi.error_response(e, request = request, request_id = request_id), status=404)
        except CcPermissionDenied as e:
            return CcRestApi.json_response(CcRestApi.error_response(e, request = request, request_id = request_id), status=403)
        except CcInternalError as e:
            return CcRestApi.json_response(CcRestApi.error_response(e, request = request, request_id = request_id), status=500)
        except CcNotImplemented as e:
            return CcRestApi.json_response(CcRestApi.error_response(e, request = request, request_id = request_id), status=501)
        except CcGatewayTimeout as e:
            return CcRestApi.json_response(CcRestApi.error_response(e, request = request, request_id = request_id), status=504)
        except CcError as e:
            return CcRestApi.json_response(CcRestApi.error_response(e, request = request, request_id = request_id), status=400)
        except KeyError as e:
            Log.error(f"Error: {e} \n {traceback.format_exc()}")
            message = f"Missing Key for {e}"
            return CcRestApi.json_response(CcRestApi.error_response(KeyError(message), request = request, request_id = request_id), status=422)
        except (ServerDisconnectedError, ClientConnectorError, ClientOSError, ConcurrentTimeoutError) as e:
            return CcRestApi.json_response(CcRestApi.error_response(e, request = request, request_id = request_id), status=503)
        except Exception as e:
            Log.critical(f"Unhandled Exception Caught: {e} \n {traceback.format_exc()}")
            return CcRestApi.json_response(CcRestApi.error_response(e, request = request, request_id = request_id), status=500)


    @staticmethod
    async def _stop():
        """
        This function stops the REST Server.
        cancels all the running tasks, stops site and event loop
        """
        CcRestApi.__is_shutting_down = True
        for task in asyncio.Task.all_tasks():
            if task != asyncio.Task.current_task():
                task.cancel()
        await CcRestApi._site.stop()
        CcRestApi._loop.stop()

    @staticmethod
    async def handle_signal(signame: str):
        """
        Signal handler callback function.
        if SIGTERM, SIGINT is received it stops the REST server.
        other all are logged and ignored.
        Args:
            signame (str): Singal name which is getting handled.
        """
        Log.info(f'Received signal: {signame}: {getattr(signal, signame)}')
        if signame in ('SIGTERM', 'SIGINT'):
            await CcRestApi._stop()
        else:
            Log.info(f'Signal: {signame}: {getattr(signal, signame)} is ignored.')

    @staticmethod
    async def _on_startup(app):
        """
        This function is executes on startup of CC Rest API Server.
        Args:
            app (web.Application): web Application object which is starting.
        """
        # Note: Additional calls needs to be added to execute on startup of CC Rest API Server

    @staticmethod
    async def _on_shutdown(app):
        """
        This function is executes on shutdown of CC Rest API Server.
        Args:
            app (web.Application): web Application object which is shuting down.
        """
        # Note: Additional calls needs to be added to execute on shutdown of CC Rest API Server

    @staticmethod
    def _start_server(app, host: str=None, port: int=None, ssl_context: ssl.SSLContext=None, access_log=None):
        """
        Starts CC REST Application server.
        Sets the signal_handler if CcRestApi._handle_signal is set to true in init().
        Args:
            app (web.Application): web Application object which is starting.
            host (str, optional): CC REST API server host. Defaults to None.
            port (int, optional): CC REST API server port. Defaults to None.
            ssl_context (ssl.SSLContext, optional): SSL context object for 'https' protocol. Defaults to None.
            access_log (any, optional): access log. Defaults to None.
        """
        CcRestApi._loop = asyncio.get_event_loop()
        runner = web.AppRunner(app, handle_signals=CcRestApi._handle_signals, access_log=access_log)
        CcRestApi._loop.run_until_complete(runner.setup())
        CcRestApi._site = web.TCPSite(runner, host=host, port=port, ssl_context=ssl_context)
        CcRestApi._loop.run_until_complete(CcRestApi._site.start())
        Log.info(f'======== CC REST API Server is running on {CcRestApi._site.name} ========')

        # Add signal handlers
        if CcRestApi._handle_signals:
            for signame in  CcRestApi._signals:
                CcRestApi._loop.add_signal_handler(getattr(signal, signame),
                                    lambda signame=signame: asyncio.ensure_future(CcRestApi.handle_signal(signame)))

    @staticmethod
    def stop():
        """
        Stops REST API server.
        Warpper to call async coroutine CcRestApi._stop().
        """
        Log.info(f'CC Rest API Server {CcRestApi._site.name} is stopping.')
        CcRestApi._loop().run_until_complete(CcRestApi._stop())

    @staticmethod
    def start():
        """
        Starts CC REST API server.
        fetches the configuration from conf and starts server.
        """
        host = None
        ha_endpoint = Conf.get(const.HA_GLOBAL_INDEX, f'service_config{const.HA_DELIM}endpoint')
        Log.info(f"Endpoint : {ha_endpoint}")
        if ha_endpoint:
            port = ha_endpoint.split(":")[-1]

        CcRestApi._start_server(CcRestApi._app, host=host, port=port, ssl_context=None, access_log=None)

    @staticmethod
    def join():
        """
        This is blocking call similar to thread.join() function.
        It waits on event loop forever unless someone like signal handler function calls loop.stops().
        from another thread you can call loop.stop() to get out of this loop.
        You can stop this loop also by pressing <Ctrl+c> if you running this application from terminal.
        """
        try:
            CcRestApi._loop.run_forever()
        finally:
            CcRestApi._loop.close()

