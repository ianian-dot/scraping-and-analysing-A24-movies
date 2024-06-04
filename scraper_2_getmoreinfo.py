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



## FOR LOOP TO ITERATE THROUGH THE URLS AND COLLECT INFO
more_info_df = initial_df.copy()
session = requests.session()
for i, row in more_info_df.iterrows():
    print(f"scraping {row['Title']}")
    url = row['URL']
    soup = soupgenerator_randomuseragent(url, session= session)
    audience_score, genre, duration, rating, box_office, prod_co = other_info(soup)
    print(audience_score, genre, duration, rating, box_office, prod_co)
    # Append the extracted info to the DataFrame
    more_info_df.at[i, 'Audience Score'] = audience_score
    more_info_df.at[i, 'Genre'] = genre
    more_info_df.at[i, 'Duration'] = duration
    more_info_df.at[i, 'Rating'] = rating
    more_info_df.at[i, 'Box Office'] = box_office
    more_info_df.at[i, 'Production Co'] = prod_co

    if i % 10 == 0:
        time.sleep(2)

## Check and compare before and after 
print(f"Before: {initial_df.shape}")
print(f"After: {more_info_df.shape}")
more_info_df.to_csv('more_info_df.csv')

## Check missing data:
more_info_df.isna().any(axis = 1).sum()

## Movies with 6 NAs (the most missing ones)
movies_6_nas = [num_na == 6 for num_na in more_info_df.isna().sum(axis = 1)]
movies_6_nas_titles = more_info_df[movies_6_nas]['Title']
# for these movies, which variables are missing?
more_info_df[movies_6_nas].isna().sum(axis = 0)

## save html as a file to inspect the html code 
# html_content = soup.prettify() ## make it nicer first

# # Specify the file path where you want to save the HTML file
# file_path = 'output.html' ## specify output path and file name 

# # Write the HTML content to the file
# with open(file_path, 'w', encoding='utf-8') as f:
#     f.write(html_content)


## VARIABLE BY VARIABLE 
missing_variables = more_info_df.isna().sum(axis = 0)>0
## See examples of titles for each missing variable 
missing_variables.index


## POPULATING DATA GAPS WITH ROTTEN TOMATOES API 
from rotten_tomatoes_client import RottenTomatoesClient

RottenTomatoesClient.search('The Farewell')