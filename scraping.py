# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import datetime as dt

def scrape_all():
    # Initiate headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in a dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now(),
        "hemisphere_image_info": hemisphere_image(browser)
    }

    # Stop webdriver and return data
    browser.quit()
    return data

# Define mars_news
def mars_news(browser):

    # Scrape Mars News
    # Visit the mars nasa news site
    url = 'https://redplanetscience.com'
    browser.visit(url)
    
    # Optional delay for loading the page 
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')
    
    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one('div.list_text')

        # Assign variables to title and summary
        slide_elem.find('div', class_='content_title')
        # Use the parent element to find the first `a` tag and save it as `news_title`
        news_title = slide_elem.find('div', class_='content_title').get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()

    except AttributeError:
        return None, None
    return news_title, news_p 

# ### JPL Space Images Featured Images
def featured_image(browser):
    # Visit URL
    url = 'https://spaceimages-mars.com'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')

    except AttributeError:
        return None

    # Use the base URL to create an absolute URL
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'
    
    return img_url

# ## Mars Facts
def mars_facts():
    # Add try/except for error handling
    try:
        # Use 'read_html' to scrape the facts table into a dataframe
        df = pd.read_html('https://galaxyfacts-mars.com')[0]

    except BaseException:
        return None

    # Assign columns and set index of dataframe
    df.columns=['Deescription', 'Mars', 'Earth']
    df.set_index('Description', inplace=True)

    # Convert dataframe into HTML format, add bootstrap
    return df.to_html(classes="table table-striped")

if __name__ == "__main__":

    # If running as script, print scraped data
    print(scrape_all())

## End session
#browser.quit()

# Hemisphere Data
def hemisphere_image(browser):

    # Visit the URL.
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)

    # Create a list to hold images and titles.
    hemisphere_image_urls = []

    #Parse the resulting html with soup.
    html = browser.html
    main_soup = soup(html, 'html.parser')

    # Add try/except for errors.
    try:
        # Find number of pictures.
        pics_count = len(main_soup.select('div.item'))

        # Use a for loop
        for i in range(pics_count):

            # Create an empty dict for results.
            hemispheres = {}

            # Find link to images.
            link_image = main_soup.select('div.description a')[i].get('href')
            browser.visit(f'https://astrogeology.usgs.gov{link_image}')

            # Parse new html page using soup.
            html = browser.html
            sample_image_soup = soup(html, 'html.parser')

            # Get full image link and title.
            img_url = sample_image_soup.select_one('div. downloads ul li a').get('href')

            img_title = sample_image_soup.select_one('h2.title').get_text()

            # Add extracts to dict.
            hemispheres = {
                'img_url': img_url,
                'img_title': img_title}

            # Append dict to image url lists.
            hemisphere_image_urls.append(hemispheres)

            # Return to main page.
            browser.back()

    except BaseException:
        return None

        # Return dictionary of each irmage url and title.
        return hemisphere_image_urls
    
if __name__ == "__main__":
    # If ran as script, print scraped data.
    print(scrape_all())