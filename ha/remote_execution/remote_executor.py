import abc


class RemoteExecutor:
    '''An abstract Base class for all the remote node
       execution'''

    __metaclass__ = abc.ABCMeta

    def __init__(self, hostname, port):
        '''Init method'''
        self._hostname = hostname
        self._port = port

    @abc.abstractmethod
    def execute(self, command):
        '''Communicates to remote node by code execution'''
        raise NotImplementedError
