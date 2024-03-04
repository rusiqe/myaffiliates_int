import os
import sys
import pymysql

# Function to extract database configuration from wp-config.php
def extract_db_config(wp_config_path):
    db_config = {}
    with open(wp_config_path, 'r') as f:
        for line in f:
            if line.strip().startswith(('define(', '$')):
                parts = line.strip().split(', ')
                if len(parts) == 2:
                    db_config[parts[0].split('(')[-1][1:-1]] = parts[1][1:-2]
    return db_config

# Search for specific URLs within the post content and meta fields of WordPress sites.
def search_for_urls_in_wordpress(sites_directory, target_url):
    links_found = False  # Flag to track if any links are found
    tables_searched = set()  # Set to store the names of tables searched
    for site in os.listdir(sites_directory):
        site_path = os.path.join(sites_directory, site)
        if os.path.isdir(site_path):
            wp_config_path = os.path.join(site_path, 'wp-config.php')
            if os.path.isfile(wp_config_path):
                db_config = extract_db_config(wp_config_path)
                if db_config:
                    try:
                        connection = pymysql.connect(**db_config)
                        cursor = connection.cursor()

                        # Check the tables in the database
                        cursor.execute("SHOW TABLES")
                        tables = cursor.fetchall()
                        table_names = [table[0] for table in tables]

                        # Search for the target URL in post content if wp_posts table exists
                        if 'wp_posts' in table_names:
                            cursor.execute("SELECT ID, post_content FROM wp_posts WHERE post_content LIKE %s", ('%' + target_url + '%',))
                            posts = cursor.fetchall()
                            tables_searched.add('wp_posts')  # Record table searched
                            for post_id, post_content in posts:
                                if target_url in post_content:
                                    print(f"Found URL {target_url} in post content for site: {site}")
                                    print(f"Post ID: {post_id}")
                                    links_found = True

                        # Search for the target URL in post meta values if wp_postmeta table exists
                        if 'wp_postmeta' in table_names:
                            cursor.execute("SELECT post_id, meta_key, meta_value FROM wp_postmeta WHERE meta_value LIKE %s", ('%' + target_url + '%',))
                            metas = cursor.fetchall()
                            tables_searched.add('wp_postmeta')  # Record table searched
                            for post_id, meta_key, meta_value in metas:
                                if target_url in meta_value:
                                    print(f"Found URL {target_url} in post meta for site: {site}")
                                    print(f"Post ID: {post_id}, Meta Key: {meta_key}")
                                    links_found = True

                        cursor.close()
                        connection.close()
                    except pymysql.Error as e:
                        print(f"Error connecting to database or executing query for site: {site}")
                        print(f"Error details: {e}")

    if not links_found:
        print(f"No links matching the specified URL ({target_url}) were found in any WordPress site.")

    print("Tables Searched:", ', '.join(tables_searched))

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python specific.py <sites_directory> <target_url>")
        sys.exit(1)

    sites_directory = sys.argv[1]
    target_url = sys.argv[2]

    search_for_urls_in_wordpress(sites_directory, target_url)
