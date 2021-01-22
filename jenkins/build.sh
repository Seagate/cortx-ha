#!/bin/bash

# Copyright (c) 2020 Seagate Technology LLC and/or its Affiliates
#
# This program is free software: you can redistribute it and/or modify it under the
# terms of the GNU Affero General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License along
# with this program. If not, see <https://www.gnu.org/licenses/>. For any questions
# about this software or licensing, please email opensource@seagate.com or
# cortx-questions@seagate.com.

set -ex
BASE_DIR=$(realpath "$(dirname $0)/..")
PROG_NAME=$(basename $0)
DIST=$(realpath $BASE_DIR/dist)
RPM_NAME="cortx-ha"
CORTX="cortx"
HA_PATH="/opt/seagate/${CORTX}"
HA1="1"
HA2="2"
BUILD_VERSION="1"
MINOR_VERSION="0.0"

usage() {
    echo """
usage: $PROG_NAME [-g <cortx-ha git version>] [-v <cortx-ha major version>] [-m <cortx-ha minor version>]
                  [-d] [-b <build no>] [-k <key>]

Options:
    -g : Build rpm with git revision
    -v : Build rpm with major version
    -m : Build rpm with minor version
    -b : Build rpm with build number
    -k : Provide key for encryption of code
        """ 1>&2;
    exit 1;
}

while getopts ":g:v:b:p:k" o; do
    case "${o}" in
        g)
            GIT_VER=${OPTARG}
            ;;
        v)
            MAJ_VER=${OPTARG}
            ;;
        m)
            MIN_VER=${OPTARG}
            ;;
        b)
            BUILD=${OPTARG}
            ;;
        k)
            KEY=${OPTARG}
            ;;
        *)
            usage
            ;;
    esac
done

# Workaround for Jenkins CI pipeline. The actual path in BASE_DIR may be very
# long, for example this happens in Jenkins environment:
#
#   /var/jenkins/workspace/GitHub-custom-ci-builds/custom_build_test/cortx-ha
#
# It then leads to a failure when running `pip3` installed by pyenv module:
#
#   bash: /var/jenkins/workspace/GitHub-custom-ci-builds/custom_build_test/cortx-ha/dist/rpmbuild/BUILD/cortx/pcswrap/.py3venv/bin/pip3: /var/jenkins/workspace/GitHub-custom-ci-builds/custom_build_test/cortx-ha/dist: bad interpreter: No such file or directory
#

if [[ $BASE_DIR =~ jenkins/workspace ]] ; then

    #ln -sfn $BASE_DIR /tmp/$RPM_NAME
    cp -a $BASE_DIR /tmp/$RPM_NAME
    BASE_DIR_OLD=$BASE_DIR
    BASE_DIR=/tmp/$RPM_NAME
fi

cd $BASE_DIR
[ -z "$GIT_VER" ] && GIT_VER=$(git rev-parse --short HEAD)
[ -z "$BUILD" ] && BUILD="${BUILD_VERSION}"
[ -z "$MAJ_VER" ] && MAJ_VER="${HA2}"
[ -z "$MIN_VER" ] && MIN_VER="${MINOR_VERSION}"
[ -z "$KEY" ] && KEY="cortx-ha@pr0duct"

echo "Using MAJOR_VERSION=${MAJ_VER} MINOR_VERSION=${MIN_VER} REVISION=${GIT_VER} BUILD=${BUILD}"

################### COPY FRESH DIR ##############################
# Create fresh one to accomodate all packages.

COPY_START_TIME=$(date +%s)
DIST="$BASE_DIR/dist"
HA_DIR="${DIST}/${CORTX}/ha"
HA_SRC_PATH="$BASE_DIR/ha"
TMPDIR="$DIST/tmp"
TMPHA="${TMPDIR}/${CORTX}/ha"
[ -d "$DIST" ] && {
    rm -rf ${DIST}
}
mkdir -p ${HA_DIR} ${TMPDIR} ${TMPHA}
if [ "$MAJ_VER" == "${HA1}" ]
then
  cp $BASE_DIR/jenkins/v1/cortx-ha.spec ${TMPDIR}
else
  cp $BASE_DIR/jenkins/v2/cortx-ha.spec ${TMPDIR}
fi
cp $BASE_DIR/VERSION ${TMPDIR}

######################### Backend ##############################

# Build HA with PyInstaller
cd $TMPDIR

sed -i -e "s/<RPM_NAME>/${RPM_NAME}/g" \
    -e "s|<HA_PATH>|${HA_PATH}|g" $TMPDIR/cortx-ha.spec
sed -i -e "s/<MAJ_VERSION>/${MAJ_VER}/g" $TMPDIR/VERSION

# Copy Backend files

cp -rs $HA_SRC_PATH/* ${TMPHA}

PYINSTALLER_FILE=$TMPDIR/pyinstaller-cortx-ha.spec
cp $BASE_DIR/jenkins/pyinstaller/pyinstaller-cortx-ha.spec ${PYINSTALLER_FILE}
sed -i -e "s|<HA_PATH>|${TMPDIR}/cortx|g" ${PYINSTALLER_FILE}
python3 -m PyInstaller --clean -y --distpath ${HA_DIR} --key ${KEY} ${PYINSTALLER_FILE}

mkdir -p $HA_DIR/conf/etc/ $HA_DIR/conf/script/
cp -rf $BASE_DIR/conf/etc/common/* $HA_DIR/conf/etc/
cp -rf $BASE_DIR/conf/script/common/* $HA_DIR/conf/script/
cp -rf $BASE_DIR/conf/logrotate/ $HA_DIR/conf/
if [ "$MAJ_VER" == "${HA1}" ]
then
   cp -rf $BASE_DIR/conf/etc/v1/* $HA_DIR/conf/etc/
   cp -rf $BASE_DIR/conf/script/v1/* $HA_DIR/conf/script/
   cp -rf $BASE_DIR/conf/iostack-ha/ $HA_DIR/conf/
   # Update HA path in setup
   sed -i -e "s|<HA_PATH>|${HA_PATH}/ha|g" ${HA_DIR}/conf/script/ha_setup
   sed -i -e "s|<HA_PATH>|${HA_PATH}/ha|g" ${HA_DIR}/conf/script/build-cortx-ha
   sed -i -e "s|<HA_PATH>|${HA_PATH}/ha|g" ${HA_DIR}/conf/script/cluster_update
else
   cp -rf $BASE_DIR/conf/etc/v2/* $HA_DIR/conf/etc/
   cp -rf $BASE_DIR/conf/script/v2/* $HA_DIR/conf/script/
   # Update version in conf file
   sed -i -e "s|<VERSION>|${MAJ_VER}|g" ${HA_DIR}/conf/etc/ha.conf
   # pcswrap will only present in v1, hence removing it from v2
   rm -rf ${TMPHA}/pcswrap
fi

################## TAR & RPM BUILD ##############################

# Remove existing directory tree and create fresh one.
cd $BASE_DIR
rm -rf ${DIST}/rpmbuild
mkdir -p ${DIST}/rpmbuild/SOURCES

cd $HA_SRC_PATH
if [ "$MAJ_VER" == "${HA1}" ]
then
  git ls-files pcswrap resource | cpio -pd $DIST/$CORTX
else
  git ls-files resource | cpio -pd $DIST/$CORTX
fi

cd $DIST
echo "Creating tar for HA build"
tar -czf ${DIST}/rpmbuild/SOURCES/${RPM_NAME}-${MAJ_VER}.${MIN_VER}.tar.gz ${CORTX}

# Generate RPMs
TOPDIR=$(realpath ${DIST}/rpmbuild)

# HA RPM
echo rpmbuild --define "version $MAJ_VER.$MIN_VER" --define "git_rev $GIT_VER" --define "build_num $BUILD" --define \
            "_topdir $TOPDIR" -bb $TMPDIR/cortx-ha.spec
rpmbuild --define "version $MAJ_VER.$MIN_VER" --define "git_rev $GIT_VER" --define "build_num $BUILD" --define \
            "_topdir $TOPDIR" -bb $TMPDIR/cortx-ha.spec

# Remove temporary directory
rm -rf ${DIST}/tmp

echo "HA RPMs ..."
find $BASE_DIR -name *.rpm

if [[ $BASE_DIR_OLD =~ jenkins/workspace ]] ; then
    cp -a $DIST $BASE_DIR_OLD
fi
