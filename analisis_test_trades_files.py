import pandas as pd
from prettytable import PrettyTable
import glob
import sys
import os
import argparse
import operator

parser = argparse.ArgumentParser(description='Analizador de operaciones de trading desde archivos CSV.')
parser.add_argument('archivos', nargs='*', help='Los archivos CSV a analizar. Si no se especifican, se mostrará un menú.')
parser.add_argument('-g', '--ganancia', action='store_true', help='Muestra la ganancia total.')
parser.add_argument('-co', '--cantidad_operaciones', action='store_true', help='Muestra la cantidad de operaciones.')
parser.add_argument('-p', '--perdida', action='store_true', help='Muestra la perdida total.')
parser.add_argument('-pg', '--porcentaje_ganancia', action='store_true', help='Muestra el porcentaje de ganancia.')
parser.add_argument('-pr', '--promedio_horas', action='store_true', help='Muestra el promedio de horas de hold.')
parser.add_argument('-pa', '--promedio_ganancia', action='store_true', help='Muestra la ganancia promedio.')
parser.add_argument('-c', '--comision', action='store_true', help='Muestra la comisión total.')
parser.add_argument('-gm', '--ganancia_mas_alto', action='store_true', help='Muestra la ganancia más alta.')
parser.add_argument('-sortby', '--ordenar_por', type=str, help='Ordena los resultados por una métrica. Ej: -sortby ganancia')
parser.add_argument('-desc', '--descendente', action='store_true', help='Ordena los resultados de forma descendente.')

args = parser.parse_args()

if args.archivos:
    if args.archivos == ["*"]:
        patron = os.path.join("./", f'*.csv')
        archivos_seleccionados = glob.glob(patron)
    else:
        archivos_seleccionados = args.archivos
else:
    patron = os.path.join("./", f'*.csv')
    files = glob.glob(patron)
    
    if not files:
        print("No se encontraron archivos CSV en el directorio.")
        sys.exit()

    for i, file in enumerate(files):
        print(f"[{i+1}] {file}")

    print("\nSelecciona los archivos que deseas analizar (ej: 1,3,4):")
    seleccion_str = input("Tu selección: ")
    try:
        indices_seleccionados = [int(x.strip()) - 1 for x in seleccion_str.split(',')]
        archivos_seleccionados = [files[i] for i in indices_seleccionados if 0 <= i < len(files)]
    except (ValueError, IndexError):
        print("Entrada no válida. Se analizarán todos los archivos por defecto.")
        archivos_seleccionados = files

if not archivos_seleccionados:
    print("No se seleccionaron archivos. Saliendo.")
    sys.exit()

mapeo_columnas = {
    'cantidad_operaciones': 'Cantidad de operaciones',
    'ganancia': 'Total',
    'perdida': 'Perdio',
    'porcentaje_ganancia': 'Porcentaje Ganancia',
    'promedio_horas': 'Promedio (horas)',
    'promedio_ganancia': 'Ganancias Promedio',
    'comision': 'Commission',
    'ganancia_mas_alto': 'Ganancia más alto (Sell)'
}

opciones_seleccionadas = any([args.ganancia, args.cantidad_operaciones, args.perdida, args.porcentaje_ganancia, args.promedio_horas, args.promedio_ganancia, args.comision, args.ganancia_mas_alto])

if opciones_seleccionadas:
    resultados_por_archivo = []
    for file in archivos_seleccionados:
        try:
            df = pd.read_csv(file)
            df["Datetime"] = pd.to_datetime(df["Datetime"])

            order_ids_to_remove = df[(df['Profit $ USDT'] == 0.0) & (df['Type'] == 'Sell')]['OrderID'].unique()
            df = df[~df['OrderID'].isin(order_ids_to_remove)]

            if "Buy" == df.iloc[-1]["Type"]:
                df.drop(df.index[-1], inplace=True)

            buys = df[df['Type'] == "Buy"][['OrderID', 'Datetime']]
            sells = df[df['Type'] == "Sell"][['OrderID', 'Datetime']]

            merged_trades = pd.merge(buys, sells, on='OrderID', suffixes=('_Buy', '_Sell'))
            merged_trades["Hold Time"] = (merged_trades["Datetime_Sell"] - merged_trades["Datetime_Buy"]).dt.total_seconds() / 3600
            unique_hold_times = merged_trades.drop_duplicates(subset='OrderID', keep='first')
            hold_time_series = unique_hold_times.set_index('OrderID')['Hold Time']

            df["Hold Time"] = pd.NA
            df.loc[df['Type'] == 'Sell', "Hold Time"] = df.loc[df['Type'] == 'Sell', 'OrderID'].map(hold_time_series)
            df["Hold Time"] = pd.to_numeric(df["Hold Time"], errors='coerce')

            max_hold = df["Hold Time"].max()
            promedio_hold = df["Hold Time"].mean()
            sells_profits = df[df['Type'] == "Sell"]["Profit $ USDT"]
            max_price = sells_profits.max()
            avg_profit = sells_profits.mean()
            total_profit = sells_profits.sum()
            ganado = sells_profits[sells_profits > 0].sum()
            perdido = sells_profits[sells_profits < 0].sum()
            Commission = df["Commission"].sum()
            ganancia_percent = (total_profit / ganado) * 100 if ganado > 0 else 0.0

            resultados_archivo = {
                'archivo': os.path.basename(file),
                'Cantidad de operaciones': len(merged_trades),
                'Total': round(total_profit, 2),
                'Perdio': round(perdido, 2),
                'Porcentaje Ganancia': round(ganancia_percent, 2),
                'Promedio (horas)': round(promedio_hold, 2),
                'Ganancias Promedio': str(round(avg_profit, 2)) + " USDT",
                'Commission': round(Commission, 2),
                'Ganancia más alto (Sell)': round(max_price, 2)
            }
            resultados_por_archivo.append(resultados_archivo)

        except FileNotFoundError:
            print(f"Error: El archivo '{file}' no fue encontrado. Ignorando.")
        except Exception as e:
            print(f"Ocurrió un error al procesar el archivo '{file}': {e}. Ignorando.")

    if args.ordenar_por:
        clave_ordenamiento = mapeo_columnas.get(args.ordenar_por)
        if clave_ordenamiento:
            try:
                resultados_por_archivo.sort(key=operator.itemgetter(clave_ordenamiento), reverse=args.descendente)
            except KeyError:
                print(f"Advertencia: No se puede ordenar por '{args.ordenar_por}'. La columna no existe en los resultados. Se mostrará sin ordenar.")

    my_table = PrettyTable()
    my_table.title = 'Informe de Análisis de Trades'
    my_table.border = True
    my_table.align = "c"
    my_table.valign = "m"

    columnas = ['Archivo']
    if args.cantidad_operaciones: columnas.append(mapeo_columnas['cantidad_operaciones'])
    if args.ganancia: columnas.append(mapeo_columnas['ganancia'])
    if args.perdida: columnas.append(mapeo_columnas['perdida'])
    if args.porcentaje_ganancia: columnas.append(mapeo_columnas['porcentaje_ganancia'])
    if args.promedio_horas: columnas.append(mapeo_columnas['promedio_horas'])
    if args.promedio_ganancia: columnas.append(mapeo_columnas['promedio_ganancia'])
    if args.comision: columnas.append(mapeo_columnas['comision'])
    if args.ganancia_mas_alto: columnas.append(mapeo_columnas['ganancia_mas_alto'])

    my_table.field_names = columnas

    for resultado in resultados_por_archivo:
        fila = [resultado['archivo']]
        if args.cantidad_operaciones: fila.append(resultado[mapeo_columnas['cantidad_operaciones']])
        if args.ganancia: fila.append(resultado[mapeo_columnas['ganancia']])
        if args.perdida: fila.append(resultado[mapeo_columnas['perdida']])
        if args.porcentaje_ganancia: fila.append(resultado[mapeo_columnas['porcentaje_ganancia']])
        if args.promedio_horas: fila.append(resultado[mapeo_columnas['promedio_horas']])
        if args.promedio_ganancia: fila.append(resultado[mapeo_columnas['promedio_ganancia']])
        if args.comision: fila.append(resultado[mapeo_columnas['comision']])
        if args.ganancia_mas_alto: fila.append(resultado[mapeo_columnas['ganancia_mas_alto']])
    
        my_table.add_row(fila)

    print(my_table.get_string())
else:
    my_table = PrettyTable()
    my_table.format = True
    my_table.border = True
    my_table.align = "c"
    my_table.valign = "m"
    my_table.left_padding_width = 1
    my_table.right_padding_width = 1
    my_table.title = f'Informe'
    my_table.add_column("Data-Archivo", ["Cantidad de operaciones", "Total", "Gano", "Perdio", "Porcentaje Ganancia", "Ganancia más alto (Sell)", "Ganancia más bajo (Sell)", "Máximo (horas)", "Mínimo (horas)", "Promedio (horas)", "Ganancias Promedio", "Commission", "0 to 1", "1.01 to 2", "2.01 to 3", "3.01 to 4", "4.01 to 5", "-1 to 0", "-2 to -1.01", "-3 to -2.01", "-4 to -3.01", "-5 to -4.01", "Mes 1","Mes 2","Mes 3","Mes 4","Mes 5","Mes 6","Mes 7","Mes 8","Mes 9","Mes 10","Mes 11","Mes 12"])

    for file in archivos_seleccionados:
        try:
            df = pd.read_csv(file)
            df["Datetime"] = pd.to_datetime(df["Datetime"])

            order_ids_to_remove = df[(df['Profit $ USDT'] == 0.0) & (df['Type'] == 'Sell')]['OrderID'].unique()
            df = df[~df['OrderID'].isin(order_ids_to_remove)]

            if "Buy" == df.iloc[-1]["Type"]:
                df.drop(df.index[-1], inplace=True)

            buys = df[df['Type'] == "Buy"][['OrderID', 'Datetime']]
            sells = df[df['Type'] == "Sell"][['OrderID', 'Datetime']]

            merged_trades = pd.merge(buys, sells, on='OrderID', suffixes=('_Buy', '_Sell'))
            merged_trades["Hold Time"] = (merged_trades["Datetime_Sell"] - merged_trades["Datetime_Buy"]).dt.total_seconds() / 3600
            unique_hold_times = merged_trades.drop_duplicates(subset='OrderID', keep='first')
            hold_time_series = unique_hold_times.set_index('OrderID')['Hold Time']

            df["Hold Time"] = pd.NA
            df.loc[df['Type'] == 'Sell', "Hold Time"] = df.loc[df['Type'] == 'Sell', 'OrderID'].map(hold_time_series)
            df["Hold Time"] = pd.to_numeric(df["Hold Time"], errors='coerce')

            max_hold = df["Hold Time"].max()
            min_hold = df["Hold Time"].min()
            promedio_hold = df["Hold Time"].mean()

            sells_profits = df[df['Type'] == "Sell"]["Profit $ USDT"]
            max_price = sells_profits.max()
            min_price = sells_profits.min()
            avg_profit = sells_profits.mean()
            
            total_profit = sells_profits.sum()
            
            ganado = sells_profits[sells_profits > 0].sum()
            perdido = sells_profits[sells_profits < 0].sum()
            
            Commission =  df["Commission"].sum()
            
            if ganado > 0:
                ganancia_percent = (total_profit / ganado) * 100
            else:
                ganancia_percent = 0.0

            profit = sells_profits
            ranges = [
                (0, 1), (1.01, 2), (2.01, 3), (3.01, 4), (4.01, 5),
                (-1, 0), (-2, -1.01), (-3, -2.01), (-4, -3.01), (-5, -4.01)
            ]
            range_counts = {}
            for low, high in ranges:
                if low < high:
                    count = profit[(profit > low) & (profit <= high)].count()
                else:
                    count = profit[(profit < low) & (profit >= high)].count()
                range_counts[f"{low} to {high}"] = count
            
            rango = []
            rango = ["No Data"] * 10
            c = 0
            for k, v in range_counts.items():
                rango[c] = f"{v}"
                c = c + 1

            df["Month"] = df["Datetime"].dt.to_period("M")
            ops_por_mes = df.groupby("Month").size()
            ops_por_mes_desc = ops_por_mes.sort_index(ascending=True)
            
            meses = []
            meses = ["No Data"] * 13
            d = 0
            for mes in ops_por_mes:
                meses[d] = mes
                d = d + 1
                
            file_name_display = os.path.basename(file)[:15] + "..." if len(os.path.basename(file)) > 15 else os.path.basename(file)
            my_table.add_column(file_name_display, [
                len(merged_trades), round(total_profit,2), round(ganado,2), round(perdido,2), 
                round(ganancia_percent,2), round(max_price,2), round(min_price,2), 
                round(max_hold,2), round(min_hold,4), round(promedio_hold,2), 
                str(round(avg_profit,2)) + " USDT", round(Commission,2), 
                rango[0], rango[1], rango[2], rango[3], rango[4], rango[5], 
                rango[6], rango[7], rango[8], rango[9], 
                meses[1], meses[2], meses[3], meses[4], meses[5], meses[6], 
                meses[7], meses[8], meses[9], meses[10], meses[11], meses[12]
            ])
        except FileNotFoundError:
            print(f"Error: El archivo '{file}' no fue encontrado. Ignorando.")
        except pd.errors.EmptyDataError:
            print(f"Error: El archivo '{file}' está vacío. Ignorando.")
        except Exception as e:
            print(f"Ocurrió un error al procesar el archivo '{file}': {e}. Ignorando.")
    
    print(my_table.get_string())
