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

import logging
from pcswrap.exception import TimeoutException
from time import sleep


class Waiter:
    def __init__(self,
                 title: str = '',
                 provider_fn=None,
                 predicate=None,
                 pause_seconds=2,
                 timeout_seconds=120):
        assert provider_fn
        assert predicate
        self.provider_fn = provider_fn
        self.predicate = predicate
        self.pause_seconds = pause_seconds
        self.timeout_seconds = timeout_seconds
        self.title = title

    def wait(self):
        time_left = self.timeout_seconds
        msg = self.title
        logging.debug(
            f'Waiting for condition "{msg}", timeout = {time_left} sec')
        while True:
            data = self.provider_fn()
            ok = self.predicate(data)
            logging.debug(f'{msg}? - {ok}')
            if ok:
                logging.debug(f'Condition "{msg}" is met, exiting')
                return
            time_left = time_left - self.pause_seconds
            if time_left <= 0:
                logging.debug(f'Condition "{msg}" is not met,'
                              ' exiting by timeout')
                raise TimeoutException()
            sleep(self.pause_seconds)
