import yfinance as yf
import datetime as datetime
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from plotly.subplots import make_subplots
#NOTE: 
# df['Datetime'] becomes df['Date'] when using an interval other than the minute intervals, when using hourly intervals it's empty so use 6m as interval instead
# yfinance only provides 1m data for the last 30 days
# Make sure date entered was an open market day (No weekends/holidays)

#Data functions
def isSupport(df, i):
    return df['Low'][i] < df['Low'][i-1] and df['Low'][i] < df['Low'][i-+1] and df['Low'][i+1] < df['Low'][i+2] and df['Low'][i-1] < df['Low'][i-2]

def isResitance(df, i):
    return df['High'][i] > df['High'][i-1] and df['High'][i] > df['High'][i-+1] and df['High'][i+1] > df['High'][i+2] and df['High'][i-1] > df['High'][i-2]

def isNotOverlap(val, lines, df):
    ave  = np.mean(df['High'] - df['Low'])
    return np.sum([abs(val-line) < ave for line in lines]) == 0   #True is returned if the value between two given lines is less than the mean of the length of candles in the dataset

allowedDifference = .2  #Currently testing, should make this user input or some kind of calculated average later on. Best results so far have been between .15 and .30
def isCommon(lines1,lines2,lines3):
    common = []
    for i in range(len(lines1)):
        for y in range(len(lines2)):
            for j in range(len(lines3)):
                if lines1[i][1] < lines2[y][1]+allowedDifference and lines1[i][1] > lines2[y][1]-allowedDifference:
                    if  lines1[i][1] < lines3[j][1]+allowedDifference and lines1[i][1] > lines3[j][1]-allowedDifference:
                        if  lines2[y][1] < lines3[j][1]+allowedDifference and lines2[y][1] > lines3[j][1]-allowedDifference:
                            common.append(lines1[i])
    return common

def numOfSubplots(fig2):
    count=0
    for i in fig2.layout:
        if i.startswith('xaxis'):
            count += 1
    return count

def getLines(df):
    lines = []
    for i in range (2,df.shape[0]-2):
        if isSupport(df, i):
            low = df['Low'][i]
            if isNotOverlap(low, lines, df):
                lines.append((i, low))
        elif isResitance(df, i):
            high = df['High'][i]
            if isNotOverlap(high, lines, df):
                lines.append((i, high))
    return lines

def drawLines(subplot):
    commonLines = isCommon(getLines(pd.read_csv(csvArr2[0])), getLines(pd.read_csv(csvArr2[1])), getLines(pd.read_csv(csvArr2[2])))
    for i in getLines(pd.read_csv(csvArr2[subplot-1])):
            if i in commonLines:
                fig2.add_hline(y=i[1], row= subplot, col=1, line_color="green")
            else:
                fig2.add_hline(y=i[1], row= subplot, col=1, line_color="black")

#Take input and parse it
ticker = input("Enter Stock Ticker: ")
date = input("Enter Date (MM-DD-YYYY): ")
month = int(date[:2])
day = int(date[3:5])
year = int(date[6:10])
ticker = yf.Ticker(ticker)
start = datetime.datetime(2022, month, day, 9, 30, 0)
end = datetime.datetime(2022, month, day, 16, 0, 0)

#Create CSV's based on the ticker and dates provided
ticker.history(start=start, end=end, interval="1m").to_csv('1myahoo.csv')
ticker.history(start=start, end=end, interval="2m").to_csv('2myahoo.csv')
ticker.history(start=start, end=end, interval="5m").to_csv('5myahoo.csv')
csvArr2 = ['1myahoo.csv','2myahoo.csv','5myahoo.csv']

#Chart creation using plotly
fig2 = make_subplots(rows=3, cols=1)
fig2.update_xaxes(rangeslider_visible=False)
fig2.update_layout(height=1000, width=1000)

df = pd.read_csv('1myahoo.csv')
fig2.append_trace(go.Candlestick(x=df['Datetime'], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close']), row=1, col=1)
df = pd.read_csv('2myahoo.csv')
fig2.append_trace(go.Candlestick(x=df['Datetime'], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close']), row=2, col=1)
df = pd.read_csv('5myahoo.csv')
fig2.append_trace(go.Candlestick(x=df['Datetime'], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close']), row=3, col=1)

#Loop to create supp/res lines for each subplot
for m in range(numOfSubplots(fig2)):
    drawLines(m+1)

fig2.show()