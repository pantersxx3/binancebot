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
import random
import telnetlib
  
def buy(Data, CLOSE, pair):
    try:
        # HOST = "localhost"
        # PORT = 10000
        # tn = telnetlib.Telnet(HOST, PORT)
        
        buySignal = False
        #zigzag_data = []
        #ZIGZAG_RESULT = False
        #ZIGZAG = MF.zigzag(Data, 2)
        #zigzag_data.append(ZIGZAG)
        #for i in range(len(zigzag_data)):
            # Si el valor actual de Zigzag es mayor que el anterior y la pendiente es positiva
            #if zigzag_data.loc[i] > zigzag_data.loc[i - 1] and zigzag_data.loc[i] > 0:
                #ZIGZAG_RESULT = True
                #break
                
        #BA, BM, BB = MF.BollingerBands(Data, 20, 2)
        #SMA1 = MF.Sma(Data, 9)
        #SMA2 = MF.Sma(Data, 200)
        #SMA2 = MF.Sma(Data, 50)
        #SMA3 = MF.Sma(Data, 25)
        price = MF.read_sell_value(pair)
        if price > 0:         
            buySignal = True if CLOSE <= (price - ((3 * price)/100)) else False
        else:
            buySignal = True
        # buySignal = CLOSE < SMA1 and CLOSE > SMA2
        #buySignal = random.choice([True, False])
        #CLOSE > SMA1 and ZIGZAG_RESULT # #and CLOSE > SMA3 and CLOSE > SMA2
        #print("buySignal=", buySignal, "CLOSE=", CLOSE, "SMA1=", SMA1, "SMA2=", SMA2)
        #random.choice([True, False]) #
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
        #zigzag_data = []
        #ZIGZAG_RESULT = False
        #ZIGZAG = MF.zigzag(Data, 2)
        #zigzag_data.append(ZIGZAG)
        #for i in range(len(zigzag_data)):
            #if zigzag_data.loc[i] < zigzag_data.loc[i - 1] and zigzag_data.loc[i] < 0:
                #ZIGZAG_RESULT = True
                #break
        #BA, BM, BB = MF.BollingerBands(Data, 20, 2)
        #SMA1 = MF.Sma(Data, 9)
        B = MF.Bought_at(pair)
        # CV = MF.read_volume_value(pair, "Buy")
        # CB = MF.read_commission_value(pair, "Buy")
        # CS = MF.read_commission_value(pair, "Sell")
        
        # S = CLOSE*CV
        # NC = S * 0.001
        # if CS > 0: 
            # CT = round(CB + CS + NC, 8)
        # else:
            # CT = round(CB + NC, 8)
        # GS = S + CT
        # GB = B * CV        
        # print("CLOSE=", CLOSE, "Objetivo=", GS, "GananciaCompra=", GB, "volumen=", CV, "ComisionCompra=", CB, "ComisionVenta=", CS, "NuevaComision=", NC, "ComisionTotal=", CT, "Venta=", S)
        #print( CLOSE, B + ((3 * B)/100))
        sellSignal1 = CLOSE >= B + ((3 * B)/100) #and CLOSE >  SMA1
        #sellSignal1 = GS > GB
        #sellSignal1 = CLOSE > B and CLOSE > BA
        #sellSignal1 = CLOSE > B and CLOSE > SMA1 
        #sellSignal1 = random.choice([True, False])
        #CLOSE > B and random.choice([True, False]) 
        #ZIGZAG_RESULT #MF.Tp(pair, CLOSE) or MF.Sl(pair, CLOSE)

        #random.choice([True, False]) #
        #cmmd = f'sellSignal1: {sellSignal1} CLOSE: {CLOSE} SMA9: {SMA1} B: {B}'
        #tn.write(cmmd.encode('utf-8'))
        
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print('Sell Error on line ' + str(exc_tb.tb_lineno))
        pass
    return sellSignal1
