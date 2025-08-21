"""
Horacio Oscar Fanelli - Pantersxx3

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
import signal

import languages_bot
from megatronmod import analyze

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
#import signal

# used for directory handling
import glob

#discord needs import request
import requests

import socket

# Needed for colorful console output
from colorama import init
init()

# needed for the binance API / websockets / Exception handling
from binance.client import Client
from binance.exceptions import BinanceAPIException
#from binance.helpers import round_step_size
from requests.exceptions import ReadTimeout, ConnectionError

# used for dates
from datetime import date, datetime, timedelta
import time

# used to repeatedly execute the code
#from itertools import count

# used to store trades and sell assets
import json

#print output tables
from prettytable import PrettyTable, from_html_one, ALL

#for regex
import re

#read csv files
import csv

#pandas library
import pandas as pd
import pandas_ta as ta

# main module, contains some strategies
#from megatronmod_functions import list_indicators
#import tp_pausebotmod

#module to control the outputs of the bot
#import atexit

#print banner
from art import *

from bokeh.plotting import figure, output_file, show
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, HoverTool, NumeralTickFormatter

from progressbar import set_progress_bar, progressBar

from collections import defaultdict

from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Pool
from functools import partial

# Load helper modules
from helpers.parameters import (
	parse_args, load_config, save_config
)

# Load creds modules
from helpers.handle_creds import (
	load_correct_creds, test_api_key,
	load_discord_creds
)

# for colourful logging to the console
class txcolors:
	YELLOW = '\033[93m'
	BLUE = '\033[94m'
	GREEN = '\033[32m'
	DEFAULT = '\033[39m'
	RED = '\033[91m'
	WHITE = '\033[97m'

	#Cyan = '\033[96m'	
	#Magenta = '\033[95m'
	#Grey = '\033[90m'
	#Black = '\033[90m'
	#yelow = '\033[33m'

global session_profit_incfees_perc, session_profit_incfees_total, session_tpsl_override_msg, is_bot_running, session_USDT_EARNED, sell_all_coins
global session_USDT_LOSS, session_USDT_WON, last_msg_discord_balance_date, session_USDT_EARNED_TODAY, parsed_creds, TUP,PUP, TDOWN, c_data
global PDOWN, TNEUTRAL, PNEUTRAL, renewlist, DISABLE_TIMESTAMPS, signalthreads, VOLATILE_VOLUME_LIST, FLAG_PAUSE, coins_up,coins_down, client
global coins_unchanged, SHOW_TABLE_COINS_BOUGHT, USED_COMMISSIONS, PAUSEBOT_MANUAL, sell_specific_coin, lostconnection, FLAG_FILE_READ
global FLAG_FILE_WRITE, historic_profit_incfees_perc, historic_profit_incfees_total, trade_wins, trade_losses, bot_started_datetime, EXIT_BOT
global JSON_REPORT, FILE_SYMBOL_INFO, SAVED_COINS, coins_bought, bot_paused, parsed_config, creds_file, access_key, secret_key
global DEBUG, ENABLE_FUNCTION_NAME, SHOW_FUNCTION_NAME, SAVE_FUNCTION_NAME, SHOW_VARIABLES_AND_VALUE, SAVE_VARIABLES_AND_VALUE, TEST_MODE
global BACKTESTING_MODE, USE_TESNET_IN_ONLINEMODE, USE_SIGNALLING_MODULES, REMOTE_INSPECTOR_BOT_PORT, REMOTE_INSPECTOR_MEGATRONMOD_PORT
global SILENT_MODE, Test_Pos_Now, SpeedBot, POSITION

SAVED_COINS = {}
parsed_creds = []
secret_key = ""
access_key = ""
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
USED_COMMISSIONS = {}
PAUSEBOT_MANUAL = False
sell_specific_coin = False
sell_all_coins = False
lostconnection = False
signalthreads = []
c_data = pd.DataFrame([])
coins_bought = {}
EXIT_BOT = False
historic_profit_incfees_perc = 0.0
historic_profit_incfees_total = 0.0
trade_wins = 0
trade_losses = 0
bot_started_datetime = ""
function_variables = {}
commissionCoins = {}
Test_Pos_Now = ""
SpeedBot = 0.0
POSITION = {}

def convertir_a_str(value):
	if isinstance(value, dict):
		return str(value)
	elif isinstance(value, list):
		return str(value)
	elif isinstance(value, pd.DataFrame):
		return value.to_string()  # Convierte el DataFrame a texto legible
	else:
		return str(value)
		
# def handle_client(client_socket):
	# try:
		# global function_variables
		# while True:
			# request = client_socket.recv(1024).decode().strip() 
			# parts = request.split(".")
			# if len(parts) == 2:
				# funcion = parts[0]
				# variable = parts[1]

				# if variable == "all_val":
					# all_vars = "\n".join([f"{k}: {convertir_a_str(v)}" for k, v in function_variables[funcion].items()])
					# response = f"{funcion}:\n {all_vars}\n <END_COMMAND>"
				# else:
					# if funcion in function_variables and variable in function_variables[funcion]:
						# response = f"{funcion}.{variable}: {function_variables[funcion][variable]}\n<END_COMMAND>"
					# else:
						# response = f"Variable {variable} no encontrada en la función {funcion}\n<END_COMMAND>"
			# else:
				# response = "Comando no reconocido. Use 'funcion.variable'\n<END_COMMAND>"
			
			# client_socket.send(response.encode()) 
			
	# except Exception as e:
		# write_log(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.YELLOW}handle_client: {languages_bot.MSG1[LANGUAGE]}: {e}{txcolors.DEFAULT}')
		# write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
		# pass   
		
# def start_telnet_server():
	# try:
		# SIGNAL_NAME = "BOT"
		# if REMOTE_INSPECTOR_MEGATRONMOD_PORT > 0:
			# server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			# server.bind(('0.0.0.0', REMOTE_INSPECTOR_MEGATRONMOD_PORT))  # Escucha en todas las interfaces en el puerto 9999
			# server.listen(5)
			# print(f'{txcolors.SELL_PROFIT}{SIGNAL_NAME}: {txcolors.DEFAULT} Servidor Telnet: escuchando en el puerto 9999')

			# while True:
				# client_socket, addr = server.accept()
				# print(f'{txcolors.SELL_PROFIT}{SIGNAL_NAME}: {txcolors.DEFAULT} Servidor Telnet: Conexión aceptada desde {addr}')
				
				# # Crear un hilo separado para manejar la conexión
				# client_handler = threading.Thread(target=handle_client, args=(client_socket,))
				# client_handler.start()
	# except Exception as e:
		# write_log(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.YELLOW}start_telnet_server: {languages_bot.MSG1[LANGUAGE]}: {e}{txcolors.DEFAULT}')
		# write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
		# pass  
	
def is_fiat():
	# check if we are using a fiat as a base currency
	#global hsp_head
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
		global client

		balance = 0.0        
		if not TEST_MODE: #or not BACKTESTING_MODE:
			balance = float(client.get_asset_balance(asset=crypto)['free']) #get_balance_wallet
			
			#if balance < 10 and not TEST_MODE: #or not BACKTESTING_MODE:
				#print(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.YELLOW}{languages_bot.MSG34[LANGUAGE]}{txcolors.DEFAULT}')
				#sys.exit(0)
		show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())
	except Exception as e:
		write_log(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.YELLOW}get_balance_wallet: {languages_bot.MSG1[LANGUAGE]}: {e}{txcolors.DEFAULT}')
		write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
		pass
	return balance

def extract_first_record(csv_file):
	with open(csv_file, "r") as f:
		data_lines = (line for line in f if not line.strip().startswith("#"))
		reader = csv.reader(data_lines)
		first_row = next(reader)
		first_row = next(reader)
	return first_row[0]

def extract_last_record(csv_file):
	with open(csv_file, "r") as f:
		data_lines = (line for line in f if not line.strip().startswith("#"))
		csv_reader = csv.reader(data_lines)
		header = next(csv_reader)
		for row in csv_reader:
			pass
		last_row = row
	return last_row[0]
	
# def update_data_coin():
	# try:
		# global c_data
		# if USE_MOST_VOLUME_COINS == True:
			# TICKERS = 'volatile_volume_' + str(date.today()) + '.txt'
		# else:
			# TICKERS = 'tickers.txt'            
		# #for line in open(TICKERS, "r"):
		# #pairs=[line.strip() + PAIR_WITH for line in open(TICKERS, "r")]
		# with open(TICKERS, "r") as file:
			# lines = file.readlines() 
		# pairs = [line.strip() + PAIR_WITH for line in lines]
			
		# for coin in pairs:
			# filecsv = coin + ".csv"
			# if os.path.exists(filecsv) and TEST_MODE and not USE_TESNET_IN_ONLINEMODE:
				# fr1 = int(extract_first_record(filecsv))/1000
				# os1 = int(time.mktime(datetime.strptime(BACKTESTING_MODE_TIME_START, "%d/%m/%y %H:%M:%S").timetuple()) - 59940.0)
				# lr1 = int(extract_last_record(filecsv))/1000
				# oe1 = int(time.mktime(datetime.strptime(BACKTESTING_MODE_TIME_END, "%d/%m/%y %H:%M:%S").timetuple()))
				# if fr1 != os1 or lr1 != oe1:
					# os.remove(filecsv)
					# c_data = pd.DataFrame([])                

	# except Exception as e:
		# write_log(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}update_data_coin: {e}{txcolors.DEFAULT}')
		# write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
		# pass
def update_data_coin():
	try:
		global c_data, PAIR
		pairs = []
		if USE_MOST_VOLUME_COINS:
			TICKERS = f'volatile_volume_{date.today()}.txt'
			# Leer la lista de pares de trading
			with open(TICKERS, "r") as file:
				lines = file.readlines()
			pairs = [line.strip() + PAIR_WITH for line in lines if line.strip()]
		else:
			pairs = PAIR		

		for coin in pairs:
			coin = coin + PAIR_WITH
			filecsv = f"{coin}.csv"
			if os.path.exists(filecsv) and TEST_MODE and not USE_TESNET_IN_ONLINEMODE:
				# Leer primer y último timestamp del CSV
				fr1 = int(extract_first_record(filecsv)) / 1000
				lr1 = int(extract_last_record(filecsv)) / 1000

				# Calcular las fechas corregidas (incluyendo los 200 registros anteriores)
				start_original = time.mktime(datetime.strptime(BACKTESTING_MODE_TIME_START, "%d/%m/%y %H:%M:%S").timetuple())
				end = time.mktime(datetime.strptime(BACKTESTING_MODE_TIME_END, "%d/%m/%y %H:%M:%S").timetuple())

				# Determinar cuántos segundos hay en un intervalo de BOT_TIMEFRAME
				timeframe_seconds = {
					"1m": 60, "3m": 180, "5m": 300, "15m": 900, "30m": 1800, "1h": 3600,
					"2h": 7200, "4h": 14400, "6h": 21600, "8h": 28800, "12h": 43200, "1d": 86400,
					"3d": 259200, "1w": 604800, "1M": 2629800
				}
				interval_seconds = timeframe_seconds.get(BOT_TIMEFRAME, 60)  # Si no existe, usa 1m (60 seg)

				# Ajustar `start` para incluir 300 registros previos
				start_adjusted = start_original - (300 * interval_seconds)

				# Si los datos no coinciden con el intervalo deseado, eliminarlos y forzar nueva descarga
				if fr1 != start_adjusted or lr1 != end:
					os.remove(filecsv)
					c_data = pd.DataFrame([])

	except Exception as e:
		write_log(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}update_data_coin: {e}{txcolors.DEFAULT}')
		write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
		pass
		
# def download_data(coin):
	# try:
		# global client
		# c = pd.DataFrame([])
		# load_credentials(True)
		# create_conection_binance(True)
		# print(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}{languages_bot.MSG3[LANGUAGE]}...{txcolors.DEFAULT}')
		# end = time.mktime(datetime.strptime(BACKTESTING_MODE_TIME_END, "%d/%m/%y %H:%M:%S").timetuple()) #datetime.now()
		# start = time.mktime(datetime.strptime(BACKTESTING_MODE_TIME_START, "%d/%m/%y %H:%M:%S").timetuple()) - 59940.0 #pd.to_datetime(end - timedelta(days = 7))
		# data = client.get_historical_klines(str(coin), BOT_TIMEFRAME, int(start) * 1000, int(end) * 1000) #download_data
		# c = pd.DataFrame(data, columns=['time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume', 'Number of trades', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore'])
		# c = c.drop(c.columns[[5, 6, 7, 8, 9, 10, 11]], axis=1)
		# c.to_csv(coin + '.csv', index=False)
		# c = pd.DataFrame([])
		# show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())
		
	# except Exception as e:
		# write_log(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}download_data: {languages_bot.MSG1[LANGUAGE]} download_data(): {e}{txcolors.DEFAULT}')
		# write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
		# pass
def download_data(coin):
	try:
		global client
		c = pd.DataFrame([])
		load_credentials(True)
		create_conection_binance(True)
		print(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}{languages_bot.MSG3[LANGUAGE]}...{txcolors.DEFAULT}')

		end = time.mktime(datetime.strptime(BACKTESTING_MODE_TIME_END, "%d/%m/%y %H:%M:%S").timetuple())
		start_original = time.mktime(datetime.strptime(BACKTESTING_MODE_TIME_START, "%d/%m/%y %H:%M:%S").timetuple())

		timeframe_seconds = {
			"1m": 60, "3m": 180, "5m": 300, "15m": 900, "30m": 1800, "1h": 3600,
			"2h": 7200, "4h": 14400, "6h": 21600, "8h": 28800, "12h": 43200, "1d": 86400,
			"3d": 259200, "1w": 604800, "1M": 2629800
		}
		
		interval_seconds = timeframe_seconds.get(BOT_TIMEFRAME, 60)
		start_adjusted = start_original - (300 * interval_seconds)
		data = client.get_historical_klines(str(coin), BOT_TIMEFRAME, int(start_adjusted) * 1000, int(end) * 1000)

		c = pd.DataFrame(data, columns=['time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume', 'Number of trades', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore'])
		c = c.drop(c.columns[[6, 7, 8, 9, 10, 11]], axis=1)
		c.to_csv(coin + '.csv', index=False)
		
		c = pd.DataFrame([])
		show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())

	except Exception as e:
		write_log(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}download_data: {languages_bot.MSG1[LANGUAGE]} download_data(): {e}{txcolors.DEFAULT}')
		write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
		pass

def write_log_trades_strategys():
	try:
		lines = []		
		if os.path.exists(file_prefix + TRADES_LOG_FILE):
			with open(file_prefix + TRADES_LOG_FILE, "r") as f:
				lines = f.readlines()
				
		existe_buy_signal = False
		
		for line in lines:
			if line.strip().startswith("#"):
				existe_buy_signal = True
				break
				
		if not existe_buy_signal:
			lines_strategy = []	
			
			with open("megatronmod_strategy.py", "r") as f:
				lines_strategy = f.readlines()
				
			for line in lines_strategy:
				if "buySignal" in line and "False" not in line and "return" not in line and "#" not in line:
					data1 = line
				if "sellSignal" in line and "False" not in line and "return" not in line and "#" not in line:
					data2 = line
					
			lines_strategy = []
			
			with open(file_prefix + TRADES_LOG_FILE, "w") as f:
				f.write("#" + data1 + "#" + data2 + "\n" + ''.join(lines))	
				
	except Exception as e:
		write_log(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}write_log_trades_strategys: {languages_bot.MSG1[LANGUAGE]} download_data(): {e}{txcolors.DEFAULT}')
		write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
		pass

# def load_position(filename="positions.json"):
	# global POSITION
	# if os.path.exists(filename):
		# with open(filename, "r") as f:
			# POSITION = json.load(f)
		# print("Posiciones cargadas:", POSITION)
	# else:
		# POSITION = {}


# def save_position(filename="positions.json"):
	# global POSITION
	# with open(filename, "w") as f:
		# json.dump(POSITION, f, indent=4)
	# print("Posiciones guardadas en", filename)
	
# def write_position_csv(coin, position):
	# try:
		# global POSITION
		# POSITION[coin] = position
		# #with open(coin + '.position', 'w') as f:
			# #f.write(str(position).replace(".0", ""))
		# show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())
	# except Exception as e:
		# write_log(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.YELLOW}write_position_csv: {languages_bot.MSG1[LANGUAGE]} write_position_csv(): {e}{txcolors.DEFAULT}')
		# write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
		# pass

# def read_position_csv(coin):
	# try:
		# global POSITION
		# pos1 = POSITION[coin]
		# # pos1 = 0
		# # if os.path.exists(coin + '.position'):
			# # with open(coin + '.position', 'r') as f:
				# # r = f.read().replace(".0", "")
				# # pos1 = int(r)
		# show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())
	# except Exception as e:
		# write_log(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.YELLOW}read_position_csv: {languages_bot.MSG1[LANGUAGE]} read_position_csv(): {e}{txcolors.DEFAULT}')
		# write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
		# pass
	# return pos1

def load_positions():
	global POSITION
	_FILE = "positions.json"
	if os.path.exists(_FILE):
		with open(_FILE, "r") as f:
			data = json.load(f)
		POSITION = {str(k): int(v) for k, v in data.items()}
	#else:
		#POSITION = {}			

def save_positions(pos = {}):
	global POSITION
	_FILE = "positions.json"
	POSITION = pos
	if len(POSITION) > 0:
		snapshot = dict(POSITION)
		with open(_FILE, "w") as f:
			json.dump(snapshot, f, indent=2)
	
def read_next_row_csv(coin, nonext=False):
	try:
		global c_data, TRADES_LOG_FILE, POSITION
		price = 0
		time1 = 0

		file_prefix = prefix_type()

		if USE_SIGNALLING_MODULES:
			while not os.path.exists('ok.ok'):
				time.sleep(0.05) #read_next_row_csv
		
		if os.path.exists('positions.json') and len(POSITION) == 0 : 
			load_positions() #load_position()
		
		if coin in POSITION: #os.path.exists(coin + '.position'):
			pos1 = POSITION[coin] #read_position_csv(coin)

			if c_data.empty:
				c_data = pd.read_csv(coin + '.csv', dtype={'Close': float}, comment='#')
				c_data.columns = ['time', 'Open', 'High', 'Low', 'Close', 'Volume']

			if nonext:
				row = c_data[c_data['time'] == pos1]
			else:
				idx = c_data.index[c_data['time'] == pos1]
				if not idx.empty and idx[0] + 1 < len(c_data):
					row = c_data.iloc[[idx[0] + 1]]
				else:
					row = pd.DataFrame([])

			if not row.empty:
				time1 = int(row.iloc[0]['time'])
				price = float(row.iloc[0]['Close'])
			else:
				if not nonext:
					menu()
					
			POSITION[coin] = time1 #write_position_csv(coin, str(time1))

		else:
			if c_data.empty:
				c_data = pd.read_csv(coin + '.csv', dtype={'Close': float}, comment='#')
				c_data.columns = ['time', 'Open', 'High', 'Low', 'Close', 'Volume']
			row = c_data.iloc[301]
			price = float(row['Close'])
			time1 = int(row['time'])
			
			POSITION[coin] = time1
			save_positions(POSITION)			
			#write_log_trades_strategys()		

		if USE_SIGNALLING_MODULES:
			try:
				os.remove("ok.ok")
			except FileNotFoundError:
				pass

		show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())

	except Exception as e:
		write_log(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.YELLOW}read_next_row_csv: {languages_bot.MSG1[LANGUAGE]} read_next_row_csv(): {e}{txcolors.DEFAULT}')
		write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")

	return price, time1

# def read_next_row_csv(coin, nonext=False):
	# try:
		# global c_data
		# pos = 0
		# price = 0
		# time1 = 0        

		# file_prefix = prefix_type()
		
		# if USE_SIGNALLING_MODULES:
			# while not os.path.exists('ok.ok'):
				# time.sleep(1/1000)
			
		# if os.path.exists(coin + '.position'):
			# pos = read_position_csv(coin) 
			# if c_data.empty:
				# c_data = pd.read_csv(coin + '.csv')            
			# locate = False
			# for row in c_data.itertuples(index=False):
				# if locate:
					# time1 = row.time
					# price = row.Close
					# break
				# if row.time == pos:
					# if nonext:
						# time1 = row.time
						# price = row.Close
						# break
					# locate = True
			# if not locate and not nonext: menu() #sys.exit(0)
  
		# else:
			# c = pd.read_csv(coin + '.csv')
			# c.columns = ['time', 'Open', 'High', 'Low', 'Close']
			# c['Close'] = c['Close'].astype(float)
			# c = c.iloc[200]
			# price = float(c['Close'])
			# time1 = int(c['time'])
			# c = pd.DataFrame([]) 
			
		# write_position_csv(coin,str(time1))

		# if USE_SIGNALLING_MODULES: 
			# os.remove("ok.ok")
		# show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())
	# except Exception as e:
		# write_log(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.YELLOW}read_next_row_csv: {languages_bot.MSG1[LANGUAGE]} read_next_row_csv(): {e}{txcolors.DEFAULT}')
		# write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
		# pass
	# return price, time1        
				
def get_all_tickers(nonext=False):
	try:
		global client, Test_Pos_Now, PAIR
		pairs = []
		coins = []
		
		if USE_MOST_VOLUME_COINS == True:
			TICKERS = 'volatile_volume_' + str(date.today()) + '.txt'
			with open(TICKERS, "r") as file:
				lines = file.readlines() 
			pairs = [line.strip() + PAIR_WITH for line in lines if line.strip()]
		else:
			pairs = PAIR            
		#for line in open(TICKERS):
		#pairs=[line.strip() + PAIR_WITH for line in open(TICKERS, "r")]  		        
		
		for coin in pairs:
			coin = coin + PAIR_WITH
			if BACKTESTING_MODE or TEST_MODE:
				file = coin + '.csv'
				while not os.path.exists(file):
					download_data(coin)
				#sys.exit(1)
				#price, time = csv_bot.read_next_row_csv(coin) #get_all_tickers 
				price, time = read_next_row_csv(coin, nonext)
				Test_Pos_Now = datetime.fromtimestamp(time/1000).strftime("%d/%m/%y %H:%M:%S")
				#print(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {languages_bot.MSG6[LANGUAGE]} {BACKTESTING_MODE_TIME_START} - {txcolors.DEFAULT}{languages_bot.MSG7[LANGUAGE]}: {time} {datetime.fromtimestamp(time/1000).strftime("%d/%m/%y %H:%M:%S")}{txcolors.DEFAULT}')
				coins.append({ 'time': time, 'symbol': coin, 'price': price})
			else:
				c = pd.DataFrame([])
				klines = ""
				if "m" in BOT_TIMEFRAME: 
					back = 'min ago UTC'
				elif "h" in BOT_TIMEFRAME:
					back = 'hour ago UTC'
				elif "d" in BOT_TIMEFRAME:
					back = 'day ago UTC'
				elif "w" in BOT_TIMEFRAME:
					back = 'week ago UTC'
				elif "M" in BOT_TIMEFRAME:
					back = 'month ago UTC'				
				klines = client.get_historical_klines(symbol=coin, interval=BOT_TIMEFRAME, start_str=str(300) + back, limit=300) #get_all_tickers
				c = pd.DataFrame(klines)
				c.columns = ['time', 'Open', 'High', 'Low', 'Close', 'Volume', 'CloseTime', 'QuoteAssetVolume', 'Trades', 'TakerBuyBase', 'TakerBuyQuote', 'Ignore']
				c = c.drop(c.columns[[6, 7, 8, 9, 10, 11]], axis=1)
				c['time'] = pd.to_datetime(c['time'], unit='ms')
				c['Close'] = c['Close'].astype(float)
				coins.append({ 'time': c['time'].iloc[-1], 'symbol': coin, 'price': float(c['Close'].iloc[-1])}) #round(float(c['Close'].iloc[-1]),5)})
				c = pd.DataFrame([])
		show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())
	except Exception as e:
		write_log(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.YELLOW}get_all_tickers: {languages_bot.MSG1[LANGUAGE]} get_all_tickers():{coin} {e} klines {klines}{txcolors.DEFAULT}')
		write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
		pass        
	return coins
	
def get_price(add_to_historical=True, prices = []):
	try:
		'''Return the current price for all coins on binance'''
		#global historical_prices, hsp_head
		
		prices = []
		data = {}
		initial_price = {}

		if len(prices) > 0:
			prices = get_all_tickers(True) #get_price
		else:
			prices = get_all_tickers() #get_price
		
		renew_list()

		for coin in prices:
			if not USE_MOST_VOLUME_COINS:
				#tickers=[line.strip() for line in open(TICKERS_LIST, "r")]
				#with open(TICKERS_LIST, "r") as file:
					#lines = file.readlines()
				#tickers = PAIR #[line.strip() for line in lines if line.strip() if line.strip()]   
				for item1 in PAIR:
					if item1 + PAIR_WITH == coin['symbol'] and coin['symbol'].replace(PAIR_WITH, "") not in EXCLUDE_PAIRS:
						if BACKTESTING_MODE:
							initial_price[coin['symbol']] = { 'price': coin['price'], 'time': coin['time']}
						else:
							initial_price[coin['symbol']] = { 'price': coin['price'], 'time': datetime.now()} 
			else:
				today = "volatile_volume_" + str(date.today()) + ".txt"
				#VOLATILE_VOLUME_LIST=[line.strip() for line in open(today)]
				with open(today, "r") as file:
					lines = file.readlines()
				VOLATILE_VOLUME_LIST = [line.strip() for line in lines]
				for item1 in VOLATILE_VOLUME_LIST:
					if item1 + PAIR_WITH == coin['symbol'] and coin['symbol'].replace(PAIR_WITH, "") not in EXCLUDE_PAIRS:
						if BACKTESTING_MODE:
							initial_price[coin['symbol']] = { 'price': coin['price'], 'time': coin['time']}
						else:
							initial_price[coin['symbol']] = { 'price': coin['price'], 'time': datetime.now()} 

		# if add_to_historical:
			# hsp_head += 1
			# if hsp_head == RECHECK_INTERVAL:
				# hsp_head = 0
			# historical_prices[hsp_head] = initial_price
		show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())
	except Exception as e:
		#import languages_bot
		#import sys
		write_log(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.YELLOW}get_price: {languages_bot.MSG1[LANGUAGE]} get_price(): {e}{txcolors.DEFAULT}')
		write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
		pass

	return initial_price

def get_volume_list():
	try:
		today = "volatile_volume_" + str(date.today()) + ".txt"
		global COINS_MAX_VOLUME, COINS_MIN_VOLUME, VOLATILE_VOLUME, tickers, client
		volatile_volume_empty = False
		volatile_volume_time = False
		if USE_MOST_VOLUME_COINS:
			today = "volatile_volume_" + str(date.today()) + ".txt"
			now = datetime.now()
			now_str = now.strftime("%d-%m-%Y %H_%M_%S")
			dt_string = datetime.strptime(now_str,"%d-%m-%Y %H_%M_%S")
			if VOLATILE_VOLUME == "":
				volatile_volume_empty = True
			else:
				tuple1 = dt_string.timetuple()
				timestamp1 = time.mktime(tuple1)
				
				dt_string_old = datetime.strptime(VOLATILE_VOLUME.replace("(", " ").replace(")", "").replace("volatile_volume_", ""),"%d-%m-%Y %H_%M_%S") + timedelta(minutes = UPDATE_MOST_VOLUME_COINS)               
				tuple2 = dt_string_old.timetuple()
				timestamp2 = time.mktime(tuple2)                    
				
				if timestamp1 > timestamp2:
					volatile_volume_time = True
						
			if volatile_volume_empty or volatile_volume_time or not os.path.exists(today):             
				VOLATILE_VOLUME = "volatile_volume_" + str(dt_string)				
				most_volume_coins = {}
				tickers_all = []				
				prices = client.get_all_tickers() #get_volume_list
				
				for coin in prices:
					if coin['symbol'] == coin['symbol'].replace(PAIR_WITH, "") + PAIR_WITH:
						tickers_all.append(coin['symbol'].replace(PAIR_WITH, ""))

				c = 0
				if not os.path.exists(VOLATILE_VOLUME + ".txt"):
					load_settings()            
					print(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}{languages_bot.MSG35[LANGUAGE]}...{txcolors.DEFAULT}')
					if not COINS_MAX_VOLUME.isnumeric() and not COINS_MIN_VOLUME.isnumeric():
						infocoinMax = client.get_ticker(symbol=COINS_MAX_VOLUME + PAIR_WITH) #get_volume_list
						infocoinMin = client.get_ticker(symbol=COINS_MIN_VOLUME + PAIR_WITH) #get_volume_list
						COINS_MAX_VOLUME1 = float(infocoinMax['quoteVolume']) #math.ceil(float(infocoinMax['quoteVolume']))
						COINS_MIN_VOLUME1 = float(infocoinMin['quoteVolume'])
						most_volume_coins.update({COINS_MAX_VOLUME : COINS_MAX_VOLUME1})
						print(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}COINS_MAX_VOLUME {round(COINS_MAX_VOLUME1)} - COINS_MIN_VOLUME {round(COINS_MIN_VOLUME1)} {languages_bot.MSG8[LANGUAGE]}...{txcolors.DEFAULT}')
					
					for coin in tickers_all:
						#try:
						infocoin = client.get_ticker(symbol= coin + PAIR_WITH) #get_volume_list
						volumecoin = float(infocoin['quoteVolume']) #/ 1000000                
						if volumecoin <= COINS_MAX_VOLUME1 and volumecoin >= COINS_MIN_VOLUME1 and coin not in EXCLUDE_PAIRS and coin not in most_volume_coins:
							most_volume_coins.update({coin : volumecoin})  					
							c = c + 1
						# except Exception as e:
							# print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
							# continue
							
					if c <= 0: 
						print(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}{languages_bot.MSG9[LANGUAGE]}...{txcolors.DEFAULT}')
						menu() #sys.exit(0)
						
					sortedVolumeList = sorted(most_volume_coins.items(), key=lambda x: x[1], reverse=True)
					
					now = datetime.now()
					now_str = now.strftime("%d-%m-%Y(%H_%M_%S)")
					VOLATILE_VOLUME = "volatile_volume_" + now_str
					
					print(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}{languages_bot.MSG10[LANGUAGE]} {str(c)} {languages_bot.MSG11[LANGUAGE]} {today} ...{txcolors.DEFAULT}')
					
					for coin in sortedVolumeList:
						with open(today,'a+') as f:
							f.write(coin[0] + '\n')
					
					set_config("VOLATILE_VOLUME", VOLATILE_VOLUME)
				else:
					print(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}{languages_bot.MSG12[LANGUAGE]}{txcolors.DEFAULT}')
					print(f'{txcolors.YELLOW}{languages_bot.MSG14[LANGUAGE]}: {txcolors.DEFAULT}{languages_bot.MSG13[LANGUAGE]}...{txcolors.DEFAULT}')
			else:    
				VOLATILE_VOLUME = "volatile_volume_" + dt_string
				return VOLATILE_VOLUME
		# else:
			# #tickers=[line.strip() for line in open(TICKERS_LIST, "r")]
			# with open(TICKERS_LIST, "r") as file:
				# lines = file.readlines() 
			# pairs = [line.strip() for line in lines if line.strip()]
			
		show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())    
	except Exception as e:
		write_log(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.YELLOW}get_volume_list(): {languages_bot.MSG1[LANGUAGE]}: {e}{txcolors.DEFAULT}')
		write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}{txcolors.DEFAULT}")
		menu() #sys.exit(0)
	return VOLATILE_VOLUME

def print_table_commissions():
	try:
		global USED_COMMISSIONS, print_TABLE_COMMISSIONS
		printTable = False
		for coin in USED_COMMISSIONS:
			if USED_COMMISSIONS[coin] > 0:
				printTable = True
				break
		if printTable and print_TABLE_COMMISSIONS:
			my_table = PrettyTable()
			my_table.format = True
			my_table.border = True
			my_table.align = "c"
			my_table.valign = "m"
			my_table.left_padding_width = 1
			my_table. right_padding_width = 1
			my_table.title = f'{txcolors.YELLOW}Commisions{txcolors.DEFAULT}'
			#my_table.field_names = ['Pantersxx3']
			my_table.field_names = ["coin", "commission"]
			for coin, coin_commission in USED_COMMISSIONS.items():
				my_table.add_row([f"{coin}", f"{coin_commission:.6f}"])
			print(" " * 50 + my_table.get_string().replace("\n", "\n" + " " * 50))
			#print(my_table)
			my_table = PrettyTable()    
	except Exception as e:
		write_log(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.YELLOW}print_table_commissions: {languages_bot.MSG1[LANGUAGE]}: {e}{txcolors.DEFAULT}')
		write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
		lost_connection(e, "print_table_commissions")
		pass        
		
def print_table_coins_saved():
	try:
		global SAVED_COINS
		printTable = False
		for coin in SAVED_COINS:
			if SAVED_COINS[coin] > 0:
				printTable = True
				break
		if printTable and SELL_PART:
			my_table = PrettyTable()
			my_table.format = True
			my_table.border = True
			my_table.align = "c"
			my_table.valign = "m"
			my_table.left_padding_width = 1
			my_table. right_padding_width = 1
			my_table.title = f'{txcolors.YELLOW}Saved Coins{txcolors.DEFAULT}'
			#my_table.field_names = ['Pantersxx3']
			my_table.field_names = ["coin", "volume"]
			for coinsaved_coin, coinsaved_volume in SAVED_COINS.items():
				my_table.add_row([f"{coinsaved_coin}", f"{coinsaved_volume}"])
			print(" " * 50 + my_table.get_string().replace("\n", "\n" + " " * 50))
			#print(my_table)
			my_table = PrettyTable()    
	except Exception as e:
		write_log(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.YELLOW}print_table_coins_saved: {languages_bot.MSG1[LANGUAGE]}: {e}{txcolors.DEFAULT}')
		write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
		lost_connection(e, "print_table_coins_saved")
		pass
	
def print_table_coins_bought():
	try:
		global coins_bought, PAIR_WITH, SHOW_TABLE_COINS_BOUGHT
		if SHOW_TABLE_COINS_BOUGHT and len(coins_bought) > 0:
			my_table = PrettyTable()
			my_table.format = True
			my_table.border = True
			my_table.align = "c"
			my_table.valign = "m"
			my_table.left_padding_width = 1
			my_table.right_padding_width = 1
			my_table.field_names = [languages_bot.MSG15[LANGUAGE], languages_bot.MSG21[LANGUAGE], languages_bot.MSG16[LANGUAGE], languages_bot.MSG17[LANGUAGE], "TP %", "SL %", languages_bot.MSG18[LANGUAGE] + " %", languages_bot.MSG19[LANGUAGE] + " $", languages_bot.MSG20[LANGUAGE]]
			
			# Asumiendo que get_price no ha cambiado, si lo ha hecho, se debe modificar aquí
			last_price = get_price(False)

			for coin in list(coins_bought):
				if coin in last_price:
					LastPriceT = float(last_price[coin]['price'])
					BuyPriceT = float(coins_bought[coin]['bought_at'])
					PriceChange_PercT = float(((LastPriceT - BuyPriceT) / BuyPriceT) * 100)
					
					if MODE == "BACKTESTING":
						buy_time = datetime.fromtimestamp(coins_bought[coin]['timestamp'] / 1000)
						current_time = datetime.fromtimestamp(last_price[coin]['time'] / 1000)
						time_held = current_time - buy_time
					else:
						time_held = timedelta(seconds=datetime.now().timestamp() - int(str(coins_bought[coin]['timestamp'])[:10]))

					if SELL_ON_SIGNAL_ONLY:
						my_table.add_row([
							f"{txcolors.GREEN if PriceChange_PercT >= 0. else txcolors.RED}{coin.replace(PAIR_WITH,'')}{txcolors.DEFAULT}",
							f"{txcolors.GREEN if PriceChange_PercT >= 0. else txcolors.RED}{coins_bought[coin]['volume']:.4f}{txcolors.DEFAULT}",
							f"{txcolors.GREEN if PriceChange_PercT >= 0. else txcolors.RED}{BuyPriceT:.4f}{txcolors.DEFAULT}",
							f"{txcolors.GREEN if PriceChange_PercT >= 0. else txcolors.RED}{LastPriceT:.4f}{txcolors.DEFAULT}",
							f"{txcolors.GREEN if PriceChange_PercT >= 0. else txcolors.RED}per signal{txcolors.DEFAULT}",
							f"{txcolors.GREEN if PriceChange_PercT >= 0. else txcolors.RED}per signal{txcolors.DEFAULT}",
							f"{txcolors.GREEN if PriceChange_PercT >= 0. else txcolors.RED}{PriceChange_PercT:.2f}{txcolors.DEFAULT}",
							f"{txcolors.GREEN if PriceChange_PercT >= 0. else txcolors.RED}{((float(coins_bought[coin]['volume'])*float(coins_bought[coin]['bought_at']))*PriceChange_PercT)/100:.2f}{txcolors.DEFAULT}",
							f"{txcolors.GREEN if PriceChange_PercT >= 0. else txcolors.RED}{str(time_held).split('.')[0]}{txcolors.DEFAULT}"])
					else:
						my_table.add_row([
							f"{txcolors.GREEN if PriceChange_PercT >= 0. else txcolors.RED}{coin.replace(PAIR_WITH,'')}{txcolors.DEFAULT}",
							f"{txcolors.GREEN if PriceChange_PercT >= 0. else txcolors.RED}{coins_bought[coin]['volume']:.4f}{txcolors.DEFAULT}",
							f"{txcolors.GREEN if PriceChange_PercT >= 0. else txcolors.RED}{BuyPriceT:.4f}{txcolors.DEFAULT}",
							f"{txcolors.GREEN if PriceChange_PercT >= 0. else txcolors.RED}{LastPriceT:.4f}{txcolors.DEFAULT}",
							f"{txcolors.GREEN if PriceChange_PercT >= 0. else txcolors.RED}{coins_bought[coin]['take_profit']:.2f}{txcolors.DEFAULT}",
							f"{txcolors.GREEN if PriceChange_PercT >= 0. else txcolors.RED}{coins_bought[coin]['stop_loss']:.2f}{txcolors.DEFAULT}",
							f"{txcolors.GREEN if PriceChange_PercT >= 0. else txcolors.RED}{PriceChange_PercT:.2f}{txcolors.DEFAULT}",
							f"{txcolors.GREEN if PriceChange_PercT >= 0. else txcolors.RED}{((float(coins_bought[coin]['volume'])*float(coins_bought[coin]['bought_at']))*PriceChange_PercT)/100:.2f}{txcolors.DEFAULT}",
							f"{txcolors.GREEN if PriceChange_PercT >= 0. else txcolors.RED}{str(time_held).split('.')[0]}{txcolors.DEFAULT}"])

			# En lugar de print con padding, se imprime directamente
			#print(my_table)
			#my_table = PrettyTable()
			return my_table.get_string()
	except Exception as e:
		write_log(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.YELLOW}print_table_coins_bought: {languages_bot.MSG1[LANGUAGE]}: {e}{txcolors.DEFAULT}')
		write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
		lost_connection(e, "print_table_coins_bought")
		pass
	
# def print_table_coins_bought():
	# try:
		# global coins_bought
		# if SHOW_TABLE_COINS_BOUGHT:
			# if len(coins_bought) > 0:
				# my_table = PrettyTable()
				# my_table.format = True
				# my_table.border = True
				# my_table.align = "c"
				# my_table.valign = "m"
				# my_table.left_padding_width = 1
				# my_table. right_padding_width = 1
				# my_table.field_names = [languages_bot.MSG15[LANGUAGE], languages_bot.MSG21[LANGUAGE], languages_bot.MSG16[LANGUAGE], languages_bot.MSG17[LANGUAGE], "TP %", "SL %", languages_bot.MSG18[LANGUAGE] + " %", languages_bot.MSG19[LANGUAGE] + " $", languages_bot.MSG20[LANGUAGE]]
				# last_price = get_price(False) #print_table_coins_bought
				# for coin in list(coins_bought):
					# LastPriceT = float(last_price[coin]['price'])#,8)
					# BuyPriceT = float(coins_bought[coin]['bought_at'])#,8)
					# PriceChange_PercT = float(((LastPriceT - BuyPriceT) / BuyPriceT) * 100)
					
					# if MODE == "BACKTESTING":
						# buy_time = datetime.fromtimestamp(coins_bought[coin]['timestamp'] / 1000)
						# current_time = datetime.fromtimestamp(last_price[coin]['time'] / 1000) 
						# time_held = current_time - buy_time 
					# else:
						# time_held = timedelta(seconds=datetime.now().timestamp() - int(str(coins_bought[coin]['timestamp'])[:10]))
				
					# if SELL_ON_SIGNAL_ONLY:
						# my_table.add_row([f"{txcolors.GREEN if PriceChange_PercT >= 0. else txcolors.RED}{coin.replace(PAIR_WITH,'')}{txcolors.DEFAULT}", f"{txcolors.GREEN if PriceChange_PercT >= 0. else txcolors.RED}{coins_bought[coin]['volume']:.4f}{txcolors.DEFAULT}", f"{txcolors.GREEN if PriceChange_PercT >= 0. else txcolors.RED}{BuyPriceT:.4f}{txcolors.DEFAULT}", f"{txcolors.GREEN if PriceChange_PercT >= 0. else txcolors.RED}{LastPriceT:.4f}{txcolors.DEFAULT}", f"{txcolors.GREEN if PriceChange_PercT >= 0. else txcolors.RED}per signal{txcolors.DEFAULT}", f"{txcolors.GREEN if PriceChange_PercT >= 0. else txcolors.RED}per signal{txcolors.DEFAULT}", f"{txcolors.GREEN if PriceChange_PercT >= 0. else txcolors.RED}{PriceChange_PercT:.2f}{txcolors.DEFAULT}", f"{txcolors.GREEN if PriceChange_PercT >= 0. else txcolors.RED}{((float(coins_bought[coin]['volume'])*float(coins_bought[coin]['bought_at']))*PriceChange_PercT)/100:.2f}{txcolors.DEFAULT}", f"{txcolors.GREEN if PriceChange_PercT >= 0. else txcolors.RED}{str(time_held).split('.')[0]}{txcolors.DEFAULT}"])
					# else:
						# my_table.add_row([f"{txcolors.GREEN if PriceChange_PercT >= 0. else txcolors.RED}{coin.replace(PAIR_WITH,'')}{txcolors.DEFAULT}", f"{txcolors.GREEN if PriceChange_PercT >= 0. else txcolors.RED}{coins_bought[coin]['volume']:.4f}{txcolors.DEFAULT}", f"{txcolors.GREEN if PriceChange_PercT >= 0. else txcolors.RED}{BuyPriceT:.4f}{txcolors.DEFAULT}", f"{txcolors.GREEN if PriceChange_PercT >= 0. else txcolors.RED}{LastPriceT:.4f}{txcolors.DEFAULT}", f"{txcolors.GREEN if PriceChange_PercT >= 0. else txcolors.RED}{coins_bought[coin]['take_profit']:.2f}{txcolors.DEFAULT}", f"{txcolors.GREEN if PriceChange_PercT >= 0. else txcolors.RED}{coins_bought[coin]['stop_loss']:.2f}{txcolors.DEFAULT}", f"{txcolors.GREEN if PriceChange_PercT >= 0. else txcolors.RED}{PriceChange_PercT:.2f}{txcolors.DEFAULT}", f"{txcolors.GREEN if PriceChange_PercT >= 0. else txcolors.RED}{((float(coins_bought[coin]['volume'])*float(coins_bought[coin]['bought_at']))*PriceChange_PercT)/100:.2f}{txcolors.DEFAULT}", f"{txcolors.GREEN if PriceChange_PercT >= 0. else txcolors.RED}{str(time_held).split('.')[0]}{txcolors.DEFAULT}"])

				# print(" " * 9 + my_table.get_string().replace("\n", "\n" + " " * 9))
				# #print(my_table)
				# my_table = PrettyTable()
		# show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())
	# except Exception as e:
		# write_log(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.YELLOW}print_table_coins_bought: {languages_bot.MSG1[LANGUAGE]}: {e}{txcolors.DEFAULT}')
		# write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
		# lost_connection(e, "print_table_coins_bought")
		# pass

def clear():
	name = os.name
	if name == 'nt':
		_ = os.system('cls')  
	else:
		_ = os.system('clear')

def convert_hhmmss():
	try:
		global bot_started_datetime
		sec = datetime.now().timestamp() - bot_started_datetime
		hours = sec // 3600
		minutes = (sec % 3600) // 60
		segundos = sec % 60
		str_time = str(truncate(hours)) + ":" + str(truncate(minutes)) + ":" + str(truncate(segundos))
	except Exception as e:
		write_log(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.YELLOW}convert_hhmmss: {languages_bot.MSG1[LANGUAGE]}: {e}{txcolors.DEFAULT}')
		write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
		pass
	return str_time

def balance_report(last_price):
	try:
		global TRADE_TOTAL, trade_wins, trade_losses, session_profit_incfees_perc, session_profit_incfees_total
		global last_price_global, session_USDT_EARNED, session_USDT_LOSS, session_USDT_WON, TUP, TDOWN, TNEUTRAL
		global session_USDT_LOSS, SAVED_COINS, coins_bought, Test_Pos_Now, SpeedBot, PAIR

		unrealised_session_profit_incfees_perc = 0
		unrealised_session_profit_incfees_total = 0
		msg1 = ""
		msg2 = "" 
		pair = ""
		BUDGET = TRADE_SLOTS * get_balance_test_mode() #balance_report
		exposure_calcuated = 0
		# if TRADE_SLOTS == 1:
			# if USE_MOST_VOLUME_COINS == True:
				# TICKERS = 'volatile_volume_' + str(date.today()) + '.txt'
			# else:
				# TICKERS = PAIR
			# #pair=str([line.strip() for line in open(TICKERS, "r")]).replace("[","").replace("]", "").replace("'", "")
			# with open(TICKERS, "r") as file:
				# pair = ", ".join(line.strip() for line in file)
		
		for coin in list(coins_bought):
			LastPriceBR = float(last_price[coin]['price'])
			#sellFeeBR = (LastPriceBR * (TRADING_FEE/100))			
			BuyPriceBR = float(coins_bought[coin]['bought_at'])
			#buyFeeBR = (BuyPriceBR * (TRADING_FEE/100))
			exposure_calcuated = exposure_calcuated + round(float(coins_bought[coin]['bought_at']) * float(coins_bought[coin]['volume']),0)
			#PriceChangeIncFees_TotalBR = float(((LastPriceBR - sellFeeBR) - (BuyPriceBR + buyFeeBR)) * coins_bought[coin]['volume'])
			#unrealised_session_profit_incfees_total = float(unrealised_session_profit_incfees_total + PriceChangeIncFees_TotalBR)

		# if unrealised_session_profit_incfees_total == 0 or BUDGET == 0: 
			# unrealised_session_profit_incfees_perc = 0
		# else:
			# unrealised_session_profit_incfees_perc = (unrealised_session_profit_incfees_total / BUDGET) * 100

		DECIMALS = int(decimals())
		CURRENT_EXPOSURE = round(exposure_calcuated, 0)
		INVESTMENT_TOTAL = round((get_balance_test_mode() * TRADE_SLOTS), DECIMALS) #balance_report
		
		# truncating some of the above values to the correct decimal places before printing
		WIN_LOSS_PERCENT = 0
		if (trade_wins > 0) and (trade_losses > 0):
			WIN_LOSS_PERCENT = round((trade_wins / (trade_wins+trade_losses)) * 100, 2)
		if (trade_wins > 0) and (trade_losses == 0):
			WIN_LOSS_PERCENT = 100
		strplus = "+"
		#print_banner()
		#if STATIC_MAIN_INFO == True: clear()
		my_table = PrettyTable()
		my_table.title = f'{txcolors.YELLOW}BINANCE TRADING BOT{txcolors.DEFAULT}'
		my_table.field_names = ['Pantersxx3']
		my_table.format = True
		my_table.border = True
		my_table.align = "c"
		my_table.valign = "m"
		my_table.header = True
		my_table.hrules = ALL
		my_table.padding_width = 3
		TRADETOTAL = round(session_USDT_EARNED + TRADE_TOTAL,3)
		if MODE == "BACKTESTING":
			my_table.add_row([f'{txcolors.DEFAULT}{languages_bot.MSG22[LANGUAGE]}: {txcolors.BLUE}{BACKTESTING_MODE_TIME_START}{txcolors.DEFAULT} | {languages_bot.MSG40[LANGUAGE]}: {txcolors.BLUE} {BACKTESTING_MODE_TIME_END}{txcolors.DEFAULT} | {languages_bot.MSG23[LANGUAGE]}: {txcolors.BLUE}{convert_hhmmss()}{txcolors.DEFAULT} | {languages_bot.MSG24[LANGUAGE]}: {txcolors.BLUE}{str(bot_paused)}{txcolors.DEFAULT} | {languages_bot.MSG25[LANGUAGE]}: {txcolors.BLUE}{TEST_MODE}{txcolors.DEFAULT} | {languages_bot.MSG26[LANGUAGE]}: {txcolors.BLUE}{BACKTESTING_MODE}{txcolors.DEFAULT}'])        
		else:
			my_table.add_row([f'{txcolors.DEFAULT}{languages_bot.MSG22[LANGUAGE]}: {txcolors.BLUE}{datetime.fromtimestamp(bot_started_datetime).strftime("%d/%m/%y %H:%M:%S").split(".")[0]}{txcolors.DEFAULT} | {languages_bot.MSG23[LANGUAGE]}: {txcolors.BLUE}{convert_hhmmss()}{txcolors.DEFAULT} | {languages_bot.MSG24[LANGUAGE]}: {txcolors.BLUE}{str(bot_paused)}{txcolors.DEFAULT} | {languages_bot.MSG25[LANGUAGE]}: {txcolors.BLUE}{TEST_MODE}{txcolors.DEFAULT} | {languages_bot.MSG26[LANGUAGE]}: {txcolors.BLUE}{BACKTESTING_MODE}{txcolors.DEFAULT}'])        
		#{txcolors.DEFAULT}{languages_bot.MSG29[LANGUAGE]}/{languages_bot.MSG31[LANGUAGE]}: {txcolors.GREEN}{str(trade_wins)}{txcolors.DEFAULT}/{txcolors.RED}{str(trade_losses)}{txcolors.DEFAULT} | 
		#| {languages_bot.MSG29[LANGUAGE]} %: {txcolors.GREEN if WIN_LOSS_PERCENT > 0. else txcolors.RED}{float(WIN_LOSS_PERCENT):g}%{txcolors.DEFAULT} 
		my_table.add_row([f'{txcolors.DEFAULT} TIMEFRAME: {txcolors.BLUE}{BOT_TIMEFRAME}{txcolors.DEFAULT} | {languages_bot.MSG27[LANGUAGE]}: {txcolors.BLUE}{str(round(get_balance_wallet(PAIR_WITH),2))}{txcolors.DEFAULT} | {languages_bot.MSG28[LANGUAGE]}: {txcolors.BLUE}{str(len(coins_bought))}{txcolors.DEFAULT}/{txcolors.BLUE}{str(TRADE_SLOTS)} {int(CURRENT_EXPOSURE)}{txcolors.DEFAULT}/{txcolors.BLUE}{int(INVESTMENT_TOTAL)} {txcolors.DEFAULT}{PAIR_WITH}{txcolors.DEFAULT} | {languages_bot.MSG30[LANGUAGE]}: {txcolors.BLUE}{trade_wins+trade_losses}{txcolors.DEFAULT}'])
		if session_USDT_EARNED > 0: 
			my_table.add_row([f'{txcolors.DEFAULT}TOTAL: {txcolors.GREEN if TRADETOTAL > 0. else txcolors.RED}{str(TRADETOTAL)} {txcolors.DEFAULT}{PAIR_WITH} | {txcolors.DEFAULT}{languages_bot.MSG31[LANGUAGE]}: {txcolors.RED}{str(format(float(session_USDT_LOSS), ".4f"))}{txcolors.DEFAULT} {PAIR_WITH} | {txcolors.DEFAULT}{languages_bot.MSG32[LANGUAGE]}: {txcolors.GREEN}{str(format(float(session_USDT_WON), ".4f"))}{txcolors.DEFAULT} {PAIR_WITH} | {languages_bot.MSG19[LANGUAGE].upper()} %: {txcolors.GREEN if (session_USDT_EARNED * 100)/INVESTMENT_TOTAL > 0. else txcolors.RED}{round((session_USDT_EARNED * 100)/INVESTMENT_TOTAL,3)}%{txcolors.DEFAULT}'])
		else:
			my_table.add_row([f'{txcolors.DEFAULT}TOTAL: {txcolors.GREEN if TRADETOTAL > 0. else txcolors.RED}{str(TRADETOTAL)} {txcolors.DEFAULT}{PAIR_WITH} | {txcolors.DEFAULT}{languages_bot.MSG31[LANGUAGE]}: {txcolors.RED}{str(format(float(session_USDT_LOSS), ".4f"))}{txcolors.DEFAULT} {PAIR_WITH} | {txcolors.DEFAULT}{languages_bot.MSG32[LANGUAGE]}: {txcolors.GREEN}{str(format(float(session_USDT_WON), ".4f"))}{txcolors.DEFAULT} {PAIR_WITH} | {languages_bot.MSG19[LANGUAGE].upper()} %: {txcolors.GREEN if (session_USDT_EARNED) > 0. else txcolors.RED}{round(0,3)}%{txcolors.DEFAULT}'])
		print("\n")
		coins_table_str = print_table_coins_bought()
		if MODE == "BACKTESTING":
			my_table.add_row([Test_Pos_Now + " - " + str(round(SpeedBot,3)) + "s/c"])
		else:
			my_table.add_row([str(round(SpeedBot,3)) + "s/c"])			
		my_table.add_row([coins_table_str])
		print(my_table)
		my_table = PrettyTable()
		#print_table_coins_bought()
		print_table_coins_saved()
		print_table_commissions()
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
		show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())
	except Exception as e:
		write_log(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.YELLOW}balance_report(): {languages_bot.MSG1[LANGUAGE]}: {e}{txcolors.DEFAULT}')
		write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
		pass
	
	return msg1 + msg2

def prefix_type():
	try:
		global TEST_MODE
		if TEST_MODE:
			fileprefix = 'test_'
		if not TEST_MODE:
			fileprefix = 'live_'
	except Exception as e:
		write_log(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.YELLOW}balance_report(): {languages_bot.MSG1[LANGUAGE]}: {e}{txcolors.DEFAULT}')
		write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
		pass
		
	return fileprefix
	
def write_log(logline, show=True, showtime=False, logfile=""):
	global LOG_FILE, LANGUAGE
	try:
		timestamp = datetime.now().strftime("%d/%m/%y %H:%M:%S")
		file_prefix = prefix_type()
		 
		if logfile == "": 
			logfile = file_prefix + LOG_FILE
		
		with open(logfile,'a') as f:
			ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
			result = ansi_escape.sub('', logline)
			if showtime:
				f.write(timestamp + ' ' + result + '\n')
			else:
				f.write(result + '\n')
		if show:
			print(f'{logline}')
	except Exception as e:
		print(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.YELLOW}write_log(): {languages_bot.MSG1[LANGUAGE]}: {e}{txcolors.DEFAULT}')
		print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
		menu() #sys.exit(0)
		
def read_log_trades(OrderID):
	try:
		ret = ""
		file_prefix = prefix_type()

		with open(file_prefix + TRADES_LOG_FILE, "r") as f:
			data_lines = (line for line in f if not line.strip().startswith("#"))
			csv_readed = csv.reader(data_lines)
			header = next(csv_readed)
			for row in csv_readed:
				if row[1] == OrderID:
						ret = row[6]
	except Exception as e:
		write_log(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.YELLOW}read_log_trades(): {languages_bot.MSG1[LANGUAGE]}: {e}{txcolors.DEFAULT}')
		write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
		pass
	return ret 

def defaultdict_from_dict(d):
	nd = lambda: defaultdict(nd)
	ni = nd()
	ni.update(d)
	return ni 

def extract_value_indicator(line):
	matches = []
	pattern = r'\((.*?)\)'
	matches = re.findall(pattern, line)
	return matches
	
def make_indicators(df):
	try:
		global TRADES_INDICATORS
		tradesindicators = prefix_type() + TRADES_INDICATORS.replace(".csv", "")
		list_indicators = []
		indicators = []
		with open("megatronmod_strategy.py", "r") as f:
			lines = f.readlines()
		for line in lines:
			if "buySignal" in line and "False" not in line and "return" not in line and "#" not in line:
				data1 = line
			if "sellSignal" in line and "False" not in line and "return" not in line and "#" not in line:
				data2 = line				
					
		for line in lines:
			if "Bollinger_Bands" in line and not "#" in line:
				df1 = pd.DataFrame()
				valores = extract_value_indicator(line)[0].split(', ')
				value1 = int(valores[1])
				value2 = int(valores[2])
				df1['time'] = df['time'] 
				df1[['bollinger_lower', 'bollinger_middle', 'bollinger_upper', 'bandwidth', 'percentcolumns']] = ta.bbands(df['Close'], length=value1, std=value2).fillna(0)
				df1 = df1[(df1 != 0).all(axis=1)]
				df1 = df1.drop('bandwidth', axis=1)
				df1 = df1.drop('percentcolumns', axis=1)
				df1.to_csv(tradesindicators + '_bollinger_bands.csv', index=False)
			elif "Cci" in line and not "#" in line:
				df1 = pd.DataFrame()
				valores = extract_value_indicator(line)[0].split(', ')
				value1 = int(valores[1]) 
				df1['time'] = df['time'] 
				df1[['cci']] = ta.cci(length=LENGHT)(df['Close'], length=value1).fillna(0)
				df1 = df1[(df1 != 0).all(axis=1)]
				df1.to_csv(tradesindicators + '_cci.csv', index=False)
			# elif "Cross" in line and not "#" in line:
				# df1 = pd.DataFrame()
				# valores = extract_value_indicator(line)[0].split(', ')
				# value1 = int(valores[1])
				# value2 = int(valores[2])
				
				# df1['date_time'] = df['date_time'] 
				# df1.to_csv('cross.csv', index=False)
			# elif "Crossover" in line and not "#" in line:
				# df1 = pd.DataFrame()
				# valores = extract_value_indicator(line)[0].split(', ')
				# value1 = int(valores[1])
				# value2 = int(valores[2])
				
				# df1['date_time'] = df['date_time'] 
				# df1.to_csv('crossover.csv', index=False)
			# elif "Crossunder" in line and not "#" in line:
				# df1 = pd.DataFrame()
				# valores = extract_value_indicator(line)[0].split(', ')
				# value1 = int(valores[1])
				# value2 = int(valores[2])

				# df1['date_time'] = df['date_time'] 
				# df1.to_csv('crossunder.csv', index=False)
			elif "Ema" in line and not "#" in line:
				df1 = pd.DataFrame()
				valores = extract_value_indicator(line)[0].split(', ')
				value1 = int(valores[1])
				df1['time'] = df['time'] 
				df1[['ema']] = ta.ema(df['Close'], length=value1).fillna(0)
				df1 = df1[(df1 != 0).all(axis=1)]
				df1.to_csv(tradesindicators + '_ema.csv', index=False)
			elif "Heikinashi" in line and not "#" in line:
				df1 = pd.DataFrame()
				df1['time'] = df['time']
				df1[['ha_open', 'ha_high', 'ha_low', 'ha_close']] = ta.ha(df['Open'], df['High'], df['Low'], df['Close']).fillna(0)
				df1 = df1[(df1 != 0).all(axis=1)]
				df1.to_csv(tradesindicators + '_heikinashi.csv', index=False)
			elif "Hma" in line and not "#" in line:
				df1 = pd.DataFrame()
				valores = extract_value_indicator(line)[0].split(', ')
				value1 = int(valores[1])
				df1['time'] = df['time']
				df1[['hma']] = ta.hma(DF_Data['Close'], value1).fillna(0)
				df1 = df1[(df1 != 0).all(axis=1)]
				df1.to_csv(tradesindicators + '_hma.csv', index=False)
			elif "Ichimoku" in line and not "#" in line:
				df1 = pd.DataFrame()
				valores = extract_value_indicator(line)[0].split(', ')
				value1 = int(valores[1])
				value2 = int(valores[2])
				value3 = int(valores[3])
				df1['time'] = df['time']
				df1[['spanA', 'spanB', 'tenkan_sen', 'kijun_sen', 'chikou_span']] = ta.ichimoku(df['High'], df['Low'], df['Close'], value1, value2, value3).fillna(0)
				df1 = df1[(df1 != 0).all(axis=1)]
				df1.to_csv(tradesindicators + '_ichimoku.csv', index=False)
			elif "Macd" in line and not "#" in line:
				df1 = pd.DataFrame()
				valores = extract_value_indicator(line)[0].split(', ')
				value1 = int(valores[1])
				value2 = int(valores[2])
				value3 = int(valores[3])
				df1['time'] = df['time'] 
				df1[['macd', 'macdhist', 'macdsig']] = ta.macd(df['Close'],value1, value2, value3).fillna(0)
				df1 = df1[(df1 != 0).all(axis=1)]
				df1.to_csv(tradesindicators + '_macd.csv', index=False)
			elif "Momentum" in line and not "#" in line:
				df1 = pd.DataFrame()
				valores = extract_value_indicator(line)[0].split(', ')
				value1 = int(valores[1])
				df1['time'] = df['time']
				df1[['momentum']] = ta.mom(df['Close'], timeperiod=value1).fillna(0)
				df1 = df1[(df1 != 0).all(axis=1)]
				df1.to_csv(tradesindicators + '_momentum.csv', index=False)
			elif "Rsi" in line and not "#" in line:
				df1 = pd.DataFrame()
				valores = extract_value_indicator(line)[0].split(', ')
				value1 = int(valores[1])
				df1['time'] = df['time']
				df1[['rsi']] = ta.rsi(df['Close'], value1).fillna(0)
				df1 = df1[(df1 != 0).all(axis=1)]
				df1.to_csv(tradesindicators + '_rsi.csv', index=False)
			elif "Sma" in line and not "#" in line:
				df1 = pd.DataFrame()
				valores = extract_value_indicator(line)[0].split(', ')
				value1 = int(valores[1])
				df1['SMA_200'] = ta.sma(df['Close'],length=value1).fillna(0)
				df1['time'] = df['time']
				df1 = df1[(df1 != 0).all(axis=1)]
				df1.to_csv(tradesindicators + '_sma.csv', index=False)
			elif "Stochastic" in line and not "#" in line:
				df1 = pd.DataFrame()
				valores = extract_value_indicator(line)[0].split(', ')
				value1 = int(valores[1])
				value2 = int(valores[2])
				value3 = int(valores[3])
				df1['time'] = df['time'] 
				df1[['k', 'd']] = ta.stoch(df['High'], df['Low'], df['Close'], value1, value2, value3).fillna(0)
				df1 = df1[(df1 != 0).all(axis=1)]
				df1.to_csv(tradesindicators + '_stochastic.csv', index=False)
			elif "Supertrend" in line and not "#" in line:
				df1 = pd.DataFrame()
				valores = extract_value_indicator(line)[0].split(', ')
				value1 = int(valores[1])
				value2 = int(valores[2])
				df1['time'] = df['time'] 
				df1[['supertrend', 'supertrend_direc', 'supertrend_down', 'supertrend_up']] = ta.supertrend(pd.to_numeric(df['High']), pd.to_numeric(df['Low']), pd.to_numeric(df['Close']), length=value1, multiplier=value2).fillna(0)
				df1 = df1[(df1 != 0).all(axis=1)]
				df1.to_csv(tradesindicators + '_supertrend.csv', index=False)
			elif "Wma" in line and not "#" in line:
				df1 = pd.DataFrame()
				valores = extract_value_indicator(line)[0].split(', ')
				value1 = int(valores[1])
				df1['time'] = df['time'] 
				df1[['wma']] = ta.wma(df['Close'], value1).fillna(0)
				df1 = df1[(df1 != 0).all(axis=1)]
				df1.to_csv(tradesindicators + '_wma.csv', index=False)
			elif "Zigzag" in line and not "#" in line:
				df1 = pd.DataFrame()
				valores = extract_value_indicator(line)[0].split(', ')
				value1 = int(valores[1])
				df1['time'] = df['time'] 
				df1['zigzag'] = ta.zigzag(high=df['High'], low=df['Low'], close=df['Close'], depth=value1).fillna(0)
				df1 = df1[(df1 != 0).all(axis=1)]
				df1.to_csv(tradesindicators + '_zigzag.csv', index=False)
			
	except Exception as e:
		write_log(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.YELLOW}make_indicators(): {languages_bot.MSG1[LANGUAGE]}: {e}{txcolors.DEFAULT}')
		write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
		pass

def obtener_color_aleatorio():
  hex_color = "#" + ''.join([choice('0123456789ABCDEF') for j in range(6)])
  return hex_color
  
def make_graphics():
	try:
		global PAIR
		prefix = prefix_type()
		tradesindicators = prefix + TRADES_INDICATORS.replace(".csv", "") + "_"
		output_file(prefix + TRADES_GRAPH)
		
		if TEST_MODE:
			if USE_MOST_VOLUME_COINS:
				TICKERS = f'volatile_volume_{date.today()}.txt'
				pairs = [line.strip() + PAIR_WITH for line in open(TICKERS)]
			else:
				pairs = PAIR 		
			
			for coin in pairs:
				coin = coin + PAIR_WITH
				transactions = pd.read_csv(prefix + TRADES_LOG_FILE, comment='#')
				#transactions['Datetime'] = pd.to_datetime(transactions['Datetime'], unit='ms')
				
				df1 = pd.read_csv(coin + ".csv").fillna(0)
				df1['time'] = pd.to_datetime(df1['time'], unit='ms')
				
				make_indicators(df1)

				extension = f"/{tradesindicators}*.csv"
				files = [item for sublist in [glob.glob(ext) for ext in [os.path.dirname(__file__) + extension]] for item in sublist]
				
				p = figure(title=f"Price Chart for {coin}", x_axis_label="Date", y_axis_label="Price", x_axis_type="datetime", width_policy="max", height_policy="max")
				p.line(df1["time"], df1["Close"], legend_label="Close Price", line_width=2, color="blue")                
				p.yaxis.formatter = NumeralTickFormatter(format="0.00")
				
				for file in files:
					if os.path.exists(file):
						df = pd.read_csv(file, comment='#').fillna(0)
						#df['time'] = pd.to_datetime(df['time'], unit='ms')
						for cn in df.columns:
							if cn not in ["time", "Close"]:
								p.line(df1['time'], df[cn], legend_label=cn, line_width=1, color=obtener_color_aleatorio())
				
				transactions['Datetime'] = pd.to_datetime(transactions['Datetime'])
				
				for _, transaction in transactions.iterrows():
					trans_time = transaction['Datetime']
					closest_time_index = df1['time'].sub(trans_time).abs().idxmin()
					closest_price = df1['Close'].iloc[closest_time_index]
					
					if transaction['Type'] == 'Buy':
						p.scatter(trans_time, closest_price, size=8, color="green", legend_label="Buy")
						#p.scatter(transaction['Datetime'], transaction['Buy Price'], size=8, color="green", legend_label="Buy")
					elif transaction['Type'] == 'Sell':
						p.scatter(trans_time, closest_price, size=8, color="red", legend_label="Sell")
						#p.scatter(transaction['Datetime'], transaction['Sell Price'], size=8, color="red", legend_label="Sell")
				
				p.add_tools(HoverTool(tooltips=[("Price", "@y{0,0.00}"), ("Date", "@x{%F %T}")], formatters={"@x": "datetime"}))
				#p_secondary.add_tools(HoverTool(tooltips=[("Value", "@y{0,0.00}"), ("Date", "@x{%F %T}")], formatters={"@x": "datetime"}))
				
				# Mostrar los gráficos uno encima del otro
				#show(column(p, p_secondary))
				show(p)
	
	except Exception as e:
		write_log(f'Error en make_graphics(): {e}')
		write_log(f"Línea del error: {sys.exc_info()[-1].tb_lineno}")

		
def convert_csv_to_html(filecsv):
	try:
		filelines = ""
		headers = ""
		htmlCode1 = ""
		htmlCode2 = ""
		h = []

		file_prefix = prefix_type()

		bot_stats_file_path = file_prefix + BOT_STATS
		if os.path.exists(bot_stats_file_path) and os.path.getsize(bot_stats_file_path) > 2:
			with open(bot_stats_file_path,'r') as f:
				bot_stats = json.load(f)
		if os.path.exists(file_prefix + filecsv):        
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
				table = PrettyTable(h) #h sin uso, verificar para que esta.
		my_table = PrettyTable()
		my_table.format = True
		my_table.border = True
		my_table.align = "c"
		my_table.valign = "m"
		my_table.field_names = [languages_bot.MSG32[LANGUAGE], languages_bot.MSG23[LANGUAGE], languages_bot.MSG29[LANGUAGE], languages_bot.MSG31[LANGUAGE], PAIR_WITH + " " + languages_bot.MSG38[LANGUAGE] + languages_bot.MSG36[LANGUAGE], PAIR_WITH + " " + languages_bot.MSG37[LANGUAGE] + languages_bot.MSG36[LANGUAGE], PAIR_WITH + " " + languages_bot.MSG32[LANGUAGE], languages_bot.MSG33[LANGUAGE]]
		my_table.add_row(["TOTAL " + str(float(bot_stats["total_capital"]) + float(bot_stats["session_USDT_EARNED"])), datetime.fromtimestamp(float(bot_stats["botstart_datetime"])).strftime("%d/%m/%y %H:%M:%S"), bot_stats["tradeWins"], bot_stats["tradeLosses"], bot_stats["session_USDT_EARNED"], bot_stats["session_USDT_LOSS"], bot_stats["session_USDT_WON"], len(coins_bought)])
		#for line in open("megatronmod_strategy.py", "r"):
		with open("megatronmod_strategy.py", "r") as f:
			lines = f.readlines()
		for line in lines:
			if "buySignal" in line and "False" not in line and "return" not in line:
				 data1 = line
			if "sellSignal" in line and "False" not in line and "return" not in line:
				data2 = line
		htmlCode2 = my_table.get_html_string() 
		my_table = PrettyTable()
		with open(file_prefix + filecsv.replace("csv","html"), 'w') as final_htmlFile:
			final_htmlFile.write(htmlCode1)
			final_htmlFile.write("\n" + htmlCode2)
			final_htmlFile.write("<br>" + '<div style=\" width: 85%; display: flex; justify-content: center; align-items: center; border: 1px solid black;\">') 
			final_htmlFile.write('<h4 style=\"color:black\">')
			final_htmlFile.write('TEST_MODE: ' + str(TEST_MODE) + "<br>")
			final_htmlFile.write('COMPOUND_INTEREST: ' + str(COMPOUND_INTEREST) + "<br>")            
			final_htmlFile.write(data1)
			final_htmlFile.write("<br>" + data2)
			final_htmlFile.write('</h4></div>')
	except Exception as e:
		write_log(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.YELLOW}convert_csv_to_html(): {languages_bot.MSG1[LANGUAGE]}: {e}{txcolors.DEFAULT}')
		write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
		pass
	
def write_log_trades(logline):
	try:
		file_prefix = prefix_type()
		logline = str(logline).replace("'","").replace("[","").replace("]","")
		write_log_trades_strategys()
		Header = False
		if os.path.exists(file_prefix + TRADES_LOG_FILE):
			with open(file_prefix + TRADES_LOG_FILE,'r') as f:
				lines = f.readlines()
				#file_stats = os.stat(file_prefix + TRADES_LOG_FILE)
			for line in lines:
				if "Datetime" in line:
					Header = True
					lines = []
					break
		if not Header: #file_stats.st_size == 0:
			HEADER = ["Datetime"+","+"OrderID"+","+"Type"+","+"Coin"+","+"Volume"+","+"Buy Price"+","+"Amount of Buy" + " " + PAIR_WITH+","+"Sell Price"+","+"Amount of Sell" + " " + PAIR_WITH+","+ "Sell Reason"+","+"Profit $" + " " + PAIR_WITH+","+"Commission"]
			with open(file_prefix + TRADES_LOG_FILE,'a') as f:
				f.write(str(HEADER).replace("'","").replace("[","").replace("]","") + '\n')
				f.write(str(logline) + '\n')
		else:
			with open(file_prefix + TRADES_LOG_FILE,'a') as f:
				f.write(str(logline) + '\n')
	except Exception as e:
		write_log(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.YELLOW}write_log_trades(): {languages_bot.MSG1[LANGUAGE]}: {e}{txcolors.DEFAULT}')
		write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
		pass
		
def get_balance_test_mode():
	try:
		global TRADE_TOTAL, PAIR_WITH
		value1 = 0.0
		file_prefix = prefix_type()
		bot_stats_file_path = file_prefix + BOT_STATS
		if os.path.exists(bot_stats_file_path) and os.path.getsize(bot_stats_file_path) > 2:
			with open(bot_stats_file_path,'r') as f:
				bot_stats = json.load(f)   
			value1 = float(bot_stats["session_" + PAIR_WITH + "_EARNED"])

		if COMPOUND_INTEREST:
			value1 = TRADE_TOTAL + value1
		else:
			value1 = TRADE_TOTAL + value1
			if value1 >= TRADE_TOTAL:
				value1 = TRADE_TOTAL
			else:
				print(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}Insufficient balance[{value1}]...Exit{txcolors.DEFAULT}')
				menu() #sys.exit(0)

		show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())
	except Exception as e:
		write_log(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.YELLOW}get_balance_test_mode(): {languages_bot.MSG1[LANGUAGE]}: {e}{txcolors.DEFAULT}')
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
	show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())
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
			print(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.YELLOW}PANIC_STOP activated.{txcolors.DEFAULT}')
			stop_signal_threads() #panic_bot
			print(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.YELLOW}The percentage of losses is greater than or equal to the established one. Bot Stopped.{txcolors.DEFAULT}')
			menu() #sys.exit(0)

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
		global bot_paused, session_profit_incfees_perc, hsp_head, session_profit_incfees_total, PAUSEBOT_MANUAL, BUY_PAUSED
		PAUSEBOT = False
		# start counting for how long the bot has been paused
		start_time = time.perf_counter()
		#coins_sold = {}

		while chek_files_paused() or PAUSEBOT_MANUAL or BUY_PAUSED: #os.path.exists("signals/pausebot.pause") or PAUSE{languages_bot.MSG5[LANGUAGE]}_MANUAL:
			# do NOT accept any external signals to buy while in pausebot mode
			remove_external_signals('buy')

			if not bot_paused:
				if PAUSEBOT_MANUAL:
					print(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.YELLOW}Purchase paused manually, stop loss and take profit will continue to work...{txcolors.DEFAULT}')
					msg = str(datetime.now()) + ' | PAUSE{languages_bot.MSG5[LANGUAGE]}.Purchase paused manually, stop loss and take profit will continue to work...'
				else:
					print(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.YELLOW}Buying paused due to negative market conditions, stop loss and take profit will continue to work...{txcolors.DEFAULT}')
					msg = str(datetime.now()) + ' | PAUSE{languages_bot.MSG5[LANGUAGE]}. Buying paused due to negative market conditions, stop loss and take profit will continue to work.'
				
				msg_discord(msg)
				bot_paused = True

			# Sell function needs to work even while paused
			coins_sold = {}
			last_price = get_price(True) #pause_bot
			coins_sold = sell_coins(last_price=last_price)
			remove_from_portfolio(coins_sold)
			
			
			# pausing here
			# if hsp_head == 1: 
				# balance_report(last_price) 
			# time.sleep((TIME_DIFFERENCE * 10) / RECHECK_INTERVAL) #wait for pause_bot
			
		else:
			# stop counting the pause time
			stop_time = time.perf_counter()
			time_elapsed = timedelta(seconds=int(stop_time-start_time))

			# resume the bot and ser pause_bot to False
			if bot_paused == True:
				print(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.YELLOW}Resuming buying due to positive market conditions, total sleep time: {time_elapsed}{txcolors.DEFAULT}')
				msg = str(datetime.now()) + ' | PAUSE{languages_bot.MSG5[LANGUAGE]}. Resuming buying due to positive market conditions, total sleep time: ' + str(time_elapsed)
				msg_discord(msg)
				bot_paused = False
		show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())
	except Exception as e:
		write_log(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.YELLOW}pause_bot: {languages_bot.MSG1[LANGUAGE]}: {e}{txcolors.DEFAULT}')
		write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
		pass
	return
	
def set_config(data, value):
	show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())
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
	show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())
	file_name = "config.yml"
	parsed_config = load_config(file_name)
	with open(file_name, 'r') as file:
		data = file.readlines()
	c = 0
	for line in data:
		c = c + 1
		if "EXCLUDE_PAIRS: [" in line:
			break
	#EXCLUDE_PAIRS = parsed_config['trading_options']['EXCLUDE_PAIRS']
	e = False
	pairs = pairs.strip().replace('USDT','')
	for coin in EXCLUDE_PAIRS:
		if coin == pairs: 
			e = True
			break
		else:
			e = False
	if not e:
		print(f'The exception has been saved in EX_PAIR in the configuration file...{txcolors.DEFAULT}')
		EXCLUDE_PAIRS.append(pairs)
		data[c-1] = "  EXCLUDE_PAIRS: " + str(EXCLUDE_PAIRS) + "\n"
		with open(file_name, 'w') as f:
			f.writelines(data)

def buy_external_signals():
	external_list = []

	# check directory and load pairs from files into external_list
	files = []
	folder = "signals"
	files = [item for sublist in [glob.glob(folder + ext) for ext in ["/*.buy", "/*.exs"]] for item in sublist]

	#signals = glob.glob(mask)  #"signals/*.buy")
	#print("signals: ", signals)
	
	for filename in files: #signals:
		with open(filename, "r") as f:
			lines = f.readlines()
		for line in lines:
			symbol = line.strip()
			if symbol.replace(PAIR_WITH, "") not in EXCLUDE_PAIRS:
				#external_list.append(symbol)
				external_list.append({'symbol': symbol})
				#external_list[symbol] = symbol
		try:
			os.remove(filename)
		except:
			print(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.YELLOW}Could not remove external signalling file{txcolors.DEFAULT}')
	show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())
	return external_list

def random_without_repeating():
	show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())      
	RandOrderId = randint(10000, 99999)		
	return RandOrderId

#use function of the OlorinSledge
def wait_for_price():
	try:
		'''calls the initial price and ensures the correct amount of time has passed before reading the current price again'''
		global historical_prices, hsp_head, coins_up, coins_down, coins_unchanged, TRADE_TOTAL, USE_VOLATILE_METOD, coins_bought
		global PAIR, c_data		
		volatile_coins = {}
		externals1 = []
		externals2 = []
		pairs = []
		coins_up = 0
		coins_down = 0
		coins_unchanged = 0	
		pause_bot()

		if USE_SIGNALLING_MODULES:
			# Here goes new code for external signalling
			externals1 = buy_external_signals() #wait_for_price USE_SIGNALLING_MODULES
			last_price = get_price(False) #wait_for_price USE_SIGNALLING_MODULES
		else:
			coins1 = []
			last_price = 0
			coins1 = []
			if USE_MOST_VOLUME_COINS == True:
				TICKERS = 'volatile_volume_' + str(date.today()) + '.txt'
				with open(TICKERS, "r") as file:
					lines = file.readlines()
				pairs = [line.strip() + PAIR_WITH for line in lines if line.strip()]
			else:
				pairs = PAIR           
			#for line in open(TICKERS):
			#pairs=[line.strip() + PAIR_WITH for line in open(TICKERS, "r")] 
			
			for pair in pairs:
				pair = pair + PAIR_WITH
				coins1.append(pair)
			externals1, externals2 = analyze(c_data, coins1, True, POSITION) #wait_for_price
			last_price = get_price(False, externals1) #wait_for_price
		
		exnumber = 0
		for excoin in externals1:
			#print("excoin=", excoin, "externals1", externals1)
			excoin = excoin['symbol']
			if excoin not in volatile_coins and excoin not in coins_bought and (len(coins_bought) + len(volatile_coins)) < TRADE_SLOTS:
				volatile_coins[excoin] = 1
				exnumber +=1               
				#print(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}External signal received on {excoin}, purchasing ${get_balance_test_mode()} {PAIR_WITH} value of {excoin}!{txcolors.DEFAULT}')

		balance_report(last_price)
		show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())
	except Exception as e:
		write_log(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.YELLOW}wait_for_price(): {languages_bot.MSG1[LANGUAGE]}: {e}{txcolors.DEFAULT}')
		write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
		lost_connection(e, "wait_for_price")        
		pass
	return volatile_coins, len(volatile_coins), last_price #historical_prices[hsp_head]
	
def get_info(coin, file):
	try:
		info = ""
		client = Client(access_key, secret_key)
		info = client.get_symbol_info(coin)
		with open(file, "a") as f:
			f.write(str(info) + '\n')
		client = ""    
		return info
	except Exception as e:
		write_log(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.YELLOW}get_info() exception: {e}{txcolors.DEFAULT}')
		write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")       
		pass 
	
def get_symbol_info(coin1):
	try:
		global FILE_SYMBOL_INFO, client
		ret = {}
		if BACKTESTING_MODE:
			#for line in open(FILE_SYMBOL_INFO, "r"):
			with open(FILE_SYMBOL_INFO, "r") as f:
				lines = f.readlines()
			for line in lines:
				if coin1 in line:
					#print("line=", line)
					ret = eval(line)
					break
			if len(ret) == 0:
				ret = get_info(coin1, FILE_SYMBOL_INFO)
		if not BACKTESTING_MODE:
			ret = client.get_symbol_info(coin1) #get_symbol_info
	except Exception as e:
		write_log(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.YELLOW}get_symbol_info() exception: {e}{txcolors.DEFAULT}')
		write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")       
		pass
	return ret

def convert_volume():
	try:
		'''Converts the volume given in TRADE_TOTAL from "USDT"(or coin selected) to the each coin's volume'''
		volatile_coins, number_of_coins, last_price = wait_for_price()
		
		global TRADE_TOTAL, session_USDT_EARNED
		lot_size = {}
		volume = {}
		
		for coin in volatile_coins:
			# Find the correct step size for each coin
			# max accuracy for BTC for example is 6 decimal points
			# while XRP is only 1
			#try:
			info = get_symbol_info(coin) #convert_volume
			#last_price = get_price(True)
			
			#step_size = info['filterType'][1]['stepSize']
			#step_size = float(info['filters'][2]['stepSize'])
			#lot_size[coin] = step_size.index('1') - 1
			
			for filt in info['filters']:
				if filt['filterType'] == 'LOT_SIZE':
					lot_size[coin] = filt['stepSize'].find('1') - 1                    
					break		
			if lot_size[coin] < 0: lot_size[coin] = 0
			#print("volume[coin]",volume[coin],"lot_size[coin]", lot_size[coin], "type", type(lot_size[coin]))
			# calculate the volume in coin from TRADE_TOTAL in PAIR_WITH (default)    

			volume[coin] = float(get_balance_test_mode() / float(last_price[coin]['price'])) #convert_volume

			# define the volume with the correct step size
			if coin not in lot_size:
				volume[coin] = float(volume[coin])
			else:
					# if lot size has 0 decimal points, make the volume an integer
				if lot_size[coin] == 0:
					volume[coin] = int(volume[coin])
				else:
					volume[coin] = truncate(volume[coin], lot_size[coin])
		
			show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())
	except ZeroDivisionError:
		pass
	except Exception as e:
		write_log(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.YELLOW}convert_volume() exception: {e}{txcolors.DEFAULT}')
		write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
		lost_connection(e, "convert_volume")        
		pass

	return volume, last_price

def simulate_commission(volume, coin):
	try:
		global client, commissionCoins
		r = 0.0
		symbol_price = 0.0
		ExistCoin = False
		if TRADING_FEE == 0.075:
			if not coin in commissionCoins:
				client = Client(access_key, secret_key)
				try:
					filter = coin.replace(PAIR_WITH, "") + "BNB"
					symbol1 = client.get_symbol_ticker(symbol=filter)				
					#print("symbol1", symbol1)
				except Exception  as e:
					symbol1 = ""
					#print(coin.replace(PAIR_WITH, "") + "BNB", e)
				try:
					filter = "BNB" + coin.replace(PAIR_WITH, "") 
					symbol2 = client.get_symbol_ticker(symbol=filter)
					#print("symbol2", symbol2)
				except Exception  as e:
					symbol2 = ""
					#print("BNB" + coin.replace(PAIR_WITH, ""), e)
			
				if not symbol1 == "":
					symbol_price = float(symbol1['price'])
					#print(symbol1)
				if not symbol2 == "":
					symbol_price = float(symbol2['price'])
					#print(symbol2)
				try:
					if symbol_price > 0:
						r = ((TRADING_FEE/100) * volume)*symbol_price
					#else:
						#print("ERROR:", TRADING_FEE, volume, symbol_price)
				except Exception  as e:
					print(e)
				coin = "BNB"	
			else:
				r = ((TRADING_FEE/100) * volume)
			commissionCoins[coin] = r
			
	except Exception as e:
			write_log(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.YELLOW} simulate_commission(): {languages_bot.MSG1[LANGUAGE]}: {e}{txcolors.DEFAULT}')
			write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
	return r, coin
	

def buy():
	try:
		global coins_bought, client, USED_COMMISSIONS

		volume, last_price = convert_volume()  # Get volume and last price data
		orders = {}

		for coin, vol in volume.items():
			if not coin in coins_bought or not coin.replace(PAIR_WITH, '') in EXCLUDE_PAIRS:
				#print(f"{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.GREEN}Preparing to buy {vol} of {coin} @ ${last_price[coin]['price']}{txcolors.DEFAULT}")
				if TEST_MODE:
					#orders[coin] = simulate_test_order(coin, vol, last_price[coin]['price'])
					order_id = random_without_repeating()
					coin_commission, pair_with = simulate_commission(vol, coin)
					USED_COMMISSIONS[pair_with] = round(USED_COMMISSIONS.get(pair_with, 0) + coin_commission, 10)
					
					#print(f"{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.GREEN}Simulated order for {coin}: {vol} @ ${last_price[coin]['price']}{txcolors.DEFAULT}")
					if MODE == "BACKTESTING":
						orders[coin] = [{
							'symbol': coin,
							'orderId': order_id,
							'time': last_price[coin]['time']
						}]
					else:	
						orders[coin] = [{
							'symbol': coin,
							'orderId': order_id,
							'time': datetime.now().timestamp()
						}]
					
					if BACKTESTING_MODE:
						#write_log_trades([datetime.fromtimestamp(last_price[coin]['time']/1000).strftime("%Y-%d-%m %H:%M:%S"),order_id,"Buy",coin.replace(PAIR_WITH,""),round(float(vol),8),str(round(float(last_price[coin]['price']),8)),str(round(float(get_balance_test_mode()),8)),0,0,"-",0,coin_commission]) #buy 
						write_log_trades([datetime.fromtimestamp(last_price[coin]['time']/1000).strftime('%Y-%m-%d %H:%M:%S')+","+str(order_id)+","+"Buy"+","+coin.replace(PAIR_WITH,"")+","+str(round(float(vol),8))+","+str(round(float(last_price[coin]['price']),8))+","+str(round(float(get_balance_test_mode()),8))+","+"0"+","+"0"+","+"-"+","+"0"+","+f"{coin_commission:.10f}"]) #buy               
				else:
					try:
						order_details = client.create_order(
							symbol=coin,
							side='BUY',
							type='MARKET',
							quantity=vol
						)

						while not order_details:
							print(f"Binance API slow for {coin}, retrying...")
							order_details = client.get_all_orders(symbol=coin, limit=1)
							time.sleep(1) #buy

						#print(f"Order processed for {coin}, saving to file.")
						orders[coin] = extract_order_data(order_details)
						order_id = orders[coin]['orderId']
						coin_commission = orders[coin]['tradeFeeBNB']
						#if BACKTESTING_MODE:
							#write_log_trades([datetime.fromtimestamp(last_price[coin]['time']/1000).strftime("%Y-%d-%m %H:%M:%S"),order_id,"Buy",coin.replace(PAIR_WITH,""),round(float(vol),8),str(round(float(last_price[coin]['price']),8)),str(round(float(get_balance_test_mode()),8)),0,0,"-",0,coin_commission]) #buy 
							#write_log_trades([last_price[coin]['time'],order_id,"Buy",coin.replace(PAIR_WITH,""),round(float(vol),8),str(round(float(last_price[coin]['price']),8)),str(round(float(get_balance_test_mode()),8)),0,0,"-",0,coin_commission]) #buy               
						#else:
							#write_log_trades([datetime.now().strftime("%Y-%d-%m %H:%M:%S"),order_id,"Buy",coin.replace(PAIR_WITH,""),round(float(vol),8),str(round(float(last_price[coin]['price']),8)),str(round(float(get_balance_test_mode()),8)),0,0,"-",0,coin_commission]) #buy 
						trade_time_raw = last_price[coin]['time']
						if isinstance(trade_time_raw, datetime):
							trade_time = trade_time_raw.strftime('%Y-%m-%d %H:%M:%S')
						else:
							trade_time = datetime.fromtimestamp(trade_time_raw / 1000).strftime('%Y-%m-%d %H:%M:%S')

						write_log_trades([trade_time, str(order_id), "Buy", coin.replace(PAIR_WITH, ""), str(round(float(vol), 8)), str(round(float(last_price[coin]['price']), 8)), str(round(float(get_balance_test_mode()), 8)), "0", "0", "-", "0", f"{coin_commission:.10f}"])
						# write_log_trades([datetime.fromtimestamp(last_price[coin]['time']/1000).strftime('%Y-%m-%d %H:%M:%S')+","+str(order_id)+","+"Buy"+","+coin.replace(PAIR_WITH,"")+","+str(round(float(vol),8))+","+str(round(float(last_price[coin]['price']),8))+","+str(round(float(get_balance_test_mode()),8))+","+"0"+","+"0"+","+"-"+","+"0"+","+f"{coin_commission:.10f}"]) #buy 
					
					except Exception as e:
						write_log(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.YELLOW} buy(): In create_order exception({coin}): {e}{txcolors.DEFAULT}')
						write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
						continue

		return orders, last_price, volume

	except Exception as e:
		write_log(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.YELLOW} buy(): {languages_bot.MSG1[LANGUAGE]}: {e}{txcolors.DEFAULT}')
		write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
		lost_connection(e, "buy")

def sell_coins(tpsl_override=False, specific_coin_to_sell="", last_price={}):
	try:
		global hsp_head, session_profit_incfees_perc, session_profit_incfees_total, coin_order_id, trade_wins
		global trade_losses, historic_profit_incfees_perc, historic_profit_incfees_total, sell_all_coins, client
		global session_USDT_EARNED, TUP, TDOWN, TNEUTRAL, USED_COMMISSIONS, TRADE_TOTAL, sell_specific_coin
		global session_USDT_LOSS, session_USDT_WON, session_USDT_EARNED, SAVED_COINS, coins_bought, SELL_PART
		global SAVED_COINS, PAIR_WITH

		coins_sold = {}
		if not coins_bought:
			return coins_sold

		externals = sell_external_signals()
		BUDGET = get_balance_test_mode() * TRADE_SLOTS

		for coin in list(coins_bought):
			LastPriceBR = float(last_price[coin]['price'])
			BuyPriceBR = float(coins_bought[coin]['bought_at'])
			PriceChange_Perc = float((LastPriceBR - BuyPriceBR) / BuyPriceBR * 100)

			if not SELL_ON_SIGNAL_ONLY:
				TP = BuyPriceBR + (BuyPriceBR * coins_bought[coin]['take_profit'] / 100)
				SL = BuyPriceBR + (BuyPriceBR * coins_bought[coin]['stop_loss'] / 100)

				if LastPriceBR > TP and USE_TRAILING_STOP_LOSS and not (sell_all_coins or tpsl_override or sell_specific_coin):
					coins_bought[coin]['stop_loss'] = coins_bought[coin]['take_profit'] - TRAILING_STOP_LOSS
					coins_bought[coin]['take_profit'] = PriceChange_Perc + TRAILING_TAKE_PROFIT
					continue

			sellCoin = False
			sell_reason = ""
			if SELL_ON_SIGNAL_ONLY:
				sellCoin = any(extcoin['symbol'] == coin for extcoin in externals)
				sell_reason = 'External Sell Signal' if sellCoin else ""
			else:
				if LastPriceBR < SL:
					ellCoin = True
					sell_reason = "TSL " if USE_TRAILING_STOP_LOSS and PriceChange_Perc >= 0 else "SL "
					sell_reason += f"{SL:.18f} reached"
				if LastPriceBR > TP:
					sellCoin = True
					sell_reason = f"TP {TP:.2f} reached"
				if coin in externals:
					sellCoin = True
					sell_reason = 'External Sell Signal'

			if sell_all_coins or sell_specific_coin or tpsl_override or specific_coin_to_sell == coin:
				sellCoin = True
				sell_reason = 'Sell All Coins' if sell_all_coins else 'Sell Specific Coin' if sell_specific_coin else 'Session TPSL Override reached' if tpsl_override else 'Specific Coin Sell'

			if sellCoin:
				q = coins_bought[coin]['volume']
				if SELL_PART:
					pre = TRADE_TOTAL / LastPriceBR
					q = get_presicion(coin, pre)
					savedcoin = coins_bought[coin]['volume'] - q
					SAVED_COINS[coin] = float(SAVED_COINS.get(coin, 0)) + savedcoin

				try:
					#print(f"{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.YELLOW}Preparing to sell {coins_bought[coin]['volume']} of {coin} @ ${last_price[coin]['price']}{txcolors.DEFAULT}")
					if not TEST_MODE:
						order_details = client.create_order(symbol=coin, side='SELL', type='MARKET', quantity=q)
						coins_sold[coin] = extract_order_data(order_details)
						OrderID = coins_sold[coin]['orderId'] #orders[coin]['orderId']
						VolumeSell = q
						LastPrice = coins_sold[coin]['avgPrice']
						coin_commission = coins_sold[coin]['tradeFeeBNB'] #, PAIRWITH = simulate_commission(coins_sold[coin]['volume'] * LastPriceBR, PAIR_WITH)
						if TRADING_FEE == 0.075:
							PAIRWITH = 'BNB'
					else:
						coins_sold[coin] = coins_bought[coin]
						coins_bought.pop(coin, None)
						VolumeSell = format(float(coins_sold[coin]['volume']), '.6f')
						coin_commission, PAIRWITH = simulate_commission(coins_sold[coin]['volume'] * LastPriceBR, coin)
						OrderID = coins_sold[coin]['orderid']
						#print(f"{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.YELLOW}Simulated order for {coin}: {VolumeSell} @ ${last_price[coin]['price']}{txcolors.DEFAULT}")
					
					USED_COMMISSIONS[PAIRWITH] = round(float(USED_COMMISSIONS.get(PAIRWITH, 0)) + coin_commission, 10)

					SellUSDT = coins_sold[coin]['volume'] * LastPriceBR
					USDTdiff = SellUSDT - (BuyPriceBR * coins_sold[coin]['volume'])
					session_USDT_EARNED += USDTdiff
					if USDTdiff < 0:
						session_USDT_LOSS += USDTdiff
					else:
						session_USDT_WON += USDTdiff

					if USDTdiff > 0:
						trade_wins += 1
					else:
						trade_losses += 1

					if BACKTESTING_MODE:
						write_log_trades([datetime.fromtimestamp(last_price[coin]['time']/1000).strftime('%Y-%m-%d %H:%M:%S')+","+str(OrderID)+","+"Sell"+","+coin.replace(PAIR_WITH, "")+","+str(round(float(VolumeSell),8))+","+str(round(float(BuyPriceBR),8))+","+read_log_trades(str(OrderID))+","+str(round(float(LastPriceBR),8))+","+str(round(float(get_balance_test_mode()),8))+","+sell_reason+","+str(round(float(USDTdiff),8))+","+f"{coin_commission:.10f}"]) #sell_coins
					else:
						write_log_trades([datetime.now().strftime('%Y-%m-%d %H:%M:%S')+","+str(OrderID)+","+"Sell"+","+coin.replace(PAIR_WITH, "")+","+str(round(float(VolumeSell),8))+","+str(round(float(BuyPriceBR),8))+","+read_log_trades(str(OrderID))+","+str(round(float(LastPriceBR),8))+","+str(round(float(get_balance_test_mode()),8))+","+sell_reason+","+str(round(float(USDTdiff),8))+","+f"{coin_commission:.10f}"]) #sell_coins
					
					update_bot_stats()
					if not (sell_all_coins or sell_specific_coin):
						balance_report(last_price)

				except Exception as e:
					write_log(f"{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}sell_coins(): Exception on selling {coin}\nException: {e}{txcolors.DEFAULT}")
					write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
					continue
					
		show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())

	except Exception as e:
		write_log(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.YELLOW}sell_coins(): {languages_bot.MSG1[LANGUAGE]}: {e}{txcolors.DEFAULT}')
		write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
		lost_connection(e, "sell_coins")

	return coins_sold
	
	
def sell_all(msgreason, session_tspl_ovr = False):
	global sell_all_coins
	msg_discord(f'{str(datetime.now())} | SELL ALL COINS: {msgreason}')

	# stop external signals so no buying/selling/pausing etc can occur
	stop_signal_threads() #sell_all

	# sell all coins NOW!
	sell_all_coins = True

	last_price = get_price() #sell_all
	coins_sold = sell_coins(session_tspl_ovr, ast_price=last_price)
	remove_from_portfolio(coins_sold)
	
	# display final info to screen
	
	#print("sell_all: last_price= ", last_price)
	discordmsg = balance_report(last_price)
	msg_discord(discordmsg)
	sell_all_coins = False
	show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())

#extracted from the code of OlorinSledge
def sell_coin(coin):
	global sell_specific_coin, last_price
	last_price = get_price()
	if MODE == "BACKTESTING":
		print(f'{txcolors.YELLOW}BOT: {txcolors.DEFAULT}{str(datetime.fromtimestamp(last_price[coin]['time'] / 1000))} | SELL SPECIFIC COIN: {coin}')
	else:
		print(f'{txcolors.YELLOW}BOT: {txcolors.DEFAULT} {str(datetime.now())} | SELL SPECIFIC COIN: {coin}')
		msg_discord(f'{str(datetime.now())} | SELL SPECIFIC COIN: {coin}')
	# sell all coins NOW!
	sell_specific_coin = True
	coins_sold = sell_coins(False, coin, last_price)
	remove_from_portfolio(coins_sold)
	sell_specific_coin = False
	show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())
	
def sell_external_signals():
	#external_list = {}
	global c_data
	signals1 = []
	signals2 = []

	if USE_SIGNALLING_MODULES:
		# check directory and load pairs from files into external_list
		signals = glob.glob("signals/*.sell")
		for filename in signals:
			with open(filename, "r") as f:
				lines = f.readlines()
			for line in lines:
				symbol = line.strip()
				#signals2.append(symbol)
				signals2.append({'symbol': symbol})
				#print(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.YELLOW}{symbol} added to sell_external_signals() list.')
			try:
				os.remove(filename)
			except:
				write_log(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.YELLOW} {"sell_external_signals()"}: Could not remove external SELL signalling file{txcolors.DEFAULT}')
		#return external_list
	else:
		coins1 = []
		TICKERS = ''
		
		if USE_MOST_VOLUME_COINS == True:
			TICKERS = 'volatile_volume_' + str(date.today()) + '.txt'
			with open(TICKERS, "r") as file:
				lines = file.readlines()
			symbols = [line.strip() + PAIR_WITH for line in lines if line.strip()] 
		else:
			symbols = PAIR
			
		#for line in open(TICKERS):
		#symbols=[line.strip() + PAIR_WITH for line in open(TICKERS, "r")] 
		   
		for symbol in symbols:
			symbol = symbol + PAIR_WITH
			coins1.append(symbol)
		signals1, signals2 = analyze(c_data, coins1, False, POSITION) # sell_external_signals()
		#tp_pausebotmod.analyze(c_data)
		
	show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())    
	return signals2
	


def extract_order_data(order_details):
	try:
		global TRADING_FEE, STOP_LOSS, TAKE_PROFIT, USED_COMMISSIONS
		transactionInfo = {}
		FILLS_TOTAL = 0
		FILLS_QTY = 0
		FILLS_FEE = 0
		BNB_YELLOW = 0        
		for fills in order_details['fills']:
			FILL_PRICE = float(fills['price'])
			FILL_QTY = float(fills['qty'])
			FILLS_FEE += float(fills['commission'])
			# if fills['commissionAsset'] == 'BNB':  
				# if float(fills['commission']) < 0:
					# USED_COMMISSIONS['BNB'] = float(USED_COMMISSIONS.get('BNB', 0)) + float(fills['commission'])
				# else:
					# USED_COMMISSIONS['BNB'] = float(USED_COMMISSIONS.get('BNB', 0)) + simulate_commission(FILL_QTY)
			# else:
				# symbol = fills['commissionAsset']
				# if float(fills['commission']) < 0:
					# USED_COMMISSIONS[symbol] = float(USED_COMMISSIONS.get(symbol, 0)) + float(fills['commission'])
				# else:
					# USED_COMMISSIONS[symbol] = float(USED_COMMISSIONS.get(symbol, 0)) + simulate_commission(FILL_QTY)
			# if (fills['commissionAsset'] != 'BNB') and (TRADING_FEE == 0.075) and (BNB_YELLOW == 0):
				#print(f"YELLOW: BNB not used for trading fee, please ")
				# BNB_YELLOW += 1
			# quantity of fills * price
			FILLS_TOTAL += (FILL_PRICE * FILL_QTY)
			# add to running total of fills quantity
			FILLS_QTY += FILL_QTY
			# increase fills array index by 1

		# calculate average fill price:
		FILL_AVG = (FILLS_TOTAL / FILLS_QTY)

		# Olorin Sledge: I only want fee at the unit level, not the total level
		tradeFeeApprox = float(FILL_AVG) * (TRADING_FEE/100)

		# the volume size is sometimes outside of precision, correct it
		try:
			info = get_symbol_info(order_details['symbol']) #extract_order_data()
			#client.get_symbol_info(order_details['symbol'])
			for filt in info['filters']:
				if filt['filterType'] == 'LOT_SIZE':
					lot_size = filt['stepSize'].find('1') - 1
					#print("lot_size", lot_size)
					break
			
			if lot_size <= 0:
				FILLS_QTY = int(FILLS_QTY)
			else:
				FILLS_QTY = truncate(FILLS_QTY, lot_size)
		except Exception as e:
			write_log(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.YELLOW}extract_order_data(internal): Exception getting coin {order_details["symbol"]} step size! Exception: {e}{txcolors.DEFAULT}')
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
		show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())
	except Exception as e:
		write_log(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.YELLOW}extract_order_data(): {languages_bot.MSG1[LANGUAGE]}: {e}{txcolors.DEFAULT}')
		write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
		pass
	return transactionInfo

def check_total_session_profit(coins_bought, last_price):
	global is_bot_running, session_tpsl_override_msg, SESSION_TAKE_PROFIT, SESSION_STOP_LOSS, BUDGET
	unrealised_session_profit_incfees_total = 0
			
	BUDGET = TRADE_SLOTS * get_balance_test_mode() #check_total_session_profit
	
	for coin in list(coins_bought):
		LastPrice = float(last_price[coin]['price'])
		#sellFee = (LastPrice * (TRADING_FEE/100))		
		BuyPrice = float(coins_bought[coin]['bought_at'])
		#buyFee = (BuyPrice * (TRADING_FEE/100))	
		#PriceChangeIncFees_Total = float(((LastPrice - sellFee) - (BuyPrice + buyFee)) * coins_bought[coin]['volume'])
		#unrealised_session_profit_incfees_total = float(unrealised_session_profit_incfees_total + PriceChangeIncFees_Total)
		
	#allsession_profits_perc = session_profit_incfees_perc +  ((unrealised_session_profit_incfees_total / BUDGET) * 100)

	#print(f'Session Override SL Feature: ASPP={allsession_profits_perc} STP {SESSION_TAKE_PROFIT} SSL {SESSION_STOP_LOSS}{txcolors.DEFAULT}')
	
	#if allsession_profits_perc >= float(SESSION_TAKE_PROFIT): 
		#session_tpsl_override_msg = "Session TP Override target of " + str(SESSION_TAKE_PROFIT) + "% met. Sell all coins now!"
		#is_bot_running = False
	#if allsession_profits_perc <= float(SESSION_STOP_LOSS):
		#session_tpsl_override_msg = "Session SL Override target of " + str(SESSION_STOP_LOSS) + "% met. Sell all coins now!"
		#is_bot_running = False   
	show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())
	
def update_portfolio(orders, last_price, volume):
	global coins_bought, client
	'''add every coin bought to our portfolio for tracking/selling later'''
	for coin in orders:
		try:
			coin_step_size = float(next(filter(lambda f: f['filterType'] == 'LOT_SIZE', client.get_symbol_info(orders[coin][0]['symbol'])['filters']))['stepSize']) #update_portfolio
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
			   #'buyFeeBNB': orders[coin]['tradeFeeBNB'],
			   #'buyFee': orders[coin]['tradeFeeUnit'] * orders[coin]['volume'],
			   'stop_loss': -STOP_LOSS,
			   'take_profit': TAKE_PROFIT,
			   'step_size': float(coin_step_size),
			   }

			#print(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}Order for {orders[coin]["symbol"]} with ID {orders[coin]["orderId"]} placed and saved to file.{txcolors.DEFAULT}')
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

			#print(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}Order for {orders[coin][0]["symbol"]} with ID {orders[coin][0]["orderId"]} placed and saved to file.{txcolors.DEFAULT}')

		# save the coins in a json file in the same directory
		with open(coins_bought_file_path, 'w') as file:
			json.dump(coins_bought, file, indent=4)
	show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())

def update_bot_stats():
	try:
		global TRADE_TOTAL, trade_wins, trade_losses, historic_profit_incfees_perc, historic_profit_incfees_total, session_USDT_EARNED, session_USDT_LOSS, session_USDT_WON, USED_COMMISSIONS
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
			'saved_coins': SAVED_COINS,
			'used_commissions': USED_COMMISSIONS,
		}

		#save session info for through session portability
		with open(bot_stats_file_path, 'w') as file:
			json.dump(bot_stats, file, indent=4)
		show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())
	except Exception as e:
		write_log(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.YELLOW}update_bot_stats(): exception: {e}{txcolors.DEFAULT}')
		write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
		pass  

def remove_from_portfolio(coins_sold):
	global coins_bought
	try:
		if coins_sold is not None:
			for coin in coins_sold:
				# code below created by getsec <3
				coins_bought.pop(coin, None)
				#del data['BTCUSDT']
			with open(coins_bought_file_path, 'w') as file:
				json.dump(coins_bought, file, indent=4)
			#if os.path.exists('signalsell_tickers.txt'):
				#os.remove('signalsell_tickers.txt')
				#for coin in coins_bought:
					#write_signallsell(coin.removesuffix(PAIR_WITH))
			show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())
	except Exception as e:
		write_log(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.YELLOW}remove_from_portfolio(): exception: {e}{txcolors.DEFAULT}')
		write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
		pass  
		
# def write_signallsell(symbol):
	# with open('signalsell_tickers.txt','a+') as f:
		# f.write(f'{symbol}\n')
	# show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())

def remove_external_signals(fileext):
	signals = glob.glob(f'signals/*.{fileext}')
	for filename in signals:
		if os.path.exists(filename):
			os.remove(filename)
	show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())
	
def load_signal_threads():
	try:
		#load signalling modules
		global signalthreads
		signalthreads = []
		if SIGNALLING_MODULES is not None and USE_SIGNALLING_MODULES: #load_signal_threads
			if len(SIGNALLING_MODULES) > 0:
				for module in SIGNALLING_MODULES:
					if os.path.exists(module + '.py'):
						print(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}Starting {module}{txcolors.DEFAULT}')
						mymodule[module] = importlib.import_module(module)
						t = threading.Thread(target=mymodule[module].do_work, args=())
						t.daemon = True
						#t = multiprocessing.Process(target=mymodule[module].do_work, args=())
						t.name = module
						t.start()
						signalthreads.append(t)
						time.sleep(0.5) #wait for load_signal_threads
					else:
						write_log(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.YELLOW}Module {module} does not exist... continuing to load other modules{txcolors.DEFAULT}')
			else:
				write_log(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.YELLOW}{"load_signal_threads"}: No modules to load {SIGNALLING_MODULES}{txcolors.DEFAULT}')
		show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())
	except Exception as e:
		write_log(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.YELLOW}load_signal_threads(): Loading external signals exception: {e}{txcolors.DEFAULT}')
		write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
		pass

def stop_signal_threads():
	try:
		global SIGNALLING_MODULES
		if USE_SIGNALLING_MODULES:
			global signalthreads
			#signalthreads= [<Thread(megatronmod, started daemon 11684)>]
			if len(signalthreads) > 0:
				for signalthread in signalthreads:
					print(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}Terminating thread {str(signalthread.name)}{txcolors.DEFAULT}')
					with open("signal.sig", "w") as f:
						f.write("0")
		  
		show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())
		#else:
			#if menu() == True: sys.exit(0)
	except Exception as e:
		write_log(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}stop_signal_threads(): {languages_bot.MSG1[LANGUAGE]}: {e}{txcolors.DEFAULT}')
		write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
		pass
	#except KeyboardInterrupt as ki:
		#print()
		#pass

def truncate(number, decimals=0):
	if not isinstance(decimals, int):
		raise TypeError("decimal places must be an integer.")
	elif decimals < 0:
		raise ValueError("decimal places has to be 0 or more.")
	elif decimals == 0:
		return math.trunc(number)

	factor = 10.0 ** decimals
	return math.trunc(number * factor) / factor

def get_presicion(coin, volume):
	global client
	info = client.get_symbol_info(coin)   
	for filt in info['filters']:
		if filt['filterType'] == 'LOT_SIZE':
			lot_size = filt['stepSize'].find('1') - 1                    
			break		
	if lot_size < 0: lot_size = 0         

	if lot_size == 0:
		volume = int(volume)
	else:
		volume = truncate(volume, lot_size)
	return volume
	
def load_settings():
	try:
		# set to false at Start
		global bot_paused, parsed_config, creds_file, access_key, secret_key, parsed_creds, client, DEFAULT_CREDS_FILE, DEFAULT_CONFIG_FILE
		bot_paused = False

		DEFAULT_CONFIG_FILE = 'config.yml'
		DEFAULT_CREDS_FILE = 'creds.yml'    

		config_file = args.config if args.config else DEFAULT_CONFIG_FILE
		parsed_config = load_config(config_file)
		

		# Default no debugging
		global DEBUG, ENABLE_FUNCTION_NAME, SHOW_FUNCTION_NAME, SAVE_FUNCTION_NAME, SHOW_VARIABLES_AND_VALUE, SAVE_VARIABLES_AND_VALUE
		global BACKTESTING_MODE_TIME_START, BACKTESTING_MODE_TIME_END, BOT_TIMEFRAME, LOG_TRADES, TRADES_LOG_FILE
		global DEBUG_SETTING, AMERICAN_USER, PAIR_WITH, QUANTITY, MAX_COINS, FIATS, TIME_DIFFERENCE, RECHECK_INTERVAL, CHANGE_IN_PRICE
		global STOP_LOSS, TAKE_PROFIT, USE_TRAILING_STOP_LOSS, TRAILING_STOP_LOSS, TRAILING_TAKE_PROFIT, TRADING_FEE
		global SIGNALLING_MODULES, MSG_DISCORD, HISTORY_LOG_FILE, TRADE_SLOTS, TRADE_TOTAL, SESSION_TPSL_OVERRIDE, coin_bought
		global SELL_ON_SIGNAL_ONLY, TRADING_FEE, SHOW_INITIAL_CONFIG, USE_MOST_VOLUME_COINS, COINS_MAX_VOLUME, USE_VOLATILE_METOD
		global COINS_MIN_VOLUME, DISABLE_TIMESTAMPS, STATIC_MAIN_INFO, COINS_BOUGHT, BOT_STATS, print_TO_FILE, TRADES_GRAPH, TRADES_INDICATORS
		global ENABLE_print_TO_FILE, EXCLUDE_PAIRS, RESTART_MODULES, SHOW_TABLE_COINS_BOUGHT, SORT_TABLE_BY, print_TABLE_COMMISSIONS
		global REVERSE_SORT, MAX_HOLDING_TIME, PROXY_HTTP, PROXY_HTTPS,USE_SIGNALLING_MODULES, REINVEST_MODE, JSON_REPORT
		global LOG_FILE, PANIC_STOP, BUY_PAUSED, UPDATE_MOST_VOLUME_COINS, VOLATILE_VOLUME, COMPOUND_INTEREST, MICROSECONDS, LANGUAGE
		global FILE_SYMBOL_INFO, TRADES_INDICATORS, USE_TRADES_INDICATORS, SELL_PART, MODE
		global SILENT_MODE, PAIR
		
		# Default no debugging
		DEBUG = False

		# Load system vars
		#TEST_MODE = parsed_config['script_options']['TEST_MODE']
		#USE_TESNET_IN_ONLINEMODE = parsed_config['script_options']['USE_TESNET_IN_ONLINEMODE']
		LANGUAGE = parsed_config['script_options']['LANGUAGE']
		USERID = 'Pantersxx3' #parsed_config['script_options']['USERID']
		#BACKTESTING_MODE = parsed_config['script_options']['BACKTESTING_MODE']
		MODE = parsed_config['script_options']['MODE']
		BACKTESTING_MODE_TIME_START = parsed_config['script_options']['BACKTESTING_MODE_TIME_START']
		BOT_TIMEFRAME = parsed_config['script_options']['BOT_TIMEFRAME']
		BACKTESTING_MODE_TIME_END = parsed_config['script_options']['BACKTESTING_MODE_TIME_END']
		USE_VOLATILE_METOD = parsed_config['script_options']['USE_VOLATILE_METOD']
		SILENT_MODE = parsed_config['script_options']['SILENT_MODE']
		#if BACKTESTING_MODE True use USE_SIGNALLING_MODULES: False
		#USE_SIGNALLING_MODULES =  False if BACKTESTING_MODE else True
		TRADES_LOG_FILE = parsed_config['script_options'].get('TRADES_LOG_FILE')
		TRADES_GRAPH = parsed_config['script_options'].get('TRADES_GRAPH')
		TRADES_INDICATORS = parsed_config['script_options'].get('TRADES_INDICATORS')
		#USE_TRADES_INDICATORS = parsed_config['script_options'].get('USE_TRADES_INDICATORS')
		FILE_SYMBOL_INFO = parsed_config['script_options'].get('FILE_SYMBOL_INFO')
		LOG_FILE = parsed_config['script_options'].get('LOG_FILE')
		JSON_REPORT  = parsed_config['script_options'].get('JSON_REPORT')
		COINS_BOUGHT = parsed_config['script_options'].get('COINS_BOUGHT')
		print_TABLE_COMMISSIONS = parsed_config['script_options'].get('print_TABLE_COMMISSIONS')
		BOT_STATS = parsed_config['script_options'].get('BOT_STATS')
		DEBUG_SETTING = parsed_config['script_options'].get('DEBUG')
		#REMOTE_INSPECTOR_MEGATRONMOD_PORT = parsed_config['script_options'].get('REMOTE_INSPECTOR_MEGATRONMOD_PORT')
		#REMOTE_INSPECTOR_BOT_PORT = parsed_config['script_options']['REMOTE_INSPECTOR_BOT_PORT']
		ENABLE_FUNCTION_NAME = False #parsed_config['script_options'].get('ENABLE_FUNCTION_NAME')
		SAVE_FUNCTION_NAME = True #parsed_config['script_options'].get('SAVE_FUNCTION_NAME')
		SHOW_FUNCTION_NAME = False #parsed_config['script_options'].get('SHOW_FUNCTION_NAME')
		SHOW_VARIABLES_AND_VALUE = False #parsed_config['script_options'].get('SHOW_VARIABLES_AND_VALUE')
		SAVE_VARIABLES_AND_VALUE = False #parsed_config['script_options'].get('SAVE_VARIABLES_AND_VALUE')    
	   
		MICROSECONDS = parsed_config['script_options'].get('MICROSECONDS')
		AMERICAN_USER = parsed_config['script_options'].get('AMERICAN_USER')

		# Load trading vars
		PAIR_WITH = parsed_config['trading_options']['PAIR_WITH']
		PAIR = parsed_config['trading_options']['PAIR']
		COMPOUND_INTEREST = parsed_config['trading_options']['COMPOUND_INTEREST']
		TRADE_TOTAL = parsed_config['trading_options']['TRADE_TOTAL']            
		TRADE_SLOTS = parsed_config['trading_options']['TRADE_SLOTS']	
		#FIATS = parsed_config['trading_options']['FIATS']
		EXCLUDE_PAIRS = parsed_config['trading_options']['EXCLUDE_PAIRS']
		
		#TIME_DIFFERENCE = parsed_config['trading_options']['TIME_DIFFERENCE']
		#RECHECK_INTERVAL = parsed_config['trading_options']['RECHECK_INTERVAL']
		
		#CHANGE_IN_PRICE = parsed_config['trading_options']['CHANGE_IN_PRICE']
		STOP_LOSS = parsed_config['trading_options']['STOP_LOSS']
		TAKE_PROFIT = parsed_config['trading_options']['TAKE_PROFIT']
		
		#COOLOFF_PERIOD = parsed_config['trading_options']['COOLOFF_PERIOD']

		#CUSTOM_LIST = parsed_config['trading_options']['CUSTOM_LIST']
		#TICKERS_LIST = parsed_config['trading_options']['TICKERS_LIST']
		
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
		
		STATIC_MAIN_INFO = parsed_config['trading_options']['STATIC_MAIN_INFO']
		DISABLE_TIMESTAMPS = parsed_config['trading_options']['DISABLE_TIMESTAMPS']
		TRADING_FEE = parsed_config['trading_options']['TRADING_FEE']
		SELL_PART = parsed_config['trading_options']['SELL_PART']
		#ALLOW_NEGATIVE_SELLING = parsed_config['trading_options']['ALLOW_NEGATIVE_SELLING']
		SIGNALLING_MODULES = parsed_config['trading_options']['SIGNALLING_MODULES']
		
		SHOW_INITIAL_CONFIG = parsed_config['trading_options']['SHOW_INITIAL_CONFIG']
		SHOW_TABLE_COINS_BOUGHT = parsed_config['trading_options']['SHOW_TABLE_COINS_BOUGHT']

		USE_MOST_VOLUME_COINS = parsed_config['trading_options']['USE_MOST_VOLUME_COINS']
		COINS_MAX_VOLUME = parsed_config['trading_options']['COINS_MAX_VOLUME']
		COINS_MIN_VOLUME = parsed_config['trading_options']['COINS_MIN_VOLUME']
		
		SORT_TABLE_BY = parsed_config['trading_options']['SORT_TABLE_BY']
		REVERSE_SORT = parsed_config['trading_options']['REVERSE_SORT']
		
		MAX_HOLDING_TIME = parsed_config['trading_options']['MAX_HOLDING_TIME']
		
		PROXY_HTTP = parsed_config['script_options']['PROXY_HTTP']
		PROXY_HTTPS = parsed_config['script_options']['PROXY_HTTPS']
		
		PANIC_STOP = parsed_config['trading_options']['PANIC_STOP']
		BUY_PAUSED = parsed_config['script_options'].get('BUY_PAUSED')
		
		UPDATE_MOST_VOLUME_COINS = parsed_config['trading_options']['UPDATE_MOST_VOLUME_COINS']
		VOLATILE_VOLUME = parsed_config['trading_options']['VOLATILE_VOLUME']
		#BNB_FEE = parsed_config['trading_options']['BNB_FEE']
		#TRADING_OTHER_FEE = parsed_config['trading_options']['TRADING_OTHER_FEE']

		set_correct_mode("","")
		
		show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())
		
	except Exception as e:
		#print(e, sys.exc_info()[-1].tb_lineno)
		write_log(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}load_settings(): {languages_bot.MSG1[LANGUAGE]}: {e}{txcolors.DEFAULT}')
		write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
		pass
		
def show_func_name(function_name, items):
	try:
		global ENABLE_FUNCTION_NAME, LANGUAGE, SHOW_VARIABLES_AND_VALUE
		global SHOW_FUNCTION_NAME, SAVE_FUNCTION_NAME, LANGUAGE
		
		# try:
			# REMOTE_INSPECTOR_BOT_PORT
		# except:
			#DEFAULT_CONFIG_FILE = 'config.yml'   
			#parsed_config = load_config(DEFAULT_CONFIG_FILE)
			#REMOTE_INSPECTOR_MEGATRONMOD_PORT = parsed_config['script_options'].get('REMOTE_INSPECTOR_MEGATRONMOD_PORT')
			#REMOTE_INSPECTOR_BOT_PORT = parsed_config['script_options']['REMOTE_INSPECTOR_BOT_PORT']
			#REMOTE_INSPECTOR_MEGATRONMOD_PORT = parsed_config['script_options'].get('REMOTE_INSPECTOR_MEGATRONMOD_PORT')
			
		ENABLE_FUNCTION_NAME = False
		SHOW_VARIABLES_AND_VALUE = False
		SAVE_FUNCTION_NAME = True
		SAVE_VARIABLES_AND_VALUE = False
			 
		# if REMOTE_INSPECTOR_BOT_PORT > 0 or REMOTE_INSPECTOR_MEGATRONMOD_PORT > 0: 
			# function_variables[function_name] = {k: v for k, v in items}
		if ENABLE_FUNCTION_NAME:
			fn = str(datetime.now()) + "_" + function_name
			if SHOW_FUNCTION_NAME:  
				if SHOW_VARIABLES_AND_VALUE:
					#all_variables = dir()
					#for name in all_variables:
					for name, myvalue in items:
						#if not name.startswith('__'):
						#myvalue = eval(name)
						print(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.RED}function_name = {name}: {myvalue} {sys.getsizeof(name)}{txcolors.DEFAULT}')
				else:
					print(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.RED}function_name {name}{txcolors.DEFAULT}')
			if ENABLE_FUNCTION_NAME and SAVE_FUNCTION_NAME and SAVE_VARIABLES_AND_VALUE:
					#all_variables = dir()
					#for name in all_variables:
					for name, value in items:
						#myvalue = eval(name)
						write_log(function_name + "= \n \t" + name + ": " + str(value) + " \n \t sizeof: " + str(sys.getsizeof(value)), False, False, "list_functions.txt")
				#else:
					#write_log(fn, False, True, "list_functions.txt")
	except Exception as e:
		write_log(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.YELLOW}func_name: {languages_bot.MSG1[LANGUAGE]}: {e}{txcolors.DEFAULT}')
		write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
		pass       
	#return fn
	
def set_correct_mode(lang, mode, Ext = False):
	try:
		global TEST_MODE, BACKTESTING_MODE, USE_TESNET_IN_ONLINEMODE, USE_SIGNALLING_MODULES, MODE, LANGUAGE
		if Ext:
			   MODE = mode
			   LANGUAGE = lang
		if MODE == "ONLINE":
			TEST_MODE = False
			BACKTESTING_MODE = False
			USE_TESNET_IN_ONLINEMODE = False
			USE_SIGNALLING_MODULES = True
		elif MODE == "ONLINETESNET":
			TEST_MODE = False
			BACKTESTING_MODE = False
			USE_TESNET_IN_ONLINEMODE = True
			USE_SIGNALLING_MODULES = True
		elif MODE == "TESTMODE":
			TEST_MODE = True
			BACKTESTING_MODE = False
			USE_TESNET_IN_ONLINEMODE = False
			USE_SIGNALLING_MODULES = True
		elif MODE == "BACKTESTING":
			TEST_MODE = True
			BACKTESTING_MODE = True
			USE_TESNET_IN_ONLINEMODE = False
			USE_SIGNALLING_MODULES = False
		else:
			print(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}MODO incorrecto, modifique en config.yml...{txcolors.DEFAULT}')
			menu() #sys.exit(0)
		
		return TEST_MODE, BACKTESTING_MODE, USE_TESNET_IN_ONLINEMODE, USE_SIGNALLING_MODULES
	
	except Exception as e:
		write_log(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}set_correct_mode(): {languages_bot.MSG1[LANGUAGE]}: {e}{txcolors.DEFAULT}')
		write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
		pass    

def load_credentials(force=False):   
	try:
		global DEFAULT_CREDS_FILE, DEBUG_SETTING, TEST_MODE, USE_TESNET_IN_ONLINEMODE, DEFAULT_CREDS_FILE, creds_file, parsed_creds
		global access_key, secret_key, LANGUAGE
		
		if DEBUG_SETTING or args.debug: DEBUG = True
		print(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}All config loaded...{txcolors.DEFAULT}')
		
		if USE_TESNET_IN_ONLINEMODE:
			creds_file = args.creds if args.creds else 'test_net_' + DEFAULT_CREDS_FILE
			parsed_creds = load_config(creds_file)
			access_key, secret_key = load_correct_creds(parsed_creds)
			print(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}Cargando credenciales de la red BINANCE TESTNET...{txcolors.DEFAULT}')
			
		if not TEST_MODE and not USE_TESNET_IN_ONLINEMODE or force:
			creds_file = args.creds if args.creds else DEFAULT_CREDS_FILE
			parsed_creds = load_config(creds_file)
			access_key, secret_key = load_correct_creds(parsed_creds)
			print(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}Cargando credenciales de la red BINANCE...{txcolors.DEFAULT}')        
		
		show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())
		
	except Exception as e:
		write_log(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}load_credentials(): {languages_bot.MSG1[LANGUAGE]}: {e}{txcolors.DEFAULT}')
		write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
		pass
		
def CheckIfAliveStation(ip_address):
	try:
		# for windows
		if os.name == 'nt':
			# YELLOW - Windows Only
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
		show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())
	except Exception as e:
		write_log(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}CheckIfAliveStation(): {languages_bot.MSG1[LANGUAGE]}: {e}{txcolors.DEFAULT}')
		write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
		pass
	return alive
	
def lost_connection(error, origin):
	global lostconnection
	if not MODE == "BACKTESTING":
		if "HTTPSConnectionPool" in str(error) or "Connection aborted" in str(error):
			#print(f"HTTPSConnectionPool - {origin}")
			stop_signal_threads() #lost_connection
			if not lostconnection:
				lostconnection = True
				write_log(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {origin} - Lost connection, waiting until it is restored...{txcolors.DEFAULT}')
				while lostconnection:
					lostconnection = True
					#if "HTTPSConnectionPool" in error:
					#try:
					response = CheckIfAliveStation("google.com")
					#print(f"response: {response}")
					if response == True:
						write_log(f'{txcolors.GREEN}{languages_bot.MSG5[LANGUAGE]}: The connection has been reestablished, continuing...{txcolors.DEFAULT}')
						lostconnection = False
						load_signal_threads()
						return
					else:
						#print(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {origin} Lost connection, waiting 5 seconds until it is restored...{txcolors.DEFAULT}') 
						lostconnection = True
						time.sleep(5) #lostconnection
			else:
				while lostconnection:
					#print(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: Lost connection, waiting 5 seconds until it is restored...{txcolors.DEFAULT}')
					time.sleep(5) #lostconnection
	show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())

def timeframe_to_seconds(timeframe):
	multipliers = {
		's': 1,        # segundos
		'm': 60,       # minutos
		'h': 3600,     # horas
		'd': 86400,    # días
		'w': 604800,   # semanas
	}
	unit = timeframe[-1]
	value = int(timeframe[:-1])
	if unit in multipliers:
		return value * multipliers[unit]
	else:
		return 0
		
def renew_list(in_init=False):
	try:
		global tickers, VOLATILE_VOLUME, FLAG_PAUSE, COINS_MAX_VOLUME, COINS_MIN_VOLUME, coins_bought
		volatile_volume_empty = False
		volatile_volume_time = False
		if USE_MOST_VOLUME_COINS == True:
			today = "volatile_volume_" + str(date.today()) + ".txt"
			if VOLATILE_VOLUME == "":
				volatile_volume_empty = True
			else:
				VOLATILE_VOLUME = VOLATILE_VOLUME. replace("(", " ").replace(")","") #re.sub(r"\(.*$", "", VOLATILE_VOLUME)
				now = datetime.now()
				dt_string = datetime.strptime(now.strftime("%d-%m-%Y %H_%M_%S"), "%d-%m-%Y %H_%M_%S")
				tuple1 = dt_string.timetuple()
				timestamp1 = time.mktime(tuple1)
				#dt_string_old = datetime.strptime(VOLATILE_VOLUME.replace("(", " ").replace(")", "").replace("volatile_volume_", ""),"%y-%m-%d %H_%M_%S") + timedelta(minutes = UPDATE_MOST_VOLUME_COINS)  
				#dt_string_old = datetime.strptime(VOLATILE_VOLUME.replace("(", " ").replace(")", "").replace("volatile_volume_", ""), "%Y-%m-%d %H_%M_%S") + timedelta(minutes=UPDATE_MOST_VOLUME_COINS)
				dt_string_old = datetime.strptime(VOLATILE_VOLUME.replace("(", " ").replace(")", "").replace("volatile_volume_", ""), "%d-%m-%Y %H_%M_%S") + timedelta(minutes=UPDATE_MOST_VOLUME_COINS)
				tuple2 = dt_string_old.timetuple()
				timestamp2 = time.mktime(tuple2)
				
				if timestamp1 > timestamp2:
					volatile_volume_time = True

			if volatile_volume_time or volatile_volume_empty or not os.path.exists(today):
				print(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}A new Volatily Volume list will be created...{txcolors.DEFAULT}')
				stop_signal_threads() #renew_list
				FLAG_PAUSE = True
				
				jsonfile = prefix_type() + COINS_BOUGHT
					
				VOLATILE_VOLUME = get_volume_list()
				
				if os.path.exists(jsonfile):    
					with open(jsonfile,'r') as f:
						coins_bought_list = json.load(f)
   
					
					with open(today,'r') as f:
						lines_today = f.readlines()

					for coin_bought in list(coins_bought_list):
						coin_bought = coin_bought.replace("USDT", "") + "\n"
						if not coin_bought in list(lines_today):
							lines_today.append(coin_bought)               
							
					with open(today,'w') as f:
						f.writelines(lines_today)

					print(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}A new Volatily Volume list has been created, {len(list(coins_bought_list))} coin(s) added...{txcolors.DEFAULT}')
					FLAG_PAUSE = False
					#renew_list()
					load_signal_threads()     
		show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())
	except Exception as e:
		write_log(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.YELLOW}renew_list(): {languages_bot.MSG1[LANGUAGE]}: {e}{txcolors.DEFAULT}')
		write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
		pass
		
def remove_by_extension(extension):
	try:
		files = [item for sublist in [glob.glob(ext) for ext in [os.path.dirname(__file__) + extension]] for item in sublist]
		#print("files: ", files)
		for file in files:
			#if file.endswith(extension):
			if os.path.exists(file): 
				print(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.YELLOW}Remove {file}{txcolors.DEFAULT}')
				os.remove(file)
		show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())
	except Exception as e:
		write_log(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.YELLOW}remove_by_extension(): {languages_bot.MSG1[LANGUAGE]}: {e}{txcolors.DEFAULT}')
		write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
		pass  

def remove_by_file_name(name):
	try:
		file1 = os.path.join(os.path.dirname(__file__), name)
		file_exists1 = os.path.exists(file1)
		if file_exists1: 
			print(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.YELLOW}Remove {file1}{txcolors.DEFAULT}')
			os.remove(file1)
		show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())
	except Exception as e:
		write_log(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.YELLOW}remove_by_extension(): {languages_bot.MSG1[LANGUAGE]}: {e}{txcolors.DEFAULT}')
		write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
		pass  
		
def check_holding_time():
	global coins_bought, MAX_HOLDING_TIME, last_price
	for coin in list(coins_bought):
		buy_time = datetime.fromtimestamp(coins_bought[coin]['timestamp'] / 1000)
		current_time = datetime.fromtimestamp(last_price[coin]['time'] / 1000)
		time_held = current_time - buy_time

		if MAX_HOLDING_TIME != 0 and time_held.total_seconds() / 60 >= MAX_HOLDING_TIME:
			print(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}Vendiendo {coin} por superar el tiempo máximo de holding.{txcolors.DEFAULT}')
			sell_coin(coin)
				
def new_or_continue():
	try:
		global COINS_BOUGHT, BOT_STAT, LOG_FILE
		file_prefix = prefix_type()     

		if os.path.exists(file_prefix + str(COINS_BOUGHT)) or os.path.exists(file_prefix + str(BOT_STATS)):
			while True:
				print(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}Do you want to continue previous session?[y/n]{txcolors.DEFAULT}')
				x = input("#: ")
				if x == "y" or x == "n":
					if x == "y":
						print(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}Continuing with the session started ...{txcolors.DEFAULT}')
						break
					else:
						print(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}Deleting previous sessions ...{txcolors.DEFAULT}')
						# if not USE_MOST_VOLUME_COINS:
							# if os.path.exists(TICKERS_LIST.replace(".txt",".backup")):
								# with open(TICKERS_LIST.replace(".txt",".backup") ,'r') as f:
									# lines_tickers = f.readlines()                            
								# with open(TICKERS_LIST,'w') as f:
									# f.writelines(lines_tickers)
								# os.remove(TICKERS_LIST.replace(".txt",".backup"))     

						remove_by_file_name(file_prefix + TRADES_LOG_FILE)
						remove_by_file_name(file_prefix + TRADES_LOG_FILE.replace("csv", "html"))
						remove_by_file_name(file_prefix + TRADES_GRAPH)
						remove_by_extension("/" + file_prefix + TRADES_INDICATORS.replace(".csv", "") + "*")
						remove_by_file_name(file_prefix + COINS_BOUGHT)
						remove_by_file_name(file_prefix + BOT_STATS)
						remove_by_file_name(file_prefix + LOG_FILE)
						remove_by_file_name("signal.sig")
						remove_by_extension("/*.log")
						remove_by_extension("/*.pause")
						remove_by_extension("/*.buy")
						remove_by_extension("/*.sell")
						remove_by_file_name("positions.json")

						print(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}Session deleted, continuing ...{txcolors.DEFAULT}')
						break
				else:
					remove_by_file_name("signal.sig")
					print(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}Press the y key or the n key ...{txcolors.DEFAULT}')
		show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())
	except Exception as e:
		write_log(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.YELLOW}new_or_continue(): {languages_bot.MSG1[LANGUAGE]}: {e}{txcolors.DEFAULT}')
		write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
		pass     
	
def get_order_info():
	try:
		global client
		x = ""
		LOOP = True
		if USE_TESNET_IN_ONLINEMODE or not TEST_MODE:        
			while LOOP:
				x = ""
				print(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}Please insert OrderID. Or insert n to return.{txcolors.DEFAULT}')
				x = input('#: ')
				#x = int(x)
				if not x == 'n':
					try:
						order_info = client.get_order( #get_order_info
							symbol="BNBUSDT",
							orderId=x
						)
						print("Order Info n ", x, ": ", order_info)
					except Exception as e:
						if "not exist" in str(e):
							print(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}Order does not exist.{txcolors.DEFAULT}')
						continue
				else:
					LOOP = False
		else:
			print(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}Please enable online mode or Tesnet.{txcolors.DEFAULT}')
		show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())
	except Exception as e:
		write_log(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.YELLOW} Exception in get_order_info(): {e}{txcolors.DEFAULT}')
		write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
		pass
		
def change_key_secretkey():
	try:
		DEFAULT_CREDS_FILE = 'creds.yml'
		x = ""
		LOOP = True
		net = ''
		key = ''
		secretkey = ''
		while LOOP:
			x = ""
			print(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}Select network or insert n to return[mainnet or testnet]{txcolors.DEFAULT}')
			net = input('#: ')
			if net == 'n':
				break
			print(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}Please insert Key Or insert n to return.{txcolors.DEFAULT}')
			key = input('#: ')
			if key == 'n':
				break
			print(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}Please insert secretKey Or insert n to return.{txcolors.DEFAULT}')
			secretkey = input('#: ')
			if secretkey == 'n':
				break
			
			if net == 'mainnet':
				creds_file = args.creds if args.creds else DEFAULT_CREDS_FILE
				creds = load_config(creds_file)
				creds['prod']['access_key'] = key
				creds['prod']['secret_key'] = secretkey
				save_config(creds_file, creds)
				print(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}Key and SecretKey saved.{txcolors.DEFAULT}')
				load_settings()
				renew_list()
				load_signal_threads()
				break
				
			if net == 'testnet':
				creds_file = args.creds if args.creds else 'test_net_' + DEFAULT_CREDS_FILE
				creds = load_config(creds_file)
				creds['prod']['access_key'] = key
				creds['prod']['secret_key'] = secretkey
				save_config(creds_file, creds)
				load_settings()
				renew_list()
				load_signal_threads()
				print(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}Key and SecretKey saved.{txcolors.DEFAULT}')
				break
				
	except Exception as e:
		write_log(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.YELLOW} Exception in change_key_secretkey(): {e}{txcolors.DEFAULT}')
		write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
		pass
 
#@atexit.register
#def end_bot():
	#try:
		#menu()
		#pass
	#except Exception as e:
		#print("end_bot:", e)
		
def menu(banner1=True):
	try:
		global COINS_MAX_VOLUME, COINS_MIN_VOLUME, LOG_FILE
		global PAUSEBOT_MANUAL, BUY_PAUSED, TRADE_TOTAL, POSITION

		stop_signal_threads() #menu

		while True:
			if banner1: banner()
			#time.sleep(5) #menu
			print(f'\n')
			print(f'{txcolors.WHITE}[A]{txcolors.YELLOW}Reload Configuration{txcolors.DEFAULT}')
			print(f'{txcolors.WHITE}[B]{txcolors.YELLOW}Reload modules{txcolors.DEFAULT}')
			print(f'{txcolors.WHITE}[C]{txcolors.YELLOW}Reload Volatily Volume List{txcolors.DEFAULT}')
			try:
				BUY_PAUSED
			except:
				DEFAULT_CONFIG_FILE = 'config.yml'   
				parsed_config = load_config(DEFAULT_CONFIG_FILE)
				BUY_PAUSED = parsed_config['script_options'].get('BUY_PAUSED')
				
			if not BUY_PAUSED:
				print(f'{txcolors.WHITE}[D]{txcolors.YELLOW}Stop Purchases{txcolors.DEFAULT}')
			else:
				print(f'{txcolors.WHITE}[D]{txcolors.YELLOW}Start Purchases{txcolors.DEFAULT}')
			print(f'{txcolors.WHITE}[E]{txcolors.YELLOW}Sell Specific Coin{txcolors.DEFAULT}')
			print(f'{txcolors.WHITE}[F]{txcolors.YELLOW}Sell All Coins{txcolors.DEFAULT}')
			try:
				TRADES_LOG_FILE
			except:
				DEFAULT_CONFIG_FILE = 'config.yml'   
				parsed_config = load_config(DEFAULT_CONFIG_FILE)
				TRADES_LOG_FILE = parsed_config['script_options'].get('TRADES_LOG_FILE')
				
			print(f'{txcolors.WHITE}[G]{txcolors.YELLOW}Convert {TRADES_LOG_FILE} to html{txcolors.DEFAULT}')
			print(f'{txcolors.WHITE}[H]{txcolors.YELLOW}Make Graphics{txcolors.DEFAULT}')
			print(f'{txcolors.WHITE}[I]{txcolors.YELLOW}Get Order Information{txcolors.DEFAULT}')
			print(f'{txcolors.WHITE}[J]{txcolors.YELLOW}Change Key and Secret Key{txcolors.DEFAULT}')
			print(f'{txcolors.WHITE}[K]{txcolors.YELLOW}Continue {languages_bot.MSG5[LANGUAGE]}{txcolors.DEFAULT}')
			print(f'{txcolors.WHITE}[L]{txcolors.YELLOW}Exit {languages_bot.MSG5[LANGUAGE]}{txcolors.DEFAULT}')
			x = input('Please enter your choice: ')
			x = str(x)
			print(f'\n')
			if x == "A" or x == "a":
				load_settings()
				renew_list()
				load_signal_threads()
				print(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.YELLOW}Reaload Completed{txcolors.DEFAULT}')
				break
			elif x == "B" or x == "b":
				stop_signal_threads() #Menu
				load_signal_threads()
				print(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.YELLOW}Modules Realoaded Completed{txcolors.DEFAULT}')
				break
			elif x == "C" or x == "c":
				stop_signal_threads() # Menu - Reload Volatily Volume List
				#load_signal_threads()
				global VOLATILE_VOLUME
				if USE_MOST_VOLUME_COINS == True:
					os.remove(VOLATILE_VOLUME + ".txt")
					VOLATILE_VOLUME = get_volume_list()
					renew_list()
				else:
					print(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.YELLOW}USE_MOST_VOLUME_COINS must be true in config.yml{txcolors.DEFAULT}')
					LOOP = False
				print(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.YELLOW}VOLATILE_VOLUME Realoaded Completed{txcolors.DEFAULT}')
				load_signal_threads()
				break
			elif x == "D" or x == "d":
				if not BUY_PAUSED:
					set_config("BUY_PAUSED", True)
					PAUSEBOT_MANUAL = True
					BUY_PAUSED = True
					stop_signal_threads() #Menu -
					load_signal_threads()                  
					break
				else:
					PAUSEBOT_MANUAL = False
					set_config("BUY_PAUSED", False)
					BUY_PAUSED = False
					stop_signal_threads() #Menu -
					load_signal_threads()
					break
			elif x == "E" or x == "e":
				#part of extracted from the code of OlorinSledge
				stop_signal_threads() #Menu -
				while not x == "n":
					#last_price = get_price() #menu
					print_table_coins_bought()
					print(f'{txcolors.YELLOW}\nType in the Symbol you wish to sell. [n] to continue {languages_bot.MSG5[LANGUAGE]}.{txcolors.DEFAULT}')
					x = input("#: ")
					if x == "":
						break
					sell_coin(x.upper() + PAIR_WITH)
				load_signal_threads()		
			elif x == "F" or x == "f":
				stop_signal_threads() #Menu - 
				print(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.YELLOW}Do you want to sell all coins?[y/n]{txcolors.DEFAULT}')
				sellall = input("#: ")
				if sellall.upper() == "Y":
					sell_all('Sell all, manual choice!')
				load_signal_threads()
			elif x == "G" or x == "g":
				print(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.YELLOW}Converting {TRADES_LOG_FILE} to html...{txcolors.DEFAULT}')
				convert_csv_to_html(TRADES_LOG_FILE)
			elif x == "H" or x == "h":
				print(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.YELLOW}Make Graphics...{txcolors.DEFAULT}')
				make_graphics()
			elif x == "I" or x == "i":
				print(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.YELLOW}Get Order Information...{txcolors.DEFAULT}')
				get_order_info()
			elif x == "J" or x == "j":
				print(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.YELLOW}Change Key and Secret Key...{txcolors.DEFAULT}')
				change_key_secretkey()
			elif x == "K" or x == "k":
				print(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.YELLOW}Continuing...{txcolors.DEFAULT}')
				break
			elif x == "L" or x == "l":
				stop_signal_threads() #Menu - 
				print(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.YELLOW}Program execution ended by user!{txcolors.DEFAULT}')
				save_positions(POSITION)
				sys.exit(0)
			else:
				print(f'wrong choice: {x}')

		show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())
	except Exception as e:
		write_log(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.YELLOW} Exception in menu(): {e}{txcolors.DEFAULT}')
		write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
		pass

def create_conection_binance(force=False):
	try:

		global BACKTESTING_MODE, AMERICAN_USER, PROXY_HTTP, PROXY_HTTPS, client, parsed_config, creds_file, parsed_creds
		global access_key, secret_key, USE_TESNET_IN_ONLINEMODE
		
		if force or USE_TESNET_IN_ONLINEMODE or not TEST_MODE:
			# Authenticate with the client, Ensure API key is good before continuing
			if AMERICAN_USER:
				if PROXY_HTTP != '' or PROXY_HTTPS != '': 
					print(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT} Using proxy ...{txcolors.DEFAULT}')
					proxies = {
							'http': PROXY_HTTP,
							'https': PROXY_HTTPS
					}
					client = Client(access_key, secret_key, {'proxies': proxies}, tld='us')
				else:
					client = Client(access_key, secret_key, tld='us')
			else:
				if PROXY_HTTP != '' or PROXY_HTTPS != '': 
					print(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT} Using proxy ...{txcolors.DEFAULT}')
					proxies = {
							'http': PROXY_HTTP,
							'https': PROXY_HTTPS
					}
					client = Client(access_key, secret_key, {'proxies': proxies})
				else:
					client = Client(access_key, secret_key)

			if USE_TESNET_IN_ONLINEMODE: client.API_URL = 'https://testnet.binance.vision/api'
			# If the users has a bad / incorrect API key.
			# this will stop the script from starting, and display a helpful error.
			api_ready, msg = test_api_key(client, BinanceAPIException)
			if api_ready is not True:
				sys.exit(f'{txcolors.BLUE}{msg}{txcolors.DEFAULT}')
			#print(client.get_account()) 
	except Exception as e:
		write_log(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.YELLOW} create_conection_binance(): {e}{txcolors.DEFAULT}')
		write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
		pass
		
def banner():
	print(f'{txcolors.YELLOW}')
	tprint('BinanceTradingBot')    
	print(f'                                               by {txcolors.RED}Pantersxx3{txcolors.DEFAULT}')                   

def handle_exit(sig, frame):
	global POSITION
	save_positions(POSITION)
	#print(POSITION)
	#sleep(2)
	#save_position()
	#sys.exit(0)

if os.name == 'nt':
	try:
		import win32api
		import win32con
		
		def console_handler(sig):
			if sig == win32con.CTRL_CLOSE_EVENT:
				handle_exit(sig, None)
				return True
			return False
			
		win32api.SetConsoleCtrlHandler(console_handler, True)
	except Exception as e:
		with open("error_exit.txt", 'w') as f:
			f.write(e)
else:
	signal.signal(signal.SIGTERM, handle_exit)  # kill
	
if __name__ == '__main__':
	try:
		req_version = (3,9)
		if sys.version_info[:2] < req_version: 
			print(f'This bot requires Python version 3.9 or higher/newer. You are running version {sys.version_info[:2]} - please upgrade your Python version!!{txcolors.DEFAULT}')
			sys.exit(0)
			# Load arguments then parse settings
		#os.system('mode con: cols=155 lines=20')
		args = parse_args()
		mymodule = {}
		banner()
		print(f'{txcolors.YELLOW}BOT: {txcolors.DEFAULT}Initializing, wait a moment...{txcolors.DEFAULT}')
		discord_msg_balance_data = ""
		last_msg_discord_balance_date = datetime.now()
		
		load_settings()
		global MSG_DISCORD, LANGUAGE, DISCORD_WEBHOOK
		global COINS_BOUGHT, BOT_STATS, TRADE_SLOTS

		#if not BACKTESTING_MODE:
			#if not CheckIfAliveStation("8.8.8.8"):
				#print(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}You not have internet, Exit...{txcolors.DEFAULT}')
				#menu() #sys.exit(0)    
	 
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
						old_out.write(f'{txcolors.YELLOW}[{str(datetime.now().replace(microsecond=0))}]{txcolors.DEFAULT} {x}')
						self.nl = False
					else:
						old_out.write(x)

				def flush(self):
					pass

			sys.stdout = St_ampe_dOut()
				
		# Load creds for correct environment
	   # print(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}Loaded config below\n{json.dumps(parsed_config, indent=4)}{txcolors.DEFAULT}')
	   # print(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}Your credentials have been loaded from {creds_file}{txcolors.DEFAULT}')
			
		if MSG_DISCORD:
			DISCORD_WEBHOOK = load_discord_creds(parsed_creds)
			
		#if MSG_DISCORD:
			#MSG_DISCORD = True

		sell_all_coins = False
		sell_specific_coin = False
		
		load_credentials()

		create_conection_binance()       

		renew_list()

		update_data_coin()

		new_or_continue()       

		#null = get_historical_price()
		
		# try to load all the coins bought by the bot if the file exists and is not empty
		coins_bought = {}

		file_prefix = prefix_type()

		# path to the saved coins_bought file
		coins_bought_file_path = file_prefix + COINS_BOUGHT

		# The below mod was stolen and altered from GoGo's fork, a nice addition for keeping a historical history of profit across multiple bot sessions.
		# path to the saved bot_stats file
		bot_stats_file_path = file_prefix + BOT_STATS

		# use separate files for testing and live trading
		#TRADES_LOG_FILE = file_prefix + TRADES_LOG_FILE
		#HISTORY_LOG_FILE = file_prefix + HISTORY_LOG_FILE
				
		bot_started_datetime = datetime.now().timestamp()
		total_capital_config = TRADE_SLOTS * get_balance_test_mode() #main

		if os.path.isfile(bot_stats_file_path) and os.stat(bot_stats_file_path).st_size!= 0:
			with open(bot_stats_file_path, "r") as file:
				bot_stats = json.load(file)
				# load bot stats:
				try:                    
					bot_started_datetime = float(bot_stats['botstart_datetime'])
				except Exception as e:
					write_log(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.YELLOW}Exception on reading botstart_datetime from {bot_stats_file_path}. Exception: {e}{txcolors.DEFAULT}')
					write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
					bot_started_datetime = datetime.now().timestamp()
					#if continue fails
					pass
				
				try:
					total_capital = bot_stats['total_capital']
				except Exception as e:
					write_log(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.YELLOW}Exception on reading total_capital from {bot_stats_file_path}. Exception: {e}{txcolors.DEFAULT}')
					write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
					total_capital = TRADE_SLOTS * get_balance_test_mode() #main
					pass

				historic_profit_incfees_perc = float(bot_stats['historicProfitIncFees_Percent'])
				historic_profit_incfees_total = float(bot_stats['historicProfitIncFees_Total'])
				trade_wins = bot_stats['tradeWins']
				trade_losses = bot_stats['tradeLosses']
				session_USDT_EARNED = float(bot_stats['session_' + PAIR_WITH + '_EARNED'])
				session_USDT_LOSS = float(bot_stats['session_' + PAIR_WITH + '_LOSS'])
				session_USDT_WON = float(bot_stats['session_' + PAIR_WITH + '_WON'])
				SAVED_COINS = bot_stats['saved_coins']
				USED_COMMISSIONS = bot_stats['used_commissions']
				
				if total_capital != total_capital_config:
					historic_profit_incfees_perc = (historic_profit_incfees_total / total_capital_config) * 100

		# rolling window of prices; cyclical queue
		#historical_prices = [None] * (TIME_DIFFERENCE * RECHECK_INTERVAL)
		#hsp_head = -1

		# if saved coins_bought json file exists and it's not empty then load it
		if os.path.exists(coins_bought_file_path) and os.stat(coins_bought_file_path).st_size > 2:
			with open(coins_bought_file_path, "r") as file:
				coins_bought = json.load(file)

		print(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}{languages_bot.MSG41[LANGUAGE]} {txcolors.DEFAULT}')

		if not TEST_MODE and not USE_TESNET_IN_ONLINEMODE:
			if not args.notimeout: # if notimeout skip this (fast for dev tests)
				write_log(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {languages_bot.MSG42[LANGUAGE]}{txcolors.DEFAULT}')
				print(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {languages_bot.MSG43[LANGUAGE]}{txcolors.DEFAULT}')
				set_progress_bar("Esperando " + str(10) + " segundos", 50 , 10)
				#time.sleep(10) #Waiting 10 seconds before live trading

		#remove_external_signals('buy')
		#remove_external_signals('sell')
		#remove_external_signals('pause')
		
		# if REMOTE_INSPECTOR_BOT_PORT > 0:
			# telnet_thread = threading.Thread(target=start_telnet_server)
			# telnet_thread.daemon = True  # El hilo se detendrá si el programa principal termina
			# telnet_thread.start()
		
		load_signal_threads()

		# seed initial prices
		#get_price() #main
		TIMEOUT_COUNT=0
		READ_CONNECTERR_COUNT=0
		BINANCE_API_EXCEPTION=0	
		
		#extract of code of OlorinSledge, Thanks
		thehour = datetime.now().hour  
		coins_sold = {}
		C = 0
		while is_bot_running:
			try:
				start_time = time.time()
				# if not MODE == "BACKTESTING":
					# now = datetime.now()
					# seconds_to_wait = timeframe_to_seconds(BOT_TIMEFRAME) - (60 - now.second - now.microsecond / 1_000_000)
					# time.sleep(seconds_to_wait)				
				coins_sold = {}
				show_func_name(traceback.extract_stack(None, 2)[0][2], locals().items())
				orders, last_price, volume = buy()
				#check_holding_time()
				update_portfolio(orders, last_price, volume)
				
				if SESSION_TPSL_OVERRIDE:
					check_total_session_profit(coins_bought, last_price)
					
				coins_sold = sell_coins(False, "", last_price)
				remove_from_portfolio(coins_sold)
				update_bot_stats()
				
				if not FLAG_PAUSE:
					#extract of code of OlorinSledge, Thanks
					if RESTART_MODULES and thehour != datetime.now().hour :
						stop_signal_threads() #Main - Restart Module
						load_signal_threads()
						thehour = datetime.now().hour
						print(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.YELLOW}Modules Realoaded Completed{txcolors.DEFAULT}')
				
				if not MODE == "BACKTESTING":
					DISABLE_WAI = False
					if not DISABLE_WAI:
						if "s" in BOT_TIMEFRAME:
							time.sleep(timeframe_to_seconds(BOT_TIMEFRAME))
						else:
							current_time = time.localtime()
							seconds_until_next_minute = timeframe_to_seconds(BOT_TIMEFRAME) - current_time.tm_sec
							print(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}Esperando {seconds_until_next_minute} segundos hasta el siguiente analisis...')
							time.sleep(seconds_until_next_minute)
							C = C + 1
							if C == 15: 
								save_positions(POSITION)
								C = 0
							
				end_time = time.time()  # Registrar el tiempo al final de la iteración
				SpeedBot = end_time - start_time  # Calcular el tiempo transcurrido
				#print(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}{SpeedBot:.4f} segundos/ciclo')
				#clear()
				
				
			except ReadTimeout as rt:
				TIMEOUT_COUNT += 1
				write_log(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}We got a timeout error from Binance. Re-loop. Connection Timeouts so far: {TIMEOUT_COUNT}{txcolors.DEFAULT}')
			except ConnectionError as ce:
				READ_CONNECTERR_COUNT += 1
				write_log(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}We got a connection error from Binance. Re-loop. Connection Errors so far: {READ_CONNECTERR_COUNT}{txcolors.DEFAULT}')
			except BinanceAPIException as bapie:
				BINANCE_API_EXCEPTION += 1
				write_log(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}We got an API error from Binance. Re-loop. API Errors so far: {BINANCE_API_EXCEPTION}.\nException:\n{bapie}{txcolors.DEFAULT}')											
			except KeyboardInterrupt as e:
				menu()
		try:
			if not is_bot_running:
				if SESSION_TPSL_OVERRIDE:
					print(f'\n \n{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.YELLOW}{session_tpsl_override_msg}{txcolors.DEFAULT}')            
					sell_all(session_tpsl_override_msg, True)
					menu() #sys.exit(0)
				else:
					print(f'\n \n{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.DEFAULT}Bot terminated for some reason.{txcolors.DEFAULT}')
		except Exception as e:
			write_log(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.YELLOW} Exception in main(): {e}{txcolors.DEFAULT}')
			write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
			pass
			
	except Exception as e:
		write_log(f'{txcolors.YELLOW}{languages_bot.MSG5[LANGUAGE]}: {txcolors.YELLOW} Exception in main(): {e}{txcolors.DEFAULT}')
		write_log(f"{languages_bot.MSG2[LANGUAGE]} {sys.exc_info()[-1].tb_lineno}")
		pass