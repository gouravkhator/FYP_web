try:
    # pre-built modules
    import pandas as pd
    import os
    from importlib import import_module

    # my defined modules
    from app.utils.global_variables import get_outputpath_csv
    from app.utils.movie_filters import add_published_date_filter, add_duration_filter, remove_zero_field_values

    import warnings; warnings.simplefilter('ignore')
except Exception as e:
    print('Some modules could not be imported')
    exit(1)

def render_simple_recommender(genre='Comedy', top_n = 10, published_date_filter = "Relevant", duration_filter = "no-filter"):
    filepath = get_outputpath_csv(filename=f'simple_recom_{genre.lower()}.csv')
    
    if not os.path.exists(filepath):
        '''
        The output simple recommender csv file is not present, so import the simple_recom module.
        This will generate the output csv files so that we can load those files for further processing.
        '''

        moduleName = "app.algos.simple_recom"
        globals()[moduleName] = import_module(moduleName)

    df = pd.read_csv(filepath, index_col='Id')

    # remove rows with zero vote_counts or zero vote_averages or zero runtime 
    df = remove_zero_field_values(df)

    # adding published date filter to movies dataframe (which are already saved in csv, sorted by weighted rating)
    df = add_published_date_filter(df, published_date_filter=published_date_filter)
    df = add_duration_filter(df, duration_filter=duration_filter)
    
    return df.head(top_n) # after filtering all, select top n

# if this module is run from command line, then just call the method above with all defaults
if __name__ == "__main__":
    print(render_simple_recommender())
