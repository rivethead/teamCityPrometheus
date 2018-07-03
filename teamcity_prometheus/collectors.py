import logging
import threading
import time
from threading import Thread
from pyteamcity import TeamCity
from models import Project


class MetricsCollector(object):
    logger = logging.getLogger(__name__)

    def __init__(self, teamcity_client=None):
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
                MetricsCollector.logger.debug("Ignoring project {}".format(project))
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
