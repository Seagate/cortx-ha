import paramiko


class SSH:
    '''class which enables remote communication using SSH'''

    def __init__(self, hostname, username, port=22, password=None):
        '''init method'''
        super(hostname, port)
        self._ssh_client = paramiko.SSHClient()
        self._username = username
        self._password = password

    def connect(self):
        '''Establishes a connection'''
        pass

    def communicate(self, command):
        '''Communicates to remote node by code execution'''
        pass

    def disconnect(self):
        '''closes the connection'''
        pass
