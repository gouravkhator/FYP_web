# imports done in try except block to handle any import exception
try:
    # pre-built modules
    import pandas as pd
    import os

    # my defined modules
    from app.utils.global_variables import get_outputpath_csv, get_genres_list, handle_internal_error
    from app.utils.clean_dataframes import clean_movies_metadata

    import warnings; warnings.simplefilter('ignore')
except Exception as e:
    print('Some modules could not be imported')
    exit(1)
    
"""Simple Recommender System"""

movies_metadata_cleaned = None

# read cleaned dataset, and if some error occurs, then log them
try:
    # clean movies metadata
    movies_metadata_cleaned = clean_movies_metadata()
except Exception as e:
    print(handle_internal_error(e))
    exit(1)

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

'''
generate_top_list: Generates the top movies list and returns the dataframe of top movies for that genre
'''
def generate_top_list(genre, percentile=0.85, top_n = 500):
    # splitting genres column data into different rows with each having a genre
    s = movies_metadata_cleaned.apply(lambda x: pd.Series(x['genres']),axis=1).stack().reset_index(level=1, drop=True)
    s.name = 'genre'
    gen_md = movies_metadata_cleaned.drop('genres', axis=1).join(s)

    # filter rows by genre
    df = gen_md[gen_md['genre'] == genre]

    # find vote counts and average ratings
    vote_counts = df[df['vote_count'].notnull()]['vote_count'].astype('int')
    vote_averages = df[df['vote_average'].notnull()]['vote_average'].astype('int')
    C = vote_averages.mean()

    # quantile the votes as per the percentile
    m = vote_counts.quantile(percentile)
    
    # qualified movies are filtered here and assigned columns that would be used
    qualified = df[(df['vote_count'] >= m) & (df['vote_count'].notnull()) & (df['vote_average'].notnull())][['title', 'year', 'vote_count', 'vote_average', 'popularity', 'poster_path', 'imdb_id', 'runtime']]

    qualified['vote_count'] = qualified['vote_count'].astype('int')
    qualified['vote_average'] = qualified['vote_average'].astype('int')
    
    # calculate weighted rating
    qualified['wr'] = qualified.apply(lambda x: (x['vote_count']/(x['vote_count']+m) * x['vote_average']) + (m/(m+x['vote_count']) * C), axis=1)

    # sort by weighted ratings in descending
    qualified = qualified.sort_values('wr', ascending=False).head(top_n)
    return qualified

# genre names
genres_list = get_genres_list()

for genre in genres_list:
    df = generate_top_list(genre)
    filepath = get_outputpath_csv(f'simple_recom_{genre.lower()}.csv')

    # make directory of outputs if it does not exist
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    df.to_csv(filepath, index_label='Id') # give the index label so as to name the 'Unnamed: 0' column
    # there is also an "id" column which is the id for each movie entry

    print(f'Saved top movies for {genre} to {filepath} ')

print('\nSaved top movies for all genres to app/outputs/simple_recom_*.csv')
