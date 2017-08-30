#!/usr/bin/python
from __future__ import unicode_literals

import time
import datetime
import threading

from . import core


class _RegularClear(threading.Thread):
    def __init__(self, interval, registry=core.REGISTRY):
        super(_RegularClear, self).__init__()
        self._interval = interval
        self._registry = registry

    def run(self):
        is_done = False
        while True:
            # reset at the last 5 second of every minute
            second = datetime.datetime.now().second
            if not is_done and second >= 55:
                is_done = True
                for name in self._registry._names_to_collectors:
                    collector = self._registry._names_to_collectors[name]
                    for metric in collector.collect():
                        if metric.type == 'summary':
                            collector.reset()
                            break
            elif is_done and second < 55:
                is_done = False
            time.sleep(1)


class Task(object):
    def __init__(self, registry=core.REGISTRY):
        self._registry = registry

    def start(self, interval=60.0):
        t_clear = _RegularClear(interval, self._registry)
        t_clear.daemon = True
        t_clear.start()
