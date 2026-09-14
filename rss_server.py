import psycopg2
from mcp.server.mcpserver import MCPServer

DB_CONFIG = {
    "host": "localhost",
    "port": 5433,
    "database": "rss_aggregator",
    "user": "postgres",
    "password": "postgres"
}

def get_conn():
    conn = psycopg2.connect(
        host="localhost",
        port=5433,
        database="rss_aggregator",
        user="postgres",
        password="postgres"
    )
    return conn


def _rows_to_text(rows):
    """Format DB rows as plain text for Claude to read."""
    if not rows:
        return "No articles found."
    lines = []
    for source, title, link, published_at in rows:
        when = published_at.strftime("%Y-%m-%d %H:%M UTC") if published_at else "unknown date"
        lines.append(f"[{when}] ({source}) {title} - {link}")
    return "\n".join(lines)


mcp = MCPServer("rss_aggregator")

@mcp.tool()
def fetch_all_articles():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT source, title, link, published_at "
            "FROM articles ORDER BY COALESCE(published_at, fetched_at) DESC LIMIT 1000",  
        )
        rows = cur.fetchall()

    return _rows_to_text(rows)

@mcp.tool()
def fetch_articles_by_source(source):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT source, title, link, published_at "
            "FROM articles WHERE source = %s ORDER BY COALESCE(published_at, fetched_at) DESC LIMIT 250",  
            (source,)
        )
        rows = cur.fetchall()

    return _rows_to_text(rows)

@mcp.tool()
def fetch_articles_by_date_range(start_date, end_date):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT source, title, link, published_at "
            "FROM articles WHERE published_at BETWEEN %s AND %s ORDER BY COALESCE(published_at, fetched_at) DESC",  
            (start_date, end_date)
        )
        rows = cur.fetchall()

    return _rows_to_text(rows)

@mcp.tool()
def search_articles_by_keywords(keywords):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT source, title, link, published_at "
            "FROM articles WHERE title ILIKE %s ORDER BY COALESCE(published_at, fetched_at) DESC",  
            (f'%{keywords}%',)
        )
        rows = cur.fetchall()

    return _rows_to_text(rows)

if __name__ == "__main__":
    mcp.run()
