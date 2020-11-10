import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import mplfinance as mpf


def loadStocks(start, end, stock):
    df = yf.download(stock, start, end, interval='1d')
    return df

def findSMA(short_sma, long_sma, df):
    SMAs = [short_sma, long_sma]

    for i in SMAs:
        df["SMA_" + str(i)] = df.iloc[:, 4].rolling(window=i).mean()

    return df, SMAs

def findMACD(data):
    # SMA
    arraySMA = [0] * data.shape[0]
    arraySMA = data.iloc[:, 4].rolling(window=10).mean()

    # Temp SMA values until I figure out how this should really work
    yesterdayEMA12 = arraySMA[12]
    yesterdayEMA26 = arraySMA[26]
    yesterdaySignal = 20

    # Generating Arrays with a size that is the number of rows
    arrayEMA12 = [0] * data.shape[0]
    arrayEMA26 = [0] * data.shape[0]
    arrayMACD = [0] * data.shape[0]
    arraySignal = [0] * data.shape[0]

    for i in range(len(data.index)):

        # Skip the first few to get a good moving average
        if i < 13:
            continue

        # Calculate the 12EMA, 26EMA, and MACD and store the values in respective arrays
        todayEMA12 = (data['Adj Close'][i] * (2 / (1 + 12))) + yesterdayEMA12 * (1 - (2 / (1 + 12)))
        yesterdayEMA12 = todayEMA12
        if i < 27:
            continue

        todayEMA26 = (data['Adj Close'][i] * (2 / (1 + 26))) + yesterdayEMA26 * (1 - (2 / (1 + 26)))
        todayMACD = todayEMA12 - todayEMA26
        yesterdayEMA26 = todayEMA26

        if i == 27:
            yesterdaySignal = todayMACD
            continue

        todaySignal = (todayMACD * (2 / (1 + 9))) + yesterdaySignal * (1 - (2 / (1 + 9)))

        # Previous EMA values to calculate next EMA value
        yesterdaySignal = todaySignal

        # Array of MACD values
        arrayMACD[i] = todayMACD

        # Array of Signal (9 EMA of MACD)
        arraySignal[i] = todaySignal

    # Store Arrays into dataframe
    data['MACD'] = arrayMACD
    data['Signal'] = arraySignal

    # Plot Test

    print(arrayMACD)
    print(arraySignal)
    plt.plot(arrayMACD)
    plt.plot(arraySignal)
    plt.show()
    # Return the dataframe
    return data

def tradeSMA(df, short_sma, long_sma):
    position = 0
    counter = 0
    percentChange = []

    for i in df.index:
        SMA_short = df["SMA_" + str(short_sma)]
        SMA_long = df["SMA_" + str(long_sma)]
        close = df['Adj Close'][i]

        # buy
        if (SMA_short[i] > SMA_long[i]):
            if (position == 0):
                buyP = close  # buy price
                position = 1  # turn position

        # sell
        elif (SMA_short[i] < SMA_long[i]):
            if (position == 1):  # have a position in down trend
                position = 0  # selling position
                sellP = close  # sell price
                perc = (sellP / buyP - 1) * 100
                percentChange.append(perc)

        if (counter == df["Adj Close"].count() - 1 and position == 1):
            position = 0
            sellP = close
            perc = (sellP / buyP - 1) * 100
            percentChange.append(perc)
    counter += 1

    return percentChange

def tradeMACD(df):
    position = 0
    counter = 0
    percentChange = []

    for i in df.index:
        close = df['Adj Close'][i]

        # buy
        if (df['MACD'][i] > df['Signal'][i]):
            if (position == 0):
                buyP = close  # buy price
                position = 1  # turn position

        # sell
        elif (df['MACD'][i] < df['Signal'][i]):
            if (position == 1):  # have a position in down trend
                position = 0  # selling position
                sellP = close  # sell price
                perc = (sellP / buyP - 1) * 100
                percentChange.append(perc)

        if (counter == df["Adj Close"].count() - 1 and position == 1):
            position = 0
            sellP = close
            perc = (sellP / buyP - 1) * 100
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
        if (i > 0):
            gains += i
            numGains += 1
        else:
            losses += i
            numLosses += 1
        totReturn = totReturn * ((i / 100) + 1)

    totReturn = round((totReturn - 1) * 100, 2)
    totTrades = numGains + numLosses

    return totTrades, totReturn


def SMA(start, end, stock, short_sma, long_sma, plot=False):
    df = loadStocks(start, end, stock)
    df_updated, SMAs = findSMA(short_sma, long_sma, df)
    percentChange = tradeSMA(df_updated, short_sma, long_sma)

    if plot == True:
        mpf.plot(df, type='ohlc', figratio=(16, 6),
                 mav=(short_sma, long_sma),
                 # volume=True, title= str(stock),
                 style='mike')

    # print(df_updated)
    return calcReturn(percentChange, df_updated)

def MACD(start, end, stock):
    df = loadStocks(start, end, stock)
    df = findMACD(df)
    percentChange = tradeMACD(df)

    return calcReturn(percentChange, df)

def main():
    start = ['2010-01-01', '2020-01-01']
    end = ['2020-01-01', '2020-03-01']
    stocks = ['SPY', 'VGT', 'XLV']
    short_sma = [10, 20, 30]
    long_sma = [50, 60, 70, 80]
    print(MACD(start[0], end[0], stocks[2]))
    SMA(start[0], end[0], stocks[0], short_sma[0], long_sma[0], True)

main()
