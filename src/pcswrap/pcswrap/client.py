import json
import logging
import os
import sys
from typing import Callable, List, Optional

from click import ClickException
from systemd import journal

from pcswrap.cli import parse_opts
from pcswrap.cli.types import (MaintenanceAll, NoOp, Shutdown, Standby,
                               StandbyAll, Status, UnmaintenanceAll, Unstandby,
                               UnstandbyAll)
from pcswrap.exception import CliException, MaintenanceFailed, TimeoutException
from pcswrap.internal.connector import CliConnector
from pcswrap.internal.waiter import Waiter
from pcswrap.types import Credentials, Node, PcsConnector, Resource

__all__ = ['Client', 'main']


def all_stopped(resource_list: List[Resource]) -> bool:
    logging.debug('The following resources are found: %s', resource_list)
    return all(not r.active for r in resource_list)


def non_standby_nodes(node_list: List[Node]) -> bool:
    logging.debug('The following nodes are found: %s', node_list)
    return all(not n.standby for n in node_list)


def has_no_resources(node_name: str) -> Callable[[List[Node]], bool]:
    def fn(nodes: List[Node]) -> bool:
        try:
            node: Node = [x for x in nodes if x.name == node_name][0]
            logging.debug('Node %s has %d resources running', node_name,
                          node.resources_running)
            return node.resources_running == 0
        except IndexError:
            logging.debug('No %s node was found', node_name)
            return False

    return fn


class Client():
    def __init__(self,
                 connector: PcsConnector = None,
                 credentials: Credentials = None):
        self.credentials = credentials
        self.connector: PcsConnector = connector or CliConnector()

        if credentials:
            self.connector.set_credentials(credentials)

        self.connector.ensure_authorized()
        self._ensure_sane()

    def _ensure_sane(self) -> None:
        self.connector.get_nodes()

    def get_all_nodes(self) -> List[Node]:
        return self.connector.get_nodes()

    def get_online_nodes(self) -> List[Node]:
        return [x for x in self.connector.get_nodes() if x.online]

    def unstandby_node(self, node_name) -> None:
        self.connector.unstandby_node(node_name)

    def standby_node(self, node_name) -> None:
        self.connector.standby_node(node_name)

    def get_cluster_name(self) -> str:
        return self.connector.get_cluster_name()

    def standby_all(self, timeout: int = 120) -> None:
        self.connector.standby_all()
        waiter = Waiter(title='no running resources',
                        timeout_seconds=timeout,
                        provider_fn=self.connector.get_resources,
                        predicate=all_stopped)
        waiter.wait()

    def unstandby_all(self, timeout: int = 120) -> None:
        self.connector.unstandby_all()
        waiter = Waiter(title='no standby nodes in cluster',
                        timeout_seconds=timeout,
                        provider_fn=self.connector.get_nodes,
                        predicate=non_standby_nodes)
        waiter.wait()

    def _is_last_online_node(self, node_name: str) -> bool:
        nodes = self.get_online_nodes()
        return len(nodes) == 1 and nodes[0].name == node_name

    def shutdown_node(self, node_name: str, timeout: int = 120) -> None:
        last_node = self._is_last_online_node(node_name)
        logging.debug(
            'Checking whether it is possible to shutdown the node %s',
            node_name)
        self.connector.ensure_shutdown_possible(node_name)

        self.connector.standby_node(node_name)
        waiter = Waiter(title=f'resources are stopped at node {node_name}',
                        timeout_seconds=timeout,
                        provider_fn=self.connector.get_nodes,
                        predicate=has_no_resources(node_name))
        waiter.wait()
        if not last_node:
            self.connector.shutdown_node(node_name)
        else:
            logging.info(
                'Node %s is the last alive node in the cluster. '
                'It will be powered off by means of direct IPMI signal '
                'without involving Pacemaker', node_name)
            self.connector.manual_shutdown_node(node_name)

    def disable_stonith(self, timeout: int = 120) -> None:
        resources = self.connector.get_stonith_resources()
        for r in resources:
            self.connector.disable_resource(r)

        waiter = Waiter(title='stonith resources are disabled',
                        timeout_seconds=timeout,
                        provider_fn=self.connector.get_stonith_resources,
                        predicate=all_stopped)
        waiter.wait()

    def enable_stonith(self, timeout: int = 120) -> None:
        resources = self.connector.get_stonith_resources()
        for r in resources:
            self.connector.enable_resource(r)

        def all_started(resource_list: List[Resource]) -> bool:
            logging.debug('The following resources are found: %s',
                          resource_list)
            return all(r.active for r in resource_list)

        waiter = Waiter(title='stonith resources are enabled',
                        timeout_seconds=timeout,
                        provider_fn=self.connector.get_stonith_resources,
                        predicate=all_started)
        waiter.wait()

    def cluster_maintenance(self, timeout: int = 120):
        logging.info('Disabling stonith resources first')

        try:
            self.disable_stonith(timeout)
        except TimeoutException:
            raise MaintenanceFailed()
        logging.debug('Switching to standby mode')
        try:
            self.standby_all(timeout)
        except Exception:
            raise MaintenanceFailed()

        logging.info('All nodes are in standby mode now')

    def cluster_unmaintenance(self, timeout: int = 120):
        self.unstandby_all(timeout=timeout)
        logging.info('All nodes are back to normal mode.')
        self.enable_stonith(timeout=timeout)
        logging.info(
            'Stonith resources are enabled. Cluster is functional now.')

    def get_status(self, is_full: bool = False) -> str:
        nodes = [node._asdict() for node in self.get_all_nodes()]
        if not is_full:
            return json.dumps(nodes)

        def safe_lower(s: Optional[str]) -> str:
            return (s or '').lower()

        eligible = self.connector.get_eligible_resource_count()

        started = 0
        stopped = 0
        for res in self.connector.get_resources():
            role = safe_lower(res.role)
            if role == 'started':
                started += 1
            elif role == 'stopped':
                stopped += 1

        result = {
            'resources': {
                'statistics': {
                    'started': started,
                    'stopped': stopped,
                    'starting': eligible - started
                }
            },
            'nodes': nodes
        }
        return json.dumps(result)


def _setup_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    console = logging.StreamHandler(stream=sys.stderr)
    journald = journal.JournaldLogHandler(identifier='pcswrap')
    logging.basicConfig(level=level,
                        handlers=[console, journald],
                        format='%(asctime)s [%(levelname)s] %(message)s')


class AppRunner:
    def __init__(self):
        self._get_client = self._get_client_default

    def _get_client_default(self, auth: Optional[Credentials]) -> Client:
        return Client(credentials=auth)

    def run(self, argv: List[str]) -> None:
        prog_name = os.environ.get('PCSCLI_PROG_NAME')
        ctx = parse_opts(args=argv,
                         prog_name=prog_name,
                         standalone_mode=False,
                         obj={'timeout_sec': 120})

        def client() -> Client:
            # This function is added to shorten the code below (no need for
            # "self." prefix and no need to add parameters)
            return self._get_client(ctx.auth)

        _setup_logging(ctx.verbose)
        cmd = ctx.command
        if isinstance(cmd, Standby):
            client().standby_node(cmd.node)
        elif isinstance(cmd, StandbyAll):
            client().standby_all(ctx.timeout_sec)
        elif isinstance(cmd, Unstandby):
            client().unstandby_node(cmd.node)
        elif isinstance(cmd, UnstandbyAll):
            client().unstandby_all(ctx.timeout_sec)
        elif isinstance(cmd, Shutdown):
            client().shutdown_node(cmd.node, timeout=ctx.timeout_sec)
        elif isinstance(cmd, MaintenanceAll):
            client().cluster_maintenance(ctx.timeout_sec)
        elif isinstance(cmd, UnmaintenanceAll):
            client().cluster_unmaintenance(ctx.timeout_sec)
        elif isinstance(cmd, Status):
            print(client().get_status(cmd.is_full))
        elif isinstance(cmd, NoOp):
            # --help or some other eager option was passed, nothing to
            # process here
            pass
        else:
            raise RuntimeError('Business logic error: unknown '
                               f'command given - {cmd}')


def main() -> None:
    try:
        AppRunner().run(sys.argv[1:])
    except MaintenanceFailed:
        logging.error('Failed to switch to maintenance mode.')
        logging.error(
            'The cluster is now unstable. Maintenance mode '
            'was not rolled back to prevent STONITH actions to happen '
            'unexpectedly.')
        prog_name = os.environ.get('PCSCLI_PROG_NAME') or 'pcswrap'
        logging.error(
            'Consider running `%s unmaintenance --all` to switch'
            ' the cluster to normal mode manually.', prog_name)
        sys.exit(1)

    except ClickException as e:
        e.show()
        sys.exit(1)
    except CliException as e:
        logging.error('Exiting with FAILURE: %s', e)
        logging.debug('Detailed info', exc_info=True)
        sys.exit(1)
    except Exception:
        logging.exception('Unexpected error happened')
        sys.exit(1)
