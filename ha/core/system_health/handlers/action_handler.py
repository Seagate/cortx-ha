#!/usr/bin/env python3

# Copyright (c) 2021 Seagate Technology LLC and/or its Affiliates
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
# For any questions about this software or licensing,
# please email opensource@seagate.com or cortx-questions@seagate.com.

from cortx.utils.log import Log

from ha.core.error import HAUnimplemented
from ha.core.event_manager.error import InvalidEvent, InvalidAction
from ha.core.event_manager.event_manager import EventManager
from ha.core.event_manager.model.action_event import RecoveryActionEvent
from ha.core.health_monitor.const import HEALTH_MON_ACTIONS
from ha.core.system_health.const import HEALTH_STATUSES
from ha.core.system_health.model.health_event import HealthEvent


class ActionHandler:
    """
    Base action handler
    """

    def __init__(self):
        self.event_manager = EventManager()

    def act(self, event: HealthEvent, action: list) -> None:
        """
        act on the event handled
        Args:
            event (HealthEvent): HealthEvent object
            action (list): Actions list.

        Returns:
            None
        """
        Log.info(f"Action handler with Event: {event} and actions : {action}")
        publish = False
        if HEALTH_MON_ACTIONS.PUBLISH_ACT.value in action:
            publish = True
        if event.event_type == HEALTH_STATUSES.ONLINE.value:
            self.on_online(event, publish)
        elif event.event_type == HEALTH_STATUSES.DEGRADED.value:
            self.on_degraded(event, publish)
        elif event.event_type == HEALTH_STATUSES.OFFLINE.value:
            self.on_offline(event, publish)
        elif event.event_type == HEALTH_STATUSES.FAILED.value:
            self.on_failure(event, publish)
        else:
            # No HA action
            raise InvalidEvent()

    def publish_event(self, event: HealthEvent) -> None:
        """
        publish event
        Args:
            event (HealthEvent): HealthEvent object

        Returns:
            None
        """
        # Create RecoveryActionEvent and call publish
        recovery_action_event = RecoveryActionEvent(event)
        self.event_manager.publish(recovery_action_event)

    def on_failure(self, event: HealthEvent, publish: bool) -> None:
        """
        on failure event handle
        Args:
            event (HealthEvent): HealthEvent object
            publish (bool): publish bool variable

        Returns:
            None
        """
        raise HAUnimplemented()

    def on_online(self, event: HealthEvent, publish: bool) -> None:
        """
        on online event handle
        Args:
            event (HealthEvent): HealthEvent object
            publish (bool): publish bool variable

        Returns:
            None
        """
        raise HAUnimplemented()

    def on_offline(self, event: HealthEvent, publish: bool) -> None:
        """
        on offline event handle
        Args:
            event (HealthEvent): HealthEvent object
            publish (bool): publish bool variable

        Returns:
            None
        """
        raise HAUnimplemented()

    def on_degraded(self, event: HealthEvent, publish: bool) -> None:
        """
        on degraded event handle
        Args:
            event (HealthEvent): HealthEvent object
            publish (bool): publish bool variable

        Returns:
            None
        """
        raise HAUnimplemented()


class DefaultActionHandler(ActionHandler):
    """
    Default action handler
    """

    def __init__(self):
        super().__init__()

    def act(self, event: HealthEvent, action: list) -> None:
        """
        act on the event handled in default action handler
        Args:
            event (HealthEvent): HealthEvent object
            action (list): Actions list.

        Returns:
            None
        """
        Log.info(f"Default action handler with Event: {event} and actions : {action}")
        if HEALTH_MON_ACTIONS.PUBLISH_ACT.value in action and len(action) == 1:
            self.publish_event(event)
        else:
            raise InvalidAction()


class NodeFailureActionHandler(ActionHandler):
    """
    Node failure action handler
    """

    def __init__(self):
        super().__init__()

    def on_online(self, event: HealthEvent, publish: bool) -> None:
        """
        on online event handle
        Args:
            event (HealthEvent): HealthEvent object
            publish (bool): publish bool variable

        Returns:
            None
        """
        Log.info(f"Handling node online event.")
        if publish:
            self.publish_event(event)

    def on_offline(self, event: HealthEvent, publish: bool) -> None:
        """
        on offline event handle
        Args:
            event (HealthEvent): HealthEvent object
            publish (bool): publish bool variable

        Returns:
            None
        """
        Log.info(f"Handling node offline event.")
        if publish:
            self.publish_event(event)
