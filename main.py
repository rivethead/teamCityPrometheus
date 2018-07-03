import logging
from teamcity_prometheus.collectors import MetricsCollector
from teamcity_prometheus.pusher import BuildsVisitor


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    collector = MetricsCollector()
    tree = collector.collect()

    build_visitor = BuildsVisitor()

    def print_to_screen(node, level):
        tabs = ("\t" * level)[:level]
        print("{}{} ({})".format(tabs, node, len(node.children)))

    tree.walk(print_to_screen)
    print("\n\n\n\n")
    tree.accept(build_visitor)

    logger.info("DONE")
