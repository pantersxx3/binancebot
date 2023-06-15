"""
Horacio Oscar Fanelli - Pantersxx3
Version: 7.00.0

Disclaimer

All investment strategies and investments involve risk of loss.
Nothing contained in this program, scripts, code or repositoy should be
construed as investment advice.Any reference to an investment's past or
potential performance is not, and should not be construed as, a recommendation
or as a guarantee of any specific outcome or profit.

By using this program you accept all liabilities,
and that no claims can be made against the developers,
or others connected with the program.

See requirements.txt for versions of modules needed

Notes:
- Requires Python version 3.9.x to run

"""
import languages_bot

#use for debug
import traceback

# use for environment variables
import os

# use if needed to pass args to external modules
import sys

# used for math functions
import math
from random import *

# used to create threads & dynamic loading of modules
import threading
import multiprocessing
import importlib
import subprocess

# used for directory handling
import glob

#discord needs import request
import requests

# Needed for colorful console output Install with: python3 -m pip install colorama (Mac/Linux) or pip install colorama (PC)
from colorama import init
init()

# needed for the binance API / websockets / Exception handling
from binance.client import Client
from binance.exceptions import BinanceAPIException
from binance.helpers import round_step_size
from requests.exceptions import ReadTimeout, ConnectionError

# used for dates
from datetime import date, datetime, timedelta
import time

# used to repeatedly execute the code
from itertools import count

# used to store trades and sell assets
import json

#print output tables
from prettytable import PrettyTable, from_html_one

#for regex
import re

#read csv files
import csv

#pandas library
import pandas as pd

import megatronmod

import atexit

# Load helper modules
from helpers.parameters import (
	parse_args, load_config
)

# Load creds modules
from helpers.handle_creds import (
	load_correct_creds, test_api_key,
	load_discord_creds
)

# for colourful logging to the console
class txcolors:
	BUY = '\033[92m'
	WARNING = '\033[93m'
	SELL_LOSS = '\033[94m'
	SELL_PROFIT = '\033[32m'
	DIM = '\033[2m\033[35m'
	BORDER = '\033[33m'
	DEFAULT = '\033[39m'
	BOT_LOSSES = '\033[91m'
	BOT_WINS = '\033[92m'
	RED = '\033[91m'
	#Blue = '\033[94m'
	#Cyan = '\033[96m'
	MENUOPTION = '\033[97m'
	#Magenta = '\033[95m'
	#Grey = '\033[90m'
	#Black = '\033[90m'
	
global session_profit_incfees_perc, session_profit_incfees_total, session_tpsl_override_msg, is_bot_running, session_USDT_EARNED, sell_all_coins
global session_USDT_LOSS, session_USDT_WON, last_msg_discord_balance_date, session_USDT_EARNED_TODAY, parsed_creds, TUP,PUP, TDOWN, c_data
global PDOWN, TNEUTRAL, PNEUTRAL, renewlist, DISABLE_TIMESTAMPS, signalthreads, VOLATILE_VOLUME_LIST, FLAG_PAUSE, coins_up,coins_down, client
global coins_unchanged, SHOW_TABLE_COINS_BOUGHT, USED_BNB_IN_SESSION, PAUSEBOT_MANUAL, sell_specific_coin, lostconnection, FLAG_FILE_READ
global FLAG_FILE_WRITE, historic_profit_incfees_perc, historic_profit_incfees_total, trade_wins, trade_losses, bot_started_datetime
 
last_price_global = 0
session_profit_incfees_perc = 0
session_profit_incfees_total = 0
session_tpsl_override_msg = ""
session_USDT_EARNED = 0
session_USDT_LOSS = 0
session_USDT_WON = 0
last_msg_discord_balance_date = 0
coins_up = 0
coins_down = 0
coins_unchanged = 0
is_bot_running = True
renewlist = 0
FLAG_PAUSE = True
FLAG_FILE_READ = False
FLAG_FILE_WRITE = False
#USED_BNB_IN_SESSION = 0
PAUSEBOT_MANUAL = False
sell_specific_coin = False
sell_all_coins = False
lostconnection = False
signalthreads = []
c_data = pd.DataFrame([])

try:
	historic_profit_incfees_perc
except NameError:
	historic_profit_incfees_perc = 0      # or some other default value.
try:
	historic_profit_incfees_total
except NameError:
	historic_profit_incfees_total = 0      # or some other default value.
try:
	trade_wins
except NameError:
	trade_wins = 0      # or some other default value.
try:
	trade_losses
except NameError:
	trade_losses = 0      # or some other default value.

bot_started_datetime = ""

def show_func_name(function_name, items):
    try:			
        if ENABLE_FUNCTION_NAME:
            fn = str(datetime.now()) + "_" + function_name
            if SHOW_FUNCTION_NAME:  
                if SHOW_VARIABLES_AND_VALUE:
					#all_variables = dir()
					#for name in all_variables:
                    for name, myvalue in items:
						#if not name.startswith('__'):
                        #myvalue = eval(name)
                        print(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.RED}{function_name} = {name}: {myvalue} {sys.getsizeof(name)}')
                else:
                    print(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.RED}{function_name} {varnames}{txcolors.DEFAULT}')
            if SAVE_FUNCTION_NAME:
                if SAVE_VARIABLES_AND_VALUE:
                    #all_variables = dir()
					#for name in all_variables:
                    for name, value in items:
						#myvalue = eval(name)
                        #print("items: name=", name, "value=", value)
                        write_log(function_name + "= \n \t" + name + ": " + str(value) + " \n \t sizeof: " + str(sys.getsizeof(value)), False, False, "list_functions.txt")
                else:
                    write_log(fn, False, False, "list_functions.txt")
    except Exception as e:
        write_log(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.WARNING}func_name: {languages_bot.MSG1[LANGUAGE]}: {e}{txcolors.DEFAULT}')
        write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
        pass       
	#return fn
	
def is_fiat():
	# check if we are using a fiat as a base currency
	global hsp_head
	PAIR_WITH = parsed_config['trading_options']['PAIR_WITH']
	#list below is in the order that Binance displays them, apologies for not using ASC order
	fiats = ['USDT', 'BUSD', 'AUD', 'BRL', 'EUR', 'GBP', 'RUB', 'TRY', 'TUSD', 'USDC', 'PAX', 'BIDR', 'DAI', 'IDRT', 'UAH', 'NGN', 'VAI', 'BVND', 'USDP']

	if PAIR_WITH in fiats:
		return True
	else:
		return False

def decimals():
	# set number of decimals for reporting fractions
	if is_fiat():
		return 4
	else:
		return 8

def get_balance_wallet(crypto):   
	try:
		balance = 0.0        
		if not TEST_MODE: #or not BACKTESTING_MODE:
			balance = float(client.get_asset_balance(asset=crypto)['free'])
			if balance < 10 and not TEST_MODE: #or not BACKTESTING_MODE:
				print(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.WARNING}{languages_bot.MSG34[LANGUAGE]}{txcolors.DEFAULT}')
				sys.exit(0)
		#show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())
	except Exception as e:
		write_log(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.WARNING}get_balance_wallet: {languages_bot.MSG1[LANGUAGE]}: {e}{txcolors.DEFAULT}')
		write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
		pass
	return balance

def extract_first_record(csv_file):
    with open(csv_file, "r") as f:
        reader = csv.reader(f)
        first_row = next(reader)
        first_row = next(reader)
    return first_row[0]

def extract_last_record(csv_file):
    with open(csv_file, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            pass
        last_row = row
    return last_row[0]
    
def update_data_coin():
    global c_data
    if USE_MOST_VOLUME_COINS == True:
        TICKERS = 'volatile_volume_' + str(date.today()) + '.txt'
    else:
        TICKERS = 'tickers.txt'            
    for line in open(TICKERS):
        pairs=[line.strip() + PAIR_WITH for line in open(TICKERS)]    
		
    for coin in pairs:
        filecsv = coin + ".csv"
        if os.path.exists(filecsv):
            fr1 = int(extract_first_record(filecsv))/1000
            os1 = int(time.mktime(datetime.strptime(BACKTESTING_MODE_TIME_START, "%d/%m/%y %H:%M:%S").timetuple()))
            lr1 = int(extract_last_record(filecsv))/1000
            oe1 = int(time.mktime(datetime.strptime(BACKTESTING_MODE_TIME_END, "%d/%m/%y %H:%M:%S").timetuple()))
            if fr1 != os1 or lr1 != oe1:
                os.remove(filecsv)
                c_data = pd.DataFrame([])                
    
def download_data(coin):
    try:
        c = pd.DataFrame([])
        create_conection_binance(True)
        print(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}{languages_bot.MSG3[LANGUAGE]}...{txcolors.DEFAULT}')
        end = time.mktime(datetime.strptime(BACKTESTING_MODE_TIME_END, "%d/%m/%y %H:%M:%S").timetuple()) #datetime.now()
        start = time.mktime(datetime.strptime(BACKTESTING_MODE_TIME_START, "%d/%m/%y %H:%M:%S").timetuple()) #pd.to_datetime(end - timedelta(days = 7))
        data = client.get_historical_klines(str(coin), Client.KLINE_INTERVAL_1MINUTE, int(start) * 1000, int(end) * 1000)
        c = pd.DataFrame(data, columns=['time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume', 'Number of trades', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore'])
        c = c.drop(c.columns[[5, 6, 7, 8, 9, 10, 11]], axis=1)
        c.to_csv(coin + '.csv', index=False)
        c = pd.DataFrame([])
        #show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())
    except Exception as e:
        write_log(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}download_data: {languages_bot.MSG1[LANGUAGE]} download_data(): {e}{txcolors.DEFAULT}')
        write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
        pass

def write_position_csv(coin, position):
	try:
		f = open(coin + '.position', 'w')
		f.write(str(position).replace(".0", ""))
		f.close()
		#show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())
	except Exception as e:
		write_log(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.WARNING}write_position_csv: {languages_bot.MSG1[LANGUAGE]} write_position_csv(): {e}{txcolors.DEFAULT}')
		write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
		pass

def read_position_csv(coin):
	try:
		pos1 = 0
		if os.path.exists(coin + '.position'):
			f = open(coin + '.position', 'r')
			r = f.read().replace(".0", "")
			pos1 = int(r)
			f.close()
		#show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())
	except Exception as e:
		write_log(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.WARNING}read_position_csv: {languages_bot.MSG1[LANGUAGE]} read_position_csv(): {e}{txcolors.DEFAULT}')
		write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
		pass
	return pos1
	
def read_next_row_csv(coin):
    try:
        global c_data
        pos = 0
        price = 0
        time1 = 0
        c = pd.DataFrame([])

        if USE_SIGNALLING_MODULES:
            while not os.path.exists('ok.ok'):
                time.sleep(1/1000)
			
        if os.path.exists(coin + '.position'):
            pos = read_position_csv(coin) 
            if c_data.empty:
                c_data = pd.read_csv(coin + '.csv')            
            c = c_data
            for i in range(len(c)):
                if c.iloc[i]['time'] == pos:
                    if i + 1 == len(c):
                        print(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {languages_bot.MSG4[LANGUAGE]}{txcolors.DEFAULT}...')
                        #convert_csv_to_html(TRADES_LOG_FILE)
                        #menu()
                        sys.exit(0)
                    else:
                        c = c.iloc[i + 1]
                        time1 = c['time']
                        price = c['Close']
                        break
            c = pd.DataFrame([])
            write_position_csv(coin,time1)    
        else:
            c = pd.read_csv(coin + '.csv')
            c.columns = ['time', 'Open', 'High', 'Low', 'Close']
            c['Close'] = c['Close'].astype(float)
            c = c.loc[999]
            price = float(c['Close'])
            time1 = int(c['time'])
            c = pd.DataFrame([])
            write_position_csv(coin,str(time1))

        if USE_SIGNALLING_MODULES: 
            os.remove("ok.ok")
        #show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())
    except Exception as e:
        write_log(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.WARNING}read_next_row_csv: {languages_bot.MSG1[LANGUAGE]} read_next_row_csv(): {e}{txcolors.DEFAULT}')
        write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
        pass
    return price, time1            
				
def get_all_tickers():
    try:
        pairs = {}
        TICKERS = ''
        coins = []
        
        if USE_MOST_VOLUME_COINS == True:
            TICKERS = 'volatile_volume_' + str(date.today()) + '.txt'
        else:
            TICKERS = 'tickers.txt'            
        for line in open(TICKERS):
            pairs=[line.strip() + PAIR_WITH for line in open(TICKERS)]    
		
        for coin in pairs:
            if BACKTESTING_MODE:
                file = coin + '.csv'
                while not os.path.exists(file):
                    download_data(coin)
                #sys.exit(1)
                #price, time = csv_bot.read_next_row_csv(coin) #get_all_tickers 
                price, time = read_next_row_csv(coin)
                print(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {languages_bot.MSG6[LANGUAGE]} {BACKTESTING_MODE_TIME_START} - {txcolors.DEFAULT}{languages_bot.MSG7[LANGUAGE]}: {time} {datetime.fromtimestamp(time/1000).strftime("%d/%m/%y %H:%M:%S")}{txcolors.DEFAULT}')
                coins.append({ 'time': time, 'symbol': coin, 'price': price})
            else:
                c = pd.DataFrame([])
                klines = client.get_historical_klines(symbol=coin, interval=BOT_TIMEFRAME, start_str=str(3) + 'min ago UTC', limit=3)
                c = pd.DataFrame(klines)
                c.columns = ['time', 'Open', 'High', 'Low', 'Close', 'Volume', 'CloseTime', 'QuoteAssetVolume', 'Trades', 'TakerBuyBase', 'TakerBuyQuote', 'Ignore']
                c = c.drop(c.columns[[5, 6, 7, 8, 9, 10, 11]], axis=1)
                c['time'] = pd.to_datetime(c['time'], unit='ms')
                c['Close'] = c['Close'].astype(float)
                coins.append({ 'time': c['time'].iloc[-1], 'symbol': coin, 'price': round(float(c['Close'].iloc[-1]),5)})
                c = pd.DataFrame([])
        #show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())
    except Exception as e:
        write_log(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.WARNING}get_all_tickers: {languages_bot.MSG1[LANGUAGE]} get_all_tickers(): {e}{txcolors.DEFAULT}')
        write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
        pass        
    return coins
	
def get_price(add_to_historical=True, prices = []):
    try:
        '''Return the current price for all coins on binance'''
        global historical_prices, hsp_head
		
        prices = []
        data = {}
        initial_price = {}

        if len(prices) <= 0:
            prices = get_all_tickers() #get_price  
        
        renew_list()

        for coin in prices:
            if CUSTOM_LIST and USE_MOST_VOLUME_COINS == False:
                tickers=[line.strip() for line in open(TICKERS_LIST)]
                for item1 in tickers:
                    if item1 + PAIR_WITH == coin['symbol'] and coin['symbol'].replace(PAIR_WITH, "") not in EX_PAIRS:
                        if BACKTESTING_MODE:
                            initial_price[coin['symbol']] = { 'price': coin['price'], 'time': coin['time']}
                        else:
                            initial_price[coin['symbol']] = { 'price': coin['price'], 'time': datetime.now()} 

            else:
                today = "volatile_volume_" + str(date.today()) + ".txt"
                VOLATILE_VOLUME_LIST=[line.strip() for line in open(today)]
                for item1 in VOLATILE_VOLUME_LIST:
                    if item1 + PAIR_WITH == coin['symbol'] and coin['symbol'].replace(PAIR_WITH, "") not in EX_PAIRS:
                        initial_price[coin['symbol']] = { 'price': coin['price'], 'time': datetime.now()} 

        if add_to_historical:
            hsp_head += 1
            if hsp_head == RECHECK_INTERVAL:
                hsp_head = 0
            historical_prices[hsp_head] = initial_price
        #show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())
    except Exception as e:
        write_log(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.WARNING}get_price: {languages_bot.MSG1[LANGUAGE]} get_price(): {e}{txcolors.DEFAULT}')
        write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
        pass
	#except KeyboardInterrupt as ki:
		#pass
    return initial_price

def get_volume_list():
	try:
		today = "volatile_volume_" + str(date.today()) + ".txt"
		global COINS_MAX_VOLUME, COINS_MIN_VOLUME, VOLATILE_VOLUME, tickers
		volatile_volume_empty = False
		volatile_volume_time = False
		if USE_MOST_VOLUME_COINS:
			today = "volatile_volume_" + str(date.today()) + ".txt"
			now = datetime.now()
			now_str = now.strftime("%d/%m/%y %H_%M_%S")
			dt_string = datetime.strptime(now_str,"%Y-%d/%m %H_%M_%S")
			if VOLATILE_VOLUME == "":
				volatile_volume_empty = True
			else:
				tuple1 = dt_string.timetuple()
				timestamp1 = time.mktime(tuple1)
				
				dt_string_old = datetime.strptime(VOLATILE_VOLUME.replace("(", " ").replace(")", "").replace("volatile_volume_", ""),"%y-%m-%d %H_%M_%S") + timedelta(minutes = UPDATE_MOST_VOLUME_COINS)               
				tuple2 = dt_string_old.timetuple()
				timestamp2 = time.mktime(tuple2)                    
				
				if timestamp1 > timestamp2:
					volatile_volume_time = True
						
			if volatile_volume_empty or volatile_volume_time or os.path.exists(today) == False:             
				VOLATILE_VOLUME = "volatile_volume_" + str(dt_string)
				
				most_volume_coins = {}
				tickers_all = []
				
				prices = client.get_all_tickers()
				
				for coin in prices:
					if coin['symbol'] == coin['symbol'].replace(PAIR_WITH, "") + PAIR_WITH:
						tickers_all.append(coin['symbol'].replace(PAIR_WITH, ""))

				c = 0
				if os.path.exists(VOLATILE_VOLUME + ".txt") == False:
					load_settings()            
					print(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}{languages_bot.MSG35[LANGUAGE]}...')
					if COINS_MAX_VOLUME.isnumeric() == False and COINS_MIN_VOLUME.isnumeric() == False:
						infocoinMax = client.get_ticker(symbol=COINS_MAX_VOLUME + PAIR_WITH)
						infocoinMin = client.get_ticker(symbol=COINS_MIN_VOLUME + PAIR_WITH)
						COINS_MAX_VOLUME1 = float(infocoinMax['quoteVolume']) #math.ceil(float(infocoinMax['quoteVolume']))
						COINS_MIN_VOLUME1 = float(infocoinMin['quoteVolume'])
						most_volume_coins.update({COINS_MAX_VOLUME : COINS_MAX_VOLUME1})
						print(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}COINS_MAX_VOLUME {round(COINS_MAX_VOLUME1)} - COINS_MIN_VOLUME {round(COINS_MIN_VOLUME1)} {languages_bot.MSG8[LANGUAGE]}...{txcolors.DEFAULT}')
					
					for coin in tickers_all:
						#try:
						infocoin = client.get_ticker(symbol= coin + PAIR_WITH)
						volumecoin = float(infocoin['quoteVolume']) #/ 1000000                
						if volumecoin <= COINS_MAX_VOLUME1 and volumecoin >= COINS_MIN_VOLUME1 and coin not in EX_PAIRS and coin not in most_volume_coins:
							most_volume_coins.update({coin : volumecoin})  					
							c = c + 1
						# except Exception as e:
							# print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
							# continue
							
					if c <= 0: 
						print(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}{languages_bot.MSG9[LANGUAGE]}...')
						sys.exit()
						
					sortedVolumeList = sorted(most_volume_coins.items(), key=lambda x: x[1], reverse=True)
					
					now = datetime.now()
					now_str = now.strftime("%y-%m-%d(%H_%M_%S)")
					VOLATILE_VOLUME = "volatile_volume_" + now_str
					
					print(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}{languages_bot.MSG10[LANGUAGE]} {str(c)} {languages_bot.MSG11[LANGUAGE]} {today} ...{txcolors.DEFAULT}')
					
					for coin in sortedVolumeList:
						with open(today,'a+') as f:
							f.write(coin[0] + '\n')
					
					set_config("VOLATILE_VOLUME", VOLATILE_VOLUME)
				else:
					if ALWAYS_OVERWRITE == False:
						print(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}{languages_bot.MSG12[LANGUAGE]}')
						print(f'{txcolors.WARNING}{languages_bot.MSG14[LANGUAGE]}: {txcolors.DEFAULT}{languages_bot.MSG13[LANGUAGE]}...')
			else:    
				VOLATILE_VOLUME = "volatile_volume_" + dt_string
				return VOLATILE_VOLUME
		else:
			tickers=[line.strip() for line in open(TICKERS_LIST)]
		#show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())    
	except Exception as e:
		write_log(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.WARNING}get_volume_list(): {languages_bot.MSG1[LANGUAGE]}: {e}{txcolors.DEFAULT}')
		write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
		print("COIN_ERROR: ", coin + PAIR_WITH)
		exit(1)
	return VOLATILE_VOLUME

def print_table_coins_bought():
    try:
        if SHOW_TABLE_COINS_BOUGHT:
            if len(coins_bought) > 0:
                my_table = PrettyTable()
                my_table.format = True
                my_table.border = True
                my_table.align = "c"
                my_table.valign = "m"
                my_table.left_padding_width = 1
                my_table. right_padding_width = 1
                my_table.field_names = [languages_bot.MSG15[LANGUAGE], languages_bot.MSG21[LANGUAGE], languages_bot.MSG16[LANGUAGE], languages_bot.MSG17[LANGUAGE], "TP %", "SL %", languages_bot.MSG18[LANGUAGE] + " %", languages_bot.MSG19[LANGUAGE] + " $", languages_bot.MSG20[LANGUAGE]]
                last_price = get_price(False)
                for coin in list(coins_bought):
                    LastPriceT = float(last_price[coin]['price'])#,8)
                    sellFeeT = (LastPriceT * (TRADING_FEE/100))
                    sellFeeTotal = (coins_bought[coin]['volume'] * LastPriceT) * (TRADING_FEE/100)
                    LastPriceLessFeesT = (LastPriceT - sellFeeT)
                    LastPricePlusFeesT = (LastPriceT + sellFeeT)
                    BuyPriceT = float(coins_bought[coin]['bought_at'])#,8)
                    buyFeeT = (BuyPriceT * (TRADING_FEE/100))
                    buyFeeTotal = (coins_bought[coin]['volume'] * BuyPriceT) * (TRADING_FEE/100)
                    BuyPricePlusFeesT = (BuyPriceT + buyFeeT)
					#ProfitAfterFees = (LastPricePlusFeesT - BuyPricePlusFeesT)#, 8)
					
					#ProfitAfterFees = (LastPriceT + sellFeeT) - (BuyPriceT + buyFeeT)
                    ProfitAfterFees = (LastPriceT - sellFeeT) - (BuyPriceT + buyFeeT)
					
					#PriceChangeIncFees_Perc = round(float(((LastPriceLessFees - BuyPricePlusFees) / BuyPricePlusFees) * 100), 3)
					#PriceChangeIncFees_PercT = float(((LastPricePlusFeesT - BuyPricePlusFeesT) / BuyPricePlusFeesT) * 100)#, 8)
					
					#PriceChangeIncFees_PercT = float((((LastPriceT + sellFeeT) - (BuyPriceT + buyFeeT)) / (BuyPriceT + buyFeeT)) * 100)#, 8)
                    PriceChangeIncFees_PercT = float((((LastPriceT - sellFeeT) - (BuyPriceT + buyFeeT)) / (BuyPriceT + buyFeeT)) * 100)#, 8)
					
                    PriceChange_PercT = float(((LastPriceT - BuyPriceT) / BuyPriceT) * 100)#, 8)
					#if PriceChangeIncFees_Perc == -100: PriceChangeIncFees_Perc = 0
                    time_held = timedelta(seconds=datetime.now().timestamp()-int(str(coins_bought[coin]['timestamp'])[:10]))
					#if IGNORE_FEE: 
						#my_table.add_row([f"{txcolors.SELL_PROFIT if PriceChangeIncFees_Perc >= 0. else txcolors.RED}{coin.replace(PAIR_WITH,'')}{txcolors.DEFAULT}", f"{txcolors.SELL_PROFIT if PriceChangeIncFees_Perc >= 0. else txcolors.RED}{coins_bought[coin]['volume']:.2f}{txcolors.DEFAULT}", f"{txcolors.SELL_PROFIT if PriceChangeIncFees_Perc >= 0. else txcolors.RED}{BuyPrice:.6f}{txcolors.DEFAULT}", f"{txcolors.SELL_PROFIT if PriceChangeIncFees_Perc >= 0. else txcolors.RED}{LastPrice:.6f}{txcolors.DEFAULT}", f"{txcolors.SELL_PROFIT if PriceChangeIncFees_Perc >= 0. else txcolors.RED}{coins_bought[coin]['take_profit']:.2f}{txcolors.DEFAULT}", f"{txcolors.SELL_PROFIT if PriceChangeIncFees_Perc >= 0. else txcolors.RED}{coins_bought[coin]['stop_loss']:.2f}{txcolors.DEFAULT}", f"{txcolors.SELL_PROFIT if PriceChangeIncFees_Perc >= 0. else txcolors.RED}{PriceChangeIncFees_Perc:.2f}{txcolors.DEFAULT}", f"{txcolors.SELL_PROFIT if PriceChangeIncFees_Perc >= 0. else txcolors.RED}{((float(coins_bought[coin]['volume'])*float(coins_bought[coin]['bought_at']))*PriceChangeIncFees_Perc)/100:.2f}{txcolors.DEFAULT}", f"{txcolors.SELL_PROFIT if PriceChangeIncFees_Perc >= 0. else txcolors.RED}{str(time_held).split('.')[0]}{txcolors.DEFAULT}"])
                    if SELL_ON_SIGNAL_ONLY:
                        my_table.add_row([f"{txcolors.SELL_PROFIT if PriceChangeIncFees_PercT >= 0. else txcolors.RED}{coin.replace(PAIR_WITH,'')}{txcolors.DEFAULT}", f"{txcolors.SELL_PROFIT if PriceChangeIncFees_PercT >= 0. else txcolors.RED}{coins_bought[coin]['volume']:.4f}{txcolors.DEFAULT}", f"{txcolors.SELL_PROFIT if PriceChangeIncFees_PercT >= 0. else txcolors.RED}{BuyPriceT:.6f}{txcolors.DEFAULT}", f"{txcolors.SELL_PROFIT if PriceChangeIncFees_PercT >= 0. else txcolors.RED}{LastPriceT:.6f}{txcolors.DEFAULT}", f"{txcolors.SELL_PROFIT if PriceChangeIncFees_PercT >= 0. else txcolors.RED}per signal{txcolors.DEFAULT}", f"{txcolors.SELL_PROFIT if PriceChangeIncFees_PercT >= 0. else txcolors.RED}per signal{txcolors.DEFAULT}", f"{txcolors.SELL_PROFIT if PriceChangeIncFees_PercT >= 0. else txcolors.RED}{PriceChangeIncFees_PercT:.2f}{txcolors.DEFAULT}", f"{txcolors.SELL_PROFIT if PriceChangeIncFees_PercT >= 0. else txcolors.RED}{((float(coins_bought[coin]['volume'])*float(coins_bought[coin]['bought_at']))*PriceChangeIncFees_PercT)/100:.2f}{txcolors.DEFAULT}", f"{txcolors.SELL_PROFIT if PriceChangeIncFees_PercT >= 0. else txcolors.RED}{str(time_held).split('.')[0]}{txcolors.DEFAULT}"])
                    else:
                        my_table.add_row([f"{txcolors.SELL_PROFIT if PriceChangeIncFees_PercT >= 0. else txcolors.RED}{coin.replace(PAIR_WITH,'')}{txcolors.DEFAULT}", f"{txcolors.SELL_PROFIT if PriceChangeIncFees_PercT >= 0. else txcolors.RED}{coins_bought[coin]['volume']:.4f}{txcolors.DEFAULT}", f"{txcolors.SELL_PROFIT if PriceChangeIncFees_PercT >= 0. else txcolors.RED}{BuyPriceT:.6f}{txcolors.DEFAULT}", f"{txcolors.SELL_PROFIT if PriceChangeIncFees_PercT >= 0. else txcolors.RED}{LastPriceT:.6f}{txcolors.DEFAULT}", f"{txcolors.SELL_PROFIT if PriceChangeIncFees_PercT >= 0. else txcolors.RED}{coins_bought[coin]['take_profit']:.2f}{txcolors.DEFAULT}", f"{txcolors.SELL_PROFIT if PriceChangeIncFees_PercT >= 0. else txcolors.RED}{coins_bought[coin]['stop_loss']:.2f}{txcolors.DEFAULT}", f"{txcolors.SELL_PROFIT if PriceChangeIncFees_PercT >= 0. else txcolors.RED}{PriceChangeIncFees_PercT:.2f}{txcolors.DEFAULT}", f"{txcolors.SELL_PROFIT if PriceChangeIncFees_PercT >= 0. else txcolors.RED}{((float(coins_bought[coin]['volume'])*float(coins_bought[coin]['bought_at']))*PriceChangeIncFees_PercT)/100:.2f}{txcolors.DEFAULT}", f"{txcolors.SELL_PROFIT if PriceChangeIncFees_PercT >= 0. else txcolors.RED}{str(time_held).split('.')[0]}{txcolors.DEFAULT}"])
                #my_table.sortby = SORT_TABLE_BY
                #my_table.reversesort = REVERSE_SORT
                print(my_table)
                my_table = PrettyTable()
        #show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())
    except Exception as e:
        write_log(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.WARNING}print_table_coins_bought: {languages_bot.MSG1[LANGUAGE]}: {e}{txcolors.DEFAULT}')
        write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
        lost_connection(e, "print_table_coins_bought")
        pass


def clear():
	# for windows
	if name == 'nt':
		_ = os.system('cls')  
	# for mac and linux(here, os.name is 'posix')
	else:
		_ = os.system('clear')

def balance_report(last_price):
    try:
        global TRADE_TOTAL, trade_wins, trade_losses, session_profit_incfees_perc, session_profit_incfees_total, last_price_global
        global session_USDT_EARNED, session_USDT_LOSS, session_USDT_WON, TUP, TDOWN, TNEUTRAL, session_USDT_LOSS

        unrealised_session_profit_incfees_perc = 0
        unrealised_session_profit_incfees_total = 0
        msg1 = ""
        msg2 = ""          
        BUDGET = TRADE_SLOTS * TRADE_TOTAL
        exposure_calcuated = 0

        for coin in list(coins_bought):
            LastPriceBR = float(last_price[coin]['price'])
            sellFeeBR = (LastPriceBR * (TRADING_FEE/100))
			
            BuyPriceBR = float(coins_bought[coin]['bought_at'])
            buyFeeBR = (BuyPriceBR * (TRADING_FEE/100))

            exposure_calcuated = exposure_calcuated + round(float(coins_bought[coin]['bought_at']) * float(coins_bought[coin]['volume']),0)

			#PriceChangeIncFees_Perc = float(((LastPrice+sellFee) - (BuyPrice+buyFee)) / (BuyPrice+buyFee) * 100)
			#PriceChangeIncFees_Total = float(((LastPrice+sellFee) - (BuyPrice+buyFee)) * coins_bought[coin]['volume'])
            PriceChangeIncFees_TotalBR = float(((LastPriceBR - sellFeeBR) - (BuyPriceBR + buyFeeBR)) * coins_bought[coin]['volume'])

			# unrealised_session_profit_incfees_perc = float(unrealised_session_profit_incfees_perc + PriceChangeIncFees_Perc)
            unrealised_session_profit_incfees_total = float(unrealised_session_profit_incfees_total + PriceChangeIncFees_TotalBR)
				
        unrealised_session_profit_incfees_perc = (unrealised_session_profit_incfees_total / BUDGET) * 100

        DECIMALS = int(decimals())
		# CURRENT_EXPOSURE = round((TRADE_TOTAL * len(coins_bought)), DECIMALS)
        CURRENT_EXPOSURE = round(exposure_calcuated, 0)
        INVESTMENT_TOTAL = round((TRADE_TOTAL * TRADE_SLOTS), DECIMALS)
		
		# truncating some of the above values to the correct decimal places before printing
        WIN_LOSS_PERCENT = 0
        if (trade_wins > 0) and (trade_losses > 0):
            WIN_LOSS_PERCENT = round((trade_wins / (trade_wins+trade_losses)) * 100, 2)
        if (trade_wins > 0) and (trade_losses == 0):
            WIN_LOSS_PERCENT = 100
        strplus = "+"
        print_banner()
        if STATIC_MAIN_INFO == True: clear()
        my_table = PrettyTable()
        my_table.title = 'BINANCE TRADING BOT'
        my_table.field_names = ['by Pantersxx3']
        my_table.format = True
        my_table.border = True
        my_table.align = "c"
        my_table.valign = "m"
        my_table.header = True
        my_table.padding_width = 3
        my_table.add_row([f'{txcolors.DEFAULT}{languages_bot.MSG22[LANGUAGE]}: {txcolors.SELL_LOSS}{(datetime.fromtimestamp(bot_started_datetime).strftime("%d/%m/%y %H:%M:%S")).split(".")[0]}{txcolors.DEFAULT} | {languages_bot.MSG23[LANGUAGE]}: {txcolors.SELL_LOSS}{str(datetime.now().timestamp() - bot_started_datetime).split(".")[0]}{txcolors.DEFAULT} | {languages_bot.MSG24[LANGUAGE]}: {txcolors.SELL_LOSS}{str(bot_paused)}{txcolors.DEFAULT} | {languages_bot.MSG25[LANGUAGE]}: {txcolors.SELL_LOSS}{TEST_MODE}{txcolors.DEFAULT} | {languages_bot.MSG26[LANGUAGE]}: {txcolors.SELL_LOSS}{BACKTESTING_MODE}{txcolors.DEFAULT}'])        
        my_table.add_row([f'{txcolors.DEFAULT} {languages_bot.MSG27[LANGUAGE]}: {txcolors.SELL_LOSS}{str(round(get_balance_wallet(PAIR_WITH),2))}{txcolors.DEFAULT} | {languages_bot.MSG28[LANGUAGE]}: {txcolors.SELL_LOSS}{str(len(coins_bought))}{txcolors.DEFAULT}/{txcolors.SELL_LOSS}{str(TRADE_SLOTS)} {int(CURRENT_EXPOSURE)}{txcolors.DEFAULT}/{txcolors.SELL_LOSS}{int(INVESTMENT_TOTAL)} {txcolors.DEFAULT}{PAIR_WITH}{txcolors.DEFAULT} | {txcolors.DEFAULT}{languages_bot.MSG29[LANGUAGE]}/{languages_bot.MSG31[LANGUAGE]}: {txcolors.BOT_WINS}{str(trade_wins)}{txcolors.DEFAULT}/{txcolors.BOT_LOSSES}{str(trade_losses)}{txcolors.DEFAULT} | {languages_bot.MSG29[LANGUAGE]} %: {txcolors.SELL_PROFIT if WIN_LOSS_PERCENT > 0. else txcolors.BOT_LOSSES}{float(WIN_LOSS_PERCENT):g}%{txcolors.DEFAULT} | {languages_bot.MSG30[LANGUAGE]}: {txcolors.SELL_LOSS}{trade_wins+trade_losses}{txcolors.DEFAULT}'])
        my_table.add_row([f'{txcolors.DEFAULT}TOTAL: {txcolors.SELL_PROFIT if session_USDT_EARNED > 0. else txcolors.BOT_LOSSES}{str(format(float(session_USDT_EARNED), ".4f"))} {txcolors.DEFAULT}{PAIR_WITH} | {txcolors.DEFAULT}{languages_bot.MSG31[LANGUAGE]}: {txcolors.BOT_LOSSES}{str(format(float(session_USDT_LOSS), ".4f"))}{txcolors.DEFAULT} {PAIR_WITH} | {txcolors.DEFAULT}{languages_bot.MSG32[LANGUAGE]}: {txcolors.SELL_PROFIT}{str(format(float(session_USDT_WON), ".4f"))}{txcolors.DEFAULT} {PAIR_WITH} | {languages_bot.MSG19[LANGUAGE].upper()} %: {txcolors.SELL_PROFIT if (session_USDT_EARNED * 100)/INVESTMENT_TOTAL > 0. else txcolors.BOT_LOSSES}{round((session_USDT_EARNED * 100)/INVESTMENT_TOTAL,3)}%{txcolors.DEFAULT}'])
        print("\n")
        print(my_table)
        my_table = PrettyTable()
        print_table_coins_bought()
        print("\n")
		
        if MSG_DISCORD:
            #improving reporting messages
            msg1 = str(datetime.now()) + "\n"
            msg2 = languages_bot.MSG22[LANGUAGE] + "         : " + datetime.fromtimestamp(bot_started_datetime).strftime("%d/%m/%y %H:%M:%S") + "\n"
            msg2 = msg2 + languages_bot.MSG23[LANGUAGE] + "     : " + str(datetime.now().timestamp() - bot_started_datetime) + "\n"
            msg2 = msg2 + languages_bot.MSG25[LANGUAGE] + "       : " + str(TEST_MODE) + "\n"
            msg2 = msg2 + languages_bot.MSG28[LANGUAGE] + "   : " + str(len(coins_bought)) + "(" + str(float(CURRENT_EXPOSURE)) + PAIR_WITH + ")" + "\n"
            msg2 = msg2 + languages_bot.MSG29[LANGUAGE] + "             : " + str(trade_wins) + "\n"
            msg2 = msg2 + languages_bot.MSG31[LANGUAGE] + "            : " + str(trade_losses) + "\n"
            msg2 = msg2 + languages_bot.MSG33[LANGUAGE] + "         : " + str(round(unrealised_session_profit_incfees_total,3))
            msg2 = msg2 + languages_bot.MSG24[LANGUAGE] + "   : " + str(bot_paused) + "\n"
            msg2 = msg2 + PAIR_WITH + languages_bot.MSG32[LANGUAGE] + "     : " + str(session_USDT_EARNED) + "\n"
            msg2 = msg2 + languages_bot.MSG19[LANGUAGE].upper() + " %:" + str((session_USDT_EARNED * 100)/INVESTMENT_TOTAL) + "\n"
            msg2 = msg2 + "-------------------"
            msg_discord_balance(msg1, msg2)
        
        panic_bot(int(INVESTMENT_TOTAL), trade_losses)
        #show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())
    except Exception as e:
        write_log(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.WARNING}balance_report(): {languages_bot.MSG1[LANGUAGE]}: {e}{txcolors.DEFAULT}')
        write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
        pass
	
    return msg1 + msg2

def prefix_type():
    if TEST_MODE:
        fileprefix = 'test_'
    else:
        fileprefix = 'live_'
    return fileprefix
    
def write_log(logline, show=True, showtime=False, LOGFILE=""):
	try:
		timestamp = datetime.now().strftime("%d/%m/%y %H:%M:%S")
		file_prefix = prefix_type()
		 
		if LOGFILE == "": 
			LOGFILE = LOG_FILE
		with open(file_prefix + LOGFILE,'a') as f:
			ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
			result = ansi_escape.sub('', logline)
			if showtime:
				f.write(timestamp + ' ' + result + '\n')
			else:
				f.write(result + '\n')
		if show:
			print(f'{logline}')
	except Exception as e:
		print(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.WARNING}write_log(): {languages_bot.MSG1[LANGUAGE]}: {e}{txcolors.DEFAULT}')
		print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
		exit(1)
		
def read_log_trades(OrderID):
	try:
		ret = ""
		file_prefix = prefix_type()

		with open(file_prefix + TRADES_LOG_FILE, "r") as fp: 
			csv_readed = csv.reader(fp)
			for row in csv_readed:
				if row[1] == OrderID:
						ret = row[6]
	except Exception as e:
		write_log(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.WARNING}read_log_trades(): {languages_bot.MSG1[LANGUAGE]}: {e}{txcolors.DEFAULT}')
		write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
		pass
	return ret 

def convert_csv_to_html(filecsv):
    try:
        filelines = ""
        headers = ""
        htmlCode1 = ""
        htmlCode2 = ""
        h = []
        if TEST_MODE:
            file_prefix = 'test_'
        else:
            file_prefix = 'live_'
        bot_stats_file_path = file_prefix + BOT_STATS
        if os.path.exists(bot_stats_file_path) and os.path.getsize(bot_stats_file_path) > 2:
            with open(bot_stats_file_path,'r') as f:
                bot_stats = json.load(f)
        with open(file_prefix + filecsv, 'r') as file:
            filelines = file.readlines() 
            headers = filelines[0] 
            headers = headers.split(',')        
            for head in headers:
                h.append(head)
            table = PrettyTable(h)
            table.format = True
            table.border = True
            table.align = "c"
            table.valign = "m"
            table.hrules = 1
            table.vrules = 1
            for i in range(1, len(filelines)) : 
                rowstr = [c.replace(".", ",") for c in filelines[i].split(',')]
                table.add_row(rowstr)
            htmlCode1 = table.get_html_string() 
            table = PrettyTable(h)
            #with open(file_prefix + filecsv.replace("csv","html"), 'a') as final_htmlFile:
                #final_htmlFile.write(htmlCode)
        my_table = PrettyTable()
        my_table.format = True
        my_table.border = True
        my_table.align = "c"
        my_table.valign = "m"
        my_table.field_names = ["total_capital", "botstart_datetime", "tradeWins", "tradeLosses", "session_USDT_EARNED", "session_USDT_LOSS", "session_USDT_WON"]
        my_table.add_row([bot_stats["total_capital"], datetime.fromtimestamp(float(bot_stats["botstart_datetime"])).strftime("%d/%m/%y %H:%M:%S"), bot_stats["tradeWins"], bot_stats["tradeLosses"], bot_stats["session_USDT_EARNED"], bot_stats["session_USDT_LOSS"], bot_stats["session_USDT_WON"]])
        htmlCode2 = my_table.get_html_string() 
        my_table = PrettyTable()
        with open(file_prefix + filecsv.replace("csv","html"), 'w') as final_htmlFile:
            final_htmlFile.write(htmlCode1)
            final_htmlFile.write("\n" + htmlCode2)
    except Exception as e:
        write_log(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.WARNING}convert_csv_to_html(): {languages_bot.MSG1[LANGUAGE]}: {e}{txcolors.DEFAULT}')
        write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
        pass
	
def write_log_trades(logline):
	try:
		#timestamp = datetime.now().strftime("%d/%m/%y %H:%M:%S")
		file_prefix = prefix_type()
		logline = str(logline).replace("'","").replace("[","").replace("]","")
		with open(file_prefix + TRADES_LOG_FILE,'a') as f:
			file_stats = os.stat(file_prefix + TRADES_LOG_FILE)
			if file_stats.st_size == 0:
				HEADER = ["Datetime", "OrderID", "Type", "Coin", "Volume", "Buy Price", "Amount of Buy" + " " + PAIR_WITH, "Sell Price", "Amount of Sell" + " " + PAIR_WITH, "Sell Reason", "Profit $" + " " + PAIR_WITH] #, "Total" + " " + PAIR_WITH]
				f.write(str(HEADER).replace("'","").replace("[","").replace("]","") + '\n')
			f.write(str(logline) + '\n')
	except Exception as e:
		write_log(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.WARNING}write_log_trades(): {languages_bot.MSG1[LANGUAGE]}: {e}{txcolors.DEFAULT}')
		write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
		pass
		
def get_balance_test_mode(total=False):
	try:
		value1 = 0.0
		value2 = 0.0
		file_prefix = prefix_type()
		bot_stats_file_path = file_prefix + BOT_STATS
		if os.path.exists(bot_stats_file_path) and os.path.getsize(bot_stats_file_path) > 2:
			with open(bot_stats_file_path,'r') as f:
				bot_stats = json.load(f)
			#value1 = float(bot_stats['total_capital'])
			value2 = float(bot_stats['session_USDT_EARNED'])

		if total:
			value1 = TRADE_TOTAL + value2
		else:
			value1 = TRADE_TOTAL
		#show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())
	except Exception as e:
		write_log(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.WARNING}get_balance_test_mode(): {languages_bot.MSG1[LANGUAGE]}: {e}{txcolors.DEFAULT}')
		write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
   
	return float(value1)
			
def msg_discord_balance(msg1, msg2):
	global last_msg_discord_balance_date, discord_msg_balance_data, last_msg_discord_balance_date
	time_between_insertion = datetime.now() - last_msg_discord_balance_date
	# only put the balance message to discord once every 60 seconds and if the balance information has changed since last times
	# message sending time was increased to 2 minutes for more convenience
	if time_between_insertion.seconds > 300:
		if msg2 != discord_msg_balance_data:
			msg_discord(msg1 + msg2)
			discord_msg_balance_data = msg2
		else:
			# ping msg to know the bot is still running
			msg_discord(".")
		#the variable is initialized so that sending messages every 2 minutes can work
		last_msg_discord_balance_date = datetime.now()

def msg_discord(msg):
	message = msg + '\n\n'
	##show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())
	if MSG_DISCORD:
		#Webhook of my channel. Click on edit channel --> Webhooks --> Creates webhook
		mUrl = "https://discordapp.com/api/webhooks/"+DISCORD_WEBHOOK
		data = {"content": message}
		response = requests.post(mUrl, json=data)
		#BB
		# print(response.content)

def panic_bot(invest, lost):
	if PANIC_STOP != 0:
		lost_percent = (lost*invest)/100
		print(f'invest= {invest} lost= {lost} lost_percent= {lost_percent}')
		if lost_percent >= PANIC_STOP and PANIC_STOP != 0:
			printf(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.WARNING}PANIC_STOP activated.{txcolors.DEFAULT}')
			stop_signal_threads()
			printf(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.WARNING}The percentage of losses is greater than or equal to the established one. Bot Stopped.{txcolors.DEFAULT}')
			exit(1)

def chek_files_paused():
	files = []
	folder = "signals"
	files = [item for sublist in [glob.glob(folder + ext) for ext in ["/*.pause", "/*.exc"]] for item in sublist]
	PAUSEBOT1 = False
	for filename in files:
		if os.path.exists(filename):
			PAUSEBOT1 = True
			break
		else:
			PAUSEBOT1 = False
	return PAUSEBOT1
	
def pause_bot():
    try:
        '''Pause the script when external indicators detect a bearish trend in the market'''
        global bot_paused, session_profit_incfees_perc, hsp_head, session_profit_incfees_total, PAUSEBOT_MANUAL
        PAUSEBOT = False
		# start counting for how long the bot has been paused
        start_time = time.perf_counter()
		#coins_sold = {}

        while chek_files_paused() or PAUSEBOT_MANUAL or BUY_PAUSED: #os.path.exists("signals/pausebot.pause") or PAUSE{languages_bot.MSG5[LANGUAGE]}_MANUAL:
			# do NOT accept any external signals to buy while in pausebot mode
            remove_external_signals('buy')

            if bot_paused == False:
                if PAUSEBOT_MANUAL:
                    print(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.WARNING}Purchase paused manually, stop loss and take profit will continue to work...{txcolors.DEFAULT}')
                    msg = str(datetime.now()) + ' | PAUSE{languages_bot.MSG5[LANGUAGE]}.Purchase paused manually, stop loss and take profit will continue to work...'
                else:
                    print(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.WARNING}Buying paused due to negative market conditions, stop loss and take profit will continue to work...{txcolors.DEFAULT}')
                    msg = str(datetime.now()) + ' | PAUSE{languages_bot.MSG5[LANGUAGE]}. Buying paused due to negative market conditions, stop loss and take profit will continue to work.'
                msg_discord(msg)

                bot_paused = True

			# Sell function needs to work even while paused
            coins_sold = {}
            coins_sold = sell_coins()
            remove_from_portfolio(coins_sold)
            last_price = get_price(True) #pause_bot
            print("pause_bot: last_price= ", last_price)
            
			# pausing here
            if hsp_head == 1: 
				# if not SCREEN_MODE == 2: print(f'Paused...Session profit: {session_profit_incfees_perc:.2f}% Est: ${session_profit_incfees_total:.{decimals()}f} {PAIR_WITH}')
                balance_report(last_price) 
            time.sleep((TIME_DIFFERENCE * 10) / RECHECK_INTERVAL) #wait for pause_bot
			
        else:
			# stop counting the pause time
            stop_time = time.perf_counter()
            time_elapsed = timedelta(seconds=int(stop_time-start_time))

			# resume the bot and ser pause_bot to False
            if bot_paused == True:
                print(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.WARNING}Resuming buying due to positive market conditions, total sleep time: {time_elapsed}{txcolors.DEFAULT}')
                msg = str(datetime.now()) + ' | PAUSE{languages_bot.MSG5[LANGUAGE]}. Resuming buying due to positive market conditions, total sleep time: ' + str(time_elapsed)
                msg_discord(msg)
                bot_paused = False
        #show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())
    except Exception as e:
        write_log(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.WARNING}pause_bot: {languages_bot.MSG1[LANGUAGE]}: {e}{txcolors.DEFAULT}')
        write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
        pass
    return
	
def set_config(data, value):
	##show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())
	file_name = "config.yml"
	parsed_config = load_config(file_name)
	with open(file_name, 'r') as file:
		items = file.readlines()
	c = 0
	for line in items:
		c = c + 1
		if data in line:
			break
	items[c-1] = "  " + data + ": " + str(value) + "\n"
	with open(file_name, 'w') as f:
		f.writelines(items)

def set_exparis(pairs):
	##show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())
	file_name = "config.yml"
	parsed_config = load_config(file_name)
	with open(file_name, 'r') as file:
		data = file.readlines()
	c = 0
	for line in data:
		c = c + 1
		if "EX_PAIRS: [" in line:
			break
	#EX_PAIRS = parsed_config['trading_options']['EX_PAIRS']
	e = False
	pairs = pairs.strip().replace('USDT','')
	for coin in EX_PAIRS:
		if coin == pairs: 
			e = True
			break
		else:
			e = False
	if e == False:
		print(f'The exception has been saved in EX_PAIR in the configuration file...{txcolors.DEFAULT}')
		EX_PAIRS.append(pairs)
		data[c-1] = "  EX_PAIRS: " + str(EX_PAIRS) + "\n"
		with open(file_name, 'w') as f:
			f.writelines(data)

def buy_external_signals():
	external_list = {}
	#signals = {}

	# check directory and load pairs from files into external_list
	files = []
	folder = "signals"
	files = [item for sublist in [glob.glob(folder + ext) for ext in ["/*.buy", "/*.exs"]] for item in sublist]

	#signals = glob.glob(mask)  #"signals/*.buy")
	#print("signals: ", signals)
	for filename in files: #signals:
		for line in open(filename):
			symbol = line.strip()
			if symbol.replace(PAIR_WITH, "") not in EX_PAIRS:
				external_list[symbol] = symbol
		try:
			os.remove(filename)
		except:
			if DEBUG: print(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.WARNING}Could not remove external signalling file{txcolors.DEFAULT}')
	#show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())
	return external_list

def random_without_repeating():
	##show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())
	if TEST_MODE:
		file_prefix = 'test_'
	else:
		file_prefix = 'live_'
	# if CREATE_BUY_SELL_FILES:
		# if megatronmod.CREATE_BUY_SELL_FILES:
			# if os.path.exists(file_prefix+'megatronmod.buy'):
				# with open(file_prefix+'megatronmod.buy', newline='') as csvfile1:
					# list1 = list(csv.reader(csvfile1, delimiter=',')) 
					# RandOrderId = int(list1[-1][0].replace("OrderID:", "")) + 1
			# else:
				# RandOrderId = 1000
		# else:
			# RandOrderId = randint(1000, 9999)
	# else:
	RandOrderId = randint(1000, 9999)
		
	return RandOrderId

#use function of the OlorinSledge
def wait_for_price():
    try:
        '''calls the initial price and ensures the correct amount of time has passed before reading the current price again'''

        global historical_prices, hsp_head, coins_up,coins_down,coins_unchanged, TRADE_TOTAL, USE_VOLATILE_METOD
		
        volatile_coins = {}
        externals1 = []
        externals2 = []
        coins_up = 0
        coins_down = 0
        coins_unchanged = 0	
        pause_bot()        
        #last_price = get_price() #wait_for_price

        if USE_SIGNALLING_MODULES:
            # Here goes new code for external signalling
            externals = buy_external_signals()
            last_price = get_price(False)
        else:
            coins1 = []
            last_price = 0
            coins1 = []
            TICKERS = ''
            if USE_MOST_VOLUME_COINS == True:
                TICKERS = 'volatile_volume_' + str(date.today()) + '.txt'
            else:
                TICKERS = 'tickers.txt'            
            for line in open(TICKERS):
                pairs=[line.strip() + PAIR_WITH for line in open(TICKERS)] 
            for pair in pairs:
                coins1.append(pair)
            #print("wait_for_price: externals1")
            externals1, externals2 = megatronmod.analyze(c_data, coins1, True)#, 0)
            last_price = get_price(False, externals1)
        
        exnumber = 0
        for excoin1 in externals1:
            excoin = excoin1['symbol']
            if excoin not in volatile_coins and excoin not in coins_bought and (len(coins_bought) + len(volatile_coins)) < TRADE_SLOTS:
                #(len(coins_bought) + exnumber + len(volatile_coins)) < TRADE_SLOTS:
                volatile_coins[excoin] = 1
                exnumber +=1               
                print(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}External signal received on {excoin}, purchasing ${TRADE_TOTAL} {PAIR_WITH} value of {excoin}!{txcolors.DEFAULT}')

        balance_report(last_price)
        #show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())
    except Exception as e:
        write_log(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.WARNING}wait_for_price(): {languages_bot.MSG1[LANGUAGE]}: {e}{txcolors.DEFAULT}')
        write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
        lost_connection(e, "wait_for_price")        
        pass
    return volatile_coins, len(volatile_coins), last_price #historical_prices[hsp_head]

def get_symbol_info(coin1):
    ret = {}
    if coin1 == "BTCUSDT" and BACKTESTING_MODE:
        ret = {'symbol': 'BTCUSDT', 'status': 'TRADING', 'baseAsset': 'BTC', 'baseAssetPrecision': 8, 'quoteAsset': 'USDT', 'quotePrecision': 8, 'quoteAssetPrecision': 8, 'baseCommissionPrecision': 8, 'quoteCommissionPrecision': 8, 'orderTypes': ['LIMIT', 'LIMIT_MAKER', 'MARKET', 'STOP_LOSS_LIMIT', 'TAKE_PROFIT_LIMIT'], 'icebergAllowed': True, 'ocoAllowed': True, 'quoteOrderQtyMarketAllowed': True, 'allowTrailingStop': True, 'cancelReplaceAllowed': True, 'isSpotTradingAllowed': True, 'isMarginTradingAllowed': True, 'filters': [{'filterType': 'PRICE_FILTER', 'minPrice': '0.01000000', 'maxPrice': '1000000.00000000', 'tickSize': '0.01000000'}, {'filterType': 'LOT_SIZE', 'minQty': '0.00001000', 'maxQty': '9000.00000000', 'stepSize': '0.00001000'}, {'filterType': 'ICEBERG_PARTS', 'limit': 10}, {'filterType': 'MARKET_LOT_SIZE', 'minQty': '0.00000000', 'maxQty': '149.41382295', 'stepSize': '0.00000000'}, {'filterType': 'TRAILING_DELTA', 'minTrailingAboveDelta': 10, 'maxTrailingAboveDelta': 2000, 'minTrailingBelowDelta': 10, 'maxTrailingBelowDelta': 2000}, {'filterType': 'PERCENT_PRICE_BY_SIDE', 'bidMultiplierUp': '5', 'bidMultiplierDown': '0.2', 'askMultiplierUp': '5', 'askMultiplierDown': '0.2', 'avgPriceMins': 5}, {'filterType': 'NOTIONAL', 'minNotional': '10.00000000', 'applyMinToMarket': True, 'maxNotional': '9000000.00000000', 'applyMaxToMarket': False, 'avgPriceMins': 5}, {'filterType': 'MAX_NUM_ORDERS', 'maxNumOrders': 200}, {'filterType': 'MAX_NUM_ALGO_ORDERS', 'maxNumAlgoOrders': 5}], 'permissions': ['SPOT', 'MARGIN', 'TRD_GRP_004', 'TRD_GRP_005', 'TRD_GRP_006'], 'defaultSelfTradePreventionMode': 'NONE', 'allowedSelfTradePreventionModes': ['NONE', 'EXPIRE_TAKER', 'EXPIRE_MAKER', 'EXPIRE_{languages_bot.MSG5[LANGUAGE]}H']}
    if not BACKTESTING_MODE:
        ret = client.get_symbol_info(coin1)
    return ret
    
def convert_volume():
    try:
        '''Converts the volume given in TRADE_TOTAL from "USDT"(or coin selected) to the each coin's volume'''
        volatile_coins, number_of_coins, last_price = wait_for_price()
        
        #print("convert_volume: last_price", last_price, datetime.now())
        
        global TRADE_TOTAL, session_USDT_EARNED
        lot_size = {}
        volume = {}
        for coin in volatile_coins:

			# Find the correct step size for each coin
			# max accuracy for BTC for example is 6 decimal points
			# while XRP is only 1
			#try:
            info = get_symbol_info(coin)
            
            #print(info)

			#step_size = info['filterType'][1]['stepSize']
			#step_size = float(info['filters'][2]['stepSize'])
			#lot_size[coin] = step_size.index('1') - 1
			
            for filt in info['filters']:
                if filt['filterType'] == 'LOT_SIZE':
                    lot_size[coin] = filt['stepSize'].find('1') - 1
					#print("volume[coin]",volume[coin],"lot_size[coin]", lot_size[coin], "type", type(lot_size[coin]))
                    break
					
            if lot_size[coin] < 0: lot_size[coin] = 0

			# calculate the volume in coin from TRADE_TOTAL in PAIR_WITH (default)
				
            if COMPOUND_INTEREST and TRADE_SLOTS == 1:
                if TEST_MODE: 
                    TRADE_TOTAL = get_balance_test_mode(True) #convert_volume
                else:
                    TRADE_TOTAL = get_balance_wallet(PAIR_WITH) #convert_volume

            volume[coin] = float(TRADE_TOTAL / float(last_price[coin]['price']))
            if TEST_MODE: 
                TRADE_TOTAL = get_balance_test_mode() #convert_volume
			#print("volume[coin]: ", volume[coin], "TRADE_TOTAL: ", TRADE_TOTAL, "float(last_price[coin]['price']): ", float(last_price[coin]['price']))

				# define the volume with the correct step size
            if coin not in lot_size:
					# original code: volume[coin] = float('{:.1f}'.format(volume[coin]))
				#volume[coin] = int(volume[coin])
                volume[coin] = float(volume[coin])
            else:
					# if lot size has 0 decimal points, make the volume an integer
                if lot_size[coin] == 0:
                    volume[coin] = float(volume[coin])
                else:
                    volume[coin] = truncate(volume[coin], lot_size[coin])
        #show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())
    except Exception as e:
        write_log(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.WARNING}convert_volume() exception: {e}{txcolors.DEFAULT}')
        write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
        lost_connection(e, "convert_volume")        
        pass
	#except KeyboardInterrupt as ki:
		#pass
    return volume, last_price

def buy():
    try:
        '''Place Buy market orders for each volatile coin found'''        
        volume, last_price = convert_volume() #buy
        orders = {}
		#global USED_BNB_IN_SESSION
        for coin in volume:
            if coin not in coins_bought and coin.replace(PAIR_WITH,'') not in EX_PAIRS:
				#if not SCREEN_MODE == 2: print(f"{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.BUY}Preparing to buy {volume[coin]} of {coin} @ ${last_price[coin]['price']}{txcolors.DEFAULT}")
                coins = {}
                coins[coin] = coin + PAIR_WITH
				#msg1 = str(datetime.now()) + ' | BUY: ' + coin + '. V:' +  str(volume[coin]) + ' P$:' + str(last_price[coin]['price']) + ' ' + PAIR_WITH + ' invested:' + str(float(volume[coin])*float(last_price[coin]['price']))
				#msg_discord(msg1)
                if TEST_MODE: 
                    RandOrderId = random_without_repeating()
                    orders[coin] = [{
                        'symbol': coin,
                        'orderId': RandOrderId, #0,
                        'time': datetime.now().timestamp()
                    }]

                    BuyUSDT = str(float(volume[coin]) * float(last_price[coin]['price'])).zfill(9)
                    volumeBuy = volume[coin] #format(volume[coin], '.6f')
                    last_price_buy = last_price[coin]['price']
                    #coin = '{0:<9}'.format(coin)
													#"Datetime", "OrderID", "Type", "Coin", "Volume", "Buy Price", "Amount of Buy", "Sell Price", "Amount of Sell", "Sell Reason", "Profit $")
                    if BACKTESTING_MODE:
                        write_log_trades([datetime.fromtimestamp(last_price[coin]['time']/1000).strftime("%d/%m/%y %H:%M:%S"), RandOrderId, "Buy", coin.replace(PAIR_WITH,""), round(float(volumeBuy),8), str(round(float(last_price_buy),8)), str(round(float(BuyUSDT),8)), 0, 0, "-", 0])                
                    else:
                        write_log_trades([datetime.now().strftime("%d/%m/%y %H:%M:%S"), RandOrderId, "Buy", coin.replace(PAIR_WITH,""), round(float(volumeBuy),8), str(round(float(last_price_buy),8)), str(round(float(BuyUSDT),8)), 0, 0, "-", 0])                
                    
                    if USE_SIGNALLING_MODULES:
                        write_signallsell(coin.removesuffix(PAIR_WITH))
					#write_log(str(datetime.now()) + " BUY: " + coin, False)
                    continue

			# try to create a real order if the test orders did not raise an exception
                try:
                    order_details = client.create_order(
                        symbol = coin,
                        side = 'BUY',
                        type = 'MARKET',
                        quantity = volume[coin]
                    )

			# error handling here in case position cannot be placed
                except Exception as e:
                    write_log(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.WARNING} buy(): In create_order exception({coin}): {e}{txcolors.DEFAULT}')
                    write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
                    pass

			# run the else block if the position has been placed and return order info
                else:
                    orders[coin] = client.get_all_orders(symbol=coin, limit=1)

				# binance sometimes returns an empty list, the code will wait here until binance returns the order
                    while orders[coin] == []:
                        write_log(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT} Binance is being slow in returning the order, calling the API again...{txcolors.DEFAULT}')
                        orders[coin] = client.get_all_orders(symbol=coin, limit=1)
                        time.sleep(1) #wait for buy

                    else:
                        print(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}Order returned, saving order to file')
                        if not TEST_MODE: #or not BACKTESTING_MODE:
                            orders[coin] = extract_order_data(order_details)
							#adding the price in USDT
                            BuyUSDT = str(orders[coin]['volume'] * orders[coin]['avgPrice']) #format(orders[coin]['volume'] * orders[coin]['avgPrice'], '.14f')).zfill(4)
                            volumeBuy = float(volume[coin]) #float(format(float(volume[coin]), '.6f'))
                            last_price_buy = orders[coin]['avgPrice'] #float(format(orders[coin]['avgPrice'], '.3f'))
							#write_log(f'last_price= {float(last_price[coin]["price"])}')
                            last_price[coin]["price"] = float(orders[coin]['avgPrice'])
							#BuyUSDT = format(BuyUSDT, '.14f')
							#improving the presentation of the log file
                            #coin = '{0:<9}'.format(coin)
							#buyFeeTotal1 = (volumeBuy * last_price_buy) * float(TRADING_FEE/100)
							#USED_BNB_IN_SESSION = USED_BNB_IN_SESSION + orders[coin]['tradeFeeBNB'] #buyFeeTotal1
									 #["Datetime",                                 "Type", "Coin", "Volume",              "Buy Price", "Amount of Buy", "Sell Price", "Amount of Sell", "Sell Reason", "Profit $"] "USDTdiff"])
                            if BACKTESTING_MODE:
                                write_log_trades([datetime.fromtimestamp(last_price[coin]['time']/1000).strftime("%d/%m/%y %H:%M:%S"), str(orders[coin]['orderId']), "Buy", coin.replace(PAIR_WITH,""), str(round(float(volumeBuy),8)), str(round(float(last_price_buy),8)), str(round(float(BuyUSDT),8)) , "0", "0", "-", "0"])
                            else:
                                write_log_trades([datetime.now().strftime("%d/%m/%y %H:%M:%S"), str(orders[coin]['orderId']), "Buy", coin.replace(PAIR_WITH,""), str(round(float(volumeBuy),8)), str(round(float(last_price_buy),8)), str(round(float(BuyUSDT),8)) , "0", "0", "-", "0"])
			
                        else:
							#adding the price in USDT
                            BuyUSDT = volume[coin] * last_price[coin]['price']
                            volumeBuy = volume[coin] #format(float(volume[coin]), '.6f')
                            last_price_buy = float(last_price[coin]['price']) #format(float(last_price[coin]['price']), '.3f')
							#BuyUSDT = str(format(BuyUSDT, '.14f')).zfill(4)
                            last_price[coin]["price"] = float(orders[coin]['avgPrice'])
							#improving the presentation of the log file
                            coin = '{0:<9}'.format(coin)
                            buyFeeTotal1 = (volumeBuy * last_price_buy) * float(TRADING_FEE/100)
							#USED_BNB_IN_SESSION = USED_BNB_IN_SESSION + buyFeeTotal1
									#(["Datetime", "Type", "Coin", "Volume", "Buy Price", "Sell Price", "Sell Reason", "Profit $"]) "USDTdiff"])
                            if BACKTESTING_MODE:
                                write_log_trades([datetime.fromtimestamp(last_price[coin]['time']/1000).strftime("%d/%m/%y %H:%M:%S"), str(RandOrderId),"Buy", coin.replace(PAIR_WITH,""), str(round(float(volumeBuy),8)), str(round(float(last_price[coin]['price']),8)), str(round(float(BuyUSDT),8)), "0", "0", "-", "0"])
                            else:
                                write_log_trades([datetime.now().strftime("%d/%m/%y %H:%M:%S"), str(RandOrderId),"Buy", coin.replace(PAIR_WITH,""), str(round(float(volumeBuy),8)), str(round(float(last_price[coin]['price']),8)), str(round(float(BuyUSDT),8)), "0", "0", "-", "0"])
                        write_signallsell(coin)
            else:
                print(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}Signal detected, but there is already an active trade on {coin}{txcolors.DEFAULT}')
        #show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())
    except Exception as e:
        write_log(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.WARNING} buy(): {languages_bot.MSG1[LANGUAGE]}: {e}{txcolors.DEFAULT}')
        write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
        lost_connection(e, "buy")
        pass
    return orders, last_price, volume


def sell_coins(tpsl_override = False, specific_coin_to_sell = ""):
    try:
        '''sell coins that have reached the STOP LOSS or TAKE PROFIT threshold'''
        global hsp_head, session_profit_incfees_perc, session_profit_incfees_total, coin_order_id, trade_wins, trade_losses, historic_profit_incfees_perc, historic_profit_incfees_total, sell_all_coins, session_USDT_EARNED, TUP, TDOWN, TNEUTRAL, USED_BNB_IN_SESSION, TRADE_TOTAL, sell_specific_coin, session_USDT_LOSS, session_USDT_WON, session_USDT_EARNED
			   
        OrderID = ""

		#last_price = get_price(add_to_historical=True)
        coins_sold = {}
        if len(coins_bought) > 0:
            externals = sell_external_signals()
            #print("externals: ", externals #[{'time': 0, 'symbol': 'BTCUSDT', 'price': 28678.99}]
            last_price = get_price(False, externals) #sell_coins 
            #print("sell_coins: last_price= ", last_price, "coins_bought: ", coins_bought, datetime.now())        
            
            BUDGET = TRADE_TOTAL * TRADE_SLOTS
        
            for coin in list(coins_bought):
            
                if sell_specific_coin and not specific_coin_to_sell == coin: continue
                    
                LastPrice = float(last_price[coin]['price'])
                sellFee = (LastPrice * (TRADING_FEE/100))
                sellFeeTotal = (coins_bought[coin]['volume'] * LastPrice) * (TRADING_FEE/100)
                LastPriceLessFees = (LastPrice - sellFee)
                LastPricePlusFees = (LastPrice + sellFee)
                
                BuyPrice = float(coins_bought[coin]['bought_at'])
                buyFee = (BuyPrice * (TRADING_FEE/100))
                buyFeeTotal = (coins_bought[coin]['volume'] * BuyPrice) * (TRADING_FEE/100)
                BuyPricePlusFees = (BuyPrice + buyFee)
                
                ProfitAfterFees = LastPriceLessFees - BuyPricePlusFees
                #ProfitAfterFees = (LastPricePlusFees - BuyPricePlusFees)
                
                PriceChange_Perc = float((LastPrice - BuyPrice) / BuyPrice * 100)
                #PriceChangeIncFees_Perc = float(((LastPrice+sellFee) - (BuyPrice+buyFee)) / (BuyPrice+buyFee) * 100)
                #PriceChangeIncFees_Unit = float((LastPrice+sellFee) - (BuyPrice+buyFee))
                PriceChangeIncFees_Perc = float(((LastPrice - sellFee) - (BuyPrice + buyFee)) / (BuyPrice + buyFee) * 100)
                PriceChangeIncFees_Unit = float((LastPrice - sellFee) - (BuyPrice + buyFee))

                # define stop loss and take profit
                TP = float(coins_bought[coin]['bought_at']) + ((float(coins_bought[coin]['bought_at']) * coins_bought[coin]['take_profit']) / 100)
                SL = float(coins_bought[coin]['bought_at']) + ((float(coins_bought[coin]['bought_at']) * coins_bought[coin]['stop_loss']) / 100)
                
                # check that the price is above the take profit and readjust SL and TP accordingly if trialing stop loss used
                
                if LastPrice > TP and USE_TRAILING_STOP_LOSS and not sell_all_coins and not tpsl_override and not sell_specific_coin:
                    # increasing TP by TRAILING_TAKE_PROFIT (essentially next time to readjust SL)
                    #add metod from OlorinSledge
                    #if PriceChange_Perc >= 0.8:
                        # price has changed by 0.8% or greater, a big change. Make the STOP LOSS trail closely to the TAKE PROFIT
                        # so you don't lose this increase in price if it falls back
                        #coins_bought[coin]['take_profit'] = PriceChange_Perc + TRAILING_TAKE_PROFIT    
                        #coins_bought[coin]['stop_loss'] = coins_bought[coin]['take_profit'] - TRAILING_STOP_LOSS

                    #else:
                        # price has changed by less than 0.8%, a small change. Make the STOP LOSS trail loosely to the TAKE PROFIT
                        # so you don't get stopped out of the trade prematurely
                    coins_bought[coin]['stop_loss'] = coins_bought[coin]['take_profit'] - TRAILING_STOP_LOSS
                    coins_bought[coin]['take_profit'] = PriceChange_Perc + TRAILING_TAKE_PROFIT

                    # we've got a negative stop loss - not good, we don't want this.
                    #if coins_bought[coin]['stop_loss'] <= 0:
                        #coins_bought[coin]['stop_loss'] = coins_bought[coin]['take_profit'] * .25

                    # supress old metod
                    #coins_bought[coin]['stop_loss'] = coins_bought[coin]['take_profit'] - TRAILING_STOP_LOSS
                    #coins_bought[coin]['take_profit'] = PriceChange_Perc + TRAILING_TAKE_PROFIT
                    # if DEBUG: print(f"{coin} TP reached, adjusting TP {coins_bought[coin]['take_profit']:.2f}  and SL {coins_bought[coin]['stop_loss']:.2f} accordingly to lock-in profit")
                    #if DEBUG: print(f"{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}{coin} TP reached, adjusting TP {coins_bought[coin]['take_profit']:.{decimals()}f} and SL {coins_bought[coin]['stop_loss']:.{decimals()}f} accordingly to lock-in profit")
                    #if DEBUG: print(f"{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}{coin} TP reached, adjusting TP {str(round(TP,2))} and SL {str(round(SL,2))} accordingly to lock-in profit")
                    continue
                # check that the price is below the stop loss or above take profit (if trailing stop loss not used) and sell if this is the case
                sellCoin = False
                sell_reason = ""
                if SELL_ON_SIGNAL_ONLY:
                    # only sell if told to by external signal
                    for extcoin in externals:
                        print("SELL_ON_SIGNAL_ONLY: ", extcoin['symbol'], coin, datetime.now())
                        if extcoin['symbol'] == coin:
                        #if coin in externals:
                            sellCoin = True
                            sell_reason = 'External Sell Signal'
                            break
                else:
                    if LastPrice < SL: 
                        sellCoin = True
                        if USE_TRAILING_STOP_LOSS:
                            if PriceChange_Perc >= 0:
                                sell_reason = "TTP " #+ str(SL) + " reached"
                            else:
                                sell_reason = "TSL " #+ str(SL) + " reached"
                        else:
                            sell_reason = "SL "  #+ str(SL) + " reached"  
                        sell_reason = sell_reason + str(format(SL, ".18f")) + " reached"
                        #sell_reason = sell_reason + str(round(SL,2)) + " reached"
                    if LastPrice > TP:
                        sellCoin = True
                        #sell_reason = "TP " + str(format(SL, ".18f")) + " reached"
                        sell_reason = "TP " + str(round(TP,2)) + " reached"
                    if coin in externals:
                        sellCoin = True
                        sell_reason = 'External Sell Signal'
                
                if sell_all_coins:
                    sellCoin = True
                    sell_reason = 'Sell All Coins'
                if sell_specific_coin:
                    sellCoin = True
                    sell_reason = 'Sell Specific Coin'    
                if tpsl_override:
                    sellCoin = True
                    sell_reason = 'Session TPSL Override reached'

                if sellCoin:
                    print(f"{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.SELL_PROFIT if PriceChangeIncFees_Perc >= 0. else txcolors.SELL_LOSS}Sell: {coins_bought[coin]['volume']} of {coin} | {sell_reason} | ${float(LastPrice):g} - ${float(BuyPrice):g}{txcolors.DEFAULT}")
                    print(f"{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.SELL_PROFIT if PriceChangeIncFees_Perc >= 0. else txcolors.SELL_LOSS}Profit: {PriceChangeIncFees_Perc:.2f}% Est: {((float(coins_bought[coin]['volume'])*float(coins_bought[coin]['bought_at']))*PriceChangeIncFees_Perc)/100:.{decimals()}f} {PAIR_WITH} (Inc Fees) {PAIR_WITH} earned: {(float(coins_bought[coin]['volume'])*float(coins_bought[coin]['bought_at']))}{txcolors.DEFAULT}")
                    #msg1 = str(datetime.now()) + '| SELL: ' + coin + '. R:' +  sell_reason + ' P%:' + str(round(PriceChangeIncFees_Perc,2)) + ' P$:' + str(round(((float(coins_bought[coin]['volume'])*float(coins_bought[coin]['bought_at']))*PriceChangeIncFees_Perc)/100,4)) + ' ' + PAIR_WITH + ' earned:' + str(float(coins_bought[coin]['volume'])*float(coins_bought[coin]['bought_at']))
                    #msg_discord(msg1)

                    # try to create a real order          
                    try:
                        if not TEST_MODE: #or not BACKTESTING_MODE:
                            #lot_size = coins_bought[coin]['step_size']
                            #if lot_size == 0:
                            #    lot_size = 1
                            #lot_size = lot_size.index('1') - 1
                            #if lot_size < 0:
                            #    lot_size = 0
                            
                            order_details = client.create_order(
                                symbol = coin,
                                side = 'SELL',
                                type = 'MARKET',
                                quantity = coins_bought[coin]['volume']
                            )

                    # error handling here in case position cannot be placed
                    except Exception as e:
                        #if repr(e).upper() == "APIERROR(CODE=-1111): PRECISION IS OVER THE MAXIMUM DEFINED FOR THIS ASSET.":
                        write_log(f"{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}sell_coins(): Exception occured on selling the coin, Coin: {coin}\nSell Volume coins_bought: {coins_bought[coin]['volume']}\nPrice:{LastPrice}\nException: {e}{txcolors.DEFAULT}")
                        write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
                        pass
                    # run the else block if coin has been sold and create a dict for each coin sold
                    else:
                        if not TEST_MODE: #or not BACKTESTING_MODE:
                            coins_sold[coin] = extract_order_data(order_details)
                            LastPrice = coins_sold[coin]['avgPrice']
                            sellFee = coins_sold[coin]['tradeFeeUnit']
                            coins_sold[coin]['orderid'] = coins_bought[coin]['orderid']
                            priceChange = float((LastPrice - BuyPrice) / BuyPrice * 100)
                            # update this from the actual Binance sale information
                            PriceChangeIncFees_Unit = float((LastPrice+sellFee) - (BuyPrice+buyFee))
                        else:     
                            coins_sold[coin] = coins_bought[coin]
                            coins = {}
                            coins[coin] = coin + PAIR_WITH						
                            OrderID = coins_bought[coin]['orderid']
                        
                        time_held = (timedelta(seconds=datetime.now().timestamp()-int(str(coins_bought[coin]['timestamp'])[:10])).total_seconds())/3600
                        
                        if int(MAX_HOLDING_TIME) != 0: 
                            if time_held >= int(MAX_HOLDING_TIME): set_exparis(coin)

                        print(f"{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}sell_coins() | Coin: {coin} | Sell Volume: {coins_bought[coin]['volume']} | Price:{LastPrice}")
                        
                        # Log trade
                        #BB profit = ((LastPrice - BuyPrice) * coins_sold[coin]['volume']) * (1-(buyFee + sellFeeTotal))  
                        profit_incfees_total = coins_sold[coin]['volume'] * PriceChangeIncFees_Unit
                        #write_log_trades(f"Sell: {coins_sold[coin]['volume']} {coin} - {BuyPrice} - {LastPrice} Profit: {profit_incfees_total:.{decimals()}f} {PAIR_WITH} ({PriceChange_Perc:.2f}%)")
                        #SellUSDT = coins_sold[coin]['volume'] * (LastPrice - sellFee)
                        
                        if IGNORE_FEE:
                            SellUSDT = coins_sold[coin]['volume'] * (LastPrice)
                            USDTdiff = SellUSDT - (BuyPrice * coins_sold[coin]['volume'])
                        else:
                            SellUSDT = coins_sold[coin]['volume'] * (LastPrice - sellFee)
                            USDTdiff = SellUSDT - ((BuyPrice + buyFee) * coins_sold[coin]['volume'])
                                
                        session_USDT_EARNED = session_USDT_EARNED + USDTdiff
                        if USDTdiff < 0:
                            session_USDT_LOSS = session_USDT_LOSS + USDTdiff
                        if USDTdiff >= 0:
                            session_USDT_WON = session_USDT_WON + USDTdiff
                        #improving the presentation of the log file
                        # it was padded with trailing zeros to give order to the table in the log file
                        VolumeSell = format(float(coins_sold[coin]['volume']), '.6f')
                        BuyPriceCoin = format(BuyPrice, '.8f')
                        SellUSDT = str(format(SellUSDT, '.14f')).zfill(4)
                        #coin = '{0:<9}'.format(coin)
                        #BuyUSDT = (BuyPrice * coins_sold[coin]['volume']) 
                        #last_price[coin]['price']
                                        #["Datetime",                                              "OrderID",            "Type",          "Coin",                        "Volume",                  "Buy Price",      "Amount of Buy", "Sell Price",    "Amount of Sell",                            "Sell Reason",          "Profit $"] "USDTdiff"])
                        if BACKTESTING_MODE:
                            write_log_trades([datetime.fromtimestamp(last_price[coin]['time']/1000).strftime("%d/%m/%y %H:%M:%S"), str(OrderID), "Sell", coin.replace(PAIR_WITH, ""), str(round(float(VolumeSell),8)), str(round(float(BuyPrice),8)), read_log_trades(str(OrderID)), str(round(float(LastPrice),8)), str(round(float(SellUSDT),8)), sell_reason, str(round(float(USDTdiff),8))])
                        else:
                            write_log_trades([datetime.now().strftime("%d/%m/%y %H:%M:%S"), str(OrderID), "Sell", coin.replace(PAIR_WITH, ""), str(round(float(VolumeSell),8)), str(round(float(BuyPrice),8)), read_log_trades(str(OrderID)), str(round(float(LastPrice),8)), str(round(float(SellUSDT),8)), sell_reason, str(round(float(USDTdiff),8))])
                        #if reinvest_mode:
                        #    TRADE_TOTAL += (profit_incfees_total / TRADE_SLOTS)
                        
                        #this is good
                        session_profit_incfees_total = session_profit_incfees_total + profit_incfees_total
                        session_profit_incfees_perc = session_profit_incfees_perc + ((profit_incfees_total/BUDGET) * 100)
                        
                        historic_profit_incfees_total = historic_profit_incfees_total + profit_incfees_total
                        historic_profit_incfees_perc = historic_profit_incfees_perc + ((profit_incfees_total/BUDGET) * 100)
                        
                        #TRADE_TOTAL*PriceChangeIncFees_Perc)/100
                        
                        #if (LastPrice+sellFee) >= (BuyPrice+buyFee):
                        #USED_BNB_IN_SESSION = USED_BNB_IN_SESSION + buyFeeTotal

                        #if (LastPrice-sellFee) >= (BuyPrice+buyFee):
                        if USDTdiff > 0.:
                        #if (LastPrice) >= (BuyPrice):
                            trade_wins += 1
                        else:
                            trade_losses += 1
                        
                        update_bot_stats()

                        if not sell_all_coins and not sell_specific_coin:
                            # within sell_all_coins, it will print display to screen
                            balance_report(last_price)

                    # sometimes get "rate limited" errors from Binance if we try to sell too many coins at once
                    # so wait 1 second in between sells
                    if not TEST_MODE:
                        time.sleep(1) #wait for sell, evited rate limited
                    else:
                        time.sleep(MICROSECONDS)
                    
                    continue

                # no action; print once every TIME_DIFFERENCE
                #if hsp_head == 1:
                    #if len(coins_bought) > 0:
                        #if not SCREEN_MODE == 2: print(f"Holding: {coins_bought[coin]['volume']} of {coin} | {LastPrice} - {BuyPrice} | Profit: {txcolors.SELL_PROFIT if PriceChangeIncFees_Perc >= 0. else txcolors.SELL_LOSS}{PriceChangeIncFees_Perc:.4f}% Est: ({(TRADE_TOTAL*PriceChangeIncFees_Perc)/100:.{decimals()}f} {PAIR_WITH}){txcolors.DEFAULT}")
                        #print(f"{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}Holding: {coins_bought[coin]['volume']} of {coin} | {LastPrice} - {BuyPrice} | Profit: {txcolors.SELL_PROFIT if PriceChangeIncFees_Perc >= 0. else txcolors.SELL_LOSS}{PriceChangeIncFees_Perc:.4f}% Est: ({((float(coins_bought[coin]['volume'])*float(coins_bought[coin]['bought_at']))*PriceChangeIncFees_Perc)/100:.{decimals()}f} {PAIR_WITH}){txcolors.DEFAULT}")         
            #if hsp_head == 1 and len(coins_bought) == 0: if not SCREEN_MODE == 2: print(f"No trade slots are currently in use")
            # if tpsl_override: is_bot_running = False 
            #show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())
    except Exception as e:
        write_log(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.WARNING}sell_coins(): {languages_bot.MSG1[LANGUAGE]}: {e}{txcolors.DEFAULT}')
        write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
        lost_connection(e, "sell_coins")
        pass
    except KeyboardInterrupt as ki:
        pass

    return coins_sold
	
def sell_all(msgreason, session_tspl_ovr = False):
    global sell_all_coins
    #show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())
    msg_discord(f'{str(datetime.now())} | SELL ALL COINS: {msgreason}')

	# stop external signals so no buying/selling/pausing etc can occur
    stop_signal_threads()

	# sell all coins NOW!
    sell_all_coins = True

    coins_sold = sell_coins(session_tspl_ovr)
    remove_from_portfolio(coins_sold)
	
	# display final info to screen
    last_price = get_price() #sell_all
    #print("sell_all: last_price= ", last_price)
    discordmsg = balance_report(last_price)
    msg_discord(discordmsg)
    sell_all_coins = False
    #show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())

#extracted from the code of OlorinSledge
def sell_coin(coin):
	#show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())
	global sell_specific_coin
	#print(f'{str(datetime.now())} | SELL SPECIFIC COIN: {coin}')
	msg_discord(f'{str(datetime.now())} | SELL SPECIFIC COIN: {coin}')
	# sell all coins NOW!
	sell_specific_coin = True
	coins_sold = sell_coins(False, coin)
	remove_from_portfolio(coins_sold)
	sell_specific_coin = False
	#show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())
	
def sell_external_signals():
    external_list = {}
    signals1 = []
    signals2 = []
    #show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())
    if USE_SIGNALLING_MODULES:
        # check directory and load pairs from files into external_list
        signals = glob.glob("signals/*.sell")
        for filename in signals:
            for line in open(filename):
                symbol = line.strip()
                external_list[symbol] = symbol
                print(f'{symbol} added to sell_external_signals() list')
            try:
                os.remove(filename)
            except:
                if DEBUG: write_log(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.WARNING} {"sell_external_signals()"}: Could not remove external SELL signalling file{txcolors.DEFAULT}')
    else:
        coins1 = []
        TICKERS = ''
        if USE_MOST_VOLUME_COINS == True:
            TICKERS = 'volatile_volume_' + str(date.today()) + '.txt'
        else:
            TICKERS = 'tickers.txt'            
        for line in open(TICKERS):
            pairs=[line.strip() + PAIR_WITH for line in open(TICKERS)] 
        for pair in pairs:
            coins1.append(pair)

        signals1, signals2 = megatronmod.analyze(c_data, coins1, False)#, 0)
        #print("sell_external_signals: ", signals2)
        #for signal in signals2:
        #    external_list[signal] = signal
    #show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())
    return signals2 #external_list

def extract_order_data(order_details):
	try:
		global TRADING_FEE, STOP_LOSS, TAKE_PROFIT
		#show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())
		transactionInfo = {}
		# This code is from GoranJovic - thank you!
		#
		# adding order fill extractions here
		#
		# just to explain what I am doing here:
		# Market orders are not always filled at one price, we need to find the averages of all 'parts' (fills) of this order.
		#
		# reset other variables to 0 before use
		FILLS_TOTAL = 0
		FILLS_QTY = 0
		FILLS_FEE = 0
		BNB_WARNING = 0
		# loop through each 'fill':
		for fills in order_details['fills']:
			FILL_PRICE = float(fills['price'])
			FILL_QTY = float(fills['qty'])
			FILLS_FEE += float(fills['commission'])
			# check if the fee was in BNB. If not, log a nice warning:
			if (fills['commissionAsset'] != 'BNB') and (TRADING_FEE == 0.075) and (BNB_WARNING == 0):
				if not SCREEN_MODE == 2: print(f"WARNING: BNB not used for trading fee, please ")
				BNB_WARNING += 1
			# quantity of fills * price
			FILLS_TOTAL += (FILL_PRICE * FILL_QTY)
			# add to running total of fills quantity
			FILLS_QTY += FILL_QTY
			# increase fills array index by 1

		# calculate average fill price:
		FILL_AVG = (FILLS_TOTAL / FILLS_QTY)

		#tradeFeeApprox = (float(FILLS_QTY) * float(FILL_AVG)) * (TRADING_FEE/100)
		# Olorin Sledge: I only want fee at the unit level, not the total level
		tradeFeeApprox = float(FILL_AVG) * (TRADING_FEE/100)

		# the volume size is sometimes outside of precision, correct it
		try:
			info = get_symbol_info(order_details['symbol']) #client.get_symbol_info(order_details['symbol'])
			#step_size = 0.0

			#step_size1 = float(info['filterType'][1]['stepSize'])
			#step_size2 = float(info['filters'][2]['stepSize'])
			#print("step_size1", step_size1, "step_size2", step_size2)
			#lot_size[coin] = step_size.index('1') - 1
			
			for filt in info['filters']:
				if filt['filterType'] == 'LOT_SIZE':
					lot_size = filt['stepSize'].find('1') - 1
					#print("lot_size", lot_size)
					break
			#step_size = info['filters'][2]['stepSize']
			#lot_size = step_size.index('1') - 1
			#lot_size = step_size - 1
			
			if lot_size <= 0:
				FILLS_QTY = int(FILLS_QTY)
			else:
				FILLS_QTY = truncate(FILLS_QTY, lot_size)
		except Exception as e:
			write_log(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.WARNING}extract_order_data(internal): Exception getting coin {order_details["symbol"]} step size! Exception: {e}{txcolors.DEFAULT}')
			write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
			pass
		# create object with received data from Binance
		transactionInfo = {
			'symbol': order_details['symbol'],
			'orderId': order_details['orderId'],
			'timestamp': order_details['transactTime'],
			'avgPrice': float(FILL_AVG),
			'volume': float(FILLS_QTY),
			'tradeFeeBNB': float(FILLS_FEE),
			'tradeFeeUnit': tradeFeeApprox,
		}
		#show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())
	except Exception as e:
		write_log(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.WARNING}extract_order_data(): {languages_bot.MSG1[LANGUAGE]}: {e}{txcolors.DEFAULT}')
		write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
		pass
	return transactionInfo

def check_total_session_profit(coins_bought, last_price):
	global is_bot_running, session_tpsl_override_msg
	#global TRADE_TOTAL
	unrealised_session_profit_incfees_total = 0
			
	BUDGET = TRADE_SLOTS * TRADE_TOTAL
	
	for coin in list(coins_bought):
		LastPrice = float(last_price[coin]['price'])
		sellFee = (LastPrice * (TRADING_FEE/100))
		
		BuyPrice = float(coins_bought[coin]['bought_at'])
		buyFee = (BuyPrice * (TRADING_FEE/100))
		
		#PriceChangeIncFees_Total = float(((LastPrice+sellFee) - (BuyPrice+buyFee)) * coins_bought[coin]['volume'])
		PriceChangeIncFees_Total = float(((LastPrice - sellFee) - (BuyPrice + buyFee)) * coins_bought[coin]['volume'])

		unrealised_session_profit_incfees_total = float(unrealised_session_profit_incfees_total + PriceChangeIncFees_Total)

	allsession_profits_perc = session_profit_incfees_perc +  ((unrealised_session_profit_incfees_total / BUDGET) * 100)

	if DEBUG: print(f'Session Override SL Feature: ASPP={allsession_profits_perc} STP {SESSION_TAKE_PROFIT} SSL {SESSION_STOP_LOSS}')
	
	if allsession_profits_perc >= float(SESSION_TAKE_PROFIT): 
		session_tpsl_override_msg = "Session TP Override target of " + str(SESSION_TAKE_PROFIT) + "% met. Sell all coins now!"
		is_bot_running = False
	if allsession_profits_perc <= float(SESSION_STOP_LOSS):
		session_tpsl_override_msg = "Session SL Override target of " + str(SESSION_STOP_LOSS) + "% met. Sell all coins now!"
		is_bot_running = False   
	#show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())
	
def update_portfolio(orders, last_price, volume):
	'''add every coin bought to our portfolio for tracking/selling later'''

	#     print(orders)
	for coin in orders:
		try:
			coin_step_size = float(next(
						filter(lambda f: f['filterType'] == 'LOT_SIZE', client.get_symbol_info(orders[coin][0]['symbol'])['filters'])
						)['stepSize'])
		except Exception as ExStepSize:
			coin_step_size = .1
			pass

		if not TEST_MODE: #or not BACKTESTING_MODE:
			coins_bought[coin] = {
			   'symbol': orders[coin]['symbol'],
			   'orderid': orders[coin]['orderId'],
			   'timestamp': orders[coin]['timestamp'],
			   'bought_at': orders[coin]['avgPrice'],
			   'volume': orders[coin]['volume'],
			   'volume_debug': volume[coin],
			   'buyFeeBNB': orders[coin]['tradeFeeBNB'],
			   'buyFee': orders[coin]['tradeFeeUnit'] * orders[coin]['volume'],
			   'stop_loss': -STOP_LOSS,
			   'take_profit': TAKE_PROFIT,
			   'step_size': float(coin_step_size),
			   }

			if not SCREEN_MODE == 2: print(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}Order for {orders[coin]["symbol"]} with ID {orders[coin]["orderId"]} placed and saved to file.{txcolors.DEFAULT}')
		else:
			coins_bought[coin] = {
				'symbol': orders[coin][0]['symbol'],
				'orderid': orders[coin][0]['orderId'],
				'timestamp': orders[coin][0]['time'],
				'bought_at': last_price[coin]['price'],
				'volume': volume[coin],
				'stop_loss': -STOP_LOSS,
				'take_profit': TAKE_PROFIT,
				'step_size': float(coin_step_size),
				}

			if not SCREEN_MODE == 2: print(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}Order for {orders[coin][0]["symbol"]} with ID {orders[coin][0]["orderId"]} placed and saved to file.{txcolors.DEFAULT}')

		# save the coins in a json file in the same directory
		with open(coins_bought_file_path, 'w') as file:
			json.dump(coins_bought, file, indent=4)
	#show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())

def update_bot_stats():
	global TRADE_TOTAL, trade_wins, trade_losses, historic_profit_incfees_perc, historic_profit_incfees_total, session_USDT_EARNED, session_USDT_LOSS, session_USDT_WON, USED_BNB_IN_SESSION
	bot_stats = {
		'total_capital' : str(TRADE_SLOTS * TRADE_TOTAL),
		'botstart_datetime' : str(bot_started_datetime),
		'historicProfitIncFees_Percent': historic_profit_incfees_perc,
		'historicProfitIncFees_Total': format(historic_profit_incfees_total, ".14f"),
		'tradeWins': trade_wins,
		'tradeLosses': trade_losses,
		'session_'+ PAIR_WITH + '_EARNED': format(session_USDT_EARNED, ".14f"),
		'session_'+ PAIR_WITH + '_LOSS': format(session_USDT_LOSS, ".14f"),
		'session_'+ PAIR_WITH + '_WON': format(session_USDT_WON, ".14f"),
		#'used_bnb_in_session': USED_BNB_IN_SESSION,
	}

	#save session info for through session portability
	with open(bot_stats_file_path, 'w') as file:
		json.dump(bot_stats, file, indent=4)
	#show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())


def remove_from_portfolio(coins_sold):
	'''Remove coins sold due to SL or TP from portfolio'''
	for coin in coins_sold:
		# code below created by getsec <3
		coins_bought.pop(coin)
	with open(coins_bought_file_path, 'w') as file:
		json.dump(coins_bought, file, indent=4)
	if os.path.exists('signalsell_tickers.txt'):
		os.remove('signalsell_tickers.txt')
		for coin in coins_bought:
			write_signallsell(coin.removesuffix(PAIR_WITH))
	#show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())
	
def write_signallsell(symbol):
	with open('signalsell_tickers.txt','a+') as f:
		f.write(f'{symbol}\n')
	#show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())

def remove_external_signals(fileext):
	signals = glob.glob(f'signals/*.{fileext}')
	for filename in signals:
		if os.path.exists(filename):
			os.remove(filename)
		#for line in open(filename):
			#try:
				#os.remove(filename)
			#except:
				#if DEBUG: write_log(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.WARNING} remove_external_signals(): Could not remove external signalling file {filename}{txcolors.DEFAULT}')
	#show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())
	
def load_signal_threads():
	try:
		#load signalling modules
		global signalthreads
		signalthreads = []
		if SIGNALLING_MODULES is not None and USE_SIGNALLING_MODULES: 
			if len(SIGNALLING_MODULES) > 0:
				for module in SIGNALLING_MODULES:
					if os.path.exists(module+'.py'):
						print(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}Starting {module}{txcolors.DEFAULT}')
						mymodule[module] = importlib.import_module(module)
						t = threading.Thread(target=mymodule[module].do_work, args=())
						#t = multiprocessing.Process(target=mymodule[module].do_work, args=())
						t.name = module
						t.daemon = True
						t.start()
						signalthreads.append(t)
						time.sleep(2000/1000) #wait for load_signal_threads
					else:
						write_log(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.WARNING}Module {module} does not exist... continuing to load other modules{txcolors.DEFAULT}')
			else:
				write_log(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.WARNING}{"load_signal_threads"}: No modules to load {SIGNALLING_MODULES}{txcolors.DEFAULT}')
		#show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())
	except Exception as e:
		write_log(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.WARNING}load_signal_threads(): Loading external signals exception: {e}{txcolors.DEFAULT}')
		write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
		pass

def stop_signal_threads():
	try:
		global signalthreads
		if len(signalthreads) > 0:
			for signalthread in signalthreads:
				print(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}Terminating thread {str(signalthread.name)}{txcolors.DEFAULT}')
				signalthread.terminate()
				signalthread.kill()
		##show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())
	except Exception as e:
		write_log(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}stop_signal_threads(): {languages_bot.MSG1[LANGUAGE]}: {e}{txcolors.DEFAULT}')
		write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
		pass
	except KeyboardInterrupt as ki:
		pass

def truncate(number, decimals=0):
	"""
	Returns a value truncated to a specific number of decimal places.
	Better than rounding
	"""
	if not isinstance(decimals, int):
		raise TypeError("decimal places must be an integer.")
	elif decimals < 0:
		raise ValueError("decimal places has to be 0 or more.")
	elif decimals == 0:
		return math.trunc(number)

	factor = 10.0 ** decimals
	return math.trunc(number * factor) / factor

def load_settings():
	##show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())
	# set to false at Start
    global bot_paused, parsed_config, creds_file, access_key, secret_key, parsed_creds
    bot_paused = False

    DEFAULT_CONFIG_FILE = 'config.yml'
    DEFAULT_CREDS_FILE = 'creds.yml'

    config_file = args.config if args.config else DEFAULT_CONFIG_FILE
    creds_file = args.creds if args.creds else DEFAULT_CREDS_FILE
    parsed_config = load_config(config_file)
    parsed_creds = load_config(creds_file)

	# Default no debugging
    global DEBUG, ENABLE_FUNCTION_NAME, SHOW_FUNCTION_NAME, SAVE_FUNCTION_NAME, SHOW_VARIABLES_AND_VALUE, SAVE_VARIABLES_AND_VALUE
    global TEST_MODE, BACKTESTING_MODE, BACKTESTING_MODE_TIME_START, BACKTESTING_MODE_TIME_END, BOT_TIMEFRAME, LOG_TRADES, TRADES_LOG_FILE
    global DEBUG_SETTING, AMERICAN_USER, PAIR_WITH, QUANTITY, MAX_COINS, FIATS, TIME_DIFFERENCE, RECHECK_INTERVAL, CHANGE_IN_PRICE
    global STOP_LOSS, TAKE_PROFIT, CUSTOM_LIST, TICKERS_LIST, USE_TRAILING_STOP_LOSS, TRAILING_STOP_LOSS, TRAILING_TAKE_PROFIT, TRADING_FEE
    global SIGNALLING_MODULES, SCREEN_MODE, MSG_DISCORD, HISTORY_LOG_FILE, TRADE_SLOTS, TRADE_TOTAL, SESSION_TPSL_OVERRIDE, coin_bought
    global SELL_ON_SIGNAL_ONLY, TRADING_FEE, SHOW_INITIAL_CONFIG, USE_MOST_VOLUME_COINS, COINS_MAX_VOLUME, MAIN_FILES_PATH, USE_VOLATILE_METOD
    global COINS_MIN_VOLUME, DISABLE_TIMESTAMPS, STATIC_MAIN_INFO, COINS_BOUGHT, BOT_STATS, PRINT_TO_FILE
    global ENABLE_PRINT_TO_FILE, EX_PAIRS, RESTART_MODULES, SHOW_TABLE_COINS_BOUGHT, ALWAYS_OVERWRITE, ALWAYS_CONTINUE, SORT_TABLE_BY
    global REVERSE_SORT, MAX_HOLDING_TIME, IGNORE_FEE, EXTERNAL_COINS, PROXY_HTTP, PROXY_HTTPS,USE_SIGNALLING_MODULES, REINVEST_MODE
    global LOG_FILE, PANIC_STOP, ASK_ME, BUY_PAUSED, UPDATE_MOST_VOLUME_COINS, VOLATILE_VOLUME, COMPOUND_INTEREST, MICROSECONDS, LANGUAGE

	# Default no debugging
    DEBUG = False

	# Load system vars
    TEST_MODE = parsed_config['script_options']['TEST_MODE']
    LANGUAGE = parsed_config['script_options']['LANGUAGE']
    BACKTESTING_MODE = parsed_config['script_options']['BACKTESTING_MODE']
    BACKTESTING_MODE_TIME_START = parsed_config['script_options']['BACKTESTING_MODE_TIME_START']
    BOT_TIMEFRAME = parsed_config['script_options']['BOT_TIMEFRAME']
    BACKTESTING_MODE_TIME_END = parsed_config['script_options']['BACKTESTING_MODE_TIME_END']
    USE_VOLATILE_METOD = parsed_config['script_options']['USE_VOLATILE_METOD']
    USE_SIGNALLING_MODULES = parsed_config['script_options']['USE_SIGNALLING_MODULES']
	#REINVEST_MODE = parsed_config['script_options']['REINVEST_MODE']
	#     LOG_TRADES = parsed_config['script_options'].get('LOG_TRADES')
    MAIN_FILES_PATH = parsed_config['script_options'].get('MAIN_FILES_PATH')
    TRADES_LOG_FILE = parsed_config['script_options'].get('TRADES_LOG_FILE')
    LOG_FILE = parsed_config['script_options'].get('LOG_FILE')
    COINS_BOUGHT = parsed_config['script_options'].get('COINS_BOUGHT')
    BOT_STATS = parsed_config['script_options'].get('BOT_STATS')
    DEBUG_SETTING = parsed_config['script_options'].get('DEBUG')
    ENABLE_FUNCTION_NAME = parsed_config['script_options'].get('ENABLE_FUNCTION_NAME')
    SAVE_FUNCTION_NAME = parsed_config['script_options'].get('SAVE_FUNCTION_NAME')
    SHOW_FUNCTION_NAME = parsed_config['script_options'].get('SHOW_FUNCTION_NAME')
    SHOW_VARIABLES_AND_VALUE = parsed_config['script_options'].get('SHOW_VARIABLES_AND_VALUE')
    SAVE_VARIABLES_AND_VALUE = parsed_config['script_options'].get('SAVE_VARIABLES_AND_VALUE')
    MICROSECONDS = parsed_config['script_options'].get('MICROSECONDS')
    AMERICAN_USER = parsed_config['script_options'].get('AMERICAN_USER')
	#EXTERNAL_COINS = parsed_config['script_options']['EXTERNAL_COINS']

	# Load trading vars
    PAIR_WITH = parsed_config['trading_options']['PAIR_WITH']
    COMPOUND_INTEREST = parsed_config['trading_options']['COMPOUND_INTEREST']
    TRADE_TOTAL = parsed_config['trading_options']['TRADE_TOTAL']            
    TRADE_SLOTS = parsed_config['trading_options']['TRADE_SLOTS']
		
	#FIATS = parsed_config['trading_options']['FIATS']
    EX_PAIRS = parsed_config['trading_options']['EX_PAIRS']
	
    TIME_DIFFERENCE = parsed_config['trading_options']['TIME_DIFFERENCE']
    RECHECK_INTERVAL = parsed_config['trading_options']['RECHECK_INTERVAL']
	
    CHANGE_IN_PRICE = parsed_config['trading_options']['CHANGE_IN_PRICE']
    STOP_LOSS = parsed_config['trading_options']['STOP_LOSS']
    TAKE_PROFIT = parsed_config['trading_options']['TAKE_PROFIT']
	
	#COOLOFF_PERIOD = parsed_config['trading_options']['COOLOFF_PERIOD']

    CUSTOM_LIST = parsed_config['trading_options']['CUSTOM_LIST']
    TICKERS_LIST = parsed_config['trading_options']['TICKERS_LIST']
	
    USE_TRAILING_STOP_LOSS = parsed_config['trading_options']['USE_TRAILING_STOP_LOSS']
    TRAILING_STOP_LOSS = parsed_config['trading_options']['TRAILING_STOP_LOSS']
    TRAILING_TAKE_PROFIT = parsed_config['trading_options']['TRAILING_TAKE_PROFIT']
	 
	# Code modified from DJCommie fork
	# Load Session OVERRIDE values - used to STOP the bot when current session meets a certain STP or SSL value
    SESSION_TPSL_OVERRIDE = parsed_config['trading_options']['SESSION_TPSL_OVERRIDE']
    SESSION_TAKE_PROFIT = parsed_config['trading_options']['SESSION_TAKE_PROFIT']
    SESSION_STOP_LOSS = parsed_config['trading_options']['SESSION_STOP_LOSS']

	# Borrowed from DJCommie fork
	# If TRUE, coin will only sell based on an external SELL signal
    SELL_ON_SIGNAL_ONLY = parsed_config['trading_options']['SELL_ON_SIGNAL_ONLY']

	# Discord integration
	# Used to push alerts, messages etc to a discord channel
    MSG_DISCORD = parsed_config['trading_options']['MSG_DISCORD']
	
    sell_all_coins = False
    sell_specific_coin = False
	
	# Functionality to "reset / restart" external signal modules(code os OlorinSledge)
    RESTART_MODULES = parsed_config['trading_options']['RESTART_MODULES']
	
	#minimal mode
    SCREEN_MODE = parsed_config['trading_options']['SCREEN_MODE']
    STATIC_MAIN_INFO = parsed_config['trading_options']['STATIC_MAIN_INFO']
    DISABLE_TIMESTAMPS = parsed_config['trading_options']['DISABLE_TIMESTAMPS']
	#PRINT_TO_FILE = parsed_config['trading_options']['PRINT_TO_FILE']
	#ENABLE_PRINT_TO_FILE = parsed_config['trading_options']['ENABLE_PRINT_TO_FILE']
    IGNORE_FEE = parsed_config['trading_options']['IGNORE_FEE']
    if IGNORE_FEE == False:
        TRADING_FEE = parsed_config['trading_options']['TRADING_FEE']
    else:
        TRADING_FEE = 0    
    SIGNALLING_MODULES = parsed_config['trading_options']['SIGNALLING_MODULES']
	
    SHOW_INITIAL_CONFIG = parsed_config['trading_options']['SHOW_INITIAL_CONFIG']
    SHOW_TABLE_COINS_BOUGHT = parsed_config['trading_options']['SHOW_TABLE_COINS_BOUGHT']

    USE_MOST_VOLUME_COINS = parsed_config['trading_options']['USE_MOST_VOLUME_COINS']
    COINS_MAX_VOLUME = parsed_config['trading_options']['COINS_MAX_VOLUME']
    COINS_MIN_VOLUME = parsed_config['trading_options']['COINS_MIN_VOLUME']
    ALWAYS_OVERWRITE = parsed_config['trading_options']['ALWAYS_OVERWRITE']
    ALWAYS_CONTINUE = parsed_config['trading_options']['ALWAYS_CONTINUE']
    ASK_ME = parsed_config['trading_options']['ASK_ME']
	
    SORT_TABLE_BY = parsed_config['trading_options']['SORT_TABLE_BY']
    REVERSE_SORT = parsed_config['trading_options']['REVERSE_SORT']
	
    MAX_HOLDING_TIME = parsed_config['trading_options']['MAX_HOLDING_TIME']
	
    IGNORE_FEE = parsed_config['trading_options']['IGNORE_FEE']
	
    PROXY_HTTP = parsed_config['script_options']['PROXY_HTTP']
    PROXY_HTTPS = parsed_config['script_options']['PROXY_HTTPS']
	
    PANIC_STOP = parsed_config['trading_options']['PANIC_STOP']
    BUY_PAUSED = parsed_config['script_options']['BUY_PAUSED']
	
    UPDATE_MOST_VOLUME_COINS = parsed_config['trading_options']['UPDATE_MOST_VOLUME_COINS']
    VOLATILE_VOLUME = parsed_config['trading_options']['VOLATILE_VOLUME']
	#BNB_FEE = parsed_config['trading_options']['BNB_FEE']
	#TRADING_OTHER_FEE = parsed_config['trading_options']['TRADING_OTHER_FEE']
    
    update_data_coin()
    
    if DEBUG_SETTING or args.debug:
        DEBUG = True
    print(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}All config loaded...{txcolors.DEFAULT}')
    access_key, secret_key = load_correct_creds(parsed_creds)
    #show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())
	
def CheckIfAliveStation(ip_address):
    try:
        ##show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())
        # for windows
        if os.name == 'nt':
            # WARNING - Windows Only
            alive = False
            ping_output = subprocess.run(['ping', '-n', '1', ip_address],shell=True,stdout=subprocess.PIPE)
            if (ping_output.returncode == 0):
                if not ('unreachable' in str(ping_output.stdout)):
                    alive = True
        else:
            alive = False
            p = os.popen(f'ping -c 1 -W 2 {ip_address}').read()
            #print(f'output= {p}')
            if ("PING" in p):
                alive = True
    except Exception as e:
        write_log(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}CheckIfAliveStation(): {languages_bot.MSG1[LANGUAGE]}: {e}{txcolors.DEFAULT}')
        write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
        pass
    return alive
	
def lost_connection(error, origin):
	##show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())
	global lostconnection
	if "HTTPSConnectionPool" in str(error) or "Connection aborted" in str(error):
		#print(f"HTTPSConnectionPool - {origin}")
		stop_signal_threads()
		if lostconnection == False:
			lostconnection = True
			#print(f"lostconnection: {lostconnection} - {origin}")
			write_log(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {origin} - Lost connection, waiting until it is restored...{txcolors.DEFAULT}')
			while lostconnection:
				lostconnection = True
				#if "HTTPSConnectionPool" in error:
				#try:
				response = CheckIfAliveStation("google.com")
				#print(f"response: {response}")
				if response == True:
					write_log(f'{txcolors.BUY}{languages_bot.MSG5[LANGUAGE]}: The connection has been reestablished, continuing...{txcolors.DEFAULT}')
					lostconnection = False
					load_signal_threads()
					return
				else:
					#print(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {origin} Lost connection, waiting 5 seconds until it is restored...{txcolors.DEFAULT}') 
					lostconnection = True
					time.sleep(5) #lostconnection
		else:
			while lostconnection:
				#print(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: Lost connection, waiting 5 seconds until it is restored...{txcolors.DEFAULT}')
				time.sleep(5) #lostconnection

def renew_list(in_init=False):
	try:
		##show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())
		global tickers, VOLATILE_VOLUME, FLAG_PAUSE, COINS_MAX_VOLUME, COINS_MIN_VOLUME
		volatile_volume_empty = False
		volatile_volume_time = False
		if USE_MOST_VOLUME_COINS == True:
			today = "volatile_volume_" + str(date.today()) + ".txt"
			if VOLATILE_VOLUME == "":
				volatile_volume_empty = True
			else:
				now = datetime.now()
				dt_string = datetime.strptime(now.strftime("%y-%m-%d %H_%M_%S"),"%y-%m-%y %H_%M_%S")
				tuple1 = dt_string.timetuple()
				timestamp1 = time.mktime(tuple1)

				#timestampNOW = now.timestamp()
				dt_string_old = datetime.strptime(VOLATILE_VOLUME.replace("(", " ").replace(")", "").replace("volatile_volume_", ""),"%y-%m-%d %H_%M_%S") + timedelta(minutes = UPDATE_MOST_VOLUME_COINS)               
				tuple2 = dt_string_old.timetuple()
				timestamp2 = time.mktime(tuple2)
				if timestamp1 > timestamp2:
					volatile_volume_time = True

			if volatile_volume_time or volatile_volume_empty or os.path.exists(today) == False:
				print(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}A new Volatily Volume list will be created...{txcolors.DEFAULT}')
				stop_signal_threads()
				FLAG_PAUSE = True
				if TEST_MODE: 
					jsonfile = "test_" + COINS_BOUGHT
				else: 
					jsonfile = "live_" + COINS_BOUGHT
					
				VOLATILE_VOLUME = get_volume_list()
				
				if os.path.exists(jsonfile):    
					with open(jsonfile,'r') as f:
						coins_bought_list = json.load(f)
   
					
					with open(today,'r') as f:
						lines_today = f.readlines()
					
					#coinstosave = []

					for coin_bought in list(coins_bought_list):
						coin_bought = coin_bought.replace("USDT", "") + "\n"
						if not coin_bought in list(lines_today):
							lines_today.append(coin_bought)
					# for coin in coins_bought_list:
						# coinstosave.append(coin.replace(PAIR_WITH,"") + "\n")
					
					# for c in coinstosave:
						# for l in lines_today:
							# if c == l:
								# break
							# else:
								# lines_today.append(c)
								# break                
							
					with open(today,'w') as f:
						f.writelines(lines_today)

					print(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}A new Volatily Volume list has been created, {len(list(coins_bought_list))} coin(s) added...{txcolors.DEFAULT}')
					FLAG_PAUSE = False
					#renew_list()
					load_signal_threads()     
				
		else:
			if in_init:
				stop_signal_threads()
				
				FLAG_PAUSE = True
				
				if TEST_MODE: 
					jsonfile = "test_" + COINS_BOUGHT
				else: 
					jsonfile = "live_" + COINS_BOUGHT
					
				if os.path.exists(jsonfile): 
					with open(jsonfile,'r') as f:
						coins_bought_list = json.load(f)

					with open(TICKERS_LIST,'r') as f:
							lines_tickers = f.readlines()
							
					if os.path.exists(TICKERS_LIST.replace(".txt",".backup")): 
						os.remove(TICKERS_LIST.replace(".txt",".backup"))
						
					with open(TICKERS_LIST.replace(".txt",".backup"),'w') as f:
						f.writelines(lines_tickers)
					
					new_lines_tickers = []
					for line_tickers in lines_tickers:
						if "\n" in line_tickers:
							new_lines_tickers.append(line_tickers)
						else:
							new_lines_tickers.append(line_tickers + "\n")
									
					for coin_bought in list(coins_bought_list):
						coin_bought = coin_bought.replace("USDT", "") + "\n"
						if not coin_bought in new_lines_tickers:
							new_lines_tickers.append(coin_bought)
							
					with open(TICKERS_LIST,'w') as f:
						f.writelines(new_lines_tickers)
					
			tickers=[line.strip() for line in open(TICKERS_LIST)]
	except Exception as e:
		write_log(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.WARNING}renew_list(): {languages_bot.MSG1[LANGUAGE]}: {e}{txcolors.DEFAULT}')
		write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
		pass
		
def remove_by_extension(extension):
	try:
		##show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())
		files = [item for sublist in [glob.glob(ext) for ext in [os.path.dirname(__file__) + extension]] for item in sublist]
		#print("files: ", files)
		for file in files:
			#if file.endswith(extension):
			if os.path.exists(file): 
				print(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.WARNING}Remove {file}{txcolors.DEFAULT}')
				os.remove(file)
	except Exception as e:
		write_log(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.WARNING}remove_by_extension(): {languages_bot.MSG1[LANGUAGE]}: {e}{txcolors.DEFAULT}')
		write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
		pass  

def remove_by_file_name(name):
	try:
		##show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())
		file1 = os.path.dirname(__file__) + "\.".replace(".","") + name
		#print("file: ", file)
		file_exists1 = os.path.exists(file1)
		#print("file: ", file1, "file_exists: ", file_exists1)
		if file_exists1: 
			print(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.WARNING}Remove {file1}{txcolors.DEFAULT}')
			os.remove(file1)
	except Exception as e:
		write_log(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.WARNING}remove_by_extension(): {languages_bot.MSG1[LANGUAGE]}: {e}{txcolors.DEFAULT}')
		write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
		pass        

def new_or_continue():
	##show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())
	if TEST_MODE: 
		file_prefix = 'test_'
	else:
		file_prefix = 'live_'      
	
	if os.path.exists(file_prefix + str(COINS_BOUGHT)) or os.path.exists(file_prefix + str(BOT_STATS)):
		LOOP = True
		END = False
		while LOOP:
			if ALWAYS_OVERWRITE and ALWAYS_CONTINUE or ALWAYS_OVERWRITE == False and ALWAYS_CONTINUE == False:
				print(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}The configuration is incorrect, ALWAYS_OVERWRITE and ALWAYS_CONTINUE cannot be true or both can be false{txcolors.DEFAULT}')
				exit(1)
			if ASK_ME:
				print(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}Do you want to continue previous session?[y/n]{txcolors.DEFAULT}')
				x = input("#: ")
			else:
				if ALWAYS_OVERWRITE:
					x = "n"
				if ALWAYS_CONTINUE:
					x = "y"

			if x == "y" or x == "n":
				if x == "y":
					print(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}Continuing with the session started ...{txcolors.DEFAULT}')
					LOOP = False
					END = True
				else:
					print(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}Deleting previous sessions ...')
					if USE_MOST_VOLUME_COINS == False:
						if os.path.exists(TICKERS_LIST.replace(".txt",".backup")):
							with open(TICKERS_LIST.replace(".txt",".backup") ,'r') as f:
								lines_tickers = f.readlines()                            
							with open(TICKERS_LIST,'w') as f:
								f.writelines(lines_tickers)
							os.remove(TICKERS_LIST.replace(".txt",".backup"))     

					remove_by_file_name(file_prefix + TRADES_LOG_FILE)
					remove_by_file_name(file_prefix + TRADES_LOG_FILE.replace("csv", "html"))
					remove_by_file_name(file_prefix + COINS_BOUGHT)
					remove_by_file_name(file_prefix + BOT_STATS)
					remove_by_file_name(file_prefix + LOG_FILE)
					remove_by_extension("/*.log")
					remove_by_extension("/*.pause")
					remove_by_extension("/*.buy")
					remove_by_extension("/*.sell")
					remove_by_extension("/*.position")

					print(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}Session deleted, continuing ...{txcolors.DEFAULT}')
					LOOP = False
					END = True
			else:
				print(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}Press the y key or the or key ...{txcolors.DEFAULT}')
				LOOP = True
		return END

@atexit.register
def end_bot():
    try:
        convert_csv_to_html(TRADES_LOG_FILE)
        menu()
    except Exception as e:
        write_log(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.WARNING} Exception in end_bot(): {e}{txcolors.DEFAULT}')
        write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
        pass
        
def menu():
    try:
		##show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())
        global COINS_MAX_VOLUME, COINS_MIN_VOLUME
        global SCREEN_MODE, PAUSEBOT_MANUAL, BUY_PAUSED, TRADE_TOTAL
        END = False
        LOOP = True
        stop_signal_threads()
        while LOOP:
            time.sleep(5) #menu
            print(f'\n \n')
            print(f'{txcolors.MENUOPTION}[1]{txcolors.WARNING}Reload Configuration{txcolors.DEFAULT}')
            print(f'{txcolors.MENUOPTION}[2]{txcolors.WARNING}Reload modules{txcolors.DEFAULT}')
            print(f'{txcolors.MENUOPTION}[3]{txcolors.WARNING}Reload Volatily Volume List{txcolors.DEFAULT}')
            if BUY_PAUSED == False: #PAUSE{languages_bot.MSG5[LANGUAGE]}_MANUAL == False or 
                print(f'{txcolors.MENUOPTION}[4]{txcolors.WARNING}Stop Purchases{txcolors.DEFAULT}')
            else:
                print(f'{txcolors.MENUOPTION}[4]{txcolors.WARNING}Start Purchases{txcolors.DEFAULT}')
            print(f'{txcolors.MENUOPTION}[5]{txcolors.WARNING}Sell Specific Coin{txcolors.DEFAULT}')
            print(f'{txcolors.MENUOPTION}[6]{txcolors.WARNING}Sell All Coins{txcolors.DEFAULT}')
            print(f'{txcolors.MENUOPTION}[7]{txcolors.WARNING}Convert {TRADES_LOG_FILE} to html{txcolors.DEFAULT}')
            print(f'{txcolors.MENUOPTION}[8]{txcolors.WARNING}Exit {languages_bot.MSG5[LANGUAGE]}{txcolors.DEFAULT}')
            x = input('Please enter your choice: ')
            x = int(x)
            print(f'\n \n')
            if x == 1:
                load_settings()
                renew_list()
                LOOP = False
                load_signal_threads()
                print(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.WARNING}Reaload Completed{txcolors.DEFAULT}')
            elif x == 2:
                stop_signal_threads()
                load_signal_threads()
                print(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.WARNING}Modules Realoaded Completed{txcolors.DEFAULT}')
                LOOP = False
            elif x == 3:
                stop_signal_threads()
				#load_signal_threads()
                global VOLATILE_VOLUME
                if USE_MOST_VOLUME_COINS == True:
                    os.remove(VOLATILE_VOLUME + ".txt")
                    VOLATILE_VOLUME = get_volume_list()
                    renew_list()
                else:
                    print(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.WARNING}USE_MOST_VOLUME_COINS must be true in config.yml{txcolors.DEFAULT}')
                    LOOP = False
                print(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.WARNING}VOLATILE_VOLUME Realoaded Completed{txcolors.DEFAULT}')
                load_signal_threads()
                LOOP = False
            elif x == 4:
                if BUY_PAUSED == False:
                    set_config("BUY_PAUSED", True)
                    PAUSEBOT_MANUAL = True
                    BUY_PAUSED = True
                    stop_signal_threads()
                    load_signal_threads()                  
                    LOOP = False
                else:
                    PAUSEBOT_MANUAL = False
                    set_config("BUY_PAUSED", False)
                    BUY_PAUSED = False
                    stop_signal_threads()
                    load_signal_threads()
                    LOOP = False
            elif x == 5:
				#part of extracted from the code of OlorinSledge
                stop_signal_threads()
                while not x == "n":
					#last_price = get_price() #menu
                    print_table_coins_bought()
                    print(f'{txcolors.WARNING}\nType in the Symbol you wish to sell. [n] to continue {languages_bot.MSG5[LANGUAGE]}.{txcolors.DEFAULT}')
                    x = input("#: ")
                    if x == "":
                        break
                    sell_coin(x.upper() + PAIR_WITH)
                load_signal_threads()
                LOOP = False				
            elif x == 6:
                stop_signal_threads()
                print(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.WARNING}Do you want to sell all coins?[y/n]{txcolors.DEFAULT}')
                sellall = input("#: ")
                if sellall.upper() == "Y":
                    sell_all('Sell all, manual choice!')
                load_signal_threads()
                LOOP = False
            elif x == 7:
                print(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.WARNING}Converting LOG_TRADES to html...{txcolors.DEFAULT}')
                convert_csv_to_html(TRADES_LOG_FILE)
                LOOP = False
            elif x == 8:
                stop_signal_threads()
                print(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.WARNING}Program execution ended by user!{txcolors.DEFAULT}')
                sys.exit(0)
            else:
                print(f'wrong choice')
                LOOP = True
		##show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())
    except Exception as e:
        write_log(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.WARNING} Exception in menu(): {e}{txcolors.DEFAULT}')
        write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
        pass
    except KeyboardInterrupt as ki:
        menu()
    return END
	
def print_banner():
	PRINT_BANNER = False
	if PRINT_BANNER:
	##show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())
		__header__='''
		\033[92m   ___ _                        __   __   _      _   _ _ _ _          _____            _ _             ___     _   
		\033[92m  | _ (_)_ _  __ _ _ _  __ ___  \ \ / ___| |__ _| |_(_| (_| |_ _  _  |_   __ _ __ _ __| (_)_ _  __ _  | _ )___| |_ 
		\033[92m  | _ | | ' \/ _` | ' \/ _/ -_)  \ V / _ | / _` |  _| | | |  _| || |   | || '_/ _` / _` | | ' \/ _` | | _ / _ |  _|
		\033[92m  |___|_|_||_\__,_|_||_\__\___|   \_/\___|_\__,_|\__|_|_|_|\__|\_, |   |_||_| \__,_\__,_|_|_||_\__, | |___\___/\__|
		\033[92m                                                                |__/                            |___/ by Pantersxx3'''
		print(f'{__header__}')
		print(f'{txcolors.DEFAULT}')

def create_conection_binance(force=False):
    global BACKTESTING_MODE, AMERICAN_USER, PROXY_HTTP, PROXY_HTTPS, client
    if not BACKTESTING_MODE or force:
        # Authenticate with the client, Ensure API key is good before continuing
        if AMERICAN_USER:
            if PROXY_HTTP != '' or PROXY_HTTPS != '': 
                print(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT} Using proxy ...')
                proxies = {
                        'http': PROXY_HTTP,
                        'https': PROXY_HTTPS
                }
                client = Client(access_key, secret_key, {'proxies': proxies}, tld='us')
            else:
                client = Client(access_key, secret_key, tld='us')
        else:
            if PROXY_HTTP != '' or PROXY_HTTPS != '': 
                print(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT} Using proxy ...')
                proxies = {
                        'http': PROXY_HTTP,
                        'https': PROXY_HTTPS
                }
                client = Client(access_key, secret_key, {'proxies': proxies})
            else:
                client = Client(access_key, secret_key)

        # If the users has a bad / incorrect API key.
        # this will stop the script from starting, and display a helpful error.
        api_ready, msg = test_api_key(client, BinanceAPIException)
        if api_ready is not True:
            exit(f'{txcolors.SELL_LOSS}{msg}{txcolors.DEFAULT}')
                
if __name__ == '__main__':
    req_version = (3,9)
    if sys.version_info[:2] < req_version: 
        print(f'This bot requires Python version 3.9 or higher/newer. You are running version {sys.version_info[:2]} - please upgrade your Python version!!{txcolors.DEFAULT}')
        sys.exit(0)
		# Load arguments then parse settings
    args = parse_args()
    mymodule = {}
    print_banner()
    print(f'')
    print(f'{txcolors.WARNING}BOT: {txcolors.DEFAULT}Initializing, wait a moment...{txcolors.DEFAULT}')
    discord_msg_balance_data = ""
    last_msg_discord_balance_date = datetime.now()
    global client
    load_settings()
    if not BACKTESTING_MODE:
        if not CheckIfAliveStation("google.com"):
            print(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}You not have internet, Exit...{txcolors.DEFAULT}')
            sys.exit(0)    
 
    if not DISABLE_TIMESTAMPS:
		# print with timestamps
        old_out = sys.stdout
        class St_ampe_dOut:
            """Stamped stdout."""
            nl = True
            def write(self, x):
                """Write function overloaded."""
                if x == '\n':
                    old_out.write(x)
                    self.nl = True
                elif self.nl:
                    old_out.write(f'{txcolors.DIM}[{str(datetime.now().replace(microsecond=0))}]{txcolors.DEFAULT} {x}')
                    self.nl = False
                else:
                    old_out.write(x)

            def flush(self):
                pass

        sys.stdout = St_ampe_dOut()
			
	# Load creds for correct environment
    if DEBUG:
        if SHOW_INITIAL_CONFIG == True: print(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}Loaded config below\n{json.dumps(parsed_config, indent=4)}{txcolors.DEFAULT}')
        if SHOW_INITIAL_CONFIG == True: print(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}Your credentials have been loaded from {creds_file}{txcolors.DEFAULT}')
		
    if MSG_DISCORD:
        DISCORD_WEBHOOK = load_discord_creds(parsed_creds)
		
	#if MSG_DISCORD:
        #MSG_DISCORD = True

    sell_all_coins = False
    sell_specific_coin = False
    
    create_conection_binance()
	
    new_or_continue()
	
    renew_list(True)

	#null = get_historical_price()
	
	# try to load all the coins bought by the bot if the file exists and is not empty
    coins_bought = {}

    if TEST_MODE: 
        file_prefix = 'test_'
    else:
        file_prefix = 'live_'

	# path to the saved coins_bought file
    coins_bought_file_path = file_prefix + COINS_BOUGHT

	# The below mod was stolen and altered from GoGo's fork, a nice addition for keeping a historical history of profit across multiple bot sessions.
	# path to the saved bot_stats file
    bot_stats_file_path = file_prefix + BOT_STATS

	# use separate files for testing and live trading
	#TRADES_LOG_FILE = file_prefix + TRADES_LOG_FILE
	#HISTORY_LOG_FILE = file_prefix + HISTORY_LOG_FILE
			
    bot_started_datetime = datetime.now().timestamp()
    total_capital_config = TRADE_SLOTS * TRADE_TOTAL

    if os.path.isfile(bot_stats_file_path) and os.stat(bot_stats_file_path).st_size!= 0:
        with open(bot_stats_file_path) as file:
            bot_stats = json.load(file)
			# load bot stats:
            try:
                
                bot_started_datetime = float(bot_stats['botstart_datetime'])
            except Exception as e:
                write_log(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.WARNING}Exception on reading botstart_datetime from {bot_stats_file_path}. Exception: {e}{txcolors.DEFAULT}')
                write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
                bot_started_datetime = datetime.now().timestamp()
				#if continue fails
                pass
			
            try:
                total_capital = bot_stats['total_capital']
            except Exception as e:
                write_log(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.WARNING}Exception on reading total_capital from {bot_stats_file_path}. Exception: {e}{txcolors.DEFAULT}')
                write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
                total_capital = TRADE_SLOTS * TRADE_TOTAL
                pass

            historic_profit_incfees_perc = float(bot_stats['historicProfitIncFees_Percent'])
            historic_profit_incfees_total = float(bot_stats['historicProfitIncFees_Total'])
            trade_wins = bot_stats['tradeWins']
            trade_losses = bot_stats['tradeLosses']
            session_USDT_EARNED = float(bot_stats['session_' + PAIR_WITH + '_EARNED'])
            session_USDT_LOSS = float(bot_stats['session_' + PAIR_WITH + '_LOSS'])
            session_USDT_WON = float(bot_stats['session_' + PAIR_WITH + '_WON'])
			
            if total_capital != total_capital_config:
                historic_profit_incfees_perc = (historic_profit_incfees_total / total_capital_config) * 100

	# rolling window of prices; cyclical queue
    historical_prices = [None] * (TIME_DIFFERENCE * RECHECK_INTERVAL)
    hsp_head = -1

	# if saved coins_bought json file exists and it's not empty then load it
    if os.path.isfile(coins_bought_file_path) and os.stat(coins_bought_file_path).st_size!= 0:
        with open(coins_bought_file_path) as file:
            coins_bought = json.load(file)

    print(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}Press Ctrl-C to stop the script. {txcolors.DEFAULT}')

    if not TEST_MODE:
        if not args.notimeout: # if notimeout skip this (fast for dev tests)
            write_log(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}WARNING: Test mode is disabled in the configuration, you are using _LIVE_ funds.{txcolors.DEFAULT}')
            print(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}WARNING: Waiting 10 seconds before live trading as a security measure!{txcolors.DEFAULT}')
            time.sleep(10) #Waiting 10 seconds before live trading

	#remove_external_signals('buy')
	#remove_external_signals('sell')
	#remove_external_signals('pause')

	#load_signal_threads()
    load_signal_threads()

	# seed initial prices
	#get_price() #main
    TIMEOUT_COUNT=0
    READ_CONNECTERR_COUNT=0
    BINANCE_API_EXCEPTION=0	
	
	#extract of code of OlorinSledge, Thanks
    thehour = datetime.now().hour  
    coins_sold = {}
    while is_bot_running:
        try:
            coins_sold = {}
            #show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())
            time_init = datetime.now()
            orders, last_price, volume = buy()

            update_portfolio(orders, last_price, volume)
			
            if SESSION_TPSL_OVERRIDE:
                check_total_session_profit(coins_bought, last_price)
				
            coins_sold = sell_coins()
            remove_from_portfolio(coins_sold)
            update_bot_stats()
			
            time_end = datetime.now()
            time_speed = time_end - time_init 
            print(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.WARNING}Time speed: {time_speed.total_seconds()} seconds{txcolors.DEFAULT}')
			#coins_sold = sell_coins()
			#remove_from_portfolio(coins_sold)
			#update_bot_stats()
			
            if FLAG_PAUSE == False:
				#extract of code of OlorinSledge, Thanks
                if RESTART_MODULES and thehour != datetime.now().hour :
                    stop_signal_threads()
                    load_signal_threads()
                    thehour = datetime.now().hour
                    print(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.WARNING}Modules Realoaded Completed{txcolors.DEFAULT}')
        except ReadTimeout as rt:
            TIMEOUT_COUNT += 1
            write_log(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}We got a timeout error from Binance. Re-loop. Connection Timeouts so far: {TIMEOUT_COUNT}{txcolors.DEFAULT}')
        except ConnectionError as ce:
            READ_CONNECTERR_COUNT += 1
            write_log(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}We got a connection error from Binance. Re-loop. Connection Errors so far: {READ_CONNECTERR_COUNT}{txcolors.DEFAULT}')
        except BinanceAPIException as bapie:
            BINANCE_API_EXCEPTION += 1
            write_log(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}We got an API error from Binance. Re-loop. API Errors so far: {BINANCE_API_EXCEPTION}.\nException:\n{bapie}{txcolors.DEFAULT}')											
        except KeyboardInterrupt as ki:
            if menu() == True: sys.exit(0)
    try:
        if not is_bot_running:
            if SESSION_TPSL_OVERRIDE:
                print(f'\n \n{txcolors.WARNING}{session_tpsl_override_msg}{txcolors.DEFAULT}')            
                sell_all(session_tpsl_override_msg, True)
                sys.exit(0)
            else:
                print(f'\n \n{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}Bot terminated for some reason.{txcolors.DEFAULT}')
    except Exception as e:
        write_log(f'{txcolors.WARNING}{languages_bot.MSG5[LANGUAGE]}: {txcolors.WARNING} Exception in main(): {e}{txcolors.DEFAULT}')
        write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
        pass
    except KeyboardInterrupt as ki:
        pass
