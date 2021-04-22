
# Commented out IPython magic to ensure Python compatibility.
# %matplotlib inline
import pandas as pd
import numpy as np
from ast import literal_eval

import warnings; warnings.simplefilter('ignore')

def write_to_csv(df, filename):
    df.to_csv(filename)
    print(f'Saved dataframe to {filename}')

movies_metadata_dataset = 'app/inputs/movies_metadata.csv'
md=pd.read_csv(movies_metadata_dataset)

md['genres'] = md['genres'].fillna('[]').apply(literal_eval).apply(lambda x: [i['name'] for i in x] if isinstance(x, list) else [])

md['year'] = pd.to_datetime(md['release_date'], errors='coerce').apply(lambda x: str(x).split('-')[0] if x != np.nan else np.nan)

# writing movies metadata cleaned version
write_to_csv(df=md, filename='app/outputs/movies_metadata_cleaned.csv')
