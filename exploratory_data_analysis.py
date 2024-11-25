import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

def main():
    '''
    Entrypoint function for this script.
    '''

    # Extract the dataset from the gzipped CSV file
    title_df = pd.read_csv('title.augmented.csv.gz', compression='gzip')

    # Print DataFrame info
    print('DataFrame info:')
    print(title_df.info())

    # Print DataFrame counts per column
    print('\nColumn counts:')
    print(title_df.aggregate('count'))

    # Print completeness ratio
    print('\nColumn completeness:')
    print(title_df.aggregate('count')/len(title_df))

    # Extract first-listed genre from the genres column as top_genre
    title_df['top_genre'] = title_df['genres'].str.split(',').str[0].str.strip()
    print('\nUnique genres listed first in genres column:')
    print(title_df['top_genre'].unique())

    # Filter on rows that have values for the top_genre columns and averageRating* columns
    filtered_title_df = title_df[title_df[['top_genre', 'averageRating', 'averageRating_principal', 'averageRating_director', 'averageRating_producer', 'averageRating_actor', 'averageRating_actress', 'averageRating_writer', 'averageRating_cinematographer', 'averageRating_composer', 'averageRating_editor', 'averageRating_production_designer']].notnull().all(axis=1)]

    # Sampled and class-balanced subset of this data, roughly balanced across top_genre and taken at even intervals over time (startYear)
    balanced_title_df = pd.DataFrame()
    unique_genres = filtered_title_df['top_genre'].unique()
    samples_per_genre = 1000 // len(unique_genres)
    for genre in unique_genres:
        filtered_title_df_by_genre = filtered_title_df[filtered_title_df['top_genre'] == genre]
        filtered_title_df_by_genre = filtered_title_df_by_genre.copy()
        filtered_title_df_by_genre['startYear_casted_as_string'] = filtered_title_df_by_genre['startYear'].apply(lambda x: str(x))
        filtered_title_df_by_genre = filtered_title_df_by_genre.sort_values(by='startYear_casted_as_string')
        num_titles = len(filtered_title_df_by_genre)
        interval = num_titles // samples_per_genre
        if interval != 0:
            filtered_sampled_title_df_by_genre = filtered_title_df_by_genre.iloc[::interval]
            filtered_sampled_title_df_by_genre.drop('startYear_casted_as_string', axis=1)
            balanced_title_df = pd.concat([balanced_title_df, filtered_sampled_title_df_by_genre])
    balanced_title_df.reset_index(drop=True, inplace=True)

    # Samples per top_genre
    print('\nSamples per top_genre:')
    print(balanced_title_df.groupby('top_genre').aggregate({ 'tconst': 'count' }))

    # Select numeric columns and drop garbage row count columns
    numeric_df = balanced_title_df.select_dtypes(include=['float64', 'int64'])
    numeric_df = numeric_df.drop(['Unnamed: 0', 'Unnamed: 0.1'], axis=1)

    # Prepare plots/ directory if it doesn't yet exist
    Path("./plots").mkdir(parents=True, exist_ok=True)
    
    # Pair plot of distributions
    sns.pairplot(numeric_df)
    plt.title('Pair Plot of Distributions')
    plt.savefig('plots/pairplot.png')

    # Correlation matrix
    correlation_matrix = numeric_df.corr()
    plt.figure(figsize=(10, 8))
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', vmin=-1, vmax=1, center=0)
    plt.title('Correlation Matrix of Average Ratings Columns')
    plt.savefig('plots/correlation.png')

if __name__ == '__main__':
    main()
