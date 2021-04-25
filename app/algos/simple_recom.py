# imports done in try except block to handle any import exception

try:
    # pre-built modules
    import pandas as pd
    import numpy as np
    import os
    from ast import literal_eval
    from sklearn.metrics.pairwise import linear_kernel

    # my defined modules
    from app.utils.csv_manipulations import write_to_csv, get_outputpath_csv
    from app.utils.clean_dataframes import clean_movies_metadata

    import warnings; warnings.simplefilter('ignore')
except Exception as e:
    print('Some modules could not be imported, error: ',e)
    exit(1)

"""Simple Recommender System"""

# clean movies metadata
md = clean_movies_metadata()

"""
We use the TMDB Ratings to come up with our Top Movies Chart. We will use IMDB's weighted rating formula to construct our chart. Mathematically, it is represented as follows:

Weighted Rating (WR) =  (v.R/(v+m))+(m.C/(v+m)) 
where,

v is the number of votes for the movie,

m is the minimum votes required to be listed in the chart,

R is the average rating of the movie,

C is the mean vote across the whole report,

The next step is to determine an appropriate value for m, the minimum votes required to be listed in the chart. We will use 85th percentile as our cutoff. In other words, for a movie to feature in the charts, it must have more votes than at least 85% of the movies in the list.
"""

"""Top Movies"""

# splitting genres column data into different rows with each having a genre
s = md.apply(lambda x: pd.Series(x['genres']),axis=1).stack().reset_index(level=1, drop=True)
s.name = 'genre'
gen_md = md.drop('genres', axis=1).join(s)

def generate_top_list(genre, percentile=0.85, get_top_n = 300):
    # filter rows by genre
    df = gen_md[gen_md['genre'] == genre]

    # find vote counts and average ratings
    vote_counts = df[df['vote_count'].notnull()]['vote_count'].astype('int')
    vote_averages = df[df['vote_average'].notnull()]['vote_average'].astype('int')
    C = vote_averages.mean()

    # quantile the votes as per the percentile
    m = vote_counts.quantile(percentile)
    
    # qualified movies are filtered here
    qualified = df[(df['vote_count'] >= m) & (df['vote_count'].notnull()) & (df['vote_average'].notnull())][['title', 'year', 'vote_count', 'vote_average', 'popularity']]

    qualified['vote_count'] = qualified['vote_count'].astype('int')
    qualified['vote_average'] = qualified['vote_average'].astype('int')
    
    # calculate weighted rating
    qualified['wr'] = qualified.apply(lambda x: (x['vote_count']/(x['vote_count']+m) * x['vote_average']) + (m/(m+x['vote_count']) * C), axis=1)

    # sort by weighted ratings in descending
    qualified = qualified.sort_values('wr', ascending=False).head(get_top_n)
    return qualified

# genre names
genre_names = [
    'Comedy', 'Fantasy', 'Animation', 'Crime'
]

for genre in genre_names:
    write_to_csv(df = generate_top_list(genre), filename = get_outputpath_csv('simple_recom_'+genre.lower()+'.csv'))

