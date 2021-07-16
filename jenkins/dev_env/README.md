# Check Prerequisite

1. Get new VM: 3 as per need.

2. Clone Repo cortx-ha in home(GID) dir
```bash
mkdir src; cd src
git clone git@github.com:Seagate/cortx-ha.git
cd cortx-ha
```

3. Copy `cortx-ha/jenkins/dev_env` dir to `/root` on all node

# Build and Install RPM

1. Build and Install RPM
  - Install all dependency package.
```bash
bash -x /root/dev_env/build_rpm.sh /root/dev.conf
```

# Set Python path (Optional)
1. Update on any if want to run code from repos
  - Update `~/.bashrc` on root user
```
# add at end of ~/.bashrc
export PYTHONPATH="${PYTHONPATH}:/home/<USER>/src/cortx-ha/"
```

2. Run bashrc to take effect
```bash
source ~/.bashrc
```

3. Test
```
# Example
/usr/bin/env python3 "/home/<USER>/src/cortx-ha/ha/cli/cortxha.py" -h
# Similarly it can be executed for any cortx-ha file
```

# Cortx Deployment Single Node

1. Copy `/root/dev_env/conf/dev.conf` to `/root/dev.conf` and fill it.
  - Fill only current node related value
  - for other node keep them None

2. Update `/etc/hosts` On node.
```
# Update Host file with node name

<ip-1>  srvnode-1
```

3. Configure other component
```bash
/usr/bin/env bash -x cortx_configure.sh /root/dev.conf singlenode
```

4. Update Consul (Follow for Single node setup)
- Link: https://github.com/Seagate/cortx-experiments/blob/main/consul/docs/consulUserGuide.md

5. Configure kafka (Follow Single node setup)
- Link: https://github.com/Seagate/cortx-utils/wiki/Kafka-Server-Setup

6. Install HA RPM
```
yum install -y cortx-ha --nogpgcheck
```

7. Mini Provision (Run on all node)
```bash
ha_setup post_install --config 'json:///root/example_config.json' --dev
ha_setup prepare --config 'json:///root/example_config.json' --dev
ha_setup config --config 'json:///root/example_config.json' --dev
ha_setup init --config 'json:///root/example_config.json' --dev
cortx cluster start
ha_setup test --config 'json:///root/example_config.json' --dev
```

8. Check status
```
pcs status --full
```

# Cortx Deployment Multi Node

1. Copy `/root/dev_env/conf/dev.conf` to `/root/dev.conf` and fill it.

2. Update `/etc/hosts` On all 3 node.
```
# Update Host file with node name

<ip-1>  srvnode-1
<ip-2>  srvnode-2
<ip-3>  srvnode-3
```

3. Update password less ssh On all 3 node.
  - Run on all node
```bash
ssh-keygen
ssh-copy-id root@srvnode-1
ssh-copy-id root@srvnode-2
ssh-copy-id root@srvnode-3
eval `ssh-agent`
ssh-add
```

4. Configure other component (Run on each node)
```bash
/usr/bin/env bash -x cortx_configure.sh /root/dev.conf multinode
```

5. Update Consul (Follow for multiple node)
- Link: https://github.com/Seagate/cortx-experiments/blob/main/consul/docs/consulUserGuide.md

6. Configure kafka (Follow 3 Node setup)
- Link: https://github.com/Seagate/cortx-utils/wiki/Kafka-Server-Setup

7. Install HA RPM
```
yum install -y cortx-ha --nogpgcheck
```

8. Mini Provision (Run on all node)
```bash
ha_setup post_install --config 'json:///root/example_config.json' --dev
ha_setup prepare --config 'json:///root/example_config.json' --dev
ha_setup config --config 'json:///root/example_config.json' --dev
ha_setup init --config 'json:///root/example_config.json' --dev
cortx cluster start
ha_setup test --config 'json:///root/example_config.json' --dev
```

9. Check status
```
pcs status --full
```
