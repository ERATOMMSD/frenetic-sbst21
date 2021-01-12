import numpy as np
import math
import logging as log
import os

from code_pipeline.tests_generation import RoadTestFactory


class FileBasedGenerator():
    """
        Generates a single test based on road_points.txt file in src/data/ folder
    """

    def __init__(self, time_budget=None, executor=None, map_size=None):
        self.time_budget = time_budget
        self.executor = executor
        self.map_size = map_size

    def start(self):
        log.info("Starting test generation")

        road_points = []

        # TODO: this can be done better
        if os.path.exists("src/data/road_points.txt"):
            with open("src/data/road_points.txt", "r") as f:
                for line in f.readlines():
                    road_points.append(tuple([float(s) for s in line.split()]))
        elif os.path.exists("../data/road_points.txt"):
            with open("../data/road_points.txt", "r") as f:
                for line in f.readlines():
                    road_points.append(tuple([float(s) for s in line.split()]))


        # Creating the RoadTest from the points
        the_test = RoadTestFactory.create_road_test(road_points)

        # Send the test for execution
        test_outcome, description, execution_data = self.executor.execute_test(the_test)

        # Print test outcome
        log.info("test_outcome %s", test_outcome)
        log.info("description %s", description)

        import time
        time.sleep(10)
