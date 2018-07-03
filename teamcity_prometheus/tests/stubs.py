class TeamCityStub(object):
    def __init__(self):
        self.canned_data = TeamCityCannedData()
        self.data = {
            "project": [self.canned_data.project_1]
        }

    def get_projects(self):
        return self.data

    def get_build_types(self, project):
        for x in self.data["project"]:
            if x["id"] == project:
                return x

        return None

    def get_builds(self, build_type_id):
        build_type = filter(
            lambda bt: bt["id"] == build_type_id, self.canned_data.build_types)

        return {"build": build_type[0]["build"]}

    def get_build_by_build_id(self, build_id):
        response = self.canned_data.builds.get(build_id, None)
        return response


class TeamCityCannedData(object):
    def __init__(self):
        self.project_1_build_type_1_build_1 = {
            "id": "build-type-1-build-1",
            "number": "1.0.0.1",
            "status": "SUCCESS",
            "branchName": "master",
            "finishDate": "20180614T160232+0000"
        }
        self.project_1_build_type_1 = {
            "id": "build-type-1",
            "name": "build-type-1-name",
            "build": [self.project_1_build_type_1_build_1]
        }

        self.project_1_build_type_2_build_1 = {
            "id": "build-type-2-build-1",
            "number": "1.0.0.2",
            "status": "SUCCESS",
            "branchName": "master",
            "finishDate": "20180614T160232+0000"
        }
        self.project_1_build_type_2_build_2 = {
            "id": "build-type-2-build-2",
            "number": "1.0.0.2",
            "status": "SUCCESS",
            "branchName": "master",
            "finishDate": "20180614T160232+0000"
        }
        self.project_1_build_type_2_build_3 = {
            "id": "build-type-2-build-3",
            "number": "1.0.1.2",
            "status": "FAILURE",
            "branchName": "other-branch",
            "finishDate": "20180614T160232+0000"
        }

        self.project_1_build_type_2 = {
            "id": "build-type-2",
            "name": "build-type-2-name",
            "build": [
                self.project_1_build_type_2_build_1,
                self.project_1_build_type_2_build_2,
                self.project_1_build_type_2_build_3
            ]
        }

        self.build_types = [self.project_1_build_type_1,
                            self.project_1_build_type_2]
        self.builds = {
            self.project_1_build_type_2_build_1["id"]: self.project_1_build_type_2_build_1,
            self.project_1_build_type_2_build_2["id"]: self.project_1_build_type_2_build_2,
            self.project_1_build_type_2_build_3["id"]: self.project_1_build_type_2_build_3,
            self.project_1_build_type_1_build_1["id"]: self.project_1_build_type_1_build_1,
        }

        self.project_1 = {
            "id": "project-1",
            "name": "project-1-name",
            "buildType": [self.project_1_build_type_1,
                          self.project_1_build_type_2]
        }

        super(TeamCityCannedData, self).__init__()

    def empty_build_types(self, project=None):
        return {"buildType": []}

    def empty_builds(self, build_type_id=None):
        return {"build": []}
