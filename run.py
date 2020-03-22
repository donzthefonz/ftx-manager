# -*- coding: utf-8 -*-
"""
* Pizza delivery prompt example
* run example by writing `python example/pizza.py` in your console
"""
from __future__ import print_function, unicode_literals

import regex
from pprint import pprint

from PyInquirer import style_from_dict, Token, prompt
from PyInquirer import Validator, ValidationError, print_json

from examples import custom_style_3, custom_style_2, custom_style_1
import yaml
from ftx.ftx_operations import FTXMasterAccount, Position, Order
from tabulate import tabulate

from babel.numbers import format_currency

# Initialise Variables
global master
master: FTXMasterAccount


class objdict(dict):
    def __getattr__(self, name):
        if name in self:
            return self[name]
        else:
            raise AttributeError("No such attribute: " + name)

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        if name in self:
            del self[name]
        else:
            raise AttributeError("No such attribute: " + name)


def print_formatting():
    print(" ")
    print(" ")
    print("===========================================================================================================")


def print_title(word):
    length = len(word)
    topline = ''
    line = ''
    for x in range(length):
        line = line + '_'
        topline = topline + '-'
    print(" ")
    print(topline)
    print(word)
    print(topline)
    print(" ")


def validate(document):
    ok = regex.match(
        '^([01]{1})?[-.\s]?\(?(\d{3})\)?[-.\s]?(\d{3})[-.\s]?(\d{4})\s?((?:#|ext\.?\s?|x\.?\s?){1}(?:\d+)?)?$',
        document.text)
    if not ok:
        raise ValidationError(
            message='Please enter a valid phone number',
            cursor_position=len(document.text))  # Move cursor to end


def validate_percent(document):
    try:
        int(document)
        ok = False
        if (int(document) and (int(document) > 0) and (int(document) < 101)):
            ok = True
        if not ok:
            raise ValidationError(
                message='Please enter a valid number between 1 and 100.',
                cursor_position=len(document.text))  # Move cursor to end
    except ValueError:
        raise ValidationError(
            message='Please enter a number between 1 and 100',
            cursor_position=len(document.text))  # Move cursor to end


class NumberValidator(Validator):
    def validate(self, document):
        try:
            int(document.text)
        except ValueError:
            raise ValidationError(
                message='Please enter a number',
                cursor_position=len(document.text))  # Move cursor to end


print('FTX Portfolio Manager')
print('')


def initialise_yaml():
    try:
        with open(r'configuration_dev.yaml') as file:
            dataMap = yaml.safe_load(file)
            return dataMap
    except Exception as e:
        with open(r'configuration.yaml') as file:
            dataMap = yaml.safe_load(file)
            return dataMap


def get_master_accounts():
    config = initialise_yaml()
    accounts = config['accounts']
    return accounts


def always_show(answers):
    return True


def get_master_account_list():
    accounts = get_master_accounts()
    names = []
    for account in accounts:
        names.append(account['account_name'])
    return names


def get_positions_list(answers):
    position_list = []
    positions = master.list_all_positions()
    for position in positions:
        position: Position
        # position_details = "Market: {}  |   Side: {}  |   PnL: {}".format(str(position.market), str(position.side),
        #                                                                 str(position.recent_pnl))
        position_details = position.market
        position_list.append(position_details)
    return position_list


def get_sub_account_list(answers):
    accounts = []
    accounts.append('All Accounts')
    accounts.extend(master.sub_account_names)
    return accounts


def get_spot_markets(answers):
    print(answers)
    names = []
    markets = master.client.list_spot_markets()
    for market in markets:
        names.append(market.get('name'))
    return names


def parse_close_positions(answers, master_account):
    try:
        message = ''
        # print("get_positions_confirmation_message")
        # print(answers)
        if answers['positions_operation'] != 'close a position':
            if answers['positions_operation'] == 'close all positions':
                market = 'all'
                market_message = 'All Positions'
            elif answers['positions_operation'] == 'close long positions':
                market = 'long'
                market_message = 'All Long Positions'
            elif answers['positions_operation'] == 'close short positions':
                market = 'short'
                market_message = 'All Short Positions'
        else:
            market = answers['which_position']
            market_message = 'position in ' + answers['which_position']
        close_size = int(answers['close_percent'])
        if close_size > 0 and close_size < 101:
            print("Are you sure you want to close [{}] by [{}%]?".format(market_message, close_size))
            return market, close_size
        else:
            print("Can't close position size by [{}]. Please try again and choose a number between 1 and 100.")
            ask_root_question(master_account)
    except Exception as e:
        print(e)


master_account_question = [{
    'type': 'list',
    'name': 'account_name',
    'message': 'What master account do you want to use?',
    'choices': get_master_account_list(),
    'filter': lambda val: val.lower(),
    'when': always_show
}]

operation_question = [{
    'type': 'list',
    'name': 'operation',
    'message': 'What operation do you want to perform?',
    'choices': ['View Balances', 'Track Liquidity', 'View Positions', 'Close Positions', 'Rebalance Portfolio',
                'Scaled Order', 'Exit'],
    'filter': lambda val: val.lower(),
    'when': always_show
}]

scaled_order_questions = [
    {
        'type': 'list',
        'name': 'account_question',
        'message': 'Which account do you want to trade from?',
        'choices': get_sub_account_list,
        'filter': lambda val: val.lower(),
        'when': always_show
    },
    {
        'type': 'list',
        'name': 'asset_question',
        'message': 'Which asset do you want to trade?',
        # 'choices': get_account_choices(),
        'choices': ["BTC/USD", "ETH/USD", "FTT/USD"],
        'filter': lambda val: val.lower(),
        'when': always_show
    },
    {
        'type': 'list',
        'name': 'buy_or_sell',
        'message': 'Buying or selling?',
        # 'choices': get_account_choices(),
        'choices': ["Buy", "Sell"],
        'filter': lambda val: val.lower(),
        'when': always_show
    },
    {
        'type': 'input',
        'name': 'trade_percentage',
        'message': 'What percentage of your available holdings do you want to buy/sell?',
        'when': always_show
    },
    {
        'type': 'input',
        'name': 'price_high',
        'message': 'Enter the highest limit price you want to trade?',
        'when': always_show
    },
    {
        'type': 'input',
        'name': 'price_low',
        'message': 'Enter the lowest limit price you want to trade?',
        'when': always_show
    }
]

account_question = [{
    'type': 'list',
    'name': 'account_question',
    'message': 'Which account is the "empty" one that you want to centralise funds in before distributing?',
    # 'choices': get_account_choices(),
    'choices': ['get choices'],
    'filter': lambda val: val.lower()
}]

confirm_question = [
    {
        'type': 'list',
        'name': 'confirm',
        'message': 'Are you sure you want to continue?',
        'choices': ['No', 'Yes'],
        'filter': lambda val: val.lower()
    }]

position_questions = [
    {
        'type': 'list',
        'name': 'positions_operation',
        'message': 'What do you want to do with your positions?',
        'choices': ['Close a Position', 'Close All Positions', 'Close Long Positions', 'Close Short Positions'],
        'filter': lambda val: val.lower()
    }
    ,
    {
        'type': 'list',
        'name': 'which_position',
        'message': 'Which position do you want to alter?',
        'choices': get_positions_list,
        'filter': lambda val: val.lower(),
        'when': lambda answers: answers['positions_operation'] == 'close a position'
    },
    {
        'type': 'input',
        'name': 'close_percent',
        'message': 'What percentage of the chosen positions do you want to close? Enter a number between 1 and 100.',
    },
]

rebalance_question = [{
    'type': 'list',
    'name': 'warning_question',
    'message': 'This will mean closing any positions you have open in any accounts affected, do you want to continue?',
    'choices': ['Yes', 'No'],
    'filter': lambda val: val.lower()
}]

questions = [
    {
        'type': 'list',
        'name': 'operation',
        'message': 'What operation do you want to perform?',
        'choices': ['Close Positions', 'Rebalance Portfolio', 'Small'],
        'filter': lambda val: val.lower()
    },
    {
        'type': 'input',
        'name': 'quantity',
        'message': 'How many do you need?',
        'validate': NumberValidator,
        'filter': lambda val: int(val)
    },
    {
        'type': 'expand',
        'name': 'toppings',
        'message': 'What about the toppings?',
        'choices': [
            {
                'key': 'p',
                'name': 'Pepperoni and cheese',
                'value': 'PepperoniCheese'
            },
            {
                'key': 'a',
                'name': 'All dressed',
                'value': 'alldressed'
            },
            {
                'key': 'w',
                'name': 'Hawaiian',
                'value': 'hawaiian'
            }
        ]
    },
    {
        'type': 'rawlist',
        'name': 'beverage',
        'message': 'You also get a free 2L beverage',
        'choices': ['Pepsi', '7up', 'Coke']
    },
    {
        'type': 'input',
        'name': 'comments',
        'message': 'Any comments on your purchase experience?',
        'default': 'Nope, all good!'
    },
    {
        'type': 'list',
        'name': 'prize',
        'message': 'For leaving a comment, you get a freebie',
        'choices': ['cake', 'fries'],
        'when': lambda answers: answers['comments'] != 'Nope, all good!'
    }
]


# def initialise_account(master_account):
#     sub_accounts: list = []
#     initialised_master: FTXMasterAccount = None
#
#     for key, account in master_account.items():
#         if account['master_account']:
#             initialised_master = FTXMasterAccount(account['api_key'], account['api_secret'])
#             initialised_master.connect()
#         client_account = FTXAccount(account['subaccount_name'], account['api_key'], account['api_secret'])
#         #client_account.connect()
#         sub_accounts.append(client_account)
#
#     if initialised_master:
#         initialised_master.sub_accounts = sub_accounts
#         return initialised_master
#
#     return None


def print_account_details(sub_account: FTXMasterAccount):
    try:
        account_info = sub_account.client.get_account_info()

        print("For sub account: [{}]".format(sub_account.name))
        total_usd_val = sub_account.total_usd_value
        print("Total USD Value of this account: [${}]".format(str(total_usd_val)))

        total_btc_col, btc_usd_val = sub_account.total_btc_collateral
        total_usd_col, usd_usd_val = sub_account.total_usd_collateral
        total_eth_col, eth_usd_val = sub_account.total_eth_collateral
        total_ftt_col, ftt_usd_val = sub_account.total_ftt_collateral

        btc_percent = str(round(btc_usd_val / total_usd_val * 100, 1)) + "%"
        eth_percent = str(round(eth_usd_val / total_usd_val * 100, 1)) + "%"
        usd_percent = str(round(usd_usd_val / total_usd_val * 100, 1)) + "%"
        ftt_percent = str(round(ftt_usd_val / total_usd_val * 100, 1)) + "%"

        table = [["BTC", total_btc_col, btc_usd_val, btc_percent], ["ETH", total_eth_col, eth_usd_val, eth_percent],
                 ["USD", total_usd_col, usd_usd_val, usd_percent], ["FTT", total_ftt_col, ftt_usd_val, ftt_percent],
                 ["Total", 'N/A', total_usd_val, "100%"]]
        headers = ["Asset", "# Coins Owned", "USD Value", "% of Capital"]
        print(tabulate(table, headers=headers, tablefmt='psql', floatfmt='.8f'))
        print("")
        print("======================================================")
        print("======================================================")
        print("")
        # pie_labels = 'BTC', 'USD', 'ETH', 'FTT'
        # pie_data = [btc_usd_val, usd_usd_val, eth_usd_val, ftt_usd_val]
        # figureObject, axesObject = plotter.subplots()
        # # Draw the pie chart
        # axesObject.pie(pie_data,
        #                labels=pie_labels,
        #                autopct='%1.1f%%',
        #                shadow=True,
        #                startangle=90)
        # # Aspect ratio - equal means pie is a circle
        # axesObject.axis('equal')
        # plotter.show()

    except Exception as e:
        print(e)


def print_master_account_summary(account: FTXMasterAccount):
    print_formatting()
    print_title("SUMMARY OF ASSETS")
    account_list = ''
    for sub in sorted(account.sub_account_names):
        account_list = account_list + sub + ', '
    account_list = account_list[:-2]

    print("Master Account: [{}]".format(account.account_name))
    print("Accounts: [{}]".format(account_list))
    print(" ")
    total_usd_val = round(account.total_usd_value, 2)
    total_btc_val = round(account.total_btc_value, 8)
    print("Total USD Value of this account: {}".format(format_currency(total_usd_val, 'USD', locale='en_US')))
    print("Total BTC Value of this account: {} BTC".format(str(total_btc_val)))
    print(" ")

    total_btc_col, btc_usd_val = account.total_btc_collateral
    total_usd_col, usd_usd_val = account.total_usd_collateral
    total_eth_col, eth_usd_val = account.total_eth_collateral
    total_ftt_col, ftt_usd_val = account.total_ftt_collateral

    btc_percent = str(round(btc_usd_val / total_usd_val * 100, 1)) + "%"
    eth_percent = str(round(eth_usd_val / total_usd_val * 100, 1)) + "%"
    usd_percent = str(round(usd_usd_val / total_usd_val * 100, 1)) + "%"
    ftt_percent = str(round(ftt_usd_val / total_usd_val * 100, 1)) + "%"

    table = [["BTC", round(total_btc_col, 8), format_currency(btc_usd_val, 'USD', locale='en_US'), btc_percent],
             ["ETH", total_eth_col, format_currency(eth_usd_val, 'USD', locale='en_US'), eth_percent],
             ["USD", round(total_usd_col, 2), format_currency(usd_usd_val, 'USD', locale='en_US'), usd_percent],
             ["FTT", total_ftt_col, format_currency(ftt_usd_val, 'USD', locale='en_US'), ftt_percent],
             ["Total", 'N/A', format_currency(total_usd_val, 'USD', locale='en_US'), "100%"]]
    headers = ["Asset", "# Coins Owned", "USD Value", "% of Capital"]
    print(tabulate(table, headers=headers, tablefmt='psql', floatfmt='.8f'))
    print_formatting()
    print_title("SUMMARY OF STRATEGIES")
    print("Accounts: [{}]".format(account_list))
    print(" ")

    table = []
    for sub_name, sub_client in account.sub_accounts.items():
        inner_list = []
        inner_list.append(sub_name)
        inner_list.append(format_currency(account.by_sub_balances_to_usd(sub_name), 'USD', locale='en_US'))
        percent_diff = str(round(account.by_sub_balances_to_usd(sub_name) / total_usd_val * 100, 1)) + "%"
        inner_list.append(percent_diff)
        table.append(inner_list)

    headers = ["Sub Account", "USD Value", "% of Capital"]
    print(tabulate(table, headers=headers, tablefmt='psql', floatfmt='.8f'))
    print(" ")
    print("===========================================================================================================")
    print(" ")


def rebalance_operation(master_account):
    pass
    # Ask user which account to centralise all capital before distributing it again.


def track_liquidity(account: FTXMasterAccount):
    """ Print out the current value in USD liquidity for LRAIC tradable assets"""
    print_formatting()
    print_title("LIQUIDITY TRACKER (1% Away from Asks/Bids)")
    assets = []

    if account.settings.liquidity_tracker['all']:
        # Get list of all markets
        markets = account.client.list_markets()
        for market in markets:
            assets.append(market['name'])
    else:
        assets = account.settings.liquidity_tracker['markets_list']

    table = []

    asset_with_liquidty = []

    for asset in assets:
        # Get orderbook details
        book = account.client.get_orderbook(asset, 100)

        ask_price = book['asks'][0][0]
        bid_price = book['bids'][0][0]

        percent_away_from_ask = ask_price * float(1.01)
        percent_away_from_bid = bid_price * float(0.99)

        ask_liquidity = 0

        for ask in book['asks']:
            if ask[0] < percent_away_from_ask:
                ask_liquidity = ask_liquidity + (ask[0] * ask[1])
            else:
                break

        bid_liquidity = 0

        for bid in book['bids']:
            if bid[0] > percent_away_from_bid:
                bid_liquidity = bid_liquidity + (bid[0] * bid[1])
            else:
                break

        liquidy_dict = {}
        liquidy_dict['asset'] = asset
        liquidy_dict['ask_liquidity'] = ask_liquidity
        liquidy_dict['bid_liquidity'] = bid_liquidity

        asset_with_liquidty.append(liquidy_dict)

    # Sort the list by liquidity
    sorted_liquidity = sorted(asset_with_liquidty, key=lambda x: x['bid_liquidity'], reverse=True)

    for asset in sorted_liquidity:
        inner_list = []
        inner_list.append(asset['asset'])
        inner_list.append(format_currency(asset['ask_liquidity'], 'USD', locale='en_US'))
        inner_list.append(format_currency(asset['bid_liquidity'], 'USD', locale='en_US'))
        table.append(inner_list)

    headers = ["Asset", "USD Ask Liquidity", "USD Bid Liquidity"]
    print(tabulate(table, headers=headers, tablefmt='psql', floatfmt='.8f'))
    print_formatting()


def ask_rebalance_question(master_account):
    answers = prompt(rebalance_question, style=custom_style_3)
    if answers['rebalance_operation'] == 'yes':
        # TODO: Implement
        rebalance_operation(master_account)
    elif answers['rebalance_operation'] == 'no':
        ask_root_question(master_account)


def close_all_positions(master_account: FTXMasterAccount):
    for account in master_account.sub_accounts:
        pass
        # Get positions

        # Close positions


def view_positions(master_account):
    print_formatting()
    print_title("ACCOUNT POSITIONS")
    all_positions = master_account.list_all_positions()
    table = []
    for position in all_positions:
        position: Position
        inner_list = []
        inner_list.append(position.market)
        inner_list.append(position.sub_account)
        inner_list.append(position.side)
        inner_list.append(format(position.open_size, '.8f'))
        inner_list.append(format_currency(abs(position.cost), 'USD', locale='en_US'))
        inner_list.append(format_currency(position.recent_pnl, 'USD', locale='en_US'))
        inner_list.append(format_currency(position.alltime_pnl, 'USD', locale='en_US'))

        table.append(inner_list)

    sorted_table = sorted(table, key=lambda x: x[5], reverse=True)
    headers = ["Market", "Sub Account", "Side", "Size", "Cost", "Current PnL", "All Time PnL"]
    print(tabulate(sorted_table, headers=headers, tablefmt='psql', floatfmt='.8f'))
    print_formatting()


def close_positions(master_account: FTXMasterAccount, market: str, close_percent: int):
    """ Close 1 or many positions by X% """
    try:
        master_account.close_positions(market, close_percent=close_percent)
        print("Success!")
    except Exception as e:
        print("Uhoh, Exception!: {}".format(e))
        print("Recommended you check your FTX accounts/positions manually!")


def ask_position_questions(master_account: FTXMasterAccount):
    position_answers = prompt(position_questions, style=custom_style_3)
    market, close_percent = parse_close_positions(position_answers, master_account)
    confirm_answer = prompt(confirm_question, style=custom_style_3)
    if confirm_answer['confirm'] == 'yes':
        close_positions(master_account, market, close_percent)
    else:
        print("Cancelled Operation.")


def ask_order_questions(master_account: FTXMasterAccount):
    scaled_order_answers = prompt(scaled_order_questions, style=custom_style_2)


def ask_root_question(master_account):
    operation_answers = prompt(operation_question, style=custom_style_3)
    # print(str(operation_answers))
    if operation_answers['operation'] == 'close positions':
        ask_position_questions(master_account)
        ask_root_question(master_account)
    elif operation_answers['operation'] == 'view balances':
        print_master_account_summary(master_account)
        ask_root_question(master_account)
    elif operation_answers['operation'] == 'view positions':
        view_positions(master_account)
        ask_root_question(master_account)
    elif operation_answers['operation'] == 'rebalance portfolio':
        # TODO: Implement
        pass
    elif operation_answers['operation'] == 'track liquidity':
        track_liquidity(master_account)
        ask_root_question(master_account)
    elif operation_answers['operation'] == 'scaled order':
        ask_order_questions(master_account)
        ask_root_question(master_account)
    else:
        exit()


def get_account_choices():
    settings = initialise_yaml()
    master_account = settings['accounts']
    return ["CAT", "HAT"]


def print_balances(master_account):
    # for sub_account in master_account.sub_accounts:
    #     sub_account: FTXAccount
    #     print_account_details(sub_account)

    print_master_account_summary(master_account)


def main():
    try:
        config = initialise_yaml()
        accounts = config['accounts']
        settings = config['settings']
        settings = objdict(settings)
        master_account = None
        if len(accounts) > 1:
            try:
                account_answers = prompt(master_account_question, style=custom_style_3)
                for account in accounts:
                    if account['account_name'].lower() == account_answers['account_name']:
                        master_account = account
            except:
                master_account = accounts[0]
                master_account = objdict(master_account)
                print("Defaulting to account: [{}]".format(master_account.account_name))
        elif len(accounts == 1):
            master_account = accounts[0]
        else:
            master_account = None
            print("No master accounts detected. Is your configuration.yaml set up correctly?")

        if master_account is not None:
            master_account = objdict(master_account)
            anti_algo_subaccount_name = master_account.anti_algo_subaccount_name
            subaccount_names = master_account.subaccount_names

            # Initialise accounts
            master_account: FTXMasterAccount = FTXMasterAccount(master_account['api_key'], master_account['api_secret'],
                                                                master_account.account_name, settings)
            if subaccount_names is not None:
                master_account.sub_account_names.extend(subaccount_names)
            master_account.anti_algo_subaccount_name = anti_algo_subaccount_name

            master_account.initialise()

            global master
            master = master_account

            try:
                ask_root_question(master_account)
            except Exception as e:
                print(e)
                # Assume we are in debug mode rather than running from windows CMD
                # Run feature being tested
                master_account.scaled_order_by_sub('BF-EOS', 'BTC/USD', 'buy', 4500, 3000, 0.005, no_orders=20)


    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
