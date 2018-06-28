import logging
import dateutil.parser
import time
import datetime
import pytz


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
        Project.logger.info("Populating project '{}' from TeamCity".format(self.name))

        build_types = team_city.get_build_types(project=self.id)

        Project.logger.debug("Got %s build types for project '%s'",
                            len(build_types["buildType"]), self.name)

        for bt in build_types["buildType"]:
            build_type = BuildType.from_dict(bt, team_city)

            Project.logger.debug("Adding build type '{}' to project '{}'".format(build_type.name, self.name))

            self.parent.append(build_type)
            break

        Project.logger.info("Project '{}' populated".format(self.name))

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

        BuildType.logger.debug("Getting builds for build type '{}'".format(new_build_type.id))

        builds = team_city.get_builds(build_type_id=new_build_type.id)

        BuildType.logger.debug("Got {} builds for build type '{}'".format(len(builds["build"]), new_build_type.name))

        for b in builds["build"]:
            build = Build.from_dict(
                team_city.get_build_by_build_id(b["id"]), team_city)

            BuildType.logger.debug("Adding build '{}' to build type '{}'".format(build.build_number, new_build_type.name))

            new_build_type.append(build)

        return new_build_type

    def __str__(self):
        return "{} - {}".format(type(self).__name__, self.name)


class Build(Node):
    logger = logging.getLogger(__name__)
    epoch_date = datetime.datetime(
        1970, 1, 1, 0, 0, 0, tzinfo=pytz.timezone('UTC'))

    def __init__(self, id, build_number, status, branch, finish_date):
        self.id = id
        self.build_number = build_number
        self.status = status
        self.parent = None
        self.branch_name = branch
        self.finished_at = finish_date
        self.finished_at_ts = (dateutil.parser.parse(
            finish_date) - Build.epoch_date).total_seconds() * 1000

        super(Build, self).__init__(id, build_number)

    def metrics(self):
        pass

    def belongs_to_node(self, node):
        self.parent = node
        return self

    def populate(self, team_city):
        pass

    @staticmethod
    def from_dict(data, team_city):
        build = Build(data["id"], data["number"], data["status"],
                      data["branchName"], data["finishDate"])

        stats = team_city.get_build_statistics_by_build_id(data["id"])

        for p in filter(lambda p: not p["name"].startswith("buildStageDuration"), stats["property"]):
            build.append(Metric(p["name"], p["value"], build.finished_at_ts))

        return build

    def __str__(self):
        return "{} - {} ({}) on {} branch and finished at {}".format(
            type(self).__name__, self.build_number, self.status, self.branch_name, self.finished_at_ts)


class Metric(Node):
    def __init__(self, name, value, as_at):
        self.name = name
        self.value = float(value)

        super(Metric, self).__init__(name, name)

    def __str__(self):
        return "{} == {}".format(self.name, self.value)
