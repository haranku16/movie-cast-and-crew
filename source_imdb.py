import pandas as pd

def source_imdb(name):
    '''
    Sources data from IMDB public datasets. Tries to fetch from local directory first, otherwise fetches over internet.

    Parameters:
        - name(str): dataset name
    
    Returns:
        - pd.DataFrame
    '''
    try:
        return pd.read_csv(f'./.data/{name}.csv')
    except:
        print(f'Local copy not found for {name}, so sourcing from the web...')
        df = pd.read_csv(f'https://datasets.imdbws.com/{name}.tsv.gz', compression='gzip', delimiter='\t')
        df.to_csv(f'./.data/{name}.csv')
        return df
