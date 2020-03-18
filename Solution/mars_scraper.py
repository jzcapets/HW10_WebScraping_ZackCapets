def scrape():
    #set up a blank list to hold all of our scraped data
    scrapeddata = {}
    
    # Import dependencies
    from bs4 import BeautifulSoup as bs
    from splinter import Browser
    import pandas as pd
    import time

#This part scrapes the headlines
    #Configure Browser
    executable_path = {'executable_path': 'chromedriver.exe'}
    browser1 = Browser('chrome', **executable_path, headless=False)
    url_marsnasa = 'https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest'
    browser1.visit(url_marsnasa)

    #scrape from browser
    soup = bs(browser1.html,'html.parser')
    #print(soup.prettify())

    #scrape the title of the first headline
    title_scrape = soup.find_all('div',class_="list_text")
    topheadline  = title_scrape[0].find_all('div','content_title')[0].text

    #scrape the teaser text for the first article
    body_scrape = soup.find_all('div',class_="list_text")
    teaser = body_scrape[0].find_all('div', class_ = 'article_teaser_body')[0].text
    

    browser1.quit()

#this part scrapes the feature photo
    #set up Browser to go to the JPL site, scrape feature photo
    url_marsjplimg = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser2 = Browser('chrome', **executable_path, headless = False)
    browser2.visit(url_marsjplimg)

    soupy = bs(browser2.html, 'html.parser')
    backgroundimage = soupy.find_all('article')[0]['style']


    #extract the url from the above result...identify the '/' character as the start of the string, and get rid of the semicolon and endquote
    imgstring = ""
    nstart = backgroundimage.find('/')
    nend = len(backgroundimage) - 3

    for n in range(nstart,nend):
        imgstring += backgroundimage[n]

    #concatenate the full image url since the above result is a relative path
    jpl = 'https://www.jpl.nasa.gov'
    jplfullurl = jpl + imgstring
    jplfullurl

    browser2.quit()

    #set up Browser for scraping
    #on this particular twitter page the latest tweet text is stored within the 27th instance of the particular css class
    url_marsweather = 'https://twitter.com/marswxreport?lang=en'
    browser3 = Browser('chrome', **executable_path, headless = False)
    browser3.visit(url_marsweather)

    #this time delay is necessary to ensure all page resources load before scraping is attempted.
        #does splinter have resources that will wait on the specific page resource to load before continuing?
    #absolutely
        #is this effective and will a more elegant solution cost extra and add complication even though this works? 
    #you bet.
    time.sleep(3)

    #set up a list to hold the weather reports that we will scrape from twitter
    #set up the keyword that the weather reports start with. If this changes in the future it can be modified here.
    weatherlist = []
    keyword = "InSight sol"

    #this css class includes many items on the page, we want just the weather reports, which all begin with 'InSight'
    soupier = bs(browser3.html, 'html.parser')
    weather = soupier.find_all('span', class_ = "css-901oao css-16my406 r-1qd0xha r-ad9z0x r-bcqeeo r-qvutc0")

    #loop through scraped html to find items within this css class matching the keyword, add these to our weather list
    for n in range(0, len(weather)):
        if keyword in weather[n].text:
            weatherlist.append(weather[n].text)
            
    #just store a reference to the latest one, i.e item 0 in our weather list, strip out the newline characters
    forecast = weatherlist[0].replace('\n',' ')
    forecast

    browser3.quit()
#this part scrapes the facts about mars
    #the url
    url_marsfacts = 'https://space-facts.com/mars/'
    #use pandas to scrape the table data (it's the middle table out of 3)
    factstable = pd.read_html(url_marsfacts)
    marsfacts_html = factstable[1].to_html(index = False)
    fixthings = marsfacts_html.replace('\n',' ')


#this part scrapes picture urls from the usgs site so we can hotlink them like scoundrels instead of properly hosting
    #urls we need
    astrourl = "https://astrogeology.usgs.gov"
    url_hemispherepics = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'

    #configure splinter
    browser4 = Browser('chrome', **executable_path, headless = False)
    browser4.visit(url_hemispherepics)

    #parse html on main mars pics page
    soupiest = bs(browser4.html, 'html.parser')

    #splinter isn't cooperating and won't let me click on links by link text or partial link text
    #this will scrape a-tags and product-item class which gives us 8 links (including duplicates)
    linklist1 = []
    for j in range(0,len(soupiest.find_all('a', class_ = "product-item"))):
        linklist1.append(soupiest.find_all('a', class_ = "product-item")[j]['href'])
    linklist1

    #get rid of duplicates -send our list to pandas dataframe, extract uniques, and back to list again in one line! huzzah!
    links = pd.DataFrame(linklist1, columns = ['link'])['link'].unique().tolist()

    #set up blank dictionary, lists to hold the scraped titles and urls

    urllist = []
    prov1 = []
    resultdict = {}

    #loop through the links we scraped for each one, send the browser to that link and get the title and url
    for k in range(0,len(links)):
        #the scraped links above are all relative to the base url for the site
        url = astrourl + links[k] 
        
        #go to the url
        browser4.visit(url) 
        
        #read the html
        soupierest = bs(browser4.html, 'html.parser') 
        
        #get the pic url
        url_item = soupierest.find_all('div', class_="downloads")[0].find_all('li')[0].find_all('a')[0]['href'] 
        urllist.append(url_item)
        
        #get the title...way easier than getting the pic url
        #this finds the word "Hemisphere" in the result string and grabs the string including 'Hemisphere'
        titletext = soupierest.find_all('title')[0].text 
        hemispherename = titletext[0:titletext.find("Hemisphere")+10]
        prov1.append(hemispherename)
        
    resultdict['title']=prov1
    resultdict['url']=urllist

    browser4.quit()
    scrapedata = {}
    scrapedata['headline']=topheadline
    scrapedata['teaser']=teaser
    scrapedata['weather']=forecast
    scrapedata['featureimage']=jplfullurl
    scrapedata['marsfacts']=fixthings
    scrapedata['pics'] = resultdict
    
    return scrapedata