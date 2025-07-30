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
  
def buy(Data, CLOSE, pair):
	try:
		# HOST = "localhost"
		# PORT = 10000
		# tn = telnetlib.Telnet(HOST, PORT)
		
		buySignal = False
		####Strategy Fibollinger(Fibonacci-Bollinger)####
		BA, BM, BB = MF.Bollinger_Bands(Data, 20, 2)
		#MF.Fibonacci(Data) == 1 and 		
		if CLOSE <= BM:
			buySignal = True
		####Strategy Bollinger and SMA200 METOD 1####
		#BA, BM, BB = MF.Bollinger_Bands(Data, 20, 2)
		#EMA200 = MF.Ema(Data, 200)
		#EMA9 = MF.Ema(Data, 9)
		#EMA21 = MF.Ema(Data, 21)
		#RSI14 = MF.Rsi(Data, 14)
		#buySignal = MF.spread_strategy(0.01, 0.07, Data) == 1 and  CLOSE > EMA200
		#print(MF.analizar_mercado_inteligente_gpu(Data))
		#r = MF.analizar_mercado_inteligente_gpu(Data, False)
		#if r['tendencia']["probabilidad_subida"] > 0.7 and r["caida"]["probabilidad_caida"] < 0.7:
			#buySignal = True
		#historial = train(Data, episodios=25, capital_inicial=100)
		#plot_performance(historial)
		#print(Data)
		#bot = TradingBot(model_path="agenteIA", window_size=25)
		#Data.columns = ["time","Open","High","Low","Close","Volume"]
		#bot.train(Data)
		
		# train_size = int(len(Data) * 0.9)
		# train_data = Data[:train_size]
		# test_data = Data[train_size:]
		
		# history = bot.monitorear_aprendizaje(
			# train_data, 
			# test_data, 
			# epochs=30, 
			# batch_size=32, 
			# evaluation_interval=5
		# )
	
		# resultados = bot.evaluar_modelo(test_data, plot=True)
		# print(f"Precisión del modelo: {resultados['accuracy']:.2%}")
		# print(f"Retorno de la estrategia: {resultados['retorno_total']:.2%}")
		# print(f"Retorno Buy & Hold: {resultados['retorno_buy_hold']:.2%}")
		# print(f"Sharpe Ratio: {resultados['sharpe_ratio']:.2f}")

		# bot.save()	
			# Tp = CLOSE + (CLOSE * 0.5) / 100
			# PREDICTIONS = MF.predict_sma(Data, 20, 60)
			# print(PREDICTIONS)				
			# for prediction in PREDICTIONS:
				# if prediction > Tp:
					# # for position in PREDICTION_POSITIONS:
						# # if position == "0":
							# # c = c + 1
					# # if not c == 10 - 1:
					# return True
		#buySignal = CLOSE < BB and CLOSE > SMA200
		#buySignal = SMA_PREDICTED[-1] > CLOSE
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
		print(e)
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
		####Strategy Fibollinger(Fibonacci-Bollinger)####
		BA, BM, BB = MF.Bollinger_Bands(Data, 20, 2)
		#MF.Fibonacci(Data) == -1 and
		if CLOSE >= BM and CLOSE > B:
			sellSignal1 = True			
		#r = MF.analizar_mercado_inteligente_gpu(Data, False)
		#if r["caida"]["probabilidad_caida"] > 0.7:
			#sellSignal1 = True
		#B = MF.Bought_at(pair)
		#EMA200 = MF.Ema(Data, 200)
		#EMA9 = MF.Ema(Data, 9)
		#EMA21 = MF.Ema(Data, 21)
		#RSI14 = MF.Rsi(Data, 14)
		#sellSignal1 = MF.spread_strategy(0.01, 0.07, Data) == 2 and  CLOSE > EMA200 and CLOSE > B or CLOSE >= round(B + ((0.1 * B)/100),5)
		
		####Strategy Take Profit 2% and Strategy Elaskar####
		#TP=0.2% TOTAL=56 WIN=22.793 USDT
		#TP=0.3% TOTAL=38 WIN=22.698 USDT
		#TP=0.4% TOTAL=20 WIN=21.872 USDT
		#TP=0.5% TOTAL=17 WIN=21.866 USDT
		#sellSignal1 = CLOSE >= round(B + ((0.1 * B)/100),5) #and CLOSE > B
		####Strategy Take Profit 3%####

		####Strategy Bollinger Metod 1####
		#BA, BM, BB = MF.Bollinger_Bands(Data, 20, 2)
		#sellSignal1 = CLOSE > B and CLOSE > BM
		####Strategy Bollinger Metod 1####
		
		####Strategy Bollinger Metod 2####
		#SMA9 = MF.Sma(Data, 9)
		#sellSignal1 = CLOSE > B and CLOSE > SMA9 
		####Strategy Bollinger Metod 1####
		
		####Strategy Bollinger Metod and SL Dynamic####
		#BA, BM, BB = MF.Bollinger_Bands(Data, 30, 2)
		#STOP_LOSS  = MF.Dynamic_StopLoss(pair, Data, CLOSE, 70, 10, BB)
		#sellSignal1 = CLOSE > B and CLOSE > BA or STOP_LOSS
		####Strategy Bollinger Metod 1####		
		
		####Strategy Bollinger Metod and SL Dynamic metod 2####
		#BA, BM, BB = MF.Bollinger_Bands(Data, 20, 2)
		#STOP_LOSS  = MF.Dynamic_StopLoss(pair, Data, CLOSE, 100, 60, BM)
		#sellSignal1 = (CLOSE > B and CLOSE > BA) #or CLOSE < SMA_PREDICTED[-1]
		#sellSignal1 = CLOSE > B and CLOSE > BA #or STOP_LOSS
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
