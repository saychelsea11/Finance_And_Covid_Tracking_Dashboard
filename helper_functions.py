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
import time

def extract_stock_info(ticker):
    url = "https://yahoofinance-stocks1.p.rapidapi.com/stock-metadata"

    querystring = {"Symbol":ticker}

    headers = {
        "X-RapidAPI-Key": "8df34c6c9fmshfbc86def7a396a8p11651djsna938a4c6a21a",
        "X-RapidAPI-Host": "yahoofinance-stocks1.p.rapidapi.com"
    }
    
    #Retrieving the stock data and converting to JSON format
    response = requests.request("GET", url, headers=headers, params=querystring)
    data = json.loads(response.text)

    return data

def retrieve_indexes_and_assets(indexes,tickers):
    index_current = []
    index_change = []
    df_index = pd.DataFrame()
    
    #Calling the extract_stock_info function for retrieving stock data
    #Extracting the open price, close price and then calculating the change percentage. The data is then stored in a dataframe. 
    for ticker in tickers: 
        data = extract_stock_info(ticker)
        market_price = data['result']['regularMarketPrice']
        market_price_open = data['result']['regularMarketOpen']
        index_current.append(market_price)
        index_change.append(((market_price - market_price_open)/market_price)*100)
        
        #Added 1.1sec of wait time between each API transaction due to the limit set by the source website
        time.sleep(1.1)

    df_index['Current Price'] = index_current
    df_index['Change Percent'] = index_change
    df_index['Index'] = indexes
    
    return (df_index)

def extract_covid_cases(url):
    req = requests.get(url)
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

    cases_dict = {'Cases':cases_val,'Deaths':deaths_val,'Recoveries':rec_val}
    
    return cases_dict

def extract_covid_vaccinations(url):
    req = requests.get(url)
    bs = BeautifulSoup(req.content)
    search = bs.find_all('td')

    vac_labels = {'Atleast one shot':'pct_given_shot','Two shots (all)':'g-fully-vaccinated','Booster shot':'g-additional',
                  'Total shots given':'g-hide-mobile','Two shots (65+)':'g-bar-col'}
    vac_flag = [0,0,0,0,0]
    atl_one_shot = 0
    two_shots = 0
    doses_del = 0
    shots_given = 0
    doses_used = 0
    count = 0

    for i in search: 
      cls = i.get('class')

      #The class names seem to have changed on the website so had to create an alternative parsing method by looking at different keywords in the class
      if cls[-1] == 'pct_given_shot':
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
      if cls[-1] == 'g-additional':
        if vac_flag[2] == 0:
            booster = i.text
            vac_flag[2] = 1
        else: 
            pass
      if cls[-2] == 'g-hide-mobile':
        if vac_flag[3] == 0:
            shots_given = i.text
            vac_flag[3] = 1
        else: 
            pass
      if cls[-1] == 'g-bar-col':
        count = count + 1
        if count == 4:
            elderly = i.text
            vac_flag[4] = 1
        else: 
            pass
      if sum(vac_flag) == 5:
        break

    vac_values = [atl_one_shot,two_shots,booster,shots_given,elderly]
    vac_values = list(map(str.strip,vac_values))
    
    return vac_labels, vac_values
  
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
    
def extract_unemp_rate(url):
    req = requests.get(url)
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
    
    return df_unemp_rate
    
def extract_inflation_rate(url):
    req = requests.get(url)
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

    #Included additional steps to handle non-numeric inflation values
    inflation_list = []
    for rate in df_inflation['inflation_rate']: 
        try:
            inflation_list.append(float(rate))
        except: 
            inflation_list.append(float(np.nan))
            
    df_inflation['inflation_rate'] = inflation_list
    df_inflation.index = df_inflation['date']
    df_inflation = df_inflation.dropna()
    
    return df_inflation
    
def extract_gdp(url):
    req = requests.get(url)
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
    
    return df_gdp
    
def calculate_buffet_indicator(url,df_gdp):
    #Extracting the U.S. total market value
    req = requests.get(url)
    bs = BeautifulSoup(req.content,'lxml')
    search = bs.find_all('td')

    us_market_val = float(search[1].text.replace(',',''))*1000000
    print ("U.S. Equity Maret Cap: $",us_market_val)
    print ("U.S. GDP: $",df_gdp['gdp'].iloc[0]*1000000000000)

    #Calculating Buffet Indicator
    buffet_ind = np.round((us_market_val/(df_gdp['gdp'].iloc[0]*1000000000000))*100,2)
    
    return buffet_ind
    
def extract_shiller_pe(url):
    #Extracting Shiller PE ratio
    req = requests.get(url)
    bs = BeautifulSoup(req.content,'lxml')
    search = bs.find_all('meta')

    shiller_pe = float(re.findall('(\d+\d+.\d+\d+)',search[1].get('content'))[0])
    
    return shiller_pe
    
def extract_debt_margin(url):
    req = requests.get(url)
    bs = BeautifulSoup(req.content,'lxml')
    search = bs.find_all('td')

    date = []
    debt = []

    for i in search:
      if "Month/Year" in i.get('data-th'):
        date.append(i.text)
      if "Debit Balances" in i.get('data-th'):
        debt.append(i.text)

    df_debt = pd.DataFrame()
    df_debt['date'] = date
    df_debt['debt'] = debt
    df_debt['debt'] = df_debt['debt'].apply(lambda x: int(x.replace(',','')))
    latest_data = df_debt[df_debt['date'].str.contains(r'-21')]
    
    return df_debt, latest_data
    
def extract_mortgage_rates(url):
    req = requests.get(url)
    bs = BeautifulSoup(req.content,'lxml')

    tr_tags = bs.find_all('tr')[:45]

    month_list = ['January','February','March','April','May','June','July','August','September','October','November','December']
    year = []
    current_years = []
    month = []
    mort_rate = []
    count = 0 #Current years count
    count2 = 0 #Count to cycle through rates and points
    count3 = 0 
    df_mortgage = pd.DataFrame()

    for i in tr_tags:
        #Find years
        th_tags = i.find_all('th')
        for j in th_tags: 
            if j.get('colspan') == '2':
                if count == 5: 
                    current_years = []
                    current_years.append(j.text)
                    count = 0
                    count = count + 1
                else: 
                    current_years.append(j.text)
                    count = count + 1
            #print ("Current years:",current_years)
            #Findings months
            if j.text in month_list: 
                #print ("yes")
                td_tags = i.find_all('td')
                #Finding rates
                for rate in td_tags: 
                    if (count2%2) == 0:
                        month.append(j.text)
                        mort_rate.append(rate.text)
                        #print (current_years)
                        #print (count3)
                        #print (current_years[count3])
                        year.append(current_years[count3])
                        count3 = count3 + 1
                    count2 = count2 + 1
                count3 = 0
                                    
    df_mortgage['rate'] = mort_rate
    df_mortgage['month'] = month
    df_mortgage['year'] = year
    df_mortgage['date'] = df_mortgage.apply(lambda x: pd.to_datetime(x[1] + '-' + x[2]),axis=1)
    df_mortgage = df_mortgage.sort_values('date')
    df_mortgage.index = df_mortgage['date']
    df_mortgage['rate'] = df_mortgage['rate'].replace('\xa0',np.nan)
    df_mortgage['rate'] = df_mortgage['rate'].map(float)
    
    return df_mortgage

# Commented out IPython magic to ensure Python compatibility.
def dash_create(df_unemp_rate,df_gdp,df_inflation,df_rates,yield_curve,vix,indexes,cases,vac_values,vac_labels,buffet_ind,
              shiller_pe,df_debt,latest_data,df_mortgage_15yr,df_mortgage_30yr):
  plt.rcParams.update(plt.rcParamsDefault)
#   %matplotlib inline
  plt.style.use('bmh')

  fig3 = plt.figure(constrained_layout=True,figsize=(42,22))
  gs = fig3.add_gridspec(40,3)

  f3_ax1 = fig3.add_subplot(gs[0:10,0])
  #plt.subplot(2,3,1)
  plt.plot(df_unemp_rate['unemployment_rate_percent'],alpha=0.8,label='Unemployment rate (%)',color='green')
  plt.plot(df_inflation.iloc[df_inflation.index>'2008']['inflation_rate'],alpha=0.8,label='Inflation rate (%)',color='blue')
  plt.plot(df_mortgage_30yr['rate'],label='30-year fixed-rate mortgage (%)',alpha=0.8,color='orange')
  plt.plot(df_mortgage_15yr['rate'],label='15-year fixed-rate mortgage (%)',alpha=0.8,color='red')
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
  #plt.subplot(2,3,2)
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
  #plt.subplot(2,3,3)
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
  #plt.subplot(2,3,3)
  plots = sns.barplot(y="Current Price", x="Index", data=indexes,alpha=0.8) 
    
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
  #plt.subplot(2,3,5)
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
  #plt.subplot(2,3,6)
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
  
  plt.show()
 
  
