"""Learnings Queries."""
import mysql.connector
# import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import math
import warnings
import os
from dotenv import load_dotenv
from queries import get_query_by_name, get_all_queries
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
        self.my_db = mysql.connector.connect(
            host=ihost,
            user=iuser,
            password=ipass,
            database=idb
            )

    def __constuct_pie(self, labels, sizes, title) -> None:
        """
        Generate a pie chart.

        Pie charts require different syntax than regular charts,
        requiring seperated fxn.

        :param labels: text to describe each slice
        :type labels: str
        :param sizes: data
        :type sizes: ArrayLike
        :param title: Title of pie chart
        :type title: str
        """
        color = cm.viridis(np.linspace(0, 1, len(sizes)))
        plt.pie(sizes, labels=labels, colors=color, autopct='%1.1f%%')
        plt.axis("equal")
        plt.title(title)
        plt.show(block=False)

    def __new_graph(self, *axes, **kwargs) -> None:
        r"""
        Make Graph with matplotlib.

        :param \*axes: captures all axes, x and y included.
            Must use positional args.
        :type \*axes: Unpack[list]
        :param \*\*kwargs: captures all kwargs to format and select graph.
            Must use keyword args.
        :type \*\*kwargs: dict[str, str | tuple]
        :rtype: None
        :meta private:
        """
        # seperate xaxis and yaxes
        xaxis: list = []
        yaxes: list[list] = []
        for idx, axis in enumerate(axes):
            assert type(axis) is list, "All axes must be type list."
            if idx == 0:
                xaxis = axis
                continue
            yaxes.append(axis)

        assert len(yaxes) > 0, "You must have at least one series."

        # custom size of graph on monitor
        if "figsize" in kwargs:
            assert type(kwargs["figsize"] is tuple), \
                "figsize type must be tuple."
        plt.figure(figsize=kwargs["figsize"]) if "figsize" in kwargs \
            else plt.figure()

        # need pie chart
        if kwargs["graphType"] == plt.pie:
            self.__constuct_pie(xaxis, yaxes[0], kwargs["title"])
            return

        # plot series
        assert "graphType" in kwargs, "Graph must have type."
        graph = kwargs["graphType"]

        # assign names for each series(displayed on legend)
        if len(yaxes) > 1:
            for idx, yaxis in enumerate(yaxes):
                graph(xaxis, yaxis, label=kwargs["colNames"][idx])
        else:
            # only one sereis, no need for labels
            graph(xaxis, *yaxes)
        # more formatting
        for key, val in kwargs.items():
            match key:
                case "ybounds":
                    # ymin and ymax on graph
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
                # these keys were used earlier
                case "figsize":
                    continue
                case "graphType":
                    continue
                case "colNames":
                    continue
                case _:
                    raise TypeError("keyword arguement not supported")
        plt.xticks(rotation=45)
        plt.tight_layout()
        if len(yaxes) > 1:
            plt.legend()
        plt.show(block=False)

    def __execute_cursor(self, query_name: str,
                         query_format: dict[str, str]) -> None:
        r"""Fetch Query from MySQL DB.

        Fetches query by name provided and formats response into something
        parsable by matplotlib.

        :param query_name: Name of query to fetch.
            Queries created and referenced in `queries.py`
        :type query_name: str
        :param query_format: kwargs for filling placeholder values
            in `query.full_query`
        :type query_format: dict[str, str]
        :rtype: None
        :meta private:
        """
        # Create Cursor object and get query
        cursor = self.my_db.cursor(buffered=True)
        query = get_query_by_name(query_name)
        assert query is not None, "Invalid query name, is query included in\
            ALL_QUERIES?"
        if query_format is None and query.require_formatting:
            raise ValueError("Queries that have placeholder values need \
                                 formatting.")

        # Add formatting if required and execute query
        if query.require_formatting:
            if query_format == {} or query_format is None:
                cursor.execute(
                    query.full_query.format(**query.default_formatting))
            else:
                cursor.execute(query.full_query.format(**query_format))
        else:
            cursor.execute(query.full_query)
        cursor.fetchall

        assert cursor.rowcount > 0, "Invalid Query, check formatting"

        # gets y axis column names(first element in for xaxis)
        # Legend of graph are names of columns
        ycolumn_names = [ele[0] for idx, ele in enumerate(cursor.description)
                         if idx != 0]
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
        # iterate over every column except the first(x axis)
        iter_cols = iter(sep_columns)
        next(iter_cols)
        for col in iter_cols:
            try:
                max_val.append(float(max(col)))
            except ValueError:
                pass
            except TypeError:
                pass
        # dont use histogram
        graph_types = {"bar": plt.bar, "line": plt.plot,
                       "histo": plt.hist, "pie": plt.pie}

        self.__new_graph(
                    *sep_columns,
                    ybounds=(0, math.ceil(float(max(max_val) * 1.5))),
                    colNames=ycolumn_names,
                    xlabel=query.xlabel,
                    ylabel=query.ylabel,
                    title=query.query_name,
                    graphType=graph_types[query.graph_type]
                    )
        cursor.close()

    def execute(self, query_name, **query_format) -> None:
        r"""Execute Query with name `query_name`.

        :param query_name: Name of query in :class:`MySQLQuery`
        :type query_name: str
        :param \*\*query_format: kwargs for filling query placeholder values
            `query.full_query` if it is required
        :type \*\*query_format: dict[str, str]
        :rtype: None
        :meta public:
        """
        if self.my_db.is_connected():
            self.__execute_cursor(query_name, query_format)


if __name__ == "__main__":
    warnings.filterwarnings("ignore")

    load_dotenv(".mysql.env", verbose=True)

    # change user and pass as applicable
    my_db = MySQLDatabase("localhost",
                          "readonly",
                          os.getenv("MYSQL_READ"),
                          "sakila"
                          )

    # add kwargs for formatting when required
    # Replace 1st arg to switch query called.
    # Can call execute multiple times in sequence

    # current method executes all queries sequentially.
    # Remove generator and for loop to specifically call select queries
    query_gen = get_all_queries()
    try:
        for query in query_gen:
            my_db.execute(query)
    except AssertionError as e:
        print(e.__class__.__name__, e, sep='\n')
    except ValueError as e:
        print(e.__class__.__name__, e, sep='\n')
    except KeyError as e:
        print(e.__class__.__name__, e, "Check query formatting", sep='\n')

    input("Press any key to continue...")
