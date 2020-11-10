import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import mplfinance as mpf

def loadStocks(start, end, stock):

    df = yf.download(stock, start, end, interval='1d')
    return df


def findRSI (data, time_window):
   
    diff = data.diff(1).dropna()        

    up_chg = 0 * diff
    down_chg = 0 * diff
    
    # up change
    up_chg[diff > 0] = diff[diff > 0]
    up_chg_avg = up_chg.ewm(com=time_window-1 , min_periods=time_window).mean()
    
    # down change 
    down_chg[diff < 0] = diff[diff < 0]  
    down_chg_avg = down_chg.ewm(com=time_window-1 , min_periods=time_window).mean()
    
    # rsi
    rs = abs(up_chg_avg/down_chg_avg)
    rsi = 100 - 100/(1+rs)
    
    return rsi    


def tradeRSI(df, high, low):
    
    position = 0 
    counter = 0
    percentChange = []   
    
    for i in df.index:
        rsi = df['RSI']
        close = df['Adj Close'][i]
        
        # buy
        if(rsi[i] < low):                          
            if(position == 0):
                buyP = close   # buy price
                position = 1   # turn position
           
        # sell    
        elif(rsi[i] > high):
            if(position == 1):   # have a position in down trend
                position = 0     # sell position
                sellP = close    # sell price
                perc = (sellP/buyP-1)*100
                percentChange.append(perc)                      
        
        if(counter == df["Adj Close"].count() -1 and position == 1):
            position = 0
            sellP = close
            perc = (sellP/buyP-1)*100
            percentChange.append(perc)
        counter += 1

    return percentChange

def calcReturn(percentChange, df):
   
    gains = 0
    numGains = 0
    losses = 0
    numLosses = 0
    totReturn = 1
   
    for i in percentChange:
        if(i > 0):
            gains += i
            numGains += 1
        else:
            losses += i
            numLosses += 1
        totReturn = totReturn*((i/100)+1)
   
    totReturn = round((totReturn-1)*100,2)
    totTrades = numGains + numLosses

    return totTrades, totReturn


def RSI(start, end, stock, low, high, plot = False):

    df = loadStocks(start, end, stock)
    df['RSI'] = findRSI(df['Adj Close'], 14)
    percentChange = tradeRSI(df, high, low)

    # need to change lines bc mav is moving average
    if plot == True:
        mpf.plot(df, type = 'ohlc',figratio=(16,6), 
         mav=(low, high), 
         #volume=True, title= str(stock), 
         style='charles')
    
    return calcReturn(percentChange, df)

def main():
    start = '2010-01-01'
    end = '2020-01-01'
    stocks = ['SPY', 'VGT', 'XLV']
    short_sma = 20
    long_sma = 40
    rsi_low = 40
    rsi_high = 60

    results = SMA(start[0], end[0], 'VGT', 20, 50, True)  
    #results = RSI(start[0], end[0], stocks[2], 30, 70)
    print(results)

    return 0
main()