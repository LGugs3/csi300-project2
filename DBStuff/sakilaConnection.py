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


class MySQLDatabase:
    """Encapsulates Database operations.

    :param my_db: Database object that fetches and returns MySQL Queries
    :type my_db: PooledMySQLConnection | MySQLConnectionAbstract
    """

    def __init__(self, ihost: str, iuser: str, ipass: str, idb: str):
        """Construct class.

        :param ihost: Database host
        :type ihost: str
        :param iuser: User to log into db with
        :type iuser: str
        :param ipass: password for `iuser`
        :type ipass: str
        :param idb: Name of database
        :type idb: str
        """
        # change user and pass as applicable
        self.my_db = mysql.connector.connect(
            host=ihost,
            user=iuser,
            password=ipass,
            database=idb
            )

    def __new_graph(self, *axes, **labels) -> None:
        r"""
        Make Bar Graph.

        :param \*axes: captures all axes, x and y included.
            Must use positional args.
        :type \*axes: Unpack[list]
        :param \*\*labels: captures all labels to format and select graph.
            Must use keyword args.
        :type \*\*labels: dict[str, str | tuple]
        :rtype: None
        :meta private:
        """
        xaxis: list = []
        yaxes: list[list] = []
        for idx, axis in enumerate(axes):
            assert type(axis) is list, "All axes must be type list."
            if idx == 0:
                xaxis = axis
                continue
            yaxes.append(axis)

        assert len(yaxes) > 0, "You must have at least one series."

        if "figsize" in labels:
            assert type(labels["figsize"] is tuple), \
                "figsize type must be tuple."
        plt.figure(figsize=labels["figsize"]) if "figsize" in labels \
            else plt.figure()
        colors = cm.viridis(np.linspace(0, 1, len(xaxis)))

        assert "graphType" in labels, "Graph must have type."
        graph = labels["graphType"]
        if len(yaxes) > 1:
            for idx, yaxis in enumerate(yaxes):
                graph(xaxis, yaxis, color=colors, label=labels["ylabel"+idx])
        else:
            graph(xaxis, *yaxes, color=colors)
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
                case "graphType":
                    continue
                case _:
                    raise TypeError("keyword arguement not supported")
        plt.xticks(rotation=45)
        plt.tight_layout()
        if len(yaxes) > 1:
            plt.legend()
        plt.show(block=False)

    def __execute_cursor(self, query_name: str,
                         formatting: dict[str, str]) -> None:
        r"""Fetch Query from MySQL DB.

        Fetches query by name provided and formats response into something
        parsable by matplotlib.

        :param query_name: Name of query to fetch.
            Queries created and referenced in `queries.py`
        :type query_name: str
        :param formatting: kwargs for filling placeholder values
            in `query.full_query`
        :type formatting: dict[str, str]
        :rtype: None
        :meta private:
        """
        # Create Cursor object and get query
        cursor = self.my_db.cursor()
        query = get_query_by_name(query_name)
        assert query is not None, "Invalid query name"
        assert formatting is not None and query.require_formatting, \
            "queries that have placeholder values needs formatting."

        # Add formatting if required and execute query
        if query.require_formatting:
            cursor.execute(query.full_query.format(**formatting))
        else:
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
            except TypeError:
                pass
        graph_types = {"bar": plt.bar, "line": plt.plot,
                       "histo": plt.hist, "pie": plt.pie}

        self.__new_graph(
                    *sep_columns,
                    ybounds=(0, math.ceil(float(max(max_val) * 1.5))),
                    xlabel="Customer Name",
                    ylabel="Average Loan Period",
                    title=query.query_name,
                    figsize=(10, 6),
                    graphType=graph_types[query.graph_type]
                    )

    def execute(self, query_name, **formatting) -> None:
        r"""Execute Query with name `query_name`.

        :param query_name: Name of query in :class:`MySQLQuery`
        :type query_name: str
        :param \*\*formatting: kwargs for formatting
            `query.full_query` if it is required
        :type \*\*formatting:
        :rtype: None
        :meta public:
        """
        # Replace 2nd arg to switch query called.
        # Can call execute_cursor multiple times in sequence
        if self.my_db.is_connected():
            self.__execute_cursor(query_name, formatting)


if __name__ == "__main__":
    warnings.filterwarnings("ignore")

    load_dotenv(".mysql.env", verbose=True)

    my_db = MySQLDatabase("localhost",
                          "readonly",
                          os.getenv("MYSQL_READ"),
                          "sakila"
                          )

    # add kwargs for formatting if required
    my_db.execute("Specified Rental Activity", day=25)
    input("Press any key to continue...")
