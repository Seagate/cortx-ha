import time


class FaultToleranceDriver:
    """
    Driver class which will poll contineously with a specific
    time gap and analyzes the alert condition and it gets
    notified to event manager
    """
    def __init__(self):
        pass

    def poll(self):
        while True:
            # Get alert condition from ALertGenerator. Analyze changes
            # with the help of event manager and notify if required
            print(f'Ready to analyze faults in the system')

            # TODO: Configure POLL_INTARVEL instead of harcoding
            time.sleep(10)

if __name__ == '__main__':
    fault_tolerance = FaultToleranceDriver()
    fault_tolerance.poll()
