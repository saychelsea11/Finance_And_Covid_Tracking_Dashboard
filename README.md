# Finance_And_Covid_Tracking_Dashboard

What we have so far!

![image](https://user-images.githubusercontent.com/31114603/109729487-ee12ac00-7b85-11eb-86d8-1647dfce9bfe.png)

### Code modifications: 
- **Yahoo Finance Indexes (3/13/21)**: In the code, "bs.find("script",text=re.compile("root.App.main")).text" seemed to return an empty string for some users which could be an issue with the Python or BeautifulSoup version. A fix for this was to use the *str()* function instead of *.text*.
- **New York Times vaccinations (3/13/21)**: The html text for the class attribute seemed to have changed on the NYT website. So the text used for parsing needed to be changed accordingly. The previous code containing the older parsing method is also shown in the code but commented out.
- **Added new metrics (10/10/21)**: Added *Shiller PE*, *Buffet indicator* and *FINRA debt margin* metrics to the dashboard as new measures of market valuation. 
- **Dashboard redesign (10/10/21)**: Reduced the *VIX volatility indicator* data to only keep the current VIX value. This data was combined with the 3 new metrics and displayed as part of the same chart on the bottom-left. 

