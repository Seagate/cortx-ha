import paramiko

from cortx.utils.ssh import SSHChannel
from ha.remote_execution.remote_executor import RemoteExecutor
from ha.const import RA_LOG_DIR
from cortx.utils.log import Log

class SSHRemoteExecutor(RemoteExecutor):
    '''class which enables remote communication using SSH'''

    def __init__(self, hostname, username, port=22, password=None):
        '''init method'''
        super(self, SSHRemoteExecutor).__init__(hostname, port)
        self._username = username
        self._password = password
        try:
            self._ssh_client = SSHChannel(self._hostname, self._port, \
                                            self._username, self._password)
        except Exception as e:
            Log.error('SSHRemoteExecutor, some error occured while connecting \
                        to SSH channel {e}')

    def execute(self, command: str) -> int:
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
        Log.info(f'Execting command: {command} on a remote host {self._hostname}')
        try:
            ret_code, res = self._ssh_client.execute(command)
        if ret_code:
            raise RemoteExecutorError(f'Failed to execute command {command} on a \
                                        remote node with error: {res}')
        except:
            raise RemoteExecutorError("Failed to execute command {command} \
                                        on a remote node")
        return ret_code

if __name__ == '__main__':
    Log.init(service_name="SSHRemoteExecutor", log_path=RA_LOG_DIR, level="INFO")
    remote_executor = SSHRemoteExecutor(hostname)
    remote_executor.execute(command)
