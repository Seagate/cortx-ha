import abc


class CommunicationMode:
    '''An abstract Base class for all the remote node
       communication mode'''

    __metaclass__ = abc.ABCMeta

    def __init__(self, hostname, port):
        '''Init method'''
        self._hostname = hostname
        self._port = port

    @abc.abstractmethod
    def connect(self):
        '''Establishes a connection'''
        raise NotImplementedError

    @abc.abstractmethod
    def communicate(self, command):
        '''Communicates to remote node by code execution'''
        raise NotImplementedError

    @abc.abstractmethod
    def disconnect(self):
        '''closes the connection'''
        raise NotImplementedError
