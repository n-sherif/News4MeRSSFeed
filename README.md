# My RSS Feed
### By Nadim Sherif

To learn more about rss feeds, Ive decideed to make a small local project where I retrieve news from multiple different sources and display them on a simple html site. Sadly I realized that the CNN rss is outdated, so all the news retrieved is from 2023 and before. Luckily the other three work fine!

Additionally, Claude Desktop is hooked up to my server via MCP so queries could be asked directly through that.

![alt text](image.png)

### Setup

1. Install the dependencies:

   ```bash
   pip install flask feedparser psycopg2-binary
   ```

2. Create the database in PostgreSQL (any port works — the default is 5432):

   ```sql
   CREATE DATABASE rss_aggregator;
   ```

3. Create the articles table:

   ```sql
   CREATE TABLE articles (
       id serial PRIMARY KEY,
       source text,
       link text UNIQUE,
       title text,
       summary text,
       article text,
       published_at timestamptz,
       fetched_at timestamptz DEFAULT now()
   );
   ```

4. Create a file called `.env` in the project folder (it's gitignored, so it stays on your machine) with your database credentials:

   ```
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=rss_aggregator
   DB_USER=postgres
   DB_PASSWORD=your_password_here


### How to Run

Running the app is very simple! all you need to do is: 
python app.py

in the project directory and the app will launch. You can either view it on the html, or directly ask Claude to bring articles youd like to view.

![alt text](image-1.png)

### How to Refresh

The feed auto refreshes everytime the app is run, and also on its own everyday at 10am and 10pm.

To refresh the feed manually you run: 
python refresh.py