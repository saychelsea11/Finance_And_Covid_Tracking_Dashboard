# Imports

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
from datetime import date, datetime
import locale
locale.setlocale(locale.LC_ALL, '')
import helper_functions as hp

"""# Important economic indicators

- https://www.finra.org/investors/insights/key-economic-indicators-every-investor-should-know

- https://www.investopedia.com/articles/personal-finance/020215/top-ten-us-economic-indicators.asp

- https://www.discoveroptions.com/mixed/content/education/articles/bigthreeeconomicindicators.html

# Scraping interest rates - *Nerdwallet*
https://www.nerdwallet.com/blog/mortgages/current-interest-rates/
"""

req = requests.get("https://www.nerdwallet.com/blog/mortgages/current-interest-rates/")
bs = BeautifulSoup(req.content,'lxml')
#bs = bs.prettify()
search = bs.find_all('td')

int_rates = pd.DataFrame()
dates = []
year_30 = []
year_15 = []
apr = []
count = 0

for i in search[:1544]:
  if i.get('class')[0] == 'column-1':
    dates.append(i.text)
    continue
  if i.get('class')[0] == 'column-2':
    year_30.append(i.text)
    continue
  if i.get('class')[0] == 'column-3':
    year_15.append(i.text)
    continue
  if i.get('class')[0] == 'column-4':
    apr.append(i.text)
    continue

int_rates['Date'] = dates
int_rates['Date'] = int_rates['Date'].apply(lambda x: pd.to_datetime(x))
int_rates['30-year rate'] = year_30
int_rates['30-year rate'] = int_rates['30-year rate'].str.extract('(\d\D\d\d)')
int_rates['30-year rate'] = int_rates['30-year rate'].apply(float)
int_rates['15-year rate'] = year_15
int_rates['15-year rate'] = int_rates['15-year rate'].str.extract('(\d\D\d\d)')
int_rates['15-year rate'] = int_rates['15-year rate'].apply(float)
int_rates['APR'] = apr
int_rates['APR'] = int_rates['APR'].str.extract('(\d\D\d\d)')
int_rates['APR'] = int_rates['APR'].apply(float)
int_rates.index = int_rates['Date']
print (int_rates.head(5))
#search

"""# Scraping real-time values for major financial indexes - *Yahoo Finance*
https://finance.yahoo.com/
"""

req = requests.get("https://finance.yahoo.com/")
bs = BeautifulSoup(req.content)
search = bs.find_all('script')
#script = bs.find("script",text=re.compile("root.App.main")).text
script = str(bs.find("script",text=re.compile("root.App.main")))

"""Note: In the code above, **"bs.find("script",text=re.compile("root.App.main")).text"** seemed to return an empty string for some users which could be an issue with the *Python* or *BeautifulSoup* version. 

A fix for this was to use the *str()* function instead of *.text*.

https://stackoverflow.com/questions/39631386/how-to-understand-this-raw-html-of-yahoo-finance-when-retrieving-data-using-pyt
"""

index_futures = ['S&P Futures','Dow Futures','Nasdaq Futures','Russell 2000 Futures','Crude Oil','10-Yr Bond','FTSE 100']
index = ['S&P 500','Dow 30','Nasdaq','Russell 2000','Crude Oil','10-Yr Bond','FTSE 100']

others = ['Gold','Silver','EUR/USD','Nikkei 225','GBP/USE']
price_type = ['regularMarketPrice','regularMarketPreviousClose']
value_curr = []
value_prev = []
value_ch_percent = []
value_ch = []
count = 0

#Checking if the index name has 'Futures'
quotes = script[script.find('quoteData'):script.find('quoteData')+20000]
price = quotes[quotes.find('S&P 500'):quotes.find('S&P 500')+8000]
current = price[price.find('regularMarketPrice'):price.find('regularMarketPrice')+500]

if len(current) == 0: 
  index_list = index_futures
else: 
  index_list = index

for i in index_list:
  count = count + 1
  price_curr,price_prev,price_change,price_change_percent = hp.extract_index_price(script,i)
  value_curr.append(price_curr)
  value_prev.append(price_prev)
  value_ch_percent.append(price_change_percent)
  value_ch.append(price_change)

indexes = pd.DataFrame()
indexes['Index'] = index_list
indexes['Current'] = value_curr
indexes['Current'] = indexes['Current'].apply(float)
indexes['Prev Close'] = value_prev
indexes['Prev Close'] = indexes['Prev Close'].apply(float)
indexes['Change'] = value_ch
indexes['Change'] = indexes['Change'].apply(float).apply(float)
#indexes['Change Percent'] = value_ch_percent
#indexes['Change Percent'] = indexes['Change Percent'].apply(float)
indexes['Change Percent'] = ((indexes['Current'] - indexes['Prev Close'])/indexes['Prev Close'])*100
indexes.index = indexes['Index']
print (indexes.head())

"""# Scraping Covid cases data - *Worldometer*
https://www.worldometers.info/coronavirus/country/us/
"""

req = requests.get("https://www.worldometers.info/coronavirus/country/us/")
bs = BeautifulSoup(req.content)

div = bs.find_all('div')
cov_data = []

for i in div:
  if i.get('id') == "maincounter-wrap":
    cov_data.append(i)

cases = cov_data[0].find('h1')
cases = cases.text
cases_val = cov_data[0].find('span')
cases_val = cases_val.text

deaths = cov_data[1].find('h1')
deaths = deaths.text
deaths_val = cov_data[1].find('span')
deaths_val = deaths_val.text


rec = cov_data[2].find('h1')
rec = rec.text 
rec_val = cov_data[2].find('span')
rec_val = rec_val.text 

print (cases,':',cases_val)
print (deaths,':',deaths_val)
print (rec,':',rec_val)

cases = {'Cases':cases_val,'Deaths':deaths_val,'Recoveries':rec_val}

"""# Scraping Covid vaccinations data - *New York Times*

https://www.nytimes.com/interactive/2020/us/covid-19-vaccine-doses.html
"""

req = requests.get("https://www.nytimes.com/interactive/2020/us/covid-19-vaccine-doses.html")
bs = BeautifulSoup(req.content)
search = bs.find_all('td')

vac_labels = {'Atleast one shot':'g-cell-color','Two shots':'g-border-r','Doses shipped':'distributed','Total shots given':'g-hide-mobile',
              'Doses used':'g-sm'}
              
vac_flag = [0,0,0,0,0]

atl_one_shot = 0
two_shots = 0
doses_del = 0
shots_given = 0
doses_used = 0

for i in search: 
  cls = i.get('class')

  #The class names seem to have changed on the website so had to create an alternative parsing method by looking at different keywords in the class
  if cls[-2] == 'g-at-least-one':
    if vac_flag[0] == 0:
        atl_one_shot = i.text
        vac_flag[0] = 1
    else: 
        pass
  if cls[-2] == 'g-fully-vaccinated':
    if vac_flag[1] == 0:
        two_shots = i.text
        vac_flag[1] = 1
    else: 
        pass
  if cls[-2] == 'distributed':
    if vac_flag[2] == 0:
        doses_del = i.text
        vac_flag[2] = 1
    else: 
        pass
  if cls[-2] == 'given':
    if vac_flag[3] == 0:
        shots_given = i.text
        vac_flag[3] = 1
    else: 
        pass
  if cls[-2] == 'pct_doses_given':
    if vac_flag[4] == 0:
        doses_used = i.text
        vac_flag[4] = 1
    else: 
        pass
  if sum(vac_flag) == 5:
    break
    
vac_values = [atl_one_shot,two_shots,doses_del,shots_given,doses_used]
vac_values = list(map(str.strip,vac_values))

print ("At least 1 shot given: ",vac_values[0])
print ("Two shots given: ",vac_values[1])
print ("Total doses delivered: ",vac_values[2])
print("Total shots given: ",vac_values[3])
print("Doses used: ",vac_values[4])

"""Note: The html text for the *class* attribute seemed to have changed on the NYT website. So the text used for parsing needed to be changed. The previous code containing the older parsing method is also shown above but commented out.

# Extracting VIX Volatility Index data - *Yahoo Finance API*

### VIX Volatility Index
"""

vix = yf.Ticker("^VIX")

# get stock info
print ("VIX Volatility Data")
print ()
print ("Regular market price", vix.info['regularMarketPrice'])
print ("Regular market price previous close",vix.info['regularMarketPreviousClose'])
print ("Regular market price market open",vix.info['regularMarketOpen'])
print ("Day high",vix.info['dayHigh'])
print ("Day low",vix.info['dayLow'])
print ("52-week high",vix.info['fiftyTwoWeekHigh'])
print ("52-week low",vix.info['fiftyTwoWeekLow'])

"""# Scraping Treasury Yield Data - YCharts
- https://ycharts.com/indicators/1_month_treasury_rate
- https://ycharts.com/indicators/3_month_treasury_rate
- https://ycharts.com/indicators/6_month_treasury_rate
- https://ycharts.com/indicators/1_year_treasury_rate
- https://ycharts.com/indicators/3_year_treasury_rate
- https://ycharts.com/indicators/5_year_treasury_rate
- https://ycharts.com/indicators/10_year_treasury_rate
- https://ycharts.com/indicators/20_year_treasury_rate
- https://ycharts.com/indicators/30_year_treasury_rate


"""

rate_1m, date_10 = hp.extract_treasury_rates('https://ycharts.com/indicators/1_month_treasury_rate')
rate_3m, date_10 = hp.extract_treasury_rates('https://ycharts.com/indicators/3_month_treasury_rate')
rate_6m, date_10 = hp.extract_treasury_rates('https://ycharts.com/indicators/6_month_treasury_rate')
rate_1, date_10 = hp.extract_treasury_rates('https://ycharts.com/indicators/1_year_treasury_rate')
rate_3, date_10 = hp.extract_treasury_rates('https://ycharts.com/indicators/3_year_treasury_rate')
rate_5, date_10 = hp.extract_treasury_rates('https://ycharts.com/indicators/5_year_treasury_rate')
rate_10, date_10 = hp.extract_treasury_rates('https://ycharts.com/indicators/10_year_treasury_rate')
rate_20, date_20 = hp.extract_treasury_rates('https://ycharts.com/indicators/20_year_treasury_rate')
rate_30, date_30 = hp.extract_treasury_rates('https://ycharts.com/indicators/30_year_treasury_rate')

df_rates = pd.DataFrame()
df_rates['1-mth'] = rate_1m.apply(float)
df_rates['3-mth'] = rate_3m.apply(float)
df_rates['6-mth'] = rate_6m.apply(float)
df_rates['1-yr'] = rate_1.apply(float)
df_rates['3-yr'] = rate_3.apply(float)
df_rates['5-yr'] = rate_5.apply(float)
df_rates['10-yr'] = rate_10.apply(float)
df_rates['20-yr'] = rate_20.apply(float)
df_rates['30-yr'] = rate_30.apply(float)

df_rates['date'] = date_10
df_rates.index = df_rates['date'].apply(pd.to_datetime)

df_rates.head()

yield_curve = df_rates.iloc[0,:-1]
print (yield_curve)

"""# Scraping unemployment rates - U.S. Bureau of Labor Statistics
https://data.bls.gov/timeseries/LNS14000000
"""

req = requests.get('https://data.bls.gov/timeseries/LNS14000000')
bs = BeautifulSoup(req.content,'lxml')
search = bs.find_all('td')

count = 0
years = 0
time_list = []
rates = []
dates = []

for i in search[6:]:
  count = count + 1
  time_list.append(count)
  rates.append(i.text)
  if count == 12: 
    years = years + 1
    count = 0 

year_list = []
for i in range(datetime.today().year-years+1,datetime.today().year+1):
  year_list.extend([i]*12)

count = 0
for i in rates: 
  dates.append(pd.to_datetime(str(time_list[count])+'/1/'+str(year_list[count])))
  count = count + 1

df_unemp_rate = pd.DataFrame()
df_unemp_rate['date'] = dates
df_unemp_rate['unemployment_rate_percent'] = rates  
df_unemp_rate['unemployment_rate_percent'] = df_unemp_rate['unemployment_rate_percent'].str.strip()
df_unemp_rate['unemployment_rate_percent'] = df_unemp_rate['unemployment_rate_percent'].replace('',np.nan)
df_unemp_rate['unemployment_rate_percent'] = df_unemp_rate['unemployment_rate_percent'].apply(float)

df_unemp_rate.index = df_unemp_rate['date']
df_unemp_rate = df_unemp_rate.dropna()
print (df_unemp_rate.head())

"""# Scraping GDP data - U.S. Inflation Calculator
https://www.usinflationcalculator.com/inflation/historical-inflation-rates/
"""

req = requests.get('https://www.usinflationcalculator.com/inflation/historical-inflation-rates/')
bs = BeautifulSoup(req.content,'lxml')
search = bs.find_all('td')

count = 0
years = 0
time_list = []
rates = []
dates = []

for i in search:
  count = count + 1
  if count == 13:
    years = years + 1
    count = 0 
    continue
  time_list.append(count)
  rates.append(i.text)

time_list = time_list[:-6]
rates = rates[:-6]

year_list = []
for i in range(datetime.today().year-years+1,datetime.today().year+1):
  year_list.extend([i]*12)

count = 0
for i in rates: 
  dates.append(pd.to_datetime(str(time_list[count])+'/1/'+str(year_list[count])))
  count = count + 1

df_inflation = pd.DataFrame()
df_inflation['date'] = dates
df_inflation['inflation_rate'] = rates  
df_inflation['inflation_rate'] = df_inflation['inflation_rate'].str.strip()
df_inflation['inflation_rate'] = df_inflation['inflation_rate'].replace('',np.nan)
df_inflation['inflation_rate'] = df_inflation['inflation_rate'].apply(float)

df_inflation.index = df_inflation['date']
df_inflation = df_inflation.dropna()
print (df_inflation.head())

"""# Scraping Gross Domestic Product (GDP) - Multpl
https://www.multpl.com/us-gdp-inflation-adjusted/table/by-year
"""

req = requests.get('https://www.multpl.com/us-gdp-inflation-adjusted/table/by-year')
bs = BeautifulSoup(req.content,'lxml')
search = bs.find_all('td')

dates = []
gdp = []

count = 0

for i in search: 
  count = count + 1
  if count == 1:
    dates.append(i.text)
  if count == 2: 
    gdp.append(i.text)
    count = 0

df_gdp = pd.DataFrame()
df_gdp['date'] = dates
df_gdp['date'] = df_gdp['date'].apply(pd.to_datetime)
df_gdp['gdp'] = gdp
df_gdp['gdp'] = df_gdp['gdp'].str.strip()
df_gdp['gdp'] = df_gdp['gdp'].str.extract('(\d+\D\d+)')
df_gdp['gdp'] = df_gdp['gdp'].apply(float)
df_gdp.index = df_gdp['date']
print (df_gdp.head())

"""# Calculating Buffet Indicator

https://www.gurufocus.com/stock-market-valuations.php

https://www.gurufocus.com/shiller-PE.php

https://www.multpl.com/shiller-pe

##### $Buffet$ $indicator$ = $U.S.$ $Equity$ $Market$ $Value$ $/$ $U.S.$ $GDP$

1. Scraping Market Value of U.S. Stock Market - Siblis Research

https://siblisresearch.com/data/us-stock-market-value/#:~:text=The%20total%20market%20capitalization%20of,about%20OTC%20markets%20from%20here.

2. U.S. GDP - Extracted in the GDP section of this notebook
"""

#Extracting the U.S. total market value
req = requests.get('https://siblisresearch.com/data/us-stock-market-value/#:~:text=The%20total%20market%20capitalization%20of,about%20OTC%20markets%20from%20here.')
bs = BeautifulSoup(req.content,'lxml')
search = bs.find_all('td')

us_market_val = float(search[1].text.replace(',',''))*1000000
print ("U.S. Equity Maret Cap: $",us_market_val)
print ("U.S. GDP: $",df_gdp['gdp'].iloc[0]*1000000000000)

#Calculating Buffet Indicator
buffet_ind = np.round((us_market_val/(df_gdp['gdp'].iloc[0]*1000000000000))*100,2)
print ("Buffet indicator: ",buffet_ind,"%")

"""# Extracting Shiller PE Ratio

https://www.gurufocus.com/shiller-PE.php

https://www.multpl.com/shiller-pe
"""

#Extracting Shiller PE ratio
req = requests.get('https://www.multpl.com/shiller-pe')
bs = BeautifulSoup(req.content,'lxml')
search = bs.find_all('meta')

shiller_pe = float(re.findall('(\d+\d+.\d+\d+)',search[1].get('content'))[0])
print ("Shiller PE Ratio: ",shiller_pe)

"""# FINRA Margin Debt

https://www.finra.org/investors/learn-to-invest/advanced-investing/margin-statistics

https://www.advisorperspectives.com/dshort/updates/2021/08/12/margin-debt-and-the-market-down-4-3-in-july-first-decline-in-15-months
"""

req = requests.get('https://www.finra.org/investors/learn-to-invest/advanced-investing/margin-statistics')
bs = BeautifulSoup(req.content,'lxml')
search = bs.find_all('td')

date = []
debt = []

for i in search:
  #print (i)
  if "Month/Year" in i.get('data-th'):
    date.append(i.text)
  if "Debit Balances" in i.get('data-th'):
    debt.append(i.text)

df_debt = pd.DataFrame()
df_debt['date'] = date
#df_debt['date'] = df_debt['date'].apply(pd.to_datetime())
df_debt['debt'] = debt
df_debt['debt'] = df_debt['debt'].apply(lambda x: int(x.replace(',','')))
latest_data = df_debt[df_debt['date'].str.contains(r'-21')]

print ("Latest Margin Debt Data: ",list(latest_data['date'])[-1], ", $" + str(list(latest_data['debt'])[-1]*1000000))

print (df_debt.head())

"""### Dashboard"""

hp.dash_create()

