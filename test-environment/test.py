import time
import random
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway, Counter, Histogram

if __name__ == "__main__":
    registry = CollectorRegistry()
    g1 = Gauge('teamcity_build_duration',
              'TeamCity build duration v1',
              ['project', 'build_type', 'build'],
              registry=registry)
    g2 = Gauge('teamcity_build_count',
              'TeamCity build duration v1',
              ['project', 'build_type', 'build'],
              registry=registry)

    # c = Counter('counting_runs',
    #             'Counting the number of times the test script ran', registry=registry)

    # h = Histogram('request_latency_seconds', 'Description of histogram', registry=registry)

    while True:
        random_value = random.randint(1, 100)
        g1.labels('project-1', 'build-type-11', 'build-111').set(random_value)
        random_value = random.randint(1, 100)
        g1.labels('project-1', 'build-type-11', 'build-112').set(random_value)
        random_value = random.randint(1, 100)
        g1.labels('project-1', 'build-type-11', 'build-113').set(random_value)
        random_value = random.randint(1, 100)
        g1.labels('project-1', 'build-type-12', 'build-121').set(random_value)
        random_value = random.randint(1, 100)
        g1.labels('project-1', 'build-type-13', 'build-131').set(random_value)
        random_value = random.randint(1, 100)

        random_value = random.randint(1, 5)
        g2.labels('project-1', 'build-type-11', 'build-111').set(random_value)
        random_value = random.randint(1, 5)
        g2.labels('project-1', 'build-type-11', 'build-112').set(random_value)
        random_value = random.randint(1, 5)
        g2.labels('project-1', 'build-type-11', 'build-113').set(random_value)
        random_value = random.randint(1, 5)
        g2.labels('project-1', 'build-type-12', 'build-121').set(random_value)
        random_value = random.randint(1, 5)
        g2.labels('project-1', 'build-type-13', 'build-131').set(random_value)
        random_value = random.randint(1, 5)

        push_to_gateway('localhost:9091', job='TeamCity', registry=registry)

        print("pushed")

        time.sleep(30)
