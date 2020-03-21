from ftx.rest.client import FtxClient


class Position:
    def __init__(self, client, sub_account, market, cost, open_size, entry_price, recent_pnl, alltime_pnl):
        self.client = client
        self.sub_account = sub_account
        self.market = market
        self.cost = cost
        self.open_size = open_size
        self.entry_price = entry_price
        self.recent_pnl = recent_pnl
        self.alltime_pnl = alltime_pnl
        self.pnl_percent = 0

    @property
    def side(self):
        if self.open_size == 0:
            return "Flat"
        elif self.open_size > 0:
            return "Long"
        elif self.open_size < 0:
            return "Short"

    # @property
    # def current_pnl(self):
    #     self.client: FtxClient
    #     mark_price = self.client.get_last_price(self.market)
    #     pnl = 0
    #
    #     price_diff = mark_price - self.entry_price
    #     percent_diff = (price_diff / self.entry_price)
    #
    #     if self.side == 'Long':
    #         pnl = (price_diff * abs(self.open_size))
    #     elif self.side == 'Short':
    #         pnl = (price_diff * abs(self.open_size) * -1)
    #     else:
    #         pnl = 0
    #
    #     open_value = abs(self.open_size) * self.entry_price
    #     pnl_percent = pnl / open_value * 100
    #     self.pnl_percent = pnl_percent
    #     return pnl


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

    def by_sub_list_positions(self, sub_account: str):
        positions = []
        client: FtxClient = self.sub_accounts[sub_account]
        client_positions = client.get_positions()
        for pos in client_positions:
            pnl = pos.get('recentPnl')
            if pnl is None:
                pnl = 0
            position_object = Position(client, sub_account, pos['future'], pos['cost'], pos['netSize'],
                                       pos['entryPrice'], pnl, pos['realizedPnl'])
            positions.append(position_object)
        return positions

    def list_all_positions(self):
        positions = []
        for sub in self.sub_account_names:
            sub_positions = self.by_sub_list_positions(sub)
            positions.extend(sub_positions)
        return positions

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
