import nexusadspy
from datetime import datetime


class NotImplementedError(Exception): pass


class AppnexusClient:
    def __init__(self, credentials):
        self.client = nexusadspy.AppnexusClient('.appnexus_auth.json')
        self.reporter = nexusadspy.AppnexusReport

    def current_impressions(advertiser_id, campaign_id):

        today = datetime.now().strftime('%Y-%m-%d')
        columns = ['day', 'hour', 'imps', 'clicks', 'campaign_id']
        report_type = 'network_analytics'
        filters = [{'campaign_id':{'operator':'=','value': campaign_id}}]

        report = reporter(advertiser_ids=advertiser_id,
                          start_date=today,
                          end_date=today, #   report_interval='last_hour',
                          filters=filters,
                          report_type=report_type,
                          columns=columns)

        output = report.get()
        window = sorted(output, key=lambda x: x['hour'], reverse=True)[0]
        current_impressions = today.get('imps')
        return current_impressions

    def current_bid_price(advertiser_id, campaign_id):
        raise NotImplementedError('Read some docs!')

    def update_bid(new_bid, advertiser_id, campaign_id):
        raise NotImplementedError('Read some docs!')