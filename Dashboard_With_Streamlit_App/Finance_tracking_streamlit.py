#!/usr/bin/env python
# coding: utf-8

# # Installations and imports

# In[ ]:


#pip install yfinance


# In[1]:


import streamlit as st
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import requests
import json
import matplotlib.pyplot as plt
import re
import pprint
import warnings
warnings.filterwarnings("ignore")
import yfinance as yf
import seaborn as sns
from datetime import date,datetime
import locale
locale.setlocale(locale.LC_ALL, '')
import helper_functions_streamlit as hp


# In[2]:


st.write("""
## Financial Indexes, Economic Indicators and COVID-19 Statistics
#### Dashboard
""")


# # Important economic indicators
# 
# - https://www.finra.org/investors/insights/key-economic-indicators-every-investor-should-know
# 
# - https://www.investopedia.com/articles/personal-finance/020215/top-ten-us-economic-indicators.asp
# 
# - https://www.discoveroptions.com/mixed/content/education/articles/bigthreeeconomicindicators.html

# # Retrievng major index and asset values - *Yahoo Finance API*
# - S&P 500
# - Dow 30
# - Nasdaq
# - Russell 2000
# - Crude Oil
# - FTSE 100
# - Gold
# - Bitcoin

# In[3]:


indexes = ['S&P 500','Dow 30','Nasdaq','Russell 2000','Crude Oil','FTSE 100','Gold','Bitcoin']
tickers = ["^GSPC","^DJI","NQ=F","RTY=F","CL=F","^FTSE","GC=F","BTC-USD"]
df_index = hp.retrieve_indexes_and_assets(indexes,tickers)

print (df_index)


# # Scraping Covid cases data - *Worldometer*
# https://www.worldometers.info/coronavirus/country/us/

# In[4]:

url = "https://www.worldometers.info/coronavirus/country/us/"
cases = hp.extract_covid_cases(url)

print ("Cases",':',cases['Cases'])
print ("Deaths",':',cases['Deaths'])
print ("Recoveries",':',cases['Recoveries'])


# # Scraping Covid vaccinations data - *New York Times*
# 
# https://www.nytimes.com/interactive/2020/us/covid-19-vaccine-doses.html

# In[6]:


url = "https://www.nytimes.com/interactive/2020/us/covid-19-vaccine-doses.html"
vac_labels, vac_values = hp.extract_covid_vaccinations(url)

print ("At least one shot: ",vac_values[0])
print ("Two shots: ",vac_values[1])
print ("Booster shot: ",vac_values[2])
print("Total shots: ",vac_values[3])
print("Two shots 65+: ",vac_values[4])


# Note: The html text for the *class* attribute seemed to have changed on the NYT website. So the text used for parsing needed to be changed. The previous code containing the older parsing method is also shown above but commented out. 

# # Extracting VIX Volatility Index data - *Yahoo Finance API*

# ### VIX Volatility Index

# In[7]:


data = hp.extract_stock_info("^VIX")
vix = data['result']['regularMarketPrice']

# get stock info
print (vix)


# # Scraping Treasury Yield Data - YCharts
# 
# - https://www.treasury.gov/resource-center/data-chart-center/interest-rates/Pages/TextView.aspx?data=longtermrateAll
# - https://www.bloomberg.com/markets/rates-bonds/government-bonds/us

# In[8]:


df_rates = hp.extract_treasury_rates('https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_yield_curve&field_tdr_date_value_month=202203')

print (df_rates.head())

#hp.extract_treasury_rates('https://www.treasury.gov/resource-center/data-chart-center/interest-rates/pages/textview.aspx?data=yield')


# In[9]:s


yield_curve = df_rates.iloc[0,:-1]
print (yield_curve)


# # Scraping unemployment rates - U.S. Bureau of Labor Statistics
# https://data.bls.gov/timeseries/LNS14000000

# In[10]:


#Calling function to extract unemployment values
url = 'https://data.bls.gov/timeseries/LNS14000000'
df_unemp_rate = hp.extract_unemp_rate(url)

print (df_unemp_rate.head())


# # Scraping GDP data - U.S. Inflation Calculator
# https://www.usinflationcalculator.com/inflation/historical-inflation-rates/

# In[11]:

#Calling function to extract inflation data
url = 'https://www.usinflationcalculator.com/inflation/historical-inflation-rates/'
df_inflation = hp.extract_inflation_rate(url)

print (df_inflation.head())


# # Scraping Gross Domestic Product (GDP) - Multpl
# https://www.multpl.com/us-gdp-inflation-adjusted/table/by-year

# In[12]:


#Calling function to extract GDP data
url = 'https://www.multpl.com/us-gdp-inflation-adjusted/table/by-year'
df_gdp = hp.extract_gdp(url)

print (df_gdp.head())
    


# # Calculating Buffet Indicator
# 
# https://www.gurufocus.com/stock-market-valuations.php
# 
# https://www.gurufocus.com/shiller-PE.php
# 
# https://www.multpl.com/shiller-pe
# 
# ##### $Buffet$ $indicator$ = $U.S.$ $Equity$ $Market$ $Value$ $/$ $U.S.$ $GDP$
# 
# 1. Scraping Market Value of U.S. Stock Market - Siblis Research
# 
# https://siblisresearch.com/data/us-stock-market-value/#:~:text=The%20total%20market%20capitalization%20of,about%20OTC%20markets%20from%20here.
# 
# 2. U.S. GDP - Extracted in the GDP section of this notebook

# In[13]:


#Calling function to calculate Buffet Indicator after extracting US total market value
url = 'https://siblisresearch.com/data/us-stock-market-value/#:~:text=The%20total%20market%20capitalization%20of,about%20OTC%20markets%20from%20here.'
buffet_ind = hp.calculate_buffet_indicator(url,df_gdp)

print ("Buffet indicator: ",buffet_ind,"%")


# # Extracting Shiller PE Ratio
# 
# https://www.gurufocus.com/shiller-PE.php
# 
# https://www.multpl.com/shiller-pe

# In[14]:


#Calling function to extract Shiller PE value
url = 'https://www.multpl.com/shiller-pe'
shiller_pe = hp.extract_shiller_pe(url)

print ("Shiller PE Ratio: ",shiller_pe)


# # FINRA Margin Debt
# 
# https://www.finra.org/investors/learn-to-invest/advanced-investing/margin-statistics
# 
# https://www.advisorperspectives.com/dshort/updates/2021/08/12/margin-debt-and-the-market-down-4-3-in-july-first-decline-in-15-months

# In[15]:


#Calculating 
url = 'https://www.finra.org/investors/learn-to-invest/advanced-investing/margin-statistics'
df_debt, latest_data = hp.extract_debt_margin(url)

print ("Latest Margin Debt Data: ",list(latest_data['date'])[-1], ", $" + str(list(latest_data['debt'])[-1]*1000000))

print (df_debt.head())


# # Dashboard

# Creating a grid to display all the information

# In[16]:


hp.dash_create(df_unemp_rate,df_gdp,df_inflation,df_rates,yield_curve,vix,df_index,cases,vac_values,vac_labels,buffet_ind,
              shiller_pe,df_debt,latest_data)


# In[ ]:




