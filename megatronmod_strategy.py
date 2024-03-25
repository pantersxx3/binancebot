# Megatronmod Strategy - All in One
# Created by: Horacio Oscar Fanelli - Pantersxx3 and NokerPlay
# This mod can be used only with:
# https://github.com/pantersxx3/Binance-Bot
#
# No future support offered, use this script at own risk - test before using real funds
# If you lose money using this MOD (and you will at some point) you've only got yourself to blame!
#CLOSE_1MIN > SMA200_1MIN and CLOSE_1MIN < SMA5_1MIN and RSI2_1MIN

import megatronmod_functions as MF
import sys
import os
#import random
  
def buy(Data, CLOSE, pair):
    try:
        BA, BM, BB = MF.BollingerBands(Data, 2, 2)
        SMA1 = MF.Sma(Data, 200)
        #SMA2 = MF.Sma(Data, 50)
        #SMA3 = MF.Sma(Data, 25)      
      
        buySignal = CLOSE < BM and CLOSE > SMA1 #and CLOSE > SMA3 and CLOSE > SMA2
        #random.choice([True, False]) #

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print('Buy Error on line ' + str(exc_tb.tb_lineno))
        pass
    return buySignal
    
    
def sell(Data, CLOSE, pair):
    try:
        sellSignal1 = True
        BA, BM, BB = MF.BollingerBands(Data, 2, 2)
        B = MF.Bought_at(pair)
        
        sellSignal1 = MF.Tp(pair, CLOSE) 
        #random.choice([True, False]) #CLOSE > B and CLOSE > BM

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print('Sell Error on line ' + str(exc_tb.tb_lineno))
        pass
    return sellSignal1
