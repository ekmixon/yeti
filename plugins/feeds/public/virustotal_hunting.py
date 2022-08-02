import logging
from datetime import timedelta

from core import Feed
from core.config.config import yeti_config
from core.observables import Hash, File


class VirusTotalHunting(Feed):
    default_values = {
        "frequency": timedelta(minutes=5),
        "name": "VirusTotalHunting",
        "source": "https://www.virustotal.com/intelligence/hunting/",
        "description": "Feed of hunting of VirusTotal",
    }

    settings = {
        "vt_url_hunting": {
            "name": "VT Url Hunting",
            "description": "on Virus Total you can make a feed in json or xml in tab hunting",
        }
    }

    def update(self):
        api_key = yeti_config.get("vt", "key")

        if not api_key:
            raise Exception("Your VT API key is not set in the yeti.conf file")

        self.source = f"https://www.virustotal.com/intelligence/hunting/notifications-feed/?key={api_key}"

        for index, item in self.update_json(key="notifications"):
            self.analyze(item)

    def analyze(self, item):
        json_string = item.to_json()
        context = {"source": self.name}

        f_vt = File.get_or_create(value=f'FILE:{item["sha256"]}')

        sha256 = Hash.get_or_create(value=item["sha256"])

        md5 = Hash.get_or_create(value=item["md5"])

        sha1 = Hash.get_or_create(value=item["sha1"])

        f_vt.active_link_to(md5, "md5", self.name)
        f_vt.active_link_to(sha1, "sha1", self.name)
        f_vt.active_link_to(sha256, "sha256", self.name)

        tags = [item["ruleset_name"], item["type"]]
        context["raw"] = json_string
        context["size"] = item["size"]
        context["score vt"] = f'{item["positives"]}/{item["total"]}'

        f_vt.tag(tags)
        f_vt.add_context(context)
