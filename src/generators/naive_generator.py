import numpy as np
import math
import logging as log

from code_pipeline.tests_generation import RoadTestFactory


class NaiveGenerator():
    """
        Generates a single test to show how to control the shape of the road by controlling the positio of the
        road points. We assume a map of 200x200
    """

    def __init__(self, time_budget=None, executor=None, map_size=None):
        self.time_budget = time_budget
        self.executor = executor
        self.map_size = map_size

    def vertical_segment(self, x, y, length):
        road_points = []
        # Create a vertical segment starting close to the left edge of the map
        interpolation_points = int(length / 10.0)
        for y in np.linspace(y, y + length, num=interpolation_points):
            road_points.append((x, y))
        return road_points

    # Radius 20.0 creates a 90-deg turn
    def curve(self, x, y, radius=20.0, direction=1.0):
        road_points = []

        center_x = x + direction * radius
        center_y = y

        interpolation_points = 5
        angles_in_deg = np.linspace(-60.0, 0.0, num=interpolation_points)

        for angle_in_rads in [math.radians(a) for a in angles_in_deg]:
            x = center_x + direction * math.sin(angle_in_rads) * radius
            y = center_y + math.cos(angle_in_rads) * radius
            road_points.append((x, y))

        return road_points

    def curve_left(self, x, y, radius=20.0):
        return self.curve(x, y, radius=radius, direction=-1.0)

    def curve_right(self, x, y, radius=20.0):
        return self.curve(x, y, radius=radius, direction=1.0)

    "direction 1.0 -> x to right | direction -1.0 -> x to left"
    def horizontal_segment(self, x, y, length, radius=0.0, direction=1.0):
        road_points = []
        # Create an horizontal segment, make sure the points line up with previous segment
        x += direction * radius / 2.0
        interpolation_points = int(length / 10.0)
        for x in np.linspace(x, x + direction * length, num=interpolation_points):
            road_points.append((x, y))
        return road_points

    def test_1(self):
        x = 100.0
        y = 10.0
        vertical_length = 100.0
        horizontal_length = 30.0
        radius = 20.0

        road_points = self.vertical_segment(x, y, vertical_length)
        road_points += self.curve_left(road_points[-1][0], road_points[-1][1], radius=radius)
        road_points += self.horizontal_segment(road_points[-1][0], road_points[-1][1], horizontal_length, radius=radius, direction=-1.0)
        return road_points

    def test_2(self):
        x = 100.0
        y = 10.0
        vertical_length = 100.0
        horizontal_length = 30.0
        radius = 20.0

        road_points = self.vertical_segment(x, y, vertical_length)
        road_points += self.curve_right(road_points[-1][0], road_points[-1][1], radius=radius)
        road_points += self.horizontal_segment(road_points[-1][0], road_points[-1][1], horizontal_length, radius=radius, direction=1.0)
        return road_points


    def start(self):
        log.info("Starting test generation")

        road_points = self.test_1()

        # Creating the RoadTest from the points
        the_test = RoadTestFactory.create_road_test(road_points)

        # Send the test for execution
        test_outcome, description, execution_data = self.executor.execute_test(the_test)

        # Print test outcome
        log.info("test_outcome %s", test_outcome)
        log.info("description %s", description)

        import time
        time.sleep(10)