try:
    # pre-built modules
    import numpy as np
    import pandas as pd
    import os
    from time import time
    import csv
    from surprise import Reader, Dataset, SVD

    # my defined modules
    from app.utils.global_variables import get_inputpath_csv, get_outputpath_csv, add_movie_filters_cli
    from app.utils.movie_filters import add_published_date_filter, add_duration_filter, remove_zero_field_values
    from app.utils.clean_dataframes import generate_smd_metadata_recom, get_cosine_sim_matrix

    import warnings; warnings.simplefilter('ignore')
except Exception as e:
    print('Some modules could not be imported, error: ',e)
    exit(1)

def save_user_movies_tocsv(user_id, user_movies, user_movie_ratings):
    ratings_filepath = get_inputpath_csv(filename='ratings_small.csv')
    metadata_smd_filepath = get_outputpath_csv(filename='metadata_smd.csv')
    
    # read smd to get the movie ids from the given titles
    metadata_smd = pd.read_csv(metadata_smd_filepath, index_col='Id')
    metadata_smd = metadata_smd.reset_index()
    
    # movie id is in the id column of smd, and index the series by title_lower
    movie_indices = pd.Series(metadata_smd['id'].tolist(), index=metadata_smd['title_lower'])
    final_movie_ids = []

    ratings_df = pd.read_csv(ratings_filepath)
    already_saved_ids = ratings_df[ratings_df["userId"] == user_id][["movieId"]]["movieId"].tolist()
    for movie_title in user_movies:
        movie_id = movie_indices.get(movie_title.lower().strip())
        
        if movie_id == None:
            continue
        
        if not movie_id in already_saved_ids:
            # if the new movie id is already saved before, don't save again
            final_movie_ids.append(movie_id)

    final_movies_len = len(final_movie_ids)
    if final_movies_len == 0:
        # if no movie titles had their names in the dataset
        raise Exception("Provided movies were already saved before or was not found in our dataset. Provide new valid movies..")

    with open(ratings_filepath, 'a+', newline='') as write_obj:
        csv_writer = csv.writer(write_obj)

        for i, movie_id in enumerate(final_movie_ids):
            # write the row in serial order: userId, movieId, rating, timestamp
            csv_writer.writerow([user_id, movie_id, user_movie_ratings[i], int(time())])

# Gets the movie titles from the user id by looking in ratings_small.csv
def get_user_movie_titles(user_id):
    ratings_filepath = get_inputpath_csv(filename='ratings_small.csv')
    metadata_smd_filepath = get_outputpath_csv(filename='metadata_smd.csv')

    ratings_df = pd.read_csv(ratings_filepath)
    saved_movie_ratings = ratings_df[ratings_df["userId"] == user_id][["movieId", "rating"]]
    user_movie_ids, user_ratings = saved_movie_ratings["movieId"].tolist(), saved_movie_ratings["rating"].tolist()

    if len(user_movie_ids) == 0:
        return []

    metadata_smd = pd.read_csv(metadata_smd_filepath, index_col='Id')
    movies_list_temp = pd.Series(metadata_smd['title'].tolist(), index=metadata_smd["id"])

    movie_titles = []
    final_ratings = []
    for index, movie_id in enumerate(user_movie_ids):
        title = movies_list_temp.get(movie_id)
        if title == None:
            continue

        movie_titles.append(title)
        # get the rating for that movie id with that index in the ids list 
        final_ratings.append(user_ratings[index])

    return (movie_titles, final_ratings)

def hybrid_initial_setup(metadata_smd):
    def convert_int(x):
        try:
            return int(x)
        except:
            return np.nan

    svd = SVD()
    reader = Reader()

    ratings_filepath = get_inputpath_csv(filename='ratings_small.csv')
    ratings = pd.read_csv(ratings_filepath)

    user_ratings_data = Dataset.load_from_df(ratings[['userId', 'movieId', 'rating']], reader)
    
    trainset = user_ratings_data.build_full_trainset()
    svd.fit(trainset)

    links_filepath = get_inputpath_csv('links.csv')
    id_map = pd.read_csv(links_filepath)[['movieId', 'tmdbId']]

    id_map['tmdbId'] = id_map['tmdbId'].apply(convert_int)
    id_map.columns = ['movieId', 'id']
    id_map = id_map.merge(metadata_smd[['title', 'id']], on='id').set_index('title')

    indices_map = id_map.set_index('id')

    return (svd, indices_map)

def recommend_hybrid(user_id, top_n = 10, published_date_filter = "Relevant", duration_filter = "no-filter"):
    # ! ISSUE: user_id is taken as string, and not int, it should be int 
    smd_filepath = get_outputpath_csv('metadata_smd.csv')
    metadata_smd = None

    # if smd is not present, then generate it
    if not os.path.exists(smd_filepath):
        metadata_smd = generate_smd_metadata_recom()

    metadata_smd = pd.read_csv(smd_filepath, index_col='Id')
    cosine_matrix, cosine_indices = get_cosine_sim_matrix(metadata_smd)

    svd, hybrid_indices_map = hybrid_initial_setup(metadata_smd)
    
    movie_indices = []
    sim_scores = []
    movie_title_list, _ = get_user_movie_titles(user_id) # get the movie titles from the user id by looking in ratings_small.csv
    
    for movie_title in movie_title_list:
        idx = cosine_indices.get(movie_title.lower().strip())
        
        if idx == None:
            continue

        current_sim_scores = list(enumerate(cosine_matrix[int(idx)]))
        sim_scores.extend(current_sim_scores)
        
        
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        '''
        Top 150 similar movies based on user saved movies
        '''
        sim_scores = sim_scores[1:151]
    
    movie_indices.extend([i[0] for i in sim_scores])
    result_movies = metadata_smd.iloc[movie_indices][['title', 'vote_count', 'vote_average', 'year', 'id', 'popularity', 'poster_path', 'imdb_id', 'runtime']]

    est_list = [] # estimated ratings list

    # as hybrid idx was having two elements as series, so appended 0 for those movies
    for x in result_movies['id']:
        hybrid_idx = hybrid_indices_map.loc[x]['movieId']
        # two cells in hybrid indices map were series, not int

        if type(hybrid_idx) == np.int64:
            est_list.append(svd.predict(user_id, hybrid_idx).est)
        else:
            est_list.append(0)
            # TODO: can append series first element
    
    result_movies['est'] = est_list

    # TODO: remove movies with 0 vote_average

    # removed duplicate movies by the movie "id"
    result_movies.drop_duplicates(subset='id', keep='first', inplace=True)
    # sort by estimated rating
    result_movies = result_movies.sort_values('est', ascending=False)

    # remove rows with zero vote_counts or zero vote_averages or zero runtime 
    result_movies = remove_zero_field_values(result_movies)

    result_movies = add_published_date_filter(result_movies, published_date_filter=published_date_filter)
    result_movies = add_duration_filter(result_movies, duration_filter=duration_filter)

    return result_movies.head(top_n)

if __name__=="__main__":
    print("----Hybrid Recommender System----")
    try:
        user_id = input("Enter your user id: ").strip()
        # TODO: add movie save part also

        # filters input
        top_n, published_date_filter, duration_filter = add_movie_filters_cli()

        print("Building hybrid recommendations for you...\n")
        
        hybrid_recommended_movies = recommend_hybrid(user_id = user_id, top_n=top_n, published_date_filter=published_date_filter, duration_filter=duration_filter)

        if hybrid_recommended_movies.shape[0] > 0:
            print("Here are some recommended movies for you : ")
            print(hybrid_recommended_movies)
            print(f"\nTotal number of {published_date_filter} recommended movies for your watched movies is {hybrid_recommended_movies.shape[0]}")

            print("\nNote: The list may contain less movies than expected, due to only showing movies based on your taste.")
        else:
            print("No movies found as per your taste...")
    except Exception as e:
        print("Error: ",e)
