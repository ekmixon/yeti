import sys
import logging
from os import path

YETI_ROOT = path.normpath(path.dirname(path.dirname(path.abspath(__file__))))
sys.path.append(YETI_ROOT)

from core.analytics import OneShotAnalytics
from core.scheduling import Scheduler
from core.observables import Observable

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    Scheduler()

    if len(sys.argv) == 1:
        print("Re-run using a analytic name as argument")
        for f in OneShotAnalytics.objects():
            print(f"  {f.name}")

    if len(sys.argv) > 1:
        name = sys.argv[1]
        f = OneShotAnalytics.objects.get(name=name)
        print(f"Running {f.name}...")
        observable = Observable.guess_type(sys.argv[2]).get_or_create(value=sys.argv[2])
        f.analyze(observable, {})
