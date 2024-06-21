import requests 
from bs4 import BeautifulSoup
import pandas as pd
from useragents_rotator import soupgenerator_randomuseragent
import time
import random

'''
One time scrape: 
Scrape the page that contains all the A24 movies 
and save them to a csv. 

This includes all the sublinks for each movie that we will scrape further
for more info
'''

## Rotten tomatoes website : https://editorial.rottentomatoes.com/guide/all-a24-movies-ranked/
rt_a24_url = 'https://editorial.rottentomatoes.com/guide/all-a24-movies-ranked/'

## Get requests and soup
s = requests.session()
soup = soupgenerator_randomuseragent(rt_a24_url, s)
## Look for each movie card -- get list of movie details
movies = soup.find_all('div', class_='countdown-item-content')
if movies:
    print('Found all movies from soup')

## Use a list to collect all the info for each movie (each movie info as a dict)
## i.e. we will have a list of dictionaries 
data = []
for i, movie in enumerate(movies):
    title_parent = movie.find('h2')
    ## TITLE
    title = title_parent.find('a').get_text(strip = True)
    ## MOVIE URL 
    movie_url = title_parent.find('a')['href']
    release_year = movie.find('span', class_='start-year').get_text(strip = True).strip('()')
    RT_score = movie.find('span', class_='tMeterScore').get_text(strip = True)
    director_parent = movie.find('div', class_ = 'info director')
    director = director_parent.find('a').get_text(strip = True)
    cast_parent = movie.find('div', class_ = 'info cast')
    casts = cast_parent.find_all('a')
    casts_combined = ','.join(cast.get_text(strip = True) for cast in casts) 
    print(casts_combined)
    data.append({'Title': title, 'Release Year': release_year, 'RT_score': RT_score, 'URL': movie_url, 
    'Director' : director, 'Cast': casts_combined})

df = pd.DataFrame(data)
print(df)
df.to_csv('a24_movies_with_urls.csv', index=False)