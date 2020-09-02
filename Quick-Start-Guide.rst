===
HA
===

This guide provides information to get the HA component ready.

**************
Prerequisites
**************
The following prerequisites must be met to install the HA component.

- Yum repositories must be available. To setup yum repos, run the following command:

 - **$ curl https://raw.githubusercontent.com/Seagate/cortx-prvsnr/dev/cli/src/cortx-prereqs.sh?token=APA75GY34Y2F5DJSOKDCZAK7ITSZC -o cortx-prereqs.sh; chmod a+x cortx-prereqs.sh**

- Run the below mentioned commands to install Python 3+, PIP, Kernel-devel (3.10.0-1062) as they are mandatory.

 - **$ yum install python36**

 - **$ yum install python36-devel**

 - **$ yum install openssl-devel**

 - **$ yum install libffi-devel**

 - **$ yum install bzip2-devel**

 - **$ yum install systemd-devel**

 - **$ yum group install "Development Tools"**
 
- The **eos-py-utils** rpm must be installed. To install the same, run the following command:

 - **$ git clone --recursive git@github.com:Seagate/cortx-py-utils.git**

 - **$ cd cortx-py-utils**

 - **$ python3 setup.py bdist_rpm**

 - **$ yum install dist/eos-py-utils-1.0.0-1.noarch.rpm**
 
Corosync and Pacemaker
======================

Perform the procedure mentioned below to setup corosync and pacemaker. To complete the setup successfully, two Virtual Machines (VMs) are required. In the below mentioned procedure, the first five steps must be performed on both the nodes and the remaining steps must be performed on the primary node.

1. Setup the yum repos. Refer the **Prerequisites** section above to know about the process of setting up.

2. Run the below mentioned commands to disable selinux and firewall.

 - **$ systemctl stop firewalld**

 - **$ systemctl disable firewalld**

 - **$ sestatus**

 - **$ setenforce 0**

 - **$ sed 's/SELINUX=enforcing/SELINUX=disabled/' /etc/sysconfig/selinux**

 - **$ shutdown -r now**

 - **$ getenforce** (It must show **Disabled**)
 
Cloning the Source Code
=======================
To clone the source code, run the following commands:

- **$ git clone --recursive git@github.com:Seagate/cortx-ha.git**

- **$ cd cortx-ha**

**Note**: To clone the source code, it is necessary to generate the SSH public key. To generate the key, refer `SSH Public Key <https://github.com/Seagate/cortx/blob/main/doc/SSH%20Public%20Key.rst>`_.

Building the Source Code
========================
To build the source code, perform the following:

1. Install the pip packages by running the following commands:

 - **$ bash jenkins/cicd/cortx-ha-dep.sh dev <github-token>**

  - Refer `GitHub Token <https://github.com/Seagate/cortx/blob/main/doc/ContributingToCortxHA.md#token-personal-access-for-command-line-required-for-submodule-clone-process>`_ to know the process that must be followed to create a GitHub token.

 - **$ python3 -m pip install -r jenkins/pyinstaller/requirements.txt**

2. Build the RPMs by navigating to the directory where the HA component has been cloned, and running one of the following commands:

 - **$ jenkins/build.sh**

 - **jenkins/build.sh -b <BUILD-NO>**
 
Installing HA
=============
To install HA perform the following procedure.

1. On both the nodes, run the following command.

 - **$ yum install -y dist/rpmbuild/RPMS/x86_64/cortx-ha-XXXX.rpm**

   For example, **yum install -y dist/rpmbuild/RPMS/x86_64/cortx-ha-1.0.0-368034b.x86_64.rpm**

2. Refer `HA <https://github.com/Seagate/cortx-ha/blob/dev/conf/setup.yaml>`_, and execute the following.

 - post_install
 
  - **/opt/seagate/cortx/ha/conf/script/ha_setup post_install**

 - config
 
  - **/opt/seagate/cortx/ha/conf/script/ha_setup config**

 - init
 
  - **/opt/seagate/cortx/ha/conf/script/ha_setup init**

 - ha
 
  - **/opt/seagate/cortx/ha/conf/script/ha_setup test**

3. On the salt primary node, run the following command.

 - **$ /opt/seagate/cortx/ha/conf/script/build-cortx-ha init /var/lib/hare/build-ees-ha-args.yaml**

**Note**: To configure HA, the CORTX stack or salt, pacemaker, and consul must be configured on the development box. Please note that HA is supported only on the hardware.
 
Resetting HA
============
To reset HA, run the relevant commands mentioned below.

- On the salt primary node, run the following command:

 - **$ /opt/seagate/cortx/ha/conf/script/build-cortx-ha cleanup /var/lib/hare/build-ees-ha-args.yaml**

- Run the following commands on the two nodes.

 - **$ /opt/seagate/cortx/ha/conf/script/ha_setup reset**

 - **$ yum remove -y cortx-ha-XXXX.rpm**
 
Tests
=====
To perform the required tests, run the following commands:

- **$ cd cortx-ha/ha/test/**

- **$ python3 main.py**
