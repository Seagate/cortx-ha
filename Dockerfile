FROM centos:7
RUN yum install -y epel-release python3
WORKDIR /opt
COPY ha/fault_tolerance/ /opt/seagate/cortx/ha/fault_tolerance/
ENTRYPOINT ["python3", "/opt/seagate/cortx/ha/fault_tolerance/fault_tolerance_driver.py"]

