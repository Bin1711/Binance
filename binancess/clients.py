from typing import Dict, Optional, List, Tuple

import aiohttp
import asyncio
import hashlib
import hmac
import requests
import time
from operator import itemgetter
from urllib.parse import urlencode


from .helpers import interval_to_milliseconds, convert_ts_str
from .exceptions import BinanceAPIException, BinanceRequestException, NotImplementedException
from .enums import HistoricalKlinesType

class BaseClient:
    
    API_URL = 'https://api.binance.{}/api'
    API_TESTNET_URL = 'https://testnet.binance.vision/api'
    MARGIN_API_URL = 'https://api.binance.{}/sapi'
    WEBSITE_URL = 'https://www.binance.{}'
    FUTURES_URL = 'https://fapi.binance.{}/fapi'
    FUTURES_TESTNET_URL = 'https://testnet.binancefuture.com/fapi'
    FUTURES_DATA_URL = 'https://fapi.binance.{}/futures/data'
    FUTURES_DATA_TESTNET_URL = 'https://testnet.binancefuture.com/futures/data'
    FUTURES_COIN_URL = "https://dapi.binance.{}/dapi"
    FUTURES_COIN_TESTNET_URL = 'https://testnet.binancefuture.com/dapi'
    FUTURES_COIN_DATA_URL = "https://dapi.binance.{}/futures/data"
    FUTURES_COIN_DATA_TESTNET_URL = 'https://testnet.binancefuture.com/futures/data'
    OPTIONS_URL = 'https://vapi.binance.{}/vapi'
    OPTIONS_TESTNET_URL = 'https://testnet.binanceops.{}/vapi'
    PUBLIC_API_VERSION = 'v1'
    PRIVATE_API_VERSION = 'v3'
    MARGIN_API_VERSION = 'v1'
    FUTURES_API_VERSION = 'v1'
    FUTURES_API_VERSION2 = "v2"
    OPTIONS_API_VERSION = 'v1'

    REQUEST_TIMEOUT: float = 10

    SYMBOL_TYPE_SPOT = 'SPOT'

    ORDER_STATUS_NEW = 'NEW'
    ORDER_STATUS_PARTIALLY_FILLED = 'PARTIALLY_FILLED'
    ORDER_STATUS_FILLED = 'FILLED'
    ORDER_STATUS_CANCELED = 'CANCELED'
    ORDER_STATUS_PENDING_CANCEL = 'PENDING_CANCEL'
    ORDER_STATUS_REJECTED = 'REJECTED'
    ORDER_STATUS_EXPIRED = 'EXPIRED'

    KLINE_INTERVAL_1MINUTE = '1m'
    KLINE_INTERVAL_3MINUTE = '3m'
    KLINE_INTERVAL_5MINUTE = '5m'
    KLINE_INTERVAL_15MINUTE = '15m'
    KLINE_INTERVAL_30MINUTE = '30m'
    KLINE_INTERVAL_1HOUR = '1h'
    KLINE_INTERVAL_2HOUR = '2h'
    KLINE_INTERVAL_4HOUR = '4h'
    KLINE_INTERVAL_6HOUR = '6h'
    KLINE_INTERVAL_8HOUR = '8h'
    KLINE_INTERVAL_12HOUR = '12h'
    KLINE_INTERVAL_1DAY = '1d'
    KLINE_INTERVAL_3DAY = '3d'
    KLINE_INTERVAL_1WEEK = '1w'
    KLINE_INTERVAL_1MONTH = '1M'

    SIDE_BUY = 'BUY'
    SIDE_SELL = 'SELL'

    ORDER_TYPE_LIMIT = 'LIMIT'
    ORDER_TYPE_MARKET = 'MARKET'
    ORDER_TYPE_STOP_LOSS = 'STOP_LOSS'
    ORDER_TYPE_STOP_LOSS_LIMIT = 'STOP_LOSS_LIMIT'
    ORDER_TYPE_TAKE_PROFIT = 'TAKE_PROFIT'
    ORDER_TYPE_TAKE_PROFIT_LIMIT = 'TAKE_PROFIT_LIMIT'
    ORDER_TYPE_LIMIT_MAKER = 'LIMIT_MAKER'

    FUTURE_ORDER_TYPE_LIMIT = 'LIMIT'
    FUTURE_ORDER_TYPE_MARKET = 'MARKET'
    FUTURE_ORDER_TYPE_STOP = 'STOP'
    FUTURE_ORDER_TYPE_STOP_MARKET = 'STOP_MARKET'
    FUTURE_ORDER_TYPE_TAKE_PROFIT = 'TAKE_PROFIT'
    FUTURE_ORDER_TYPE_TAKE_PROFIT_MARKET = 'TAKE_PROFIT_MARKET'
    FUTURE_ORDER_TYPE_LIMIT_MAKER = 'LIMIT_MAKER'

    TIME_IN_FORCE_GTC = 'GTC'  # Good till cancelled
    TIME_IN_FORCE_IOC = 'IOC'  # Immediate or cancel
    TIME_IN_FORCE_FOK = 'FOK'  # Fill or kill

    ORDER_RESP_TYPE_ACK = 'ACK'
    ORDER_RESP_TYPE_RESULT = 'RESULT'
    ORDER_RESP_TYPE_FULL = 'FULL'

    # For accessing the data returned by Client.aggregate_trades().
    AGG_ID = 'a'
    AGG_PRICE = 'p'
    AGG_QUANTITY = 'q'
    AGG_FIRST_TRADE_ID = 'f'
    AGG_LAST_TRADE_ID = 'l'
    AGG_TIME = 'T'
    AGG_BUYER_MAKES = 'm'
    AGG_BEST_MATCH = 'M'

    # new asset transfer api enum
    SPOT_TO_FIAT = "MAIN_C2C"
    SPOT_TO_USDT_FUTURE = "MAIN_UMFUTURE"
    SPOT_TO_COIN_FUTURE = "MAIN_CMFUTURE"
    SPOT_TO_MARGIN_CROSS = "MAIN_MARGIN"
    SPOT_TO_MINING = "MAIN_MINING"
    FIAT_TO_SPOT = "C2C_MAIN"
    FIAT_TO_USDT_FUTURE = "C2C_UMFUTURE"
    FIAT_TO_MINING = "C2C_MINING"
    USDT_FUTURE_TO_SPOT = "UMFUTURE_MAIN"
    USDT_FUTURE_TO_FIAT = "UMFUTURE_C2C"
    USDT_FUTURE_TO_MARGIN_CROSS = "UMFUTURE_MARGIN"
    COIN_FUTURE_TO_SPOT = "CMFUTURE_MAIN"
    MARGIN_CROSS_TO_SPOT = "MARGIN_MAIN"
    MARGIN_CROSS_TO_USDT_FUTURE = "MARGIN_UMFUTURE"
    MINING_TO_SPOT = "MINING_MAIN"
    MINING_TO_USDT_FUTURE = "MINING_UMFUTURE"
    MINING_TO_FIAT = "MINING_C2C"

    def __init__(
        self, api_key: Optional[str] = None, api_secret: Optional[str] = None,
        requests_params: Dict[str, str] = None, tld: str = 'com',
        testnet: bool = False
    ):
        """Binance API Client constructor

        :param api_key: Api Key
        :type api_key: str.
        :param api_secret: Api Secret
        :type api_secret: str.
        :param requests_params: optional - Dictionary of requests params to use for all calls
        :type requests_params: dict.
        :param testnet: Use testnet environment - only available for vanilla options at the moment
        :type testnet: bool

        """

        self.tld = tld
        self.API_URL = self.API_URL.format(tld)
        self.MARGIN_API_URL = self.MARGIN_API_URL.format(tld)
        self.WEBSITE_URL = self.WEBSITE_URL.format(tld)
        self.FUTURES_URL = self.FUTURES_URL.format(tld)
        self.FUTURES_DATA_URL = self.FUTURES_DATA_URL.format(tld)
        self.FUTURES_COIN_URL = self.FUTURES_COIN_URL.format(tld)
        self.FUTURES_COIN_DATA_URL = self.FUTURES_COIN_DATA_URL.format(tld)
        self.OPTIONS_URL = self.OPTIONS_URL.format(tld)
        self.OPTIONS_TESTNET_URL = self.OPTIONS_TESTNET_URL.format(tld)

        self.API_KEY = api_key
        self.API_SECRET = api_secret
        self.session = self._init_session()
        self._requests_params = requests_params
        self.response = None
        self.testnet = testnet
        self.timestamp_offset = 0

    def _get_headers(self) -> Dict:
        headers = {
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',  # noqa
        }
        if self.API_KEY:
            assert self.API_KEY
            headers['X-MBX-APIKEY'] = self.API_KEY
        return headers

    def _init_session(self):
        raise NotImplementedError

    def _create_api_uri(self, path: str, signed: bool = True, version: str = PUBLIC_API_VERSION) -> str:
        url = self.API_URL
        if self.testnet:
            url = self.API_TESTNET_URL
        v = self.PRIVATE_API_VERSION if signed else version
        return url + '/' + v + '/' + path

    def _create_margin_api_uri(self, path: str, version: str = MARGIN_API_VERSION) -> str:
        return self.MARGIN_API_URL + '/' + version + '/' + path

    def _create_website_uri(self, path: str) -> str:
        return self.WEBSITE_URL + '/' + path

    def _create_futures_api_uri(self, path: str) -> str:
        url = self.FUTURES_URL
        if self.testnet:
            url = self.FUTURES_TESTNET_URL
        return url + '/' + self.FUTURES_API_VERSION + '/' + path

    def _create_futures_data_api_uri(self, path: str) -> str:
        url = self.FUTURES_DATA_URL
        if self.testnet:
            url = self.FUTURES_DATA_TESTNET_URL
        return url + '/' + path

    def _create_futures_coin_api_url(self, path: str, version=1) -> str:
        url = self.FUTURES_COIN_URL
        if self.testnet:
            url = self.FUTURES_COIN_TESTNET_URL
        options = {1: self.FUTURES_API_VERSION, 2: self.FUTURES_API_VERSION2}
        return url + "/" + options[version] + "/" + path

    def _create_futures_coin_data_api_url(self, path: str, version=1) -> str:
        url = self.FUTURES_COIN_DATA_URL
        if self.testnet:
            url = self.FUTURES_COIN_DATA_TESTNET_URL
        return url + "/" + path

    def _create_options_api_uri(self, path: str) -> str:
        url = self.OPTIONS_URL
        if self.testnet:
            url = self.OPTIONS_TESTNET_URL
        return url + '/' + self.OPTIONS_API_VERSION + '/' + path

    def _generate_signature(self, data: Dict) -> str:

        ordered_data = self._order_params(data)
        query_string = '&'.join([f"{d[0]}={d[1]}" for d in ordered_data])
        m = hmac.new(self.API_SECRET.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256)
        return m.hexdigest()

    @staticmethod
    def _order_params(data: Dict) -> List[Tuple[str, str]]:
        """Convert params to list with signature as last element

        :param data:
        :return:

        """
        data = dict(filter(lambda el: el[1] is not None, data.items()))
        has_signature = False
        params = []
        for key, value in data.items():
            if key == 'signature':
                has_signature = True
            else:
                params.append((key, str(value)))
        # sort parameters by key
        params.sort(key=itemgetter(0))
        if has_signature:
            params.append(('signature', data['signature']))
        return params

    def _get_request_kwargs(self, method, signed: bool, force_params: bool = False, **kwargs) -> Dict:

        # set default requests timeout
        kwargs['timeout'] = self.REQUEST_TIMEOUT

        # add our global requests params
        if self._requests_params:
            kwargs.update(self._requests_params)

        data = kwargs.get('data', None)
        if data and isinstance(data, dict):
            kwargs['data'] = data

            # find any requests params passed and apply them
            if 'requests_params' in kwargs['data']:
                # merge requests params into kwargs
                kwargs.update(kwargs['data']['requests_params'])
                del(kwargs['data']['requests_params'])

        if signed:
            # generate signature
            kwargs['data']['timestamp'] = int(time.time() * 1000 + self.timestamp_offset)
            kwargs['data']['signature'] = self._generate_signature(kwargs['data'])

        # sort get and post params to match signature order
        if data:
            # sort post params and remove any arguments with values of None
            kwargs['data'] = self._order_params(kwargs['data'])
            # Remove any arguments with values of None.
            null_args = [i for i, (key, value) in enumerate(kwargs['data']) if value is None]
            for i in reversed(null_args):
                del kwargs['data'][i]

        # if get request assign data array to params value for requests lib
        if data and (method == 'get' or force_params):
            kwargs['params'] = '&'.join('%s=%s' % (data[0], data[1]) for data in kwargs['data'])
            del(kwargs['data'])

        return kwargs    
    
    
class Client(BaseClient):
    
    def __init__(
        self, api_key: Optional[str] = None, api_secret: Optional[str] = None,
        requests_params: Dict[str, str] = None, tld: str = 'com',
        testnet: bool = False
    ):

        super().__init__(api_key, api_secret, requests_params, tld, testnet)

        # init DNS and SSL cert
        self.ping()

    def _init_session(self) -> requests.Session:

        headers = self._get_headers()

        session = requests.session()
        session.headers.update(headers)
        return session

    def _request(self, method, uri: str, signed: bool, force_params: bool = False, **kwargs):

        kwargs = self._get_request_kwargs(method, signed, force_params, **kwargs)

        self.response = getattr(self.session, method)(uri, **kwargs)
        return self._handle_response(self.response)

    @staticmethod
    def _handle_response(response: requests.Response):
        """Internal helper for handling API responses from the Binance server.
        Raises the appropriate exceptions when necessary; otherwise, returns the
        response.
        """
        if not (200 <= response.status_code < 300):
            raise BinanceAPIException(response, response.status_code, response.text)
        try:
            return response.json()
        except ValueError:
            raise BinanceRequestException('Invalid Response: %s' % response.text)

    def _request_api(
        self, method, path: str, signed: bool = False, version=BaseClient.PUBLIC_API_VERSION, **kwargs
    ):
        uri = self._create_api_uri(path, signed, version)
        return self._request(method, uri, signed, **kwargs)

    def _request_futures_api(self, method, path, signed=False, **kwargs) -> Dict:
        uri = self._create_futures_api_uri(path)

        return self._request(method, uri, signed, True, **kwargs)

    def _request_futures_data_api(self, method, path, signed=False, **kwargs) -> Dict:
        uri = self._create_futures_data_api_uri(path)

        return self._request(method, uri, signed, True, **kwargs)

    def _request_futures_coin_api(self, method, path, signed=False, version=1, **kwargs) -> Dict:
        uri = self._create_futures_coin_api_url(path, version=version)

        return self._request(method, uri, signed, True, **kwargs)

    def _request_futures_coin_data_api(self, method, path, signed=False, version=1, **kwargs) -> Dict:
        uri = self._create_futures_coin_data_api_url(path, version=version)

        return self._request(method, uri, signed, True, **kwargs)

    def _request_options_api(self, method, path, signed=False, **kwargs) -> Dict:
        uri = self._create_options_api_uri(path)

        return self._request(method, uri, signed, True, **kwargs)

    def _request_margin_api(self, method, path, signed=False, **kwargs) -> Dict:
        uri = self._create_margin_api_uri(path)

        return self._request(method, uri, signed, **kwargs)

    def _request_website(self, method, path, signed=False, **kwargs) -> Dict:
        uri = self._create_website_uri(path)
        return self._request(method, uri, signed, **kwargs)

    def _get(self, path, signed=False, version=BaseClient.PUBLIC_API_VERSION, **kwargs):
        return self._request_api('get', path, signed, version, **kwargs)

    def _post(self, path, signed=False, version=BaseClient.PUBLIC_API_VERSION, **kwargs) -> Dict:
        return self._request_api('post', path, signed, version, **kwargs)

    def _put(self, path, signed=False, version=BaseClient.PUBLIC_API_VERSION, **kwargs) -> Dict:
        return self._request_api('put', path, signed, version, **kwargs)

    def _delete(self, path, signed=False, version=BaseClient.PUBLIC_API_VERSION, **kwargs) -> Dict:
        return self._request_api('delete', path, signed, version, **kwargs)

    # Exchange Endpoints

    def get_products(self) -> Dict:
        """Return list of products currently listed on Binance

        Use get_exchange_info() call instead

        :returns: list - List of product dictionaries

        :raises: BinanceRequestException, BinanceAPIException

        """
        products = self._request_website('get', 'exchange-api/v1/public/asset-service/product/get-products')
        return products

    def get_exchange_info(self) -> Dict:
        """Return rate limits and list of symbols

        :returns: list - List of product dictionaries

        .. code-block:: python

            {
                "timezone": "UTC",
                "serverTime": 1508631584636,
                "rateLimits": [
                    {
                        "rateLimitType": "REQUESTS",
                        "interval": "MINUTE",
                        "limit": 1200
                    },
                    {
                        "rateLimitType": "ORDERS",
                        "interval": "SECOND",
                        "limit": 10
                    },
                    {
                        "rateLimitType": "ORDERS",
                        "interval": "DAY",
                        "limit": 100000
                    }
                ],
                "exchangeFilters": [],
                "symbols": [
                    {
                        "symbol": "ETHBTC",
                        "status": "TRADING",
                        "baseAsset": "ETH",
                        "baseAssetPrecision": 8,
                        "quoteAsset": "BTC",
                        "quotePrecision": 8,
                        "orderTypes": ["LIMIT", "MARKET"],
                        "icebergAllowed": false,
                        "filters": [
                            {
                                "filterType": "PRICE_FILTER",
                                "minPrice": "0.00000100",
                                "maxPrice": "100000.00000000",
                                "tickSize": "0.00000100"
                            }, {
                                "filterType": "LOT_SIZE",
                                "minQty": "0.00100000",
                                "maxQty": "100000.00000000",
                                "stepSize": "0.00100000"
                            }, {
                                "filterType": "MIN_NOTIONAL",
                                "minNotional": "0.00100000"
                            }
                        ]
                    }
                ]
            }

        :raises: BinanceRequestException, BinanceAPIException

        """

        return self._get('exchangeInfo', version=self.PRIVATE_API_VERSION)

    def get_symbol_info(self, symbol) -> Optional[Dict]:
        """Return information about a symbol

        :param symbol: required e.g BNBBTC
        :type symbol: str

        :returns: Dict if found, None if not

        .. code-block:: python

            {
                "symbol": "ETHBTC",
                "status": "TRADING",
                "baseAsset": "ETH",
                "baseAssetPrecision": 8,
                "quoteAsset": "BTC",
                "quotePrecision": 8,
                "orderTypes": ["LIMIT", "MARKET"],
                "icebergAllowed": false,
                "filters": [
                    {
                        "filterType": "PRICE_FILTER",
                        "minPrice": "0.00000100",
                        "maxPrice": "100000.00000000",
                        "tickSize": "0.00000100"
                    }, {
                        "filterType": "LOT_SIZE",
                        "minQty": "0.00100000",
                        "maxQty": "100000.00000000",
                        "stepSize": "0.00100000"
                    }, {
                        "filterType": "MIN_NOTIONAL",
                        "minNotional": "0.00100000"
                    }
                ]
            }

        :raises: BinanceRequestException, BinanceAPIException

        """

        res = self.get_exchange_info()

        for item in res['symbols']:
            if item['symbol'] == symbol.upper():
                return item

        return None

    # General Endpoints

    def ping(self) -> Dict:
        """Test connectivity to the Rest API.

        https://binance-docs.github.io/apidocs/spot/en/#test-connectivity

        :returns: Empty array

        .. code-block:: python

            {}

        :raises: BinanceRequestException, BinanceAPIException

        """
        return self._get('ping', version=self.PRIVATE_API_VERSION)

    def get_server_time(self) -> Dict:
        """Test connectivity to the Rest API and get the current server time.

        https://binance-docs.github.io/apidocs/spot/en/#check-server-time

        :returns: Current server time

        .. code-block:: python

            {
                "serverTime": 1499827319559
            }

        :raises: BinanceRequestException, BinanceAPIException

        """
        return self._get('time', version=self.PRIVATE_API_VERSION)

    # Market Data Endpoints

    def get_all_tickers(self) -> List[Dict[str, str]]:
        """Latest price for all symbols.

        https://binance-docs.github.io/apidocs/spot/en/#symbol-price-ticker

        :returns: List of market tickers

        .. code-block:: python

            [
                {
                    "symbol": "LTCBTC",
                    "price": "4.00000200"
                },
                {
                    "symbol": "ETHBTC",
                    "price": "0.07946600"
                }
            ]

        :raises: BinanceRequestException, BinanceAPIException

        """
        return self._get('ticker/price', version=self.PRIVATE_API_VERSION)

    def get_orderbook_tickers(self) -> Dict:
        """Best price/qty on the order book for all symbols.

        https://binance-docs.github.io/apidocs/spot/en/#symbol-order-book-ticker

        :param symbol: optional
        :type symbol: str

        :returns: List of order book market entries

        .. code-block:: python

            [
                {
                    "symbol": "LTCBTC",
                    "bidPrice": "4.00000000",
                    "bidQty": "431.00000000",
                    "askPrice": "4.00000200",
                    "askQty": "9.00000000"
                },
                {
                    "symbol": "ETHBTC",
                    "bidPrice": "0.07946700",
                    "bidQty": "9.00000000",
                    "askPrice": "100000.00000000",
                    "askQty": "1000.00000000"
                }
            ]

        :raises: BinanceRequestException, BinanceAPIException

        """
        return self._get('ticker/bookTicker', version=self.PRIVATE_API_VERSION)

    def get_order_book(self, **params) -> Dict:
        """Get the Order Book for the market

        https://binance-docs.github.io/apidocs/spot/en/#order-book

        :param symbol: required
        :type symbol: str
        :param limit:  Default 100; max 1000
        :type limit: int

        :returns: API response

        .. code-block:: python

            {
                "lastUpdateId": 1027024,
                "bids": [
                    [
                        "4.00000000",     # PRICE
                        "431.00000000",   # QTY
                        []                # Can be ignored
                    ]
                ],
                "asks": [
                    [
                        "4.00000200",
                        "12.00000000",
                        []
                    ]
                ]
            }

        :raises: BinanceRequestException, BinanceAPIException

        """
        return self._get('depth', data=params, version=self.PRIVATE_API_VERSION)

    def get_recent_trades(self, **params) -> Dict:
        """Get recent trades (up to last 500).

        https://binance-docs.github.io/apidocs/spot/en/#recent-trades-list

        :param symbol: required
        :type symbol: str
        :param limit:  Default 500; max 1000.
        :type limit: int

        :returns: API response

        .. code-block:: python

            [
                {
                    "id": 28457,
                    "price": "4.00000100",
                    "qty": "12.00000000",
                    "time": 1499865549590,
                    "isBuyerMaker": true,
                    "isBestMatch": true
                }
            ]

        :raises: BinanceRequestException, BinanceAPIException

        """
        return self._get('trades', data=params)

    def get_historical_trades(self, **params) -> Dict:
        """Get older trades.

        https://binance-docs.github.io/apidocs/spot/en/#old-trade-lookup

        :param symbol: required
        :type symbol: str
        :param limit:  Default 500; max 1000.
        :type limit: int
        :param fromId:  TradeId to fetch from. Default gets most recent trades.
        :type fromId: str

        :returns: API response

        .. code-block:: python

            [
                {
                    "id": 28457,
                    "price": "4.00000100",
                    "qty": "12.00000000",
                    "time": 1499865549590,
                    "isBuyerMaker": true,
                    "isBestMatch": true
                }
            ]

        :raises: BinanceRequestException, BinanceAPIException

        """
        return self._get('historicalTrades', data=params, version=self.PRIVATE_API_VERSION)

    def get_aggregate_trades(self, **params) -> Dict:
        """Get compressed, aggregate trades. Trades that fill at the time,
        from the same order, with the same price will have the quantity aggregated.

        https://binance-docs.github.io/apidocs/spot/en/#compressed-aggregate-trades-list

        :param symbol: required
        :type symbol: str
        :param fromId:  ID to get aggregate trades from INCLUSIVE.
        :type fromId: str
        :param startTime: Timestamp in ms to get aggregate trades from INCLUSIVE.
        :type startTime: int
        :param endTime: Timestamp in ms to get aggregate trades until INCLUSIVE.
        :type endTime: int
        :param limit:  Default 500; max 1000.
        :type limit: int

        :returns: API response

        .. code-block:: python

            [
                {
                    "a": 26129,         # Aggregate tradeId
                    "p": "0.01633102",  # Price
                    "q": "4.70443515",  # Quantity
                    "f": 27781,         # First tradeId
                    "l": 27781,         # Last tradeId
                    "T": 1498793709153, # Timestamp
                    "m": true,          # Was the buyer the maker?
                    "M": true           # Was the trade the best price match?
                }
            ]

        :raises: BinanceRequestException, BinanceAPIException

        """
        return self._get('aggTrades', data=params, version=self.PRIVATE_API_VERSION)

    def aggregate_trade_iter(self, symbol: str, start_str=None, last_id=None):
        """Iterate over aggregate trade data from (start_time or last_id) to
        the end of the history so far.

        If start_time is specified, start with the first trade after
        start_time. Meant to initialise a local cache of trade data.

        If last_id is specified, start with the trade after it. This is meant
        for updating a pre-existing local trade data cache.

        Only allows start_str or last_id—not both. Not guaranteed to work
        right if you're running more than one of these simultaneously. You
        will probably hit your rate limit.

        See dateparser docs for valid start and end string formats http://dateparser.readthedocs.io/en/latest/

        If using offset strings for dates add "UTC" to date string e.g. "now UTC", "11 hours ago UTC"

        :param symbol: Symbol string e.g. ETHBTC
        :type symbol: str
        :param start_str: Start date string in UTC format or timestamp in milliseconds. The iterator will
        return the first trade occurring later than this time.
        :type start_str: str|int
        :param last_id: aggregate trade ID of the last known aggregate trade.
        Not a regular trade ID. See https://binance-docs.github.io/apidocs/spot/en/#compressed-aggregate-trades-list

        :returns: an iterator of JSON objects, one per trade. The format of
        each object is identical to Client.aggregate_trades().

        :type last_id: int
        """
        if start_str is not None and last_id is not None:
            raise ValueError(
                'start_time and last_id may not be simultaneously specified.')

        # If there's no last_id, get one.
        if last_id is None:
            # Without a last_id, we actually need the first trade.  Normally,
            # we'd get rid of it. See the next loop.
            if start_str is None:
                trades = self.get_aggregate_trades(symbol=symbol, fromId=0)
            else:
                # The difference between startTime and endTime should be less
                # or equal than an hour and the result set should contain at
                # least one trade.
                start_ts = convert_ts_str(start_str)
                # If the resulting set is empty (i.e. no trades in that interval)
                # then we just move forward hour by hour until we find at least one
                # trade or reach present moment
                while True:
                    end_ts = start_ts + (60 * 60 * 1000)
                    trades = self.get_aggregate_trades(
                        symbol=symbol,
                        startTime=start_ts,
                        endTime=end_ts)
                    if len(trades) > 0:
                        break
                    # If we reach present moment and find no trades then there is
                    # nothing to iterate, so we're done
                    if end_ts > int(time.time() * 1000):
                        return
                    start_ts = end_ts
            for t in trades:
                yield t
            last_id = trades[-1][self.AGG_ID]

        while True:
            # There is no need to wait between queries, to avoid hitting the
            # rate limit. We're using blocking IO, and as long as we're the
            # only thread running calls like this, Binance will automatically
            # add the right delay time on their end, forcing us to wait for
            # data. That really simplifies this function's job. Binance is
            # fucking awesome.
            trades = self.get_aggregate_trades(symbol=symbol, fromId=last_id)
            # fromId=n returns a set starting with id n, but we already have
            # that one. So get rid of the first item in the result set.
            trades = trades[1:]
            if len(trades) == 0:
                return
            for t in trades:
                yield t
            last_id = trades[-1][self.AGG_ID]

    def get_klines(self, **params) -> Dict:
        """Kline/candlestick bars for a symbol. Klines are uniquely identified by their open time.

        https://binance-docs.github.io/apidocs/spot/en/#kline-candlestick-data

        :param symbol: required
        :type symbol: str
        :param interval: -
        :type interval: str
        :param limit: - Default 500; max 1000.
        :type limit: int
        :param startTime:
        :type startTime: int
        :param endTime:
        :type endTime: int

        :returns: API response

        .. code-block:: python

            [
                [
                    1499040000000,      # Open time
                    "0.01634790",       # Open
                    "0.80000000",       # High
                    "0.01575800",       # Low
                    "0.01577100",       # Close
                    "148976.11427815",  # Volume
                    1499644799999,      # Close time
                    "2434.19055334",    # Quote asset volume
                    308,                # Number of trades
                    "1756.87402397",    # Taker buy base asset volume
                    "28.46694368",      # Taker buy quote asset volume
                    "17928899.62484339" # Can be ignored
                ]
            ]

        :raises: BinanceRequestException, BinanceAPIException

        """
        return self._get('klines', data=params, version=self.PRIVATE_API_VERSION)

    def _klines(self, klines_type: HistoricalKlinesType = HistoricalKlinesType.SPOT, **params) -> Dict:
        """Get klines of spot (get_klines) or futures (futures_klines) endpoints.

        :param klines_type: Historical klines type: SPOT or FUTURES
        :type klines_type: HistoricalKlinesType

        :return: klines, see get_klines

        """
        if 'endTime' in params and not params['endTime']:
            del params['endTime']

        if HistoricalKlinesType.SPOT == klines_type:
            return self.get_klines(**params)
        elif HistoricalKlinesType.FUTURES == klines_type:
            return self.futures_klines(**params)
        else:
            raise NotImplementedException(klines_type)

    def _get_earliest_valid_timestamp(self, symbol, interval, klines_type: HistoricalKlinesType = HistoricalKlinesType.SPOT):
        """Get earliest valid open timestamp from Binance

        :param symbol: Name of symbol pair e.g BNBBTC
        :type symbol: str
        :param interval: Binance Kline interval
        :type interval: str
        :param klines_type: Historical klines type: SPOT or FUTURES
        :type klines_type: HistoricalKlinesType

        :return: first valid timestamp

        """
        kline = self._klines(
            klines_type=klines_type,
            symbol=symbol,
            interval=interval,
            limit=1,
            startTime=0,
            endTime=int(time.time() * 1000)
        )
        return kline[0][0]

    def get_historical_klines(self, symbol, interval, start_str, end_str=None, limit=500,
                              klines_type: HistoricalKlinesType = HistoricalKlinesType.SPOT):
        """Get Historical Klines from Binance

        :param symbol: Name of symbol pair e.g BNBBTC
        :type symbol: str
        :param interval: Binance Kline interval
        :type interval: str
        :param start_str: Start date string in UTC format or timestamp in milliseconds
        :type start_str: str|int
        :param end_str: optional - end date string in UTC format or timestamp in milliseconds (default will fetch everything up to now)
        :type end_str: str|int
        :param limit: Default 500; max 1000.
        :type limit: int
        :param klines_type: Historical klines type: SPOT or FUTURES
        :type klines_type: HistoricalKlinesType

        :return: list of OHLCV values

        """
        return self._historical_klines(symbol, interval, start_str, end_str=end_str, limit=limit, klines_type=klines_type)

    def _historical_klines(self, symbol, interval, start_str, end_str=None, limit=500,
                           klines_type: HistoricalKlinesType = HistoricalKlinesType.SPOT):
        """Get Historical Klines from Binance (spot or futures)

        See dateparser docs for valid start and end string formats http://dateparser.readthedocs.io/en/latest/

        If using offset strings for dates add "UTC" to date string e.g. "now UTC", "11 hours ago UTC"

        :param symbol: Name of symbol pair e.g BNBBTC
        :type symbol: str
        :param interval: Binance Kline interval
        :type interval: str
        :param start_str: Start date string in UTC format or timestamp in milliseconds
        :type start_str: str|int
        :param end_str: optional - end date string in UTC format or timestamp in milliseconds (default will fetch everything up to now)
        :type end_str: None|str|int
        :param limit: Default 500; max 1000.
        :type limit: int
        :param klines_type: Historical klines type: SPOT or FUTURES
        :type klines_type: HistoricalKlinesType

        :return: list of OHLCV values

        """
        # init our list
        output_data = []

        # convert interval to useful value in seconds
        timeframe = interval_to_milliseconds(interval)

        start_ts = convert_ts_str(start_str)

        # establish first available start timestamp
        first_valid_ts = self._get_earliest_valid_timestamp(symbol, interval, klines_type)
        start_ts = max(start_ts, first_valid_ts)

        # if an end time was passed convert it
        end_ts = convert_ts_str(end_str)

        idx = 0
        while True:
            # fetch the klines from start_ts up to max 500 entries or the end_ts if set
            temp_data = self._klines(
                klines_type=klines_type,
                symbol=symbol,
                interval=interval,
                limit=limit,
                startTime=start_ts,
                endTime=end_ts
            )

            # handle the case where exactly the limit amount of data was returned last loop
            if not len(temp_data):
                break

            # append this loops data to our output data
            output_data += temp_data

            # set our start timestamp using the last value in the array
            start_ts = temp_data[-1][0]

            idx += 1
            # check if we received less than the required limit and exit the loop
            if len(temp_data) < limit:
                # exit the while loop
                break

            # increment next call by our timeframe
            start_ts += timeframe

            # sleep after every 3rd call to be kind to the API
            if idx % 3 == 0:
                time.sleep(1)

        return output_data

    def get_historical_klines_generator(self, symbol, interval, start_str, end_str=None,
                                        klines_type: HistoricalKlinesType = HistoricalKlinesType.SPOT):
        """Get Historical Klines generator from Binance

        :param symbol: Name of symbol pair e.g BNBBTC
        :type symbol: str
        :param interval: Binance Kline interval
        :type interval: str
        :param start_str: Start date string in UTC format or timestamp in milliseconds
        :type start_str: str|int
        :param end_str: optional - end date string in UTC format or timestamp in milliseconds (default will fetch everything up to now)
        :type end_str: str|int
        :param klines_type: Historical klines type: SPOT or FUTURES
        :type klines_type: HistoricalKlinesType

        :return: generator of OHLCV values

        """

        return self._historical_klines_generator(symbol, interval, start_str, end_str=end_str, klines_type=klines_type)

    def _historical_klines_generator(self, symbol, interval, start_str, end_str=None,
                                     klines_type: HistoricalKlinesType = HistoricalKlinesType.SPOT):
        """Get Historical Klines generator from Binance (spot or futures)

        See dateparser docs for valid start and end string formats http://dateparser.readthedocs.io/en/latest/

        If using offset strings for dates add "UTC" to date string e.g. "now UTC", "11 hours ago UTC"

        :param symbol: Name of symbol pair e.g BNBBTC
        :type symbol: str
        :param interval: Binance Kline interval
        :type interval: str
        :param start_str: Start date string in UTC format or timestamp in milliseconds
        :type start_str: str|int
        :param end_str: optional - end date string in UTC format or timestamp in milliseconds (default will fetch everything up to now)
        :type end_str: str|int
        :param klines_type: Historical klines type: SPOT or FUTURES
        :type klines_type: HistoricalKlinesType

        :return: generator of OHLCV values

        """
        # setup the max limit
        limit = 500

        # convert interval to useful value in seconds
        timeframe = interval_to_milliseconds(interval)

        # convert our date strings to milliseconds
        start_ts = convert_ts_str(start_str)

        # establish first available start timestamp
        first_valid_ts = self._get_earliest_valid_timestamp(symbol, interval, klines_type)
        start_ts = max(start_ts, first_valid_ts)

        # if an end time was passed convert it
        end_ts = convert_ts_str(end_str)

        idx = 0
        while True:
            # fetch the klines from start_ts up to max 500 entries or the end_ts if set
            output_data = self._klines(
                klines_type=klines_type,
                symbol=symbol,
                interval=interval,
                limit=limit,
                startTime=start_ts,
                endTime=end_ts
            )

            # handle the case where exactly the limit amount of data was returned last loop
            if not len(output_data):
                break

            # yield data
            for o in output_data:
                yield o

            # set our start timestamp using the last value in the array
            start_ts = output_data[-1][0]

            idx += 1
            # check if we received less than the required limit and exit the loop
            if len(output_data) < limit:
                # exit the while loop
                break

            # increment next call by our timeframe
            start_ts += timeframe

            # sleep after every 3rd call to be kind to the API
            if idx % 3 == 0:
                time.sleep(1)

    def get_avg_price(self, **params):
        """Current average price for a symbol.

        https://binance-docs.github.io/apidocs/spot/en/#current-average-price

        :param symbol:
        :type symbol: str

        :returns: API response

        .. code-block:: python

            {
                "mins": 5,
                "price": "9.35751834"
            }
        """
        return self._get('avgPrice', data=params, version=self.PRIVATE_API_VERSION)

    def get_ticker(self, **params):
        """24 hour price change statistics.

        https://binance-docs.github.io/apidocs/spot/en/#24hr-ticker-price-change-statistics

        :param symbol:
        :type symbol: str

        :returns: API response

        .. code-block:: python

            {
                "priceChange": "-94.99999800",
                "priceChangePercent": "-95.960",
                "weightedAvgPrice": "0.29628482",
                "prevClosePrice": "0.10002000",
                "lastPrice": "4.00000200",
                "bidPrice": "4.00000000",
                "askPrice": "4.00000200",
                "openPrice": "99.00000000",
                "highPrice": "100.00000000",
                "lowPrice": "0.10000000",
                "volume": "8913.30000000",
                "openTime": 1499783499040,
                "closeTime": 1499869899040,
                "fristId": 28385,   # First tradeId
                "lastId": 28460,    # Last tradeId
                "count": 76         # Trade count
            }

        OR

        .. code-block:: python

            [
                {
                    "priceChange": "-94.99999800",
                    "priceChangePercent": "-95.960",
                    "weightedAvgPrice": "0.29628482",
                    "prevClosePrice": "0.10002000",
                    "lastPrice": "4.00000200",
                    "bidPrice": "4.00000000",
                    "askPrice": "4.00000200",
                    "openPrice": "99.00000000",
                    "highPrice": "100.00000000",
                    "lowPrice": "0.10000000",
                    "volume": "8913.30000000",
                    "openTime": 1499783499040,
                    "closeTime": 1499869899040,
                    "fristId": 28385,   # First tradeId
                    "lastId": 28460,    # Last tradeId
                    "count": 76         # Trade count
                }
            ]

        :raises: BinanceRequestException, BinanceAPIException

        """
        return self._get('ticker/24hr', data=params, version=self.PRIVATE_API_VERSION)

    def get_symbol_ticker(self, **params):
        """Latest price for a symbol or symbols.

        https://binance-docs.github.io/apidocs/spot/en/#symbol-price-ticker

        :param symbol:
        :type symbol: str

        :returns: API response

        .. code-block:: python

            {
                "symbol": "LTCBTC",
                "price": "4.00000200"
            }

        OR

        .. code-block:: python

            [
                {
                    "symbol": "LTCBTC",
                    "price": "4.00000200"
                },
                {
                    "symbol": "ETHBTC",
                    "price": "0.07946600"
                }
            ]

        :raises: BinanceRequestException, BinanceAPIException

        """
        return self._get('ticker/price', data=params, version=self.PRIVATE_API_VERSION)

    def get_orderbook_ticker(self, **params):
        """Latest price for a symbol or symbols.

        https://binance-docs.github.io/apidocs/spot/en/#symbol-order-book-ticker

        :param symbol:
        :type symbol: str

        :returns: API response

        .. code-block:: python

            {
                "symbol": "LTCBTC",
                "bidPrice": "4.00000000",
                "bidQty": "431.00000000",
                "askPrice": "4.00000200",
                "askQty": "9.00000000"
            }

        OR

        .. code-block:: python

            [
                {
                    "symbol": "LTCBTC",
                    "bidPrice": "4.00000000",
                    "bidQty": "431.00000000",
                    "askPrice": "4.00000200",
                    "askQty": "9.00000000"
                },
                {
                    "symbol": "ETHBTC",
                    "bidPrice": "0.07946700",
                    "bidQty": "9.00000000",
                    "askPrice": "100000.00000000",
                    "askQty": "1000.00000000"
                }
            ]

        :raises: BinanceRequestException, BinanceAPIException

        """
        return self._get('ticker/bookTicker', data=params, version=self.PRIVATE_API_VERSION)

    # Account Endpoints

    def create_order(self, **params):
        """Send in a new order

        Any order with an icebergQty MUST have timeInForce set to GTC.

        https://binance-docs.github.io/apidocs/spot/en/#new-order-trade

        :param symbol: required
        :type symbol: str
        :param side: required
        :type side: str
        :param type: required
        :type type: str
        :param timeInForce: required if limit order
        :type timeInForce: str
        :param quantity: required
        :type quantity: decimal
        :param quoteOrderQty: amount the user wants to spend (when buying) or receive (when selling)
            of the quote asset, applicable to MARKET orders
        :type quoteOrderQty: decimal
        :param price: required
        :type price: str
        :param newClientOrderId: A unique id for the order. Automatically generated if not sent.
        :type newClientOrderId: str
        :param icebergQty: Used with LIMIT, STOP_LOSS_LIMIT, and TAKE_PROFIT_LIMIT to create an iceberg order.
        :type icebergQty: decimal
        :param newOrderRespType: Set the response JSON. ACK, RESULT, or FULL; default: RESULT.
        :type newOrderRespType: str
        :param recvWindow: the number of milliseconds the request is valid for
        :type recvWindow: int

        :returns: API response

        Response ACK:

        .. code-block:: python

            {
                "symbol":"LTCBTC",
                "orderId": 1,
                "clientOrderId": "myOrder1" # Will be newClientOrderId
                "transactTime": 1499827319559
            }

        Response RESULT:

        .. code-block:: python

            {
                "symbol": "BTCUSDT",
                "orderId": 28,
                "clientOrderId": "6gCrw2kRUAF9CvJDGP16IP",
                "transactTime": 1507725176595,
                "price": "0.00000000",
                "origQty": "10.00000000",
                "executedQty": "10.00000000",
                "status": "FILLED",
                "timeInForce": "GTC",
                "type": "MARKET",
                "side": "SELL"
            }

        Response FULL:

        .. code-block:: python

            {
                "symbol": "BTCUSDT",
                "orderId": 28,
                "clientOrderId": "6gCrw2kRUAF9CvJDGP16IP",
                "transactTime": 1507725176595,
                "price": "0.00000000",
                "origQty": "10.00000000",
                "executedQty": "10.00000000",
                "status": "FILLED",
                "timeInForce": "GTC",
                "type": "MARKET",
                "side": "SELL",
                "fills": [
                    {
                        "price": "4000.00000000",
                        "qty": "1.00000000",
                        "commission": "4.00000000",
                        "commissionAsset": "USDT"
                    },
                    {
                        "price": "3999.00000000",
                        "qty": "5.00000000",
                        "commission": "19.99500000",
                        "commissionAsset": "USDT"
                    },
                    {
                        "price": "3998.00000000",
                        "qty": "2.00000000",
                        "commission": "7.99600000",
                        "commissionAsset": "USDT"
                    },
                    {
                        "price": "3997.00000000",
                        "qty": "1.00000000",
                        "commission": "3.99700000",
                        "commissionAsset": "USDT"
                    },
                    {
                        "price": "3995.00000000",
                        "qty": "1.00000000",
                        "commission": "3.99500000",
                        "commissionAsset": "USDT"
                    }
                ]
            }

        :raises: BinanceRequestException, BinanceAPIException, BinanceOrderException, BinanceOrderMinAmountException, BinanceOrderMinPriceException, BinanceOrderMinTotalException, BinanceOrderUnknownSymbolException, BinanceOrderInactiveSymbolException

        """
        return self._post('order', True, data=params)

    def order_limit(self, timeInForce=BaseClient.TIME_IN_FORCE_GTC, **params):
        """Send in a new limit order

        Any order with an icebergQty MUST have timeInForce set to GTC.

        :param symbol: required
        :type symbol: str
        :param side: required
        :type side: str
        :param quantity: required
        :type quantity: decimal
        :param price: required
        :type price: str
        :param timeInForce: default Good till cancelled
        :type timeInForce: str
        :param newClientOrderId: A unique id for the order. Automatically generated if not sent.
        :type newClientOrderId: str
        :param icebergQty: Used with LIMIT, STOP_LOSS_LIMIT, and TAKE_PROFIT_LIMIT to create an iceberg order.
        :type icebergQty: decimal
        :param newOrderRespType: Set the response JSON. ACK, RESULT, or FULL; default: RESULT.
        :type newOrderRespType: str
        :param recvWindow: the number of milliseconds the request is valid for
        :type recvWindow: int

        :returns: API response

        See order endpoint for full response options

        :raises: BinanceRequestException, BinanceAPIException, BinanceOrderException, BinanceOrderMinAmountException, BinanceOrderMinPriceException, BinanceOrderMinTotalException, BinanceOrderUnknownSymbolException, BinanceOrderInactiveSymbolException

        """
        params.update({
            'type': self.ORDER_TYPE_LIMIT,
            'timeInForce': timeInForce
        })
        return self.create_order(**params)

    def order_limit_buy(self, timeInForce=BaseClient.TIME_IN_FORCE_GTC, **params):
        """Send in a new limit buy order

        Any order with an icebergQty MUST have timeInForce set to GTC.

        :param symbol: required
        :type symbol: str
        :param quantity: required
        :type quantity: decimal
        :param price: required
        :type price: str
        :param timeInForce: default Good till cancelled
        :type timeInForce: str
        :param newClientOrderId: A unique id for the order. Automatically generated if not sent.
        :type newClientOrderId: str
        :param stopPrice: Used with stop orders
        :type stopPrice: decimal
        :param icebergQty: Used with iceberg orders
        :type icebergQty: decimal
        :param newOrderRespType: Set the response JSON. ACK, RESULT, or FULL; default: RESULT.
        :type newOrderRespType: str
        :param recvWindow: the number of milliseconds the request is valid for
        :type recvWindow: int

        :returns: API response

        See order endpoint for full response options

        :raises: BinanceRequestException, BinanceAPIException, BinanceOrderException, BinanceOrderMinAmountException, BinanceOrderMinPriceException, BinanceOrderMinTotalException, BinanceOrderUnknownSymbolException, BinanceOrderInactiveSymbolException

        """
        params.update({
            'side': self.SIDE_BUY,
        })
        return self.order_limit(timeInForce=timeInForce, **params)

    def order_limit_sell(self, timeInForce=BaseClient.TIME_IN_FORCE_GTC, **params):
        """Send in a new limit sell order

        :param symbol: required
        :type symbol: str
        :param quantity: required
        :type quantity: decimal
        :param price: required
        :type price: str
        :param timeInForce: default Good till cancelled
        :type timeInForce: str
        :param newClientOrderId: A unique id for the order. Automatically generated if not sent.
        :type newClientOrderId: str
        :param stopPrice: Used with stop orders
        :type stopPrice: decimal
        :param icebergQty: Used with iceberg orders
        :type icebergQty: decimal
        :param newOrderRespType: Set the response JSON. ACK, RESULT, or FULL; default: RESULT.
        :type newOrderRespType: str
        :param recvWindow: the number of milliseconds the request is valid for
        :type recvWindow: int

        :returns: API response

        See order endpoint for full response options

        :raises: BinanceRequestException, BinanceAPIException, BinanceOrderException, BinanceOrderMinAmountException, BinanceOrderMinPriceException, BinanceOrderMinTotalException, BinanceOrderUnknownSymbolException, BinanceOrderInactiveSymbolException

        """
        params.update({
            'side': self.SIDE_SELL
        })
        return self.order_limit(timeInForce=timeInForce, **params)

    def order_market(self, **params):
        """Send in a new market order

        :param symbol: required
        :type symbol: str
        :param side: required
        :type side: str
        :param quantity: required
        :type quantity: decimal
        :param quoteOrderQty: amount the user wants to spend (when buying) or receive (when selling)
            of the quote asset
        :type quoteOrderQty: decimal
        :param newClientOrderId: A unique id for the order. Automatically generated if not sent.
        :type newClientOrderId: str
        :param newOrderRespType: Set the response JSON. ACK, RESULT, or FULL; default: RESULT.
        :type newOrderRespType: str
        :param recvWindow: the number of milliseconds the request is valid for
        :type recvWindow: int

        :returns: API response

        See order endpoint for full response options

        :raises: BinanceRequestException, BinanceAPIException, BinanceOrderException, BinanceOrderMinAmountException, BinanceOrderMinPriceException, BinanceOrderMinTotalException, BinanceOrderUnknownSymbolException, BinanceOrderInactiveSymbolException

        """
        params.update({
            'type': self.ORDER_TYPE_MARKET
        })
        return self.create_order(**params)

    def order_market_buy(self, **params):
        """Send in a new market buy order

        :param symbol: required
        :type symbol: str
        :param quantity: required
        :type quantity: decimal
        :param quoteOrderQty: the amount the user wants to spend of the quote asset
        :type quoteOrderQty: decimal
        :param newClientOrderId: A unique id for the order. Automatically generated if not sent.
        :type newClientOrderId: str
        :param newOrderRespType: Set the response JSON. ACK, RESULT, or FULL; default: RESULT.
        :type newOrderRespType: str
        :param recvWindow: the number of milliseconds the request is valid for
        :type recvWindow: int

        :returns: API response

        See order endpoint for full response options

        :raises: BinanceRequestException, BinanceAPIException, BinanceOrderException, BinanceOrderMinAmountException, BinanceOrderMinPriceException, BinanceOrderMinTotalException, BinanceOrderUnknownSymbolException, BinanceOrderInactiveSymbolException

        """
        params.update({
            'side': self.SIDE_BUY
        })
        return self.order_market(**params)

    def order_market_sell(self, **params):
        """Send in a new market sell order

        :param symbol: required
        :type symbol: str
        :param quantity: required
        :type quantity: decimal
        :param quoteOrderQty: the amount the user wants to receive of the quote asset
        :type quoteOrderQty: decimal
        :param newClientOrderId: A unique id for the order. Automatically generated if not sent.
        :type newClientOrderId: str
        :param newOrderRespType: Set the response JSON. ACK, RESULT, or FULL; default: RESULT.
        :type newOrderRespType: str
        :param recvWindow: the number of milliseconds the request is valid for
        :type recvWindow: int

        :returns: API response

        See order endpoint for full response options

        :raises: BinanceRequestException, BinanceAPIException, BinanceOrderException, BinanceOrderMinAmountException, BinanceOrderMinPriceException, BinanceOrderMinTotalException, BinanceOrderUnknownSymbolException, BinanceOrderInactiveSymbolException

        """
        params.update({
            'side': self.SIDE_SELL
        })
        return self.order_market(**params)