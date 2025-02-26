# Megatronmod Strategy - All in One
# Created by: Horacio Oscar Fanelli - Pantersxx3 and NokerPlay
# This mod can be used only with:
# https://github.com/pantersxx3/Binance-Bot
#
# No future support offered, use this script at own risk - test before using real funds
# If you lose money using this MOD (and you will at some point) you've only got yourself to blame!

#Inficators avaibles:
#MF.Crossover, MF.Crossunder, MF.Cross, MF.Ichimoku, MF.Bollinger MF.Bands, MF.Supertrend, MF.Momentum, MF.Hikinashi
#MF.Macd, MF.Cci, MF.SL, MF.TP, MF.Bought_at, MF.Zigzag, MF.Ema, MF.Sma, MF.Stochastic, MF.Rsi, MF.Wma, MF.Hma

import megatronmod_functions as MF
import sys
import os
import random
import telnetlib
  
def buy(Data, CLOSE, pair):
    try:
        # HOST = "localhost"
        # PORT = 10000
        # tn = telnetlib.Telnet(HOST, PORT)
        
        buySignal = False                
        
        ####Strategy Bollinger and SMA200 METOD 1####
        BA, BM, BB = MF.Bollinger_Bands(Data, 30, 2)
        SMA200 = MF.Sma(Data, 200)
        buySignal = CLOSE < BB and CLOSE > SMA200
        ####Strategy Bollinger and SMA200 METOD 1####
        
        ####Strategy Elaskar####
        #price = MF.read_sell_value(pair)
        #if price > 0:         
        #    buySignal = True if CLOSE <= (price - ((1 * price)/100)) else False
        #else:
        #    buySignal = True
        ####Strategy Elaskar####
        
        ####Strategy SMA9 and SMA200####
        #SMA9 = MF.Sma(Data, 9)
        #SMA200 = MF.Sma(Data, 200)
        #buySignal = CLOSE < SMA9 and CLOSE > SMA200
        ####Strategy SM9####
        
        ####Strategy Random####
        #buySignal = random.choice([True, False])
        ####Strategy Random####        


        #cmmd = f'buySignal: {buySignal} CLOSE: {CLOSE} SMA9: {SMA1} SMA200: {SMA2}'
        #tn.write(cmmd.encode('utf-8'))
        
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print('Buy Error on line ' + str(exc_tb.tb_lineno))
        pass
    return buySignal
    
    
def sell(Data, CLOSE, pair):
	try:
        # HOST = "localhost"
        # PORT = 10000
        # tn = telnetlib.Telnet(HOST, PORT)
		sellSignal1 = False        
		B = MF.Bought_at(pair)
        ####Strategy Take Profit 2% and Strategy Elaskar####
		#TP=0.2% TOTAL=56 WIN=22.793 USDT
		#TP=0.3% TOTAL=38 WIN=22.698 USDT
		#TP=0.4% TOTAL=20 WIN=21.872 USDT
		#TP=0.5% TOTAL=17 WIN=21.866 USDT
		#sellSignal1 = CLOSE >= round(B + ((0.25 * B)/100),5)
        ####Strategy Take Profit 3%####

        ####Strategy Bollinger Metod 1####
		#BA, BM, BB = MF.Bollinger_Bands(Data, 20, 2)
		#sellSignal1 = CLOSE > B and CLOSE > BM
        ####Strategy Bollinger Metod 1####
        
        ####Strategy Bollinger Metod 2####
        #SMA9 = MF.Sma(Data, 9)
        #sellSignal1 = CLOSE > B and CLOSE > SMA9 
        ####Strategy Bollinger Metod 1####
		
		####Strategy Bollinger Metod 3####
		BA, BM, BB = MF.Bollinger_Bands(Data, 30, 2)
		sellSignal1 = CLOSE > B and CLOSE > BA
        ####Strategy Bollinger Metod 1####		
        
		####STOPLOSS####
		#sellSignal1 =  MF.SL(pair, CLOSE)
		####STOPLOSS####
		
        ####Strategy Random Metod 1####
        #sellSignal1 = random.choice([True, False])
        ####Strategy Random Metod 1####
        
        ####Strategy Random Metod 2####
        #sellSignal1 = CLOSE > B and random.choice([True, False])
        ####Strategy Random Metod 2####


        #cmmd = f'sellSignal1: {sellSignal1} CLOSE: {CLOSE} SMA9: {SMA1} B: {B}'
        #tn.write(cmmd.encode('utf-8'))
        
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		print('Sell Error on line ' + str(exc_tb.tb_lineno))
		pass
	return sellSignal1
