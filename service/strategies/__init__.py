from strategies.pacing import Pacing


class StrategyError(Exception): pass


class Strategies:
    def __init__(self):
        self.strategies = {
            'pacing': Pacing
        }

    def get(strategy):
        s = self.strategies.get(strategy)
        if s is None:
            raise StrategyError('Strategy Not Implmented!')
        return s