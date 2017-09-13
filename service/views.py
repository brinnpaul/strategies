import os
import json

from datetime import timedelta
from flask import request, make_response, render_template

from service import app, redis_store, celery
from service.tasks import async_current_impressions

@app.route('/heartbeat', methods=['GET'])
def heartbeat():
    return 'Oh my beating heart!'

@app.route('/campaigns', methods=['GET'])
def get_campaigns():
    campaigns = redis_store.get('campaigns').decode('utf8')
    return campaigns

@app.route('/campaign/<campaign_id>', methods=['GET'])
def get_campaign(campaign_id):
    campaigns = json.loads(redis_store.get('campaigns').decode('utf8'))
    data = campaigns.get(campaign_id)
    return json.dumps({'campaign_id': campaign_id, 'data': data})

@app.route('/campaign/set', methods=['POST'])
def set_campaign():
    campaign_id = request.data.get('campaign_id')
    advertiser_id = request.data.get('advertiser_id')
    delete = request.data.get('delete'),
    report = request.data.get('report')
    if campaign_id is None:
        return 'No Campaign ID!'
    if advertiser_id is None:
        return 'No Advertiser ID!'

    campaigns = json.loads(redis_store.get('campaigns').decode('utf8'))
    campaigns[campaign_id] = {
        'delete': delete,
        'report': report,
        'advertiser_id': advertiser_id
        }
    redis_store.set('campaigns', json.dumps(campaigns))

    return 'Set campaign_id: {}'.format(campaign_id)

@app.route('/campaign/update', methods=['PUT'])
def update_campaign():
    campaign_id = request.data.get('campaign_id')
    advertiser_id = request.data.get('advertiser_id')
    delete = request.data.get('delete'),
    report = request.data.get('report')
    if campaign_id is None:
        return 'No Campaign ID!'
    updates = {
        'delete': delete,
        'report': report,
        'advertiser_id': advertiser_id
        }
    campaigns = json.loads(redis_store.get('campaigns').decode('utf8'))
    for update in updates:
        if updates[update] is not None:
            campaigns[campaign_id][update] = updates[update]

    redis_store.set('campaigns', json.dumps(campaigns))


@app.route('/report/<advertiser_id>/<campaign_id>', methods=['GET'])
def report(advertiser_id, campaign_id):
    kwargs = {'advertiser_id':advertiser_id, 'campaign_id':campaign_id}
    report = async_current_impressions.apply_async(kwargs=kwargs)
    return 'Generating Report for Advertiser: {}, Campiagn: {}'.format(advertiser_id, campaign_id)
