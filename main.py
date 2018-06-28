from prometheus_client import CollectorRegistry, Gauge, push_to_gateway
from pyteamcity import TeamCity
import logging
import threading
import time
from threading import Thread
from teamCityPrometheus import MetricsCollector


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    collector = MetricsCollector()
    tree = collector.collect()

    def print_to_screen(node, level):
        tabs = ("\t" * level)[:level]
        print("{}{} ({})".format(tabs, node, len(node.children)))

    tree.walk(print_to_screen)

    logger.info("DONE")
