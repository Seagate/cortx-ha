FROM centos:7
RUN yum install -y epel-release python3
WORKDIR /opt
COPY fault_tolerance/ ./fault_tolerance/
ENTRYPOINT ["python3", "./fault_tolerance/fault_tolerance_driver.py"]

