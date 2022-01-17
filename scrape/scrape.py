import os
import time
import settings

from api import GETRequest
from fileio import FileIO
from tqdm import tqdm


def collect_catalog_data(catalog_load):
    csvfile = FileIO(catalog_load.get('csv_file_name'), filetype='csv')
    jsonfile = FileIO(catalog_load.get('json_file_name'), filetype='json')
    
    url = os.path.join(settings.API_BASE_URL, catalog_load.get('uri'))
    params = catalog_load.get('params')
    
    request = GETRequest(url, params)
    map_fn = catalog_load['mapping']

    print("Collecting {} pages:".format(request.total_pages))
    for page_num in tqdm(range(1, request.total_pages + 1)):
        params.update({'page': page_num})
        response = request.get_json_response(params=params)

        content = map_fn(response)
        csvfile.write_content(content)
        jsonfile.write_content(content)

def collect_recurring_data(recurring_load, uc_all_posts=False):
    csvfile = FileIO(recurring_load.get('csv_file_name'), filetype='csv')
    jsonfile = FileIO(recurring_load.get('json_file_name'), filetype='json')
    last_load_date = csvfile.get_last_load_date('date')
    
    url = os.path.join(settings.API_BASE_URL, recurring_load.get('uri'))
    params = recurring_load.get('params')
    #params.update({'after': last_load_date})
    
    request = GETRequest(url, params)
    map_fn = recurring_load['mapping']

    print("Collecting {} pages:".format(request.total_pages))
    for page_num in tqdm(range(1, request.total_pages + 1)):
        params.update({'page': page_num})
        response = request.get_json_response(params=params)

        if uc_all_posts is True:
            if response.get('latest_date') < last_load_date:
                break
            content = map_fn(
                response.get('data'),
                response.get('latest_date')
            )
        else:
            content = map_fn(response)
        
        csvfile.write_content(content)
        jsonfile.write_content(content)

def write_content(fileio, content):
    fileio.write_content(content)

def collect_detailed_data(detailed_load):
    in_csvfile = FileIO(detailed_load.get('in_csv_file_name'), filetype='csv')
    
    out_csvfile = FileIO(detailed_load.get('csv_file_name'), filetype='csv')
    in_csvfile.exclude_lines(out_csvfile.existing_ids)
    #out_jsonfile = FileIO(detailed_load.get('json_file_name'), filetype='json')
    #last_load_date = out_csvfile.get_last_load_date('date')
    
    map_fn = detailed_load['mapping']

    for i, chunk in enumerate(in_csvfile.chunks(100)):
        print("Chunk {}/{}".format(i+1, int((in_csvfile.num_lines)/100)))
        
        content = []
        for line in tqdm(chunk):
            url = line['api_link']
            request = GETRequest(url)
            response = request.get_json_response()
            if response:
                item = map_fn(response, line['category_name'])
                content.append(item)
        if content:
            out_csvfile.write_content(content)
        #out_jsonfile.write_content(content)
        
        print("Remaining records: {}".format(in_csvfile.num_lines-((i+1)*100)))

def scrape_links():
    for i, catalog_load in enumerate(settings.CATALOG_LOADS):
        filepath = os.path.join(
            settings.BASE_DIR, 
            settings.SITE_NAME,
            catalog_load.get('csv_file_name')
        )
        if not os.path.isfile(filepath):
            print("Collecting {} of {} catalog loads".format(i+1, len(settings.CATALOG_LOADS)))
            collect_catalog_data(catalog_load)
        else:
            print("Catalog load {} already completed".format(catalog_load['uri']))
    
    #for i, recurring_load in enumerate(settings.RECURRING_LOADS):
    #    print("Collecting {} of {} recurring loads".format(i+1, len(settings.RECURRING_LOADS)))
    #    uc_all_posts = True if 'uc-all-posts' in recurring_load['uri'] else False
    #    collect_recurring_data(recurring_load, uc_all_posts)

def scrape_details():
    for i, detailed_load in enumerate(settings.DETAILED_LOADS):
        print("Collecting {} of {} detailed loads".format(i+1, len(settings.DETAILED_LOADS)))
        collect_detailed_data(detailed_load)

def scrape():
    start = time.time()
    #scrape_links()
    scrape_details()
    end = time.time()
    print("Time elapsed: {}h ({} min)".format((end-start)/3600, (end-start)/60))
    

if __name__ == '__main__':
    scrape()