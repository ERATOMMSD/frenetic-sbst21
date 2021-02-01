import logging as log
from jmetal.algorithm.singleobjective.evolution_strategy import EvolutionStrategy
from jmetal.operator import PolynomialMutation
from jmetal.util.termination_criterion import StoppingByTime
from src.generators.base_frenet_generator import BaseFrenetGenerator
from src.generators.problems.road_problem import RoadGeneration


class EvolutionaryFrenetGenerator(BaseFrenetGenerator):

    def start(self):

        frenet_step = 10
        # Number of generated kappa points depends on the size of the map + random variation
        number_of_points = int(self.map_size / frenet_step)

        problem = RoadGeneration(self, number_of_points)
        log.info("Starting test generation")

        algorithm = EvolutionStrategy(
            problem=problem,
            mu=10,
            lambda_=10,
            elitist=True,
            mutation=PolynomialMutation(probability=1.0 / problem.number_of_variables),
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
