'''Module which provides service class'''

from abc import ABC


class Service(ABC):
    '''Abstract base class which provides service related
       operations'''

    def __init__(self):
        '''Init method'''
        pass

    @abc.abstractmethod
    def start(self, *args, **kwargs):
        '''Generic method to start the service'''
        raise NotImplementedError

    @abc.abstractmethod
    def stop(self, *args, **kwargs):
        '''Generic method to stop the service'''
        raise NotImplementedError

    @abc.abstractmethod
    def status(self, service_name, node_id, service_type):
        '''Generic method to get the status of the service'''
        raise NotImplementedError
