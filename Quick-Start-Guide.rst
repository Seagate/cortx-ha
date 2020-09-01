============
HA Component
============

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
 
Cloning the Source Code
=======================
To clone the source code, run the following commands:

- **$ git clone --recursive git@github.com:Seagate/cortx-ha.git**

- **$ cd cortx-ha**

**Note**: To clone the source code, it is necessary to generate the SSH public key. To generate the key, refer `SSH Public Key <https://github.com/Seagate/cortx/blob/main/doc/SSH%20Public%20Key.rst>`_.
