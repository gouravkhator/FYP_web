# installed modules
from flask import Flask, render_template, request, session, abort, redirect
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests
import json
import os
import pathlib
import requests

# my modules
from firebase_admin_methods import create_user
from app.model_render.simple_recom_render import render_simple_recommender
from app.algos.metadata_recom import get_metadata_based_recom
from app.algos.hybrid_recom import recommend_hybrid, save_user_movies_tocsv, get_user_movie_titles
from app.utils.global_variables import get_duration_filters_list, get_genres_list

app = Flask(__name__)

'''
As auth-callback is the redirect uri, and its hosted on localhost, so its insecure

We have to enable OAUTHLIB_INSECURE_TRANSPORT to allow the logins.
'''
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

client_secrets_filepath = os.path.join(pathlib.Path(__file__).parent, "key/client_secret_oauth.json")

if not os.path.exists(client_secrets_filepath):
    print("Please keep the client_secret_oauth.json in the key/ directory. It is the secret config for google oauth..")
    exit(1)

client_secret_file_obj = open(client_secrets_filepath, 'r')
client_secret_dict = json.load(client_secret_file_obj)

client_secret_file_obj.close()

GOOGLE_CLIENT_ID = client_secret_dict.get('web')['client_id'] # this is used in auth callback
app.secret_key = GOOGLE_CLIENT_ID # just any random secret key can be given here

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_filepath,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri=client_secret_dict.get('web')['redirect_uris'][1]
)

@app.route('/')
def home_page():
    return render_template('index.html')

# Returns the context containing movies with their info segregated, and other info
def get_context_from_movies(movies_list, context, others):
    if movies_list.shape[0] == 0:
        # no movies were returned so throw error
        raise Exception("Oops! No movies returned as per your filters")

    return {
        **context,
        **others,

        'title_list': movies_list['title'].tolist(),
        'year_list': movies_list['year'].tolist(),
        'vote_count_list': movies_list['vote_count'].tolist(),
        'rating_list': movies_list['vote_average'].tolist(),
        'posters_list': movies_list['poster_path'].tolist(),
        'imdb_id_list': movies_list['imdb_id'].tolist(),
        'movie_durations_list': movies_list['runtime'].tolist(),
    }

@app.route('/recommend/content-based', methods=['GET', 'POST'])
def metadata_based_recommender_page():
    # common data sent for both GET and POST request
    context = {
        'genres_list': get_genres_list(), # list of all available genres
        'duration_filters_list': get_duration_filters_list(), # list of all available duration filters
    }

    if request.method == 'POST':
        searched_movie = request.form.get('searched-movie')

        top_n_str = request.form.get('top-n')
        published_date_filter = request.form.get('published-date-filter') or "Relevant"
        duration_filter = request.form.get('duration-filter') or "no-filter"

        genre_filter_input = request.form.get('genre-filter')

        movies_list = None
        top_n = 10

        if top_n_str != None:
            top_n = int(top_n_str)

        try:
            if genre_filter_input != None:
                # show simple recommender for genre
                movies_list = render_simple_recommender(genre = genre_filter_input, top_n = top_n, published_date_filter = published_date_filter, duration_filter = duration_filter)

                context = get_context_from_movies(movies_list=movies_list, context=context, others={
                    'top_n': top_n,
                    'published_date_filter': published_date_filter,
                    'duration': duration_filter,
                    'genre': genre_filter_input,
                })
            else:
                # show content metadata based recommendation
                movies_list, searched_movie_info = get_metadata_based_recom(searched_movie.strip(), top_n = top_n, published_date_filter = published_date_filter, duration_filter = duration_filter)
                
                # format the searched_movie_info into a dictionary
                searched_movie_info = searched_movie_info.to_dict().items()
                final_movie_info = {}
                for key, value in searched_movie_info:
                    final_movie_info[key] = list(value.values())[0]

                # get the context which contains all info of movies, along with the filters and other info provided
                context = get_context_from_movies(movies_list=movies_list, context=context, others={
                    'top_n': top_n,
                    'published_date_filter': published_date_filter,
                    'duration': duration_filter,
                    'searched_movie': searched_movie,
                    'searched_movie_info': final_movie_info,
                })
        except Exception as e:
            context = {
                **context,
                'error_message': e,
                'top_n': top_n,
                'published_date_filter': published_date_filter,
                'duration': duration_filter,

                'searched_movie': searched_movie,
                'genre': genre_filter_input,
            }

    return render_template('metadata_based_page.html', **context)

@app.route('/recommend/hybrid', methods=['GET', 'POST'])
def hybrid_recommender_page():
    context = {
        'session': session,
        'duration_filters_list': get_duration_filters_list(), # list of all available duration filters
    }

    # passing user saved movies with its ratings
    if 'google_id' in session:
        user_movie_titles, user_movie_ratings = get_user_movie_titles(user_id=session["google_id"])

        context = {
            **context,
            'user_movie_titles': user_movie_titles,
            'user_movie_ratings': user_movie_ratings,
        }

    if request.method == "POST":
        
        user_movies = []
        user_movie_ratings = []

        # get the movie inputs from user
        for i in range(1,6):
            movie_value = request.form.get(f'movie-title-{i}')
            movie_rating_str = request.form.get(f'movie-rating-{i}')
            movie_rating = 4.5 # by default

            if movie_rating_str and movie_rating_str.strip() != "":
                movie_rating = float(movie_rating_str.strip())

            if movie_value and movie_value.strip() != "":
                user_movies.append(movie_value)
                user_movie_ratings.append(movie_rating)

        try:
            if len(user_movies) == 0:
                # no movies provided from user
                raise Exception('Please provide atleast one movie input for us to perform hybrid recommendation..')

            # if the user is not logged in, redirect to hybrid page
            if "google_id" in session:
                # save the movie and ratings for that user to csv
                save_user_movies_tocsv(session["google_id"], user_movies, user_movie_ratings)
            else:
                return redirect('/recommend/hybrid')

            context = {
                **context,
                'success_message': 'Your movie preferences are saved',
            }
        except Exception as e:
            context = {
                **context,
                'error_message': e,
            }
    elif request.method == "GET":
        list_movies_preference = request.args.get('list-movies') # if the form is submitted actually, and not just get request occurred directly

        if list_movies_preference == "true":
            
            top_n_str = request.args.get('top-n')
            published_date_filter = request.args.get('published-date-filter') or "Relevant"
            duration_filter = request.args.get('duration-filter') or "no-filter"

            movies_list = None
            top_n = 10

            if top_n_str != None:
                top_n = int(top_n_str)

            try:
                # if the user is not logged in, redirect to hybrid page
                if "google_id" in session:
                    # get hybrid recommended movies
                    movies_list = recommend_hybrid(session["google_id"], top_n=top_n, published_date_filter = published_date_filter, duration_filter = duration_filter)
                else:
                    return redirect('/recommend/hybrid')
                
                context = get_context_from_movies(movies_list=movies_list, context=context, others={
                    # filters
                    'top_n': top_n,
                    'published_date_filter': published_date_filter,
                    'duration': duration_filter,
                })
            except Exception as e:
                context = {
                    **context,
                    'error_message': e,

                    'top_n': top_n,
                    'published_date_filter': published_date_filter,
                    'duration': duration_filter,
                }

    return render_template('hybrid_recom_page.html', **context)

'''
Google OAUTH Routes
'''
@app.route('/login')
def login():
    if "google_id" in session:
        return redirect('/')

    authorization_url, state = flow.authorization_url()
    session["state"] = state # to avoid CSRF attacks
    return redirect(authorization_url)

@app.route('/logout')
def logout():
    if not "google_id" in session:
        context = {
            'error_message': "You are not logged in. So, Logout is not possible",
        }
        # TODO: add error message in the page
        return redirect('/')
    
    session.clear()
    context =  {
        'success_message': "Congrats, you are logged out successfully.."
    }
    # TODO: add success message in the page
    return redirect('/')

@app.route('/auth-callback')
def auth_callback():
    flow.fetch_token(authorization_response=request.url)

    if not session["state"] == request.args["state"]:
        abort(500)  # State does not match!

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )

    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")
    session["email"] = id_info.get("email")
    
    create_user(str(id_info.get('email')).strip(), str(id_info.get('sub')).strip())

    return redirect("/recommend/hybrid")

if __name__ == '__main__':
    app.run("localhost", "8000", debug=True)
