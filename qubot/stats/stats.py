from typing import Dict, Optional, Union
from datetime import date
from copy import deepcopy
from time import time

class Stats:

    def __init__(self, stat_class: str):
        self.stat_class = stat_class
        self.__stats = {}
        self.__pending_timers = {}

    def record(self, stat_name: str, event: any):
        if stat_name not in self.__stats:
            self.empty_events(stat_name)
        elif not type(self.__stats[stat_name]) is dict or "count" not in self.__stats[stat_name] or "events" not in self.__stats[stat_name]:
            raise Exception("cannot record event")
        if type(event) is dict:
            event["recorded_at"] = str(date.today())
        self.__stats[stat_name]["count"] += 1
        self.__stats[stat_name]["events"].append(event)

    def increment(self, stat_name: str, count=1):
        if stat_name not in self.__stats:
            self.empty_counter(stat_name)
        elif not isinstance(self.__stats[stat_name], int):
            raise Exception("cannot increment non-integer stat")
        self.__stats[stat_name] += count

    def decrement(self, stat_name: str, count=1):
        if stat_name not in self.__stats:
            self.empty_counter(stat_name)
        elif not isinstance(self.__stats[stat_name], int):
            raise Exception("cannot decrement non-integer stat")
        self.__stats[stat_name] -= count

    def empty_counter(self, stat_name: str):
        self.__stats[stat_name] = 0

    def empty_events(self, stat_name: str):
        self.__stats[stat_name] = {"count": 0, "events": []}

    def empty_timers(self, stat_name: str):
        self.__stats[stat_name] = {"avg_millis": 0, "max_millis": 0, "min_millis": 0, "times": []}

    def set(self, stat_name: str, value: any):
        if stat_name in self.__stats:
            raise Exception("'%s' already exists in the stats object" % stat_name)
        self.__stats[stat_name] = value

    def get(self, stat_name: str) -> Optional[Union[int, any]]:
        if stat_name not in self.__stats:
            return None
        elif isinstance(self.__stats[stat_name], int):
            return self.__stats[stat_name]
        return self.__stats[stat_name]["events"]

    def get_count(self, stat_name: str) -> int:
        if stat_name not in self.__stats:
            return 0
        elif isinstance(self.__stats[stat_name], int):
            return self.__stats[stat_name]
        return self.__stats[stat_name]["count"]

    def reset(self):
        self.__stats = {}

    def to_dict(self) -> Dict:
        return self.__stats

    def merge(self, other):
        new_stats = deepcopy(self.__stats)
        other_stats = deepcopy(other.to_dict())
        for stat_name in other_stats:
            if stat_name not in new_stats:
                new_stats[stat_name] = other_stats[stat_name]
        self.__stats = new_stats
        return self

    def start_timer(self, stat_name: str):
        self.__pending_timers[stat_name] = time() * 1000

    def stop_timer(self, stat_name: str):
        stop_millis = time() * 1000
        if stat_name not in self.__pending_timers:
            raise Exception("'%s' timer not started" % stat_name)
        if stat_name not in self.__stats:
            self.empty_timers(stat_name)
        time_millis = stop_millis - self.__pending_timers[stat_name]
        self.__stats[stat_name]["times"].append(time_millis)
        max_millis = self.__stats[stat_name]["times"][0]
        min_millis = self.__stats[stat_name]["times"][0]
        sum_millis = 0
        for time_millis in self.__stats[stat_name]["times"]:
            if time_millis > max_millis:
                max_millis = time_millis
            if time_millis < min_millis:
                min_millis = time_millis
            sum_millis += time_millis
        avg_millis = sum_millis / len(self.__stats[stat_name]["times"])
        self.__stats[stat_name]["max_millis"] = max_millis
        self.__stats[stat_name]["min_millis"] = min_millis
        self.__stats[stat_name]["avg_millis"] = avg_millis

    def __str__(self):
        return str(self.__stats)
