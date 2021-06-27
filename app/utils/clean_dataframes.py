# pre-defined modules
import pandas as pd
import numpy as np
import re
import os
from ast import literal_eval
from nltk.stem.snowball import SnowballStemmer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# my defined modules
from app.utils.global_variables import get_inputpath_csv, get_outputpath_csv

import warnings; warnings.simplefilter('ignore')

def clean_movies_metadata():
    print("Cleaning movies_metadata.csv...")
    movies_metadata_dataset_path = get_inputpath_csv(filename='movies_metadata.csv')
    
    # check if original unprocessed dataset is present or not
    if not os.path.exists(movies_metadata_dataset_path):
        raise Exception(f'Input dataset: {movies_metadata_dataset_path} not found')

    md=pd.read_csv(movies_metadata_dataset_path)
    
    md['genres'] = md['genres'].fillna('[]').apply(literal_eval).apply(lambda x: [i['name'] for i in x] if isinstance(x, list) else [])

    # get the year part
    md['year'] = pd.to_datetime(md['release_date'], errors='coerce').apply(lambda x: str(x).split('-')[0] if x != np.nan else np.nan)

    md['title_lower'] = md['title'].apply(lambda x: str(x).lower().strip() if isinstance(x, str) else x) # converting to lower case

    # scraping poster path from imdb website and saving to cleaned movies metadata file in the poster_path_scraped field
    # md['poster_path_scraped'] = md['imdb_id'].apply(lambda imdbid: get_poster_image_path(imdb_id = imdbid.strip()) if imdbid != None else "")

    filepath = get_inputpath_csv('movies_metadata_cleaned.csv')

    # writing movies metadata cleaned version
    md.to_csv(filepath, index_label='Id')
    print(f'Saved cleaned movies metadata to {filepath}')
    
    return md

# generates smd (dataframe which has all links, credits, keywords, movies data processed in 1 dataframe) for metadata based recommendation
def generate_smd_metadata_recom():
    print('Processing datasets and generating smd csv file...')
    # initialisation
    movies_metadata_cleaned = None
    links = None
    credits_dataset = None
    keywords = None

    '''
    check_file_exists_and_read: Checks if the path exists or not and if it exists then reads the csv and returns the DataFrame
    '''
    def check_file_exists_and_read(filepath):
        if not os.path.exists(filepath):
            raise Exception(f'Input dataset: {filepath} not found')
        
        return pd.read_csv(filepath)

    # read cleaned datasets and uncleaned datasets, and if some error occurs, then log them
    try:
        # clean movies metadata
        movies_metadata_cleaned = clean_movies_metadata()
        
        dataset_path = get_inputpath_csv(filename='links.csv')
        links = check_file_exists_and_read(dataset_path)

        dataset_path = get_inputpath_csv(filename='credits.csv')
        credits_dataset = check_file_exists_and_read(dataset_path)

        dataset_path = get_inputpath_csv(filename='keywords.csv')
        keywords = check_file_exists_and_read(dataset_path)
    except Exception as e:
        print('Error caused: ', e.args[0])
        exit(1)

    '''
    get_director: Gets the director from the dataset
    '''
    def get_director(x):
        for i in x:
            if i['job'] == 'Director':
                return i['name']
        return np.nan

    '''
    filter_keywords: Filters the keywords
    '''
    def filter_keywords(x, s):
        words = []
        for i in x:
            if i in s:
                words.append(i)
        return words

    '''
    clean_for_metadata_recom: Cleans, adds metadata fields and generates smd (the final accumulated dataframe)
    '''
    def clean_for_metadata_recom(movies_metadata_cleaned, links, credits_dataset, keywords):
        links = links[links['tmdbId'].notnull()]['tmdbId'].astype('int')

        movies_metadata_cleaned = movies_metadata_cleaned.drop([19730, 29503, 35587])
        movies_metadata_cleaned['id'] = movies_metadata_cleaned['id'].astype('int')
        smd = movies_metadata_cleaned[movies_metadata_cleaned['id'].isin(links)]

        smd['tagline'] = smd['tagline'].fillna('')
        smd['description'] = smd['overview'] + smd['tagline']
        smd['description'] = smd['description'].fillna('')

        keywords['id'] = keywords['id'].astype('int')
        credits_dataset['id'] = credits_dataset['id'].astype('int')
        movies_metadata_cleaned['id'] = movies_metadata_cleaned['id'].astype('int')

        movies_metadata_cleaned = movies_metadata_cleaned.merge(credits_dataset, on='id')
        movies_metadata_cleaned = movies_metadata_cleaned.merge(keywords, on='id')

        smd = movies_metadata_cleaned[movies_metadata_cleaned['id'].isin(links)]

        smd['cast'] = smd['cast'].apply(literal_eval)
        smd['crew'] = smd['crew'].apply(literal_eval)
        smd['keywords'] = smd['keywords'].apply(literal_eval)
        smd['cast_size'] = smd['cast'].apply(lambda x: len(x))
        smd['crew_size'] = smd['crew'].apply(lambda x: len(x))

        smd['director'] = smd['crew'].apply(get_director)
        smd['cast'] = smd['cast'].apply(lambda x: [i['name'] for i in x] if isinstance(x, list) else [])
        smd['cast'] = smd['cast'].apply(lambda x: x[:3] if len(x) >=3 else x)
        smd['keywords'] = smd['keywords'].apply(lambda x: [i['name'] for i in x] if isinstance(x, list) else [])

        smd['cast'] = smd['cast'].apply(lambda x: [str.lower(i.replace(" ", "")) for i in x])
        smd['director'] = smd['director'].astype('str').apply(lambda x: str.lower(x.replace(" ", "")))

        smd['director'] = smd['director'].apply(lambda x: [x,x])

        s = smd.apply(lambda x: pd.Series(x['keywords']),axis=1).stack().reset_index(level=1, drop=True)
        s.name = 'keyword'
        s = s.value_counts()
        s = s[s > 1]

        # using stemmer for keywords stemming
        stemmer = SnowballStemmer('english')

        smd['keywords'] = smd['keywords'].apply(filter_keywords, args=(s,))
        smd['keywords'] = smd['keywords'].apply(lambda x: [stemmer.stem(i) for i in x])
        smd['keywords'] = smd['keywords'].apply(lambda x: [str.lower(i.replace(" ", "")) for i in x])

        smd['original_title'] = smd['original_title'].apply(lambda x: [x])

        smd['soup'] = smd['keywords'] + smd['cast'] + smd['cast'] + smd['director'] + smd['genres'] + smd['genres'] + smd['original_title'] + smd['original_title']
        smd['soup'] = smd['soup'].apply(lambda x: ' '.join(x))

        '''
        Dropping duplicate movies with same title_lower.
        We were removing duplicate movies with same title.

        But, we were checking title_lower fields for recommending, so movies with same title could have different title_lower field values. (The movies could be : diLwAle and Dilwale for example and they could be different movies all together)

        So, if processing was on title_lower, we should also delete duplicate movies with same title_lower fields.
        ''' 
        smd.drop_duplicates(subset='title_lower', keep='first', inplace=True)
        return smd

    smd = clean_for_metadata_recom(movies_metadata_cleaned, links, credits_dataset, keywords)

    # saving smd dataframe to csv
    smd_filepath = get_outputpath_csv(filename='metadata_smd.csv')
    # make outputs directory if it does not exist
    os.makedirs(os.path.dirname(smd_filepath), exist_ok=True)

    smd.to_csv(smd_filepath, index_label='Id')
    print(f'Saved smd dataset to {smd_filepath}')

'''
generate_cosine_sim_matrix: Generates the cosine similarity matrix from the cleaned dataset
'''
def generate_cosine_sim_matrix(smd):
    print('Generating cosine similarity matrix. Please wait for a while...')
    count = CountVectorizer(analyzer='word',ngram_range=(1, 2),min_df=0, stop_words='english')
    count_matrix = count.fit_transform(smd['soup'])
    
    cosine_sim = cosine_similarity(count_matrix, count_matrix)
    filepath = get_outputpath_csv('cosine_matrix.npy')
    np.save(filepath, cosine_sim)
    
    print(f'Generated cosine similarity matrix to {filepath}')

    return cosine_sim

'''
get_cosine_sim_matrix: Returns the cosine similarity matrix from the cleaned dataset
'''
def get_cosine_sim_matrix(metadata_smd):
    cosine_matrix_filepath = get_outputpath_csv('cosine_matrix.npy')
    cosine_matrix = None

    if not os.path.exists(cosine_matrix_filepath):
        print(f"Please generate cosine similarity matrix in the path: {cosine_matrix_filepath} .. Without cosine similarity matrix, metadata based recommendation will not work.")
        exit(1)
    
    cosine_matrix = np.load(cosine_matrix_filepath, mmap_mode='r')

    metadata_smd = metadata_smd.reset_index()
    indices = pd.Series(metadata_smd.index, index=metadata_smd['title_lower'])
    # get indices of title_lower, which is the lowercase version of movie title

    return (cosine_matrix, indices)
