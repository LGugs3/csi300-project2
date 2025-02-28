"""Hold Stuff for Queries."""


class MySQLQuery:
    """
    Contains All Query Info.

    Parameters
    ----------
    section_num: int
        matches section number on packet
    query_name: str
        unique name to fetch object by
    full_query: str
        MySQL query that :class:``mysql.connector`` uses
    num_columns_returned: int
        Num of columns returned by query
    graph_type: str
        type of graph used to visualize data
    require_formatting: bool
        If ``full_query`` has placeholder values
    """

    def __init__(
            self,
            section_num: int,
            query_name: str,
            full_query: str,
            num_columns_returned: int,
            graph_type: str = "bar",
            require_formatting: bool = False
            ):
        """:no-index:Init Custom Query class."""
        self.section_num = section_num
        self.query_name = query_name
        self.full_query = full_query
        self.num_columns_returned = num_columns_returned
        self.graph_type = graph_type
        self.require_formatting = require_formatting

    def __str__(self):
        """Return :variable:`self.full_query`."""
        return self.full_query


querystr1 = """
SELECT CONCAT(c.first_name, ' ', c.last_name) AS full_name,
AVG(TIMESTAMPDIFF(DAY, r.rental_date, r.return_date))
AS avg_loan_period
FROM rental r
JOIN customer c ON r.customer_id = c.customer_id
GROUP BY c.first_name, c.last_name
ORDER BY avg_loan_period DESC
LIMIT 100;
"""

querystr2 = """
SELECT customer_id, COUNT(rental_id) AS num_rentals
FROM rental
GROUP BY customer_id;
"""

querystr3 = """
SELECT DATE(rental_date), COUNT(DAY(rental_date)) AS num_rentals
FROM rental
WHERE DAY(rental_date) = {day}
GROUP BY DATE(rental_date);
"""
# construct all queries.
# python doesnt like the type hints missing here for some reason
query1: MySQLQuery = MySQLQuery(1, "Average Rental Duration", querystr1, 2)
query2: MySQLQuery = MySQLQuery(1, "Num rentals per customer", querystr2, 2)
query3: MySQLQuery = MySQLQuery(1, "Specified Rental Activity", querystr3, 1,
                                "bar", True)

# Contains all queries
ALL_QUERIES: list[MySQLQuery] = [query1, query2, query3]


def get_query_by_name(name: str) -> MySQLQuery | None:
    """Get query by name.

    :param name: name of query. Matches ``MySQLQuery.query_name``
    :type name: str
    :return: Returns :class:`MySQLQuery` if one is found.
    :rtype: MySQLQuery | None
    """
    for query in ALL_QUERIES:
        if query.query_name == name:
            return query
    return None
