# lind links in a wordpress database by searching for urls in all site content, use the config files and credentials in 
# server site folders to cycle through all discovered databases and site folders 

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

# Function to search for URLs within WordPress content and metadata
def search_for_urls_in_wordpress(sites_directory, url_pattern):
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

                        # Search for URLs in post content
                        cursor.execute("SELECT ID, post_content FROM wp_posts WHERE post_content REGEXP %s", (url_pattern,))
                        posts = cursor.fetchall()
                        for post_id, post_content in posts:
                            if re.search(url_pattern, post_content):
                                print(f"Found URL in post content for site: {site}")
                                print(f"Post ID: {post_id}")

                        # Search for URLs in post meta values
                        cursor.execute("SELECT post_id, meta_key, meta_value FROM wp_postmeta WHERE meta_value REGEXP %s", (url_pattern,))
                        metas = cursor.fetchall()
                        for post_id, meta_key, meta_value in metas:
                            if re.search(url_pattern, meta_value):
                                print(f"Found URL in post meta for site: {site}")
                                print(f"Post ID: {post_id}, Meta Key: {meta_key}")

                        cursor.close()
                        connection.close()
                    except pymysql.Error as e:
                        print(f"Error searching for URLs for site: {site}")
                        print(f"Error details: {e}")
                    
                    else:
                        print(f"Error searching for URLs for site: {site}")
                        print(f"Error details: {e}")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python find_links.py <sites_directory> <url_pattern>")
        sys.exit(1)

    sites_directory = sys.argv[1]
    url_pattern = sys.argv[2]

    search_for_urls_in_wordpress(sites_directory, url_pattern)
)