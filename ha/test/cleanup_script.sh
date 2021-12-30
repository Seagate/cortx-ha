ha_setup cleanup --config yaml:///etc/cortx/cluster.conf --services fault_tolerance
pkill -f /usr/lib/python3.6/site-packages/ha/monitor/k8s/monitor.py
pkill -f /usr/lib/python3.6/site-packages/ha/core/health_monitor/health_monitord.py
pkill -f /usr/lib/python3.6/site-packages/ha/fault_tolerance/fault_tolerance_driver.py
