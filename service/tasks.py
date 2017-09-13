import json
import nexusadspy

from datetime import timedelta, datetime
from celery import signature
from service import celery, redis_store
from service.appnexus_client import AppnexusClient
from service.strategies import Strategies

celery.conf.update(
    CELERYBEAT_SCHEDULE={
        'ping': {
            'task': 'tasks.ping',
            'schedule': timedelta(minutes=60)
        }
    }
)

def apply_strategy(self,
                   advertiser_id=None,
                   campaign_id=None,
                   strategy=None,
                   daily_limit=None):

    client = AppnexusClient()
    current_impressions = client.current_impressions(advertiser_id, campaign_id)
    current_bid_price = client.current_bid_price(advertiser_id, campaign_id)

    strategy = Strategies().get(strategy)
    new_bid = strategy.get_updated_bid(current_impressions,
                                       daily_limit,
                                       bid_price)

    client.update_bid(advertiser_id, campaign_id, new_bid)

@celery.task
def beat_strategy(*args, **kwargs):
    apply_strategy(**kwargs)

@celery.task(name='tasks.ping')
def ping():
    campaigns = json.loads(redis_store.get('campaigns').decode('utf8'))

    campaigns_to_delete = []
    apply_strategy = []
    for campaign_id in campaigns:
        print('Campaign: {}, data: {}'.format(campaign_id, campaigns[campaign_id]))
        campaign_data = campaigns[campaign_id]
        if campaign_data.get('delete') == 'True':
            print('Deleting Campaign: {}'.format(campaign_id))
            campaigns_to_delete.append(campaign_id)
        if campaign_data.get('report') == 'True':
            campaigns_to_report.append(campaign_id)

    for campaign in campaigns_to_delete:
        del campaigns[campaign]

    redis_store.set('campaigns', json.dumps(campaigns))

    for campaign_id in apply_strategy:
        campaign = campaigns.get(campaign_id)
        advertiser_id = campaign.get('advertiser_id')
        strategy = campaign.get('strategy')
        daily_limit = campaign.get('daily_limit')
        kwargs = {
            'advertiser_id':advertiser_id,
            'campaign_id':campaign_id,
            'strategy': strategy,
            'daily_limit': daily_limit
            }
        beat_strategy.apply_async(kwargs=kwargs)

@celery.task(name='tasks.report', bind=True)
def async_current_impressions(self, *args, **kwargs):
    advertiser_id = kwargs.get('advertiser_id')
    campaign_id = kwargs.get('campaign_id')
    client = AppnexusClient()
    current_impressions = client.current_impressions(advertiser_id, campaign_id)

@celery.task(name='tasks.update_bid', bind=True)
def manual_update_bid(self, *args, **kwargs):
    update_bid(**kwargs)