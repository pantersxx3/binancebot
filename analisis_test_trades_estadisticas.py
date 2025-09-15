import pandas as pd
import ta

# === Funciones que ya tenías ===
def Calculate_Market_Direction(data, adx_period=20, adx_threshold=20):
    adx = ta.trend.ADXIndicator(
        high=data["High"], low=data["Low"], close=data["Close"], window=adx_period
    ).adx().iloc[-1]
    di_plus = ta.trend.ADXIndicator(
        high=data["High"], low=data["Low"], close=data["Close"], window=adx_period
    ).adx_pos().iloc[-1]
    di_minus = ta.trend.ADXIndicator(
        high=data["High"], low=data["Low"], close=data["Close"], window=adx_period
    ).adx_neg().iloc[-1]
    
    if adx > adx_threshold:
        if di_plus > di_minus:
            return "alcista"
        elif di_minus > di_plus:
            return "bajista"
    return "sin_tendencia"

def Atr_Normalized(data, atr_period=20):
    atr = ta.volatility.AverageTrueRange(
        high=data["High"], low=data["Low"], close=data["Close"], window=atr_period
    ).average_true_range().iloc[-1]
    return atr / data["Close"].iloc[-1]

def Check_Volume(data, window=20, umbral=1.2):
    volumen_actual = data["Volume"].iloc[-1]
    volumen_promedio = data["Volume"].rolling(window).mean().iloc[-1]
    return bool(volumen_actual > umbral * volumen_promedio)

def Check_Consolidation(data, adx_threshold=20, atr_threshold=0.003):
    adx = ta.trend.ADXIndicator(
        high=data["High"], low=data["Low"], close=data["Close"], window=20
    ).adx().iloc[-1]
    atr = Atr_Normalized(data, 20)
    return adx < adx_threshold and atr < atr_threshold

def Detect_Market_Type(data, umbral_alto_volatilidad=0.01):
    tendencia = Calculate_Market_Direction(data, 20, 20)
    volatilidad = Atr_Normalized(data, 20)
    consolidacion = Check_Consolidation(data, 20, 0.003)
    volumen_alto = Check_Volume(data, 20, 1.2)
    
    if tendencia == "alcista" and volumen_alto:
        return "tendencia_alcista_confirmada"
    elif tendencia == "bajista" and volumen_alto:
        return "tendencia_bajista_confirmada"
    elif consolidacion and not volumen_alto:
        return "consolidacion_confirmado"
    elif volatilidad > umbral_alto_volatilidad:
        return "volatil_confirmado"
    else:
        return "rango_lateral_confirmado"


# === Función para agregar indicadores al DataFrame ===
def add_indicators(df):
    # RSI
    df["RSI"] = ta.momentum.RSIIndicator(df["Close"], window=14).rsi()
    
    # MACD
    macd = ta.trend.MACD(df["Close"])
    df["MACD"] = macd.macd()
    df["MACD_signal"] = macd.macd_signal()
    
    # EMAs
    df["EMA20"] = df["Close"].ewm(span=20).mean()
    df["EMA50"] = df["Close"].ewm(span=50).mean()
    df["EMA200"] = df["Close"].ewm(span=200).mean()
    
    # ATR normalizado
    atr = ta.volatility.AverageTrueRange(
        high=df["High"], low=df["Low"], close=df["Close"], window=20
    )
    df["ATR_norm"] = atr.average_true_range() / df["Close"]
    
    return df


# === Función para etiquetar el tipo de mercado en todo el histórico ===
def label_market_types(df):
    labels = []
    for i in range(len(df)):
        sub = df.iloc[:i+1]  # dataset hasta la vela actual
        if len(sub) < 50:    # esperar al menos 50 velas para cálculos
            labels.append(None)
            continue
        labels.append(Detect_Market_Type(sub))
    df["market_type"] = labels
    return df


# === Función principal de análisis ===
def analyze_market_statistics(df):
    df = add_indicators(df)
    df = label_market_types(df)
    
    stats = df.groupby("market_type")[["RSI", "MACD", "ATR_norm", "EMA20", "EMA50", "EMA200"]].agg(
        ["mean", "min", "max", "std"]
    )
    
    return stats


# === Uso ===
# Suponiendo que df es tu DataFrame con columnas: ["Open","High","Low","Close","Volume"]
# Ejemplo:
df = pd.read_csv("BTCUSDT.csv")  # tu dataset de 1 año
stats = analyze_market_statistics(df)
print(stats)
