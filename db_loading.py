"""
Creat the table, get data from the api, then filter and upload on the database
"""
import re
import sys
from os.path import basename

import numpy as np
import pandas as pd
import yaml
from numpy import nan
from sodapy import Socrata
from sqlalchemy import Column, MetaData, Table, create_engine
from sqlalchemy.types import BOOLEAN, FLOAT, INTEGER, VARCHAR

##### CONNECT TO DB


def connect_db(_url):
    """
    Get schema and metadata
    Creat columns
    And return connection to db
    """

    with open("schema_db.yaml", "r", encoding="utf-8") as file:
        schema = yaml.safe_load(file)

    meta = MetaData()

    ### CREATION OF COLUMNS

    columns = []
    columns_types = {}
    for column in schema["tables"][0]["columns"]:
        column_name = column["name"]
        column_type = eval(column["type"].upper())
        columns_types[column_name] = column_type
        column_primary_key = column.get("primary_key", False)
        columns.append(Column(column_name, column_type, primary_key=column_primary_key))

    table_name = schema["tables"][0]["name"]

    Table(table_name, meta, *columns)

    ### CONNECT TO DB

    engine = create_engine(_url)

    meta.create_all(engine)

    return table_name, columns_types, engine.connect()


##### DOWNLOAD API DATA


def get_api_data():
    """
    Download data from api
    """

    client = Socrata("data.seattle.gov", None)
    results = client.get("2bpz-gwpy", limit=5000)
    return pd.DataFrame.from_records(results)


##### CLEANING DATA


def cleaning_data(_df):
    """
    Cleaning data
    """

    _df.replace(["NULL", ""], nan, inplace=True)
    _df = _df[_df.compliancestatus == "Compliant"]

    _df.drop(
        columns=[
            "compliancestatus",
            "defaultdata",
            "state",
            "city",
            "datayear",
            "outlier",
        ],
        inplace=True,
    )

    _df.rename(
        columns={"secondlargestpropertyuse": "secondlargestpropertyusetypegfa"},
        inplace=True,
    )

    _df["neighborhood"] = _df["neighborhood"].str.upper()
    _df["neighborhood"] = _df["neighborhood"].str.replace(" NEIGHBORHOODS", "")

    _df.loc[
        _df.propertyname == "Chief Seattle Club/Monterey Lofts", "neighborhood"
    ] = "DOWNTOWN"

    _df.loc[_df.propertyname == "INScape", "neighborhood"] = "GREATER DUWAMISH"

    _df["numberofbuildings"].replace("0", "1", inplace=True)
    _df["numberofbuildings"].fillna("1", inplace=True)

    _df["numberoffloors"].replace(["0", "99"], "1", inplace=True)

    _df.dropna(
        subset=[
            "listofallpropertyusetypes",
            "largestpropertyusetype",
            "totalghgemissions",
        ],
        inplace=True,
    )

    return _df


##### PIVOT


def pivot(_df):
    """
    Pivot data gfa
    """

    col_types = _df["listofallpropertyusetypes"].apply(
        lambda x: re.split(r", (?![^(]*\))", x)
    )
    all_types = np.unique(np.array(col_types.values.sum())).tolist()

    list_rows = []

    for _, row in _df.iterrows():
        row_dict = {
            "osebuildingid": row["osebuildingid"],
            "propertygfatotal": row["propertygfatotal"],
            row["largestpropertyusetype"]: row["largestpropertyusetypegfa"],
        }

        for col in ["secondlargestpropertyusetype", "thirdlargestpropertyusetype"]:
            if type_use := row[col]:
                row_dict[type_use] = row[col + 'gfa']

        list_rows.append(row_dict)

    return pd.DataFrame(list_rows)


##### MAIN


def main(_url):
    """
    Main
    """

    table_name, columns_types, conn = connect_db(_url)

    api_df = get_api_data()

    api_df = cleaning_data(api_df)

    api_df.to_sql(
        table_name, conn, index=False, if_exists="append", dtype=columns_types
    )

    pivot_df = pivot(api_df)

    pivot_df.to_sql('buildings_gfa', conn, index=False)


if __name__ == "__main__":
    argv = sys.argv

    if len(argv) != 2:
        raise Exception(f"Argument error: {basename(__file__)} need an url")

    main(argv[1])
