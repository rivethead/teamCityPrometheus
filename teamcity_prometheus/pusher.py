from prometheus_client import CollectorRegistry, Gauge, push_to_gateway, Counter, Histogram
from models import Build


class Visitor(object):
    def __init__(self):
        super(Visitor, self).__init__()


class BuildsVisitor(Visitor):
    def __init__(self):
        super(BuildsVisitor, self).__init__()

    def visit(self, node):
        if type(node).__name__ == Build.__name__:
            print("{} = {}".format(node, type(node).__name__))


class BuildMetricsGenerator(object):
    def __init__(self):
        super(BuildMetricsGenerator, self).__init__()

    def generate(self, build):
        labels = self._create_labels(build)

        metrics = []
        for m in build.children:
            metrics.append((m.name, m.value))

        return (labels, metrics)

    @staticmethod
    def _create_labels(build):
        build_type = build.parent.name
        project = build.parent.parent.name

        return [project, build_type, build.version]
