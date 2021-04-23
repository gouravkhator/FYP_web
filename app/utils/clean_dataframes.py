
# Commented out IPython magic to ensure Python compatibility.
# %matplotlib inline
import pandas as pd
import numpy as np
from ast import literal_eval

from app.utils.csv_manipulations import write_to_csv

import warnings; warnings.simplefilter('ignore')

def clean_movies_metadata():
    movies_metadata_dataset = 'app/inputs/movies_metadata.csv'
    md=pd.read_csv(movies_metadata_dataset)

    md['genres'] = md['genres'].fillna('[]').apply(literal_eval).apply(lambda x: [i['name'] for i in x] if isinstance(x, list) else [])

    md['year'] = pd.to_datetime(md['release_date'], errors='coerce').apply(lambda x: str(x).split('-')[0] if x != np.nan else np.nan)

    # writing movies metadata cleaned version
    write_to_csv(df=md, filename='app/inputs/movies_metadata_cleaned.csv')
    return md
