import logging as log
from jmetal.algorithm.singleobjective.genetic_algorithm import GeneticAlgorithm
from jmetal.operator import BinaryTournamentSelection, PolynomialMutation, SBXCrossover, NullCrossover
from src.generators.base_frenet_generator import BaseFrenetGenerator
from src.generators.problems.road_problem import RoadGeneration
from src.generators.problems.mutations import SingleKappaMutation
from jmetal.util.termination_criterion import StoppingByTime


# TODO: Define types to avoid type warnings in crossover and mutation parameters.
class FreneticGenerator(BaseFrenetGenerator):

    def __init__(self, time_budget=None, executor=None, map_size=None, population_size=50, offspring_size=20,
                 mutation=PolynomialMutation, crossover=SBXCrossover(0.9, 20.0)):
        self.population_size = population_size
        self.offspring_size = offspring_size
        self.mutation = mutation
        self.crossover = crossover

        super().__init__(time_budget=time_budget, executor=executor, map_size=map_size)

    def start(self):
        log.info("Starting test generation")
        # Distance between two frenet steps
        frenet_step = 10

        # Number of generated kappa points depends on the size of the map + random variation
        number_of_points = int(self.map_size / frenet_step)
        problem = RoadGeneration(self, number_of_points)
        algorithm = GeneticAlgorithm(
            problem=problem,
            population_size=self.population_size,
            offspring_population_size=self.offspring_size,
            mutation=self.mutation(1.0 / problem.number_of_variables, 20.0),
            crossover=self.crossover,
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


class FreneticGeneratorPolySBX20(FreneticGenerator):
    def __init__(self, time_budget=None, executor=None, map_size=None):
        super().__init__(time_budget=time_budget, executor=executor, map_size=map_size,
                         population_size=20, offspring_size=20, mutation=PolynomialMutation,
                         crossover=SBXCrossover(0.9, 20.0))


class FreneticGeneratorPolySBX50(FreneticGenerator):
    def __init__(self, time_budget=None, executor=None, map_size=None):
        super().__init__(time_budget=time_budget, executor=executor, map_size=map_size,
                         population_size=50, offspring_size=50, mutation=PolynomialMutation,
                         crossover=SBXCrossover(0.9, 20.0))


class FreneticGeneratorPolyNull20(FreneticGenerator):
    def __init__(self, time_budget=None, executor=None, map_size=None):
        super().__init__(time_budget=time_budget, executor=executor, map_size=map_size,
                         population_size=20, offspring_size=20, mutation=PolynomialMutation,
                         crossover=NullCrossover())


class FreneticGeneratorPolyNull50(FreneticGenerator):
    def __init__(self, time_budget=None, executor=None, map_size=None):
        super().__init__(time_budget=time_budget, executor=executor, map_size=map_size,
                         population_size=50, offspring_size=50, mutation=PolynomialMutation,
                         crossover=NullCrossover())


class FreneticGeneratorKappaBX20(FreneticGenerator):
    def __init__(self, time_budget=None, executor=None, map_size=None):
        super().__init__(time_budget=time_budget, executor=executor, map_size=map_size,
                         population_size=20, offspring_size=20, mutation=SingleKappaMutation,
                         crossover=SBXCrossover(0.9, 20.0))


class FreneticGeneratorKappaSBX50(FreneticGenerator):
    def __init__(self, time_budget=None, executor=None, map_size=None):
        super().__init__(time_budget=time_budget, executor=executor, map_size=map_size,
                         population_size=50, offspring_size=50, mutation=SingleKappaMutation,
                         crossover=SBXCrossover(0.9, 20.0))


class FreneticGeneratorKappaNull20(FreneticGenerator):
    def __init__(self, time_budget=None, executor=None, map_size=None):
        super().__init__(time_budget=time_budget, executor=executor, map_size=map_size,
                         population_size=20, offspring_size=20, mutation=SingleKappaMutation,
                         crossover=NullCrossover())


class FreneticGeneratorKappaNull50(FreneticGenerator):
    def __init__(self, time_budget=None, executor=None, map_size=None):
        super().__init__(time_budget=time_budget, executor=executor, map_size=map_size,
                         population_size=50, offspring_size=50, mutation=SingleKappaMutation,
                         crossover=NullCrossover())