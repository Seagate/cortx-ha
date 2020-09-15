'''Module which provides Hare service class'''


class HareService(Service):

    '''
       All Hare service oprations implementation which uses
       Hctl wrapper
    '''

    def __init__(self):
        '''Init method'''
        # Uses plugin to perform service wrapper
        self._service_plugin = HctlWrapper()

    def start(self, *args, **kwargs):
        '''Method to start the Hare service'''

        self._service_plugin.start()

    def stop(self, *args, **kwargs):
        '''Method to stop the Hare service'''

        self._service_plugin.stop()

    def status(self, *args, **kwargs):
        '''Method to get the Hare service status'''

        self._service_plugin.status()
