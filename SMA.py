import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import mplfinance as mpf

def loadStocks(start, end, stock):

    df = yf.download(stock, start, end, interval='1d')
    return df

def findSMA(short_sma, long_sma, df):

    SMAs=[short_sma, long_sma]

    for i in SMAs:
        df["SMA_"+str(i)]= df.iloc[:,4].rolling(window=i).mean()

    return df, SMAs

def tradeSMA(df, short_sma, long_sma):
    
    position = 0 
    counter = 0
    percentChange =[]  
    
    for i in df.index:
        SMA_short = df["SMA_"+str(short_sma)]
        SMA_long = df["SMA_"+str(long_sma)]
        close = df['Adj Close'][i]
        
        # buy
        if(SMA_short[i] > SMA_long[i]):                    
            if(position == 0):
                buyP = close   # buy price
                position = 1   # turn position
        
        # sell     
        elif(SMA_short[i] < SMA_long[i]):
            if(position == 1):   # have a position in down trend
                position = 0     # selling position
                sellP = close    # sell price
                perc = (sellP/buyP-1)*100
                percentChange.append(perc)                   
        
        if(counter == df["Adj Close"].count()-1 and position == 1):
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

def SMA(start, end, stock, short_sma, long_sma, plot = False):

    df = loadStocks(start, end, stock)
    df_updated, SMAs = findSMA(short_sma, long_sma, df)
    percentChange = tradeSMA(df_updated, short_sma, long_sma)

    if plot == True:
        mpf.plot(df, type = 'line',figratio=(16,6), 
         mav=(short_sma,long_sma), 
         #volume=True, title= str(stock), 
         style='charles')
    
    return calcReturn(percentChange, df_updated)

def main():
    start = ['2010-01-01']
    end = ['2020-01-01']
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