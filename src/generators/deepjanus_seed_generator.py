# This code is used in the paper
# "Model-based exploration of the frontier of behaviours for deep learning system testing"
# by V. Riccio and P. Tonella
# https://doi.org/10.1145/3368089.3409730

import logging as log

from src.generators.base_generator import BaseGenerator
from sample_test_generators.deepjanus_seed_generator import RoadGenerator


class JanusGenerator(BaseGenerator):

    def start(self):
        log.info("Starting test generation")
        # Originally generates a single test.
        # It has been modified to generate test until the budget is used up.

        # TODO: Shall we modify this values?
        NODES = 10
        MAX_ANGLE = 40
        NUM_SPLINE_NODES = 20
        SEG_LENGTH = 25

        while self.executor.get_remaining_time() > 0:
            road_points = RoadGenerator(num_control_nodes=NODES, max_angle=MAX_ANGLE, seg_length=SEG_LENGTH,
                                 num_spline_nodes=NUM_SPLINE_NODES).generate()

            self.execute_test(road_points)

        self.store_dataframe()
