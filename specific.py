import os
import sys
import pymysql
import re

# Function to extract database configuration from wp-config.php
def extract_db_config(wp_config_path):
    db_config = {}
    with open(wp_config_path, 'r') as f:
        for line in f:
            match = re.match(r"define\('DB_(NAME|USER|PASSWORD|HOST)',\s*'(.*)'\);", line)
            if match:
                db_config[match.group(1).lower()] = match.group(2)
    return db_config

# Search for specific URLs within the post content and meta fields of WordPress sites.
def search_for_urls_in_wordpress(sites_directory, target_url):
    links_found = False  # Flag to track if any links are found
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

                        # Search for the target URL in post content
                        cursor.execute("SELECT ID, post_content FROM wp_posts WHERE post_content LIKE %s", ('%' + target_url + '%',))
                        posts = cursor.fetchall()
                        for post_id, post_content in posts:
                            if target_url in post_content:
                                print(f"Found URL {target_url} in post content for site: {site}")
                                print(f"Post ID: {post_id}")
                                links_found = True

                        # Search for the target URL in post meta values
                        cursor.execute("SELECT post_id, meta_key, meta_value FROM wp_postmeta WHERE meta_value LIKE %s", ('%' + target_url + '%',))
                        metas = cursor.fetchall()
                        for post_id, meta_key, meta_value in metas:
                            if target_url in meta_value:
                                print(f"Found URL {target_url} in post meta for site: {site}")
                                print(f"Post ID: {post_id}, Meta Key: {meta_key}")
                                links_found = True

                        cursor.close()
                        connection.close()
                    except pymysql.Error as e:
                        print(f"Error searching for URLs for site: {site}")
                        print(f"Error details: {e}")

    if not links_found:
        print(f"No links matching the specified URL ({target_url}) were found in any WordPress site.")
