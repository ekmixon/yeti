import logging
from datetime import timedelta

from core.errors import ObservableValidationError
from core.feed import Feed
from core.observables import Ip


class FeodoTrackerIPBlockList(Feed):
    default_values = {
        "frequency": timedelta(hours=24),
        "name": "FeodoTrackerIPBlocklist",
        "source": "https://feodotracker.abuse.ch/downloads/ipblocklist.csv",
        "description": "Feodo Tracker IP Feed. This feed shows a full list C2s.",
    }

    def update(self):
        for firs_line, (index, line) in enumerate(self.update_csv(
            delimiter=",",
            filter_row="first_seen_utc",
            names=[
                "first_seen_utc",
                "dst_ip",
                "dst_port",
                "c2_status",
                "last_online",
                "malware",
            ],
        )):
            if firs_line != 0:
                self.analyze(line)

    # pylint: disable=arguments-differ
    def analyze(self, line):

        tags = [line["malware"].lower(), "c2", "blocklist"]
        context = {
            "first_seen": line["first_seen_utc"],
            "source": self.name,
            "last_online": line["last_online"],
            "c2_status": line["c2_status"],
            "port": line["dst_port"],
        }

        try:
            ip_obs = Ip.get_or_create(value=line["dst_ip"])
            ip_obs.add_context(context, dedup_list=["last_online"])
            ip_obs.tag(tags)

        except ObservableValidationError as e:
            logging.error(f"Invalid line: {e}\nLine: {line}")
