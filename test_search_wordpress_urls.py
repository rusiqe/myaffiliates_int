import unittest
from specific import search_for_url_in_wordpress

class TestSearchWordpressUrls(unittest.TestCase):

    def test_search_url_in_post_content(self):
        # Mock data
        sites_directory = 'test_data' 
        target_url = 'http://example.com'
        expected_post_id = 123

        # Call function
        search_for_url_in_wordpress(sites_directory, target_url)

        # Assert URL found in expected post
        self.assertIn('Found URL http://example.com in post content for site: testsite', self.output)
        self.assertIn('Post ID: 123', self.output)

    def test_search_url_in_post_meta(self):
        # Mock data
        sites_directory = 'test_data'
        target_url = 'http://example.com'
        expected_post_id = 456
        expected_meta_key = 'test_meta_key'

        # Call function 
        search_for_url_in_wordpress(sites_directory, target_url)

        # Assert URL found in expected post meta
        self.assertIn('Found URL http://example.com in post meta for site: testsite', self.output) 
        self.assertIn('Post ID: 456, Meta Key: test_meta_key', self.output)

    def test_database_connection_error(self):
        # Mock data
        sites_directory = 'test_data'
        target_url = 'http://example.com'

        # Patch pymysql to raise an error
        with patch('pymysql.connect') as mock_connect:
            mock_connect.side_effect = pymysql.Error()

            # Call function
            search_for_url_in_wordpress(sites_directory, target_url)

            # Assert error handled correctly
            self.assertIn('Error searching for URL for site: testsite', self.output)
            self.assertIn('Error details:', self.output)

