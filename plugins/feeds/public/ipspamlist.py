import logging
from datetime import timedelta

from dateutil import parser

from core import Feed
from core.errors import ObservableValidationError
from core.observables import Ip


class IPSpamList(Feed):
    default_values = {
        "frequency": timedelta(days=1),
        "name": "IPSpamList",
        "source": "http://www.ipspamlist.com/public_feeds.csv",
        "description": "Service provided by NoVirusThanks that keeps track of malicious "
        "IP addresses engaged in hacking attempts, spam comments",
    }

    def update(self):

        for index, line in self.update_csv(delimiter=",", filter_row="first_seen"):
            self.analyze(line)

    def analyze(self, line):

        context = {
            "source": self.name,
            "threat": line["category"],
            "first_seen": line["first_seen"],
            "last_seen": parser.parse(line["last_seen"]),
            "attack_count": line["attacks_count"],
        }
        ip_address = line["ip_address"]
        try:
            ip_obs = Ip.get_or_create(value=ip_address)
            ip_obs.tag(context["threat"])
            ip_obs.add_source(self.name)
            ip_obs.add_context(context)
        except ObservableValidationError as e:
            logging.error(f"Error in IP format {ip_address} {e}")
