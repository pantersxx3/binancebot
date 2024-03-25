# Megatronmod Strategy - All in One
# Created by: Horacio Oscar Fanelli - Pantersxx3 and NokerPlay
# This mod can be used only with:
# https://github.com/pantersxx3/Binance-Bot
#
# No future support offered, use this script at own risk - test before using real funds
# If you lose money using this MOD (and you will at some point) you've only got yourself to blame!

from tradingview_ta import TA_Handler, Interval, Exchange
from binance.client import Client, BinanceAPIException
from helpers.parameters import parse_args, load_config
from datetime import date, datetime, timedelta
from collections import defaultdict
import pandas_ta as ta #pta
import pandas as pd
import threading
import os
import sys
import glob
import math
import time
import talib
import ccxt
import re
import json
import numpy as np
import random

# Load creds modules
from helpers.handle_creds import (
    load_correct_creds, load_discord_creds
    )

global config_file, creds_file, parsed_creds, parsed_config, USE_MOST_VOLUME_COINS, PAIR_WITH, SELL_ON_SIGNAL_ONLY, TEST_MODE, LOG_FILE
global COINS_BOUGHT, EXCHANGE, SCREENER, STOP_LOSS, TAKE_PROFIT, TRADE_SLOTS, BACKTESTING_MODE, BACKTESTING_MODE_TIME_START, SIGNAL_NAME
global access_key, secret_key, client, txcolors, bought, timeHold, ACTUAL_POSITION, args, BACKTESTING_MODE_TIME_START


class txcolors:
    BUY = '\033[92m'
    WARNING = '\033[93m'
    SELL_LOSS = '\033[91m'
    SELL_PROFIT = '\033[32m'
    DIM = '\033[2m\033[35m'
    Red = '\033[31m'
    DEFAULT = '\033[39m'
    
DEFAULT_CONFIG_FILE = 'config.yml'
DEFAULT_CREDS_FILE = 'creds.yml'

# Settings
args = parse_args()
config_file = args.config if args.config else DEFAULT_CONFIG_FILE
creds_file = args.creds if args.creds else DEFAULT_CREDS_FILE
parsed_creds = load_config(creds_file)
parsed_config = load_config(config_file)
access_key, secret_key = load_correct_creds(parsed_creds)

LANGUAGE = parsed_config['script_options']['LANGUAGE']
USE_MOST_VOLUME_COINS = parsed_config['trading_options']['USE_MOST_VOLUME_COINS']
BACKTESTING_MODE_TIME_START = parsed_config['script_options']['BACKTESTING_MODE_TIME_START']
PAIR_WITH = parsed_config['trading_options']['PAIR_WITH']
SELL_ON_SIGNAL_ONLY = parsed_config['trading_options']['SELL_ON_SIGNAL_ONLY']
TEST_MODE = parsed_config['script_options']['TEST_MODE']
LOG_FILE = parsed_config['script_options'].get('LOG_FILE')
COINS_BOUGHT = parsed_config['script_options'].get('COINS_BOUGHT')
STOP_LOSS = parsed_config['trading_options']['STOP_LOSS']
TAKE_PROFIT = parsed_config['trading_options']['TAKE_PROFIT']
TRADES_GRAPH = parsed_config['script_options'].get('TRADES_GRAPH')
TRADES_INDICATORS = parsed_config['script_options'].get('TRADES_INDICATORS')
TRADE_SLOTS = parsed_config['trading_options']['TRADE_SLOTS']
BACKTESTING_MODE = parsed_config['script_options']['BACKTESTING_MODE']
BACKTESTING_MODE_TIME_START = parsed_config['script_options']['BACKTESTING_MODE_TIME_START']
MICROSECONDS = 2

if USE_MOST_VOLUME_COINS == True:
    TICKERS = 'volatile_volume_' + str(date.today()) + '.txt'
else:
    TICKERS = 'tickers.txt'
            
#ACTUAL_POSITION = 0
SIGNAL_NAME = 'MEGATRONMOD'
#CREATE_BUY_SELL_FILES = True
#DEBUG = True
EXCHANGE = 'BINANCE'
SCREENER = 'CRYPTO'

#JSON_FILE_BOUGHT = SIGNAL_NAME + '.json'

                                    
def write_log(logline, LOGFILE = LOG_FILE, show = True, time = False):
    try:
        if TEST_MODE:
            file_prefix = 'test_'
        else:
            file_prefix = 'live_'  
        with open(file_prefix + LOGFILE,'a') as f:
            ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
            result = ansi_escape.sub('', logline)
            if show: print(f'{logline}')
            if time:
                timestamp = datetime.now().strftime('%Y-%d-%m %H:%M:%S') + ','                    
            else:
                timestamp = ''
            f.write(timestamp + result + '\n') 
    except Exception as e:
        print(f'{txcolors.DEFAULT}{SIGNAL_NAME} write_log: Exception in function: {e}{txcolors.DEFAULT}')
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print('Error on line ' + str(exc_tb.tb_lineno))
        exit(1)

def read_position_csv(coin):
    try:
        pos1 = 0
        if os.path.exists(coin + '.position'):
            f = open(coin + '.position', 'r')
            pos1 = int(f.read().replace('.0', ''))
            f.close()
        else:
            pos1 = -1
            #os.remove(coin + '.position')
    except Exception as e:
        write_log(f'{txcolors.DEFAULT}{SIGNAL_NAME}: {txcolors.SELL_LOSS} - Exception: read_position_csv(): {e}{txcolors.DEFAULT}', SIGNAL_NAME + '.log', True, False)
        write_log('Error on line ' + str(exc_tb.tb_lineno), SIGNAL_NAME + '.log', True, False)
        pass
    return pos1

def get_analysis(d, tf, p, position1=0, el_profe=False, num_records=1000):
    try:
        global BACKTESTING_MODE
        c = pd.DataFrame([])
        e = 0
        if BACKTESTING_MODE:
            if position1 > 0:
                if d.empty:
                    d = pd.read_csv(p + '.csv')
                    d.columns = ['time', 'Open', 'High', 'Low', 'Close']
                    d['Close'] = d['Close'].astype(float)
                else:
                    d['Close'] = d['Close'].astype(float)
                c = d.query('time < @position1').tail(num_records)
                inttime = int(position1)/1000            
                position2 = c['time'].iloc[0]
                print(f'{txcolors.SELL_PROFIT}{SIGNAL_NAME}: {txcolors.DEFAULT}{BACKTESTING_MODE_TIME_START} - Posicion actual {datetime.fromtimestamp(inttime).strftime("%d/%m/%y %H:%M:%S")} - {position2} - {position1}...{txcolors.DEFAULT}')
                d = pd.DataFrame([])
        else:            
            client = Client(access_key, secret_key)
            klines = client.get_historical_klines(symbol=p, interval=tf, start_str=str(num_records) + 'min ago UTC', limit=num_records)
            c = pd.DataFrame(klines)
            c.columns = ['time', 'Open', 'High', 'Low', 'Close', 'Volume', 'CloseTime', 'QuoteAssetVolume', 'Trades', 'TakerBuyBase', 'TakerBuyQuote', 'Ignore']
            c = c.drop(c.columns[[5, 6, 7, 8, 9, 10, 11]], axis=1)
            c['time'] = pd.to_datetime(c['time'], unit='ms')
            c['Close'] = c['Close'].astype(float)
    except Exception as e:
        write_log(f'{txcolors.DEFAULT}{SIGNAL_NAME}: {txcolors.SELL_LOSS} - Exception: get_analysis(): {e}{txcolors.DEFAULT}', SIGNAL_NAME + '.log', True, False)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        write_log('Error on line ' + str(exc_tb.tb_lineno), SIGNAL_NAME + '.log', True, True) 
    return c

   
def crossunder(arr1, arr2):
    CrossUnder = 0
    if not arr1 == None or not arr2 == None:
        if arr1 != arr2:
            if arr1 > arr2 and arr2 < arr1:
                CrossUnder = True
            else:
                CrossUnder = False
        else:
            CrossUnder = False
    return CrossUnder

def crossover(arr1, arr2):
    CrossOver = 0
    if not arr1 == None or not arr2 == None:
        if arr1 != arr2:
            if arr1 < arr2 and arr2 > arr1:
                CrossOver = True
            else:
                CrossOver = False
        else:
            CrossOver = False
    return CrossOver
    
def cross(arr1, arr2):
    if round(arr1,5) == round(arr2,5):
        Cross = True
    else:
        Cross = False
    return Cross
    
def isNone(var):
    if var == None:
        r = 0
    else:
        r = var
    return r
    
def load_json(p):
    try:
        bought_analysis1MIN = {}
        value1 = 0
        value2 = 0
        value3 = 0
        if TEST_MODE:
            file_prefix = 'test_'
        else:
            file_prefix = 'live_'
        coins_bought_file_path = file_prefix + COINS_BOUGHT
        if os.path.exists(coins_bought_file_path) and os.path.getsize(coins_bought_file_path) > 2:
            with open(coins_bought_file_path,'r') as f:
                bought_analysis1MIN = json.load(f)
            for analysis1MIN in bought_analysis1MIN.keys():
                value3 = value3 + 1                
            if p in bought_analysis1MIN:
                value1 = round(float(bought_analysis1MIN[p]['bought_at']),5)
                value2 = round(float(bought_analysis1MIN[p]['timestamp']),5)
                bought_analysis1MIN = {}
    except Exception as e:
        write_log(f'{txcolors.DEFAULT}{SIGNAL_NAME}: {txcolors.SELL_LOSS} - Exception: load_json(): {e}{txcolors.DEFAULT}', SIGNAL_NAME + '.log', True, False)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        write_log('Error on line ' + str(exc_tb.tb_lineno), SIGNAL_NAME + '.log', True, False)
    return value1, value2, value3

def isfloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False
        
def print_dic(dic, with_key=False, with_value=True):
    try:
        str1 = ''
        for key, value in dic.items():
            if with_key == False:
                if not value == {}:
                    if isfloat(value):
                        str1 = str1 + str(round(float(value),5)) + ','
                    else:
                        str1 = str1 + str(value) + ','
            else:
                if with_value:
                    if not value == {}:
                        if isfloat(value):    
                            str1 = str1 + str(key) + ':' + str(round(float(value),5)) + ','
                        else:
                            str1 = str1 + str(key) + ':' + str(value) + ','
                else:
                    str1 = str1 + str(key) + ','
    except Exception as e:
        write_log(f'{txcolors.DEFAULT}{SIGNAL_NAME}: {txcolors.SELL_LOSS} - Exception: print_dic(): {e}{txcolors.DEFAULT}', SIGNAL_NAME + '.log', True, False)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        write_log('Error on line ' + str(exc_tb.tb_lineno), SIGNAL_NAME + '.log', True, False)
    return str1[:-1]
    
def list_indicators():
    try:
        list_variables = {}
        all_variables = dir()
        for name in all_variables:
            if name.endswith('_1MIN') and not name.endswith('_5MIN'):
                myvalue = round(float(eval(name)), 5)
                #list_variables = {name : myvalue}
                list_variables = {myvalue}
    except Exception as e:
        write_log(f'{txcolors.DEFAULT}{SIGNAL_NAME}: {txcolors.Red}Exception: list_indicators(): {e}', SIGNAL_NAME + '.log', True, False)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        write_log('Error on line ' + str(exc_tb.tb_lineno), SIGNAL_NAME + '.log', True, False)
        pass
    return list_variables
 
def defaultdict_from_dict(d):
    nd = lambda: defaultdict(nd)
    ni = nd()
    ni.update(d)
    return ni

def ret_time(df):
    TIME_1M = df['time'].iloc[-1]
    if not isinstance(TIME_1M, pd._libs.tslibs.timestamps.Timestamp):
        time1 = int(TIME_1M)/1000
        time_1MIN = datetime.fromtimestamp(int(time1)).strftime("%d/%m/%y %H:%M:%S")
    else:
        time_1MIN = TIME_1M
    return time_1MIN
    
def save_indicator(items):
    try:

        if TEST_MODE:
                file_prefix = 'test_'
        else:
            file_prefix = 'live_'                
         
        data_indicator = pd.DataFrame([]) 
        csv_indicators = file_prefix + TRADES_INDICATORS
        
        for name, myvalue in list(items):
            if name.endswith('_IND'): # or name == 'time_1MIN':
                myvalue = str(myvalue).strip()
                data_indicators = pd.DataFrame([])
                data_indicators[name] = [myvalue] 
                   
                if not data_indicators.empty:
                    data_indicators.to_csv(csv_indicators.replace('.csv', '') + "_" + name + '.csv', mode='a', index=False, header=False)

    except Exception as e:
        write_log(f'{txcolors.DEFAULT}{SIGNAL_NAME}: {txcolors.Red}Exception: save_indicator(): {e}', SIGNAL_NAME + '.log', True, False)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        write_log('Error on line ' + str(exc_tb.tb_lineno), SIGNAL_NAME + '.log', True, False)
        pass

# def save_strategy(items):
    # try:
        # TRADES_STRATEGY = 'strategy.csv'
        # if TEST_MODE:
                # file_prefix = 'test_'
        # else:
            # file_prefix = 'live_'                
         
        # data_strategy = pd.DataFrame([]) #buySignal price sellSignal price result
        # csv_strategy  = file_prefix + TRADES_STRATEGY
        
        # for name, myvalue in list(items):
            # if name.startswith('buy') or name.startswith('sell'):
                # myvalue = str(myvalue).strip()
                # data_strategy = pd.DataFrame([])
                # if 'buy' in name:
                    # data_strategy [name] = [myvalue] 
                   
                # if not data_strategy.empty:
                    # data_strategy.to_csv(csv_strategy, mode='a', index=False, header=False)

    # except Exception as e:
        # write_log(f'{txcolors.DEFAULT}{SIGNAL_NAME}: {txcolors.Red}Exception: save_indicator(): {e}', SIGNAL_NAME + '.log', True, False)
        # exc_type, exc_obj, exc_tb = sys.exc_info()
        # write_log('Error on line ' + str(exc_tb.tb_lineno), SIGNAL_NAME + '.log', True, False)
        # pass
        
def Ichimoku(DF_Data, TENKA, KIJUN, SENKU):
    df = pd.DataFrame(DF_Data)
    df[['spanA', 'spanB', 'tenkan_sen', 'kijun_sen', 'chikou_span']] = ta.ichimoku(DF_Data['High'], DF_Data['Low'], DF_Data['Close'], TENKA, KIJUN, SENKU)
    spanA = round(df['spanA'], 4)
    spanB = round(df['spanB'], 4)
    tenkan_sen_IND = round(df['tenkan_sen'], 4)
    kijun_sen_IND = round(df['kijun_sen'], 4)
    chikou_span_IND = round(df['chikou_span'], 4)
    #time_1MIN = ret_time(DF_Data)
    save_indicator(locals().items())
    return spanA_IND, spanB_IND, tenkan_sen_IND, kijun_sen_IND, chikou_span_IND
    
def BollingerBands(DF_Data, LENGHT, STD):
    df = pd.DataFrame()
    df[['lower', 'middle', 'upper', 'bandwidth', 'percentcolumns']] = ta.bbands(DF_Data['Close'], length=LENGHT, std=STD)
    B1_IND = round(df['upper'].iloc[-1], 4)
    BM_IND = round(df['middle'].iloc[-1], 4)
    B2_IND = round(df['lower'].iloc[-1], 4)
    #time_1MIN = ret_time(DF_Data)
    save_indicator(locals().items())
    return B1_IND, BM_IND, B2_IND

def Supertrend(DF_Data, LENGHT, MULT):
    df = pd.DataFrame()
    df[['supertrend', 'supertrend_direc', 'supertrend_down', 'supertrend_up']] = ta.supertrend(pd.to_numeric(DF_Data['High']), pd.to_numeric(DF_Data['Low']), pd.to_numeric(DF_Data['Close']), length=LENGHT, multiplier=MULT)
    SUPERTRENDUP_IND = round(df['supertrend_up'].iloc[-1], 4)
    SUPERTRENDDOWN_IND = round(df['supertrend_down'].iloc[-1], 4)
    SUPERTREND_IND = round(df['supertrend'].iloc[-1], 4)
    #time_1MIN = ret_time(DF_Data)
    save_indicator(locals().items())
    return SUPERTREND_IND, SUPERTRENDDOWN_IND, SUPERTRENDUP_IND

def Momentum(DF_Data, LENGHT):
    MOMENTUM_IND = round(ta.mom(DF_Data['Close'], timeperiod=LENGHT).iloc[-1], 4)
    #time_1MIN = ret_time(DF_Data)    
    save_indicator(locals().items())
    return MOMENTUM_IND
    
def Ema(DF_Data, LENGHT):
    EMA_IND = round(ta.ema(DF_Data['Close'], length=LENGHT).iloc[-1], 4)
    #time_1MIN = ret_time(DF_Data)
    save_indicator(locals().items())
    return EMA_IND

def Sma(DF_Data, LENGHT):
    SMA_IND = round(ta.sma(DF_Data['Close'],length=LENGHT).iloc[-1], 4)
    #time_1MIN = ret_time(DF_Data)
    save_indicator(locals().items())    
    return SMA_IND

def Stochastic(DF_Data, LENGHT, K, D):
    STOCHK_1M_DATA = pd.DataFrame()
    STOCHK_1M_DATA[['k', 'd']] = ta.stoch(DF_Data['High'], DF_Data['Low'], DF_Data['Close'], LENGHT, K, D)
    STOCHK_IND = round(STOCHK_1M_DATA['k'].iloc[-1], 4)
    STOCHD_IND = round(STOCHK_1M_DATA['d'].iloc[-1], 4)
    #time_1MIN = ret_time(DF_Data)
    save_indicator(locals().items())
    return STOCHK_IND, STOCHD_IND
    
def Rsi(DF_Data, LENGHT):
    RSI_IND = round(ta.rsi(DF_Data['Close'], LENGHT).iloc[-1], 4)
    #time_1MIN = ret_time(DF_Data)
    save_indicator(locals().items())
    return RSI_IND

def Wma(DF_Data, LENGHT):
    WMA_IND = round(ta.wma(DF_Data['Close'], LENGHT).iloc[-1], 4)
    #time_1MIN = ret_time(DF_Data)
    save_indicator(locals().items())
    return WMA_IND
    
def Hma(DF_Data, LENGHT):
    HMA_IND = round(ta.hma(DF_Data['Close'], LENGHT).iloc[-1], 4)
    #time_1MIN = ret_time(DF_Data)
    save_indicator(locals().items())
    return HMA_IND
    
def Heikinashi(DF_Data):
    HEIKINASHI_1M_DATA = pd.DataFrame()
    HEIKINASHI_1M_DATA[['ha_open', 'ha_high', 'ha_low', 'ha_close']] = ta.ha(DF_Data['Open'], DF_Data['High'], DF_Data['Low'], DF_Data['Close'])
    HEIKINASHI_OPEN_IND = round(HEIKINASHI_1M_DATA['ha_open'], 4)
    HEIKINASHI_HIGH_IND = round(HEIKINASHI_1M_DATA['ha_high'], 4)
    HEIKINASHI_LOW_IND = round(HEIKINASHI_1M_DATA['ha_low'], 4)
    HEIKINASHI_CLOSE_IND = round(HEIKINASHI_1M_DATA['ha_close'], 4)
    #time_1MIN = ret_time(DF_Data)
    save_indicator(locals().items())
    return HEIKINASHI_OPEN_IND, HEIKINASHI_HIGH_IND, HEIKINASHI_LOW_IND, HEIKINASHI_CLOSE_IND

def Macd(DF_Data, FAST, SLOW, SIGNAL):
    MACD_IND, MACDHIST_IND, MACDSIG_IND = round(ta.macd(DF_Data['Close'],FAST, SLOW, SIGNAL).iloc[-1], 4)
    #time_1MIN = ret_time(DF_Data)
    save_indicator(locals().items())
    return MACD_IND, MACDHIST_IND, MACDSIG_IND
    
def Cci(DF_Data, LENGHT):
    CCI_IND = round(DF_Data.ta.cci(length=LENGHT).iloc[-1], 4)
    #time_1MIN = ret_time(DF_Data)
    save_indicator(locals().items())
    return CCI_IND

def Sl(PAIR, CLOSE_1MIN):
    bought_at, timeHold, coins_bought = load_json(PAIR)
    SL = float(bought_at) - ((float(bought_at) * float(STOP_LOSS)) / 100)
    return (float(CLOSE_1MIN) < float(SL) and float(SL) != 0)
    
def Tp(PAIR, CLOSE_1MIN):
    try:
        global TAKE_PROFIT
        sellSignalTP = False
        bought_at, timeHold, coins_bought = load_json(PAIR)
        TP = float(bought_at) + ((float(bought_at) * float(TAKE_PROFIT)) / 100)
        sellSignalTP = (float(CLOSE_1MIN) > float(TP) and float(TP) != 0.0)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print('Tp Error on line ' + str(exc_tb.tb_lineno))
        pass
    return sellSignalTP
    
def Bought_at(PAIR):
    bought_at, timeHold, coins_bought = load_json(PAIR)
    return bought_at