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
    xlabel: str
        describes xaxis on graph
    ylabel: str
        describes yaxis on graph
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
            xlabel: str,
            ylabel: str,
            num_columns_returned: int,
            graph_type: str = "bar",
            require_formatting: bool = False
            ):
        """:no-index:Init Custom Query class."""
        self.section_num = section_num
        self.query_name = query_name
        self.full_query = full_query
        self.xlabel = xlabel
        self.ylabel = ylabel
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
SELECT DATE(rental_date) AS rental_date, COUNT(DAY(rental_date)) AS num_rentals
FROM rental
WHERE DAY(rental_date) = {day}
GROUP BY DATE(rental_date);
"""

querystr4 = """
SELECT f.rating, COUNT(r.rental_id) AS num_rentals
FROM rental r
JOIN inventory i ON r.inventory_id = i.inventory_id
JOIN film f ON i.film_id = f.film_id
GROUP BY f.rating;
"""
# construct all queries.
# python doesnt like the type hints missing here for some reason
query1: MySQLQuery = MySQLQuery(1, "AvgRentalDur", querystr1, "Customer Name",
                                "Average Rental Period", 2)
query2: MySQLQuery = MySQLQuery(1, "RentalNumPerCustomer", querystr2,
                                "Customer ID", "Number of Rentals", 2)
query3: MySQLQuery = MySQLQuery(1, "SpecifiedRentalActivity", querystr3,
                                "Date of Rental", "Number of Rentals",
                                1, "bar", True)
query4: MySQLQuery = MySQLQuery(2, "AggregatedRentalPerRating", querystr4,
                                "Rating", "Number Rentals", 2, "pie")

# Contains all queries
ALL_QUERIES: list[MySQLQuery] = [query1, query2, query3, query4]


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
