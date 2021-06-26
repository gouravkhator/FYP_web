import os
import pandas as pd

def get_inputpath_csv(filename):
    return os.path.normpath(f'app/inputs/{filename}')

def get_outputpath_csv(filename):
    return os.path.normpath(f'app/outputs/{filename}')

def get_genres_list():
    return [
        'Comedy', 'Animation', 'Romance', 'Crime', 'Fantasy', 'Horror', 'Family', 'Adventure', 'Drama', 'Thriller', 'History', 'Science Fiction', 'Action', 'War', 'Mystery', 'Foreign', 'Music', 'Documentary',
    ]

def get_duration_filters_list():
    durations = [
        "<100", "100-200", "200+"
    ]

    # add "Minutes" to each duration like: <100 Minutes
    return ["{} {}".format(i,"Minutes") for i in durations]

def add_movie_filters_cli():
    try:
        top_n = int(input("Top N: ").strip())
        published_date_filter = input("Published Date Filter: ").strip().capitalize()

        print("Menu for duration filter: \nPress 1 for <100 minutes\nPress 2 for 100-200 minutes\nPress 3 for 200+ minutes\nPress 0 for no filters..\n")

        duration_choice = int(input("Enter your choice: ").strip())
        duration_filter = "no-filter"

        if duration_choice == 1:
            duration_filter = "<100 Minutes"
        elif duration_choice == 2:
            duration_filter = "100-200 Minutes"
        elif duration_choice == 3:
            duration_filter = "200+ Minutes"
        elif duration_choice == 0:
            duration_filter = "no-filter"
    except Exception as e:
        print("Error: ", e)
    
    return (top_n, published_date_filter, duration_filter)

# Gets the movie info for the searched movie
def get_searched_movie_info(searched_movie_title, metadata_smd):
    if searched_movie_title and searched_movie_title.strip() != "":
        searched_movie_title = searched_movie_title.lower().strip()

        metadata_smd = metadata_smd.reset_index()
        movie_info = metadata_smd[metadata_smd["title_lower"] == searched_movie_title][['title', 'vote_count', 'vote_average', 'year', 'id', 'popularity', 'poster_path', 'imdb_id', 'runtime']]

        return movie_info
    
    return None
