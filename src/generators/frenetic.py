import logging as log
from jmetal.algorithm.singleobjective.genetic_algorithm import GeneticAlgorithm
from jmetal.operator import BinaryTournamentSelection, PolynomialMutation, SBXCrossover
from src.generators.base_frenet_generator import BaseFrenetGenerator
from src.generators.problems.road_problem import RoadGeneration
from jmetal.util.termination_criterion import StoppingByTime


class FreneticGenerator(BaseFrenetGenerator):

    def start(self):

        frenet_step = 10
        # Number of generated kappa points depends on the size of the map + random variation
        number_of_points = int(self.map_size / frenet_step)

        problem = RoadGeneration(self, number_of_points)
        log.info("Starting test generation")

        # population size is 10 per hour
        population_size = max(int(self.time_budget / 3600) * 10, 10)

        algorithm = GeneticAlgorithm(
            problem=problem,
            population_size=population_size,
            offspring_population_size=population_size,
            mutation=PolynomialMutation(1.0 / problem.number_of_variables, 20.0),
            crossover=SBXCrossover(0.9, 20.0),
            selection=BinaryTournamentSelection(),
            termination_criterion=StoppingByTime(max_seconds=self.time_budget),
        )

        algorithm.run()
        result = algorithm.get_result()

        print('Algorithm: {}'.format(algorithm.get_name()))
        print('Problem: {}'.format(problem.get_name()))
        print('Solution: {}'.format(result.variables))
        print('Fitness: {}'.format(result.objectives[0]))
        print('Computing time: {}'.format(algorithm.total_computing_time))

        self.store_dataframe()
