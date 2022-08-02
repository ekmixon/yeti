import logging
import re
from datetime import datetime, timedelta

from pytz import timezone

from core.common.utils import parse_date_to_utc
from core.errors import ObservableValidationError
from core.feed import Feed
from core.observables import Hash


class CertPaIT(Feed):

    default_values = {
        "frequency": timedelta(minutes=30),
        "name": "CertPaIT",
        "source": "https://infosec.cert-pa.it/analyze/submission.rss",
        "description": "This feed contains data from infosec.cert-pa.it",
    }

    regexes = (
        re.compile(r"IsDLL: (?P<isdll>\w+)"),
        re.compile(r"Packers: (?P<packers>\w+)"),
        re.compile(r"AntiDBG: (?P<antidbg>\w+)"),
        re.compile(r"AntiVM: (?P<antivm>\w+)"),
        re.compile(r"Signed: (?P<signed>\w+)"),
        re.compile(r"XOR: (?P<xor>\w+)"),
    )

    re_generic_details = re.compile(
        "<p>Filename: <b>(?P<filename>.*)\\</b\\><br>Filetype: (?P<filetype>.*)</p>"
    )

    def update(self):

        since_last_run = datetime.now(timezone("UTC")) - self.frequency

        for item in self.update_xml(
            "item", ["title", "link", "pubDate", "description"]
        ):
            pub_date = parse_date_to_utc(item["pubDate"])
            if self.last_run is not None and since_last_run > pub_date:
                continue

            self.analyze(item, pub_date)

    def analyze(self, item, pub_date):
        md5 = item["title"].replace("MD5: ", "")
        context = {"date_added": pub_date, "source": self.name, "url": item["link"]}
        if matched := self.re_generic_details.match(item["description"]):
            context |= matched.groupdict()

        for regex_compiled in self.regexes:
            if matched := regex_compiled.search(item["description"]):
                context.update(matched.groupdict())

        try:
            if md5:
                hash_data = Hash.get_or_create(value=md5)
                hash_data.add_context(context)
                hash_data.add_source(self.name)
        except ObservableValidationError as e:
            logging.error(e)
