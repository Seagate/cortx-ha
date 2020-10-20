#!/bin/sh
#
# Copyright (C) 2015 Andrew Beekhof <andrew@beekhof.net>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
##############################################################################
# Sample configuration (cib fragment in xml notation)
# ================================
# <configuration>
#   <alerts>
#     <alert id="alert_sample" path="/path/to/alert_file.sh">
#       <instance_attributes id="config_for_alert_file">
#         <nvpair id="debug_option_1" name="debug_exec_order" value="false"/>
#       </instance_attributes>
#       <meta_attributes id="config_for_timestamp">
#         <nvpair id="ts_fmt" name="timestamp-format" value="%H:%M:%S.%06N"/>
#       </meta_attributes>
#       <recipient id="logfile_destination" value="/path/to/logfile"/>
#     </alert>
#   </alerts>
# </configuration>

# No one will probably ever see this echo, unless they run the script manually.
# An alternative would be to log to the system log, or similar. (We can't send
# this to the configured recipient, because that variable won't be defined in
# this case either.)
if [ -z $CRM_alert_version ]; then
    echo "$0 must be run by Pacemaker version 1.1.15 or later"
    exit 0
fi

# Alert agents must always handle the case where no recipients are defined,
# even if it's a no-op (a recipient might be added to the configuration later).
if [ -z "${CRM_alert_recipient}" ]; then
    echo "$0 requires a recipient configured with a full filename path"
    exit 0
fi

debug_exec_order_default="false"

# Pacemaker passes instance attributes to alert agents as environment variables.
# It is completely up to the agent what instance attributes to support.
# Here, we define an instance attribute "debug_exec_order".
: ${debug_exec_order=${debug_exec_order_default}}

if [ "${debug_exec_order}" = "true" ]; then
    tstamp=`printf "%04d. " "$CRM_alert_node_sequence"`
    if [ ! -z "$CRM_alert_timestamp" ]; then
        tstamp="${tstamp} $CRM_alert_timestamp (`date "+%H:%M:%S.%06N"`): "
    fi
else
    if [ ! -z "$CRM_alert_timestamp" ]; then
        tstamp="$CRM_alert_timestamp: "
    fi
fi

IEM_EVENT=/etc/cortx/ha/iem_ha.csv

case $CRM_alert_kind in
    node)
        echo "${tstamp}Node '${CRM_alert_node}' is now '${CRM_alert_desc}'" >> "${CRM_alert_recipient}"
        msg=$(grep "${CRM_alert_node} ${CRM_alert_desc}" ${IEM_EVENT} | awk -F',' '{print $2}') && {
            logger $msg
        } || true
        ;;
    fencing)
        # Other keys:
        #
        # CRM_alert_node
        # CRM_alert_task
        # CRM_alert_rc
        #
        echo "${tstamp}Fencing ${CRM_alert_desc}" >> "${CRM_alert_recipient}"
        ;;
    resource)
        # Other keys:
        #
        # CRM_alert_target_rc
        # CRM_alert_status
        # CRM_alert_rc
        #
        if [ ${CRM_alert_interval} = "0" ]; then
            CRM_alert_interval=""
        else
            CRM_alert_interval=" (${CRM_alert_interval})"
        fi

        if [ ${CRM_alert_target_rc} = "0" ]; then
            CRM_alert_target_rc=""
        else
            CRM_alert_target_rc=" (target: ${CRM_alert_target_rc})"
        fi

        case ${CRM_alert_desc} in
            Cancelled) ;;
            *)
                echo "${tstamp}Resource operation '${CRM_alert_task}${CRM_alert_interval}' for '${CRM_alert_rsc}' on '${CRM_alert_node}': ${CRM_alert_desc}${CRM_alert_target_rc}" >> "${CRM_alert_recipient}"
                ;;
        esac
        ;;
    attribute)
        #
        echo "${tstamp}Attribute '${CRM_alert_attribute_name}' on node '${CRM_alert_node}' was updated to '${CRM_alert_attribute_value}'" >> "${CRM_alert_recipient}"
        ;;

    *)
        echo "${tstamp}Unhandled $CRM_alert_kind alert" >> "${CRM_alert_recipient}"
        env | grep CRM_alert >> "${CRM_alert_recipient}"
        ;;
esac