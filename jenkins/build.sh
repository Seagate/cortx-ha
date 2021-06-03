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
DIST_DIR="$BASE_DIR/dist/cortx-ha"
PROG_NAME=$(basename $0)
HA_INSTALL_PATH="/opt/seagate/cortx/ha"
HA2="2"
MINOR_VERSION="0"
REVISION_VERSION="0"

usage() {
    echo """
usage: $PROG_NAME [-v <cortx-ha major version>] [-m <cortx-ha minor version>]
                  [-r <cortx-ha revision version>] [-b <build no>] [-k <key>]

Options:
    -v : Build rpm with major version
    -m : Build rpm with minor version
    -r : Build rpm with revision version
    -b : Build rpm with build number
        """ 1>&2;
    exit 1;
}

while getopts ":v:m:r:b:k" o; do
    case "${o}" in
        v)
            MAJ_VER=${OPTARG}
            ;;
        m)
            MIN_VER=${OPTARG}
            ;;
        r)
            PATCH_VER=${OPTARG}
            ;;
        b)
            BUILD=${OPTARG}
            ;;
        *)
            usage
            ;;
    esac
done

cd $BASE_DIR

[ -z $"$BUILD" ] && BUILD="$(git rev-parse --short HEAD)" \
        || BUILD="${BUILD}_$(git rev-parse --short HEAD)"
[ -z "$MAJ_VER" ] && MAJ_VER="${HA2}"
[ -z "$MIN_VER" ] && MIN_VER="${MINOR_VERSION}"
[ -z "$PATCH_VER" ] && PATCH_VER="${REVISION_VERSION}"

echo "Using MAJOR_VERSION=${MAJ_VER} MINOR_VERSION=${MIN_VER} REVISION=${PATCH_VER} BUILD=${BUILD}"
version="${MAJ_VER}.${MIN_VER}.${PATCH_VER}"

# Cleanup
rm -rf $BASE_DIR/dist

# Copy
mkdir -p $DIST_DIR
cp -rf `ls -A | grep -v "dist" | grep -v ".git*"` $DIST_DIR/

cd $DIST_DIR

# Update version in conf file
sed -i -e "s|<VERSION>|${version}|g" ${DIST_DIR}/conf/etc/v2/ha.conf

/usr/bin/env python3 setup.py bdist_rpm --version="${version}" --install-dir="${HA_INSTALL_PATH}" --release="$BUILD" \
--force-arch x86_64 --post-install jenkins/rpm/v2/post_install_script.sh \
--post-uninstall jenkins/rpm/v2/post_uninstall_script.sh

# Above --force-arch flag and below code is just for backward compatibility.
# Can be removed once integration is done with RE.
rpm_file=`ls -1 ${DIST_DIR}/dist/ | grep x86_64 | grep -v debug`
mkdir -p ${BASE_DIR}/dist/rpmbuild/RPMS/x86_64
cp ${DIST_DIR}/dist/${rpm_file} ${BASE_DIR}/dist/rpmbuild/RPMS/x86_64/

cd ${BASE_DIR}/dist
rm -rf $DIST_DIR

echo "********** RPM ****************"
realpath $(find -name "*.rpm")
