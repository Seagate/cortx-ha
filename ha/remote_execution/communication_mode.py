class CommunicationMode

    def __init__(self):
        pass

    @abstract
    def connect(self, hostname, username):
        '''Establishes a connection'''
        pass

    @abstract
    def communicate(self, command):
        '''Communicates to remote node by code execution'''
        pass

    @abstract
    def disconnect(self):
        '''closes the connection'''
        pass
