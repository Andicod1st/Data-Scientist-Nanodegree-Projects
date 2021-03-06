import sys
import pandas as pd
from sqlalchemy import create_engine

def load_data(messages_filepath, categories_filepath):
    '''
    Load the datasets and merged them to generate a dataframe
    to be used for analysis
    
    Args:
        messages_filepath: The path of messages dataset.
        categories_filepath: The path of categories dataset.
        
    Returns:
        A merged dataset
    '''
    
    messages = pd.read_csv(messages_filepath)
    categories = pd.read_csv(categories_filepath)
    df = pd.merge(messages, categories, how='outer',on=['id'])
    return df

def clean_data(df):
    '''
    Perfom necessary data preprocessing and data cleaning required 
    on the dataset to aid improve model performances
    
    Args:
        df: The merged loaded dataset.
        
    Returns:
        A cleaned and preprocessed dataframe is returned
    '''
    categories = df.categories.str.split(';', expand = True)
    row = categories.loc[0]
    category_colnames = row.apply(lambda x: x[:-2]).values.tolist()
    categories.columns = category_colnames
    categories.related.loc[categories.related == 'related-2'] = 'related-1'
    for column in categories:
        categories[column] = categories[column].astype(str).str[-1]
        categories[column] = pd.to_numeric(categories[column])
    df.drop('categories', axis = 1, inplace = True)
    df = pd.concat([df, categories], axis = 1)
    df.drop_duplicates(subset = 'id', inplace = True)
    return df

def save_data(df, database_filepath):
    """
    The cleaned data is loaded into a database to serve
    as input to the NLP/ML pipeline
    
    Args:
        df: The merged loaded dataset.
        database_filepath: The filepath to save the loaded file
    """
    engine = create_engine('sqlite:///' + database_filepath)
    df.to_sql('df', engine, index=False)

def main():
    if len(sys.argv) == 4:

        messages_filepath, categories_filepath, database_filepath = sys.argv[1:]

        print('Loading data...\n    MESSAGES: {}\n    CATEGORIES: {}'
              .format(messages_filepath, categories_filepath))
        df = load_data(messages_filepath, categories_filepath)

        print('Cleaning data...')
        df = clean_data(df)

        print('Saving data...\n    DATABASE: {}'.format(database_filepath))
        save_data(df, database_filepath)

        print('Cleaned data saved to database!')

    else:
        print('Please provide the filepaths of the messages and categories '\
              'datasets as the first and second argument respectively, as '\
              'well as the filepath of the database to save the cleaned data '\
              'to as the third argument. \n\nExample: python process_data.py '\
              'disaster_messages.csv disaster_categories.csv '\
              'DisasterResponse.db')


if __name__ == '__main__':
    main()