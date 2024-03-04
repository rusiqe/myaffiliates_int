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

                        # Search for the target URL in post content
                        query = "SELECT ID, post_content FROM wp_posts WHERE post_content LIKE %s"
                        print(f"Executing query: {query}")
                        cursor.execute(query, ('%' + target_url + '%',))
                        posts = cursor.fetchall()
                        print(f"Query returned {len(posts)} results")
                        for post_id, post_content in posts:
                            if target_url in post_content:
                                print(f"Found URL {target_url} in post content for site: {site}")
                                print(f"Post ID: {post_id}")

                        # Search for the target URL in post meta values
                        query = "SELECT post_id, meta_key, meta_value FROM wp_postmeta WHERE meta_value LIKE %s"
                        print(f"Executing query: {query}")
                        cursor.execute(query, ('%' + target_url + '%',))
                        metas = cursor.fetchall()
                        print(f"Query returned {len(metas)} results")
                        for post_id, meta_key, meta_value in metas:
                            if target_url in meta_value:
                                print(f"Found URL {target_url} in post meta for site: {site}")
                                print(f"Post ID: {post_id}, Meta Key: {meta_key}")

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
