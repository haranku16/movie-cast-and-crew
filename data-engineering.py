import pandas as pd
from pathlib import Path

# Create a local data directory for faster retrieval of IMDB data when re-running the script.
Path("./.data").mkdir(parents=True, exist_ok=True)

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

def main():
    '''
    Entrypoint for the script.
    '''

    # Source the data from IMDB public datasets
    print('Sourcing data from IMDB...')
    name_basics_df = source_imdb('name.basics')
    title_basics_df = source_imdb('title.basics')
    title_principals_df = source_imdb('title.principals')
    title_ratings_df = source_imdb('title.ratings')

    # Merge ratings into title_principals_df
    title_principals_df = pd.merge(title_principals_df[['tconst', 'nconst', 'category']], 
                                   title_ratings_df[['tconst', 'averageRating']], 
                                   left_on='tconst', 
                                   right_on='tconst', 
                                   how='left')

    # Compute mean of averageRating grouped by nconst (name)
    print('Computing mean of averageRating grouped by nconst (name)...')
    name_mean_ratings_df = title_principals_df.groupby('nconst').aggregate({'averageRating': 'mean'})

    # Merge average ratings by nconst into name_basics_df. This is the person's mean of averageRatings over all titles.
    print("Merging into name_basics_df...")
    name_basics_df = pd.merge(name_basics_df, name_mean_ratings_df, left_on='nconst', right_on='nconst', how='left')
    del name_mean_ratings_df

    # Compute mean of averageRating grouped by nconst (name) and category (role in the film's production)
    print("Compute mean of averageRating grouped by nconst (name) and category (role in the film's production)...")
    principal_ratings_agg_df = title_principals_df.groupby(['nconst', 'category']).aggregate({ 'averageRating': 'mean' })
    principal_ratings_agg_df = principal_ratings_agg_df.reset_index()

    # Flatten the aggregation into columns, like averageRating_actor, averageRating_actress, averageRating_director, etc.
    # These are the person's average ratings for each role that they've performed on any title.
    principal_ratings_agg_df = principal_ratings_agg_df.pivot(index='nconst', columns='category', values='averageRating').reset_index()
    principal_ratings_agg_df.columns.name = None
    principal_ratings_agg_df.columns = [f'averageRating_{col}' if col != 'nconst' else 'nconst' for col in principal_ratings_agg_df.columns]

    # Merge averageRating category means into name_basics_df on nconst
    print("Merging into name_basics_df...")
    name_basics_df = pd.merge(name_basics_df, principal_ratings_agg_df, left_on='nconst', right_on='nconst', how='left')
    del principal_ratings_agg_df

    # Rename averageRating as averageRating_principal, because eventually we want the title_basics_df to have both the averageRating
    # (the film's actual average rating) as well as the mean of each principal's averageRating across all of their titles.
    name_basics_df['averageRating_principal'] = name_basics_df['averageRating']
    name_basics_df = name_basics_df.drop('averageRating', axis=1)
    average_rating_column_names = [col for col in name_basics_df.columns if col.startswith('averageRating')]

    # Merge averageRating into title_basics_df
    print("Merging averageRating into title_basics_df...")
    title_basics_df = pd.merge(title_basics_df, title_ratings_df[['tconst', 'averageRating']], left_on='tconst', right_on='tconst', how='left')
    del title_ratings_df

    # Merge the averageRating_{category} columns (means across all principals) into title_basics_df
    print("Merging averageRating_\{category\} columns into title_basics_df...")
    temp_df = title_principals_df[['tconst', 'nconst']]
    right_cols = ['nconst']
    right_cols.extend(average_rating_column_names)
    temp_df = pd.merge(temp_df, name_basics_df[right_cols], left_on='nconst', right_on='nconst', how='left')
    agg_cols = ['tconst']
    agg_cols.extend(average_rating_column_names)
    temp_df = temp_df[agg_cols].groupby('tconst').mean()
    title_basics_df = pd.merge(title_basics_df, temp_df, left_on='tconst', right_on='tconst', how='left')
    title_basics_df.head()
    del temp_df

    # Export the engineered datasets
    print("Exporting datasets...")
    title_basics_df.to_csv('title.augmented.csv.gz', compression='gzip')
    print("title.augmented.csv.gz exported!")
    name_basics_df.to_csv('name.augmented.csv.gz', compression='gzip')
    print("name.augmented.csv.gz exported!")

if __name__ == '__main__':
    main()
