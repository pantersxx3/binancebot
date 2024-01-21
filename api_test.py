import os
import sys
import time
import pandas as pd
import asyncio
from binance import Client, AsyncClient, BinanceSocketManager
from binance.exceptions import BinanceAPIException
from pprint import pformat
from binance.helpers import round_step_size
from binance.enums import *
TEST_API_KEY = 'LeDeK6MTfC5fHuctvxhEBGEr99afbXOlLxx9vfudt6Dpd6Sb9ZEvnwSGFbznzEr6'
TEST_API_SECRET = 'LS1Ic3SNpoemeDVHeSJ6iQ4BnIrbBNw9y8SjcasBLerUrwRBAEKse8ub5STaoL6F'
#  Instantiate Binance API client TESTNET US Market
client = Client(api_key=TEST_API_KEY, api_secret=TEST_API_SECRET, testnet=True, tld='us')


def get_info(coin, file):
    info = client.get_symbol_info(coin)
    with open(file, "a") as f:
        f.write(str(info) + '\n')
    return info
    #step_size1 = "" #info['stepSize']
    #step_size2 = info['filters'][2]
    #print("step_size1", step_size1, "step_size2", step_size2)
    #lot_size[coin] = step_size.index('1') - 1
            
    #for filt in info['filters']:
        #if filt['filterType'] == 'LOT_SIZE':
            #lot_size = int(filt['stepSize'].find('1') - 1)
            #print("lot_size", lot_size)
            #break