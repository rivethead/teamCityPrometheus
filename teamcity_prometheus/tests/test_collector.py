import unittest
import sys
from mock import MagicMock, Mock
from pyteamcity import TeamCity
from stubs import TeamCityCannedData, TeamCityStub

sys.path.append('../../')
from teamcity_prometheus.models import Project
from teamcity_prometheus.collectors import MetricsCollector


class CollectorTestCase(unittest.TestCase):
    def test_collecting_flat_project_structure(self):
        collector = MetricsCollector()
