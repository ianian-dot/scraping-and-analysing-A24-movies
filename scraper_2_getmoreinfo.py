import pandas as pd
from useragents_rotator import soupgenerator_randomuseragent
import time 
import random
import requests

initial_df  = pd.read_csv('a24_movies_with_urls.csv')
initial_df.head()
initial_df.columns
## Index(['Title', 'Release Year', 'Rating', 'URL'], dtype='object')
## Current info we have: movie, release year, rating, url, director, casts

## Aim: extract more info, such as 
## - rating: e.g. R rated
## - audience rating : see if this correlates with rt scores
## - genre : see ratings over genres, etc
## - release date : use to see interesting time trends 
## - producer :
## - runtime : see if movies have gotten longer over time?

## For loop to loop through each movie's url to dig for more info 
# testurl1 = initial_df['URL'][0]
# print(testurl1)
# soup = soupgenerator_randomuseragent(testurl1)
# type(soup)
# ## 1: Find audience score 
# score_board_element = soup.find('score-board-deprecated', attrs={'data-qa': 'score-panel'})
# # Extract the value of the 'audiencescore' attribute
# if score_board_element:
#     audience_score = score_board_element.get('audiencescore')
#     print("Audience Score:", audience_score)


# for url in initial_df['URL'][:10]:
#     print(url)
#     soup = soupgenerator_randomuseragent(url)
#     print(audience_score(soup))


def info_finder(soup, textsearch):
    item = None
    item_sib = soup.find(class_ = 'info-item-label' ,string= lambda text: text and textsearch.lower() in text.lower())
    if item_sib:
        item = item_sib.find_next_sibling().get_text(strip=True)
    else: 
        print(f'{textsearch} not found')
    return item



def other_info(soup):
    # Initialize variables
    audience_score = None
    genre = None
    duration = None
    rating = None
    box_office = None
    prod_co = None
    
    # AUDIENCE SCORE
    score_board_element = soup.find('score-board-deprecated', attrs={'data-qa': 'score-panel'})
    if score_board_element:
        audience_score = score_board_element.get('audiencescore')  # get the attribute
    else:
        print("Audience score not found.")
        
    # GENRE, DURATION
    info_text = soup.find('p', class_="info")
    if info_text:
        info_text = info_text.text.replace(' ', '').split(',')
        if len(info_text) >= 3:
            _, genre, duration = info_text[:3]  # Assuming genre and duration are the first two elements
    else:
        genre = info_finder(soup, 'genre')
        duration = info_finder(soup, 'runtime')

    # rating, box office, production co
    info_list = soup.find('ul', id='info')
    if info_list:
        # Rating
        rating = info_finder(info_list, 'rating')

        # Box office
        box_office = info_finder(info_list, 'box office')

        # Production co
        prod_co = info_finder(info_list, 'production co')
    else:
        print("Info list not found.")    

    return audience_score, genre, duration, rating, box_office, prod_co


def other_info_improved(soup):
    # Initialize variables
    audience_score = None
    genre = None
    duration = None
    rating = None
    box_office = None
    prod_co = None
    
    # AUDIENCE SCORE
    score_board_element = soup.find('score-board-deprecated', attrs={'data-qa': 'score-panel'})
    if score_board_element:
        audience_score = score_board_element.get('audiencescore')  # get the attribute
    else:
        score_board_element = soup.find('score-icon-audience-deprecated')
        if score_board_element: 
            audience_score = score_board_element.get('percentage')
        else:
            audience_score = soup.find('span', class_ = 'percentage', 
                                       attrs = {'data-qa': 'audience-score'})


        
    # GENRE, DURATION
    info_text = soup.find('p', class_="info")
    if info_text:
        info_text = info_text.text.replace(' ', '').split(',')
        if len(info_text) >= 3:
            _, genre, duration = info_text[:3]  # Assuming genre and duration are the first two elements
    else:
        genre = info_finder(soup, 'genre')
        duration = info_finder(soup, 'runtime')
        
    # rating, box office, production co
    # rating, box office, production co
    info_list = soup.find('ul', id='info')
    if info_list:
        # Rating
        rating = info_finder(info_list, 'rating')
        

        # Box office
        box_office = info_finder(info_list, 'box office')

        # Production co
        prod_co = info_finder(info_list, 'production co')
    else:
        print("Info list not found.")    

    return audience_score, genre, duration, rating, box_office, prod_co

def other_info_updated(soup):
    '''
    UPDATED METHOD FOR THE NEW WEBSITE FORMATTING 
    ALSO THE MOST EFFICIENT AND CAPTURES ALL DETAILS FROM THE MOVIE INFO TABLE INSTEAD OF HAVING TO PICK OUT CERTAIN 
    INFO
    '''
    audience_score = None
    number_audience_reviews = None

    ## 1. Audience scores 
    audience_score = soup.find('rt-button', {'slot': 'audienceScore'}).get_text(strip=True)
    number_audience_reviews = soup.find('rt-link', {'slot': 'audienceReviews'}).get_text(strip=True)

    ## === TABLE INFORMATION AT THE BOTTOM
    all_categories = soup.find_all('div', class_ = 'category-wrap')
    category_title = [category.find('dt').get_text(strip = True) for category in all_categories]
    category_value = [category.find('dd').get_text(strip = True) for category in all_categories]
    details_dict = {title:value for title,value in zip(category_title, category_value)}
    # Add audience scores and number of aud reviews
    details_dict['audience_score'] = audience_score
    details_dict['number_audience_reviews'] = number_audience_reviews

    return details_dict


    


## FOR LOOP TO ITERATE THROUGH THE URLS AND COLLECT INFO
def loop_and_scrape_more_info(original_df, session, dict_collector):
    for i, row in original_df.iterrows():
        print(f"scraping {row['Title']}")
        url = row['URL']
        soup = soupgenerator_randomuseragent(url, session= session)
        info = other_info_updated(soup)
        print(info)
        dict_collector.append(info)
        if i % 10 == 0:
            time.sleep(2)

    return(dict_collector)
    
## Get the info
session = requests.session()
dict_collector = []
extra_info_list_of_dic = loop_and_scrape_more_info(initial_df, session, dict_collector)

## Make the df 
extra_df = pd.DataFrame(extra_info_list_of_dic)


## Check and clean df 
print(extra_df.shape)
print(initial_df.shape)

## Check cols to see if there are duplicates (e.g. slightly different spelling)
extra_df.columns

## Append to original df 
full_df = pd.concat([initial_df, extra_df], axis=1) ## combine horizontally 

## Save 
full_df.to_csv('full_scraped_a24_df.csv')



########## ============================================================
########## ============================================================
########## ============================================================
## TESTING - DELETE LATER 
# session = requests.session()
# url = 'https://www.rottentomatoes.com/m/amy_2015'
# soup = soupgenerator_randomuseragent(url, session)

# soup.find('rt-button', {'slot': 'audienceScore'}).get_text(strip=True)
# soup.find('div', class_ = 'content-wrap').find_all('div', class_ = 'category-wrap')
# all_categories = soup.find_all('div', class_ = 'category-wrap')
# category_title = [category.find('dt').get_text(strip = True) for category in all_categories]
# category_value = [category.find('dd').get_text(strip = True) for category in all_categories]
# details_dict = {title:value for title,value in zip(category_title, category_value)}

