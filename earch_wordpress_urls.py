import os
import sys
import pymysql
import re

# Extracts the database configuration from the given WordPress wp-config.php file.
def extract_db_config(wp_config_path):
    # Same as before

# Search for specific URLs within the post content and meta fields of WordPress sites.
def search_for_urls_in_wordpress(sites_directory, url_pattern):
    for site in os.listdir(sites_directory):
        site_path = os.path.join(sites_directory, site)
        if os.path.isdir(site_path):
            wp_config_path = os.path.join(site_path, 'wp-config.php')
            if os.path.isfile(wp_config_path):
                db_config = extract_db_config(wp_config_path)
                if db_config:
                    db_host, db_user, db_password, db_name = db_config
                    try:
                        connection = pymysql.connect(host=db_host, user=db_user, password=db_password, db=db_name)
                        cursor = connection.cursor()

                        # Search for URLs in post content
                        cursor.execute("SELECT ID, post_content FROM wp_posts WHERE post_content REGEXP %s", (url_pattern,))
                        posts = cursor.fetchall()
                        for post in posts:
                            post_id, post_content = post
                            # Check if the post content contains the URL pattern
                            if re.search(url_pattern, post_content):
                                print(f"Found URL in post content for site: {site}")
                                print(f"Post ID: {post_id}")

                        # Search for URLs in post meta values
                        cursor.execute("SELECT post_id, meta_key, meta_value FROM wp_postmeta WHERE meta_value REGEXP %s", (url_pattern,))
                        metas = cursor.fetchall()
                        for meta in metas:
                            post_id, meta_key, meta_value = meta
                            # Check if the meta value contains the URL pattern
                            if re.search(url_pattern, meta_value):
                                print(f"Found URL in post meta for site: {site}")
                                print(f"Post ID: {post_id}, Meta Key: {meta_key}")

                        cursor.close()
                        connection.close()
                    except pymysql.Error as e:
                        print(f"Error searching for URLs for site: {site}")
                        print(f"Error details: {e}")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python search_wordpress_urls.py <sites_directory> <url_pattern>")
        sys.exit(1)

    sites_directory = sys.argv[1]
    url_pattern = sys.argv[2]

    search_for_urls_in_wordpress(sites_directory, url_pattern)