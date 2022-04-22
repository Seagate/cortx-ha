import os
import signal
import ssl
import time
from abc import ABC
from aiohttp import web
import asyncio
from asyncio import CancelledError as AsyncioCancelledError
from concurrent.futures import CancelledError as ConcurrentCancelledError

from cortx.utils.log import Log
from cortx.utils.conf_store import Conf
from ha import const
from ha.core import error

class Response:
    pass

class CcRestApi(ABC):

    _app = None
    _loop = None
    _site = None
    __is_shutting_down = False
    _singals = ('SIGINT', 'SIGTERM')

    # Test function just to check whether CC REST API server is alive
    # TODO: to be removed CORTX-30932
    @staticmethod
    async def handler_check_alive(request):
        return web.Response(text="CORTX CC REST API server is alive.")

    @staticmethod
    def init() -> None:

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
        # TODO: CORTX-30931 implement
        pass

    @staticmethod
    def json_response(resp_obj, status=200):
        # TODO: CORTX-30931 Implement
        pass

    @staticmethod
    def error_response(err: Exception, **kwargs):
        # TODO: CORTX-30931 Implement
        pass

    @staticmethod
    @web.middleware
    async def rest_middleware(request, handler):
        Log.debug(f"Rest middleware is called: request = {request} handler = {handler}")
        if CcRestApi.__is_shutting_down:
            # TODO : CORTX-30931 return json proper response with HTTP status = 503
            return CcRestApi.json_response("CC is shutting down", status=503)
        try:
            request_id = int(time.time())

            try:
                await CcRestApi.check_for_unsupported_endpoint(request)
            except Exception as e:
                Log.warn(f"Exception: {e}")
                # TODO:
                CcRestApi.error_response(Exception("Invalid endpoint."))

            resp = await handler(request)

            if isinstance(resp, web.StreamResponse):
                return resp

            status = 200
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

        # TODO: CORTX-30931 Handle multiple exceptions, below is the just 1 added
        except (ConcurrentCancelledError, AsyncioCancelledError) as e:
            Log.warn(f"Client cancelled call for {request.method} {request.path}")
            # TODO: CORTX-30931 use CcRequestCancelled return proper response
            return CcRestApi.json_response(CcRestApi.error_response(Exception("Call cancelled by client"),
                                            request = request, request_id = request_id), status=499)

    @staticmethod
    async def _shut_down():
        Log.info('CC Rest API Server is shutting down.')
        CcRestApi.__is_shutting_down = True
        for task in asyncio.Task.all_tasks():
            if task != asyncio.Task.current_task():
                task.cancel()
        await CcRestApi._site.stop()
        CcRestApi._loop.stop()


    @staticmethod
    async def handle_signal(signame: str):
        Log.info(f'Received signal: {signame}: {getattr(signal, signame)}')
        await CcRestApi._shut_down()

    @staticmethod
    async def _on_startup(app):
        Log.debug('REST API server startup')
        # Note: Additional calls needs to be added to execute on startup of CC Rest API Server

    @staticmethod
    async def _on_shutdown(app):
        Log.debug('REST API server shutdown')
        # Note: Additional calls needs to be added to execute on shutdown of CC Rest API Server

    @staticmethod
    def _start_server(app, host=None, port=None, ssl_context=None, access_log=None):
        CcRestApi._loop = asyncio.get_event_loop()
        runner = web.AppRunner(app, access_log=access_log)
        CcRestApi._loop.run_until_complete(runner.setup())
        CcRestApi._site = web.TCPSite(runner, host=host, port=port, ssl_context=ssl_context)
        CcRestApi._loop.run_until_complete(CcRestApi._site.start())
        Log.info(f'======== CC REST API Server is running on {CcRestApi._site.name} ========')

        # Add signal handlers
        for signame in  CcRestApi._signals:
            CcRestApi._loop.add_signal_handler(getattr(signal, signame),
                                lambda signame=signame: asyncio.ensure_future(CcRestApi.handle_signal(signame)))

    @staticmethod
    def start():

        host = None
        ha_endpoint = Conf.get(const.HA_GLOBAL_INDEX, f'service_config{const.HA_DELIM}endpoint')
        if ha_endpoint:
            port = ha_endpoint.split(":")[-1]
        else:
            port = 23501

        CcRestApi._start_server(CcRestApi._app, host=host, port=port, ssl_context=None, access_log=None)

    @staticmethod
    def join():
        try:
            CcRestApi._loop.run_forever()
        finally:
            CcRestApi._loop.close()