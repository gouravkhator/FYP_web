from os import path

def write_to_csv(df, filename, parent_folder_location=path.join('app', 'outputs')):
    df.to_csv(path.join(parent_folder_location, filename))
    print(f'Saved to {filename}')
