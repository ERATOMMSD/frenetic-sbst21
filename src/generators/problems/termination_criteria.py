from jmetal.util.termination_criterion import TerminationCriterion
from code_pipeline.executors import AbstractTestExecutor
import logging as log


class StoppingByExecutor(TerminationCriterion):

    def __init__(self, executor: AbstractTestExecutor):
        super(StoppingByExecutor, self).__init__()
        self.executor = executor

    def update(self, *args, **kwargs):
        pass

    @property
    def is_met(self):
        log.info(f'Remaining time {self.executor.get_remaining_time()}')
        return self.executor.get_remaining_time() <= 50
