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
  
def buy(Data, CLOSE, pair):
	try:
		# HOST = "localhost"
		# PORT = 10000
		# tn = telnetlib.Telnet(HOST, PORT)
		
		buySignal = False
		# H, L = MF.Pivots_Hl(Data)
		# buySignal = MF.Ema(Data, 9) < MF.Ema(Data, 21) and MF.Rsi(Data, 14) < 30 and CLOSE < MF.Ema(Data, 21) and MF.Macd_Ind(Data, 12, 26, 9) < -1.05
		# buySignal = MF.Rsi(Data, 14) < 30 and MF.check_volume(Data)
		# buySignal = MF.Rsi(Data, 14) < 30 and MF.check_volume(Data) and MF.Ema(Data, 50) < MF.Ema(Data, 200)
		# buySignal = MF.Rsi(Data, 14) < 30 and MF.check_volume(Data) and MF.Macd_Ind(Data, 12, 26, 9) < -1.5 and MF.Ema(Data, 50) < MF.Ema(Data, 200)
		# buySignal = MF.Rsi(Data, 14) < 30 and MF.check_volume(Data)
		valor_rsi_sobrecompra, valor_rsi_sobreventa, valor_macd_buy, valor_macd_venta = MF.calcular_rangos_dinamicos_macd_rsi(Data, 14, 12, 26, 9, 70, 30, 30, 30)
		#print(valor_rsi_sobrecompra, valor_rsi_sobreventa, valor_macd_buy, valor_macd_venta)
		values = MF.guardar_rangos_dinamicos(pair, 15, valor_rsi_sobrecompra, valor_rsi_sobreventa, valor_macd_buy, valor_macd_venta)
		valor_rsi_sobrecompra = values["rsi_over"]
		#valor_rsi_sobreventa = values["rsi_under"]
		valor_macd_buy = values["macd_buy"]
		#valor_macd_venta = values["macd_sell"]
		buySignal = MF.Rsi(Data, 14) < valor_rsi_sobrecompra and MF.Check_Volume(Data) and MF.Macd_Ind(Data, 12, 26, 9) < valor_macd_buy and MF.Ema(Data, 50) < MF.Ema(Data, 200) and MF.Low_Volatility(Data, CLOSE)
		# buySignal = MF.Ema(Data, 9) < MF.Ema(Data, 21) and MF.Rsi(Data, 14) < 30 and CLOSE < MF.Ema(Data, 21)
		# buySignal = MF.spread_strategy(0.01, 0.07, Data) == 1 and CLOSE > MF.Ema(Data, 200) and (CLOSE < MF.B(Data) or CLOSE <= round(MF.B(Data) - ((0.1 * MF.B(Data))/100), 5))
		# buySignal = MF.Rsi(Data, 14) < 50 and L <= CLOSE and MF.Macd_Ind(Data, 12, 26, 9) < -0.95
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		print(e)
		print('Buy Error on line ' + str(exc_tb.tb_lineno))
		pass
	return buySignal
	
	
def sell(Data, CLOSE, pair):
	try:
		sellSignal = False
		B = MF.Bought_at(pair)
		# sellSignal = MF.Ema(Data, 9) > MF.Ema(Data, 21) and MF.Rsi(Data, 14) > 70 and CLOSE > MF.Ema(Data, 21)and MF.Macd_Ind(Data, 12, 26, 9) > 0.85
		# sellSignal = MF.Rsi(Data, 14) > 70 and MF.check_volume(Data) and MF.Ema(Data, 50) > MF.Ema(Data, 200)
		# sellSignal = bool(MF.Rsi(Data, 14) > 70 and MF.check_volume(Data) and MF.Macd_Ind(Data, 12, 26, 9) > 0.85 and MF.Ema(Data, 50) > MF.Ema(Data, 200)) or MF.Sl(pair, CLOSE, 4) 
		# sellSignal = MF.Rsi(Data, 14) > 70 and MF.check_volume(Data) or MF.Sl(pair, CLOSE, 4)
		# sellSignal = MF.Rsi(Data, 14) > 70 and MF.check_volume(Data) and MF.Macd_Ind(Data, 12, 26, 9) > 0.85 and MF.Ema(Data, 50) > MF.Ema(Data, 200) and MF.low_volatility(Data, CLOSE) or MF.Sl(pair, CLOSE, 4)
		valor_rsi_sobrecompra, valor_rsi_sobreventa, valor_macd_buy, valor_macd_venta = MF.calcular_rangos_dinamicos_macd_rsi(Data, 14, 12, 26, 9, 70, 30, 30, 30)
		#print(valor_rsi_sobrecompra, valor_rsi_sobreventa, valor_macd_buy, valor_macd_venta)
		values = MF.guardar_rangos_dinamicos(pair, 15, valor_rsi_sobrecompra, valor_rsi_sobreventa, valor_macd_buy, valor_macd_venta)
		#valor_rsi_sobrecompra = values["rsi_over"]
		valor_rsi_sobreventa = values["rsi_under"]
		#valor_macd_buy = values["macd_buy"]
		valor_macd_venta = values["macd_sell"]
		sellSignal = MF.Rsi(Data, 14) > valor_rsi_sobreventa and MF.Check_Volume(Data) and MF.Macd_Ind(Data, 12, 26, 9) > valor_macd_venta and MF.Ema(Data, 50) > MF.Ema(Data, 200) and MF.Low_Volatility(Data, CLOSE)
		# H, L = MF.Pivots_Hl(Data)
		# sellSignal = MF.Rsi(Data, 14) > 50 and H >= CLOSE and MF.Macd_Ind(Data, 12, 26, 9) > 1 or MF.Sl(pair, CLOSE, 1)
	except Exception as e:
		print(e)
		exc_type, exc_obj, exc_tb = sys.exc_info()
		print('Sell Error on line ' + str(exc_tb.tb_lineno))
		pass
	return sellSignal
