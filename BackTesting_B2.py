# Back Testing Program for an Exponential Moving Average Cross Over Trading Algorithm
# By: Maximilian Was Damji
# Time reported and given in Universal Time Coordinated timezone

import datetime as date
import requests
import pytz

import tableprint
import numpy as np

print('Date must be given in year, month, date, hour, minute, second format.')
print('Year is a four digit number, month is a two digit number,')
print('date is a two digit number, hour is a two digit number,')
print('minute is a two digit number and second is a two digit number.')
print('For example, "2016-01-01 14:30:00" is a valid string.')
print('BackTesting Date:')

END_TIME = str(input())

PERIOD = int(300)
DATA_POINTS = int(500)

CURRENCY_PAIR = str('USDT_BTC')

LONG = int(30)
SHORT = int(5)

# String -> Float
# String must be given in year, month, date, hour, minute, second format.
# Year is a four digit number, month is a two digit number,
# date is a two digit number, hour is a two digit number,
# minute is a two digit number and second is a two digit number.
# For example, "2016-01-01 14:30:00" is a valid string.
# For a given string, yeilds a unix time stamp.

def date_converter(string):
	date_t = pytz.utc.localize(date.datetime.strptime(string,"%Y-%m-%d %H:%M:%S"))
	unix_t = date.datetime.timestamp(date_t)
	return(unix_t)

# String & Float & Float & Float -> ListOfFloat
# For a currency pair, start time in unix time,
# end time in unix time and period between price data in seconds,
# yeild a list of float representing the prices of the given currency pair.

def fetch_past(pair, start, end, period):
	j_data = requests.get('https://poloniex.com/public?command=returnChartData&currencyPair={0}&start={1}&end={2}&period={3}'.format(str(pair), str(start), str(end), str(period)))
	d_list = j_data.json()
	price_list = list()
	for i in d_list:
		price_list.append(i['close'])
		# One can request the following:
		# "date", "high", "low", "open", "close", "volume", "quoteVolume", "weightedAverage"
	return(price_list)

# Float Integer -> Float
# Yeilds a float equal to the original float
# subtracted by period * data_points

def start_time(end_t):
	start_t = float(end_t - (PERIOD * DATA_POINTS))
	return(start_t)

# String -> ListOfPrice

# For a given string, yeilds a list of past prices.
# The number of elements in the list is equal to data_points.
# The interval of time between each data point is specified by period.
# String must be given in year, month, date, hour, minute, second format.
# Year is a four digit number, month is a two digit number,
# date is a two digit number, hour is a two digit number
# minute is a two digit number and second is a two digit number.
# For example, "2016-01-01 14:30:00" is a valid string.

# <template as function composition>

def list_price(date):
	return(fetch_past(CURRENCY_PAIR, start_time(date_converter(date)), date_converter(date), PERIOD))

# ListOfFloat & Integer & Integer -> Float
# For a given list of prices, number of values to include
# in the exponential average, the position of the most
# weighted value in the list of prices.
# The most weighted value is the last value
# to be considered in the exponential average.

def ema(list, bin, position):
	if bin > position:
		return(list[position])
	else:
		return((list[position] - ema(list, bin, (position - 1))) * (2 / (bin + 1)) + ema(list, bin, (position - 1)))

# ListOfFloat -> ListOfFloat
# Yeilds a list of exponential averages.

def ema_list(p_list, bin):
	A_LIST = list()
	P_EMA = float()

	for i in range(len(p_list)):
		if bin > i:
			P_EMA = p_list[i]
			A_LIST.append(P_EMA)
		else:
			P_EMA = (p_list[i] - P_EMA) * (2 / (bin + 1)) + P_EMA
			A_LIST.append(P_EMA)

	return(A_LIST)

# ListOfFloat & Integer & Integer -> ListOfString
# For a given list of prices, bin value one and bin value two,
# yeild a list of actions where the actions
# are one of the following:
# - buy
# - sell
# - null

def action(p_list, short, long):
	action_list = list()
	short_ema = ema_list(p_list, short)
	long_ema = ema_list(p_list, long)

	for i in range(len(p_list)):
		action_list.append(short_ema[i] > long_ema[i])

	return(action_list)

# ListOfBoolean -> ListOfString
# If the past boolean is the same as the current boolean, yeild an empty string
# If the present boolean is True and the past boolean is False, yeild 'Buy'
# else, yeild 'sell'

def action_list(b_list):
        action = ['']
        for i in range(len(b_list) - 1):
                if b_list[i] == b_list[i+1]:
                        action.append('')
                else:
                        if b_list[i+1]:
                                action.append('buy')
                        else:
                                action.append('sell')
        return(action)



tableprint.banner('Exponential Moving Average Cross Over Strategy')

PRICE_LIST = list_price(END_TIME)
SHORT_EMA = ema_list(PRICE_LIST, SHORT)
LONG_EMA = ema_list(PRICE_LIST, LONG)
ACTION_LIST = action_list(action(PRICE_LIST, SHORT, LONG))








# Dictionaries

ACCOUNT_A1 = {'USD' : 1000.00 , 'BTC' : 0.0}
BOOLEAN_ACTION = {True : 'buy', False : 'sell'}
BOOLEAN_CURRENCY = {True : 'BTC', False : 'USD'}
BOOLEAN_PRICE = {True : 1, False: -1}

# Account Currency Currency Float Float -> Account
# For a given account, currency to be sold, currency to be bought,
# amount of currency to be sold and price of currency to be bought,
# yeild an account with the exchange cleared.
# The price of the currency to be bought must be given in the currency to be sold.

def exchange(account, sell, buy, amount, price):
        account[sell] -= amount
        account[buy] += amount / price
        print(account)

# exchange(ACCOUNT_A1, 'USD', 'BTC', 1000.0, 500.0)

# Review and fix this function

def list_balance(price_list, action_list, account):
	SEARCH_BOOLEAN = True
	
	for i in range(len(action_list)):
		if BOOLEAN_ACTION[SEARCH_BOOLEAN] == action_list[i]:
			SELL = BOOLEAN_CURRENCY[not SEARCH_BOOLEAN]
			BUY = BOOLEAN_CURRENCY[SEARCH_BOOLEAN]
			AMOUNT = account[BOOLEAN_CURRENCY[not SEARCH_BOOLEAN]]
			PRICE = price_list[i] ** BOOLEAN_PRICE[SEARCH_BOOLEAN]
			exchange(account, SELL, BUY, AMOUNT, PRICE)
			
			SEARCH_BOOLEAN = not SEARCH_BOOLEAN
		else:
			pass





headers = ['Price', 'E. Average {}'.format(str(SHORT)), 'E. Average {}'.format(str(LONG)), 'State']

t_data = np.array([PRICE_LIST, SHORT_EMA, LONG_EMA, ACTION_LIST])
data = np.transpose(t_data)

tableprint.table(data, headers, width=30)

list_balance(PRICE_LIST, ACTION_LIST, ACCOUNT_A1)
