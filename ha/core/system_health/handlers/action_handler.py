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

from ha.core.event_manager.model.action_event import RecoveryActionEvent
from ha.core.event_manager.event_manager import EventManager
from ha.core.system_health.model.health_event import HealthEvent
from ha.core.system_health.const import EVENT_ACTIONS, HEALTH_STATUSES
from ha.core.event_manager.error import InvalidEvent, InvalidAction
from ha.core.error import HAUnimplemented


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
        publish = False
        if EVENT_ACTIONS.PUBLISH.value in action:
            publish = True
        # Take any defined HA actions.
        if event.event_type == HEALTH_STATUSES.ONLINE:
            self.on_online(event, publish)
        elif event.event_type == HEALTH_STATUSES.DEGRADED:
            self.on_degraded(event, publish)
        elif event.event_type == HEALTH_STATUSES.OFFLINE:
            self.on_offline(event, publish)
        elif event.event_type == HEALTH_STATUSES.FAILED:
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
        self.event_manager.publish(event.resource_type, recovery_action_event)

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
        if EVENT_ACTIONS.PUBLISH.value in action and len(action) == 1:
            self.publish_event(event)
        else:
            raise InvalidAction()


class NodeFruPSUActionHandler(ActionHandler):
    """
    Node Fru PSU action handler
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
        # E.g. start some service then publish
        if publish:
            self.publish_event(event)

    def on_failure(self, event: HealthEvent, publish: bool) -> None:
        """
        on failure event handle
        Args:
            event (HealthEvent): HealthEvent object
            publish (bool): publish bool variable

        Returns:
            None
        """
        if publish:
            self.publish_event(event)
        # E.g. stop some service after publish


class NodeFruFanActionHandler(ActionHandler):
    """
    Node Fru Fan action handler
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
        # E.g. start some service then publish
        if publish:
            self.publish_event(event)

    def on_failure(self, event: HealthEvent, publish: bool) -> None:
        """
        on failure event handle
        Args:
            event (HealthEvent): HealthEvent object
            publish (bool): publish bool variable

        Returns:
            None
        """
        if publish:
            self.publish_event(event)
        # E.g. stop some service after publish


class NodeSWActionHandler(ActionHandler):
    """
    Node SW action handler
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
        # E.g. start some service then publish
        if publish:
            self.publish_event(event)

    def on_failure(self, event: HealthEvent, publish: bool) -> None:
        """
        on failure event handle
        Args:
            event (HealthEvent): HealthEvent object
            publish (bool): publish bool variable

        Returns:
            None
        """
        if publish:
            self.publish_event(event)
        # E.g. stop some service after publish
