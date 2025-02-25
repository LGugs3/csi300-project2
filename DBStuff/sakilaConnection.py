"""Learnings Queries."""
import mysql.connector
# import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import math
import warnings
import os
from dotenv import load_dotenv
from queries import get_query_by_name
import numpy as np


def new_bar_graph(*axes, **labels) -> None:
    """
    Make bar graph.

    Accept axes and formatting labels and put them
    into matplotlib to create a bar graph.

    Parameters
    ----------
        `*axes` :
            captures all axes, x and y included.
            Must use positional args.
        `**labels` :
            captures all labels to format graph.
            Must use keyword args.

    Returns
    -------
    *None*
    """
    xaxis: list = []
    yaxes: list[list] = []
    for idx, axis in enumerate(axes):
        assert type(axis) is list, "All axes must be type list"
        if idx == 0:
            xaxis = axis
            continue
        yaxes.append(axis)

    if "figsize" in labels:
        assert type(labels["figsize"] is tuple), "figsize type must be tuple."
    plt.figure(figsize=labels["figsize"]) if "figsize" in labels \
        else plt.figure()
    colors = cm.viridis(np.linspace(0, 1, len(xaxis)))

    if len(yaxes) > 1:
        for idx, yaxis in enumerate(yaxes):
            plt.bar(xaxis, yaxis, color=colors, label=labels["ylabel"+idx])
    else:
        plt.bar(xaxis, *yaxes, color=colors)
    for key, val in labels.items():
        match key:
            case "ybounds":
                assert type(val[0]) in (int, float) and \
                    type(val[1]) in (int, float), \
                    "yaxis bounds must be of type int"
                plt.ylim(val[0], val[1])
            case "xlabel":
                assert type(val) is str, "xlabel must be string"
                plt.xlabel(val)
            case "ylabel":
                assert type(val) is str, "xlabel must be string"
                plt.ylabel(val)
            case "title":
                assert type(val) is str, "xlabel must be string"
                plt.title(val)
            case "figsize":
                continue
            case _:
                raise TypeError("keyword arguement not supported")
    plt.xticks(rotation=45)
    plt.tight_layout()
    if len(yaxes) > 1:
        plt.legend()
    plt.show(block=False)


def execute_cursor(my_db, query_name: str) -> None:
    """
    Fetch Query from MySQL DB.

    Fetches query by name provided and formats response into something
    parsable by matplotlib.

    Parameters
    ----------
    my_db : CMySQLConnection | MySQLConnection
        MySQLConnector object.
        Reference to database to query.
    query_name : string
        Name of query to fetch.
        Queries created and referenced in `queries.py`

    Returns
    -------
    *None*
    """
    # Create Cursor object and get query
    cursor = my_db.cursor()
    query = get_query_by_name(query_name)
    assert query is not None, "Invalid query name"
    # Execute query
    cursor.execute(query.full_query)
    cursor.fetchall

    # Prepare lists to swap columns and rows
    all_columns: list[list] = []
    all_columns = [[col for col in i] for i in cursor]
    sep_columns = [[] for i in all_columns[0]]
    # reverse columns and rows
    for i in all_columns:
        for idx, nest in enumerate(i):
            sep_columns[idx].append(nest)

    # get max value to set y bounds
    max_val: list[float] = []
    for col in sep_columns:
        try:
            max_val.append(float(max(col)))
        except ValueError:
            pass

    new_bar_graph(
                *sep_columns,
                ybounds=(0, math.ceil(float(max(max_val) * 1.5))),
                xlabel="Customer Name",
                ylabel="Average Loan Period",
                title="Average Loan Period for Every Customer",
                figsize=(10, 6)
                )


if __name__ == "__main__":
    warnings.filterwarnings("ignore")

    load_dotenv(".mysql.env", verbose=True)

    # change user and pass as applicable
    my_db = mysql.connector.connect(
        host="localhost",
        user="readonly",
        password=os.getenv("MYSQL_READ"),
        database="sakila"
        )
    print(type(my_db))

    # Replace 2nd arg to switch query called. Can call execute_cursor multiple
    # times in sequence
    if my_db.is_connected():
        execute_cursor(my_db, "Average Rental Duration")
        input("Press any key to continue...")
