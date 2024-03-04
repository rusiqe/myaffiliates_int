import os
import sys
import pymysql
import re

# Extracts the database configuration from the given WordPress wp-config.php file.
def extract_db_config(wp_config_path):
    config_lines = open(wp_config_path).readlines()

    db_host = re.search(r"define\(\s*'DB_HOST',\s*'(.*)'\s*\);", ''.join(config_lines), re.IGNORECASE)
    db_user = re.search(r"define\(\s*'DB_USER',\s*'(.*)'\s*\);", ''.join(config_lines), re.IGNORECASE)
    db_password = re.search(r"define\(\s*'DB_PASSWORD',\s*'(.*)'\s*\);", ''.join(config_lines), re.IGNORECASE)
    db_name = re.search(r"define\(\s*'DB_NAME',\s*'(.*)'\s*\);", ''.join(config_lines), re.IGNORECASE)

    if db_host and db_user and db_password and db_name:
        return db_host.group(1), db_user.group(1), db_password.group(1), db_name.group(1)
    else:
        return None

# Search for the target URL in the post content and post meta of WordPress sites.
def search_for_url_in_wordpress(sites_directory, target_url):
    for site in os.listdir(sites_directory):
        site_path = os.path.join(sites_directory, site)
        if os.path.isdir(site_path):
            wp_config_path = os.path.join(site_path, 'wp-config.php')
            if os.path.isfile(wp_config_path):
                db_config = extract_db_config(wp_config_path)
                if db_config:
                    db_host, db_user, db_password, db_name = db_config
                    print(f"Connecting to database {db_name} at {db_host} with user {db_user}")
                    try:
                        connection = pymysql.connect(host=db_host, user=db_user, password=db_password, db=db_name)
                        cursor = connection.cursor()

                        # Get all tables in the database
                        cursor.execute("SHOW TABLES")
                        tables = cursor.fetchall()

                        for table in tables:
                            table = table[0]
                            print(f"Searching table {table}")

                            # Get all text-based columns in the table
                            cursor.execute(f"SHOW COLUMNS FROM {table} WHERE Type LIKE '%%text%%' OR Type LIKE '%%varchar%%'")
                            columns = cursor.fetchall()

                            for column in columns:
                                column = column[0]
                                print(f"Searching column {column}")

                                # Search for the target URL in the column
                                query = f"SELECT {column} FROM {table} WHERE {column} LIKE %s"
                                print(f"Executing query: {query}")
                                cursor.execute(query, ('%' + target_url + '%',))
                                results = cursor.fetchall()
                                print(f"Query returned {len(results)} results")

                                for result in results:
                                    if target_url in result[0]:
                                        print(f"Found URL {target_url} in table {table}, column {column} for site: {site}")

                        cursor.close()
                        connection.close()
                    except pymysql.Error as e:
                        print(f"Error searching for URL for site: {site}")
                        print(f"Error details: {e}")

if __name__ == '__main__':
    # ... same as before ...if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python search_wordpress_urls.py <sites_directory> <target_url>")
        sys.exit(1)

    sites_directory = sys.argv[1]
    target_url = sys.argv[2]

    search_for_url_in_wordpress(sites_directory, target_url)
