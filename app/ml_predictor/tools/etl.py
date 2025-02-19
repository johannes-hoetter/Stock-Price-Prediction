"""
- author: Johannes Hötter (https://github.com/johannes-hoetter)
- version: 1.0
- last updated on: 02/12/2018

This script can be used to do a full etl process on the stock data.
"""


import pandas as pd
import numpy as np
import os
from tqdm import tqdm
import sys

# Custom Modules
from web_crawler import StockDataCrawler
from data_converter import DataConverter
from data_handler import DataHandler

def full_etl(crawler, converter, data_handler, data_dir='../data'):
    """
    Extracts, Transforms and Loads (Saves) Finance Data from the Quandl API.
    Creates the following:
    - one csv file for each stock symbol containing all the finance data
    - one database which has one table for each stock symbol
    - one npz file which contains scaled and converted finance data for each stock symbol. useable for machine learning.
    :param crawler (object from web_crawler.py): WebCrawler
    :param converter (object from data_converter.py): DataConverter
    :param data_handler (object from data_handler.py): DataHandler
    :param data_dir (string): path to the data directory of the project
    :return:
    """

    dl_dir = '{}/raw'.format(data_dir)
    ml_dir = '{}/ml_format'.format(data_dir)
    crawler.download_data(directory=dl_dir)
    print("Start Conversion of Data...")
    for file in tqdm(os.listdir(dl_dir)):
        csv_file = os.path.join(dl_dir, file)
        symbol = csv_file[12:-4] # get the symbol of '../data/raw\{}.csv', where {} is the symbol
        try:
            # get a dataframe from the csv file and convert it into the target shape
            df = pd.read_csv(csv_file)
            df = converter.convert_df(df)
            df = converter.fill_targets(df)

            # scales the values and prepares them for machine learning
            # X and y are numpy arrays which get saved as npz files
            X, y = converter.convert_ml_format(df, symbol)

            # save the dataframe as a table in the DataFrames.db
            data_handler.save_to_db(df, symbol) # will save the data in data/cleaned

            # save the arrays
            data_handler.save_to_npz(X, y, symbol, save_dir=ml_dir)
        except:
            continue
    # Serialize the used objects
    crawler.serialize()
    converter.serialize()
    data_handler.serialize()


def get_sp500_data():
    """
    Gets the table from the Wikipedia Entry to the List of SP500 Companies
    :return pandas dataframe: table containing the stock names
    """
    sp500_data = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
    convert_first_row_as_header(sp500_data)
    return sp500_data    


def convert_first_row_as_header(df):
    """
    Take the first row of a dataframe as its header; INPLACE!
    :param df (pandas dataframe): source
    """
    df.columns = df.iloc[0]
    df.drop(0, axis=0, inplace=True)


if __name__ == '__main__': # if the script is called directly
    sp500_data = get_sp500_data()
    crawler = StockDataCrawler(sp500_data)
    converter = DataConverter()
    data_handler = DataHandler()
    full_etl(crawler, converter, data_handler)