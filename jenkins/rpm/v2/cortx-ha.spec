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

Name: <RPM_NAME>
Version: %{version}
Release: %{dist}
Summary: HA Tools
License: Seagate
URL: https://github.com/Seagate/cortx-ha
Source0: <RPM_NAME>-%{version}.tar.gz
%define debug_package %{nil}

%description
HA Tools

%prep
%setup -n cortx
# Nothing to do here

%build

%install
rm -rf ${RPM_BUILD_ROOT}
mkdir -p ${RPM_BUILD_ROOT}<HA_PATH>
cp -rp . ${RPM_BUILD_ROOT}<HA_PATH>
exit 0

%post
HA_DIR=<HA_PATH>/ha
RES_AGENT="/usr/lib/ocf/resource.d/seagate"
mkdir -p $HA_DIR/bin /usr/bin $RES_AGENT

# Move binary file
# TODO: Remove one of path of CLI
ln -sf $HA_DIR/lib/cortxha $HA_DIR/bin/cortx
ln -sf $HA_DIR/lib/cortxha /usr/bin/cortx
ln -sf $HA_DIR/lib/cortxha /usr/bin/cortxha
ln -sf $HA_DIR/lib/dynamic_fid_service_ra $HA_DIR/bin/dynamic_fid_service_ra
# TODO: dynamic_fid_service_ra to RESOURCE_AGENT path from setup post_install
ln -sf $HA_DIR/lib/dynamic_fid_service_ra $RES_AGENT/dynamic_fid_service_ra
ln -sf $HA_DIR/lib/ha_setup $HA_DIR/bin/ha_setup
ln -sf $HA_DIR/lib/ha_setup /usr/bin/ha_setup
ln -sf $HA_DIR/lib/ha_setup /usr/local/bin/ha_setup
ln -sf $HA_DIR/lib/event_analyzerd $HA_DIR/bin/event_analyzerd
ln -sf $HA_DIR/lib/event_analyzerd /usr/bin/event_analyzerd
ln -sf $HA_DIR/lib/event_analyzerd /usr/local/bin/event_analyzerd
ln -sf $HA_DIR/lib/pcmk_alert $HA_DIR/bin/pcmk_alert
ln -sf $HA_DIR/lib/pcmk_alert /usr/bin/pcmk_alert
ln -sf $HA_DIR/lib/pcmk_alert /usr/local/bin/pcmk_alert
ln -sf $HA_DIR/lib/health_monitord /usr/bin/health_monitord
ln -sf $HA_DIR/lib/health_monitord /usr/local/bin/health_monitord
exit 0

%preun
exit 0

%postun
[ $1 -eq 1 ] && exit 0
HA_DIR=<HA_PATH>/ha
rm -f /usr/bin/cortx 2> /dev/null;
rm -f $HA_DIR/bin/cortx 2> /dev/null;
rm -f $RES_AGENT/dynamic_fid_service_ra 2> /dev/null;
rm -f $HA_DIR/bin/dynamic_fid_service_ra 2> /dev/null;
rm -f /usr/local/bin/ha_setup 2> /dev/null;
rm -f /usr/bin/ha_setup 2> /dev/null;
rm -f $HA_DIR/bin/ha_setup 2> /dev/null;
rm -f /usr/local/bin/event_analyzerd 2> /dev/null;
rm -f /usr/bin/event_analyzerd 2> /dev/null;
rm -f $HA_DIR/bin/event_analyzerd 2> /dev/null;
rm -f /usr/local/bin/pcmk_alert 2> /dev/null;
rm -f /usr/bin/pcmk_alert 2> /dev/null;
rm -f $HA_DIR/bin/pcmk_alert 2> /dev/null;
rm -f /usr/local/bin/health_monitord 2> /dev/null;
rm -f /usr/bin/health_monitord 2> /dev/null;
rm -f $HA_DIR/bin/health_monitord 2> /dev/null;
exit 0

%clean

%files
# TODO - Verify permissions, user and groups for directory.
%defattr(-, root, root, -)
<HA_PATH>/*

%changelog
* Thu Jan 28 2021 Ajay Paratmandali <ajay.paratmandali@seagate.com> - 2.0.0
- Add new entry for dynamic_fid_service_ra
* Mon Jan 25 2021 Amol Shinde <amol.shinde@seagate.com> - 2.0.0
- Initial spec file for HA2
