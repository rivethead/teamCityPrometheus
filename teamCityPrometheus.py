import logging
import threading
import time
from threading import Thread
from pyteamcity import TeamCity


class Node(object):
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.children = []
        # self.data.belongs_to_node(self)

    def append(self, node):
        node.parent = self
        self.children.append(node)

    def find(self, id):
        if self.id == id:
            return self

        for c in self.children:
            found = c.find(id)

            if not found is None:
                return found

        return None

    def walk(self, func, level=0):
        func(self, level)

        for c in self.children:
            c.walk(func, level + 1)

    def __str__(self):
        return self.id


class Metric(object):
    def __init__(self, name, value):
        self.name = name
        self.value = value


class Project(Node):
    logger = logging.getLogger(__name__)

    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.node = None

        super(Project, self).__init__(id, name)

    def belongs_to_node(self, node):
        self.parent = node
        return self

    @staticmethod
    def from_dict(data):
        return Project(data["id"], data["name"])

    def populate(self, team_city):
        Project.logger.info("Getting build types for project '%s'", self.name)

        build_types = team_city.get_build_types(project=self.id)

        Project.logger.info("Got %s build types for project '%s'",
                            len(build_types["buildType"]), self.name)

        for bt in build_types["buildType"]:
            build_type = BuildType.from_dict(bt, team_city)

            Project.logger.info("Adding build type '%s' to project '%s'",
                                build_type.name, self.name)

            self.parent.append(build_type)

    def __str__(self):
        return "{} - {}".format(type(self).__name__, self.name)


class BuildType(Node):
    logger = logging.getLogger(__name__)

    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.parent = None

        super(BuildType, self).__init__(id, name)

    def belongs_to_node(self, node):
        self.parent = node
        return self

    def metrics(self):
        return self.parent.children

    def populate(self, team_city):
        pass

    @staticmethod
    def from_dict(data, team_city):
        new_build_type = BuildType(data["id"], data["name"])

        BuildType.logger.info("Getting builds for build type '%s'",
                              new_build_type.id)

        builds = team_city.get_builds(build_type_id=new_build_type.id)

        BuildType.logger.info("Got %s builds for build type '%s'",
                              len(builds["build"]), new_build_type.name)

        for b in builds["build"]:
            build = Build.from_dict(b, team_city)

            BuildType.logger.info("Adding build '%s' to build type '%s'",
                                  build.build_number, new_build_type.name)

            new_build_type.append(build)

        return new_build_type

    def __str__(self):
        return "{} - {}".format(type(self).__name__, self.name)


class Build(Node):
    BUILD_STATUS = "status"
    BUILD_DURATION = "duration"
    BUILD_TEST_STATUS = "test_status"

    def __init__(self, id, build_number, status):
        self.id = id
        self.build_number = build_number
        self.status = status
        self.parent = None
        self.build_metrics = [
            Metric(Build.BUILD_STATUS, 1 if status == "SUCCESS" else 0),
            Metric(Build.BUILD_DURATION, 0)]

        super(Build, self).__init__(id, build_number)

    def metrics(self):
        return self.build_metrics

    def belongs_to_node(self, node):
        self.parent = node
        return self

    def populate(self, team_city):
        pass

    @staticmethod
    def from_dict(data, team_city):
        build = Build(data["id"], data["number"], data["status"])

        # stats = team_city.get_build_statistics_by_build_id(data["id"])

        return build

    def __str__(self):
        return "{} - {} ({})".format(type(self).__name__, self.build_number, self.status)


class MetricsCollector(object):
    logger = logging.getLogger(__name__)

    def __init__(self):
        self.threads = []

    def collect(self):
        tc = self._create_team_city_connection()

        MetricsCollector.logger.info("Getting projects from TeamCity")

        projects = tc.get_projects()

        MetricsCollector.logger.info("Got %s projects from TeamCity",
                                     len(projects["project"]))

        filtering = CollectorFilter()

        root = Project("_Root", "Root Project")

        for p in filter(lambda p: p["id"] != root.id, projects["project"]):
            project = Project.from_dict(p)
            if not filtering.include(project):
                MetricsCollector.logger.debug(
                    "Ignoring project {}".format(project))
                continue

            parent = root.find(p["parentProjectId"])

            MetricsCollector.logger.info("Adding '%s' to the project '%s'",
                                         project.name, parent.name)

            parent.append(project)

        self.threads = []
        root.walk(self._collect)

        self._wait_for_population_to_complete()

        return root

    def _collect(self, node, level):
        thread = Thread(name=node.name, target=node.populate,
                        args=(self._create_team_city_connection(),))
        thread.setDaemon(False)
        self.threads.append(thread)

        thread.start()

    def _wait_for_population_to_complete(self):
        number_of_threads_running = len(self.threads)
        max_wait_time = 300  # in seconds
        time_waited = 0
        wait_time = 5  # in seconds

        MetricsCollector.logger.info(
            "Waiting for %s threads to collect the TeamCity structure", number_of_threads_running)

        while number_of_threads_running > 0 and time_waited < max_wait_time:
            MetricsCollector.logger.info("%s thread(s) running populating structure. Time waited thus far is %s out of %s",
                                         number_of_threads_running, time_waited, max_wait_time)
            number_of_threads_running = len(
                filter(lambda t: t.isAlive(), self.threads))

            time.sleep(wait_time)
            time_waited = time_waited + wait_time

    def _create_team_city_connection(self):
        tc_url = 'teamcity.structureit.net'
        tc_username = 'administrator'

        tc = TeamCity(tc_username, 'Galeforce8+',
                      tc_url, protocol='https', port=443)

        return tc


class CollectorFilter(object):
    def __init__(self):
        self._include = ["homestead"]
        super(CollectorFilter, self).__init__()

    def include(self, node):
        return unicode.lower(node.name) in self._include


class CollectorIncludeFilter(object):
    def __init__(self, include=[]):
        self._include = [] if include is None else include
        super(CollectorIncludeFilter, self).__init__()


class CollectionFilter(object):
    def __init__(self, projects=[], build_types=[], builds=[]):
        self.projects = [] if projects is None else projects
        self.build_types = [] if build_types is None else build_types
        self.builds = [] if builds is None else builds

        super(CollectionFilter, self).__init__()
