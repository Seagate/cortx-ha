#!/bin/bash

set -e
BASE_DIR=$(realpath "$(dirname $0)/..")
PROG_NAME=$(basename $0)
DIST=$(realpath $BASE_DIR/dist)
RPM_NAME="cortx-ha"
CORTX="cortx"
HA_PATH="/opt/seagate/${CORTX}"

usage() {
    echo """
usage: $PROG_NAME [-v <coretx-ha version>]
                            [-b <build no>] [-k <key>]

Options:
    -v : Build rpm with version
    -b : Build rpm with build number
    -k : Provide key for encryption of code
        """ 1>&2;
    exit 1;
}

while getopts ":g:v:b:p:k" o; do
    case "${o}" in
        v)
            VER=${OPTARG}
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

cd $BASE_DIR
[ -z $"$BUILD" ] && BUILD="$(git rev-parse --short HEAD)" \
        || BUILD="${BUILD}_$(git rev-parse --short HEAD)"
[ -z "$VER" ] && VER=$(cat $BASE_DIR/VERSION)
[ -z "$KEY" ] && KEY="cortx-ha@pr0duct"

echo "Using VERSION=${VER} BUILD=${BUILD}"

################### COPY FRESH DIR ##############################

# Create fresh one to accomodate all packages.
COPY_START_TIME=$(date +%s)
DIST="$BASE_DIR/dist"
HA_DIR="${DIST}/${CORTX}/ha"
TMPDIR="$DIST/tmp"
TMPHA="${TMPDIR}/${CORTX}/ha"
[ -d "$DIST" ] && {
    rm -rf ${DIST}
}
mkdir -p ${HA_DIR} ${TMPDIR} ${TMPHA}
cp $BASE_DIR/jenkins/cortx-ha.spec ${TMPDIR}

######################### Backend ##############################

# Build HA
cd $TMPDIR

# Copy Backend files
cp -rs $BASE_DIR/src/* ${TMPHA}
cp -rf $BASE_DIR/src/conf $HA_DIR/

# Update HA path in setup
sed -i -e "s|<HA_PATH>|${HA_PATH}/ha|g" ${HA_DIR}/conf/ha_setup
sed -i -e "s|<HA_PATH>|${HA_PATH}/ha|g" ${HA_DIR}/conf/build-cortx-ha

# Setup Python virtual environment
VENV="${TMPDIR}/${CORTX}/venv"
if [ -d "${VENV}/bin" ]; then
    echo "Using existing Python virtual environment..."
else
    echo "Setting up Python 3.6 virtual environment..."
    python3.6 -m venv "${VENV}"
fi
source "${VENV}/bin/activate"
python --version
pip install --upgrade pip
pip install pyinstaller==3.5

# Check python package
req_file=$BASE_DIR/jenkins/pyinstaller/requirment.txt
echo "Installing python packages..."
pip install -r $req_file > /dev/null || {
    echo "Unable to install package from $req_file"; exit 1;
};

pip uninstall -y numpy
pip install numpy --no-binary :all:

PYINSTALLER_FILE=$TMPDIR/pyinstaller-cortx-ha.spec
cp $BASE_DIR/jenkins/pyinstaller/pyinstaller-cortx-ha.spec ${PYINSTALLER_FILE}
sed -i -e "s|<HA_PATH>|${TMPDIR}/cortx|g" ${PYINSTALLER_FILE}
pyinstaller --clean -y --distpath ${HA_DIR} --key ${KEY} ${PYINSTALLER_FILE}

deactivate
################## Add HA_PATH #################################

# Genrate spec file for HA
sed -i -e "s/<RPM_NAME>/${RPM_NAME}/g" \
    -e "s|<HA_PATH>|${HA_PATH}|g" $TMPDIR/cortx-ha.spec

################## TAR & RPM BUILD ##############################

# Remove existing directory tree and create fresh one.
cd $BASE_DIR
rm -rf ${DIST}/rpmbuild
mkdir -p ${DIST}/rpmbuild/SOURCES

# Create tar for ha
cd ${DIST}
echo "Creating tar for ha build"
tar -czf ${DIST}/rpmbuild/SOURCES/${RPM_NAME}-${VER}.tar.gz ${CORTX}

# Generate RPMs
TOPDIR=$(realpath ${DIST}/rpmbuild)

# HA RPM
echo rpmbuild --define "version $VER" --define "dist $BUILD" --define "_topdir $TOPDIR" \
            -bb $BASE_DIR/jenkins/cortx-ha.spec
rpmbuild --define "version $VER" --define "dist $BUILD" --define "_topdir $TOPDIR" -bb $TMPDIR/cortx-ha.spec

# Remove temporary directory
\rm -rf ${DIST}/tmp

echo "HA RPMs ..."
find $BASE_DIR -name *.rpm
