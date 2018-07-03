import unittest
import sys
from mock import MagicMock, Mock
from pyteamcity import TeamCity
from stubs import TeamCityCannedData, TeamCityStub

sys.path.append('../../')
from teamcity_prometheus.models import Project


class ModelTestCase(unittest.TestCase):
    def test_creating_empty_project(self):
        canned_data = TeamCityCannedData()
        actual_project = Project.from_dict(canned_data.project_1)
        actual_project.id = "project-1"

        self.assertEqual(actual_project.id, "project-1")
        self.assertEqual(actual_project.name, "project-1-name")
        self.assertEqual(0, len(actual_project.children))

    def test_populate_project_with_no_build_types(self):
        canned_data = TeamCityCannedData()
        tc_client = TeamCity()
        tc_client.get_build_types = canned_data.empty_build_types

        project = Project.from_dict(canned_data.project_1)
        project.populate(tc_client)

        self.assertEqual(0, len(project.children))

    def test_populate_project_with_multiple_build_types_with_no_builds(self):
        canned_data = TeamCityCannedData()

        tc_client = TeamCityStub()
        tc_client.get_builds = canned_data.empty_builds

        project = Project.from_dict(canned_data.project_1)
        project.populate(tc_client)

        self.assertEqual(len(canned_data.project_1["buildType"]), len(project.children))

        expected_build_types = canned_data.project_1["buildType"]

        for e in expected_build_types:
            actual_build_type = project.find(e["id"])

            self.assertIsNotNone(actual_build_type)
            self.assertEqual(e["name"], actual_build_type.name)
            self.assertEqual(0, len(actual_build_type.children))

    def test_populate_project_with_multiple_build_types_with_multiple_builds(self):
        tc_client = TeamCityStub()
        canned_data = TeamCityCannedData()

        tc_client.get_build_statistics_by_build_id = MagicMock(return_value={"property": []})

        project = Project.from_dict(canned_data.project_1)
        project.populate(tc_client)

        self.assertEqual(len(canned_data.project_1["buildType"]), len(project.children))  # two build types

        for bt in canned_data.project_1["buildType"]:
            actual_build_type = project.find(bt["id"])
            self.assertIsNotNone(actual_build_type)
            self.assertEqual(actual_build_type.name, bt["name"])
            self.assertEqual(len(actual_build_type.children), len(bt["build"]))

            # assert builds
            for b in bt["build"]:
                actual_build = actual_build_type.find(b["id"])
                self.assertIsNotNone(actual_build)
                self.assertEqual(actual_build.build_number, b["number"])
                self.assertEqual(actual_build.finished_at, b["finishDate"])
                self.assertEqual(actual_build.finished_at_ts, 1528992152000.0)
                self.assertEqual(actual_build.status, b["status"])
                self.assertEqual(actual_build.branch_name, b["branchName"])


