import re

import click
from click.exceptions import UsageError
from pcswrap.cli.types import (CLIContext, MaintenanceAll, NoOp, Shutdown,
                               Standby, StandbyAll, Status, UnmaintenanceAll,
                               Unstandby, UnstandbyAll)
from pcswrap.types import Credentials


def _sanitize_name(name):
    name = name.strip('-')
    return re.sub('-', '_', name)


def ensure_either_exists(ctx, var_a, var_b):
    a = _sanitize_name(var_a)
    b = _sanitize_name(var_b)
    ok = bool(ctx.params[a]) ^ bool(ctx.params[b])
    if not ok:
        raise UsageError(f'Either {var_a} or {var_b} must be specified. '
                         'Please choose one.')


def ensure_if_first_then_second(ctx, var_a, var_b):
    a = _sanitize_name(var_a)
    b = _sanitize_name(var_b)
    ok = not bool(ctx.params[a]) or bool(ctx.params[b])
    if not ok:
        raise UsageError(
            f'If {var_a} specified then {var_b} is also required. '
            f' Please add {var_b}.')


@click.group()
def cli():
    pass


@cli.command(help='Show status of all cluster nodes.')
@click.option('--full',
              default=False,
              is_flag=True,
              help='Show overall cluster status, so not only nodes '
              'will be included.')
@click.pass_context
def status(ctx, full):
    ctx.obj['command'] = Status(is_full=full)
    return ctx.obj


@cli.command(help='Shutdown (power off) the node by name.')
@click.argument('node')
@click.option('--timeout-sec',
              type=int,
              default=120,
              help='Maximum time that this command will'
              ' wait for any operation to complete before raising an error')
@click.pass_context
def shutdown(ctx, node, timeout_sec):
    ctx.obj['timeout_sec'] = timeout_sec
    ctx.obj['command'] = Shutdown(node=node)
    return ctx.obj


@cli.command(help='Switch the cluster to maintenance mode.')
@click.option('--all', is_flag=True, required=True)
@click.option('--timeout-sec',
              type=int,
              default=120,
              help='Maximum time that this command will'
              ' wait for any operation to complete before raising an error')
@click.pass_context
def maintenance(ctx, timeout_sec, **kwargs):
    ctx.obj['timeout_sec'] = timeout_sec
    ctx.obj['command'] = MaintenanceAll()
    return ctx.obj


@cli.command(help='Move the cluster from maintenance back to normal mode.')
@click.option('--all', is_flag=True, required=True)
@click.option('--timeout-sec',
              type=int,
              default=120,
              help='Maximum time that this command will'
              ' wait for any operation to complete before raising an error')
@click.pass_context
def unmaintenance(ctx, timeout_sec, **kwargs):
    ctx.obj['timeout_sec'] = timeout_sec
    ctx.obj['command'] = UnmaintenanceAll()
    return ctx.obj


@cli.command(help='Put the given node into standby mode.')
@click.option('--all',
              default=False,
              is_flag=True,
              help='Put all the nodes in the cluster to standby mode (no node '
              'name is required).')
@click.argument('node', required=False)
@click.pass_context
def standby(ctx, all=False, node=None):
    ensure_either_exists(ctx, '--all', 'node')
    ctx.obj['command'] = StandbyAll() if all else Standby(node=node)
    return ctx.obj


@cli.command(help='Remove the given node from standby mode.')
@click.option('--all',
              default=False,
              is_flag=True,
              help='Remove all the nodes in the cluster from standby mode '
              '(no node name is required).')
@click.argument('node', required=False)
@click.pass_context
def unstandby(ctx, all=False, node=None):
    ensure_either_exists(ctx, '--all', 'node')
    ctx.obj['command'] = UnstandbyAll() if all else Unstandby(node=node)
    return ctx.obj


# This is a workaround for https://github.com/pallets/click/issues/347
@click.command(cls=click.CommandCollection, sources=[cli])  # type: ignore
@click.option('--verbose', default=False, is_flag=True)
@click.option('--username')
@click.option('--password')
@click.pass_context
def cli_main(ctx, verbose, username, password):
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    ctx.obj['auth'] = None
    ensure_if_first_then_second(ctx, 'username', 'password')
    if username:
        ctx.obj['auth'] = Credentials(username=username, password=password)
    return ctx.obj


def parse_opts(**kwargs) -> CLIContext:
    result = cli_main(**kwargs)
    if not isinstance(result, dict):
        return CLIContext(command=NoOp(),
                          auth=None,
                          verbose=False,
                          timeout_sec=0)

    return CLIContext(command=result['command'],
                      auth=result.get('auth', None),
                      verbose=result['verbose'],
                      timeout_sec=result['timeout_sec'])
