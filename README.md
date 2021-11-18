# Finance_And_Covid_Tracking_Dashboard

What we have so far!

![image](https://user-images.githubusercontent.com/31114603/141147778-2866edd6-02a5-466c-8985-8b10a5a24e84.png)

### Code modifications: 
**3/13/21**
- **Yahoo Finance Indexes**: In the code, "bs.find("script",text=re.compile("root.App.main")).text" seemed to return an empty string for some users which could be an issue with the Python or BeautifulSoup version. A fix for this was to use the *str()* function instead of *.text*.
- **New York Times vaccinations**: The html text for the class attribute seemed to have changed on the NYT website. So the text used for parsing needed to be changed accordingly. The previous code containing the older parsing method is also shown in the code but commented out.

**10/10/21**
- **Added new metrics**: Added *Shiller PE*, *Buffet indicator* and *FINRA debt margin* metrics to the dashboard as new measures of market valuation. 
- **Dashboard redesign**: Reduced the *VIX volatility indicator* data to only keep the current VIX value. This data was combined with the 3 new metrics and displayed as part of the same chart on the bottom-left. 

**11/10/21**
- **Changed source for major indexes**: Now retrieving major indexes information using the Yahoo Finance API which is increasing compute time by a few seconds. No longer scraping the information from a web source. 
- **Added *Gold* and *Bitcoin* assets**: Added Gold and Bitcoin metrics part of the *Indexes and Assets* plot. These metrics are also being extracted using the Yahoo Finance API. 
- **Changed source for interest rates**: Now retrieving long-term and short-term interest rates from *Treasury.gov* which is an official source instead of *Ycharts*. 
- **Monthly data for interest rates**: Interest rates plot x-axis now covers the current month. 

**11/18/21**
- **Added Streamlit functionality**: Created Python scripts to generate the dashboard using Streamlit. The dashboard can now be viewed on a browser as an App. The code is located in the *Dashboard_With_Streamlit_App* folder. The *requirements.txt* file is also included there. 

