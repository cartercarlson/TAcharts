from TAcharts.py.utils import *
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
pd.plotting.register_matplotlib_converters()


class Ichimoku:
    def __init__(self, FILE='data/15min.csv', period=None):
        self.df = pd.read_csv(FILE)
        if period:
            self.df = group_candles(self.df, period)
        # self.date = [datetime.strptime(x, '%Y-%m-%d %H:%M:%S') for x in self.df['date']]
        # self.date = self.df['date'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S'))

        self.df['price'] = self.df['close'].shift(1)
        self.ichimoku = {}


    def build(self, tenkan_period, kijun_period, senkou_b_period, displacement):
        ''' Create Ichimoku data '''

        self._extend_dates(displacement)

        # Tenkan (conversion line) = (highest high + highest low)/2 for the past x periods
        # Kijun (base line) = (highest high + lowest low)/2 for the past x*3 periods
        self._build_lines(tenkan=tenkan_period, kijun=kijun_period)

        # Chikou (lagging span) = Current closing price time-shifted backwards x*3 periods
        # Senkou span A (leading span A) = (tenkan + kijun)/2 time-shifted forwards x*3 periods
        # Senkou span B (leading span B) = (highest high + lowest low)/2 for past x*6 periods, shifted forwards x*3 periods
        self._build_spans(senkou_b_period=senkou_b_period, displacement=displacement)
        return


    def _extend_dates(self, displacement):
        last_date = datetime.strptime(self.df['date'].iat[-1], '%Y-%m-%d %H:%M:%S')
        new_dates = [last_date + timedelta(days=i+1) for i in range(displacement)]
        self.df = self.df.append({'date': new_dates}, ignore_index=True, sort=False)
        return


    def _build_lines(self, **kwargs):
        for i in kwargs:
            high = self.df['high'].rolling(window=kwargs[i]).max()
            low = self.df['low'].rolling(window=kwargs[i]).min()
            self.ichimoku[i] = (high + low)/2
        return


    def _build_spans(self, senkou_b_period, displacement):
        self.ichimoku['chikou'] = self.df['price'].shift(-displacement)
        self.ichimoku['senkou_a'] = (self.ichimoku['tenkan'] + self.ichimoku['kijun']) / 2

        self._build_lines(senkou_b=senkou_b_period)

        self.ichimoku['senkou_a'] = self.ichimoku['senkou_a'].shift(displacement)
        self.ichimoku['senkou_b'] = self.ichimoku['senkou_b'].shift(displacement)
        return


    def plot(self):
        fig, ax = plt.subplots(figsize=(20,10))

        x = self.df['date']
        plt.plot(x, self.ichimoku['tenkan'], color='blue')
        plt.plot(x, self.ichimoku['kijun'], color='maroon')
        plt.plot(x, self.df['price'], color='black', linewidth=1)
        plt.plot(x, self.ichimoku['senkou_a'], color='green', linewidth=0.5)
        plt.plot(x, self.ichimoku['senkou_b'], color='red', linewidth=0.5)

        ax.set(xlabel='Month (2019)', ylabel='BTC price ($)')
        plt.rc('axes', labelsize=20)
        plt.rc('font', size=16)

        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
        plt.xticks(rotation=45)

        plt.fill_between(
            x, self.ichimoku['senkou_a'], self.ichimoku['senkou_b'],
            where=self.ichimoku['senkou_a'] >= self.ichimoku['senkou_b'],
            facecolor='limegreen',
            interpolate=True
        )
        plt.fill_between(
            x, self.ichimoku['senkou_a'], self.ichimoku['senkou_b'],
            where=self.ichimoku['senkou_a'] <= self.ichimoku['senkou_b'],
            facecolor='salmon',
            interpolate=True
        )
        return plt.show()


ichi = Ichimoku(period=96)
ichi.build(20, 60, 120, 30)


ichi.plot()