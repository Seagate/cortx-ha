import paramiko


class SSH

    def __init__(self):
        self._ssh_client = paramiko.SSHClient()

    def connect(self, hostname, username):
        '''Establishes a connection'''
        pass

    def communicate(self, command):
        '''Communicates to remote node by code execution'''
        pass

    def disconnect(self):
        '''closes the connection'''
        pass
