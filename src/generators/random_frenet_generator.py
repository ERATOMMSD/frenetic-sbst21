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
        # Storing the ancestors of a test that failed to reduce close relatives.
        self.ancestors_of_failed_tests = set()
        self.ancestors_lookahead = 5
        # Bounds on the number of kappas of randomly generated paths
        super().__init__(time_budget, executor, map_size)

    def start(self):
        self.generate_initial_population()
        self.generate_mutants()
        self.store_dataframe()
        sleep(10)

    def generate_initial_population(self):
        while self.executor.get_remaining_time() > self.time_budget * (1.0 - self.random_gen_budget):
            log.info("Random generation. Remaining time %s", self.executor.get_remaining_time())
            kappas = self.generate_random_test()
            self.execute_frenet_test(kappas)
        return

    def generate_mutants(self):
        # Initializing current tests as generation 0 to track how many generations took to fail.
        self.df['generation'] = 0
        self.df['visited'] = False

        # Iterating the tests according to the value of the min_oob_distance (closer to fail).
        while self.executor.get_remaining_time() > 0:
            parent = self.df[(self.df.outcome != 'INVALID') & (~self.df.visited) & (self.df.min_oob_distance < -0.5)].sort_values('min_oob_distance', ascending=True).head(1)
            if len(parent):
                self.df.at[parent.index, 'visited'] = True
                self.mutate_test(parent)
            else:
                # If there is no good parent try random generation
                kappas = self.generate_random_test()
                self.execute_frenet_test(kappas)

    def mutate_test(self, parent):
        # Parent info to be added to the dataframe
        ancestors = []
        if parent.method.item() != 'random':
            ancestors = parent.ancestors.item()
        ancestors += [parent.index.item()]

        parent_info = {'parent_index': parent.index.item(), 'parent_outcome': parent.outcome.item(),
                       'parent_min_oob_distance': parent.min_oob_distance.item(),
                       'generation': parent.generation.item() + 1,
                       'ancestors': ancestors}
        # Looking to close relatives to avoid too similar tests
        for ancestor_id in ancestors[-self.ancestors_lookahead:]:
            if ancestor_id in self.ancestors_of_failed_tests:
                return
        # Applying different mutations depending on the outcome
        if parent.outcome.item() == 'FAIL':
            self.mutate_failed_test(parent, parent_info)
        else:
            self.mutate_passed_test(parent, parent_info)

    def mutate_passed_test(self, parent, parent_info):
        # TODO: Implement more interesting and smarter mutations such as adding a kappa, modifying paths, etc.
        kappa_mutations = [('add 1 to 5 kappas at the end', self.add_kappas),
                           ('randomly remove 1 to 5 kappas', self.randomly_remove_kappas),
                           ('remove 1 to 5 kappas from front', lambda ks: ks[random.randint(1, 5):]),
                           ('remove 1 to 5 kappas from tail', lambda ks: ks[:-random.randint(1, 5)]),
                           ('increase kappas 10~50%',
                            lambda ks: list(map(lambda x: x * random.randint(11, 15) / 10, ks))),
                           ('randomly modify 1 to 5 kappas', self.random_modification)]

        self.perform_kappa_mutations(kappa_mutations, parent, parent_info)

    def mutate_failed_test(self, parent, parent_info):
        # Only reversing roads that produced a failure already
        # Mutations to the road
        # TODO: Is it possible to obtain the kappas given cartesians?
        road_points = parent.road.item()
        # Execute reversed original test
        log.info('Mutation function: {:s}'.format('reverse road'))
        log.info('Parent ({:s}) {:0.3f} accum_neg_oob and {:0.3f} min oob distance'.format(parent.outcome.item(),
                                                                                           parent.accum_neg_oob.item(),
                                                                                           parent.min_oob_distance.item()))
        # Do not revisit a reverse road
        self.execute_test(road_points[::-1], method='reversed road',
                          extra_info={'visited': True},
                          parent_info=parent_info)

        # reversible mutations that we may want to avoid in tests that passed because they are easily reversible
        kappa_mutations = [('reverse kappas', lambda ks: ks[::-1]),
                           ('split and swap kappas', lambda ks: ks[int(len(ks) / 2):] + ks[:int(len(ks) / 2)]),
                           ('flip sign kappas', lambda ks: list(map(lambda x: x * -1.0, ks)))]

        self.perform_kappa_mutations(kappa_mutations, parent, parent_info, extra_info={'visited': True})

    def perform_kappa_mutations(self, kappa_mutations, parent, parent_info, extra_info={}):
        # Only considering paths with more than 10 kappa points for mutations
        # kappas might be empty if the parent was obtained from reverse road points mutation
        kappas = parent.kappas.item()
        if kappas and len(kappas) > 10:
            i = 0
            while self.executor.get_remaining_time() > 0 and i < len(kappa_mutations):
                name, function = kappa_mutations[i]
                log.info("Generating mutants. Remaining time %s", self.executor.get_remaining_time())
                log.info('Mutation function: {:s}'.format(name))
                log.info('Parent ({:s}) {:0.3f} accum_neg_oob and {:0.3f} min oob distance'.format(parent.outcome.item(),
                                                                                              parent.accum_neg_oob.item(),
                                                                                              parent.min_oob_distance.item()))
                m_kappas = function(kappas)
                outcome = self.execute_frenet_test(m_kappas, method=name, parent_info=parent_info, extra_info=extra_info, avoid_weaker=True)

                # When there is a mutant of this branch that fails, we stop mutating this branch.
                if outcome == 'FAIL':
                    for ancestor_id in parent_info['ancestors'][-self.ancestors_lookahead:]:
                        self.ancestors_of_failed_tests.add(ancestor_id)
                    break
                i += 1

    @staticmethod
    def get_next_kappa(last_kappa, kappa_bound=0.05, kappa_delta=0.07):
        return random.choice(np.linspace(max(-kappa_bound, last_kappa - kappa_delta),
                                         min(kappa_bound, last_kappa + kappa_delta)))

    @staticmethod
    def add_kappas(kappas):
        # number of kappas to added
        k = random.randint(1, 5)
        modified_kappas = kappas[:]
        last_kappa = kappas[-1]
        while k > 0:
            # Randomly add a kappa
            modified_kappas.append(RandomFrenetGenerator.get_next_kappa(last_kappa))
            k -= 1
        return modified_kappas

    @staticmethod
    def randomly_remove_kappas(kappas):
        # number of kappas to be removed
        k = random.randint(1, 5)
        modified_kappas = kappas[:]
        while k > 0 and len(modified_kappas) > 5:
            # Randomly remove a kappa
            i = random.randint(0, len(modified_kappas) - 1)
            del modified_kappas[i]
            k -= 1
        return modified_kappas

    @staticmethod
    def random_modification(kappas):
        # number of kappas to be modified
        k = random.randint(1, 5)
        # Randomly modified kappa
        indexes = random.sample(range(len(kappas) - 1), k)
        modified_kappas = kappas[:]
        for i in indexes:
            modified_kappas[i] += random.choice(np.linspace(-0.05, 0.05))
        return modified_kappas

    def execute_frenet_test(self, kappas, method='random', parent_info={}, extra_info={}, avoid_weaker=False):
        extra_info['kappas'] = kappas
        return self.execute_test(self.kappas_to_road_points(kappas), method=method, parent_info=parent_info,
                                 extra_info=extra_info, avoid_weaker=avoid_weaker)

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

    def generate_random_test(self, frenet_step=10, kappa_delta=0.05, kappa_bound=0.07):
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
        number_of_points = int(self.map_size / frenet_step) + random.randint(-5, 15)

        # Producing randomly generated kappas for the given setting.
        kappas = [0.0] * number_of_points
        for i in range(len(kappas)):
            kappas[i] = RandomFrenetGenerator.get_next_kappa(kappas[i - 1], kappa_bound, kappa_delta)

        return kappas

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
