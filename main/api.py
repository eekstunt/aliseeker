import re
import json
from time import sleep

import requests

from django.conf import settings

from main import utils

GOODS_API_URL = 'http://api.epn.bz/json'
PAYEER_API_URL = 'https://payeer.com/ajax/api/api.php'


class GoodsAPI:
    def __init__(self,
        user_api_key=settings.EPN_API_KEY, user_hash=settings.EPN_HASH, api_version='2',
        api_url=GOODS_API_URL, requests_timeout=settings.REQUESTS_TIMEOUT
    ):
        self._user_api_key = user_api_key
        self._user_hash = user_hash
        self._api_version = api_version

        self._api_url = api_url
        self._requests_timeout = requests_timeout

    def get_offer_id(self, long_link):
        amount_of_repetitions = 1
        for repetition in range(amount_of_repetitions):
            final_page = requests.get(long_link, timeout=self._requests_timeout)
            if repetition != amount_of_repetitions - 1:
                sleep(settings.LINK_CHECKING_DELAY)
        final_link = final_page.url

        if 'aliexpress.com/' not in final_link:
            raise ValueError(final_link)

        try:
            offer_id_str = re.search('[/_]\d+\.html', final_link).group()[1:-5]
        except:
            raise ValueError(final_link)
        offer_id = int(offer_id_str)

        offer_info = self.get_offer_info(offer_id)

        return offer_id

    def get_offer_link(self, offer_id):
        offer_info = self.get_offer_info(offer_id)
        offer_link = offer_info['url']

        return offer_link

    def get_offer_info(self, offer_id, language='en', currency='USD'):
        request = {
            'action': 'offer_info',
            'lang': language,
            'id': offer_id,
            'currency': currency
        }

        offer_info = self._query(request)['offer']

        return offer_info

    def get_similar_offers_info(self, base_offer_info, accuracy, min_price_usd, language='en', currency='USD', limit=settings.MAX_AMOUNT_OF_OFFERS):
        request = {
            'action': 'search',
            'query': utils.shorten_text(base_offer_info['name'], accuracy),
            'orderby': 'price',
            'order_direction': 'asc',
            'limit': limit,
            'lang': language,
            'currency': currency,
            'price_min': min_price_usd
        }

        offers_info = self._query(request)['offers']

        return offers_info

    def _query(self, request):
        data = {
            'user_api_key': self._user_api_key,
            'user_hash': self._user_hash,
            'api_version': self._api_version,
            'requests': {'0': request}
        }

        response = requests.post(self._api_url,
            data=json.dumps(data),
            timeout=self._requests_timeout
        ).json()
        result = response['results'][0]

        return result

    def get_offer_price_from_info(self, offer_info):
        if 'sale_price' in offer_info:
            price = offer_info['sale_price']
        else:
            price = offer_info['price']

        return float(price)


class PayeerAPI:
    def __init__(self,
        account=settings.PAYEER_ACCOUNT, api_id=settings.PAYEER_API_ID, api_pass=settings.PAYEER_API_PASS,
        api_url=PAYEER_API_URL, requests_timeout=settings.REQUESTS_TIMEOUT, proxies=settings.PAYEER_PROXIES
    ):
        self._account = account
        self._api_id = api_id
        self._api_pass = api_pass

        self._api_url = api_url
        self._requests_timeout = requests_timeout
        self._proxies = proxies

    def balance(self):
        request = {
            'action': 'balance'
        }
        return self._query(request)

    def output(self, ps, sum_in, cur_in, cur_out, to):
        request = {
            'action': 'output',
            'ps': ps,
            'sumIn': sum_in,
            'curIn': cur_in,
            'curOut': cur_out,
            'param_ACCOUNT_NUMBER': to
        }
        return self._query(request)

    def _query(self, request):
        data = {
            'account': self._account,
            'apiId': self._api_id,
            'apiPass': self._api_pass
        }
        data.update(request)

        response = requests.post(self._api_url,
            data=data,
            timeout=self._requests_timeout,
            proxies=self._proxies
        ).json()

        return response
