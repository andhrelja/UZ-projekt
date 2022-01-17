import requests

class GETRequest:
    def __init__(self, url, params=None):
        self.url = url
        self.params = params
        if params and 'per_page' in params.keys():
            self._set_total_pages()
    
    def _get(self, url=None, params=None):
        if params:
            self.params.update(params)
        if url:            
            response = requests.get(url, self.params)
        else:
            response = requests.get(self.url, self.params)
        
        if response.status_code == 200:
            self.response = response
        elif response.status_code == 401:
            self.response = None
        else:
            response.raise_for_status()
    
    def get_json_response(self, url=None, params=None):
        self._get(url, params)
        if self.response:
            return self.response.json()
    
    def get_text_response(self, url=None, params=None):
        self._get(url, params)
        if self.response:
            return self.response.text

    def _set_total_pages(self):
        self._get()
        header_total_pages = self.response.headers.get('x-wp-totalpages')
        if header_total_pages:
            self.total_pages = int(header_total_pages)
        else:
            response = self.get_json_response()
            self.total_pages = int(response.get('total_pages'))
    