from random import randint
from time import sleep
from src.generators.base_generator import BaseGenerator

import logging as log
import pandas as pd


class RandomGenerator(BaseGenerator):
    """
        This simple (naive) test generator creates roads using 3 and 8 points randomly placed on the map.
        We expect that this generator quickly creates plenty of tests, but many of them will be invalid as roads
        will likely self-intersect.
    """

    def start(self):

        while self.executor.get_remaining_time() > 0:
            # Some debugging
            log.info("Starting test generation. Remaining time %s", self.executor.get_remaining_time())

            number_of_points = randint(3, 8)

            log.info("Trying to generate a random test with %d", number_of_points)
            # Pick up random points from the map. They will be interpolated anyway to generate the road
            road_points = []
            for i in range(0, number_of_points):
                road_points.append((randint(0, self.map_size), randint(0, self.map_size)))

            self.execute_test(road_points)

            if self.executor.road_visualizer:
                sleep(5)

        self.store_dataframe()
