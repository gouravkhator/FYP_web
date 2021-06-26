from datetime import date
from dateutil.relativedelta import relativedelta

def add_published_date_filter(df, published_date_filter = "Relevant"):
    df['year'] = df['year'].apply(lambda x: 0 if x=="NaT" else x).astype('int') 
    # the type of year is in str in some movies

    published_filter_years = {"Newest": 8, "Mid": 15, "Oldest": 15}
    '''
    for Relevant, no published date filter, and no sorting by year
    for Newest, latest 8 years, sorted by year descending
    for Mid, latest 15 years (including newest movies also), sorted by year descending
    for Oldest, older than 15 years, sorted by year ascending
    '''
    # Filtering out based on Published filter criteria
    if published_date_filter == "Newest":

        # starting year for the Newest filter, as of current year
        # date.today() is current date and subtract it with corresponding years (cannot directly subtract date and int so use relativedelta)
        
        start_range_year = (date.today() - relativedelta(years=published_filter_years.get(published_date_filter))).year
        df = df[df['year'] >= start_range_year]
        df = df.sort_values('year', ascending=False) # sort by year in descending

    elif published_date_filter == "Mid":

        start_range_year = (date.today() - relativedelta(years=published_filter_years.get(published_date_filter))).year
        df = df[df['year'] >= start_range_year]
        df = df.sort_values('year', ascending=False) # sort by year in descending

    elif published_date_filter == "Oldest":

        start_range_year = (date.today() - relativedelta(years=published_filter_years.get(published_date_filter))).year
        df = df[df['year'] < start_range_year]
        df = df.sort_values('year', ascending=True) # sort by year in ascending

    return df

def add_duration_filter(df, duration_filter = "no-filter"):
    df['runtime'] = df['runtime'].astype('float') # the type of runtime is in str in some movies

    if duration_filter == "<100 Minutes":
        df = df[df['runtime'] < 100]
    elif duration_filter == "100-200 Minutes":
        df = df[(df['runtime'] >= 100) & (df['runtime'] <= 200)]
    elif duration_filter == "200+ Minutes":
        df = df[df['runtime'] > 200]

    return df

# Removes rows which have zero vote counts, zero ratings, zero durations
def remove_zero_field_values(df):
    df['runtime'] = df['runtime'].astype('float') # the type of runtime is in str in some movies

    df = df[(df['runtime'] >= 1) & (df['vote_count'] >= 1) & (df['vote_average'] >= 1)]
    return df
