#!/usr/bin/python
"""Tests for the .info() method

Hits the HTTP interface in ways which call the various .info() methods.
"""


import sys
from os import path

import unittest
import requests

YETI_ROOT = path.normpath(
    path.dirname(path.dirname(path.dirname(path.abspath(__file__))))
)
sys.path.append(YETI_ROOT)

from core.config.config import yeti_config, Dictionary

YETI_SERVICE = getattr(yeti_config, "yeti", Dictionary(host="localhost", port=5000))

SAMPLE_DOMAIN = "example.com"
SAMPLE_SOURCE = "Yeti_Test"

SAMPLE_OBSERVABLE = {
    "value": f"http://{SAMPLE_DOMAIN}/yeti-test",
    "tags": [SAMPLE_SOURCE],
    "source": SAMPLE_SOURCE,
    "context": {},
}

SAMPLE_ACTOR = {
    "type": "Actor",
    "name": "Joe's Garage",
    "description": "Joe's is the place",
    "tags": [SAMPLE_SOURCE],
}
SAMPLE_INDICATOR = {
    "diamond": "capability",
    "name": "Joe scanner",
    "pattern": "[Jj]oe",
    "location": "network",
    "type": "Regex",
    "description": SAMPLE_SOURCE,
}


class ObservableInfo(unittest.TestCase):
    """Calls core.observables.observable.Observable.info()"""

    def setUp(self):
        self.id = None
        self.url = None
        self.ok_to_delete = False
        return

    def tearDown(self):
        if self.ok_to_delete:
            resp = requests.delete(self.url, headers={"Accept": "application/json"})
        return

    def test_info(self):
        resp = requests.post(
            f"http://{YETI_SERVICE.host}:{YETI_SERVICE.port}/api/observable/",
            json=SAMPLE_OBSERVABLE,
            headers={"Accept": "application/json"},
        )

        self.assertEqual(resp.status_code, 200, "Expected 200 status")

        self.assertTrue("id" in resp.json(), "Expected 'id' in response")

        self.id = resp.json()["id"]
        self.assertTrue("url" in resp.json(), "Expected 'url' in response")

        self.url = resp.json()["url"]
        self.assertEqual(
            resp.json()["value"],
            SAMPLE_OBSERVABLE["value"],
            f'Expected to see {SAMPLE_OBSERVABLE["value"]} as value',
        )


        self.assertTrue(self.id in self.url, "url should contain id")
        self.ok_to_delete = True
        return


class EntityInfo(unittest.TestCase):
    """Calls core.entities.entity.Entity.info()"""

    BASE_URL = "http://{}:{}/api/entity/".format(YETI_SERVICE.host, YETI_SERVICE.port)

    def setUp(self):
        self.url = None
        self.ok_to_delete = False
        return

    def tearDown(self):
        if self.ok_to_delete:
            resp = requests.delete(self.url, headers={"Accept": "application/json"})
        return

    def test_info(self):
        resp = requests.post(
            EntityInfo.BASE_URL,
            json=SAMPLE_ACTOR,
            headers={"Accept": "application/json"},
        )

        self.assertEqual(resp.status_code, 200, "Expected 200 status")

        self.assertTrue("url" in resp.json(), "Expected 'url' in response")

        self.url = resp.json()["url"]
        self.assertEqual(
            resp.json()["name"],
            SAMPLE_ACTOR["name"],
            f'Expected to see {SAMPLE_ACTOR["name"]} as name',
        )


        self.assertTrue(EntityInfo.BASE_URL in self.url, "url should contain BASE_URL")
        self.ok_to_delete = True
        return


class IndicatorInfo(unittest.TestCase):
    """Calls core.indicators.indicator.Indicator.info()"""

    BASE_URL = "http://{}:{}/api/indicator/".format(
        YETI_SERVICE.host, YETI_SERVICE.port
    )

    def setUp(self):
        self.url = None
        self.ok_to_delete = False
        return

    def tearDown(self):
        if self.ok_to_delete:
            resp = requests.delete(self.url, headers={"Accept": "application/json"})
        return

    def test_info(self):
        resp = requests.post(
            IndicatorInfo.BASE_URL,
            json=SAMPLE_INDICATOR,
            headers={"Accept": "application/json"},
        )

        self.assertEqual(resp.status_code, 200, "Expected 200 status")

        self.assertTrue("url" in resp.json(), "Expected 'url' in response")

        self.url = resp.json()["url"]
        self.assertEqual(
            resp.json()["name"],
            SAMPLE_INDICATOR["name"],
            f'Expected to see {SAMPLE_INDICATOR["name"]} as name',
        )


        self.assertTrue(
            IndicatorInfo.BASE_URL in self.url, "url should contain BASE_URL"
        )
        self.ok_to_delete = True
        return


if __name__ == "__main__":
    unittest.main(verbosity=2)
