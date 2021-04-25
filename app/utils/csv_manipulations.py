import os

def get_inputpath_csv(filename):
    return os.path.normpath(f'app/inputs/{filename}')

def get_outputpath_csv(filename):
    return os.path.normpath(f'app/outputs/{filename}')
 
def write_to_csv(df, filename, display_df_name='dataframe'):
    df.to_csv(filename)
    print(f'Saved {display_df_name} to {filename}')

