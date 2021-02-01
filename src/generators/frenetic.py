import math
import logging as log
from jmetal.algorithm.singleobjective.genetic_algorithm import GeneticAlgorithm
from jmetal.operator import BinaryTournamentSelection, PolynomialMutation, SBXCrossover
from jmetal.problem.singleobjective.unconstrained import FloatProblem, FloatSolution
from jmetal.util.termination_criterion import StoppingByTime
from src.generators.base_frenet_generator import BaseFrenetGenerator


class FreneticGenerator(BaseFrenetGenerator):

    def start(self):

        frenet_step = 10
        # Number of generated kappa points depends on the size of the map + random variation
        number_of_points = int(self.map_size / frenet_step)

        problem = RoadGeneration(self, number_of_points)
        log.info("Starting test generation")

        algorithm = GeneticAlgorithm(
            problem=problem,
            population_size=100,
            offspring_population_size=100,
            mutation=PolynomialMutation(1.0 / problem.number_of_variables, 20.0),
            crossover=SBXCrossover(0.9, 20.0),
            selection=BinaryTournamentSelection(),
            termination_criterion=StoppingByTime(max_seconds=self.time_budget)
        )

        algorithm.run()
        result = algorithm.get_result()

        print('Algorithm: {}'.format(algorithm.get_name()))
        print('Problem: {}'.format(problem.get_name()))
        print('Solution: {}'.format(result.variables))
        print('Fitness: {}'.format(result.objectives[0]))
        print('Computing time: {}'.format(algorithm.total_computing_time))

        self.store_dataframe()


class RoadGeneration(FloatProblem):

    INVALID_SCORE = 10000
    FAIL_BONUS = 10

    def __init__(self, generator: FreneticGenerator, number_of_variables: int = 10, lower_bound: float = -0.07, upper_bound: float = 0.07):
        super(RoadGeneration, self).__init__()
        self.number_of_objectives = 1
        self.number_of_variables = number_of_variables
        self.number_of_constraints = 0

        self.obj_directions = [self.MINIMIZE]
        self.obj_labels = ['f(x)']

        self.lower_bound = [lower_bound for _ in range(number_of_variables)]
        self.upper_bound = [upper_bound for _ in range(number_of_variables)]

        self.generator = generator

        FloatSolution.lower_bound = self.lower_bound
        FloatSolution.upper_bound = self.upper_bound

    def evaluate(self, solution: FloatSolution) -> FloatSolution:

        kappas = solution.variables

        outcome, min_oob_distance = self.generator.execute_frenet_test(kappas)

        if outcome != 'INVALID':
            solution.objectives[0] = min_oob_distance
        else:
            solution.objectives[0] = RoadGeneration.INVALID_SCORE

        if outcome == 'FAIL':
            solution.objectives[0] -= RoadGeneration.FAIL_BONUS

        return solution

    def get_name(self) -> str:
        return 'RoadGeneration'
