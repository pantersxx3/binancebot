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
from datetime import datetime
import sys
import os
import random
global estadisticas
estadisticas = {}
estadisticas["tendencia_alcista_confirmada"] = 0
estadisticas['consolidacion'] = 0
estadisticas['volatil'] = 0
estadisticas['rango_lateral'] = 0
  
def buy(Data, CLOSE, pair):
	try:
		# HOST = "localhost"
		# PORT = 10000
		# tn = telnetlib.Telnet(HOST, PORT)
		
		buySignal = False
		buySignal = MF.Ema(Data, 9) < MF.Ema(Data, 21) and MF.Rsi(Data, 14) < 30 and CLOSE < MF.Ema(Data, 21) or MF.Rsi(Data, 14) < 30 and MF.check_volume(Data)
		# if tipo == 'tendencia_bajista_confirmada':
		# buySignal = MF.Ema(Data, 9) < MF.Ema(Data, 21) and MF.Rsi(Data, 14) < 30 and CLOSE < MF.Ema(Data, 21)
		# elif tipo == 'consolidacion':
			# BA, BM, BB = MF.Bollinger_Bands(Data, 20, 2)
			# buySignal = CLOSE < BB
		# if tipo == 'volatil':
			# #EMA200 = MF.Ema(Data, 200)
			# High_break = Data['High'].rolling(20).max().iloc[-1]
			# Low_break = Data['Low'].rolling(20).min().iloc[-1]
			# buySignal = CLOSE < Low_break and confirmar_volumen(Data)
			#MF.detectar_tipo_de_mercado(Data) == 'rango_lateral' and
		# buySignal =  MF.Rsi(Data, 14) < 30 and MF.check_volume(Data)
			#--------------------------------------------
			#BA, BM, BB = MF.Bollinger_Bands(Data, 20, 2)
			#if CLOSE <= BB and MF.confirmar_volumen(Data):
				#buySignal = True
			#--------------------------------------------
			#if MF.spread_strategy(0.01, 0.07, Data) == 1 and CLOSE <= MF.B(Data) * 0.999:
				#buySignal = True
			#--------------------------------------------
			# buySignal = MF.spread_strategy(0.01, 0.07, Data) == 1 and CLOSE > MF.Ema(Data, 200) and (CLOSE < MF.B(Data) or CLOSE <= round(MF.B(Data) - ((0.1 * MF.B(Data))/100), 5))
		
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		print(e)
		print('Buy Error on line ' + str(exc_tb.tb_lineno))
		pass
	return buySignal
	
	
def sell(Data, CLOSE, pair):
	try:
		# HOST = "localhost"
		# PORT = 10000
		# tn = telnetlib.Telnet(HOST, PORT)
		sellSignal = False
		sellSignal = MF.Ema(Data, 9) > MF.Ema(Data, 21) and MF.Rsi(Data, 14) > 70 and CLOSE > MF.Ema(Data, 21) or MF.Rsi(Data, 14) > 70 and MF.check_volume(Data)
		#if tipo == 'tendencia_alcista_confirmada':
		# sellSignal = MF.Ema(Data, 9) > MF.Ema(Data, 21) and MF.Rsi(Data, 14) > 70 and CLOSE > MF.Ema(Data, 21)
		# elif tipo == 'consolidacion':
			# BA, BM, BB = MF.Bollinger_Bands(Data, 20, 2)
			# sellSignal = CLOSE > BA
		# elif tipo == 'volatil':
			# estadisticas['volatil'] = estadisticas['volatil'] + 1
			# EMA200 = MF.Ema(Data, 200)
			# High_break = Data['High'].rolling(20).max().iloc[-1]
			# Low_break = Data['Low'].rolling(20).min().iloc[-1]
			# sellSignal = CLOSE > High_break and CLOSE > EMA200 and MF.confirmar_volumen(Data)
			#MF.detectar_tipo_de_mercado(Data) == 'rango_lateral' and 
		# sellSignal = MF.Rsi(Data, 14) > 70 and MF.check_volume(Data)
			#adx = MF.Adx(Data)[0]
			#if adx < 20 and (CLOSE > BA or CLOSE < BB):
				#pass
			#EMA200 = MF.Ema(Data, 200)
			#spread = MF.spread_strategy(0.01, 0.07, Data)
			#B = MF.B(Data)
			#if spread == 2 and CLOSE >= B * 1.001:
				#sellSignal = True
			#------------------
			# BA, BM, BB = MF.Bollinger_Bands(Data, 20, 2)
			# if CLOSE >= BA and MF.confirmar_volumen(Data):
				# sellSignal = True
			#------------------
			# estadisticas['rango_lateral'] = estadisticas['rango_lateral'] + 1
			# EMA200 = MF.Ema(Data, 200)
			# spread = MF.spread_strategy(0.01, 0.07, Data)
			# CLOSE = Data['Close'].iloc[-1]
			# B = MF.B(Data)
			# sellSignal = spread == 2 and CLOSE > EMA200 and (CLOSE > B or CLOSE >= round(B + ((0.1 * B)/100), 5))
		#print(estadisticas)
	except Exception as e:
		print(e)
		exc_type, exc_obj, exc_tb = sys.exc_info()
		print('Sell Error on line ' + str(exc_tb.tb_lineno))
		pass
	return sellSignal
