from datetime import datetime
from strategies.base import BaseStrategy

class Pacing(BaseStrategy):
    def __init__(self):
        self.schedule = (
            (   0, 0.0000), (  30, 0.0177), (  60, 0.0315), (  90, 0.0453),
            ( 120, 0.0551), ( 150, 0.0648), ( 180, 0.0722), ( 210, 0.0796),
            ( 240, 0.0861), ( 270, 0.0926), ( 300, 0.0994), ( 330, 0.1063),
            ( 360, 0.1157), ( 390, 0.1251), ( 420, 0.1396), ( 450, 0.1540),
            ( 480, 0.1731), ( 510, 0.1922), ( 540, 0.2154), ( 570, 0.2387),
            ( 600, 0.2649), ( 630, 0.2912), ( 660, 0.3189), ( 690, 0.3467),
            ( 720, 0.3745), ( 750, 0.4023), ( 780, 0.4318), ( 810, 0.4614),
            ( 840, 0.4903), ( 870, 0.5192), ( 900, 0.5483), ( 930, 0.5775),
            ( 960, 0.6057), ( 990, 0.6339), (1020, 0.6604), (1050, 0.6870),
            (1080, 0.7119), (1110, 0.7368), (1140, 0.7619), (1170, 0.7870),
            (1200, 0.8115), (1230, 0.8361), (1260, 0.8619), (1290, 0.8877),
            (1320, 0.9132), (1350, 0.9387), (1380, 0.9605), (1410, 0.9823),
            (1440, 1.0000)
        )

    def _get_desired_pace(self):
        """Get Weighted Average of Two Closest Pacing Windows"""
        d0 = datetime.now().strftime('%Y-%m-%d')
        df = datetime.now() - datetime.strptime(d0, '%Y-%m-%d')
        mins = df.seconds / 60

        min_diff = 30
        pace_schedule = self.schedule
        for p in range(0, len(pace_schedule)):
            diff = abs(mins - pace_schedule[p][0])
            if diff < min_diff:
                time_window = p
                min_diff = diff
                break

        if time_window == 49:
            return 1.0

        current_pace = self.schedule[time_window][1]
        next_pace = self.schedule[time_window+1][1]
        current_weight = float(min_diff) / 30
        next_weight = 1 - (float(min_diff) / 30)

        desired_pace = current_pace * current_weight + next_pace * next_weight
        return desired_pace

    @staticmethod
    def _lmap_multiplier(current, desired, sensitivity=1, _min=0.7, _max=1.3):
        """Based of logistic map x_n+1 = l * x_n * (1-x_n)
           Estimates a multiplier to update bid price"""
        ratio = float(current)/desired
        multiplier = 1 + (sensitivity * ratio * (1-ratio))
        if multiplier > _max:
            return _max
        if multiplier < _min:
            return _min
        return multiplier

    def get_updated_bid(self,
                   impressions_current=None,
                   impressions_limit=None,
                   bid_price=None,
                   min_bid=None,
                   max_bid=None):
        desired_pace = self._get_desired_pace()
        current_pace = float(impressions_current) / impressions_limit

        m = self._lmap_multiplier(current_pace, desired_pace)
        new_bid = round(m * bid_price, 2)

        if min_bid:
            if new_bid < min_bid:
                return min_bid
        if max_bid:
            if new_bid > max_bid:
                return max_bid
        return new_bid
