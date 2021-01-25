import os

import re
import pandas as pd

from .utils import lower_col_names, lower_columns, capitalize_columns_names

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ASSETS_DIR = os.path.join(PROJECT_DIR, "assets")
PRODUCTS_PATH = os.path.join(ASSETS_DIR, "PRODUCTS.csv")
PRICES_STOCK_PATH = os.path.join(ASSETS_DIR, "PRICES-STOCK.csv")


# Process CSV files
def process_csv_files():
    products_df = pd.read_csv(filepath_or_buffer=PRODUCTS_PATH, sep="|")
    prices_stock_df = pd.read_csv(filepath_or_buffer=PRICES_STOCK_PATH, sep="|")

    # filter for STOCK > 0
    prices_stock_df = prices_stock_df[prices_stock_df['STOCK'] > 0]

    # filter BRANCHES MM, RHSM
    prices_stock_df = prices_stock_df.loc[prices_stock_df['BRANCH'].isin(['MM', 'RHSM'])]

    # Delete null values
    products_df.fillna(value='', inplace=True)

    # Adding STORE and URL columns
    products_df['STORE'] = 'Richarts'
    products_df['URL'] = 'n/a'

    # Filtering SKU values of products_df present in prices_stock_df
    filter = products_df['SKU'].isin(prices_stock_df['SKU'].values)
    products_df = products_df[filter]

    # Taking the lowest pricing and the total stock availability
    branchproducts_df = prices_stock_df.groupby(['SKU', 'BRANCH'], as_index=False, sort=False,
                                                group_keys=False).aggregate(
        {'PRICE': 'min', 'STOCK': 'sum'})

    # Converting data types
    prices_stock_df['BRANCH'] = prices_stock_df['BRANCH'].astype('category')
    # Cleaning & styling
    products_df['DESCRIPTION'] = products_df['DESCRIPTION'].apply(lambda x: re.sub('<.*?>', '', x))
    products_df['PACKAGE'] = products_df['DESCRIPTION'].apply(
        lambda x: re.findall(r'(?!0)\d+\s?\w+\.?$', x))
    products_df['PACKAGE'] = products_df['PACKAGE'].apply(''.join).apply(
        lambda x: x.replace('.', ''))
    products_df['CATEGORY'] = products_df['CATEGORY'].str.cat(
        [products_df['SUB_CATEGORY'], products_df['SUB_SUB_CATEGORY']], sep=' | ')

    # Drop columns not required
    products_df = products_df.drop(
        columns=['SUB_CATEGORY', 'SUB_SUB_CATEGORY', 'ORGANIC_ITEM', 'KIRLAND_ITEM', 'BUY_UNIT',
                 'FINELINE_NUMBER',
                 'DESCRIPTION_STATUS'])

    # Using styling functions
    capitalize_columns_names(products_df, ['NAME', 'BRAND', 'DESCRIPTION'])
    lower_columns(products_df, ['CATEGORY', 'PACKAGE'])
    lower_col_names(products_df, branchproducts_df)

    print(products_df)
    print(branchproducts_df)


if __name__ == "__main__":
    process_csv_files()
