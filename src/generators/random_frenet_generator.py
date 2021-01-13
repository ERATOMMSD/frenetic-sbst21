import numpy as np
import logging as log
import src.utils.frenet as frenet
import random
from time import sleep

from code_pipeline.tests_generation import RoadTestFactory


class RandomFrenetGenerator():
    """
        Generates tests using the frenet framework with n-points.
    """

    def __init__(self, time_budget=None, executor=None, map_size=None):
        self.time_budget = time_budget
        self.executor = executor
        self.map_size = map_size

    def start(self):

        while self.executor.get_remaining_time() > 0:
            # Some debugging
            log.info("Starting test generation. Remaining time %s", self.executor.get_remaining_time())

            # Currently using an initial setup similar to the GUI.
            frenet_step = 13
            y0 = 10
            x0 = self.map_size / 2
            theta0 = 1.57
            kappa_delta = 0.07
            kappa_bound = 0.05

            ss = np.arange(y0 + frenet_step, self.map_size, frenet_step)

            kappas = [0.0] * len(ss)

            for i, kp in enumerate(kappas):
                kappas[i] = random.choice(np.linspace(max(-kappa_bound, kappas[i-1] - kappa_delta),
                                                      min(kappa_bound, kappas[i-1] + kappa_delta)))

            # Transforming the frenet points to cartesian
            (xs, ys) = frenet.frenet_to_cartesian(x0, y0, theta0, ss, kappas)

            road_points = self.reframe_road(xs, ys)

            # Some more debugging
            log.info("Generated test using: %s", road_points)
            the_test = RoadTestFactory.create_road_test(road_points)

            # Try to execute the test
            test_outcome, description, execution_data = self.executor.execute_test(the_test)

            # Print the result from the test and continue
            log.info("test_outcome %s", test_outcome)
            log.info("description %s", description)

            if self.executor.road_visualizer:
                sleep(5)

    def reframe_road(self, xs, ys):
        margin = 10
        if max(xs) > self.map_size:
            shift = min(xs) + margin
            xs = list(map(lambda x: x - shift, xs))
            log.debug('Shifting to the left')
        elif min(xs) < margin:
            shift = self.map_size - max(xs) - margin
            xs = list(map(lambda x: x + shift, xs))
            log.debug('Shifting to the right')
        if min(ys) < margin:
            shift = self.map_size - max(ys) - margin
            ys = list(map(lambda y: y + shift, ys))
            log.debug('Shifting to the top')
        elif max(ys) > self.map_size:
            # Probably can't do much since I started at the bottom...
            pass
        return list(zip(xs, ys))
