# cortx-ha

HA Project

### Setup
1. Install eos-py-utils rpm
```
yum install -y eos-py-utils
```

2. Install pip packages
```
bash jenkins/cicd/cortx-ha-dep.sh
```

3. Build RPMs
```
./jenkins/build.sh -b <BUILD_NO>
```

4. Install RPM
```
yum install -y cortx-ha
```

5. Export RPM to cicd

6. Check CICD if return non zero then exit and fail build
```
bash jenkins/cicd/cortx-ha-cicd.sh
```
