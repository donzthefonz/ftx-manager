from ftx.rest.client import FtxClient


class Order:
    def __init__(self, market, side, price_low, price_high, order_type, size, reduce_only=False):
        self.market = market
        self.side = side
        self.price_low = price_low
        self.price_high = price_high
        self.order_type = order_type
        self.reduce_only = reduce_only

    @property
    def scaled_order(self):
        if self.price_low == self.price_high:
            return False
        else:
            return True


class FTXMasterAccount:
    def __init__(self, key, secret, account_name, settings):
        self.account_name = account_name
        self.client: FtxClient
        self.key = key
        self.secret = secret
        self.sub_account_names = []
        self.sub_accounts = {}
        self.anti_algo_subaccount = FtxClient
        self.anti_algo_subaccount_name = ''
        self.settings = settings

    def initialise(self):
        self.connect()
        if len(self.sub_account_names) == 0:
            # Get all sub accounts
            self.sub_account_names = self.get_sub_account_names()

        for sub in self.sub_account_names:
            client = FtxClient(self.key, self.secret, sub)
            self.sub_accounts[sub] = client
        self.anti_algo_subaccount_name = FtxClient(self.key, self.secret, self.anti_algo_subaccount_name)

    def connect(self, account_name=None):
        if account_name is not None:
            self.client = FtxClient(self.key, self.secret,
                                    account_name)
        else:
            self.client = FtxClient(self.key, self.secret)

    @property
    def total_usd_value(self):
        """ Returns the total USD value of all accounts."""
        total_usd = 0
        for sub in self.sub_account_names:
            total_usd = total_usd + self.by_sub_balances_to_usd(sub)
        return total_usd

    @property
    def total_btc_value(self):
        """ Returns the total BTC value of all accounts."""
        total_usd = self.total_usd_value
        markets = self.client.list_markets()
        btc_book = self.client.get_orderbook("BTC/USD", 5)
        btc_price = btc_book['asks'][0][0]
        btc_value = total_usd / btc_price
        return btc_value

    @property
    def total_usd_collateral(self):
        """ Returns the total USD collateral and value of all accounts."""
        total_col = 0
        total_usd_val = 0
        for sub in self.sub_account_names:
            col, usd_val = self.by_sub_usd_collateral(sub)
            total_col = total_col + col
            total_usd_val = total_usd_val + usd_val
        return total_col, total_usd_val

    @property
    def total_btc_collateral(self):
        """ Returns the total BTC collateral and value of all accounts."""
        total_col = 0
        total_usd_val = 0
        for sub in self.sub_account_names:
            col, usd_val = self.by_sub_btc_collateral(sub)
            total_col = total_col + col
            total_usd_val = total_usd_val + usd_val
        return total_col, total_usd_val

    @property
    def total_eth_collateral(self):
        """ Returns the total ETH collateral and value of all accounts."""
        total_col = 0
        total_usd_val = 0
        for sub in self.sub_account_names:
            col, usd_val = self.by_sub_eth_collateral(sub)
            total_col = total_col + col
            total_usd_val = total_usd_val + usd_val
        return total_col, total_usd_val

    @property
    def total_ftt_collateral(self):
        """ Returns the total FTT collateral and value of all accounts."""
        total_col = 0
        total_usd_val = 0
        for sub in self.sub_account_names:
            col, usd_val = self.by_sub_ftt_collateral(sub)
            total_col = total_col + col
            total_usd_val = total_usd_val + usd_val
        return total_col, total_usd_val

    def by_sub_balances_to_usd(self, sub_account: str):
        usd = 0
        client: FtxClient = self.sub_accounts[sub_account]
        balances = client.get_balances()
        for balance in balances:
            usd = usd + balance['usdValue']
        return usd

    def by_sub_eth_collateral(self, sub_account: str):
        usd_value = 0
        col = 0
        client: FtxClient = self.sub_accounts[sub_account]
        balances = client.get_balances()
        for balance in balances:
            if balance['coin'] == 'ETH':
                col = col + balance['total']
                usd_value = usd_value + balance['usdValue']
        return col, usd_value

    def by_sub_btc_collateral(self, sub_account: str):
        usd_value = 0
        col = 0
        client: FtxClient = self.sub_accounts[sub_account]
        balances = client.get_balances()
        for balance in balances:
            if balance['coin'] == 'BTC':
                col = col + balance['total']
                usd_value = usd_value + balance['usdValue']
        return col, usd_value

    def by_sub_usd_collateral(self, sub_account: str):
        usd_value = 0
        col = 0
        client: FtxClient = self.sub_accounts[sub_account]
        balances = client.get_balances()
        for balance in balances:
            if balance['coin'] == 'USD' or balance['coin'] == 'USDT':
                col = col + balance['total']
                usd_value = usd_value + balance['usdValue']
        return col, usd_value

    def by_sub_ftt_collateral(self, sub_account: str):
        usd_value = 0
        col = 0
        client: FtxClient = self.sub_accounts[sub_account]
        balances = client.get_balances()
        for balance in balances:
            if balance['coin'] == 'FTT':
                col = col + balance['total']
                usd_value = usd_value + balance['usdValue']
        return col, usd_value

    def get_sub_account_names(self):
        names = []
        subs = self.client.list_sub_accounts()
        for sub in subs:
            names.append(sub['nickname'])
        return names

    def scaled_order_by_sub(self, subaccount_name, order: Order):
        client: FtxClient = self.sub_accounts[subaccount_name]
        # TODO: scaled order for asset, side, size, low, high, spread
        pass