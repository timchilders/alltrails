# No Pain, No Gain: analyzing Colorado trail reviews from Alltrails.com
![banner](/images/banner.jpg)
### Tim Childers | Data Science Immersive (May '21) | Capstone Project I
[Presentation](https://docs.google.com/presentation/d/1kdCTQPEqYhegzGAEBTwRqjShCLQG_Jh9Sd1J0s4u_uU/edit?usp=sharing)
## Introduction
I've always been an enthusiastic hiker and backpacker. When I look back at my favorite hiking trips, there's one thing they have in common. They were all uniquely challenging or difficult and I experienced a little pain and suffering during the hike. They were all hikes that I consider [type II fun](https://www.rei.com/blog/climb/fun-scale) (miserable while it was happening, but fun in retrospect). This led me to a question. Are other hikers like me?\

To answer this question, this project takes an in-depth look at the reviews of the most popular trails in Colorado hosted on [Alltrails.com](https://www.alltrails.com/us/colorado)

The goals of this project are:
<ol>
  <li>Webscrape Alltrails.com for every trail listed in Colorado</li>
  <li>Determine if hikes are rated higher if they are more challenging/difficult.</li>
</ol> 

## Methods

### Web Scraping
I used selenium and beautifulsoup to web scrape alltrails.com. Initially, I was succesfull at scraping the first 1000 trail cards of hikes in CO. These trail cards included information on hike length, difficulty, location, star rating, and a brief description of each trail. In order to get more information, including elevation gain, trail features, etc., each trail url needed to be opened individually. This is where I ran into problems. After accessing one trail url, Alltrails began sending CAPTCHAS to my webdriver. I implemented a webdriver function to randomize specific driver options as a solution. Despite many workarounds, this too failed. Given the time constraint of this project (4 days), I settled on using an older dataset from [another repo](https://github.com/oschow/take-a-hike). 

script located in src/:

```scraper.py```
a script which created selenium webdrivers to access alltrails urls and dynamically grab html. Beautifulsoup is used to parse the html and store data in a Pandas DataFrame. Results are exported as a csv.
  
### EDA
The dataset contains nearly 1500 trails located in CO, with features including: rating, elevation gain, trail length, a list of trail features, and # of reviews.

<p float="left">
  <img src="/images/trail_features.png" width="450" />
  <img src="/images/trail_locations.png" width="450" /> 
</p>

Exploring the ratings column, the data is right-skewed and centered around the mean of 4.1 stars. There are few trails rated below 4 stars. There was also noticable  This was likely due to trails with one or few reviews, so I also filtered for trails with at least 5 reviews, which produced a more 'normal' looking distribution with a greater right-skew, centered around the mean of ~4.2. 

<p float="left">
  <img src="/images/trail_ratings_compared.png" width="900" />
</p>

To see which features were more interesting, I created a correlation matrix. Focusing on the ratings column, it appears there is some positive correlation of elevation gain and trail length with how it's rated. However, this correlation does not appear to be strong. Other interesting features that stick out are a negative correlation of kid-friendly trails and ratings and a strong positive correlation of wildlife and wildflowers with views. 

<p align="center">
  <img src="/images/heat_map.png" width="500" />
</p>

notebook located in notebooks/:

```EDA.ipynb```

### Hypothesis Testing

*High rated hikes are on average more difficult than low rated hikes. (difficult = difficulty rating, longer distance, higher elevation gain)*

* Null hypothesis: difficulty rating, hike length or total elevation gain have no effect on hike rating.
* one-tailed so setting alpha threshold to 0.025/2 to account for overtesting of first test. (0.025 for elevation and length)

*High rated hikes feature waterfalls and wildflowers.* 

* Null hypothesis: popular hikes have no distinctive features.
* Testing hypothesis for one-tailed statistic, alpha threshold is 0.025

**1st Hypothesis:** *More difficult trails are rated higher.*

First, I created three samples from the population for each difficulty rating (easy,moderate,hard).

<p float="left">
  <img src="/images/difficulty_distro.png" width="900" />
</p>

I then determined whether any of my features are normally distributed using the *Shapiro-Wilk test*. After testing each feature, I determined none of the features had p-values greater than 0.05 and I could not assume they were normally distributed. With this in mind, I decided to use the *Mann-Whitney U Test*, to test each of my hypotheses.

The test returned a p-value of 8.9 x 10^-12 for testing hard to easy samples, and 0.00236 for hard to moderate samples. Both p-values were too low to accept the null-hypothesis, meaning trails rated as hard were statistically rated with more stars than easy trails and moderate trails.

I repeated the *Mann-Whitney U Test* with two samples of trails seperated by their ratings. Trails with ratings in the 75 percentile were selected as the high-rated sample. Trails below were considered low-rated.

The total elevation gain (in feet) and trail length (in miles) were tested as the independent variables of the samples, both yielding p-values far below the treshold. 


**2nd Hypothesis:** *High rated trails are more scenic (they have waterfall and wildflower features.*
Two samples were taken from the data for each hypothesis (wildflowers and waterfalls), one sample containing trails with the feature, and the other without the feature.

<p float="left">
  <img src="/images/beauty_distro.png" width="900" />
</p>

Again, I conducted a *Mann-Whitney U Test* for each hypothesis. The waterfalls samples yielded a p-value of: 0.0006, far below the alpha of 0.025. However the waterfall samples yielded a p-value of 0.052, higher than the alpha.

notebook located in notebooks/:

```Hypothesis_Testing.ipynb```

### Future Steps
* Find a workaround for Alltrails CAPTCHA system to collect more and updated trail data.
* Conduct sentiment analysis on trail review text.
* Determine if difficult hikes are rated better because these hikes generally have better views (above treeline,etc.) rather than hikers enjoying sweating.


