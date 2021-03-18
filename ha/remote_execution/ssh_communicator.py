# Copyright (c) 2021 Seagate Technology LLC and/or its Affiliates
#
# This program is free software: you can redistribute it and/or modify it under the
# terms of the GNU Affero General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License along
# with this program. If not, see <https://www.gnu.org/licenses/>. For any questions
# about this software or licensing, please email opensource@seagate.com or
# cortx-questions@seagate.com.

"""Module for remote communication over SSH channel"""


import argparse
import sys

from cortx.utils.log import Log
from cortx.utils.ssh import SSHChannel
from ha.const import RA_LOG_DIR
from ha.core.error import RemoteExecutorError
from ha.remote_execution.remote_executor import RemoteExecutor


class SSHRemoteExecutor(RemoteExecutor):
    '''class which enables remote communication using SSH'''

    def __init__(self, hostname, username=None, port=22, password=None):
        '''init method'''
        super(SSHRemoteExecutor, self).__init__(hostname, port)
        self._username = username
        self._password = password
        try:
            self._ssh_client = SSHChannel(self._hostname, self._username, \
                                            self._password, self._port)
        except Exception as err:
            Log.error(f'SSHRemoteExecutor, some error occured while connecting \
                        to SSH channel {err}')

    def execute(self, command: str) -> None:
        '''
        Communicates to remote node by code execution

        Parameters:
            command: command to be executed on a remote node

        Return:
            int

        Exceptions:
                RemoteExecutorError
        '''
        ret_code = 0
        res = None
        Log.info(f'Executing command: {command} on a remote host: {self._hostname}')
        try:
            ret_code, res = self._ssh_client.execute(command)
            if ret_code:
                raise RemoteExecutorError(f'Error: Failed to \
                                            execute command {command} on a \
                                            remote node: {self._hostname} with \
                                            error: {res}', ret_code)
        except RemoteExecutorError as ree:
            raise ree
        except Exception as err:
            raise RemoteExecutorError(f"Error: {err}.Some problem occured while executing \
                                        command {command} on a remote node: \
                                        {self._hostname}", ret_code)

def _parse_args():
    parser = argparse.ArgumentParser(description="RemoteExecutor using SSH")
    parser.add_argument("--hostname", help="Remote system host-name", required=True)
    parser.add_argument("--command", help="command to be executed", required=True)
    args = parser.parse_args()
    return args

def main() -> None:
    args = _parse_args()
    remote_executor = SSHRemoteExecutor(args.hostname)
    remote_executor.execute(args.command)

if __name__ == '__main__':
    Log.init(service_name="SSHRemoteExecutor", log_path=RA_LOG_DIR, level="INFO")
    try:
        main()
    except RemoteExecutorError as re:
        print(re.error())
        sys.exit(re.rc())
    except Exception as exc:
        print(exc)
        sys.exit(1)

