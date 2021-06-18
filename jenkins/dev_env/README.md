# Configure Dev env for HA

  - Prerequisite
  - Build RPM
  - Configure setup service.

## Part 1: Prerequisite

1. 3 VM (Red Hat cloudForm CentOS 7.8)

1. Clone Repo:
    - Clone repo in Home User (GID User)
    - Update `<git-user>` in clone command

  ```bash
  $ ssh <USER>@VM.seagate.com
  $ mkdir /home/<user>/src
  $ cd /home/<user>/src
  $ git clone git@github.com:<git-user>/cortx-ha.git
  ```


## Part 2: Build RPM
  - It will install all required packages including Python.
  - Update `cortx-ha/jenkins/dev_env/dev.conf`
  ```bash
  # Run from root user only
  /home/<user>/src/cortx-ha/jenkins/dev_env/build_rpm.sh /home/<user>/src/cortx-ha/jenkins/dev_env/dev.conf
  ```