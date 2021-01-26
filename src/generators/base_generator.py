from abc import ABC
import logging as log
import numpy as np
import pandas as pd
import itertools as it
import os
from pathlib import Path

from time import sleep
from datetime import datetime
from code_pipeline.tests_generation import RoadTestFactory


class BaseGenerator(ABC):

    def __init__(self, time_budget=None, executor=None, map_size=None):
        self.time_budget = time_budget
        self.executor = executor
        self.map_size = map_size
        self.df = pd.DataFrame()

    def store_dataframe(self, name):
        log.info("Storing the results in to a csv file.")
        # Storing the results as csv in experiments folder
        file_date = datetime.now().strftime('%Y%m%d-%H%M')
        with open('experiments/{:s}-{:s}-results.csv'.format(file_date, name), 'w') as outfile:
            self.df.to_csv(outfile)
        return

    def execute_test(self, road_points, method='random', extra_info={}, parent_info={}):
        # Some more debugging
        log.info("Generated test using: %s", road_points)
        the_test = RoadTestFactory.create_road_test(road_points)

        # Try to execute the test
        test_outcome, description, execution_data = self.executor.execute_test(the_test)

        # Print the result from the test and continue
        log.info("test_outcome %s", test_outcome)
        log.info("description %s", description)
        info = {'outcome': test_outcome, 'description': description, 'road': road_points, 'method': method,
                'visited': False}

        # Adding extra info to the dataframe
        for k, v in extra_info.items():
            info[k] = v

        # Storing the data in a dataframe for next phase
        if execution_data:
            # base metrics
            metrics = ['steering', 'steering_input', 'brake', 'brake_input', 'throttle', 'throttle_input',
            'wheelspeed', 'vel_kmh', 'oob_counter', 'oob_distance']
            functions = [('max', np.max), ('min', np.min), ('mean', np.mean), ('avg', np.average)]
            for metric, (name, func) in it.product(metrics, functions):
                metric_data = [y for y in map(lambda x: getattr(x, metric), execution_data) if y is not None]
                if metric_data:
                    info['{:s}_{:s}'.format(name, metric)] = func(metric_data)
            info['max_oob_percentage'] = execution_data[-1].max_oob_percentage

            # complex metrics
            accum_neg_oob = self.accumulated_negative_oob(execution_data)
            info['accum_neg_oob'] = accum_neg_oob

            # parent info
            for k, v in parent_info.items():
                info[k] = v

            # Retrieving file name
            last_file = sorted(Path('simulations/beamng_executor').iterdir(), key=os.path.getmtime)[-1]
            info['simulation_file'] = last_file.name

            # Logging some info for debugging
            log.info('Min oob_distance: {:0.3f}'.format(info['min_oob_distance']))
            log.info('Accumulated negative oob_distance: {:0.3f}'.format(accum_neg_oob))

        self.df = self.df.append(info, ignore_index=True)
        if self.executor.road_visualizer:
            sleep(5)
        return info['outcome']

    @staticmethod
    def accumulated_negative_oob(execution_data):
        """
        Note: Normalizing oob_distance to be negative.
        Default interval: [-2, 2] --> Normalized interval: [-4, 0]
        Args:
            execution_data: execution data from the simulator
        Returns:
            Accumulated oob_distance when the center the mass already crossed one of the lanes (oob_distance < 0).
        """
        return (sum(
            map(lambda k: (execution_data[k].oob_distance - 2) * (execution_data[k].timer - execution_data[k - 1].timer)
            if execution_data[k].oob_distance < 0 else 0, range(1, len(execution_data)))))