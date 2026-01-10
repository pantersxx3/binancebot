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

# import pandas as pd
# import numpy as np

# def optimizar_emas_bruta():
    # try:
        # resultados = []
        # df = pd.read_csv("BNBUSDT_1m_actual.csv")
        # df['time'] = pd.to_numeric(df['time'], errors='coerce')
        # df['time_dt'] = pd.to_datetime(df['time'], unit='ms')

        # targets = [
            # ("2025-12-24 12:17:00", "H"), ("2025-12-24 12:07:00", "L"),
            # ("2025-12-24 11:12:00", "H"), ("2025-12-24 10:59:00", "L"),
            # ("2025-12-24 10:41:00", "H"), ("2025-12-24 09:50:00", "H"),
            # ("2025-12-24 09:36:00", "L"), ("2025-12-24 09:17:00", "H"),
            # ("2025-12-24 08:59:00", "L"), ("2025-12-24 08:47:00", "H"),
            # ("2025-12-24 08:34:00", "L"), ("2025-12-24 07:50:00", "H"),
            # ("2025-12-24 07:29:00", "L"), ("2025-12-24 07:11:00", "H"),
            # ("2025-12-24 06:38:00", "L"), ("2025-12-24 06:24:00", "H"),
            # ("2025-12-24 06:15:00", "L"), ("2025-12-24 05:50:00", "H"),
            # ("2025-12-24 05:46:00", "L"), ("2025-12-24 05:25:00", "H")
        # ]
        # for f in range(2, 31): #for f in range(2, 16):
            # for s in range(f + 1, 81): #for s in range(f + 1, 41):
                # ema_f = df['Close'].ewm(span=f, adjust=False).mean()
                # ema_s = df['Close'].ewm(span=s, adjust=False).mean()
                # crossovers = (ema_f > ema_s) & (ema_f.shift(1) <= ema_s.shift(1))
                # crossunders = (ema_f < ema_s) & (ema_f.shift(1) >= ema_s.shift(1))
                # aciertos = 0
                # for fecha_str, tipo in targets:
                    # t_target = pd.to_datetime(fecha_str)
                    # mask = (df['time_dt'] >= t_target - pd.Timedelta(seconds=120)) & (df['time_dt'] <= t_target + pd.Timedelta(seconds=120))                    
                    # if tipo == "L" and crossovers[mask].any():
                        # aciertos += 1
                    # elif tipo == "H" and crossunders[mask].any():
                        # aciertos += 1
                
                # if aciertos > 0:
                    # resultados.append({'fast': f, 'slow': s, 'aciertos': aciertos})
        
        # df_res = pd.DataFrame(resultados).sort_values(by='aciertos', ascending=False)
        # df_res.to_csv('Datos_Emas.csv', index=False)
        # print("fin")
        # return df_res
    # except Exception as e:
        # #MF.write_log(f'{txcolors.DEFAULT}{SIGNAL_NAME}: {txcolors.SELL_LOSS} - Exception: {e}{txcolors.DEFAULT}', MAIN_PATH + SIGNAL_NAME + '.log', True, False)
        # exc_type, exc_obj, exc_tb = sys.exc_info()
        # print('optimizar_emas_bruta Error on line ' + str(exc_tb.tb_lineno))
        # pass
# Ejecución
# ranking = optimizar_emas_bruta(df, pivotes_target)
# print(ranking.head(10))

#Data = time Open High Low Close Volume
def buy(Data, CLOSE, pair, main_path):
    try:
        # HOST = "localhost"
        # PORT = 10000
        # tn = telnetlib.Telnet(HOST, PORT)
        
        buySignal = False
        _, _, BI= MF.Bollinger_Bands(Data, 20, 2)
        buySignal = CLOSE <= BI and MF.Rsi(Data, 14) < 45
        #buySignal = MF.Rsi(Data, 14) < 30 and MF.Check_Volume(Data) and MF.Macd_Ind(Data, 12, 26, 9) < -1 and MF.Ema(Data, 50) < MF.Ema(Data, 200) and MF.Low_Volatility(Data, CLOSE)
        #TMA, TMAH, TMAL = MF.tma_bands(Data) 
        #ema_fast_df = MF.Ema_df(Data, 10)
        #ema_slow_df = MF.Ema_df(Data, 40)
        
        # MF.Cross_Emas devuelve 1 para cruce al alza (Golden Cross)
        #cruce_alza = MF.Cross_Emas(ema_fast_df, "Ema_10", ema_slow_df, "Ema_40") == 1
        
        # Filtro adicional con RSI y Tendencia (como en tus comentarios)
        #rsi_val = MF.Rsi(Data, 14)
        #ema_tendencia = MF.Ema(Data, 200)
        # HL_HH = MF.get_gann_status(Data)
        # HH_HL_anterior = ""
        # HL_anterior = 0
        # HH_anterior = 0
        # if os.path.exists("HL_HH.txt"):
            # with open("HL_HH.txt", "r") as f:
                # HH_HL_anterior = f.readline().split(",")
            # if HH_HL_anterior[0] == "HH":
                # HH_anterior = HH_HL_anterior[1]
            # elif HH_HL_anterior[0] == "HL":
                # HL_anterior = HH_HL_anterior[1]
        #buySignal = MF.get_gann_status(Data, 10) == "HL"
        #buySignal = CLOSE < TMAL and CLOSE > MF.Ema(Data, 200) 
        # with open("HL_HH.txt", "w") as f:
            # timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # f.write(f'{HL_HH},{CLOSE}\n')
        
        #agent = IA.PredictiveReinforcementAgent()
        #df_ema50 = MF.EMA_df(Data, 50)
        #action, prediction = agent.predict_and_act(df_ema50)
        
        # # === EMAs que necesitamos ===
        # ema5  = MF.Ema(Data, 5)
        # ema8  = MF.Ema(Data, 8)
        # ema13 = MF.Ema(Data, 13)
        # ema50 = MF.Ema(Data, 50)          # Filtro de tendencia

        # # Condiciones exactas de la estrategia 5-8-13 (solo LONG)
        # condicion1 = ema5 > ema8 > ema13                    # Orden alcista y separadas
        # condicion2 = CLOSE > ema50                          # Tendencia general alcista
        # condicion3 = Data['Close'].iloc[-2] <= ema13             # Pullback o toque a la EMA13 (opcional pero mejora mucho el winrate)
        # # Si quieres entrada más agresiva quita la condicion3

        # buySignal = condicion1 and condicion2 and condicion3
        
        # H, L = MF.Pivots_Hl(Data)
        # prepared_data = MF.prepare_data_for_zigzag(Data)
        # zigzag_data = MF.Zigzag_safe(prepared_data, 2, 0.3)
        # last_value, last_type, last_index = MF.get_last_zigzag_pivot(zigzag_data)
        # print(f"\nÚltimo pivote: {last_value} ({last_type}) en {last_index}")
        # print("H:", H, "L:", L)
        # new_high_pivot, new_low_pivot = MF.Pivots_HL_optimized(Data)
        # print(new_high_pivot, new_low_pivot)
        # print("new_high_pivot:", new_high_pivot, "new_low_pivot:", new_low_pivot)
        # buySignal = MF.Ema(Data, 9) < MF.Ema(Data, 21) and MF.Rsi(Data, 14) < 30 and CLOSE < MF.Ema(Data, 21) and MF.Macd_Ind(Data, 12, 26, 9) < -1.05
        # buySignal = MF.Rsi(Data, 14) < 30 and MF.check_volume(Data)
        # buySignal = MF.Rsi(Data, 14) < 30 and MF.check_volume(Data) and MF.Ema(Data, 50) < MF.Ema(Data, 200)
        # buySignal = MF.Rsi(Data, 14) < 30 and MF.check_volume(Data) and MF.Macd_Ind(Data, 12, 26, 9) < -1.5 and MF.Ema(Data, 50) < MF.Ema(Data, 200)
        # buySignal = MF.Rsi(Data, 14) < 30 and MF.check_volume(Data)
        # valor_rsi_sobrecompra, valor_rsi_sobreventa, valor_macd_buy, valor_macd_venta = MF.calcular_rangos_dinamicos_macd_rsi(Data, 14, 12, 26, 9, 70, 30, 30, 30)
        # print(valor_rsi_sobrecompra, valor_rsi_sobreventa, valor_macd_buy, valor_macd_venta)
        # values = MF.guardar_rangos_dinamicos(pair, 15, valor_rsi_sobrecompra, valor_rsi_sobreventa, valor_macd_buy, valor_macd_venta)
        # valor_rsi_sobrecompra = values["rsi_over"]
        # valor_rsi_sobreventa = values["rsi_under"]
        # valor_macd_buy = values["macd_buy"]
        #valor_macd_venta = values["macd_sell"]
        # buySignal = MF.Rsi(Data, 14) < valor_rsi_sobrecompra and MF.Check_Volume(Data) and MF.Macd_Ind(Data, 12, 26, 9) < valor_macd_buy and MF.Ema(Data, 50) < MF.Ema(Data, 200) and MF.Low_Volatility(Data, CLOSE)
        # resultados = MF.calcular_probabilidad_5m_adelante(Data)

        # Imprimir los resultados
        # print("--- Análisis de los n precios de BNB/USDT ---")
        # print(f"Probabilidad histórica de subida: {resultados['prob_subida_5m']}%")
        # print(f"Probabilidad histórica de bajada: {resultados['prob_bajada_5m']}%")
        # print(f"Porcentaje promedio de subida: {resultados['avg_subida_5m']}%")
        # print(f"Porcentaje promedio de bajada: {resultados['avg_bajada_5m']}%")
        # print(f"Volatilidad histórica: {resultados['volatilidad_historica_5m']}")
        # buySignal = MF.Ema(Data, 9) < MF.Ema(Data, 21) and MF.Rsi(Data, 14) < 30 and CLOSE < MF.Ema(Data, 21)
        # buySignal = MF.spread_strategy(0.01, 0.07, Data) == 1 and CLOSE > MF.Ema(Data, 200) and (CLOSE < MF.B(Data) or CLOSE <= round(MF.B(Data) - ((0.1 * MF.B(Data))/100), 5))
        # buySignal = MF.Rsi(Data, 14) < 50 and L <= CLOSE and MF.Macd_Ind(Data, 12, 26, 9) < -0.95
        # buySignal =  CLOSE <= L and last_value == L
        # if buySignal:
            # print("Pivots_L:", L, "zigzag:", last_value)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(e)
        print('Buy Error on line ' + str(exc_tb.tb_lineno))
        pass
    return buySignal
    
    
def sell(Data, CLOSE, pair, main_path):
    try:
        sellSignal = False
        #sellSignal = bool(MF.Rsi(Data, 14) > 70 and MF.Check_Volume(Data) and MF.Macd_Ind(Data, 12, 26, 9) > 3 and MF.Ema(Data, 50) > MF.Ema(Data, 200) and MF.Low_Volatility(Data, CLOSE))
        #es_stop_loss = MF.Sl(pair, CLOSE, 2.0, main_path)  # 2% SL
        #es_take_profit = MF.Tp(pair, CLOSE, 3.0, main_path) # 3% TP
        
        # Señal de salida por indicadores (ej. Cruce a la baja)
        # ema_fast_df = MF.Ema_df(Data, 10)
        # ema_slow_df = MF.Ema_df(Data, 40)
        # cruce_baja = MF.Cross_Emas(ema_fast_df, "Ema_10", ema_slow_df, "Ema_40") == -1
        BS, BM, _= MF.Bollinger_Bands(Data, 20, 2)
        #sellSignal = CLOSE >= (BS if MF.Ema(Data, 20) > MF.Ema(Data, 50) else BM) and MF.Rsi(Data, 14) > 62 and CLOSE > MF.Bought_at(pair, main_path)
        # if MF.Ema(Data, 20) > MF.Ema(Data, 50): 
        sellSignal = CLOSE >= BM and MF.Rsi(Data, 14) > 62 and CLOSE > MF.Bought_at(pair, main_path)
        #if CLOSE > MF.Bought_at(pair, main_path): print(CLOSE, MF.Bought_at(pair, main_path))
        # else:
            # sellSignal = CLOSE >= BM and MF.Rsi(Data, 14) > 62 and CLOSE > MF.Bought_at(pair, main_path)
        # TMA, TMAH, TMAL = MF.tma_bands(Data) 
        # sell_Signal =  (CLOSE > TMAH and CLOSE > MF.Ema(Data, 200) and CLOSE > MF.Bought_at(pair, main_path)) or MF.StopLoss_Time(pair, Data['time'].iloc[-1], 1440, main_path) 
        # decision = MF.get_trade_signal_with_risk(Data, "sell", MF.Get_Balance_TestMode(main_path))
        # if decision['action'] == 'TRADE':
            # sl = decision['sl']
            # tp = decision['tp']
            # sellSignal = sell_Signal or CLOSE <= sl or CLOSE >= tp

        # ema5  = MF.Ema(Data, 5)
        # ema8  = MF.Ema(Data, 8)
        # ema13 = MF.Ema(Data, 13)

        # # Precio de compra para calcular ganancia/perdida (el bot ya lo guarda en Bought_at)
        # bought_price = MF.Bought_at(pair)

        # # === SALIDAS POSIBLES (tú eliges cuál activar) ===

        # # Opción 1: Salida automática cuando EMA5 cruza hacia abajo la EMA13 (la más usada)

        # # Opción 2: Take Profit fijo (ejemplo +1.2%)
        # #tp_porcentaje = 1.2
        # #salida_tp = CLOSE >= bought_price * (1 + tp_porcentaje / 100)

        # # Opción 3: Stop Loss fijo (ejemplo -0.6%)
        # #sl_porcentaje = 0.6
        # #salida_sl = CLOSE <= bought_price * (1 - sl_porcentaje / 100)

        # # Opción 4: Salida por toque a EMA5 desde abajo (más conservadora)
        # # salida_conservadora = CLOSE < ema5

        # # Elegimos la combinación que más te guste
        # sellSignal = ema5 < ema13 #or salida_tp or salida_sl
        
        # B = MF.Bought_at(pair)
        # sellSignal = MF.Ema(Data, 9) > MF.Ema(Data, 21) and MF.Rsi(Data, 14) > 70 and CLOSE > MF.Ema(Data, 21)and MF.Macd_Ind(Data, 12, 26, 9) > 0.85
        # sellSignal = MF.Rsi(Data, 14) > 70 and MF.check_volume(Data) and MF.Ema(Data, 50) > MF.Ema(Data, 200)
        # sellSignal = bool(MF.Rsi(Data, 14) > 70 and MF.check_volume(Data) and MF.Macd_Ind(Data, 12, 26, 9) > 0.85 and MF.Ema(Data, 50) > MF.Ema(Data, 200)) or MF.Sl(pair, CLOSE, 4) 
        # sellSignal = MF.Rsi(Data, 14) > 70 and MF.check_volume(Data) or MF.Sl(pair, CLOSE, 4)
        # sellSignal = MF.Rsi(Data, 14) > 70 and MF.check_volume(Data) and MF.Macd_Ind(Data, 12, 26, 9) > 0.85 and MF.Ema(Data, 50) > MF.Ema(Data, 200) and MF.low_volatility(Data, CLOSE) or MF.Sl(pair, CLOSE, 4)
        # valor_rsi_sobrecompra, valor_rsi_sobreventa, valor_macd_buy, valor_macd_venta = MF.calcular_rangos_dinamicos_macd_rsi(Data, 14, 12, 26, 9, 70, 30, 30, 30)
        # print(valor_rsi_sobrecompra, valor_rsi_sobreventa, valor_macd_buy, valor_macd_venta)
        # values = MF.guardar_rangos_dinamicos(pair, 15, valor_rsi_sobrecompra, valor_rsi_sobreventa, valor_macd_buy, valor_macd_venta)
        # valor_rsi_sobrecompra = values["rsi_over"]
        # valor_rsi_sobreventa = values["rsi_under"]
        # valor_macd_buy = values["macd_buy"]
        # valor_macd_venta = values["macd_sell"]
        # sellSignal = MF.Rsi(Data, 14) > valor_rsi_sobreventa and MF.Check_Volume(Data) and MF.Macd_Ind(Data, 12, 26, 9) > valor_macd_venta and MF.Ema(Data, 50) > MF.Ema(Data, 200) and MF.Low_Volatility(Data, CLOSE)
        # H, L = MF.Pivots_Hl(Data)
        # prepared_data = MF.prepare_data_for_zigzag(Data)
        # zigzag_data = MF.Zigzag_safe(prepared_data, 2, deviation=0.3)
        # last_value, last_type, last_index = MF.get_last_zigzag_pivot(zigzag_data)
        # print(f"\nÚltimo pivote: {last_value} ({last_type}) en {last_index}")
        # print("H:", H, "L:", L)
        # new_high_pivot, new_low_pivot = MF.Pivots_HL_optimized(Data)
        # print(new_high_pivot, new_low_pivot)
        # print("new_high_pivot:", new_high_pivot, "new_low_pivot:", new_low_pivot)
        # sellSignal = MF.Rsi(Data, 14) > 50 and H >= CLOSE and MF.Macd_Ind(Data, 12, 26, 9) > 1 or MF.Sl(pair, CLOSE, 1)
        # sellSignal = CLOSE >= H and last_value == H 
        # if sellSignal:
            # print("Pivots_H:", H, "zigzag:",last_value)
    except Exception as e:
        print(e)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print('Sell Error on line ' + str(exc_tb.tb_lineno))
        pass
    return sellSignal
