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
License: Seagate Proprietary
URL: https://github.com/Seagate/cortx-ha
Source0: <RPM_NAME>-%{version}.tar.gz
#TODO: Dependency on Hare rpm
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
mkdir -p $HA_DIR/bin /usr/bin

# Move binary file
ln -sf $HA_DIR/lib/hw_comp_ra $HA_DIR/bin/hw_comp_ra
ln -sf $HA_DIR/lib/iem_comp_ra $HA_DIR/bin/iem_comp_ra
ln -sf $HA_DIR/lib/cortxha $HA_DIR/bin/cortxha
ln -sf $HA_DIR/lib/cortxha /usr/bin/cortxha
exit 0

%preun
exit 0

%postun
[ $1 -eq 1 ] && exit 0
HA_DIR=<HA_PATH>/ha
rm -f $HA_DIR/bin/hw_comp_ra 2> /dev/null;
rm -f $HA_DIR/bin/iem_comp_ra 2> /dev/null;
rm -f /usr/bin/cortxha 2> /dev/null;
rm -f $HA_DIR/bin/cortxha 2> /dev/null;
exit 0

%clean

%files
# TODO - Verify permissions, user and groups for directory.
%defattr(-, root, root, -)
<HA_PATH>/*

%changelog
* Mon Jan 25 2021 Amol Shinde <amol.shinde@seagate.com> - 2.0.0
- Initial spec file for HA2