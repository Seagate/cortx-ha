#!/usr/bin/env python3

# Copyright (c) 2021 Seagate Technology LLC and/or its Affiliates
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

from ha import const
from ha.execute import SimpleCommand
from ha.core.controller.element_controller import ElementController
from ha.core.error import HAUnimplemented

class PcsClusterController(ElementController):
    """
    Pcs cluster controller to perform pcs cluster level operation.
    """
    def __init__(self):
        """
        Initalize pcs cluster controller
        """
        super(PcsClusterController, self).__init__()
        self._execute = SimpleCommand()

    def _validate(self, args) -> None:
        """
        Validate args.

        Args:
            args ([dict]): cluster args

        {element: cluster, action: <start|stop|standby|active>,
        args: {process_type: <sync|async>}}
        """
        pass

    def remove_node(self):
        raise HAUnimplemented("Cluster remove node is not supported.")

    def add_node(self):
        raise HAUnimplemented("Cluster add node is not supported.")

    def start(self) -> None:
        Log.debug("Executing cluster start")
        _output, _err, _rc = self._execute.run_cmd(const.HCTL_START, check_error=False)
        Log.info(f"IO stack started. Output: {_output}, Err: {_err}, RC: {_rc}")
        self.status()
        if self._responce.get_rc() == 0:
            Log.info("Cluster started successfully")
            self._responce.output("Cluster started successfully")
            self._responce.rc(0)
        else:
            Log.error("Cluster failed to start")
            self._responce.output("Cluster failed to start")
            self._responce.rc(1)

    def stop(self) -> None:
        Log.info("Executing cluster Stop")
        _output, _err, _rc = self._execute.run_cmd(const.HCTL_STOP, check_error=False)
        Log.info(f"Io stack stopped successfully. Output: {_output}, Err: {_err}, RC: {_rc}")
        self.status()
        if self._responce.get_rc() == 1:
            Log.info("Cluster stopped successfully")
            self._responce.output("Cluster stopped successfully...")
            self._responce.rc(0)
        else:
            Log.error("Cluster failed to stop")
            self._responce.output("Cluster failed to stop")
            self._responce.rc(1)

    def status(self) -> None:
        _output, _err, _rc = self._execute.run_cmd(const.HCTL_STATUS, check_error=False)
        self._responce.rc(_rc)
        status = const.HCTL_STARTED_STATUS if _rc == 0 else const.HCTL_STOPPED_STATUS
        self._responce.output(status)

    def standby(self) -> None:
        raise HAUnimplemented("This feature is not implemented")

    def active(self) -> None:
        raise HAUnimplemented("This feature is not implemented")