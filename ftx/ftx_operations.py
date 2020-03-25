from ftx.rest.client import FtxClient


class Balance:
    def __init__(self, coin, usd_value, total, free):
        self.coin = coin
        self.usd_value = usd_value
        self.total = total
        self.free = free


class SubBalance:
    def __init__(self, sub_name, usd_value, balances: [Balance]):
        self.sub_name = sub_name
        self.usd_value = usd_value
        self.balances = balances


class TransferInstructions:
    def __init__(self, coin, size, source_account, destination_account):
        self.coin = coin
        self.size = size
        self.source_account = source_account
        self.destination_account = destination_account


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
        total_usd = total_usd + self.by_sub_balances_to_usd()
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
        col, usd_val = self.by_sub_usd_collateral()
        total_col = total_col + col
        total_usd_val = total_usd_val + usd_val
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
        col, usd_val = self.by_sub_btc_collateral()
        total_col = total_col + col
        total_usd_val = total_usd_val + usd_val
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
        col, usd_val = self.by_sub_eth_collateral()
        total_col = total_col + col
        total_usd_val = total_usd_val + usd_val
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
        col, usd_val = self.by_sub_ftt_collateral()
        total_col = total_col + col
        total_usd_val = total_usd_val + usd_val
        for sub in self.sub_account_names:
            col, usd_val = self.by_sub_ftt_collateral(sub)
            total_col = total_col + col
            total_usd_val = total_usd_val + usd_val
        return total_col, total_usd_val

    def by_sub_balances_to_usd(self, sub_account: str = None):
        usd = 0
        if sub_account:
            client: FtxClient = self.sub_accounts[sub_account]
        else:
            client = self.client
        balances = client.get_balances()
        for balance in balances:
            usd = usd + balance['usdValue']
        return usd

    def by_sub_eth_collateral(self, sub_account: str = None):
        usd_value = 0
        col = 0
        if sub_account:
            client: FtxClient = self.sub_accounts[sub_account]
        else:
            client = self.client
        balances = client.get_balances()
        for balance in balances:
            if balance['coin'] == 'ETH':
                col = col + balance['total']
                usd_value = usd_value + balance['usdValue']
        return col, usd_value

    def by_sub_btc_collateral(self, sub_account: str = None):
        usd_value = 0
        col = 0
        if sub_account:
            client: FtxClient = self.sub_accounts[sub_account]
        else:
            client = self.client
        balances = client.get_balances()
        for balance in balances:
            if balance['coin'] == 'BTC':
                col = col + balance['total']
                usd_value = usd_value + balance['usdValue']
        return col, usd_value

    def by_sub_usd_collateral(self, sub_account: str = None):
        usd_value = 0
        col = 0
        if sub_account:
            client: FtxClient = self.sub_accounts[sub_account]
        else:
            client = self.client
        balances = client.get_balances()
        for balance in balances:
            if balance['coin'] == 'USD' or balance['coin'] == 'USDT':
                col = col + balance['total']
                usd_value = usd_value + balance['usdValue']
        return col, usd_value

    def by_sub_ftt_collateral(self, sub_account: str = None):
        usd_value = 0
        col = 0
        if sub_account:
            client: FtxClient = self.sub_accounts[sub_account]
        else:
            client = self.client
        balances = client.get_balances()
        for balance in balances:
            if balance['coin'] == 'FTT':
                col = col + balance['total']
                usd_value = usd_value + balance['usdValue']
        return col, usd_value

    def by_sub_list_positions(self, sub_account: str = None):
        positions = []
        if sub_account:
            client: FtxClient = self.sub_accounts[sub_account]
        else:
            client = self.client
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
        sub_positions = self.by_sub_list_positions()
        positions.extend(sub_positions)
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

    def scaled_order_all(self, market, side, high, low, percent_size, no_orders=20):
        subs = self.sub_account_names
        for sub in subs:
            self.by_sub_scaled_order(sub, market, side, high, low, percent_size, no_orders)

    def by_sub_scaled_order(self, subaccount_name, market, side, high, low, percent_size, no_orders=10):
        if subaccount_name is not None:
            client: FtxClient = self.sub_accounts[subaccount_name.upper()]
        else:
            client = self.client
        usd_size = client.get_free_usd_balance()
        usd_pos_size = usd_size / 100 * percent_size
        coin_price = client.get_last_price(market)
        coin_size = usd_pos_size / coin_price
        if usd_pos_size / no_orders > 1:
            client.place_scaled_order(market, side, high, low, coin_size, no_orders)
            print(
                "Successfully placed scaled order in Sub Account: {}    |   Market: {}".format(subaccount_name, market))
            return True
        else:
            print("USD Balance too low for this order. Free USD: ${}   |   Sub Account: {}".format(usd_size,
                                                                                                   subaccount_name))
            return False

    def by_sub_find_open_position_by_market(self, subaccount_name, market_str):
        if subaccount_name is not None:
            client: FtxClient = self.sub_accounts[subaccount_name.upper()]
        else:
            client = self.client
        positions = client.get_positions()
        positions_to_close = []
        for position in positions:
            if position.get('netSize') != 0:
                if position.get('future').lower() == market_str:
                    positions_to_close.append(position)
                elif market_str == 'all':
                    positions_to_close.append(position)
                elif market_str == 'long':
                    if position.get('netSize') > 0:
                        positions_to_close.append(position)
                elif market_str == 'short':
                    if position.get('netSize') < 0:
                        positions_to_close.append(position)
        return positions_to_close

    def by_sub_close_positions(self, subaccount_name, positions, close_percent):
        if subaccount_name is not None:
            client: FtxClient = self.sub_accounts[subaccount_name.upper()]
        else:
            client = self.client
        result = None
        for position in positions:
            close_size = position.get('openSize') / 100 * close_percent
            if position.get('netSize') > 0:
                # Position is Long so we must sell
                result = client.place_order(market=position.get('future'), side='sell', price=None, type='market',
                                            size=close_size, reduce_only=True)
            elif position.get('netSize') < 0:
                # Position is Short so we must buy
                result = client.place_order(market=position.get('future'), side='buy', price=None, type='market',
                                            size=close_size, reduce_only=True)
        return result

    def close_positions(self, market_str, close_percent):
        for sub in self.sub_account_names:
            positions = self.by_sub_find_open_position_by_market(sub, market_str)
            if len(positions) > 0:
                self.by_sub_close_positions(sub, positions, close_percent)

    def all_usd_flat(self):
        for sub in self.sub_account_names:
            self.by_sub_usd_flat(sub)

    def by_sub_usd_flat(self, subaccount_name):
        if subaccount_name is not None:
            client: FtxClient = self.sub_accounts[subaccount_name.upper()]
        else:
            client = self.client
        balances = client.get_balances()
        for balance in balances:
            if balance['coin'] == 'BTC' or balance['coin'] == 'ETH':
                free = balance['free']
                if free > 0:
                    market = balance['coin'] + '/USD'
                    client.place_order(market, 'sell', price=None, size=free, type='market')

    def get_all_balances(self):
        sub_balances_list = []
        balances, total_usd_value = self.by_sub_get_balances()
        sub_balance = SubBalance('Main Account', total_usd_value, balances)
        sub_balances_list.append(sub_balance)
        for sub in self.sub_account_names:
            balances, total_usd_value = self.by_sub_get_balances(sub)
            sub_balance = SubBalance(sub, total_usd_value, balances)
            sub_balances_list.append(sub_balance)

        return sub_balances_list

    def by_sub_get_balances(self, subaccount_name=None):
        if subaccount_name is not None:
            client: FtxClient = self.sub_accounts[subaccount_name.upper()]
        else:
            client = self.client
        balances = client.get_balances()
        balance_objects = []
        total_usd_value = 0
        for balance in balances:
            balance_object = Balance(balance['coin'], balance['usdValue'], balance['total'], balance['free'])
            balance_objects.append(balance_object)
            total_usd_value = total_usd_value + balance['usdValue']
        return balance_objects, total_usd_value
