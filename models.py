import logging


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
    def __init__(self, id, build_number, status):
        self.id = id
        self.build_number = build_number
        self.status = status
        self.parent = None

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
        build = Build(data["id"], data["number"], data["status"])

        # stats = team_city.get_build_statistics_by_build_id(data["id"])

        return build

    def __str__(self):
        return "{} - {} ({})".format(type(self).__name__, self.build_number, self.status)
