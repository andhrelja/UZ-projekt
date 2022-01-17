import os
import csv
import json

import settings

class FileIO:
    def __init__(self, filename, filetype):
        dirname = os.path.join(
            settings.BASE_DIR,
            settings.SITE_NAME
        )
        if not os.path.isdir(dirname):
            os.mkdir(dirname)
        
        self.filename = os.path.join(dirname, *filename.split("/"))
        self.filetype = filetype
        if self.filetype == 'csv':
            self.lines = self._read_csv_content(limit=None)
        elif self.filetype == 'json':
            self.lines = self._read_json_content(limit=None)
    
    @property
    def num_lines(self):
        return len(self.lines)

    @property
    def existing_ids(self):
        return [row['id'] for row in self.lines] if self.lines else []
    
    def get_last_load_date(self, colname):
        if self.filetype == 'csv':
            if os.path.isfile(self.filename):
                return self._get_last_load_date_csv(colname)
            else:
                return '2021-01-01 00:00:00'
        elif self.filetype == 'json':
            if os.path.isfile(self.filename):
                return self._get_last_load_date_json(colname)
            else:
                return '2021-01-01 00:00:00'
    
    def exclude_lines(self, exclude_ids):
        self.lines = [line if line['id'] not in exclude_ids else None for line in self.lines]
        self.lines = list(filter(
            lambda x: x is not None 
                and x['date'] >= '2021-01-01T00:00:00' 
                and x['date'] <= '2021-12-31T23:59:59', 
            self.lines))
    
    def write_content(self, content):
        if os.path.isfile(self.filename):
            if self.filetype == 'csv':
                self._append_csv_content(content)
            elif self.filetype == 'json':
                self._append_json_content(content)
        else:
            if self.filetype == 'csv':
                self._write_csv_content(content)
            elif self.filetype == 'json':
                self._write_json_content(content)
    
    def chunks(self, n_chunks):
        for i in range(0, self.num_lines, n_chunks):
            yield self.lines[i:i+n_chunks]
        
    def _read_json_content(self, limit=None):
        if not os.path.isfile(self.filename):
            return None
        with open(self.filename, 'r', encoding='utf-8') as jsonfile:
            content = json.load(jsonfile)
            return content[:limit]
    
    
    def _read_csv_content(self, limit=None):
        if not os.path.isfile(self.filename):
            return None
        with open(self.filename, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            return list(reader)[:limit]
    
    def _get_last_load_date_csv(self, colname):
        with open(self.filename, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            max_item = max(reader, key=lambda x: x[colname])
            return max_item[colname]
    
    def _get_last_load_date_json(self, colname):
        with open(self.filename, 'r', encoding='utf-8') as jsonfile:
            content = json.load(jsonfile)
            max_item = max(content, key=lambda x: x[colname])
            return max_item[colname]
    
    def _write_csv_content(self, content):
        with open(self.filename, 'w', encoding='utf-8', newline='') as csvfile:
            if isinstance(content, list):
                writer = csv.DictWriter(csvfile, content[0].keys())
                writer.writeheader()
                writer.writerows(content)
            elif isinstance(content, dict):
                writer = csv.DictWriter(csvfile, content.keys())
                writer.writeheader()
                writer.writerow(content)
    
    def _append_csv_content(self, content):
        with open(self.filename, 'a', encoding='utf-8', newline='') as csvfile:
            if isinstance(content, list):
                writer = csv.DictWriter(csvfile, content[0].keys())
                writer.writerows(content)
            elif isinstance(content, dict):
                writer = csv.DictWriter(csvfile, content.keys())
                writer.writerow(content)
            
            
    
    def _write_json_content(self, content):
        if isinstance(content, dict):
            content = [content]
        with open(self.filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(content, jsonfile, ensure_ascii=False, indent=2)
    
    def _append_json_content(self, content):
        if isinstance(content, dict):
            content = [content]
        with open(self.filename, 'a', encoding='utf-8') as jsonfile:
            existing_content = json.load(jsonfile)
            content += existing_content
            json.dump(content, jsonfile, ensure_ascii=False, indent=2)
    
    