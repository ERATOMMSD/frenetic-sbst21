import random

from jmetal.core.operator import Mutation
from jmetal.core.solution import FloatSolution
from jmetal.util.ckecking import Check


class SingleKappaMutation(Mutation[FloatSolution]):

    def __init__(self, probability: float, distribution_index: float = 0.20):
        super(SingleKappaMutation, self).__init__(probability=probability)
        self.distribution_index = distribution_index
        self.multiply_probability = 0.7

    def execute(self, solution: FloatSolution) -> FloatSolution:
        Check.that(issubclass(type(solution), FloatSolution), "Solution type invalid")

        for i in range(solution.number_of_variables):
            rand = random.random()
            if rand <= self.probability:
                y = solution.variables[i]
                mult_rand = random.random()
                if mult_rand < self.multiply_probability:
                    solution.variables[i] = self.multiply_kappa(y)
                else:
                    solution.variables[i] = self.flip_sign(y)

        return solution

    @staticmethod
    def multiply_kappa(x):
        # Multiplier defines how much the points will be modified 50% ~ 150%
        multiplier = random.randint(5, 15) / 10
        return x * multiplier

    @staticmethod
    def flip_sign(x):
        # Flipping the sign
        return -1.0 * x

    def get_name(self):
        return 'Single Kappa mutation'


class GlobalKappaMutation(Mutation[FloatSolution]):

    def __init__(self, probability: float, distribution_index: float = 0.20):
        super(GlobalKappaMutation, self).__init__(probability=probability)
        self.distribution_index = distribution_index

    def execute(self, solution: FloatSolution) -> FloatSolution:
        Check.that(issubclass(type(solution), FloatSolution), "Solution type invalid")

        rnd = random.random()
        if rnd < 0.7:
            # Multiplier defines how much the points will be modified 50% ~ 150%
            multiplier = random.randint(5, 15) / 10
            mutation_function = lambda x: x * multiplier
        else:
            # Flipping the sign
            mutation_function = lambda x: -1.0 * x

        for i in range(solution.number_of_variables):
            rand = random.random()
            if rand <= self.probability:
                y = solution.variables[i]
                solution.variables[i] = mutation_function(y)

        return solution

    def get_name(self):
        return 'Global Kappa mutation'
