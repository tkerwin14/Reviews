'''
Program: ny_reviews.py
Author: TK
Date Created: 8/31/2018
Purpose: 
'''


import pandas as pd
from selenium import webdriver
import time
from bs4 import BeautifulSoup
import codecs
import re

def scrollPage(driver): 
    '''
    Parameters: 
    driver - WebDriver - the Chrome browser
    Scrolls to the end of the page.
    '''
    SCROLL_PAUSE_TIME = 10
    
    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    
        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)
    
        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    return True 

def pullFullPage(url): 
    '''
    Parameters: 
    driver - WebDriver - Chrome browser
    url - string - the url of NY Times reviews 
    Saves out the page source after scrolling to the end.
    '''
    driver = webdriver.Chrome()
    driver.get(url)
    moreBtn = driver.find_element_by_css_selector(".load-more-button")
    moreBtn.click()
    scrollPage(driver)
    with open("ny_reviews.htm", "w") as f: 
        f.write(driver.page_source)
    driver.close()

def tryValue(elem): 
    '''
    Parameters: 
    elem - BeautifulSoupHTMLElement - the element you want to extract text from
    Returns text if element exists and removes all the new line characters.
    '''
    try: 
        return elem.text.replace("\n", "")
    except: 
        return None

def pullStars(sb): 
    '''
    Parameters: 
    sb - BeautifulSoupHTMLElement - a single section for the review
    Returns the number of stars given in the review or whether it was
    a critic's pick. It returns None if neither appear in the text.
    '''
    starValue = None
    vs = sb.find("span", "visually-hidden")
    if vs != None: 
        starValue = vs.text
    else: 
        cp = sb.find("li", 'critics-pick')
        if (cp != None): 
            starValue = "Critic's Pick"
    return starValue 

def parseBody(sb, sf): 
    '''
    Parameters: 
    sb - BeautifulSoupHTMLElement - a single section for the review
    Returns a body parsed out into a full review section.
    '''
    rObj = {}
    rObj["name"] = re.sub("\s+", " ", sb.find("h2", "headline").text).strip().replace("\n", "")
    rObj['stars'] = pullStars(sb)
    rObj["price"] = tryValue(sb.find("li", {"itemprop": "priceRange"}))
    rObj["cuisine"] = tryValue(sb.find("li", {"itemprop": "servesCuisine"}))
    rObj["address"] = tryValue(sb.find("li", {"itemprop": "addressLocality"}))
    rObj["summary"] = sb.find("p", "summary").text
    rObj["author"] = tryValue(sb.find("span", "author-name"))
    rObj["url"] = sb.find("a", "story-link")["href"]
    rObj["datePublished"] = tryValue(sf.find("time", "dateline"))
    return rObj

def parseReviews(): 
    '''
    Takes in the HTML of the reviews and parses them out into a dataframe.
    '''
    #First read in the HTML:
    htmlDoc = codecs.open("ny_reviews.htm", "r")
    htmlText = htmlDoc.read()
    bs = BeautifulSoup(htmlText, "html.parser")
    #Get the story bodies: 
    storyBodies = bs.find_all("div", "story-body")
    storyFeet = bs.find_all("footer", "story-footer")
    restLst = []
    for sb, sf in zip(storyBodies, storyFeet): 
        rObj = parseBody(sb, sf)
        restLst.append(rObj)
    return pd.DataFrame(restLst)
    
#Pull the HTML version:
urlStart = "https://www.nytimes.com/reviews/dining?action=click&contentCollection=dining&region=navbar&module=collectionsnav&pagetype=sectionfront&pgtype=sectionfront"
pullFullPage(urlStart)

#Get the parsed version:
df = parseReviews()



