import numpy as np
import logging as log
import src.utils.frenet as frenet
import random
from time import sleep
from src.generators.base_generator import BaseGenerator


class RandomFrenetGenerator(BaseGenerator):
    """
        Generates tests using the frenet framework to determine curvatures.
    """

    def __init__(self, time_budget=None, executor=None, map_size=None):
        # Spending 20% of the time on random generation
        self.random_gen_budget = 0.2
        # Margin size w.r.t the map
        self.margin = 10
        super().__init__(time_budget, executor, map_size)

    def start(self):
        self.generate_random_tests()
        self.generate_mutants()
        self.store_dataframe('frenet')
        sleep(10)

    def generate_random_tests(self):
        while self.executor.get_remaining_time() > self.time_budget * (1.0 - self.random_gen_budget):
            log.info("Random generation. Remaining time %s", self.executor.get_remaining_time())
            kappas, road_points = self.generate_random_test()
            self.execute_frenet_test(kappas)
        return

    def generate_mutants(self):
        # Iterating the tests according to the value of the oob_percentage (failed first) and min_oob_distance (closer to fail).
        # TODO: This shouldn't be two phase generation [random, mutants of rnd].
        for index, row in self.df[self.df['outcome'] != 'INVALID'].sort_values(['max_oob_percentage', 'min_oob_distance'], ascending=(False, True)).iterrows():

            # Mutations to the road
            # TODO: Is it possible to obtain the kappas given cartesians?
            road_points = row['road']
            if self.executor.get_remaining_time() <= 0:
                return

            # Parent info to be added to the dataframe
            parent_info = {'parent_index': index, 'parent_outcome': row['outcome'], 'parent_min_oob_distance': row['min_oob_distance']}

            # Execute reversed original test
            log.info('Mutation function: {:s}'.format('reverse road'))
            log.info('Parent ({:s}) {:0.2f} accum_neg_oob and {:0.2f} min oob distance'.format(row['outcome'], row['accum_neg_oob'], row['min_oob_distance']))
            self.execute_test(road_points[::-1], method='reversed road', parent_info=parent_info)

            # Mutations to the kappas
            # TODO: Implement more interesting and smarter mutations such as adding a kappa, modifying paths, etc.
            kappas = row['kappas']
            kappa_mutations = [('reverse kappas', lambda ks: ks[::-1]),
                               ('split and swap kappas', lambda ks: ks[int(len(ks)/2):] + ks[:int(len(ks)/2)]),
                               ('flip sign kappas', lambda ks: list(map(lambda x: x * -1.0, ks))),
                               ('increase kappas 10%', lambda ks: list(map(lambda x: x * 1.1, ks))),
                               ('randomly modify a kappa', self.random_modification)]

            for name, function in kappa_mutations:
                if self.executor.get_remaining_time() <= 0:
                    return
                log.info("Generating mutants. Remaining time %s", self.executor.get_remaining_time())
                log.info('Mutation function: {:s}'.format(name))
                log.info('Parent ({:s}) {:0.3f} accum_neg_oob and {:0.3f} min oob distance'.format(row['outcome'], row['accum_neg_oob'], row['min_oob_distance']))
                m_kappas = function(kappas)
                self.execute_frenet_test(m_kappas, method=name)
        return

    def execute_frenet_test(self, kappas, method='random'):
        return self.execute_test(self.kappas_to_road_points(kappas), method=method, extra_info={'kappas': kappas})

    @staticmethod
    def random_modification(kappas):
        # Randomly modified kappa
        i = random.randint(0, len(kappas)-1)
        kappas[i] += random.choice(np.linspace(-0.05, 0.05))
        return kappas

    def kappas_to_road_points(self, kappas, frenet_step=10, theta0=1.57):
        """
        Args:
            kappas: list of kappa values
            frenet_step: The distance between to points.
            theta0: The initial angle of the line. (1.57 == 90 degrees)
        Returns:
            road points in cartesian coordinates
        """
        # Using the bottom center of the map.
        y0 = self.margin
        x0 = self.map_size / 2
        ss = np.arange(y0, self.map_size, frenet_step)

        # Transforming the frenet points to cartesian
        (xs, ys) = frenet.frenet_to_cartesian(x0, y0, theta0, ss, kappas)
        road_points = self.reframe_road(xs, ys)
        return road_points

    def generate_random_test(self, frenet_step=10, theta0=1.57, kappa_delta=0.05, kappa_bound=0.07):
        """ Generates a test using frenet framework to determine the curvature of the points.
         Currently using an initial setup similar to the GUI.
         TODO: Make the frenet setup part of the experiment to adapt w.r.t. the output of the tests.
        Args:
            frenet_step: The distance between to points.
            theta0: The initial angle of the line. (1.57 == 90 degrees)
            kappa_delta: The maximum difference between two consecutive kappa values.
            kappa_bound: The maximum value of kappa allowed.
        Returns:
            a list of kappa values and its cartesian representation.
        """

        # Producing randomly generated kappas for the given setting.
        ss = np.arange(self.margin, self.map_size, frenet_step)
        kappas = [0.0] * len(ss)
        for i in range(len(kappas)):
            kappas[i] = random.choice(np.linspace(max(-kappa_bound, kappas[i - 1] - kappa_delta),
                                                  min(kappa_bound, kappas[i - 1] + kappa_delta)))

        # Transforming the frenet points to cartesian
        road_points = self.kappas_to_road_points(kappas, frenet_step=frenet_step, theta0=theta0)
        return kappas, road_points

    def reframe_road(self, xs, ys):
        """
        Args:
            xs: cartesian x coordinates
            ys: cartesian y coordinates
        Returns:
            A representation of the road that fits the map size (when possible).
        """
        if max(xs) > self.map_size - self.margin:
            shift = min(xs) - self.margin
            xs = list(map(lambda x: x - shift, xs))
            log.info('Shifting to the left')
        elif min(xs) < self.margin:
            shift = self.map_size - max(xs) - self.margin
            xs = list(map(lambda x: x + shift, xs))
            log.info('Shifting to the right')
        if min(ys) < self.margin:
            shift = self.map_size - max(ys) - self.margin
            ys = list(map(lambda y: y + shift, ys))
            log.info('Shifting to the top')
        elif max(ys) > self.map_size - self.margin:
            # Probably can't do much since I started at the bottom...
            pass
        return list(zip(xs, ys))
