import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import mplfinance as mpf

def loadStocks(start, end, stock):
    df = yf.download(stock, start, end, interval='1d')
    return df

def findMFI(high, low, close, volume, time_window):
    tp = (high + low + close)/3
    rmf = tp * volume

    diff = rmf.diff(1).dropna()

    pmf = 0 * diff
    nmf = 0 * diff

    # up change
    pmf[diff > 0] = diff[diff > 0]
    pmf_avg = pmf.ewm(com=time_window - 1, min_periods=time_window).mean()

    # down change
    nmf[diff < 0] = diff[diff < 0]
    nmf_avg = nmf.ewm(com=time_window - 1, min_periods=time_window).mean()

    # mfi
    mfr = abs(pmf_avg / nmf_avg)
    mfi = 100 - 100 / (1 + mfr)

    return mfi

def tradeMFI(df, high, low):
    position = 0
    counter = 0
    percentChange = []

    for i in df.index:
        mfi = df['MFI']
        close = df['Adj Close'][i]

        # buy
        if (mfi[i] < low):
            if (position == 0):
                position = 1  # buy position
                buyP = close  # buy price

        # sell
        elif (mfi[i] > high):
            if (position == 1):
                position = 0  # sell position
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

def MFI(start, end, stock, low, high, plot=False):
    df = loadStocks(start, end, stock)
    df['MFI'] = findMFI(df['High'], df['Low'], df['Adj Close'], df['Volume'], 14)
    percentChange = tradeMFI(df, high, low)

    # need to change lines bc mav is moving average
    if plot == True:
        lowarray = [low] * len(df.index)
        higharray = [high] * len(df.index)
        mfi = df['MFI']
        mfiarray = []
        for i in df.index:
            mfiarray.append(mfi[i])

        fig = plt.figure(num=1, clear=True)
        ax = fig.add_subplot(1, 1, 1)
        ax.plot(mfiarray)
        ax.plot(lowarray, 'g-')
        ax.plot(higharray, 'r-')
        plt.show()

    return calcReturn(percentChange, df)

def main():
    start = ['2010-01-01']
    end = ['2020-01-01']
    stocks = ['SPY', 'VGT', 'XLV']
    mfi_low = 45
    mfi_high = 70

    results = MFI(start[0], end[0], stocks[0], mfi_low, mfi_high)
    print(results)

    return 0

main()
