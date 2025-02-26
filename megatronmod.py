# Megatronmod Strategy - All in One
# Created by: Horacio Oscar Fanelli - Pantersxx3 and NokerPlay
# This mod can be used only with:
# https://github.com/pantersxx3/Binance-Bot
#
# No future support offered, use this script at own risk - test before using real funds
# If you lose money using this MOD (and you will at some point) you've only got yourself to blame!

import os
import sys
import json
import glob
import math
import time
import socket
import threading
import pandas as pd
import pandas_ta as ta
import megatronmod_strategy as MS
import megatronmod_functions as MF
from datetime import date, datetime, timedelta
from helpers.parameters import parse_args, load_config
import traceback

# Diccionario para almacenar las variables locales de cada función
variables_funciones = {}

global config_file, creds_file, parsed_creds, parsed_config, USE_MOST_VOLUME_COINS, PAIR_WITH, SELL_ON_SIGNAL_ONLY, TEST_MODE, LOG_FILE
global COINS_BOUGHT, EXCHANGE, SCREENER, STOP_LOSS, TAKE_PROFIT, TRADE_SLOTS, BACKTESTING_MODE, BACKTESTING_MODE_TIME_START, SIGNAL_NAME
global access_key, secret_key, client, txcolors, bought, timeHold, ACTUAL_POSITION, args, BACKTESTING_MODE_TIME_START, USE_MOST_VOLUME_COINS
global TEST_MODE, BACKTESTING_MODE, USE_TESNET_IN_ONLINEMODE, USE_SIGNALLING_MODULES, LANGUAGE, BOT_TIMEFRAME

class txcolors:
    BUY = '\033[92m'
    WARNING = '\033[93m'
    SELL_LOSS = '\033[91m'
    SELL_PROFIT = '\033[32m'
    DIM = '\033[2m\033[35m'
    Red = '\033[31m'
    DEFAULT = '\033[39m'

DEFAULT_CONFIG_FILE = 'config.yml'
SIGNAL_NAME = 'MEGATRONMOD'
SIGNAL_FILE_BUY = 'signals/' + SIGNAL_NAME + '.buy'
SIGNAL_FILE_SELL ='signals/' + SIGNAL_NAME + '.sell' 
 
# Settings
args = parse_args()
config_file = args.config if args.config else DEFAULT_CONFIG_FILE
parsed_config = load_config(config_file)
 
global TEST_MODE, BACKTESTING_MODE, USE_TESNET_IN_ONLINEMODE, USE_SIGNALLING_MODULES, MODE, LANGUAGE, REMOTE_INSPECTOR_MEGATRONMOD_PORT

PAIR_WITH = parsed_config['trading_options']['PAIR_WITH']
TRADE_SLOTS = parsed_config['trading_options']['TRADE_SLOTS']
MODE = parsed_config['script_options']['MODE']
SELL_ON_SIGNAL_ONLY = parsed_config['trading_options']['SELL_ON_SIGNAL_ONLY']
LOG_FILE = parsed_config['script_options'].get('LOG_FILE')
USE_MOST_VOLUME_COINS = parsed_config['trading_options']['USE_MOST_VOLUME_COINS']
LANGUAGE = parsed_config['script_options']['LANGUAGE']
REMOTE_INSPECTOR_MEGATRONMOD_PORT = parsed_config['script_options']['REMOTE_INSPECTOR_MEGATRONMOD_PORT']
BOT_TIMEFRAME = parsed_config['script_options']['BOT_TIMEFRAME']
#USE_SIGNALLING_MODULES =  False if BACKTESTING_MODE else True

MICROSECONDS = 2

        
def register_func_name(function_name, items):
    global variables_funciones
    variables_funciones[function_name] = {k: v for k, v in items}
    
def convertir_a_str(value):
    if isinstance(value, dict):
        return str(value)
    elif isinstance(value, list):
        return str(value)
    elif isinstance(value, pd.DataFrame):
        return value.to_string()  # Convierte el DataFrame a texto legible
    else:
        return str(value)
        
def handle_client(client_socket):
    try:
        global variables_funciones
        while True:
            request = client_socket.recv(1024).decode().strip() 
            parts = request.split(".")
            if len(parts) == 2:
                funcion = parts[0]
                variable = parts[1]

                if variable == "all_val":
                    all_vars = "\n".join([f"{k}: {convertir_a_str(v)}" for k, v in variables_funciones[funcion].items()])
                    response = f"{funcion}:\n {all_vars}\n <END_COMMAND>"
                else:
                    if funcion in variables_funciones and variable in variables_funciones[funcion]:
                        response = f"{funcion}.{variable}: {variables_funciones[funcion][variable]}\n<END_COMMAND>"
                    else:
                        response = f"Variable {variable} no encontrada en la función {funcion}\n<END_COMMAND>"
            else:
                response = "Comando no reconocido. Use 'funcion.variable'\n<END_COMMAND>"
            
            client_socket.send(response.encode()) 
            
    except Exception as e:
        MF.write_log(f'{txcolors.DEFAULT}{SIGNAL_NAME}: {txcolors.SELL_LOSS} - Exception: {e}{txcolors.DEFAULT}', SIGNAL_NAME + '.log', True, False)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        MF.write_log('Error on line ' + str(exc_tb.tb_lineno), SIGNAL_NAME + '.log', True, False)
        pass  
        
def start_telnet_server():
    if REMOTE_INSPECTOR_MEGATRONMOD_PORT > 0:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('0.0.0.0', REMOTE_INSPECTOR_MEGATRONMOD_PORT))  # Escucha en todas las interfaces en el puerto 9999
        server.listen(5)
        print(f'{txcolors.SELL_PROFIT}{SIGNAL_NAME}: {txcolors.DEFAULT} Servidor Telnet: escuchando en el puerto 9999')

        while True:
            client_socket, addr = server.accept()
            print(f'{txcolors.SELL_PROFIT}{SIGNAL_NAME}: {txcolors.DEFAULT} Servidor Telnet: Conexión aceptada desde {addr}')
            
            # Crear un hilo separado para manejar la conexión
            client_handler = threading.Thread(target=handle_client, args=(client_socket,))
            client_handler.start()
        
def analyze(d, pairs, buy=True):
	try:
		global TEST_MODE, BACKTESTING_MODE, USE_TESNET_IN_ONLINEMODE, USE_SIGNALLING_MODULES, MODE, LANGUAGE

		signal_coins1 = []
		signal_coins2 = []
		analysis = {}
		buySignal00 = False
		sellSignal00 = False
		position2 = 0
        
		from Boot import set_correct_mode
		TEST_MODE, BACKTESTING_MODE, USE_TESNET_IN_ONLINEMODE, USE_SIGNALLING_MODULES = set_correct_mode(LANGUAGE, MODE, True)
        
		if TEST_MODE:
			file_prefix = 'test_'
		else:
			file_prefix = 'live_'     
    
		print(f'{txcolors.SELL_PROFIT}{SIGNAL_NAME}: {txcolors.DEFAULT}Analyzing {len(pairs)} coins...{txcolors.DEFAULT}')
        
        
		for pair in pairs:
			if BACKTESTING_MODE:
				position2 = MF.read_position_csv(pair)
				if not os.path.exists(pair + '.csv'): 
					print(f'{txcolors.SELL_PROFIT}{SIGNAL_NAME}: {txcolors.DEFAULT}Whaiting for Download Data...{txcolors.DEFAULT}')
					if USE_SIGNALLING_MODULES:
						while not os.path.exists(pair + '.csv'):
							time.sleep(1/1000) #Wait for download 
					else:
						print(f'{txcolors.SELL_PROFIT}{SIGNAL_NAME}: {txcolors.DEFAULT}Data file not found. Whaiting for Download Data...{txcolors.DEFAULT}')
                        
			analysis = MF.get_analysis(d, BOT_TIMEFRAME, pair, position2, 200)

			if not analysis.empty:
				CLOSE = float(analysis['Close'].iloc[-1]) #round(float(analysis['Close'].iloc[-1]),6)
                #OPEN_1MIN = round(float(analysis['Open'].iloc[-1]),6) 
                #CLOSE_ANT = round(float(analysis['Close'].iloc[-2]),6)
				time1 = 0
                #TIME_1M = analysis['time'].iloc[-1]
                #time1 = int(TIME_1M)/1000
                #time_1MIN = datetime.fromtimestamp(int(time1)).strftime("%d/%m/%y %H:%M:%S") 
				buySignal00 = MS.buy(analysis, CLOSE, pair)
				sellSignal00 = MS.sell(analysis, CLOSE, pair)

				analysis = {}
                
				if buy:
					bought_at, timeHold, coins_bought = MF.load_json(pair)            
					if coins_bought < TRADE_SLOTS and bought_at == 0:                
						if buySignal00:
							signal_coins1.append({ 'time': position2, 'symbol': pair, 'price': CLOSE})
                            #MF.write_log(f'BUY {CLOSE} {position2}', LOG_FILE, False, False)
							if USE_SIGNALLING_MODULES:
								print(f'{txcolors.SELL_PROFIT}{SIGNAL_NAME}: {txcolors.DEFAULT}Buy signal detected...{txcolors.DEFAULT}')
								with open(SIGNAL_FILE_BUY,'w+') as f:
									f.write(pair + '\n') 
                                #break
                
				if SELL_ON_SIGNAL_ONLY:
					bought_at, timeHold, coins_bought = MF.load_json(pair)
					if float(bought_at) != 0 and float(coins_bought) != 0 and float(CLOSE) != 0:                       
						if sellSignal00 and float(bought_at) != 0:
							signal_coins2.append({ 'time': position2, 'symbol': pair, 'price': CLOSE})
							print(f'{txcolors.SELL_PROFIT}{SIGNAL_NAME}: {txcolors.DEFAULT}Sell signal detected...{txcolors.DEFAULT}')
                            #MF.write_log(f'SELL {CLOSE} {bought_at} {position2}', LOG_FILE, False, False)
							if USE_SIGNALLING_MODULES:
								with open(SIGNAL_FILE_SELL,'w+') as f:
									f.write(pair + '\n')
                                    #break                      
		register_func_name("analyze", locals().items())
	except Exception as e:
		MF.write_log(f'{txcolors.DEFAULT}{SIGNAL_NAME}: {txcolors.SELL_LOSS} - Exception: {e}{txcolors.DEFAULT}', SIGNAL_NAME + '.log', True, False)
		exc_type, exc_obj, exc_tb = sys.exc_info()
		MF.write_log('Error on line ' + str(exc_tb.tb_lineno), SIGNAL_NAME + '.log', True, False)
		pass
	return signal_coins1, signal_coins2

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

def do_work():
	try:
		global TEST_MODE, BACKTESTING_MODE, USE_TESNET_IN_ONLINEMODE, USE_SIGNALLING_MODULES, MODE, LANGUAGE, BOT_TIMEFRAME
		signalcoins1 = []
		signalcoins2 = []
		pairs = {}
		dataBuy = {}
		dataSell = {}
        
		from Boot import set_correct_mode
		TEST_MODE, BACKTESTING_MODE, USE_TESNET_IN_ONLINEMODE, USE_SIGNALLING_MODULES = set_correct_mode(LANGUAGE, MODE, True)
        
        #telnet_thread = threading.Thread(target=start_telnet_server)
        #telnet_thread.daemon = True  # El hilo se detendrá si el programa principal termina
        #telnet_thread.start()
        
		if USE_MOST_VOLUME_COINS == True:
			TICKERS = 'volatile_volume_' + str(date.today()) + '.txt'
		else:
			TICKERS = 'tickers.txt'            

		for line in open(TICKERS):
			pairs=[line.strip() + PAIR_WITH for line in open(TICKERS)] 
            
		while True:
            #if not threading.main_thread().is_alive(): exit()
			if os.path.exists("signal.sig"):
				print(f'{txcolors.SELL_PROFIT}{SIGNAL_NAME}: {txcolors.DEFAULT}Exit...{txcolors.DEFAULT}') 
				os.remove("signal.sig")
				sys.exit(0)
			print(f'{txcolors.SELL_PROFIT}{SIGNAL_NAME}: {txcolors.DEFAULT}Analyzing {len(pairs)} coins...{txcolors.DEFAULT}') 
			if BACKTESTING_MODE:
				while os.path.exists('ok.ok'):
					time.sleep(1/1000) #do_work
				signalcoins1, signalcoins2 = analyze(pd.DataFrame([]), pairs, True)
				with open('ok.ok','w') as f:
					f.write('1')
			else:
				signalcoins1, signalcoins2 = analyze(pd.DataFrame([]), pairs, True)
			time.sleep(MICROSECONDS) #do_work
            # if len(signalcoins1) > 0:
                # print(f'{txcolors.SELL_PROFIT}{SIGNAL_NAME}: {txcolors.DEFAULT}{len(signalcoins1)} coins of {len(pairs)} with Buy Signals. Waiting {1} minutes for next analysis.{txcolors.DEFAULT}')
                # #time.sleep(MICROSECONDS)
            # else:
                # print(f'{txcolors.SELL_PROFIT}{SIGNAL_NAME}: {txcolors.DEFAULT}{len(signalcoins1)} coins of {len(pairs)} with Buy Signals. Waiting {1} minutes for next analysis.{txcolors.DEFAULT}')
                # #time.sleep(MICROSECONDS)            
			DISABLE_WAI = False
			if not DISABLE_WAI:
				if "s" in BOT_TIMEFRAME:
					time.sleep(timeframe_to_seconds(BOT_TIMEFRAME))
				else:
					current_time = time.localtime()
					seconds_until_next_minute = timeframe_to_seconds(BOT_TIMEFRAME) - current_time.tm_sec
					print(f'{txcolors.SELL_PROFIT}{SIGNAL_NAME}: {txcolors.DEFAULT}Esperando {seconds_until_next_minute} segundos hasta el siguiente analisis...')
					time.sleep(seconds_until_next_minute)    
            
			register_func_name("do_work", locals().items())
	except Exception as e:
		MF.write_log(f'{txcolors.DEFAULT}{SIGNAL_NAME}: {txcolors.SELL_LOSS} - Exception: do_work(): {e}{txcolors.DEFAULT}', SIGNAL_NAME + '.log', True, False)
		exc_type, exc_obj, exc_tb = sys.exc_info()
		MF.write_log('Error on line ' + str(exc_tb.tb_lineno), SIGNAL_NAME + '.log', True, False)
		pass
		#except KeyboardInterrupt as ki:
			#pass