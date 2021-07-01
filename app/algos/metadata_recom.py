try:
    # pre-built modules
    import pandas as pd
    import os

    # my defined modules
    from app.utils.global_variables import get_outputpath_csv, add_movie_filters_cli, get_searched_movie_info, handle_internal_error
    from app.utils.clean_dataframes import generate_smd_metadata_recom, get_cosine_sim_matrix
    from app.utils.movie_filters import add_published_date_filter, add_duration_filter, remove_zero_field_values

    import warnings; warnings.simplefilter('ignore')
except Exception as e:
    print('Some modules could not be imported')
    exit(1)

'''
weighted_rating: Generates the weighted rating using x, m and C
'''
def weighted_rating(x, m, C):
    v = x['vote_count']
    R = x['vote_average']
    return (v/(v+m) * R) + (m/(m+v) * C)

'''
get_metadata_based_recom: Main function for generating recommended movies based on metadata.

Params:

title: The movie title for which we want other similar metadata based recommended movies
'''
def get_metadata_based_recom(title, top_n=10, published_date_filter = "Relevant", duration_filter = "no-filter"):
    smd_filepath = get_outputpath_csv('metadata_smd.csv')
    smd = None

    # if smd is not present, then generate it
    if not os.path.exists(smd_filepath):
        smd = generate_smd_metadata_recom()

    smd = pd.read_csv(smd_filepath, index_col='Id')

    cosine_sim, indices = get_cosine_sim_matrix(smd)

    idx = indices.get(title.lower().strip()) 
    # the movie titles are stored in lowercase format in title_lower field for checking without case sensitivity, so get the index of its lower case equivalent
    
    if idx == None:
        raise Exception(f"No movies matched the given movie : {title}", True)

    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:151]
    movie_indices = [i[0] for i in sim_scores]
    
    movies = smd.iloc[movie_indices][['title', 'year', 'vote_count', 'vote_average', 'popularity', 'poster_path', 'imdb_id', 'runtime']]

    vote_counts = movies[movies['vote_count'].notnull()]['vote_count'].astype('int')
    vote_averages = movies[movies['vote_average'].notnull()]['vote_average'].astype('int')
    C = vote_averages.mean()
    m = vote_counts.quantile(0.3)

    qualified = movies[(movies['vote_count'] >= m) & (movies['vote_count'].notnull()) & (movies['vote_average'].notnull())]
    qualified['vote_count'] = qualified['vote_count'].astype('int')
    qualified['vote_average'] = qualified['vote_average'].astype('int')

    # Compute the weighted rating
    qualified['wr'] = qualified.apply(weighted_rating, axis=1, args=(m,C))

    # first sort by weighted rating, then sort by year if user wants that, then select top n

    # sort the movies by weighted rating descending
    qualified = qualified.sort_values('wr', ascending=False)

    # remove rows with zero vote_counts or zero vote_averages or zero runtime 
    qualified = remove_zero_field_values(qualified)

    # add published date filter on qualified movie dataframe
    qualified = add_published_date_filter(qualified, published_date_filter=published_date_filter)
    qualified = add_duration_filter(qualified, duration_filter=duration_filter)
    
    searched_movie_info = get_searched_movie_info(searched_movie_title = title.lower().strip(), metadata_smd=smd)

    return (qualified.head(top_n), searched_movie_info) # select top n

if __name__ == '__main__':
    print('----Content Based Recommender System----')
    movie = input("Enter your favorite movie : ").strip()
    # filters input
    top_n, published_date_filter, duration_filter = add_movie_filters_cli()
    
    try:
        print("Building metadata based recommendations for you...\n")

        qualified, _ = get_metadata_based_recom(title=movie, top_n=top_n, published_date_filter=published_date_filter, duration_filter=duration_filter)
        
        if qualified.shape[0] > 0:
            print("Here are some movies (recommended based on metadata) for you :")
            print(qualified)
            print(f"\nTotal number of {published_date_filter} recommended movies for {movie} is {qualified.shape[0]}")
            print("\nNote: The list may contain less movies than expected, due to only showing movies based on your taste.")
        else:
            print("No movies found as per your taste...")
    except Exception as e:
        print("Error: \n", handle_internal_error(e))
