class NotImplmentedError(Exception): pass


class BaseStrategy:
    def get_updated_bid():
        """Implemented per strategy"""
        raise NotImplmentedError('Not here!')