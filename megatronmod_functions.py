# Megatronmod Strategy - All in One
# Created by: Horacio Oscar Fanelli - Pantersxx3 and NokerPlay
# This mod can be used only with:
# https://github.com/pantersxx3/Binance-Bot
#
# No future support offered, use this script at own risk - test before using real funds
# If you lose money using this MOD (and you will at some point) you've only got yourself to blame!

#Crossover, Crossunder, Cross, Ichimoku, Bollinger Bands, Supertrend, Momentum, Hikinashi
#Macd, Cci, SL, TP, Bought_at, Zigzag, Ema, Sma, Stochastic, Rsi, Wma, Hma

from tradingview_ta import TA_Handler, Interval, Exchange
from binance.client import Client, BinanceAPIException
from helpers.parameters import parse_args, load_config

from datetime import date, datetime, timedelta
from collections import defaultdict
import pandas_ta as ta #pta
import pandas as pd
from ta.trend import SMAIndicator, EMAIndicator, CCIIndicator, MACD, ADXIndicator
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands, AverageTrueRange
from ta.volume import OnBalanceVolumeIndicator, VolumeWeightedAveragePrice
import threading
import os
import sys
import glob
import math
import time
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
global access_key, secret_key, client, txcolors, bought, timeHold, ACTUAL_POSITION, args, TEST_MODE, BACKTESTING_MODE
global USE_TESNET_IN_ONLINEMODE, USE_SIGNALLING_MODULES, LANGUAGE, MAX_HOLDING_TIME, BOT_STATS


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
BOT_STATS = parsed_config['script_options']['BOT_STATS']
#BACKTESTING_MODE_TIME_START = parsed_config['script_options']['BACKTESTING_MODE_TIME_START']
PAIR_WITH = parsed_config['trading_options']['PAIR_WITH']
SELL_ON_SIGNAL_ONLY = parsed_config['trading_options']['SELL_ON_SIGNAL_ONLY']
MODE = parsed_config['script_options']['MODE']
LOG_FILE = parsed_config['script_options'].get('LOG_FILE')
COINS_BOUGHT = parsed_config['script_options'].get('COINS_BOUGHT')
STOP_LOSS = parsed_config['trading_options']['STOP_LOSS']
TAKE_PROFIT = parsed_config['trading_options']['TAKE_PROFIT']
TRADES_GRAPH = parsed_config['script_options'].get('TRADES_GRAPH')
TRADES_INDICATORS = parsed_config['script_options'].get('TRADES_INDICATORS')
TRADE_SLOTS = parsed_config['trading_options']['TRADE_SLOTS']
#BACKTESTING_MODE = parsed_config['script_options']['BACKTESTING_MODE']
BACKTESTING_MODE_TIME_START = parsed_config['script_options']['BACKTESTING_MODE_TIME_START']
MAX_HOLDING_TIME = parsed_config['trading_options']['MAX_HOLDING_TIME']
MICROSECONDS = 2
      
#ACTUAL_POSITION = 0
SIGNAL_NAME = 'MEGATRONMOD'
#CREATE_BUY_SELL_FILES = True
#DEBUG = True
EXCHANGE = 'BINANCE'
SCREENER = 'CRYPTO'

#JSON_FILE_BOUGHT = SIGNAL_NAME + '.json'
        
def write_log(logline, LOGFILE = LOG_FILE, show = True, time = False):
    try:
        from Boot import set_correct_mode
        TEST_MODE, BACKTESTING_MODE, USE_TESNET_IN_ONLINEMODE, USE_SIGNALLING_MODULES = set_correct_mode(LANGUAGE, MODE, True)
        # if TEST_MODE:
            # file_prefix = 'test_'
        # else:
            # file_prefix = 'live_'  
        with open(LOGFILE,'a') as f:
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
        exc_type, exc_obj, exc_tb = sys.exc_info()
        write_log('Error on line ' + str(exc_tb.tb_lineno), SIGNAL_NAME + '.log', True, False)
        pass
    return pos1

def get_analysis(d, tf, p, position1=0, num_records=1000, history_data=None):
    try:
        global BACKTESTING_MODE, BACKTESTING_MODE_TIME_START
        from Boot import set_correct_mode
        TEST_MODE, BACKTESTING_MODE, USE_TESNET_IN_ONLINEMODE, USE_SIGNALLING_MODULES = set_correct_mode(LANGUAGE, MODE, True)
        c = pd.DataFrame([])
        e = 0
        if history_data == None:
            history_data = p + '.csv'
            
        if BACKTESTING_MODE:
            if position1 > 0:
                if d.empty:
                    d = pd.read_csv(history_data)
                    d.columns = ['time', 'Open', 'High', 'Low', 'Close', 'Volume']
                    d['Close'] = d['Close'].astype(float)
                else:
                    d['Close'] = d['Close'].astype(float)
                #c = d.query('time < @position1').tail(num_records)
                idx = d["time"].searchsorted(position1)
                c = d.iloc[max(0, idx - num_records):idx]
                inttime = int(position1)/1000            
                position2 = c['time'].iloc[0]
                #print(f'{txcolors.SELL_PROFIT}{SIGNAL_NAME}: {txcolors.DEFAULT}{BACKTESTING_MODE_TIME_START} - Posicion actual {datetime.fromtimestamp(inttime).strftime("%d/%m/%y %H:%M:%S")} - {position2} - {position1}...{txcolors.DEFAULT}')
                d = pd.DataFrame([])
        else:            
            client = Client(access_key, secret_key)
            if "m" in tf: 
                back = 'min ago UTC'
            elif "h" in tf:
                back = 'hour ago UTC'
            elif "d" in tf:
                back = 'day ago UTC'
            elif "w" in tf:
                back = 'week ago UTC'
            elif "M" in tf:
                back = 'month ago UTC'				

            klines = client.get_historical_klines(symbol=p, interval=tf, start_str=str(num_records) + back, limit=num_records)
            c = pd.DataFrame(klines)
            c.columns = ['time', 'Open', 'High', 'Low', 'Close', 'Volume', 'CloseTime', 'QuoteAssetVolume', 'Trades', 'TakerBuyBase', 'TakerBuyQuote', 'Ignore']
            c = c.drop(c.columns[[6, 7, 8, 9, 10, 11]], axis=1)
            c['time'] = pd.to_datetime(c['time'], unit='ms')
            c['Close'] = c['Close'].astype(float)
            #print(c)
    except Exception as e:
        write_log(f'{txcolors.DEFAULT}{SIGNAL_NAME}: {txcolors.SELL_LOSS} - Exception: get_analysis(): {e}{txcolors.DEFAULT}', SIGNAL_NAME + '.log', True, False)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        write_log('Error on line ' + str(exc_tb.tb_lineno), SIGNAL_NAME + '.log', True, True) 
    return c

   
def Cross_Emas(df1, namestr1, df2, namestr2):
    try:
        data = pd.DataFrame(index=df1.index)
        data[namestr1] = df1
        data[namestr2] = df2
        
        data['Diff'] = data[namestr1] - data[namestr2]
        data['Signal'] = 0

        # Usamos .loc o sumamos las condiciones para no sobrescribir
        # Golden Cross (1): EMA rápida cruza por encima de la lenta
        data.loc[(data['Diff'] > 0) & (data['Diff'].shift(1) <= 0), 'Signal'] = 1
        
        # Death Cross (-1): EMA rápida cruza por debajo de la lenta
        data.loc[(data['Diff'] < 0) & (data['Diff'].shift(1) >= 0), 'Signal'] = -1

        # Obtener el último estado (el momento actual)
        current_signal = data['Signal'].iloc[-1]
        
        # if current_signal == 1:
            # print(f"¡Cruce al ALZA detectado! {namestr1} subió por encima de {namestr2}")
        # elif current_signal == -1:
            # print(f"¡Cruce a la BAJA detectado! {namestr1} cayó por debajo de {namestr2}")
            
        return current_signal

    except Exception as e:
        write_log(f'{txcolors.DEFAULT}{SIGNAL_NAME}: {txcolors.SELL_LOSS} - Exception: Cross_Emas(): {e}{txcolors.DEFAULT}', SIGNAL_NAME + '.log', True, False)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        write_log('Error on line ' + str(exc_tb.tb_lineno), SIGNAL_NAME + '.log', True, True)     
    
def isNone(var):
    if var == None:
        r = 0
    else:
        r = var
    return r

def read_volume_value(coin, type):
    try:
        if TEST_MODE:
            file_prefix = 'test_'
        else:
            file_prefix = 'live_' 
            
        if os.path.exists(file_prefix + 'trades.csv'):
            column_names = ["Datetime", "OrderID", "Type", "Coin", "Volume", "Buy Price", "Amount of Buy USDT", "Sell Price", "Amount of Sell USDT", "Sell Reason", "Profit $ USDT", "Commission"]
            df = pd.read_csv(file_prefix + 'trades.csv', delimiter=',', names=column_names)
            #Datetime, OrderID, Type, Coin, Volume, Buy Price, Amount of Buy USDT, Sell Price, Amount of Sell USDT, Sell Reason, Profit $ USDT
            filtered = df[(df["Type"] == " " + type) & (df["Coin"] == " " + coin.replace(PAIR_WITH, ""))]
            if len(filtered) > 1:
                return round(float(filtered["Volume"].iloc[-1]),8)
            elif len(filtered) == 1:
                return round(float(filtered["Volume"].iloc[0]), 8)
            else:
                return 0.0
        else:
            return 0.0            
    except Exception as e:
        write_log(f'{txcolors.DEFAULT}{SIGNAL_NAME}: {txcolors.SELL_LOSS} - Exception: read_comission_value(): {e}{txcolors.DEFAULT}', SIGNAL_NAME + '.log', True, False)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        write_log('Error on line ' + str(exc_tb.tb_lineno), SIGNAL_NAME + '.log', True, False)
        
def read_commission_value(coin, type):
    try:
        if TEST_MODE:
            file_prefix = 'test_'
        else:
            file_prefix = 'live_'
            
        if os.path.exists(file_prefix + 'trades.csv'):
            column_names = ["Datetime", "OrderID", "Type", "Coin", "Volume", "Buy Price", "Amount of Buy USDT", "Sell Price", "Amount of Sell USDT", "Sell Reason", "Profit $ USDT", "Commission"]
            df = pd.read_csv(file_prefix + 'trades.csv', names=column_names)
            #Datetime, OrderID, Type, Coin, Volume, Buy Price, Amount of Buy USDT, Sell Price, Amount of Sell USDT, Sell Reason, Profit $ USDT
            filtered = df[(df["Type"] == " " + type) & (df["Coin"] == " " + coin.replace(PAIR_WITH, ""))]
            if len(filtered) > 1:
                return round(float(filtered["Commission"].iloc[-1]), 8)
            elif len(filtered) == 1:
                return round(float(filtered["Commission"].iloc[0]), 8)
            else:
                return 0.0
        else:
            return 0.0
    except Exception as e:
        write_log(f'{txcolors.DEFAULT}{SIGNAL_NAME}: {txcolors.SELL_LOSS} - Exception: read_commission_value(): {e}{txcolors.DEFAULT}', SIGNAL_NAME + '.log', True, False)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        write_log('Error on line ' + str(exc_tb.tb_lineno), SIGNAL_NAME + '.log', True, False)
        
def read_sell_value(coin):
    try:
        if TEST_MODE:
            file_prefix = 'test_'
        else:
            file_prefix = 'live_'
            
        if os.path.exists(file_prefix + 'trades.csv'):
            column_names = ["Datetime", "OrderID", "Type", "Coin", "Volume", "Buy Price", "Amount of Buy USDT", "Sell Price", "Amount of Sell USDT", "Sell Reason", "Profit $ USDT", "Commission"]
            df = pd.read_csv(file_prefix + 'trades.csv', names=column_names)
            #Datetime, OrderID, Type, Coin, Volume, Buy Price, Amount of Buy USDT, Sell Price, Amount of Sell USDT, Sell Reason, Profit $ USDT
            filtered = df[(df["Type"] ==' Sell') & (df["Coin"] == " " + coin.replace(PAIR_WITH, ""))]
            if len(filtered) > 1:
                return round(float(filtered["Sell Price"].iloc[-1]), 8)
            elif len(filtered) == 1:
                return round(float(filtered["Sell Price"].iloc[0]), 8)
            else:
                return 0.0
        else:
            return 0.0
    except Exception as e:
        write_log(f'{txcolors.DEFAULT}{SIGNAL_NAME}: {txcolors.SELL_LOSS} - Exception: read_sell_value(): {e}{txcolors.DEFAULT}', SIGNAL_NAME + '.log', True, False)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        write_log('Error on line ' + str(exc_tb.tb_lineno), SIGNAL_NAME + '.log', True, False)

def load_json_boot_stats(p, main_path):
    try:
        from Boot import set_correct_mode
        TEST_MODE, BACKTESTING_MODE, USE_TESNET_IN_ONLINEMODE, USE_SIGNALLING_MODULES = set_correct_mode(LANGUAGE, MODE, True)
        boot_stats = {}
        if TEST_MODE:
            file_prefix = 'test_'
        else:
            file_prefix = 'live_'
        boot_stats_file_path = main_path + file_prefix + BOT_STATS
        if os.path.exists(boot_stats_file_path) and os.path.getsize(boot_stats_file_path) > 2:
            with open(boot_stats_file_path,'r') as f:
                boot_stats = json.load(f)
            # for analysis1MIN in bought_analysis1MIN.keys():
                # value3 = value3 + 1                
            # if p in bought_analysis1MIN:
                # value1 = round(float(bought_analysis1MIN[p]['bought_at']),8)
                # value2 = round(float(bought_analysis1MIN[p]['time']),8)
                # bought_analysis1MIN = {}
    except Exception as e:
        write_log(f'{txcolors.DEFAULT}{SIGNAL_NAME}: {txcolors.SELL_LOSS} - Exception: load_json_bought(): {e}{txcolors.DEFAULT}', SIGNAL_NAME + '.log', True, False)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        write_log('Error on line ' + str(exc_tb.tb_lineno), SIGNAL_NAME + '.log', True, False)
    return boot_stats[p]
    
def load_json_bought(p, main_path):
    try:
        from Boot import set_correct_mode
        TEST_MODE, BACKTESTING_MODE, USE_TESNET_IN_ONLINEMODE, USE_SIGNALLING_MODULES = set_correct_mode(LANGUAGE, MODE, True)
        bought_analysis1MIN = {}
        value1 = 0
        value2 = 0
        value3 = 0
        if TEST_MODE:
            file_prefix = 'test_'
        else:
            file_prefix = 'live_'
        coins_bought_file_path = main_path + file_prefix + COINS_BOUGHT
        if os.path.exists(coins_bought_file_path) and os.path.getsize(coins_bought_file_path) > 2:
            with open(coins_bought_file_path,'r') as f:
                bought_analysis1MIN = json.load(f)
            for analysis1MIN in bought_analysis1MIN.keys():
                value3 = value3 + 1                
            if p in bought_analysis1MIN:
                value1 = round(float(bought_analysis1MIN[p]['bought_at']),8)
                value2 = round(float(bought_analysis1MIN[p]['time']),8)
                bought_analysis1MIN = {}
    except Exception as e:
        write_log(f'{txcolors.DEFAULT}{SIGNAL_NAME}: {txcolors.SELL_LOSS} - Exception: load_json_bought(): {e}{txcolors.DEFAULT}', SIGNAL_NAME + '.log', True, False)
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
                        str1 = str1 + str(round(float(value),8)) + ','
                    else:
                        str1 = str1 + str(value) + ','
            else:
                if with_value:
                    if not value == {}:
                        if isfloat(value):    
                            str1 = str1 + str(key) + ':' + str(round(float(value),8)) + ','
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
        list_indicators = []
        list_indicators = ["Bollinger_Bands", "Cci", "Cross", "Crossover", "Crossunder", "Ema", "Heikinashi", "Hma", "Ichimoku", "Macd", "Momentum", "Rsi", "Sl", "Sma", "Stochastic", "Supertrend", "Tp", "Wma", "Zigzag"]
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
    
# def save_indicator(items):
    # try:

        # if TEST_MODE:
                # file_prefix = 'test_'
        # else:
            # file_prefix = 'live_'                
         
        # data_indicator = pd.DataFrame([]) 
        # csv_indicators = file_prefix + TRADES_INDICATORS
        
        # for name, myvalue in list(items):
            # if name.endswith('_IND'): # or name == 'time_1MIN':
                # myvalue = str(myvalue).strip()
                # data_indicators = pd.DataFrame([])
                # data_indicators[name] = [myvalue] 
                   
                # if not data_indicators.empty:
                    # data_indicators.to_csv(csv_indicators.replace('.csv', '') + "_" + name + '.csv', mode='a', index=False, header=False)

    # except Exception as e:
        # write_log(f'{txcolors.DEFAULT}{SIGNAL_NAME}: {txcolors.Red}Exception: #save_indicator(): {e}', SIGNAL_NAME + '.log', True, False)
        # exc_type, exc_obj, exc_tb = sys.exc_info()
        # write_log('Error on line ' + str(exc_tb.tb_lineno), SIGNAL_NAME + '.log', True, False)
        # pass

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
        # write_log(f'{txcolors.DEFAULT}{SIGNAL_NAME}: {txcolors.Red}Exception: #save_indicator(): {e}', SIGNAL_NAME + '.log', True, False)
        # exc_type, exc_obj, exc_tb = sys.exc_info()
        # write_log('Error on line ' + str(exc_tb.tb_lineno), SIGNAL_NAME + '.log', True, False)
        # pass
        
def Ichimoku(DF_Data, TENKA, KIJUN, SENKU):
    df = pd.DataFrame(DF_Data)
    df[['spanA', 'spanB', 'tenkan_sen', 'kijun_sen', 'chikou_span']] = ta.ichimoku(DF_Data['High'], DF_Data['Low'], DF_Data['Close'], TENKA, KIJUN, SENKU)
    spanA = round(df['spanA'], 8)
    spanB = round(df['spanB'], 8)
    tenkan_sen_IND = round(df['tenkan_sen'], 8)
    kijun_sen_IND = round(df['kijun_sen'], 8)
    chikou_span_IND = round(df['chikou_span'], 8)
    #time_1MIN = ret_time(DF_Data)
    #save_indicator(locals().items())
    return spanA_IND, spanB_IND, tenkan_sen_IND, kijun_sen_IND, chikou_span_IND

def Heikinashi(DF_Data):
    HEIKINASHI_1M_DATA = pd.DataFrame()
    HEIKINASHI_1M_DATA[['ha_open', 'ha_high', 'ha_low', 'ha_Close']] = ta.ha(DF_Data['Open'], DF_Data['High'], DF_Data['Low'], DF_Data['Close'])
    HEIKINASHI_OPEN_IND = round(HEIKINASHI_1M_DATA['ha_open'], 8)
    HEIKINASHI_HIGH_IND = round(HEIKINASHI_1M_DATA['ha_high'], 8)
    HEIKINASHI_LOW_IND = round(HEIKINASHI_1M_DATA['ha_low'], 8)
    HEIKINASHI_CLOSE_IND = round(HEIKINASHI_1M_DATA['ha_Close'], 8)
    #time_1MIN = ret_time(DF_Data)
    #save_indicator(locals().items())
    return HEIKINASHI_OPEN_IND, HEIKINASHI_HIGH_IND, HEIKINASHI_LOW_IND, HEIKINASHI_CLOSE_IND
    
def Bollinger_Bands(DF_Data, LENGHT, STD):
    df = pd.DataFrame()
    df[['lower', 'middle', 'upper', 'bandwidth', 'percentcolumns']] = ta.bbands(DF_Data['Close'], length=LENGHT, std=STD)
    B1_IND = round(df['upper'].iloc[-1], 8)
    BM_IND = round(df['middle'].iloc[-1], 8)
    B2_IND = round(df['lower'].iloc[-1], 8)
    #time_1MIN = ret_time(DF_Data)
    #save_indicator(locals().items())
    return B1_IND, BM_IND, B2_IND

def Supertrend(DF_Data, LENGHT, MULT):
    df = pd.DataFrame()
    df[['supertrend', 'supertrend_direc', 'supertrend_down', 'supertrend_up']] = ta.supertrend(pd.to_numeric(DF_Data['High']), pd.to_numeric(DF_Data['Low']), pd.to_numeric(DF_Data['Close']), length=LENGHT, multiplier=MULT)
    SUPERTRENDUP_IND = round(df['supertrend_up'].iloc[-1], 8)
    SUPERTRENDDOWN_IND = round(df['supertrend_down'].iloc[-1], 8)
    SUPERTREND_IND = round(df['supertrend'].iloc[-1], 8)
    #time_1MIN = ret_time(DF_Data)
    #save_indicator(locals().items())
    return SUPERTREND_IND, SUPERTRENDDOWN_IND, SUPERTRENDUP_IND

def Momentum(DF_Data, LENGHT):
    MOMENTUM_IND = round(ta.mom(DF_Data['Close'], timeperiod=LENGHT).iloc[-1], 8)
    #time_1MIN = ret_time(DF_Data)    
    #save_indicator(locals().items())
    return MOMENTUM_IND
    
def Ema(DF_Data, LENGHT):
    EMA_IND = round(ta.ema(DF_Data['Close'], length=LENGHT).iloc[-1], 8)
    #time_1MIN = ret_time(DF_Data)
    #save_indicator(locals().items())
    return EMA_IND

def Ema_df(DF_Data, LENGHT):
    EMA_IND = ta.ema(DF_Data['Close'], length=LENGHT)
    return EMA_IND
    
def Sma(DF_Data, LENGHT):
    SMA_IND = round(ta.sma(DF_Data['Close'],length=LENGHT).iloc[-1], 8)
    #time_1MIN = ret_time(DF_Data)
    #save_indicator(locals().items())    
    return SMA_IND
    
def Sma_df(DF_Data, LENGHT):
    SMA_IND = ta.sma(DF_Data['Close'],length=LENGHT)   
    return SMA_IND

def Stochastic(DF_Data, LENGHT, K, D):
    STOCHK_DATA = pd.DataFrame()
    STOCHK_DATA[['k', 'd']] = ta.stoch(DF_Data['High'], DF_Data['Low'], DF_Data['Close'], LENGHT, K, D)
    STOCHK_IND = round(STOCHK_DATA['k'].iloc[-1], 8)
    STOCHD_IND = round(STOCHK_DATA['d'].iloc[-1], 8)
    #time_1MIN = ret_time(DF_Data)
    #save_indicator(locals().items())
    return STOCHK_IND, STOCHD_IND
    
def Stochastic_df(DF_Data, LENGHT, K, D):
    STOCHK_DATA = pd.DataFrame()
    STOCHK_DATA[['k', 'd']] = ta.stoch(DF_Data['High'], DF_Data['Low'], DF_Data['Close'], LENGHT, K, D)
    STOCHK_IND = STOCHK_DATA['k']
    STOCHD_IND = STOCHK_DATA['d']
    #time_1MIN = ret_time(DF_Data)
    #save_indicator(locals().items())
    return STOCHK_IND, STOCHD_IND
    
def Rsi(DF_Data, LENGHT):
    RSI_IND = round(ta.rsi(DF_Data['Close'], LENGHT).iloc[-1], 8)
    #time_1MIN = ret_time(DF_Data)
    #save_indicator(locals().items())
    return RSI_IND

def Rsi_df(DF_Data, LENGHT):
    RSI_IND = ta.rsi(DF_Data['Close'], LENGHT)
    #time_1MIN = ret_time(DF_Data)
    #save_indicator(locals().items())
    return RSI_IND

def Wma(DF_Data, LENGHT):
    WMA_IND = round(ta.wma(DF_Data['Close'], LENGHT).iloc[-1], 8)
    #time_1MIN = ret_time(DF_Data)
    #save_indicator(locals().items())
    return WMA_IND
    
def Hma(DF_Data, LENGHT):
    HMA_IND = round(ta.hma(DF_Data['Close'], LENGHT).iloc[-1], 8)
    #time_1MIN = ret_time(DF_Data)
    #save_indicator(locals().items())
    return HMA_IND
    
def Macd(DF_Data, FAST, SLOW, SIGNAL):
    MACD_IND, MACDHIST_IND, MACDSIG_IND = round(ta.macd(DF_Data['Close'],FAST, SLOW, SIGNAL).iloc[-1], 8)
    #time_1MIN = ret_time(DF_Data)
    #save_indicator(locals().items())
    return MACD_IND, MACDHIST_IND, MACDSIG_IND

def Macd_df(DF_Data, FAST, SLOW, SIGNAL):
    macd_df = ta.macd(DF_Data['Close'],FAST, SLOW, SIGNAL)
    MACD_IND = macd_df[f"MACD_{FAST}_{SLOW}_{SIGNAL}"]
    MACDHIST_IND = macd_df[f"MACDh_{FAST}_{SLOW}_{SIGNAL}"]
    MACDSIG_IND = macd_df[f"MACDs_{FAST}_{SLOW}_{SIGNAL}"]
    return MACD_IND, MACDHIST_IND, MACDSIG_IND

def Macd_Ind(DF_Data, FAST, SLOW, SIGNAL):
    MACD_IND, MACDHIST_IND, MACDSIG_IND = round(ta.macd(DF_Data['Close'],FAST, SLOW, SIGNAL).iloc[-1], 8)
    #time_1MIN = ret_time(DF_Data)
    #save_indicator(locals().items())
    return MACD_IND

def Macd_Hist(DF_Data, FAST, SLOW, SIGNAL):
    MACD_IND, MACDHIST_IND, MACDSIG_IND = round(ta.macd(DF_Data['Close'],FAST, SLOW, SIGNAL).iloc[-1], 8)
    #time_1MIN = ret_time(DF_Data)
    #save_indicator(locals().items())
    return MACDHIST_IND

def Macd_Sig(DF_Data, FAST, SLOW, SIGNAL):
    MACD_IND, MACDHIST_IND, MACDSIG_IND = round(ta.macd(DF_Data['Close'],FAST, SLOW, SIGNAL).iloc[-1], 8)
    #time_1MIN = ret_time(DF_Data)
    #save_indicator(locals().items())
    return MACDSIG_IND

def Macd_Hist_df(DF_Data, FAST, SLOW, SIGNAL):
    macd_df = ta.macd(DF_Data['Close'],FAST, SLOW, SIGNAL)
    MACDHIST_IND = macd_df[f"MACDh_{FAST}_{SLOW}_{SIGNAL}"]
    #time_1MIN = ret_time(DF_Data)
    #save_indicator(locals().items())
    return MACDHIST_IND
    
def Macd_Sig_df(DF_Data, FAST, SLOW, SIGNAL):
    macd_df = ta.macd(DF_Data['Close'],FAST, SLOW, SIGNAL)
    # MACD_IND = macd_df[f"MACD_{FAST}_{SLOW}_{SIGNAL}"]
    # MACDHIST_IND = macd_df[f"MACDh_{FAST}_{SLOW}_{SIGNAL}"]
    MACDSIG_IND = macd_df[f"MACDs_{FAST}_{SLOW}_{SIGNAL}"]
    return MACDSIG_IND

def Macd_Ind_df(DF_Data, FAST, SLOW, SIGNAL):
    macd_df = ta.macd(DF_Data['Close'],FAST, SLOW, SIGNAL)
    MACD_IND = macd_df[f"MACD_{FAST}_{SLOW}_{SIGNAL}"]
        # MACDHIST_IND = macd_df[f"MACDh_{FAST}_{SLOW}_{SIGNAL}"]
        # MACDSIG_IND = macd_df[f"MACDs_{FAST}_{SLOW}_{SIGNAL}"]
    return MACD_IND
    
def Cci(DF_Data, LENGHT):
    CCI_IND = round(DF_Data.ta.cci(length=LENGHT).iloc[-1], 8)
    #time_1MIN = ret_time(DF_Data)
    #save_indicator(locals().items())
    return CCI_IND

def Sl(PAIR, CLOSE, STOPLOSS, main_path):
    try:
        r = False
        bought_at = Bought_at(PAIR, main_path) #, timeHold, coins_bought = load_json_bought(PAIR)
        SL = float(bought_at) - ((float(bought_at) * float(STOPLOSS)) / 100)
        r = float(CLOSE) < float(SL) and float(SL) != 0.0
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print('Sl Error on line ' + str(exc_tb.tb_lineno))
        pass    
    return r
    
def Tp(PAIR, CLOSE, TAKEPROFIT, main_path):
    try:
        sellSignalTP = False
        bought_at = Bought_at(PAIR, main_path) #, timeHold, coins_bought = load_json_bought(PAIR)
        TP = float(bought_at) + ((float(bought_at) * float(TAKEPROFIT)) / 100)
        sellSignalTP = (float(CLOSE) > float(TP) and float(TP) != 0.0)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print('Tp Error on line ' + str(exc_tb.tb_lineno))
        pass
    return sellSignalTP
    
def Bought_at(PAIR, main_path):
    bought_at, timeHold, coins_bought = load_json_bought(PAIR, main_path)
    return bought_at

def Bought_timeHold(PAIR, main_path):
    bought_at, timeHold, coins_bought = load_json_bought(PAIR, main_path)
    return timeHold
    
def TimeHold(pair, current_timestamp, main_path):
    current_timestamp_seconds = current_timestamp/1000
    TimeHold_seconds = Bought_timeHold(pair, main_path)/1000
    TimeHold_sec = current_timestamp_seconds - TimeHold_seconds
    TimeHold_min = TimeHold_sec / 60
    return TimeHold_min

def Zigzag(DF_data, length=10, deviation=5.0):
    """
    Calcula pivotes ZigZag en un DataFrame de precios.
    
    Parameters:
    DF_data (pd.DataFrame): DataFrame con columnas 'High', 'Low', 'Close'
    length (int): Profundidad para buscar pivotes (default: 10)
    deviation (float): Desviación porcentual mínima (default: 5.0%)
    
    Returns:
    pd.DataFrame: DataFrame original con columnas adicionales:
        - 'ZigZag_Value': Valor del pivote ZigZag (float)
        - 'ZigZag_Type': 'High' o 'Low' según el tipo de pivote (string)
        - 'ZigZag_Signal': True donde hay pivote (bool)
    """
    
    # Verificar columnas necesarias
    required_cols = ['High', 'Low', 'Close']
    for col in required_cols:
        if col not in DF_data.columns:
            raise ValueError(f"El DataFrame debe contener la columna '{col}'")
    
    # Crear copia para no modificar el original
    df = DF_data.copy()
    
    # Inicializar columnas con tipos correctos
    df['ZigZag_Value'] = np.nan  # float
    df['ZigZag_Type'] = None     # object/string
    df['ZigZag_Signal'] = False  # bool
    
    # Asegurar que las columnas de precios sean float
    for col in ['High', 'Low', 'Close']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Variables para tracking
    last_pivot_value = np.nan
    last_pivot_index = -1
    last_pivot_type = None
    
    for i in range(length, len(df)):
        current_high = float(df['High'].iloc[i])
        current_low = float(df['Low'].iloc[i])
        
        # Buscar máximo y mínimo en la ventana
        high_window = df['High'].iloc[i-length:i].astype(float)
        low_window = df['Low'].iloc[i-length:i].astype(float)
        
        is_potential_high = current_high == high_window.max()
        is_potential_low = current_low == low_window.min()
        
        # Aplicar desviación porcentual
        deviation_factor = deviation / 100.0
        
        # Verificar si last_pivot_value es numérico
        last_pivot_numeric = not pd.isna(last_pivot_value) and isinstance(last_pivot_value, (int, float, np.number))
        
        if is_potential_high and last_pivot_numeric:
            required_move = float(last_pivot_value) * deviation_factor
            if current_high >= float(last_pivot_value) + required_move:
                df.loc[df.index[i], 'ZigZag_Value'] = float(current_high)
                df.loc[df.index[i], 'ZigZag_Type'] = 'High'
                df.loc[df.index[i], 'ZigZag_Signal'] = True
                last_pivot_value = float(current_high)
                last_pivot_index = i
                last_pivot_type = 'High'
        
        elif is_potential_low and last_pivot_numeric:
            required_move = float(last_pivot_value) * deviation_factor
            if current_low <= float(last_pivot_value) - required_move:
                df.loc[df.index[i], 'ZigZag_Value'] = float(current_low)
                df.loc[df.index[i], 'ZigZag_Type'] = 'Low'
                df.loc[df.index[i], 'ZigZag_Signal'] = True
                last_pivot_value = float(current_low)
                last_pivot_index = i
                last_pivot_type = 'Low'
        
        # Primer pivote (sin referencia previa)
        elif pd.isna(last_pivot_value):
            if is_potential_high:
                df.loc[df.index[i], 'ZigZag_Value'] = float(current_high)
                df.loc[df.index[i], 'ZigZag_Type'] = 'High'
                df.loc[df.index[i], 'ZigZag_Signal'] = True
                last_pivot_value = float(current_high)
                last_pivot_index = i
                last_pivot_type = 'High'
            elif is_potential_low:
                df.loc[df.index[i], 'ZigZag_Value'] = float(current_low)
                df.loc[df.index[i], 'ZigZag_Type'] = 'Low'
                df.loc[df.index[i], 'ZigZag_Signal'] = True
                last_pivot_value = float(current_low)
                last_pivot_index = i
                last_pivot_type = 'Low'
    
    return df

def Zigzag_safe(DF_data, length=10, deviation=5.0):

    df = DF_data.copy()
    
    # Convertir columnas a float
    for col in ['High', 'Low', 'Close']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    df = df.assign(
        ZigZag_Value=np.nan,
        ZigZag_Type=pd.Series(dtype='object'),
        ZigZag_Signal=False
    )
    
    last_pivot = np.nan
    last_type = None
    
    for i in range(length, len(df)):
        try:
            high_val = float(df['High'].iloc[i])
            low_val = float(df['Low'].iloc[i])
            
            # Ventana de lookback
            high_window = df['High'].iloc[i-length:i].apply(lambda x: float(x) if pd.notna(x) else np.nan)
            low_window = df['Low'].iloc[i-length:i].apply(lambda x: float(x) if pd.notna(x) else np.nan)
            
            is_high = high_val == high_window.max()
            is_low = low_val == low_window.min()
            
            deviation_pct = deviation / 100.0
            
            if is_high:
                if pd.isna(last_pivot) or high_val >= last_pivot * (1 + deviation_pct):
                    df.loc[df.index[i], 'ZigZag_Value'] = float(high_val)
                    df.loc[df.index[i], 'ZigZag_Type'] = 'High'
                    df.loc[df.index[i], 'ZigZag_Signal'] = True
                    last_pivot = float(high_val)
                    last_type = 'High'
                    
            elif is_low:
                if pd.isna(last_pivot) or low_val <= last_pivot * (1 - deviation_pct):
                    df.loc[df.index[i], 'ZigZag_Value'] = float(low_val)
                    df.loc[df.index[i], 'ZigZag_Type'] = 'Low'
                    df.loc[df.index[i], 'ZigZag_Signal'] = True
                    last_pivot = float(low_val)
                    last_type = 'Low'
                    
        except (ValueError, TypeError) as e:
            print(f"Error en índice {i}: {e}")
            continue    
    return df

def contar_decimales(numero):
    numero_str = str(numero)
    if '.' in numero_str:
        parte_decimal = numero_str.split('.')[1]
        return len(parte_decimal)
    else:
        return 0

def should_sell_due_to_risk(coin, CLOSE, time, sl, th):
    r = False
    if Sl(coin, CLOSE, sl):
        r = True	
    time_held = TimeHold(coin, time)
    if time_held > th:
        r = True		
    return r

def StopLoss_Time(coin, time, m_time, main_path):
    time_held = TimeHold(coin, time, main_path)
    if time_held > m_time:
        return True
    return False
# def Dynamic_StopLoss(coin, DF_Data, CLOSE, LENGHT, time_wait, value):
    # try:
        # coinfile = coin + ".st"
        # if Bought_at(coin):
            # #BA, BM, BB = Bollinger_Bands(DF_Data, LENGHT, 2)
            # if os.path.exists(coinfile):
                # if CLOSE > value:
                    # os.remove(coinfile)
                    # return False
                
                # if os.path.exists(coin + '.position'):
                    # with open(coin + '.position', 'r') as f:
                        # last_time = float(f.read().replace(".0", ""))
                # else:
                    # return False
                    
                # with open(coinfile, "r") as f:
                    # first_time = float(f.read().strip())			
                # time_elapsed = ((last_time - first_time) / 60) / 1000

                # if time_elapsed >= time_wait:
                    # os.remove(coinfile)
                    # return True
            # else:				
                # if CLOSE < value:
                    # if os.path.exists(coin + '.position'):
                        # with open(coin + '.position', 'r') as f:
                            # last_time = float(f.read().replace(".0", ""))
                    # else:
                        # return False
                        
                    # with open(coinfile, 'w') as f:
                        # f.write(str(last_time))
                    # return False
    # except Exception as e:
        # exc_type, exc_obj, exc_tb = sys.exc_info()
        # print(e)
        # print('check_bollingerLow_and_holding Error on line ' + str(exc_tb.tb_lineno))
        # pass 
    # return False
    
def calculate_spread(min_spread, max_spread, DF_Data):
    open_price = DF_Data['Open'].iloc[-1]   # precio de compra
    close_price = DF_Data['Close'].iloc[-1] # precio de venta
    spread = (close_price - open_price) / open_price * 100  # % de spread
    if spread <= min_spread:
        return 1
    elif spread >= max_spread:
        return 2

def calculate_fibonacci(data, length=100):
    if len(data) < length:
        raise ValueError("No hay suficientes datos para calcular Fibonacci.")
    sub_data = data[-length:]
    
    max_price = sub_data['High'].max()
    min_price = sub_data['Low'].min()
    
    diff = max_price - min_price
    
    niveles = {
        '0.0': max_price,
        '0.236': max_price - 0.236 * diff,
        '0.382': max_price - 0.382 * diff,
        '0.5': max_price - 0.5 * diff,
        '0.618': max_price - 0.618 * diff,
        '0.786': max_price - 0.786 * diff,
        '1.0': min_price
    }
    return niveles

def Fibonacci(data, length=100):
    fibo = calculate_fibonacci(data, length)
    nivel_618 = fibo['0.618']
    
    precio_anterior = data['Close'].iloc[-2]
    precio_actual = data['Close'].iloc[-1]

    if precio_anterior < nivel_618 and precio_actual > nivel_618:
        return 1 #"COMPRA"
    elif precio_anterior > nivel_618 and precio_actual < nivel_618:
        return -1 #"VENTA"
    else:
        return 0 #"ESPERAR"

def B(data):
    return (data['High'].iloc[-1] + data['Low'].iloc[-1] + data['Close'].iloc[-1]) / 3
    
def Adx(data, adx_period=14):
    adx = ADXIndicator(
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        window=adx_period
    )

    ADX = adx.adx()
    DI_positive = adx.adx_pos()
    DI_negative = adx.adx_neg()

    return ADX.iloc[-1], DI_positive.iloc[-1], DI_negative.iloc[-1]
    
def filter_with_adx(data, adx_umbral=25):
    adx_indicador = ADXIndicator(data['High'], data['Low'], data['Close'], window=14)
    adx = adx_indicador.adx().iloc[-1]
    return adx < adx_umbral
    
def Atr(data, atr_period=14):
    atr = AverageTrueRange(
        high=data['High'],
        low=data['Low'], 
        close=data['Close'],
        window=atr_period
    ).average_true_range()
    
    return atr.iloc[-1]  # ← Valor ABSOLUTO, no normalizado

def Atr_df(data, atr_period=14):
    atr = AverageTrueRange(
        high=data['High'],
        low=data['Low'], 
        close=data['Close'],
        window=atr_period
    ).average_true_range()
    
    return atr
    
def Dynamic_Sl_Atr(coin, current_price, data, atr_multiplier=2.5):
    bought_at = Bought_at(coin)	
    if bought_at <= 0:
        return False	
    atr_absolute = Atr(data, 14)	
    sl_price = bought_at - (atr_absolute * atr_multiplier)	
    if current_price <= sl_price:
        return True	
    return False
    
def Check_Volume_df(data, window=5, umbral=1.2):
    volumen_actual = data['Volume']
    volumen_promedio = data['Volume'].rolling(window).mean()
    return volumen_actual > umbral * volumen_promedio
    
def Check_Volume_Growth(data, velas=3):
    # Detecta si el volumen ha subido en las últimas N velas
    vol = data['Volume'].tail(velas).values
    return all(vol[i] > vol[i-1] for i in range(1, len(vol)))

def Low_Volatility(Data, CLOSE):
    return Atr(Data, 14) < (CLOSE * 0.005)
    
def Low_Volatility_df(Data, CLOSE):
    return Atr_df(Data, 14) < (CLOSE * 0.005)
    
def Calculate_Market_Direction(data, adx_period=14, adx_threshold=20):
    ADX, DI_positive, DI_negative = Adx(data, adx_period)
    
    if ADX > adx_threshold:
        if DI_positive > DI_negative:
            return 'alcista'
        elif DI_negative > DI_positive:
            return 'bajista'		
    return 'sin_tendencia'
    
def Atr_Normalized(data, atr_period=14):
    atr_value = AverageTrueRange(
        high=data['High'],
        low=data['Low'],
        close=data['Close'], 
        window=atr_period
    ).average_true_range().iloc[-1]
    
    normalized_atr = atr_value / data['Close'].iloc[-1]
    return normalized_atr  # ← Ej: 0.015 para 1.5% de volatilidad
    
def Check_Volume(data, window=5, umbral=1.2):
    volumen_actual = data['Volume'].iloc[-1]
    volumen_promedio = data['Volume'].rolling(window).mean().iloc[-1]
    return bool(volumen_actual > umbral * volumen_promedio)
    
def Check_Consolidation(data, adx_threshold=20, atr_threshold=0.003):
    adx, _, _ = Adx(data)
    atr = Atr_Normalized(data)
    return adx < adx_threshold and atr < atr_threshold
    
def Detect_Market_Type(data, umbral_alto_volatilidad=0.01):
    tendencia = Calculate_Market_Direction(data, 20, 20)
    volatilidad = Atr_Normalized(data, 20)
    consolidacion = Check_Consolidation(data, 20, 0.003)
    volumen_alto = Check_Volume(data, 20, 1.2)
    if tendencia == 'alcista' and volumen_alto:
        return 'tendencia_alcista_confirmada'
    elif tendencia == 'bajista' and volumen_alto:
        return 'tendencia_bajista_confirmada'
    elif consolidacion and not volumen_alto:
        return 'consolidacion_confirmado'
    elif volatilidad > umbral_alto_volatilidad:
        return 'volatil_confirmado'
    else:
        return 'rango_lateral_confirmado'

def Pivots_Hl_df(df, left=10, right=10):
    highs = df['High'].to_numpy(dtype=float)
    lows = df['Low'].to_numpy(dtype=float)

    pivot_highs_idx = []
    pivot_lows_idx = []

    for i in range(left, len(df) - right):
        window_high = highs[i-left:i+right+1]
        window_low = lows[i-left:i+right+1]

        if highs[i] == np.max(window_high):
            pivot_highs_idx.append(i)

        if lows[i] == np.min(window_low):
            pivot_lows_idx.append(i)

    # Valores en los índices encontrados
    pivot_high_prices = highs[pivot_highs_idx] if pivot_highs_idx else []
    pivot_low_prices = lows[pivot_lows_idx] if pivot_lows_idx else []
    # pivot_points = ta.PivotPoints(high=data['High'], low=data['Low'], close=data['close'], method="standard")
    # print(pivot_points.p())
    # pivot_high_prices = 0
    # pivot_low_prices = 0
    
    return pivot_high_prices, pivot_low_prices
    
def Pivots_Hl(df, left=10, right=10):
    high_prices, low_prices = Pivots_Hl_df(df, left, right)
    last_high = high_prices[-1] if len(high_prices) > 0 else None
    last_low = low_prices[-1] if len(low_prices) > 0 else None
    return last_high, last_low

def detect_new_pivots(df, left=10, right=10):
    """
    Detecta si la última barra de un DataFrame es un nuevo pivote alto o bajo.
    
    Args:
        df (pd.DataFrame): DataFrame con columnas 'High' y 'Low'.
        left (int): Número de barras a la izquierda para confirmar el pivote.
        
    Returns:
        tuple: (new_high_pivot, new_low_pivot)
    """
    if len(df) < left + 1:
        # No hay suficientes datos para verificar
        return None, None

    highs = df['High'].to_numpy(dtype=float)
    lows = df['Low'].to_numpy(dtype=float)

    # Precios de la última barra
    last_high = highs[-1]
    last_low = lows[-1]

    # Precios de la ventana 'left' anterior a la última barra
    window_highs = highs[-left-1:-1]
    window_lows = lows[-right-1:-1]

    new_high_pivot = None
    new_low_pivot = None

    # Comprobar si la última barra es un nuevo máximo local
    if last_high >= np.max(window_highs):
        new_high_pivot = last_high

    # Comprobar si la última barra es un nuevo mínimo local
    if last_low <= np.min(window_lows):
        new_low_pivot = last_low

    return new_high_pivot, new_low_pivot

def Pivots_HL_optimized(data, left=10, right=10):
    try:
        if 'High' not in data.columns or 'Low' not in data.columns:
            raise ValueError("El DataFrame debe contener las columnas 'High' y 'Low'")
        
        result = data.copy()
        left_high_max = data['High'].shift(1).rolling(window=left).max()
        right_high_max = data['High'].shift(-right).rolling(window=right).max().shift(right - 1)
        
        left_low_min = data['Low'].shift(1).rolling(window=left).min()
        right_low_min = data['Low'].shift(-right).rolling(window=right).min().shift(right - 1)
        
        result['Pivot_High'] = (data['High'] > left_high_max) & (data['High'] > right_high_max)
        result['Pivot_Low'] = (data['Low'] < left_low_min) & (data['Low'] < right_low_min)
        
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(e)
        print('Pivots_HL_optimized Error on line ' + str(exc_tb.tb_lineno))
        pass 
    return result['Pivot_High'], result['Pivot_Low']
    
def calcular_rangos_dinamicos_macd_rsi(df, rsi_l=14, macd_f=12, macd_l=26, macd_s=9, rsi_pct_buy=90, rsi_pct_sell=10, macd_pct_buy=75, macd_pct_sell=25):
    df = df.copy()
    df['RSI'] = Rsi_df(df, rsi_l)
    df['MACD'] = Macd_Ind_df(df, macd_f, macd_l, macd_s)

    # Convertir a numérico y eliminar NaN
    macd = pd.to_numeric(df['MACD'], errors='coerce').dropna()
    rsi = pd.to_numeric(df['RSI'], errors='coerce').dropna()

    # RSI: percentiles dinámicos
    valor_rsi_sobrecompra = np.percentile(rsi, rsi_pct_buy)
    valor_rsi_sobreventa = np.percentile(rsi, rsi_pct_sell)

    # MACD: percentiles dinámicos (separados en positivos y negativos)
    macd_pos = macd[macd > 0]
    macd_neg = macd[macd < 0]

    valor_macd_buy = np.percentile(macd_pos, macd_pct_buy) if len(macd_pos) > 0 else 0
    valor_macd_venta = np.percentile(macd_neg, macd_pct_sell) if len(macd_neg) > 0 else 0

    return valor_rsi_sobrecompra, valor_rsi_sobreventa, valor_macd_buy, valor_macd_venta

def guardar_rangos_dinamicos(coin, n_velas, rsi_over, rsi_under, macd_buy, macd_sell):
    try:
        FILE = "rangos_dinamicos.json"
        FILE1 = "rangos_dinamicos_1.json"

        if not os.path.exists(FILE1):
            data_1 = {}
            data_1[coin] = []
            data_1[coin] = {
                "coin": coin,
                "rsi_over": rsi_over,
                "rsi_under": rsi_under,
                "macd_buy": macd_buy,
                "macd_sell": macd_sell
            }
            with open(FILE1, "w") as f:
                json.dump(data_1, f, indent=2)
            data_1 = {}
            data_1[coin] = []
            
        if not os.path.exists(FILE):
            data = {}
        else:
            with open(FILE, "r") as f:
                data = json.load(f)

        # si la coin no existe, inicializar lista
        if coin not in data:
            data[coin] = []

        # agregar nuevo registro
        data[coin].append({
            "rsi_over": rsi_over,
            "rsi_under": rsi_under,
            "macd_buy": macd_buy,
            "macd_sell": macd_sell
        })

        # guardar el archivo actualizado
        with open(FILE, "w") as f:
            json.dump(data, f, indent=2)

        # si llegamos a n_velas registros → calcular promedio
        if len(data[coin]) >= n_velas:
            rsi_over_avg = round(sum(d["rsi_over"] for d in data[coin]) / len(data[coin]), 2)
            rsi_under_avg = round(sum(d["rsi_under"] for d in data[coin]) / len(data[coin]), 2)
            macd_buy_avg = round(sum(d["macd_buy"] for d in data[coin]) / len(data[coin]), 2)
            macd_sell_avg = round(sum(d["macd_sell"] for d in data[coin]) / len(data[coin]), 2)
            os.remove(FILE)
            os.remove(FILE1)
            data_1 = {}
            data_1[coin] = {}
            data_1[coin] = {
                "rsi_over": rsi_over_avg,
                "rsi_under": rsi_under_avg,
                "macd_buy": macd_buy_avg,
                "macd_sell": macd_sell_avg
            }
            with open(FILE1, "w") as f:
                json.dump(data_1, f, indent=2)
            #data[coin] = []
            #with open(FILE, "w") as f:
                #json.dump(data, f, indent=2)
        else:
            data2 = {}
            with open(FILE1, "r") as f:
                data2 = json.load(f)
            return {
                "rsi_over": float(data2[coin]['rsi_over']),
                "rsi_under": float(data2[coin]['rsi_under']),
                "macd_buy": float(data2[coin]['macd_buy']),
                "macd_sell": float(data2[coin]['macd_sell'])
            }

        return {
            "rsi_over": rsi_over_avg,
            "rsi_under": rsi_under_avg,
            "macd_buy": macd_buy_avg,
            "macd_sell": macd_sell_avg
        }

    except Exception as e:
        write_log(f'{txcolors.DEFAULT}{SIGNAL_NAME}: {txcolors.SELL_LOSS} - Exception: guardar_rangos_dinamicos(): {e}{txcolors.DEFAULT}', SIGNAL_NAME + '.log', True, False)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        write_log('Error on line ' + str(exc_tb.tb_lineno), SIGNAL_NAME + '.log', True, False)

def calcular_probabilidad_y_movimientos(df):
    if df.empty or len(df) < 2:
        return {
            'prob_subida': 0,
            'prob_bajada': 0,
            'avg_subida': 0,
            'avg_bajada': 0,
            'volatilidad_historica': 0
        }

    precios = df['Close']

    retornos = precios.pct_change().dropna()

    subidas = retornos[retornos > 0]
    bajadas = retornos[retornos < 0]

    total_movimientos = len(retornos)
    if total_movimientos == 0:
        return {
            'prob_subida': 0,
            'prob_bajada': 0,
            'avg_subida': 0,
            'avg_bajada': 0,
            'volatilidad_historica': 0
        }

    prob_subida = (len(subidas) / total_movimientos) * 100
    prob_bajada = (len(bajadas) / total_movimientos) * 100

    avg_subida = subidas.mean() * 100 if not subidas.empty else 0
    avg_bajada = bajadas.mean() * 100 if not bajadas.empty else 0

    volatilidad = retornos.std()

    resultados = {
        'prob_subida': round(prob_subida, 2),
        'prob_bajada': round(prob_bajada, 2),
        'avg_subida': round(avg_subida, 2),
        'avg_bajada': round(avg_bajada, 2),
        'volatilidad_historica': round(volatilidad, 4)
    }

    return resultados

def calcular_probabilidad_5m_adelante(df):
    print(df)
    if df.empty or len(df) < 5:
        print("El DataFrame es muy pequeño para calcular períodos de 5 minutos.")
        return {
            'prob_subida_5m': 0,
            'prob_bajada_5m': 0,
            'avg_subida_5m': 0,
            'avg_bajada_5m': 0,
            'volatilidad_historica_5m': 0
        }

    # 2. Resamplear (agrupar) los datos de 1 minuto a 5 minutos
    # Esto toma el precio de cierre de la primera vela y el precio de cierre de la última vela
    # de cada bloque de 5 minutos para calcular el cambio.
    # Necesitas que el índice del DataFrame sea de tipo datetime.
    try:
        df.index = pd.to_datetime(df.index)
        df_5m = df['Close'].resample('5min').ohlc()
    except Exception as e:
        print(f"Error al convertir el índice a datetime: {e}")
        print("Asegúrate de que el índice del DataFrame sea de tipo fecha y hora.")
        return None

    # 3. Calcular los retornos porcentuales entre el inicio y el final de cada período de 5m
    retornos_5m = (df_5m['Close'] - df_5m['Open']) / df_5m['Open']

    # 4. Clasificar los retornos en subidas y bajadas
    subidas = retornos_5m[retornos_5m > 0]
    bajadas = retornos_5m[retornos_5m < 0]

    # 5. Calcular las probabilidades y promedios
    total_movimientos = len(retornos_5m)
    if total_movimientos == 0:
        return {
            'prob_subida_5m': 0,
            'prob_bajada_5m': 0,
            'avg_subida_5m': 0,
            'avg_bajada_5m': 0,
            'volatilidad_historica_5m': 0
        }

    prob_subida = (len(subidas) / total_movimientos) * 100
    prob_bajada = (len(bajadas) / total_movimientos) * 100

    avg_subida = subidas.mean() * 100 if not subidas.empty else 0
    avg_bajada = bajadas.mean() * 100 if not bajadas.empty else 0

    volatilidad = retornos_5m.std()

    # 6. Almacenar los resultados en un diccionario
    resultados = {
        'prob_subida_5m': round(prob_subida, 2),
        'prob_bajada_5m': round(prob_bajada, 2),
        'avg_subida_5m': round(avg_subida, 2),
        'avg_bajada_5m': round(avg_bajada, 2),
        'volatilidad_historica_5m': round(volatilidad, 4)
    }

    return resultados
    
def Trailing_Stop_Loss(PAIR, CLOSE, TRAILING_PERCENT, main_path):
    """
    Trailing Stop Loss basado en porcentaje.
    El stop loss se ajusta automáticamente cuando el precio sube.
    
    Args:
        PAIR: Par de trading (ej: 'BTCUSDT')
        CLOSE: Precio actual de cierre
        TRAILING_PERCENT: Porcentaje para trailing (ej: 2.0 para 2%)
        main_path: Ruta principal del proyecto
    
    Returns:
        bool: True si se debe vender por trailing stop loss
    """
    try:
        from Boot import set_correct_mode
        TEST_MODE, BACKTESTING_MODE, USE_TESNET_IN_ONLINEMODE, USE_SIGNALLING_MODULES = set_correct_mode(LANGUAGE, MODE, True)
        
        # Obtener precio de compra
        bought_at = Bought_at(PAIR, main_path)
        if bought_at <= 0:
            return False
            
        if TEST_MODE:
            file_prefix = 'test_'
        else:
            file_prefix = 'live_'
        
        # Archivo para guardar el precio máximo alcanzado
        trail_file = main_path + file_prefix + f'trailing_{PAIR.replace("/", "_")}.json'
        
        current_price = float(CLOSE)
        buy_price = float(bought_at)
        
        # Si no existe archivo de trailing, inicializar con precio de compra
        if not os.path.exists(trail_file):
            trail_data = {
                'buy_price': buy_price,
                'highest_price': buy_price,
                'current_stop': buy_price * (1 - TRAILING_PERCENT/100)
            }
            with open(trail_file, 'w') as f:
                json.dump(trail_data, f)
            return False
        
        # Leer datos de trailing existentes
        with open(trail_file, 'r') as f:
            trail_data = json.load(f)
        
        highest_price = float(trail_data['highest_price'])
        current_stop = float(trail_data['current_stop'])
        
        # Actualizar precio máximo si el precio actual es mayor
        if current_price > highest_price:
            highest_price = current_price
            current_stop = highest_price * (1 - TRAILING_PERCENT/100)
            
            # Guardar actualización
            trail_data['highest_price'] = highest_price
            trail_data['current_stop'] = current_stop
            
            with open(trail_file, 'w') as f:
                json.dump(trail_data, f)
            
            return False
        
        # Verificar si el precio cayó por debajo del trailing stop
        if current_price <= current_stop:
            # Eliminar archivo de trailing
            if os.path.exists(trail_file):
                os.remove(trail_file)
            return True
        
        return False
        
    except Exception as e:
        write_log(f'{txcolors.DEFAULT}{SIGNAL_NAME}: {txcolors.SELL_LOSS} - Exception: Trailing_Stop_Loss(): {e}{txcolors.DEFAULT}', SIGNAL_NAME + '.log', True, False)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        write_log('Error on line ' + str(exc_tb.tb_lineno), SIGNAL_NAME + '.log', True, False)
        return False


def Trailing_Take_Profit(PAIR, CLOSE, TAKE_PROFIT_PERCENT, TRAILING_PERCENT, main_path):
    """
    Trailing Take Profit: Bloquea ganancias cuando se alcanza un take profit,
    luego usa trailing stop para proteger ganancias.
    
    Args:
        PAIR: Par de trading
        CLOSE: Precio actual
        TAKE_PROFIT_PERCENT: Porcentaje inicial de take profit (ej: 3.0)
        TRAILING_PERCENT: Porcentaje de trailing después de TP (ej: 1.5)
        main_path: Ruta principal
    
    Returns:
        bool: True si se debe vender por trailing take profit
    """
    try:
        from Boot import set_correct_mode
        TEST_MODE, BACKTESTING_MODE, USE_TESNET_IN_ONLINEMODE, USE_SIGNALLING_MODULES = set_correct_mode(LANGUAGE, MODE, True)
        
        bought_at = Bought_at(PAIR, main_path)
        if bought_at <= 0:
            return False
            
        if TEST_MODE:
            file_prefix = 'test_'
        else:
            file_prefix = 'live_'
        
        trail_file = main_path + file_prefix + f'trailing_tp_{PAIR.replace("/", "_")}.json'
        current_price = float(CLOSE)
        buy_price = float(bought_at)
        
        # Calcular precio objetivo de take profit inicial
        initial_tp_price = buy_price * (1 + TAKE_PROFIT_PERCENT/100)
        
        # Si no existe archivo de trailing TP
        if not os.path.exists(trail_file):
            # Verificar si ya alcanzamos el take profit inicial
            if current_price >= initial_tp_price:
                # Inicializar trailing TP
                trail_data = {
                    'buy_price': buy_price,
                    'tp_reached': True,
                    'highest_price': current_price,
                    'trailing_stop': current_price * (1 - TRAILING_PERCENT/100)
                }
                with open(trail_file, 'w') as f:
                    json.dump(trail_data, f)
                return False
            else:
                return False
        
        # Leer datos existentes
        with open(trail_file, 'r') as f:
            trail_data = json.load(f)
        
        # Solo seguimos si ya alcanzamos TP inicial
        if not trail_data.get('tp_reached', False):
            return False
        
        highest_price = float(trail_data['highest_price'])
        trailing_stop = float(trail_data['trailing_stop'])
        
        # Actualizar precio máximo
        if current_price > highest_price:
            highest_price = current_price
            trailing_stop = highest_price * (1 - TRAILING_PERCENT/100)
            
            trail_data['highest_price'] = highest_price
            trail_data['trailing_stop'] = trailing_stop
            
            with open(trail_file, 'w') as f:
                json.dump(trail_data, f)
            
            return False
        
        # Verificar si caímos por debajo del trailing stop
        if current_price <= trailing_stop:
            if os.path.exists(trail_file):
                os.remove(trail_file)
            return True
        
        return False
        
    except Exception as e:
        write_log(f'{txcolors.DEFAULT}{SIGNAL_NAME}: {txcolors.SELL_LOSS} - Exception: Trailing_Take_Profit(): {e}{txcolors.DEFAULT}', SIGNAL_NAME + '.log', True, False)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        write_log('Error on line ' + str(exc_tb.tb_lineno), SIGNAL_NAME + '.log', True, False)
        return False


def ATR_Stop_Loss(PAIR, CLOSE, DF_Data, ATR_MULTIPLIER=2.0, ATR_PERIOD=14, main_path=None):
    """
    Stop Loss dinámico basado en ATR (Average True Range).
    El stop loss se ajusta según la volatilidad del mercado.
    
    Args:
        PAIR: Par de trading
        CLOSE: Precio actual
        DF_Data: DataFrame con datos de precio
        ATR_MULTIPLIER: Multiplicador del ATR (ej: 2.0)
        ATR_PERIOD: Período para cálculo del ATR
        main_path: Ruta principal
    
    Returns:
        bool: True si se debe vender por stop loss basado en ATR
    """
    try:
        bought_at = Bought_at(PAIR, main_path) if main_path else Bought_at(PAIR)
        if bought_at <= 0:
            return False
        
        # Calcular ATR actual (valor absoluto)
        atr_value = Atr(DF_Data, ATR_PERIOD)
        
        # Calcular precio de stop loss
        sl_price = float(bought_at) - (float(atr_value) * ATR_MULTIPLIER)
        
        # Verificar si el precio actual está por debajo del SL
        if float(CLOSE) <= sl_price:
            return True
        
        return False
        
    except Exception as e:
        write_log(f'{txcolors.DEFAULT}{SIGNAL_NAME}: {txcolors.SELL_LOSS} - Exception: ATR_Stop_Loss(): {e}{txcolors.DEFAULT}', SIGNAL_NAME + '.log', True, False)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        write_log('Error on line ' + str(exc_tb.tb_lineno), SIGNAL_NAME + '.log', True, False)
        return False


def ATR_Take_Profit(PAIR, CLOSE, DF_Data, ATR_MULTIPLIER=3.0, ATR_PERIOD=14, main_path=None):
    """
    Take Profit dinámico basado en ATR.
    
    Args:
        PAIR: Par de trading
        CLOSE: Precio actual
        DF_Data: DataFrame con datos
        ATR_MULTIPLIER: Multiplicador para TP (generalmente mayor que para SL)
        ATR_PERIOD: Período ATR
        main_path: Ruta principal
    
    Returns:
        bool: True si se debe vender por take profit basado en ATR
    """
    try:
        bought_at = Bought_at(PAIR, main_path) if main_path else Bought_at(PAIR)
        if bought_at <= 0:
            return False
        
        # Calcular ATR
        atr_value = Atr(DF_Data, ATR_PERIOD)
        
        # Calcular precio de take profit
        tp_price = float(bought_at) + (float(atr_value) * ATR_MULTIPLIER)
        
        # Verificar si el precio actual superó el TP
        if float(CLOSE) >= tp_price:
            return True
        
        return False
        
    except Exception as e:
        write_log(f'{txcolors.DEFAULT}{SIGNAL_NAME}: {txcolors.SELL_LOSS} - Exception: ATR_Take_Profit(): {e}{txcolors.DEFAULT}', SIGNAL_NAME + '.log', True, False)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        write_log('Error on line ' + str(exc_tb.tb_lineno), SIGNAL_NAME + '.log', True, False)
        return False

def Cleanup_Trailing_Files(PAIR):
    """
    Limpia archivos de trailing cuando se vende una posición.
    
    Args:
        PAIR: Par de trading
    """
    try:
        from Boot import set_correct_mode
        TEST_MODE, BACKTESTING_MODE, USE_TESNET_IN_ONLINEMODE, USE_SIGNALLING_MODULES = set_correct_mode(LANGUAGE, MODE, True)
        
        if TEST_MODE:
            file_prefix = 'test_'
        else:
            file_prefix = 'live_'
        
        # Archivos a eliminar
        files_to_clean = [
            file_prefix + f'trailing_{PAIR.replace("/", "_")}.json',
            file_prefix + f'trailing_tp_{PAIR.replace("/", "_")}.json'
        ]
        
        for file_path in files_to_clean:
            if os.path.exists(file_path):
                os.remove(file_path)
                
    except Exception as e:
        write_log(f'{txcolors.DEFAULT}{SIGNAL_NAME}: {txcolors.WARNING} - Exception al limpiar archivos trailing: {e}{txcolors.DEFAULT}', SIGNAL_NAME + '.log', True, False)

def calculate_support_resistance_levels(Data, lookback=50):
    """
    Calcula niveles de soporte y resistencia basados en pivotes históricos
    """
    try:
        if len(Data) < lookback:
            return {'supports': [], 'resistances': [], 'current_price': Data['Close'].iloc[-1]}
        
        df = Data.tail(lookback).copy()
        
        # Encontrar pivotes altos (resistencias)
        resistances = []
        for i in range(2, len(df)-2):
            if (df['High'].iloc[i] > df['High'].iloc[i-1] and 
                df['High'].iloc[i] > df['High'].iloc[i-2] and
                df['High'].iloc[i] > df['High'].iloc[i+1] and
                df['High'].iloc[i] > df['High'].iloc[i+2]):
                resistances.append({
                    'price': float(df['High'].iloc[i]),
                    'index': i,
                    'strength': 1  # Contar toques posteriores para fuerza
                })
        
        # Encontrar pivotes bajos (soportes)
        supports = []
        for i in range(2, len(df)-2):
            if (df['Low'].iloc[i] < df['Low'].iloc[i-1] and 
                df['Low'].iloc[i] < df['Low'].iloc[i-2] and
                df['Low'].iloc[i] < df['Low'].iloc[i+1] and
                df['Low'].iloc[i] < df['Low'].iloc[i+2]):
                supports.append({
                    'price': float(df['Low'].iloc[i]),
                    'index': i,
                    'strength': 1
                })
        
        # Agrupar niveles cercanos (tolerancia del 1%)
        def group_levels(levels, tolerance=0.01):
            if not levels:
                return []
            
            levels_sorted = sorted(levels, key=lambda x: x['price'])
            grouped = []
            current_group = [levels_sorted[0]]
            
            for level in levels_sorted[1:]:
                if abs(level['price'] - current_group[0]['price']) / current_group[0]['price'] <= tolerance:
                    current_group.append(level)
                else:
                    # Calcular precio promedio del grupo
                    avg_price = sum(l['price'] for l in current_group) / len(current_group)
                    grouped.append({
                        'price': avg_price,
                        'strength': len(current_group),
                        'members': current_group
                    })
                    current_group = [level]
            
            if current_group:
                avg_price = sum(l['price'] for l in current_group) / len(current_group)
                grouped.append({
                    'price': avg_price,
                    'strength': len(current_group),
                    'members': current_group
                })
            
            return sorted(grouped, key=lambda x: x['strength'], reverse=True)
        
        grouped_resistances = group_levels(resistances)
        grouped_supports = group_levels(supports)
        
        current_price = float(Data['Close'].iloc[-1])
        
        # Encontrar resistencia más cercana por encima del precio actual
        next_resistance = None
        for res in grouped_resistances:
            if res['price'] > current_price:
                next_resistance = res
                break
        
        # Encontrar soporte más cercano por debajo del precio actual
        next_support = None
        for sup in grouped_supports:
            if sup['price'] < current_price:
                next_support = sup
                break
        
        return {
            'supports': grouped_supports[:5],  # Top 5 soportes
            'resistances': grouped_resistances[:5],  # Top 5 resistencias
            'next_support': next_support,
            'next_resistance': next_resistance,
            'current_price': current_price
        }
        
    except Exception as e:
        write_log(f'{txcolors.DEFAULT}{SIGNAL_NAME}: Error en calculate_support_resistance_levels: {e}', SIGNAL_NAME + '.log', True, False)
        return {'supports': [], 'resistances': [], 'current_price': 0}

def calculate_next_resistance(Data, lookback=100, tolerance_pct=1.5):
    """
    Calcula el próximo nivel de resistencia por encima del precio actual
    """
    try:
        if len(Data) < lookback:
            return None
        
        current_price = Data['Close'].iloc[-1]
        df = Data.tail(lookback)
        
        # Método 1: Pivots altos recientes
        pivots_high = []
        window = 5  # Velas a cada lado para identificar pivote
        
        for i in range(window, len(df)-window):
            if df['High'].iloc[i] == df['High'].iloc[i-window:i+window+1].max():
                pivots_high.append(float(df['High'].iloc[i]))
        
        # Método 2: Máximos de Fibonacci (simplificado)
        recent_high = df['High'].max()
        recent_low = df['Low'].min()
        
        fib_levels = {
            '0.236': recent_high - (recent_high - recent_low) * 0.236,
            '0.382': recent_high - (recent_high - recent_low) * 0.382,
            '0.5': recent_high - (recent_high - recent_low) * 0.5,
            '0.618': recent_high - (recent_high - recent_low) * 0.618,
            '0.786': recent_high - (recent_high - recent_low) * 0.786,
        }
        
        # Combinar métodos y filtrar
        all_resistances = pivots_high + list(fib_levels.values())
        
        # Filtrar resistencias por encima del precio actual
        resistances_above = [r for r in all_resistances if r > current_price]
        
        if not resistances_above:
            # Si no hay resistencias por encima, usar extensión de Fibonacci
            extension = 1.272  # Extensión común
            fib_extended = recent_high + (recent_high - recent_low) * (extension - 1)
            resistances_above = [fib_extended]
        
        # Agrupar resistencias cercanas (dentro del tolerance_pct)
        resistances_above.sort()
        grouped = []
        current_group = []
        
        for res in resistances_above:
            if not current_group:
                current_group.append(res)
            elif abs(res - current_group[0]) / current_group[0] <= tolerance_pct/100:
                current_group.append(res)
            else:
                grouped.append(sum(current_group) / len(current_group))
                current_group = [res]
        
        if current_group:
            grouped.append(sum(current_group) / len(current_group))
        
        # Retornar la resistencia más cercana
        return min(grouped) if grouped else current_price * 1.1  # Default: 10% arriba
        
    except Exception as e:
        write_log(f'{txcolors.DEFAULT}{SIGNAL_NAME}: Error en calculate_next_resistance: {e}', SIGNAL_NAME + '.log', True, False)
        return None
        
def analyze_market_type(Data, CLOSE):
    """
    Determina el tipo de mercado actual
    """
    # 1. Calcular volatilidad (ATR normalizado)
    atr_value = Atr(Data, 14)
    atr_percent = (atr_value / CLOSE) * 100
    
    # 2. Calcular tendencia (ADX)
    adx_value, di_plus, di_minus = Adx(Data, 14)
    
    # 3. Calcular rango (High-Low diferencia)
    recent_high = Data['High'].tail(20).max()
    recent_low = Data['Low'].tail(20).min()
    range_percent = ((recent_high - recent_low) / recent_low) * 100
    
    # 4. Determinar tipo
    if adx_value > 25 and di_plus > di_minus:
        return "STRONG_TREND_UP"
    elif adx_value > 25 and di_minus > di_plus:
        return "STRONG_TREND_DOWN"
    elif atr_percent > 3.0:
        return "HIGH_VOLATILITY"
    elif range_percent < 8.0:
        return "RANGING"
    elif Data['Close'].iloc[-1] > recent_high * 0.98:
        return "BREAKOUT"
    else:
        return "NORMAL"

def calculate_next_resistance(Data, lookback=100, tolerance_pct=1.5):
    """
    Calcula el próximo nivel de resistencia por encima del precio actual
    """
    try:
        if len(Data) < lookback:
            return None
        
        current_price = Data['Close'].iloc[-1]
        df = Data.tail(lookback)
        
        # Método 1: Pivots altos recientes
        pivots_high = []
        window = 5  # Velas a cada lado para identificar pivote
        
        for i in range(window, len(df)-window):
            if df['High'].iloc[i] == df['High'].iloc[i-window:i+window+1].max():
                pivots_high.append(float(df['High'].iloc[i]))
        
        # Método 2: Máximos de Fibonacci (simplificado)
        recent_high = df['High'].max()
        recent_low = df['Low'].min()
        
        fib_levels = {
            '0.236': recent_high - (recent_high - recent_low) * 0.236,
            '0.382': recent_high - (recent_high - recent_low) * 0.382,
            '0.5': recent_high - (recent_high - recent_low) * 0.5,
            '0.618': recent_high - (recent_high - recent_low) * 0.618,
            '0.786': recent_high - (recent_high - recent_low) * 0.786,
        }
        
        # Combinar métodos y filtrar
        all_resistances = pivots_high + list(fib_levels.values())
        
        # Filtrar resistencias por encima del precio actual
        resistances_above = [r for r in all_resistances if r > current_price]
        
        if not resistances_above:
            # Si no hay resistencias por encima, usar extensión de Fibonacci
            extension = 1.272  # Extensión común
            fib_extended = recent_high + (recent_high - recent_low) * (extension - 1)
            resistances_above = [fib_extended]
        
        # Agrupar resistencias cercanas (dentro del tolerance_pct)
        resistances_above.sort()
        grouped = []
        current_group = []
        
        for res in resistances_above:
            if not current_group:
                current_group.append(res)
            elif abs(res - current_group[0]) / current_group[0] <= tolerance_pct/100:
                current_group.append(res)
            else:
                grouped.append(sum(current_group) / len(current_group))
                current_group = [res]
        
        if current_group:
            grouped.append(sum(current_group) / len(current_group))
        
        # Retornar la resistencia más cercana
        return min(grouped) if grouped else current_price * 1.1  # Default: 10% arriba
        
    except Exception as e:
        write_log(f'{txcolors.DEFAULT}{SIGNAL_NAME}: Error en calculate_next_resistance: {e}', SIGNAL_NAME + '.log', True, False)
        return None

def Get_Balance_TestMode(main_path):
    return load_json_boot_stats("total_capital", main_path)

def _wma_calc(series, period):
    """Calcula la Media Móvil Ponderada (WMA) para la primera suavización (ssi)."""
    weights = np.arange(1, period + 1)
    # El método rolling().apply() se utiliza para aplicar la fórmula de WMA en cada ventana
    wma_series = series.rolling(window=period).apply(lambda x: np.dot(x, weights) / weights.sum(), raw=True)
    return wma_series

def _sma_calc(series, period):
    """Calcula la Media Móvil Simple (SMA) para la segunda suavización (TMA)."""
    return series.rolling(window=period).mean()


def tma_bands(data, TMAPeriodBack=35, ATRPeriodBack=75, ATRMultiplier=4.0):
    """
    Calcula las Bandas TMA (Triangular Moving Average Bands) con ATR.
    
    Basado en el script de Pine:
    ssi  = WMA(Close, TMAPeriodBack)
    tma  = SMA(ssi, TMAPeriodBack)  # SMA usado como aproximación al 'swma'
    range_series = ATR(ATRPeriodBack) * ATRMultiplier
    tmah = tma + range_series
    tmal = tma - range_series
    
    Args:
        data (pd.DataFrame): DataFrame con columnas 'Close', 'High', 'Low'.
        TMAPeriodBack (int): Período para la WMA y la segunda suavización (TMA). (defval=35)
        ATRPeriodBack (int): Período para el cálculo del ATR. (defval=75)
        ATRMultiplier (float): Multiplicador para el ancho de banda. (defval=4.0)

    Returns:
        pd.DataFrame: El DataFrame original con las columnas 'TMA', 'TMAH' (Upper Band) 
                      y 'TMAL' (Lower Band) añadidas.
    """
    
    df = data.copy()
    ssi = _wma_calc(df['Close'], TMAPeriodBack)
    tma = _sma_calc(ssi, TMAPeriodBack)
    df['TMA'] = tma
    atr_indicator = AverageTrueRange(high=df['High'], low=df['Low'], close=df['Close'], window=ATRPeriodBack)
    atr_series = atr_indicator.average_true_range()    
    range_series = atr_series * ATRMultiplier
    df['TMAH'] = df['TMA'] + range_series
    df['TMAL'] = df['TMA'] - range_series
    df.dropna(subset=['TMA', 'TMAH', 'TMAL'], inplace=True)    
    return round(df['TMA'].iloc[-1], 2), round(df['TMAH'].iloc[-1], 2), round(df['TMAL'].iloc[-1], 2)

def get_gann_status(df, pivot_strength=10):
    """
    df: DataFrame con ['High', 'Low']
    pivot_strength: Cuántas velas a la izquierda/derecha deben ser menores/mayores.
                    A mayor número, pivotes más grandes (menos ruido).
                    A menor número, pivotes más frecuentes (más ruido).
    """
    highs = df['High'].values
    lows = df['Low'].values
    
    swings = []
    types = [] 

    # Buscamos pivotes basados en la fuerza (pivot_strength)
    for i in range(pivot_strength, len(df) - pivot_strength):
        # DETECTAR MÁXIMO (Pivote High)
        # Es un High si es mayor que los 'n' anteriores y los 'n' posteriores
        is_high = True
        for j in range(1, pivot_strength + 1):
            if highs[i] <= highs[i-j] or highs[i] < highs[i+j]:
                is_high = False
                break
        
        if is_high:
            swings.append(highs[i])
            types.append("H")
            continue # No puede ser High y Low a la vez

        # DETECTAR MÍNIMO (Pivote Low)
        is_low = True
        for j in range(1, pivot_strength + 1):
            if lows[i] >= lows[i-j] or lows[i] > lows[i+j]:
                is_low = False
                break
        
        if is_low:
            swings.append(lows[i])
            types.append("L")

    # Clasificación de estructura (igual que antes)
    if len(swings) < 4: return "NN"

    if types[-1] == "L":
        return "HL" if swings[-1] > swings[-3] else "LL"
    elif types[-1] == "H":
        return "HH" if swings[-1] > swings[-3] else "LH"

    return "NN"
    
def get_bollinger_percentage_df(df, length=20, std=2):
    df = df.copy()
    bbands = ta.bbands(df['Close'], length=length, std=std)
    
    # Nombres de las columnas generadas por pandas_ta: 
    # BBL (Lower), BBM (Mid), BBU (Upper)
    lower = bbands[f'BBL_{length}_{float(std)}']
    upper = bbands[f'BBU_{length}_{float(std)}']
    
    # Fórmula del %b: (Precio - Low) / (Upper - Low)
    df['pct_b'] = (df['Close'] - lower) / (upper - lower)
    
    return df['pct_b']

def get_bollinger_percentage(df, length=20, std=2):
    df = df.copy()
    bbands = ta.bbands(df['Close'], length=length, std=std)
    
    # Nombres de las columnas generadas por pandas_ta: 
    # BBL (Lower), BBM (Mid), BBU (Upper)
    lower = bbands[f'BBL_{length}_{float(std)}']
    upper = bbands[f'BBU_{length}_{float(std)}']
    
    # Fórmula del %b: (Precio - Low) / (Upper - Low)
    df['pct_b'] = (df['Close'] - lower) / (upper - lower)
    
    return df['pct_b'].iloc[-1]