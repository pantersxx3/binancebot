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
import os
import sys
import glob
import math
from datetime import date, datetime, timedelta
import time
import threading
import pandas as pd
import pandas_ta as ta #pta
import talib
import ccxt
import re
import json
import pandas as pd
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
    Red = "\033[31m"
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
client = Client(access_key, secret_key)

LANGUAGE = parsed_config['script_options']['LANGUAGE']
USE_MOST_VOLUME_COINS = parsed_config['trading_options']['USE_MOST_VOLUME_COINS']
USE_SIGNALLING_MODULES = parsed_config['script_options']['USE_SIGNALLING_MODULES']
BACKTESTING_MODE_TIME_START = parsed_config['script_options']['BACKTESTING_MODE_TIME_START']
PAIR_WITH = parsed_config['trading_options']['PAIR_WITH']
SELL_ON_SIGNAL_ONLY = parsed_config['trading_options']['SELL_ON_SIGNAL_ONLY']
TEST_MODE = parsed_config['script_options']['TEST_MODE']
LOG_FILE = parsed_config['script_options'].get('LOG_FILE')
COINS_BOUGHT = parsed_config['script_options'].get('COINS_BOUGHT')
STOP_LOSS = parsed_config['trading_options']['STOP_LOSS']
TAKE_PROFIT = parsed_config['trading_options']['TAKE_PROFIT']
TRADE_SLOTS = parsed_config['trading_options']['TRADE_SLOTS']
BACKTESTING_MODE = parsed_config['script_options']['BACKTESTING_MODE']
BACKTESTING_MODE_TIME_START = parsed_config['script_options']['BACKTESTING_MODE_TIME_START']
MICROSECONDS = 2

if USE_MOST_VOLUME_COINS == True:
    TICKERS = "volatile_volume_" + str(date.today()) + ".txt"
else:
    TICKERS = 'tickers.txt'
            
#ACTUAL_POSITION = 0
SIGNAL_NAME = 'MEGATRONMOD'
#CREATE_BUY_SELL_FILES = True
#DEBUG = True
EXCHANGE = 'BINANCE'
SCREENER = 'CRYPTO'
SIGNAL_FILE_BUY = 'signals/' + SIGNAL_NAME + '.buy'
SIGNAL_FILE_SELL ='signals/' + SIGNAL_NAME + '.sell'
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
                timestamp = datetime.now().strftime("%Y-%d-%m %H:%M:%S") + ','                    
            else:
                timestamp = ""
            f.write(timestamp + result + '\n')            
    except Exception as e:
        print(f'{txcolors.DEFAULT}{SIGNAL_NAME} write_log: Exception in function: {e}{txcolors.DEFAULT}')
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print("Error on line " + str(exc_tb.tb_lineno))
        exit(1)

def read_position_csv(coin):
    try:
        pos1 = 0
        if os.path.exists(coin + '.position'):
            f = open(coin + '.position', 'r')
            pos1 = int(f.read().replace(".0", ""))
            f.close()
        else:
            pos1 = -1
            #os.remove(coin + '.position')
    except Exception as e:
        write_log(f'{txcolors.DEFAULT}{SIGNAL_NAME}: {txcolors.SELL_LOSS} - Exception: read_position_csv(): {e}{txcolors.DEFAULT}', SIGNAL_NAME + ".log", True, False)
        write_log("Error on line " + str(exc_tb.tb_lineno), SIGNAL_NAME + ".log", True, False)
        pass
    return pos1


def heikin_ashi(df):
    heikin_ashi_df = pd.DataFrame(index=df.index.values, columns=['open', 'high', 'low', 'close'])    
    heikin_ashi_df['close'] = (df['open'] + df['high'] + df['low'] + df['close']) / 4    
    for i in range(len(df)):
        if i == 0:
            heikin_ashi_df.iat[0, 0] = df['open'].iloc[0]
        else:
            heikin_ashi_df.iat[i, 0] = (heikin_ashi_df.iat[i-1, 0] + heikin_ashi_df.iat[i-1, 3]) / 2        
    heikin_ashi_df['high'] = heikin_ashi_df.loc[:, ['open', 'close']].join(df['high']).max(axis=1)    
    heikin_ashi_df['low'] = heikin_ashi_df.loc[:, ['open', 'close']].join(df['low']).min(axis=1)    
    return heikin_ashi_df
 
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
                c = d.query("time < @position1").tail(num_records)
                inttime = int(position1)/1000            
                position2 = c['time'].iloc[0]
                print(f'{txcolors.SELL_PROFIT}{SIGNAL_NAME}: {txcolors.DEFAULT}{BACKTESTING_MODE_TIME_START} - Posicion actual {datetime.fromtimestamp(inttime).strftime("%d/%m/%y %H:%M:%S")} - {position2} - {position1}...{txcolors.DEFAULT}')
                d = pd.DataFrame([])
        else:
            klines = client.get_historical_klines(symbol=p, interval=tf, start_str=str(num_records) + 'min ago UTC', limit=num_records)
            c = pd.DataFrame(klines)
            c.columns = ['time', 'Open', 'High', 'Low', 'Close', 'Volume', 'CloseTime', 'QuoteAssetVolume', 'Trades', 'TakerBuyBase', 'TakerBuyQuote', 'Ignore']
            c = c.drop(c.columns[[5, 6, 7, 8, 9, 10, 11]], axis=1)
            c['time'] = pd.to_datetime(c['time'], unit='ms')
            c['Close'] = c['Close'].astype(float)
    except Exception as e:
        write_log(f'{txcolors.DEFAULT}{SIGNAL_NAME}: {txcolors.SELL_LOSS} - Exception: get_analysis(): {e}{txcolors.DEFAULT}', SIGNAL_NAME + ".log", True, False)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        write_log("Error on line " + str(exc_tb.tb_lineno), SIGNAL_NAME + ".log", True, True) 
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
        write_log(f'{txcolors.DEFAULT}{SIGNAL_NAME}: {txcolors.SELL_LOSS} - Exception: load_json(): {e}{txcolors.DEFAULT}', SIGNAL_NAME + ".log", True, False)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        write_log("Error on line " + str(exc_tb.tb_lineno), SIGNAL_NAME + ".log", True, False)
    return value1, value2, value3

def TA_HMA(close, period):
    hma = ta.WMA(2 * ta.WMA(close, int(period / 2)) - ta.WMA(close, period), int(np.sqrt(period)))
    return hma
    
def isfloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False
        
def print_dic(dic, with_key=False, with_value=True):
    try:
        str1 = ""
        for key, value in dic.items():
            if with_key == False:
                if not value == {}:
                    if isfloat(value):
                        str1 = str1 + str(round(float(value),5)) + ","
                    else:
                        str1 = str1 + str(value) + ","
            else:
                if with_value:
                    if not value == {}:
                        if isfloat(value):    
                            str1 = str1 + str(key) + ":" + str(round(float(value),5)) + ","
                        else:
                            str1 = str1 + str(key) + ":" + str(value) + ","
                else:
                    str1 = str1 + str(key) + ","
    except Exception as e:
        write_log(f'{txcolors.DEFAULT}{SIGNAL_NAME}: {txcolors.SELL_LOSS} - Exception: print_dic(): {e}{txcolors.DEFAULT}', SIGNAL_NAME + ".log", True, False)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        write_log("Error on line " + str(exc_tb.tb_lineno), SIGNAL_NAME + ".log", True, False)
    return str1[:-1]
    
def list_indicators():
    try:
        list_variables = {}
        all_variables = dir()
        for name in all_variables:
            if name.endswith("_1MIN") and not name.endswith("_5MIN"):
                myvalue = round(float(eval(name)), 5)
                #list_variables = {name : myvalue}
                list_variables = {myvalue}
    except Exception as e:
        write_log(f'{txcolors.DEFAULT}{SIGNAL_NAME}: {txcolors.Red}Exception: list_indicators(): {e}', SIGNAL_NAME + ".log", True, False)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        write_log("Error on line " + str(exc_tb.tb_lineno), SIGNAL_NAME + ".log", True, False)
        pass
    return list_variables
 
def ichimoku_cloud(df):
    try:
        tenkan_sen = df.rolling(9).mean()
        kijun_sen = df.rolling(26).mean()
        senkou_span_a = (tenkan_sen + kijun_sen) / 2
        senkou_span_b = df.rolling(52).mean()
        chikou_span = df.shift(26)
    except Exception as e:
        write_log(f'{txcolors.DEFAULT}{SIGNAL_NAME}: {txcolors.Red}Exception: ichimoku_cloud(): {e}{txcolors.DEFAULT}', SIGNAL_NAME + ".log", True, False)
        write_log("Error on line " + str(exc_tb.tb_lineno), SIGNAL_NAME + ".log", True, False)
        pass
    return tenkan_sen, kijun_sen, senkou_span_a, senkou_span_b, chikou_span 
 
   
def analyze(d, pairs, buy=True):
    try:
        global BACKTESTING_MODE

        signal_coins1 = []
        signal_coins2 = []
        analysis1MIN = {}

        if TEST_MODE:
            file_prefix = 'test_'
        else:
            file_prefix = 'live_'     
    
        print(f'{txcolors.SELL_PROFIT}{SIGNAL_NAME}: {txcolors.DEFAULT}Analyzing {len(pairs)} coins...{txcolors.DEFAULT}')
        
        for pair in pairs:
            position2 = read_position_csv(pair)
            if not os.path.exists(pair + '.csv'): 
                print(f'{txcolors.SELL_PROFIT}{SIGNAL_NAME}: {txcolors.DEFAULT}Whaiting for Download Data...{txcolors.DEFAULT}')
                if USE_SIGNALLING_MODULES:
                    while not os.path.exists(pair + '.csv'):
                        time.sleep(1/1000) #Wait for download 
                else:
                    print(f'{txcolors.SELL_PROFIT}{SIGNAL_NAME}: {txcolors.DEFAULT}Data file not found. Whaiting for Download Data...{txcolors.DEFAULT}')
                        
            analysis1MIN = get_analysis(d, '1m', pair, position2, True, 1000)
            #analysis5MIN = get_analysis(d, '5m', pair, position2, False)
            #analysis15MIN = get_analysis('15m', pair)

            if analysis1MIN.empty == False:
                CLOSE = round(float(analysis1MIN['Close'].iloc[-1]),5) 
                #CLOSE_ANT = round(float(analysis1MIN['Close'].iloc[-2]),5)
                #TIME = analysis1MIN['time'].iloc[-1]            
                # print(f'{txcolors.SELL_PROFIT}MEGATRONMOD:{txcolors.DEFAULT} Time: {time_1m} Close: {CLOSE}')
                
                # df = pd.DataFrame()
                # df[['lower', 'middle', 'upper', 'bandwidth', 'percentcolumns']] = ta.bbands(analysis1MIN['Close'], length=10, std=2) #nbdevup=2,  nbdevdn=2, timeperiod=10)

                # B1_1MIN = round(df['upper'].iloc[-1], 2)
                # BM_1MIN = round(df['middle'].iloc[-1], 2)
                # B2_1MIN = round(df['lower'].iloc[-1], 2)
                # tenkan_sen, kijun_sen, senkou_span_a, senkou_span_b, chikou_span = ichimoku_cloud(analysis1MIN['Close'])
                # ICHIMOKU_SENKOUSPANA_1M = round(senkou_span_a.iloc[-1],5) 
                # ICHIMOKU_SENKOUSPANB_1M = round(senkou_span_b.iloc[-1],5)                 
                
                # SUPERTREND_1M = ta.supertrend(pd.to_numeric(analysis1MIN['High']), pd.to_numeric(analysis1MIN['Low']), pd.to_numeric(analysis1MIN['Close']), length=10.0, multiplier=3.0)
                # SUPERTRENDUP_1M = SUPERTREND_1M['SUPERTl_10_3.0'].iloc[-1]
                # SUPERTRENDDOWN_1M = SUPERTREND_1M['SUPERTs_10_3.0'].iloc[-1]
                
                # df_close_time = pd.concat([analysis1MIN['time'], analysis1MIN['Close']], axis=1)
                # preunix =  int(position2)/1000
                # unix = datetime.fromtimestamp(preunix)
                # datt = unix.strftime("%d/%m/%y %H:%M:%S")
                # pred_fut = preunix + (5*60)

                # print(f'CLOSE: {CLOSE} valor futuro en 5 minutos: {PREDICT_1MIN}%')
                
                # df1 = pd.DataFrame()
                # df1[['lower', 'middle', 'upper', 'bandwidth', 'percentcolumns']] = ta.bbands(analysis1MIN['Close'], period=18, std=2) #nbdevup=2,  nbdevdn=2, timeperiod=10)
                
                # B11_1MIN = round(df['upper'].iloc[-1], 2)
                # BM1_1MIN = round(df['middle'].iloc[-1], 2)
                # B21_1MIN = round(df['lower'].iloc[-1], 2)
                
                # write_log(f'MEGATRONMOD: position: {position2} B1_1MIN: {B1_1MIN}  BM_1MIN: {BM_1MIN} B2_1MIN: {B2_1MIN} CLOSE: {CLOSE}')
                # MOMENTUM50_1MIN = round(ta.MOM(analysis1MIN['Close'], timeperiod=50).iloc[-1], 2)
                # print("B1: ", B1_1MIN.iloc[-1], "BM: ", BM_1MIN.iloc[-1], "B2: ", B2_1MIN.iloc[-1])
                # B1_1MIN, B2_1MIN = bollinger_bands(analysis1MIN, 10)         
                     
                # EMA2_1MIN = round(ta.ema(analysis1MIN['Close'], length=2).iloc[-1],5)
                # EMA3_1MIN = round(ta.ema(analysis1MIN['Close'], length=3).iloc[-1],5)
                # EMA9_1MIN = round(ta.ema(analysis1MIN['Close'], length=9).iloc[-1],5)
                # EMA10_1MIN = round(ta.ema(analysis1MIN['Close'], length=10).iloc[-1],5)
                # EMA20_1MIN = round(ta.ema(analysis1MIN['Close'], length=20).iloc[-1],5)
                # EMA21_1MIN = round(ta.ema(analysis1MIN['Close'], length=21).iloc[-1],5)
                # EMA23_1MIN = round(ta.ema(analysis1MIN['Close'], length=23).iloc[-1],5)
                # EMA25_1MIN = round(ta.ema(analysis1MIN['Close'], length=25).iloc[-1],5)                
                # EMA50_1MIN = round(ta.ema(analysis1MIN['Close'], length=50).iloc[-1],5)
                # EMA100_1MIN = round(ta.ema(analysis1MIN['Close'], length=100).iloc[-1],5)
                
                # HMA70_1MIN = round(ta.hma(analysis1MIN['Close'],70).iloc[-1],5)
                # HMA90_1MIN = round(ta.hma(analysis1MIN['Close'],90).iloc[-1],5)  
                # HEIKINASHI_1M_DATA = ta.ha(analysis1MIN['Open'], analysis1MIN['High'], analysis1MIN['Low'], analysis1MIN['Close'])

                # MACD_1MIN, MACDHIST_1MIN, MACDSIG_1MIN = round(ta.macd(analysis1MIN['Close'],12, 26, 9).iloc[-1],5) #round(analysis1MIN.indicators["MACD.macd"],5)
                # #MACD_5MIN = round(pta.macd(analysis5MIN['Close'],12, 26, 9).iloc[-1],5) #round(analysis1MIN.indicators["MACD.macd"],5) 
                
                # CCI20_1MIN =  round(ta.cci(analysis1MIN['High'], analysis1MIN['Low'], analysis1MIN['Close'], length=20).iloc[-1],5)
                # CCI14_1MIN =  round(analysis1MIN.ta.cci(length=14).iloc[-1],5)
                
                # RSI1_15MIN = round(ta.rsi(analysis15MIN['Close'], 1).iloc[-1],5) #round(analysis15MIN.indicators['RSI[1]'],5)
                # RSI2_1MIN = round(ta.rsi(analysis1MIN['Close'], 2).iloc[-1],5) #round(ta.rsi(analysis1MIN['Close'], 2).iloc[-1],5)
                # RSI_5MIN = round(ta.rsi(analysis5MIN['Close'], 1).iloc[-1],5) #round(analysis5MIN.indicators['RSI'],5)
                # RSI5_1MIN = round(ta.rsi(analysis1MIN['Close'], 5).iloc[-1],5)
                # RSI6_1MIN = round(ta.rsi(analysis1MIN['Close'], 6).iloc[-1],5)
                # RSI9_1MIN = round(ta.rsi(analysis1MIN['Close'], 9).iloc[-1],5)
                # RSI10_1MIN = round(ta.rsi(analysis1MIN['Close'], 10).iloc[-1],5)
                # RSI12_1MIN = round(ta.rsi(analysis1MIN['Close'], 12).iloc[-1],5)
                # RSI14_1MIN_DATA = ta.rsi(analysis1MIN['Close'], 14)
                # RSI14_1MIN = round(RSI14_1MIN_DATA.iloc[-1],5)
                # RSI14_1MIN = round(ta.rsi(analysis1MIN['Close'], 14).iloc[-1],5) #round(analysis1MIN.indicators['RSI'],5)
                # RSI14_5MIN = round(ta.rsi(analysis5MIN['Close'], 14).iloc[-1],5) #round(analysis5MIN.indicators['RSI'],5)
                # RSI15_1MIN = round(ta.rsi(analysis1MIN['Close'], 15).iloc[-1],5) #round(ta.rsi(analysis1MIN['Close'], 15).iloc[-1],5)
                  
                
                # STOCH14K_1M_DATA = ta.stoch(analysis1MIN["High"], analysis1MIN["Low"], analysis1MIN["Close"], 14, 3, 3)
                # STOCH14K_1M = STOCH14K_1M_DATA['STOCHk_14_3_3'].iloc[-1]
                # STOCH14D_1M = STOCH14K_1M_DATA['STOCHd_14_3_3'].iloc[-1]
                # STOCH1K_1M_DATA = ta.stoch(analysis1MIN["High"], analysis1MIN["Low"], analysis1MIN["Close"], 1, 3, 3)
                # STOCH1K_1M = STOCH1K_1M_DATA['STOCHk_1_3_3'].iloc[-1]
                # STOCH1D_1M = STOCH1K_1M_DATA['STOCHd_1_3_3'].iloc[-1]
                # STOCH10K_1M_DATA = ta.stoch(analysis1MIN["High"], analysis1MIN["Low"], analysis1MIN["Close"], 10, 4, 4)
                # STOCH10K_1M = STOCH10K_1M_DATA['STOCHk_10_4_4'].iloc[-1]
                # STOCH10D_1M = STOCH10K_1M_DATA['STOCHd_10_4_4'].iloc[-1]
                # STOCH_DIFF_1MIN = round(STOCH_K_1MIN - STOCH_D_1MIN,5)
                
                # SMA3_1MIN = round(ta.sma(analysis1MIN['Close'],length=3).iloc[-1],5) 
                # SMA5_1MIN = round(ta.sma(analysis1MIN['Close'],length=5).iloc[-1],5) #round(analysis1MIN.indicators['SMA5'],5)                
                # SMA7_1MIN = round(ta.sma(analysis1MIN['Close'],length=7).iloc[-1],5)
                # SMA9_1MIN = round(ta.sma(analysis1MIN['Close'],length=9).iloc[-1],5)
                # SMA25_1MIN = round(ta.sma(analysis1MIN['Close'],length=25).iloc[-1],5)
                # SMA29_1MIN = round(ta.sma(analysis1MIN['Close'],length=29).iloc[-1],5)
                # SMA26_1MIN = round(ta.sma(analysis1MIN['Close'],length=26).iloc[-1],5)
                # SMA55_1MIN = round(ta.sma(analysis1MIN['Close'],length=55).iloc[-1],5)
                # SMA10_1MIN = round(ta.sma(analysis1MIN['Close'],length=10).iloc[-1],5) #round(analysis1MIN.indicators['SMA10'],5)            
                # SMA20_1MIN = round(ta.sma(analysis1MIN['Close'],length=20).iloc[-1],5)   
                # SMA100_1MIN = round(ta.sma(analysis1MIN['Close'],length=100).iloc[-1],5) #round(analysis1MIN.indicators['SMA100'],5)
                # SMA200_1MIN = round(ta.sma(analysis1MIN['Close'],length=200).iloc[-1],5) #round(analysis1MIN.indicators['SMA200'],5)
                # SMA5_5MIN = round(ta.sma(analysis5MIN['Close'],length=5).iloc[-1],5) #round(analysis5MIN.indicators['SMA5'],5)
                # SMA10_5MIN = round(ta.sma(analysis5MIN['Close'],length=10).iloc[-1],5) #round(analysis5MIN.indicators['SMA10'],5)                                                   
                # SMA20_5MIN = round(ta.sma(analysis5MIN['Close'],length=20).iloc[-1],5) #round(analysis5MIN.indicators['SMA20'],5)            
                # #SMA100_5MIN = round(ta.sma(analysis5MIN['Close'],length=50).iloc[-1],5) + round(ta.sma(analysis5MIN['Close'],length=50).iloc[-1],5) #round(analysis5MIN.indicators['SMA100'],5)
                # SMA200_5MIN = round(ta.sma(analysis5MIN['Close'],length=50).iloc[-1],5) + round(ta.sma(analysis5MIN['Close'],length=50).iloc[-1],5) + round(ta.sma(analysis5MIN['Close'],length=50).iloc[-1],5) + round(ta.sma(analysis5MIN['Close'],length=50).iloc[-1],5) #round(analysis5MIN.indicators['SMA200'],5)

                if buy:
                    bought_at, timeHold, coins_bought = load_json(pair)            
                    if coins_bought < TRADE_SLOTS and bought_at == 0:
                        # buySignal0 = RSI14_5MIN <= 40 and STOCH_K_5MIN <= 20 and STOCH_D_5MIN <= 20
                        # buySignal1 = (EMA2_1MIN > EMA3_1MIN) and (RSI2_1MIN < 45) and (STOCH_K_5MIN > STOCH_D_5MIN) and (STOCH_K_5MIN < 70 and STOCH_D_5MIN < 70)
                        # buySignal2 = RSI10_1MIN < 50 and RSI5_1MIN < 55 and RSI15_1MIN < 55 # 101/118 -2.7626
                        # buySignal3 = cross(EMA9_1MIN, EMA21_1MIN) and (CLOSE > HMA90_1MIN) #ni sirve
                        # buySignal4 = (SMA10_1MIN > SMA20_1MIN) and (SMA20_1MIN > SMA200_1MIN) and (MACD_1MIN <= 30) #34/51 -1.4994
                        # buySignal5 = (SMA5_1MIN > SMA10_1MIN > SMA20_1MIN) and (RSI14_5MIN >= 12 and RSI14_5MIN <= 55)
                        # buySignal6 = (RSI10_1MIN <= RSI14_1MIN) #110/116 -1.2060
                        # buySignal7 = (MACD_1MIN < 0) and (RSI14_1MIN < 50) #90/92 0.5693 < 50 #37/38 -1.2028 #67/68 -1.0721 < 40 #86/96 -0.3119 < 55
                        # buySignal8 = RSI2_1MIN < 30 and RSI14_1MIN < 30 #36/39 -1.3599
                        # buySignal9 = (STOCH_DIFF_1MIN >= 5) and (STOCH_K_1MIN >= 30 and STOCH_K_1MIN <= 60) and (STOCH_D_1MIN >= 30 and STOCH_D_1MIN <= 60) and (RSI10_1MIN >= 40)
                        # buySignal10 = RSI14_5MIN <= 40 and STOCH_K_5MIN <= 20 and STOCH_D_5MIN <= 20
                        # buySignal11 = CLOSE > SMA200_1MIN and CLOSE < SMA5_1MIN and RSI2_1MIN < 10 #37/32 1.4676 < 10 #28/29 0.1070 < 7 #31/30 0.2971 < 8 #34/31 1.0645 < 9 # 30/31 2.1526 tp.15 sl.10 #30/31 2.2948 intcomp
                        # buySignal12 = (RSI2_1MIN < 30) and (STOCH1K_1M > STOCH1D_1M) and (STOCH1K_1M < 50 and STOCH1D_1M < 50) #54/71 0.2953 tp.15 sl.10
                        # buySignal13 = (CCI20_1MIN != -200) and (CCI20_1MIN < -200) and (-200 > CCI20_1MIN) #ni sirve
                        # buySignal14 = float(EMA50_1MIN) >= float(EMA100_1MIN) #ni sirve
                        # buySignal15 = float(SMA9_1MIN) >= float(SMA29_1MIN) #53/82 0.4046 tp.15 sl.10
                        # buySignal17 = CLOSE < B2_1MIN
                        # buySignal18 = CLOSE < BM_1MIN
                        # buySignal19 = CLOSE < BM_1MIN  and RSI14_1MIN > 40
                        # buySignal20 = ((SMA3_1MIN > BM1_1MIN) and (RSI14_1MIN > 50) and (MACD_1MIN > 6)) #and CLOSE < B11_1MIN)
                        # buySignal21 = ((CLOSE > B2_1MIN) and (RSI6_1MIN > 50))
                        # buySignal22 = (CLOSE < B2_1MIN and RSI9_1MIN < 30)
                        # buySignal23 = (CLOSE > B2_1MIN and CLOSE < BM_1MIN and RSI9_1MIN < 30)
                        # buySignal24 = CLOSE > ICHIMOKU_SENKOUSPANA_1M and CLOSE > ICHIMOKU_SENKOUSPANB_1M 
                        # buySignal25 = RSI9_1MIN < 30 and CLOSE < SUPERTRENDDOWN_1M 
                        # buySignal26 = crossover(RSI14_1MIN, ta.sma(RSI14_1MIN_DATA, 14).iloc[-1]) and crossover(MACD_1MIN, MACDSIG_1MIN) and crossover(STOCH14K_1M, ta.sma(STOCH14K_1M_DATA['STOCHk_14_3_3'], 14).iloc[-1]) #114/119 -0.5414 #95/94 -0.6949
                        # buySignal27 = STOCH10K_1M < 50 and RSI5_1MIN >= 20
                        # buySignal28 = CLOSE > SMA5_1MIN and RSI5_1MIN < 50
                        buySignal29 = random.choice([True, False])
                        all_variables = dir()
                        for name in all_variables:
                            if name.startswith("buySignal"):
                                myvalue = eval(name)
                                dataBuy = {name:myvalue}
                                if myvalue:
                                    all_variables = ""
                                    signal_coins1.append({ 'time': position2, 'symbol': pair, 'price': CLOSE})
                                    if USE_SIGNALLING_MODULES:
                                        with open(SIGNAL_FILE_BUY,'a+') as f:
                                            f.write(pair + '\n') 
                                        break
                
                if SELL_ON_SIGNAL_ONLY:
                    bought_at, timeHold, coins_bought = load_json(pair)
                    if float(bought_at) != 0 and float(coins_bought) != 0 and float(CLOSE) != 0:
                        SL = float(bought_at) - ((float(bought_at) * float(STOP_LOSS)) / 100)
                        TP = float(bought_at) + ((float(bought_at) * float(TAKE_PROFIT)) / 100)
                        # sellSignalTP = (float(CLOSE) > float(TP) and float(TP) != 0) and float(CLOSE) > float(bought_at)
                        # sellSignalSL = (float(CLOSE) < float(SL) and float(SL) != 0)
                        # sellSignal0 = (float(RSI14_5MIN) >= 70 and STOCH_K_5MIN >= 80 and STOCH_D_5MIN >= 80 and float(CLOSE) > float(bought_at))
                        # sellSignal1 = (float(RSI10_1MIN) > 50 and RSI5_1MIN > 55 and RSI15_1MIN > 55 and float(CLOSE) > float(bought_at))
                        # sellSignal2 = (float(RSI2_1MIN) > 80 and float(CLOSE) > float(bought_at))
                        # sellSignal3 = ((float(CLOSE) < HMA90_1MIN and float(CLOSE) > float(bought_at)))  
                        # sellSignal4 = (float(RSI10_1MIN) >= 90 and float(CLOSE) > float(bought_at))
                        # sellSignal5 = (crossunder(RSI2_1MIN, 90) and float(CLOSE) > float(bought_at))
                        # sellSignal6 = (crossunder(STOCH_D_1MIN, 80) and float(CLOSE) > float(bought_at))
                        # sellSignal7 = (float(RSI2_1MIN) > 75 and float(CLOSE) > float(bought_at))
                        # sellSignal8 = (float(CCI20_1MIN) > 100 and float(CLOSE) > float(bought_at))
                        # sellSignal9 = (float(EMA50_1MIN) <= float(EMA100_1MIN) and float(CLOSE) > float(bought_at))
                        # sellSignal10 = (float(SMA9_1MIN) <= float(SMA29_1MIN) and float(CLOSE) > float(bought_at))
                        # sellSignal11 = ((baja == False and (precio > media) and (sma_20/sma_20_anterior > 1.002) and (precio/precio_anterior > 1.002)) or (baja == True and precio/ultimo_precio > 1.01) and float(CLOSE) > float(bought_at))
                        # sellSignal12 = (CLOSE > B1_1MIN and float(CLOSE) > float(bought_at))
                        # sellSignal13 = (CLOSE > BM_1MIN and float(CLOSE) > float(bought_at))
                        # sellSignal14 = (CLOSE > B1_1MIN and float(CLOSE) > float(bought_at)) # and RSI14_1MIN >= 60)
                        # sellSignal15 = (SMA3_1MIN < BM1_1MIN and RSI14_1MIN < 50 and MACD_1MIN < 6 and CLOSE > bought_at) #and CLOSE < B11_1MIN)
                        # sellSignal16 = ((CLOSE > B1_1MIN) and (RSI9_1MIN > 70) and (CLOSE > bought_at))
                        # sellSignal17 = ((CLOSE < B1_1MIN) and (RSI14_1MIN > 50) and CLOSE > bought_at)
                        # sellSignal18 = (CLOSE > BM_1MIN and RSI9_1MIN > 70 and CLOSE > bought_at)
                        # sellSignal19 = CLOSE < ICHIMOKU_SENKOUSPANA_1M and CLOSE < ICHIMOKU_SENKOUSPANB_1M and CLOSE > bought_at
                        # sellSignal20 = crossover(RSI14_1MIN, ta.sma(RSI14_1MIN_DATA, 14).iloc[-1]) and crossover(MACD_1MIN, MACDSIG_1MIN) and not crossover(STOCH14K_1M, ta.sma(STOCH14K_1M_DATA['STOCHk_14_3_3'], 14).iloc[-1])
                        # sellSignal21 = (MACD_1MIN > 0) and (RSI14_1MIN > 50) and CLOSE > bought_at
                        # sellSignal22 = STOCH10K_1M > 5 and RSI5_1MIN > 66 #and CLOSE > bought_at
                        # sellSignal22 = CLOSE > SMA5_1MIN and RSI5_1MIN > 50 and CLOSE > bought_at #53/39 2.2178 # 41/10 3.6789 buySignal28 buySignal11 #176/93 1.1840 sl.10 buySignal11 buySignal28 #84/42 1.4573 buySignal11 sl.10
                        # sellSignal23 = CLOSE > SMA200_1MIN and CLOSE > SMA5_1MIN and RSI2_1MIN > 90
                        sellSignal24 = random.choice([True, False])
                        all_variables = dir()
                        for name in all_variables:
                            if name.startswith("sellSignal"):
                                myvalue = eval(name)
                                dataSell = {name:myvalue}
                                if myvalue and float(bought_at) != 0:
                                    signal_coins2.append({ 'time': position2, 'symbol': pair, 'price': CLOSE})
                                    with open(SIGNAL_FILE_SELL,'a+') as f:
                                        f.write(pair + '\n')
                                    break 
    except Exception as e:
        write_log(f'{txcolors.DEFAULT}{SIGNAL_NAME}: {txcolors.SELL_LOSS} - Exception: {e}{txcolors.DEFAULT}', SIGNAL_NAME + ".log", True, False)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        write_log("Error on line " + str(exc_tb.tb_lineno), SIGNAL_NAME + ".log", True, False)
        pass
    return signal_coins1, signal_coins2

def do_work():
    try:
        signalcoins1 = []
        signalcoins2 = []
        pairs = {}
        dataBuy = {}
        dataSell = {}
        for line in open(TICKERS):
            pairs=[line.strip() + PAIR_WITH for line in open(TICKERS)] 
        while True:
                #if not threading.main_thread().is_alive(): exit()
                print(f'{txcolors.SELL_PROFIT}{SIGNAL_NAME}: {txcolors.DEFAULT}Analyzing {len(pairs)} coins...{txcolors.DEFAULT}') 
                if BACKTESTING_MODE:
                    while os.path.exists('ok.ok'):
                        time.sleep(1/1000) #do_work
                    signalcoins1, signalcoins2 = analyze(pd.DataFrame([]), pairs, True)
                    with open('ok.ok','w') as f:
                        f.write("1")
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
        write_log(f'{txcolors.DEFAULT}{SIGNAL_NAME}: {txcolors.SELL_LOSS} - Exception: do_work(): {e}{txcolors.DEFAULT}', SIGNAL_NAME + ".log", True, False)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        write_log("Error on line " + str(exc_tb.tb_lineno), SIGNAL_NAME + ".log", True, False)
        pass
        #except KeyboardInterrupt as ki:
            #pass