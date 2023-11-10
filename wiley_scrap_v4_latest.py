from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import time

def get_issue_links():
    links = []
    for year in range(0,24):
        for issue in range(1,13):
            links.append(f"https://onlinelibrary.wiley.com/toc/10970266/{2023-year}/{44-year}/{issue}")
    links.remove('https://onlinelibrary.wiley.com/toc/10970266/2023/44/12')
    return links

def get_volume_and_issue(soup):
    vol_issue = soup.find('div',class_='cover-image__parent-item') # volume and issue number.
    n = vol_issue.text.split(",")
    VOLUME = int(n[0].split()[1]) #volume number
    ISSUE = int(n[1].split()[1]) # issue number
    
    return VOLUME,ISSUE

def get_month_year(soup):
    date = soup.find('div','cover-image__date').text
    MONTH = date.split()[0]
    YEAR = date.split()[1]
    return MONTH,YEAR

def get_authors_list(soup):
    #authors list. 
    s = soup.find_all('div',class_='comma__list')
    authors = []
    for i in range(len(s)):
        authors.append(s[i].text.strip().replace("\xa0\n","").strip(","))
    return authors
    
def get_titles_and_article_links(soup):
    # getting titles and links of articles. 
    titles = []
    links = []
    s = soup.find_all('a',class_='issue-item__title visitable')
    for i in s:
        titles.append(i.text.strip()) #adding title on a page to the titles list
    s = soup.find_all('a',title='Abstract')
    for i in s:
        links.append("https://onlinelibrary.wiley.com"+ i.get('href')) # completing the link , 
    titles.pop(0)
    return titles,links
        
def finalized_data(links,titles,authors,volume,issue,month,year):
    article_details = []
    research = None
    managerial = None
    for link,title,author in zip(links,titles,authors):
        driver = webdriver.Chrome()
        driver.get(link)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source,'html.parser')
        driver.quit()
        print(title)
        #research summary and managerial summary 
        try:
            s = soup.find('div',class_ = "article-section__content en main")
            p = s.find_all('p')
            research = p[0].text
            if len(p)==2:
                managerial = p[1].text 
        except AttributeError:
            pass
    
        data  = {'volume': volume, 
         'issue' : issue,
         'month':month , 
         'year':year,
         'type': "RESEARCH SUMMARY" , 
         'title':title,
         'author':author,
         'abstract_research_summary':research, 
        'abstract managerial summary':managerial,
         } 
        
        article_details.append(data)
    return article_details
        
if __name__ == "__main__":
    start_index = int(input('start_index: '))
    end_index = int(input('end_index: '))
    data_list = []
    links = get_issue_links()[start_index:end_index]
    print(links)
    for link in links:
        
        driver = webdriver.Chrome()
        driver.get(link)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source,'html.parser')
        driver.quit()

        #----------------------------------------------
        print(link)
        volume,issue = get_volume_and_issue(soup)
        print('successfully get volume and issue\n')
        month,year = get_month_year(soup)
        print('successfully get month and year')
        authors = get_authors_list(soup)
        print('successfully get authors')
        titles,links = get_titles_and_article_links(soup)
        print('successfully get titles ')
        #--------------------------------------------------
        articles = finalized_data(links,titles,authors,volume,issue,month,year)
        print('\n\n.......finalizing your data.......')
        data_list.append(pd.DataFrame(articles))
        print('all process completed . no errors.')      
    df = pd.concat(data_list,ignore_index=True)
    df.to_csv('wiley_scraped_articles.csv',index=False)
    print('finally done hurray bro . finally finally done . approx 3000 links . opened..')
