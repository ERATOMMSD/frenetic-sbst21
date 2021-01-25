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
        # Initializing current tests as generation 0 to track how many generations took to fail.
        self.df['generation'] = 0
        self.df['visited'] = False
        print(self.df.head())
        # Iterating the tests according to the value of the oob_percentage (failed first) and min_oob_distance (closer to fail).
        while self.executor.get_remaining_time() > 0:
            parent = self.df[(self.df.outcome == 'PASS') & ~self.df.visited].sort_values('min_oob_distance', ascending=True).head(1)
            self.df.at[parent.index, 'visited'] = True

            # Mutations to the road
            # TODO: Is it possible to obtain the kappas given cartesians?
            road_points = parent.road.item()
            if self.executor.get_remaining_time() <= 0:
                return

            # Parent info to be added to the dataframe
            parent_info = {'parent_index': parent.index, 'parent_outcome': parent.outcome.item(),
                           'parent_min_oob_distance': parent.min_oob_distance.item(),
                           'generation': parent.generation.item() + 1}

            # Execute reversed original test
            log.info('Mutation function: {:s}'.format('reverse road'))
            log.info('Parent ({:s}) {:0.3f} accum_neg_oob and {:0.3f} min oob distance'.format(parent.outcome.item(),
                                                                                               parent.accum_neg_oob.item(),
                                                                                               parent.min_oob_distance.item()))

            self.execute_test(road_points[::-1], method='reversed road', parent_info=parent_info)

            # Mutations to the kappas
            # TODO: Implement more interesting and smarter mutations such as adding a kappa, modifying paths, etc.
            kappas = parent.kappas.item()
            # kappas might be empty if the parent was obtained from reverse road points mutation
            if kappas:
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
                    log.info('Parent ({:s}) {:0.3f} accum_neg_oob and {:0.3f} min oob distance'.format(parent.outcome.item(),
                                                                                                       parent.accum_neg_oob.item(),
                                                                                                       parent.min_oob_distance.item()))
                    m_kappas = function(kappas)
                    outcome = self.execute_frenet_test(m_kappas, method=name, parent_info=parent_info)
                    # When there is a mutant of this branch that fails, we stop mutating this branch.
                    if outcome == 'FAIL':
                        break
        return

    def execute_frenet_test(self, kappas, method='random', parent_info={}):
        return self.execute_test(self.kappas_to_road_points(kappas), method=method, parent_info=parent_info, extra_info={'kappas': kappas})

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
        ss = np.arange(y0, (len(kappas) + 1) * frenet_step, frenet_step)

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
        # Number of generated kappa points depends on the size of the map + random variation
        number_of_points = int(self.map_size/frenet_step) + random.randint(-5, 15)

        print(number_of_points)

        # Producing randomly generated kappas for the given setting.
        kappas = [0.0] * number_of_points
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
        min_xs = min(xs)
        min_ys = min(ys)
        road_width = 10  # TODO: How to get the exact road width?
        if (max(xs) - min_xs + road_width > self.map_size - self.margin) \
            or (max(ys) - min_ys + road_width > self.map_size - self.margin):
            log.info("Road won't fit")
            # TODO: Fail the entire test and start over
        xs = list(map(lambda x: x - min_xs + road_width, xs))
        ys = list(map(lambda y: y - min_ys + road_width, ys))
        return list(zip(xs, ys))
