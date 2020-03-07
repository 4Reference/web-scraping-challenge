# Import dependancies
from splinter import Browser
from bs4 import BeautifulSoup as bs
import time
import requests
import pandas as pd
import GetOldTweets3 as got

def init_browser():
    executable_path = {"executable_path": "chromedriver.exe"}
    return Browser("chrome", **executable_path, headless=False)

def scrape():
    browser = init_browser()

    # Create holder for Mars data
    mars_data = {}

    ## NASA Mars News ##
    news_url = 'https://mars.nasa.gov/news/'
    browser.visit(news_url)
    time.sleep(4)
    html=browser.html
    soup = bs(html, 'html.parser')
    time.sleep(3)
    news_title = soup.find('div', class_='content_title').text
    news_p = soup.find('div', class_='article_teaser_body').text

    # Update mars_data
    mars_data['news_title'] = news_title
    mars_data['news_p'] = news_p

    ## JPL Mars Space Images - Featured Image ##
    image_url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(image_url)
    time.sleep(4)
    html = browser.html
    soup = bs(html, 'html.parser')
    time.sleep(3)
    base_url = 'https://www.jpl.nasa.gov'
    image_url = soup.find('article', class_='carousel_item')
    footer = image_url.find('footer')
    ref = footer.find('a')
    full_href = ref['data-fancybox-href']
    featured_image_url = base_url + full_href

    # Update mars_data
    mars_data['featured_image_url'] = featured_image_url

    ## Mars Weather ##
    tweetCriteria = got.manager.TweetCriteria().setUsername("MarsWxReport").setMaxTweets(5)
    tweet = got.manager.TweetManager.getTweets(tweetCriteria)
    weather_tweet = []
    for x in tweet: 
        twit = x.text
        if 'InSight' and 'sol' in twit:
            weather_tweet.append(twit)
            break
        else: 
            pass
    mars_weather = weather_tweet[0]

    # Update mars_data
    mars_data['mars_weather'] = mars_weather

    ## Mars Facts ##
    url = 'https://space-facts.com/mars/'
    browser.visit(url)
    html=browser.html
    soup = bs(html, 'html.parser')
    table_df = ((pd.read_html(url))[0]).rename(columns={0: "Description", 1: "Value"}).set_index(['Description'])
    html_table = (table_df.to_html()).replace('\n', '')

    # Update mars_data
    mars_data['mars_facts'] = html_table

    ## Mars Hemispheres ##
    mars_hemispheres_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(mars_hemispheres_url)
    time.sleep(2)
    links = browser.find_by_css('.description .itemLink')
    hemisphere_image_urls = []
    hrefs = []
    titles = []
    for link in links:
        hrefs.append(link['href'])
        titles.append(link.text)
    current_index = 0
    for href in hrefs:
        browser.visit(href)
        time.sleep(1)
        # find url for image
        css_image = '.downloads ul li a'
        image_link = browser.find_by_css(css_image)[0]
        hemisphere_image_urls.append({"title" : titles[current_index], "img_url" : image_link['href']})
        current_index += 1
    hemisphere_image_urls

    # Update mars_data
    mars_data['hemisphere_image_urls'] = hemisphere_image_urls

    # Close the browser after scraping
    browser.quit()

    # Return results
    return mars_data