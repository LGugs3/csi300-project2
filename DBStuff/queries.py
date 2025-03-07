"""Hold Stuff for Queries."""


class MySQLQuery:
    """
    Contains All Query Info.

    Parameters
    ----------
    section_num: float
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
            section_num: float,
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
SELECT c.name, COUNT(r.rental_id) AS num_rentals
FROM rental r
JOIN inventory i on r.inventory_id = i.inventory_id
JOIN film_category fc on i.film_id = fc.film_id
JOIN category c on c.category_id = fc.category_id
GROUP BY c.name;
"""

querystr5 = """
SELECT name, AVG(count_rentals) AS avg_rentals
FROM (
SELECT c.name, count(DATE(r.rental_date)) as count_rentals
FROM rental r
JOIN inventory i ON r.inventory_id = i.inventory_id
JOIN film_category fc ON i.film_id = fc.film_id
JOIN category c ON c.category_id = fc.category_id
GROUP BY c.name, DATE(r.rental_date)
) AS Z
GROUP BY name;
"""

querystr6 = """
select f.title, count(r.rental_id) as num_rentals
from rental r
JOIN inventory i ON r.inventory_id = i.inventory_id
JOIN film f ON i.film_id = f.film_id
JOIN film_category fc ON i.film_id = fc.film_id
JOIN category c ON c.category_id = fc.category_id
WHERE c.name = "{category}"
GROUP BY f.title
ORDER BY num_rentals DESC
LIMIT 5;
"""

querystr7 = """
select CONCAT(a.first_name, ' ', a.last_name) AS full_name, COUNT(r.rental_id)\
    AS num_rentals
from film f
join film_actor fa ON f.film_id = fa.film_id
JOIN actor a ON fa.actor_id = a.actor_id
JOIN inventory i ON f.film_id = i.film_id
JOIN rental r ON i.inventory_id = r.inventory_id
GROUP BY a.first_name, a.last_name;
"""

querystr8 = """
select CONCAT(a.first_name, ' ', a.last_name) AS full_name, COUNT(r.rental_id)\
    AS num_rentals
from film f
join film_actor fa ON f.film_id = fa.film_id
JOIN actor a ON fa.actor_id = a.actor_id
JOIN inventory i ON f.film_id = i.film_id
JOIN rental r ON i.inventory_id = r.inventory_id
JOIN film_category fc ON f.film_id = fc.film_id
JOIN category c ON fc.category_id = c.category_id
WHERE c.name = "{category}"
GROUP BY a.first_name, a.last_name
ORDER BY num_rentals DESC;
"""

querystr9 = """
SELECT CONCAT(a.first_name, ' ', a.last_name) AS full_name, COUNT(r.rental_id)\
    AS num_rentals
FROM film f
join film_actor fa ON f.film_id = fa.film_id
JOIN actor a ON fa.actor_id = a.actor_id
JOIN inventory i ON f.film_id = i.film_id
JOIN rental r ON i.inventory_id = r.inventory_id
GROUP BY a.first_name, a.last_name
ORDER BY num_rentals DESC
LIMIT 10;
"""

# construct all queries.
# python doesnt like the type hints missing here for some reason
query1: MySQLQuery = MySQLQuery(1.2, "AvgRentalDur", querystr1,
                                "Customer Name", "Average Rental Period", 2)
query2: MySQLQuery = MySQLQuery(1.1, "RentalNumPerCustomer", querystr2,
                                "Customer ID", "Number of Rentals", 2)
query3: MySQLQuery = MySQLQuery(1.3, "SpecifiedRentalActivity", querystr3,
                                "Date of Rental", "Number of Rentals",
                                1, "bar", True)
query4: MySQLQuery = MySQLQuery(2.1, "TotalRentalsPerRating", querystr4,
                                "Rating", "Number Rentals", 2)
query5: MySQLQuery = MySQLQuery(2.2, "AvgRentalRatePerCategory", querystr5,
                                "Category", "Average Rentals per Day", 2)
query6: MySQLQuery = MySQLQuery(2.3, "TopRentalsInCategory", querystr6,
                                "Title of DVD", "Total Rentals", 2,
                                "bar", True)
query7: MySQLQuery = MySQLQuery(3.1, "NumRentalsPerActor", querystr7,
                                "Actor Name", "Number of Rentals", 2)
query8: MySQLQuery = MySQLQuery(3.2, "NumRentalsPerActorInCategory", querystr8,
                                "Actor Name", "Number of Rentals", 2,
                                "bar", True)
query9: MySQLQuery = MySQLQuery(3.3, "TopActorsByRentalCount", querystr9,
                                "Actor Name", "Number of Rentals", 2)

# Contains all queries
ALL_QUERIES: list[MySQLQuery] = [query1, query2, query3, query4, query5,
                                 query6, query7, query8]


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
