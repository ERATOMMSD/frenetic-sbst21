import logging as log
from jmetal.algorithm.multiobjective.nsgaii import NSGAII
from jmetal.operator import PolynomialMutation, SBXCrossover
from jmetal.util.comparator import DominanceComparator
from src.generators.problems.termination_criteria import StoppingByExecutor
from src.generators.base_frenet_generator import BaseFrenetGenerator
from src.generators.problems.road_problem import RoadGeneration


class NSGAIIFrenetGenerator(BaseFrenetGenerator):

    def start(self):

        frenet_step = 10
        # Number of generated kappa points depends on the size of the map + random variation
        number_of_points = int(self.map_size / frenet_step)

        problem = RoadGeneration(self, number_of_points)
        log.info("Starting test generation")

        algorithm = NSGAII(
            problem=problem,
            population_size=100,
            offspring_population_size=100,
            mutation=PolynomialMutation(probability=1.0 / problem.number_of_variables, distribution_index=20.0),
            crossover=SBXCrossover(probability=0.9, distribution_index=20.0),
            termination_criterion=StoppingByExecutor(executor=self.executor),
            dominance_comparator=DominanceComparator()
        )

        algorithm.run()
        result = algorithm.get_result()

        print('Algorithm: {}'.format(algorithm.get_name()))
        print('Problem: {}'.format(problem.get_name()))
        print('Solution: {}'.format(result.variables))
        print('Fitness: {}'.format(result.objectives[0]))
        print('Computing time: {}'.format(algorithm.total_computing_time))

        self.store_dataframe()
