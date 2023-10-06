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

def buy(Data, CLOSE, pair):
    try:
        BA, BM, BB = MF.BollingerBands(Data, 21, 2)
        #RSI = MF.Rsi(Data, 7)
        #EMA = MF.Ema(Data, 9)
        #STOCHK, STOCHD = MF.Stochastic(Data, 14, 3, 3)
        SMA1 = MF.Sma(Data, 200)
        #SMA2 = MF.Sma(Data, 50)
        #SMA3 = MF.Sma(Data, 25)      
      
        buySignal = CLOSE < BM and CLOSE > SMA1 #and CLOSE > SMA2 #and CLOSE > SMA3
        #print("CLOSE=", CLOSE, "BM=", BM, "SMA1=", SMA1, "SMA2=", SMA2, buySignal)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print('Buy Error on line ' + str(exc_tb.tb_lineno))
        pass
    return buySignal
    
    
def sell(Data, CLOSE, pair):
    try:
        BA, BM, BB = MF.BollingerBands(Data, 21, 2)
        #RSI = MF.Rsi(Data, 7)
        B = MF.Bought_at(pair)
        #EMA = MF.Ema(Data, 9)
        #STOCHK, STOCHD = MF.Stochastic(Data, 14, 3, 3)
        sellSignal =  CLOSE > B and CLOSE > BM #MF.Tp(True, pair, CLOSE, True) or MF.Sl(True, pair, CLOSE) and  #CLOSE > BM
        
                
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print('Sell Error on line ' + str(exc_tb.tb_lineno))
        pass
    return sellSignal