ha_setup config --config yaml:///etc/cortx/cluster.conf --services fault_tolerance
/opt/seagate/cortx/ha/bin/ha_start --config yaml:///etc/cortx/cluster.conf --services fault_tolerance
/opt/seagate/cortx/ha/bin/ha_start --config yaml:///etc/cortx/cluster.conf --services health_monitor
/opt/seagate/cortx/ha/bin/ha_start --config yaml:///etc/cortx/cluster.conf --services k8s_monitor
