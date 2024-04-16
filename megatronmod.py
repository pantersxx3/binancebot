# Megatronmod Strategy - All in One
# Created by: Horacio Oscar Fanelli - Pantersxx3 and NokerPlay
# This mod can be used only with:
# https://github.com/pantersxx3/Binance-Bot
#
# No future support offered, use this script at own risk - test before using real funds
# If you lose money using this MOD (and you will at some point) you've only got yourself to blame!

import os
import sys
import glob
import math
import time
import threading
import pandas as pd
import pandas_ta as ta
import megatronmod_strategy as MS
import megatronmod_functions as MF
from datetime import date, datetime, timedelta
from helpers.parameters import parse_args, load_config

global config_file, creds_file, parsed_creds, parsed_config, USE_MOST_VOLUME_COINS, PAIR_WITH, SELL_ON_SIGNAL_ONLY, TEST_MODE, LOG_FILE
global COINS_BOUGHT, EXCHANGE, SCREENER, STOP_LOSS, TAKE_PROFIT, TRADE_SLOTS, BACKTESTING_MODE, BACKTESTING_MODE_TIME_START, SIGNAL_NAME
global access_key, secret_key, client, txcolors, bought, timeHold, ACTUAL_POSITION, args, BACKTESTING_MODE_TIME_START, USE_MOST_VOLUME_COINS
global BACKTESTING_MODE

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
 
BACKTESTING_MODE_TIME_START = parsed_config['script_options']['BACKTESTING_MODE_TIME_START']
PAIR_WITH = parsed_config['trading_options']['PAIR_WITH']
TRADE_SLOTS = parsed_config['trading_options']['TRADE_SLOTS']
TEST_MODE = parsed_config['script_options']['TEST_MODE']
SELL_ON_SIGNAL_ONLY = parsed_config['trading_options']['SELL_ON_SIGNAL_ONLY']
LOG_FILE = parsed_config['script_options'].get('LOG_FILE')
USE_MOST_VOLUME_COINS = parsed_config['trading_options']['USE_MOST_VOLUME_COINS']
BACKTESTING_MODE = parsed_config['script_options']['BACKTESTING_MODE']
USE_SIGNALLING_MODULES =  False if BACKTESTING_MODE else True

MICROSECONDS = 2
 
def analyze(d, pairs, buy=True):
    try:
        global BACKTESTING_MODE

        signal_coins1 = []
        signal_coins2 = []
        analysis1MIN = {}
        buySignal00 = False
        sellSignal00 = False
        
        if TEST_MODE:
            file_prefix = 'test_'
        else:
            file_prefix = 'live_'     
    
        print(f'{txcolors.SELL_PROFIT}{SIGNAL_NAME}: {txcolors.DEFAULT}Analyzing {len(pairs)} coins...{txcolors.DEFAULT}')
        
        for pair in pairs:
            position2 = MF.read_position_csv(pair)
            if not os.path.exists(pair + '.csv'): 
                print(f'{txcolors.SELL_PROFIT}{SIGNAL_NAME}: {txcolors.DEFAULT}Whaiting for Download Data...{txcolors.DEFAULT}')
                if USE_SIGNALLING_MODULES:
                    while not os.path.exists(pair + '.csv'):
                        time.sleep(1/1000) #Wait for download 
                else:
                    print(f'{txcolors.SELL_PROFIT}{SIGNAL_NAME}: {txcolors.DEFAULT}Data file not found. Whaiting for Download Data...{txcolors.DEFAULT}')
                        
            analysis1MIN = MF.get_analysis(d, '1m', pair, position2, True, 1000)

            if not analysis1MIN.empty:
                CLOSE_1MIN = round(float(analysis1MIN['Close'].iloc[-1]),5)
                #OPEN_1MIN = round(float(analysis1MIN['Open'].iloc[-1]),5) 
                #CLOSE_1MIN_ANT = round(float(analysis1MIN['Close'].iloc[-2]),5)
                time1 = 0
                #TIME_1M = analysis1MIN['time'].iloc[-1]
                #time1 = int(TIME_1M)/1000
                #time_1MIN = datetime.fromtimestamp(int(time1)).strftime("%d/%m/%y %H:%M:%S") 
                buySignal00 = MS.buy(analysis1MIN, CLOSE_1MIN, pair)
                sellSignal00 = MS.sell(analysis1MIN, CLOSE_1MIN, pair)

                analysis1MIN = {}
                
                if buy:
                    bought_at, timeHold, coins_bought = MF.load_json(pair)            
                    if coins_bought < TRADE_SLOTS and bought_at == 0:                
                        if buySignal00:
                            signal_coins1.append({ 'time': position2, 'symbol': pair, 'price': CLOSE_1MIN})
                            MF.write_log(f'BUY {CLOSE_1MIN} {position2}', LOG_FILE, False, False)
                            if USE_SIGNALLING_MODULES:
                                with open(SIGNAL_FILE_BUY,'w+') as f:
                                    f.write(pair + '\n') 
                                break
                
                if SELL_ON_SIGNAL_ONLY:
                    bought_at, timeHold, coins_bought = MF.load_json(pair)
                    if float(bought_at) != 0 and float(coins_bought) != 0 and float(CLOSE_1MIN) != 0:                       
                        if sellSignal00 and float(bought_at) != 0:
                            signal_coins2.append({ 'time': position2, 'symbol': pair, 'price': CLOSE_1MIN})
                            MF.write_log(f'SELL {CLOSE_1MIN} {bought_at} {position2}', LOG_FILE, False, False)
                            if USE_SIGNALLING_MODULES:
                                with open(SIGNAL_FILE_SELL,'w+') as f:
                                    f.write(pair + '\n')
                                break 
    except Exception as e:
        MF.write_log(f'{txcolors.DEFAULT}{SIGNAL_NAME}: {txcolors.SELL_LOSS} - Exception: {e}{txcolors.DEFAULT}', SIGNAL_NAME + '.log', True, False)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        MF.write_log('Error on line ' + str(exc_tb.tb_lineno), SIGNAL_NAME + '.log', True, False)
        pass
    return signal_coins1, signal_coins2

def do_work():
    try:
        signalcoins1 = []
        signalcoins2 = []
        pairs = {}
        dataBuy = {}
        dataSell = {}
        
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
            if len(signalcoins1) > 0:
                print(f'{txcolors.SELL_PROFIT}{SIGNAL_NAME}: {txcolors.DEFAULT}{len(signalcoins1)} coins of {len(pairs)} with Buy Signals. Waiting {1} minutes for next analysis.{txcolors.DEFAULT}')
                time.sleep(MICROSECONDS)
            else:
                print(f'{txcolors.SELL_PROFIT}{SIGNAL_NAME}: {txcolors.DEFAULT}{len(signalcoins1)} coins of {len(pairs)} with Buy Signals. Waiting {1} minutes for next analysis.{txcolors.DEFAULT}')
                time.sleep(MICROSECONDS)
    except Exception as e:
        MF.write_log(f'{txcolors.DEFAULT}{SIGNAL_NAME}: {txcolors.SELL_LOSS} - Exception: do_work(): {e}{txcolors.DEFAULT}', SIGNAL_NAME + '.log', True, False)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        MF.write_log('Error on line ' + str(exc_tb.tb_lineno), SIGNAL_NAME + '.log', True, False)
        pass
        #except KeyboardInterrupt as ki:
            #pass