import pandas as pd
from datetime import date
from tqdm import tqdm
import re
import csv


start_date = pd.to_datetime('2021-01-01T00:00:00', format='%Y-%m-%dT%H:%M:%S')
end_date = pd.to_datetime('2021-12-31T23:59:59', format='%Y-%m-%dT%H:%M:%S')

SELECT = ['id', 'date', 'title', 'text', 'author', 'category_name', 'categories', 'tags']
ARTICLES_PATH = 'C:\\Users\\AndreaHrelja\\Documents\\Faks\\5. godina\\3. semestar\\UPZ\\Seminar-Final\\scrape\\n1info\\csv\\n1info.csv'
ARTICLES_CLEAN_PATH = 'C:\\Users\\AndreaHrelja\\Documents\\Faks\\5. godina\\3. semestar\\UPZ\\Seminar-Final\\scrape\\n1info\\csv\\clean-n1info.csv'
COVID_TAGS = [
    'SARS-CoV-2', 'COVID-19', 'corona', 'korona', 'epidemij', 'pandemij', 'lockdown', 'antimaskeri',
    'samoizolacij', 'novozaražen', 'propusnic', 'cjepiv', 'cijepljen', 'cjepljen', 'antivakseri',
    'WHO', 'stožer civilne zaštite', 'prva doza', 'druga doza', 'treća doza', 'booster doza',
    'omikron soj', 'omikorn soj', 'britanski soj', 'delta soj', 'novi soj',
    'južnoafrički soj', 'indijski soj', 'brazilski soj', 'mutirani soj',
    'češki soj', 'lambda soj', 'sojevi koronavirusa', 'njujorški soj',
    'BioNTech', 'Pfizer', 'Sputnik V', 'AstraZeneca', 'Astra Zeneca'
]
VACCINE_TAGS = [
    'cjepiv', 'cijepljen', 'cjepljen',
    'prva doza', 'druga doza', 'treća doza', 'booster doza',
    'BioNTech', 'Pfizer', 'Sputnik V', 'AstraZeneca', 'Astra Zeneca'
]
SOJ_TAGS = [
    'omikron soj', 'omikorn soj', 'britanski soj', 'delta soj', 'novi soj',
    'južnoafrički soj', 'indijski soj', 'brazilski soj', 'mutirani soj',
    'češki soj', 'lambda soj', 'sojevi koronavirusa', 'njujorški soj',
]
ANTI_TAGS = ['antimaskeri', 'antivakseri',]
CLEAN_HTML = re.compile(r'<[^>]+>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')

def eliminate_duplicates():
    print("Eliminating duplicates")
    new_content = []
    items = {}
    with open(ARTICLES_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        content = list(reader)
    
    for item in tqdm(content):
        if not item['id'] in items.keys():
            items[item['id']] = 1
            new_content.append(item)
    
    with open(ARTICLES_CLEAN_PATH, 'w', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=new_content[0].keys())
        writer.writeheader()
        writer.writerows(new_content)
        
    print("Done")
    

def clean():
    print("Transforming the dataframe")
    df = pd.read_csv(ARTICLES_CLEAN_PATH, encoding='utf-8')[SELECT]
    df.to_json(ARTICLES_PATH.replace('csv', 'json'), force_ascii=False, indent=2, orient='records')
    
    df['tags'] = df['tags'].transform(eval)
    df['categories'] = df['categories'].transform(eval)

    df['date']  = pd.to_datetime(df['date'], format='%Y-%m-%dT%H:%M:%S').dt.date
    df['month'] = pd.to_datetime(df['date'], format='%Y-%m-%dT%H:%M:%S').dt.date.transform(
        lambda x: date(x.year, x.month, 1))
    df['datetime'] = pd.to_datetime(df['date'], format='%Y-%m-%dT%H:%M:%S')
    df = df[(df['datetime'] >= start_date) & (df['datetime'] <= end_date)]

    df['text'] = df['text'].transform(lambda x: x.replace('\nN1 pratite putem aplikacija za\xa0Android\xa0|\xa0iPhone/iPad\xa0i društvenih mreža\xa0Twitter\xa0|\xa0Facebook\xa0|\xa0Instagram.\n', ''))
    df['text'] = df['text'].transform(lambda x: ' ' + x + ' ')
    df['text'] = df['text'].transform(lambda x: re.sub(CLEAN_HTML, '', x).strip())
    df['title'] = df['title'].transform(lambda x: re.sub(CLEAN_HTML, '', x).strip())

    df['covid_related'] = df['tags'].transform(
        lambda tags: any(covid_tag.lower() in tag.lower() for tag in tags for covid_tag in COVID_TAGS) if tags else None)
    df['vaccine_related'] = df['tags'].transform(
        lambda tags: any(vaccine_tag.lower() in tag.lower() for tag in tags for vaccine_tag in VACCINE_TAGS) if tags else None)
    df['anti_related']  = df['tags'].transform(
        lambda tags: any(soj_tag.lower() in tag.lower() for tag in tags for soj_tag in SOJ_TAGS) if tags else None)
    df['soj_related']   = df['tags'].transform(
        lambda tags: any(anti_tag.lower() in tag.lower() for tag in tags for anti_tag in ANTI_TAGS) if tags else None)

    for covid_tag in COVID_TAGS:
        df.loc[df['title'].str.contains(covid_tag, case=False), 'covid_related'] = True
        df.loc[df['text'].astype(str).str.contains(covid_tag, case=False), 'covid_related'] = True

    for vaccine_tag in VACCINE_TAGS:
        df.loc[df['title'].str.contains(vaccine_tag, case=False), 'vaccine_related'] = True
        df.loc[df['text'].astype(str).str.contains(vaccine_tag, case=False), 'vaccine_related'] = True

    for anti_tag in ANTI_TAGS:
        df.loc[df['title'].str.contains(anti_tag, case=False), 'anti_related'] = True
        df.loc[df['text'].astype(str).str.contains(anti_tag, case=False), 'anti_related'] = True

    for soj_tag in SOJ_TAGS:
        df.loc[df['title'].str.contains(soj_tag, case=False), 'soj_related'] = True
        df.loc[df['text'].astype(str).str.contains(soj_tag, case=False), 'soj_related'] = True

    df.to_csv(ARTICLES_CLEAN_PATH, encoding='utf-8')
    df.to_json(ARTICLES_CLEAN_PATH.replace('csv', 'json'), force_ascii=False, indent=2, orient='records')
    print("Done")

if __name__ == '__main__':
    eliminate_duplicates()
    clean()
