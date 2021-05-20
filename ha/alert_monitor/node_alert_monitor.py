'''Dervied module in the Monitoring hierarchy which monitors node alert'''

class NodeAlertMonitor():
    '''
    Module responsible for analyzing an alert information
    to generate an IEM and sending the IEM across.
    '''
    #TODO: Inherit this class from base AlertMonitor

    # TODO: This can be initialized at base level
    IEC_mapping_dict = {
        'severity': {'shutdown': 'W', 'poweron': 'I'},
        'source': 'S',
        'component': '008',
        'module': '001',
        'event': {'failure': '0001', 'recover': '0002'}
        }

    def __init__(self):
        ''''Init method'''
        # Name of the node event. e.g. shutdown or poweron
        # Can be known from base class. Values may change
        self._event = None
        self._event_type = 'failure'

    def create_iem(self):
        '''Creates the structure required to send the information as IEC'''
        # From the base implementation, self.alert_desc value will be available
        # From which, actual event can be found. like shutdown or poweron
        severity = self.IEC_mapping_dict['severity'][self._event]
        if self._event == 'poweron':
            self._event_type = 'recover'
        event = self.IEC_mapping_dict['event'][self._event_type]
        iec_string = f"IEC:{severity}{self.IEC_mapping_dict['source']}{self.IEC_mapping_dict['component']}{self.IEC_mapping_dict['module']}{event}"
        # TODO: Send to the syslog
