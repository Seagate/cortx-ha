'''Module which provides template for a plugin'''

from abc import abc, ABC
import abc

from ha.utility.error import HAUnimplemented


class ServicePlugin(ABC):
    '''Abstract Base class for all service plugin
       implementation'''

    def __init__(self):
        '''Init method'''
        pass

    @abc.abstractmethod
    def start(self):
        ''''Abstract method to start the service'''
        raise HAUnimplemented()

    @abc.abstractmethod
    def stop(self):
        ''''Abstract method to stop the service'''
        raise HAUnimplemented()

    @abc.abstractmethod
    def status(self):
        ''''Abstract method to get the status of the service'''
        raise HAUnimplemented()


