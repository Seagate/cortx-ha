'''Module which provides service class'''

from abc import ABC
import abc

from ha.utility.error import HAUnimplemented


class Service(ABC):
    '''Abstract base class which provides service related
       operations'''

    SERVICE_TYPE = None

    def __init__(self):
        '''Init method'''
        pass

    @abc.abstractmethod
    def start(self, *args, **kwargs):
        '''Generic method to start the service'''
        raise HAUnimplemented()

    @abc.abstractmethod
    def stop(self, *args, **kwargs):
        '''Generic method to stop the service'''
        raise HAUnimplemented()

    @abc.abstractmethod
    def status(self, service_name, node_id, service_type):
        '''Generic method to get the status of the service'''
        raise HAUnimplemented()


class ClusteredService(Service):
    '''Base class for all clustered service
       implementation'''

    SERVICE_TYPE = 'clustered'


class NodeService(Service):
    ''''Abstract Base class for all node service
        implementation'''

    SERVICE_TYPE = 'node'

