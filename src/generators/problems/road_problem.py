from jmetal.problem.singleobjective.unconstrained import FloatProblem, FloatSolution
from src.generators.base_frenet_generator import BaseFrenetGenerator


class RoadGeneration(FloatProblem):

    INVALID_SCORE = 10
    FAIL_BONUS = 5

    def __init__(self, generator: BaseFrenetGenerator, number_of_variables: int = 10, lower_bound: float = -0.07, upper_bound: float = 0.07):
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
