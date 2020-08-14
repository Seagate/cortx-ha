[![Codacy Badge](https://app.codacy.com/project/badge/Grade/f6cc639394904affa325a6e8b84706e8)](https://www.codacy.com?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=Seagate/cortx-ha&amp;utm_campaign=Badge_Grade)

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
