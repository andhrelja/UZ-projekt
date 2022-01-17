import os
import mappings

BASE_DIR = os.path.dirname(__file__)
API_BASE_URL = 'https://hr.n1info.com/'
SITE_NAME = 'data/'

CATALOG_LOADS = [
    {
        'uri': 'wp-json/wp/v2/categories',
        'params': {
            'per_page': 50
        },
        'json_file_name': 'json/categories.json',
        'csv_file_name': 'csv/categories.csv',
        'mapping': mappings.CATEGORIES_MAPPING
    },
    {
        'uri': 'wp-json/wp/v2/tags',
        'params': {
            'per_page': 50
        },
        'json_file_name': 'json/tags.json',
        'csv_file_name': 'csv/tags.csv',
        'mapping': mappings.TAGS_MAPPING
    }
]

RECURRING_LOADS = [
    {
        'uri': 'wp-json/wp/v2/uc-all-posts/',
        'params': {
            'per_page': 50
        },
        'json_file_name': 'json/posts.json',
        'csv_file_name': 'csv/posts.csv',
        'mapping': mappings.CUSTOM_POSTS_MAPPING
    },
]

DETAILED_LOADS = [
    {
        'uri': 'wp-json/wp/v2/posts/{}/',
        'in_csv_file_name': 'csv/posts.csv',
        'json_file_name': 'json/posts-detail.json',
        'csv_file_name': 'csv/posts-detail.csv',
        'mapping': mappings.CUSTOM_POST_MAPPING
    },
]