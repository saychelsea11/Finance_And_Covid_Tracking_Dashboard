import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings("ignore")
import re
import requests
from bs4 import BeautifulSoup
from datetime import date, datetime
import json
  
def extract_treasury_rates(url):
    req = requests.get(url)
    bs = BeautifulSoup(req.content,'lxml')
    search = bs.find_all('table')

    cols_list = []
    df_date = []
    df_1mo = []
    df_3mo = []
    df_6mo = []
    df_1yr = []
    df_3yr = []
    df_5yr = []
    df_10yr = []
    df_20yr = []
    df_30yr = []
    count = 0

    data = search[0].find_all('td')

    for j in data:
        count = count + 1
        if count == 1:
            df_date.append(j.text)
        elif count == 9:
            df_1mo.append(float(j.text.strip()))
        elif count == 11: 
            df_3mo.append(float(j.text.strip()))
        elif count == 12: 
            df_6mo.append(float(j.text.strip()))
        elif count == 13: 
            df_1yr.append(float(j.text.strip()))
        elif count == 15: 
            df_3yr.append(float(j.text.strip()))
        elif count == 16: 
            df_5yr.append(float(j.text.strip()))
        elif count == 18: 
            df_10yr.append(float(j.text.strip()))
        elif count == 19: 
            df_20yr.append(float(j.text.strip()))
        elif count == 20: 
            df_30yr.append(float(j.text.strip()))
            count = 0

    df_rates = pd.DataFrame()
    df_rates['1mo'] = df_1mo
    df_rates['3mo'] = df_3mo
    df_rates['6mo'] = df_6mo
    df_rates['1yr'] = df_1yr
    df_rates['3yr'] = df_3yr
    df_rates['5yr'] = df_5yr
    df_rates['10yr'] = df_10yr
    df_rates['20yr'] = df_20yr
    df_rates['30yr'] = df_30yr
    df_rates = df_rates
    df_rates['Date'] = df_date

    df_rates.index = df_rates['Date'].apply(pd.to_datetime)
    df_rates = df_rates.drop('Date',axis=1)

    return df_rates

# Commented out IPython magic to ensure Python compatibility.
def dash_create(df_unemp_rate,df_gdp,df_inflation,df_rates,yield_curve,vix,indexes,cases,vac_values,vac_labels,buffet_ind,
              shiller_pe,df_debt,latest_data):
  plt.rcParams.update(plt.rcParamsDefault)
#   %matplotlib inline
  plt.style.use('bmh')

  fig3 = plt.figure(constrained_layout=True,figsize=(42,22))
  gs = fig3.add_gridspec(40,3)

  f3_ax1 = fig3.add_subplot(gs[0:10,0])
  plt.plot(df_unemp_rate['unemployment_rate_percent'],alpha=0.8,label='Unemployment rate (%)',color='green')
  plt.plot(df_inflation.iloc[df_inflation.index>'2011']['inflation_rate'],alpha=0.8,label='Inflation rate (%)',color='blue')
  plt.xticks(rotation=0,size=20)
  plt.xlabel('Timeline',size=25)
  plt.yticks(size=20)
  plt.ylabel('Rate (%)',size=25)
  plt.title('Critical Economic Indicators',size=30)
  #plt.axis('off')
  plt.legend(prop={'size':15})

  f3_ax2 = fig3.add_subplot(gs[11:21,0])
  plt.plot(df_gdp.iloc[df_gdp.index>'2011']['gdp'],marker='o',alpha=0.8,label='GDP',color='orange')
  plt.xticks(rotation=15,size=20)
  plt.xlabel('Timeline',size=25)
  plt.yticks(size=20)
  plt.ylabel('$ (Trillion)',size=25)
  plt.legend(prop={'size':15})

  f3_ax3 = fig3.add_subplot(gs[0:10,1])
  plt.plot(df_rates['1mo'],label=df_rates.columns[0],alpha=1)
  plt.plot(df_rates['3mo'],label=df_rates.columns[1],alpha=1)
  plt.plot(df_rates['6mo'],label=df_rates.columns[2],alpha=1)
  plt.plot(df_rates['1mo'],label=df_rates.columns[3],alpha=1)
  plt.plot(df_rates['3yr'],label=df_rates.columns[4],alpha=1)
  plt.plot(df_rates['5yr'],label=df_rates.columns[5],alpha=1)
  plt.plot(df_rates['10yr'],label=df_rates.columns[6],alpha=1)
  plt.plot(df_rates['20yr'],label=df_rates.columns[7],alpha=1)
  plt.plot(df_rates['30yr'],label=df_rates.columns[8],alpha=1)
  plt.xticks(rotation=30,size=20)
  plt.xlabel('Timeline',size=25)
  plt.yticks(size=20)
  plt.ylabel('Rate (%)',size=25)
  plt.title('U.S. Treasury Yield Rates and Yield Curve',size=30)
  #plt.axis('off')
  plt.legend(loc='upper left',prop={'size':15})

  f3_ax3 = fig3.add_subplot(gs[11:21,1])
  plt.plot(yield_curve,marker='o')
  plt.xticks(yield_curve.index,rotation=15,size=20)
  plt.yticks(size=20)
  plt.ylabel('Rate (%)',size=25)
  plt.xlabel('Treasury Security',size=25)
  
  #vix_data = {"MarketPrice":vix.info['regularMarketPrice'],"PreviousClose":vix.info['regularMarketPreviousClose'],"MarketOpen":vix.info['regularMarketOpen'],"DayHigh":vix.info['dayHigh'],"DayLow":vix.info['dayLow']}
  f3_ax4 = fig3.add_subplot(gs[0:10,2])  
  plots = sns.barplot(y="Change Percent", x="Index", data=indexes,alpha=0.8) 
    
  # Iterrating over the bars one-by-one 
  for bar in plots.patches: 
    # Using Matplotlib's annotate function and 
    # passing the coordinates where the annotation shall be done 
    # x-coordinate: bar.get_x() + bar.get_width() / 2 
    # y-coordinate: bar.get_height() 
    # free space to be left to make graph pleasing: (0, 8) 
    # ha and va stand for the horizontal and vertical alignment 
      plots.annotate(format(bar.get_height(), '.2f'),  
                    (bar.get_x() + bar.get_width() / 2,bar.get_height()+0.6), ha='center', va='center', 
                    size=20, xytext=(0,8), 
                    textcoords='offset points')  
  plt.xlabel('Index',size=25)
  plt.ylabel('Change (%)',size=25)
  plt.title('Major Indexes and Assets',size=30)
  #plt.axis('off')
  plt.xticks(size=20,rotation=15)
  plt.yticks(size=20)

  f3_ax4 = fig3.add_subplot(gs[11:21,2])  
  plots = sns.barplot(y="Current", x="Index", data=indexes,alpha=0.8) 
    
  # Iterrating over the bars one-by-one 
  for bar in plots.patches: 
    # Using Matplotlib's annotate function and 
    # passing the coordinates where the annotation shall be done 
    # x-coordinate: bar.get_x() + bar.get_width() / 2 
    # y-coordinate: bar.get_height() 
    # free space to be left to make graph pleasing: (0, 8) 
    # ha and va stand for the horizontal and vertical alignment 
      plots.annotate(format(bar.get_height(), '.2f'),  
                    (bar.get_x() + bar.get_width() / 2,bar.get_height()+0.6), ha='center', va='center', 
                    size=20, xytext=(0,8), 
                    textcoords='offset points')  
  plt.xlabel('Index',size=25)
  plt.ylabel('Current Value',size=25)
  #plt.title('Major Indexes (current value)',size=25)
  #plt.axis('off')
  plt.xticks(size=20, rotation=15)
  plt.yticks(size=20)

  #vix_data = {"MarketPrice":vix.info['regularMarketPrice'],"PreviousClose":vix.info['regularMarketPreviousClose'],"MarketOpen":vix.info['regularMarketOpen'],"DayHigh":vix.info['dayHigh'],"DayLow":vix.info['dayLow']}

  #df_vix = pd.DataFrame()
  #df_vix['Stat'] = list(vix_data.keys())
  #df_vix['Value'] = list(vix_data.values())

  f3_ax5 = fig3.add_subplot(gs[22:40,0])

  valuation_metric_names = ["VIX Index","Buffet Indicator","Shiller PE Ratio","Margin Debt"]
  valuation_metric_values = [vix,'{}%'.format(buffet_ind),shiller_pe,'${:n}B'.format(list(latest_data['debt'])[-1])]

  x = [1.8,1.8,4.2,4.2]
  y = [24,-22,24,-22]
  color = ['mediumaquamarine','mediumorchid','brown','orange']
  count = 0
  plt.scatter(x,y,s=67000,alpha=0.6,marker='s',c=color,edgecolors='black')
  for i,j in zip(x,y):
    plt.annotate(valuation_metric_names[count],xy=(i-0.5,j),size=25)
    plt.annotate(valuation_metric_values[count],xy=(i-0.5,j-5),size=30)
    count = count + 1
  plt.axis('off')
  plt.xlim(0,6)
  plt.xticks(size=25)
  plt.ylim(-50,50)
  plt.title('Market Valuation Metrics',size=30)

  f3_ax6 = fig3.add_subplot(gs[22:40,1])
  x = [2,3,4]
  y = [19,-21,19]
  c = ['blue','red','blue']
  count = 0
  plt.scatter(x,y,s=72000,alpha=0.3,c='red',edgecolors='black')
  for i,j in zip(x,y):
    plt.annotate(list(cases.keys())[count],xy=(i-0.5,j),size=25)
    plt.annotate(list(cases.values())[count],xy=(i-0.5,j-5),size=30)
    count = count + 1
  plt.axis('off')
  plt.xlim(0,6)
  plt.xticks(size=20)
  plt.ylim(-50,50)
  plt.title('COVID-19 Cases',size=30)

  f3_ax7 = fig3.add_subplot(gs[22:40,2])
  x = [1,2,3,4,5]
  y = [19,-21,19,-21,19]
  c = ['blue','red','blue','red','blue']
  count = 0
  plt.scatter(x,y,s=72000,alpha=0.3,c='green',edgecolors='black')
  for i,j in zip(x,y):
    plt.annotate(list(vac_labels.keys())[count],xy=(i-0.5,j),size=25)
    plt.annotate(vac_values[count],xy=(i-0.5,j-5),size=30)
    count = count + 1
  plt.axis('off')
  plt.xlim(0,6)
  plt.xticks(size=25)
  plt.ylim(-50,50)
  plt.title('COVID-19 Vaccinations',size=30)

  plt.tight_layout(pad=4)
  
  #Executing Streamlit's 'pyplot' command to create plots using the 'matplotlib' framework
  st.pyplot(fig3)
  
  #plt.show()
  
def extract_stock_info(ticker):
  url = "https://yh-finance.p.rapidapi.com/stock/v2/get-summary"

  querystring = {"symbol":ticker,"region":"US"}

  headers = {
      'x-rapidapi-host': "yh-finance.p.rapidapi.com",
      'x-rapidapi-key': "c8c32e16cdmsh40250af4d5c9cb6p17932cjsna77272b10ac1"
      }
      
  response = requests.request("GET", url, headers=headers, params=querystring)
  data = json.loads(response.text)

  return data