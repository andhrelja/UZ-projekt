import json
import re

clean_html = re.compile('<.*?>')
filename = 'C:/Users/AndreaHrelja/Documents/Faks/5. godina/3. semestar/UPZ/Scrapeinar/scrape/n1info/json/categories.json'
with open(filename, 'r', encoding='utf-8') as f:
    categories_content = json.load(f)

categories = {
    cat['id']: cat['name'] for cat in categories_content
}

CATEGORIES_MAPPING = lambda content: [{
    'id':               category.get('id'),
    'name':             category.get('name'),
    'description':      category.get('description'),
    'slug':             category.get('description'),
    'count':            category.get('count'),
    'portal_link':      category.get('link'),
    'posts_api_link':   category.get('_links').get('wp:post_type')[0]['href'],
    'self_api_link':    category.get('_links').get('self')[0]['href'],
} for category in content]

TAGS_MAPPING = lambda content: [{
    'id':               tag.get('id'),
    'name':             tag.get('name'),
    'description':      tag.get('description'),
    'slug':             tag.get('description'),
    'count':            tag.get('count'),
    'portal_link':      tag.get('link'),
    'posts_api_link':   tag.get('_links').get('wp:post_type')[0]['href'],
    'self_api_link':    tag.get('_links').get('self')[0]['href'],
} for tag in content]

CUSTOM_POSTS_MAPPING = lambda content, latest_date: [{
    'id':            post.get('id'),
    'date':          latest_date,
    'category_name': post.get('category_name'),
    'site_link':     post.get('link'),
    'api_link':      'https://hr.n1info.com/wp-json/wp/v2/posts/{}/'.format(post.get('id')),
} for post in content]

CUSTOM_POST_MAPPING = lambda content, category_name: {
    'id':               content.get('id'),
    'date':             content.get('date'),
    'title':            re.sub(clean_html, '', content.get('title', {}).get('rendered')),
    'text':             re.sub(clean_html, '', content['content']['rendered']) if 'content' in content.keys() and content['content']['rendered'] != '' else re.sub(clean_html, '', content.get('acf', {}).get('single-post_emphasized-text_text-area', '') + '/n' + content.get('acf', {}).get('single-post_post-content_wysiwyg-editor')),
    'author':           content['author_info']['display_name'] if 'author_info' in content.keys() else content.get('yoast_head_json', {}).get('twitter_misc', {}).get('Napisao/la'),
    'categories':       [categories[cat_id] for cat_id in content.get('categories', [])],
    'tags':             [tag['name'] for tag in content.get('tags', [])] if not content.get('tags', []) == False else [],
    'comments_allowed': content.get('comments_allowed'),
    'category_name':    category_name,
    'comments_link':    content.get('_links', {}).get('replies', [{'href': None}])[0].get('href')
}
