import requests
import logging
import json
from pathlib import Path
from environs import Env


logger = logging.getLogger()
env = Env()
env.read_env()
log_file = 'main.log'
BASE_DIR = Path(__file__).resolve().parent


def configuring_logging():
    logger.setLevel(logging.INFO)
    logger_handler = logging.StreamHandler()
    # logger_handler = logging.handlers.RotatingFileHandler(
    #     Path.joinpath(BASE_DIR, log_file), maxBytes=(1048576*5), backupCount=3
    # )
    logger_formatter = logging.Formatter(
        '%(asctime)s : %(levelname)s : %(message)s',
        datefmt='%d-%m-%Y %H:%M:%S'
    )
    logger_handler.setFormatter(logger_formatter)
    logger.addHandler(logger_handler)
    return logger


def get_from_tilda(tilda_publickey, tilda_secretkey, url, project_id=None, page_id=None):
    data = {
        'publickey': tilda_publickey,
        'secretkey': tilda_secretkey,
    }
    if project_id:
        data['projectid'] = project_id
    elif page_id:
        data['pageid'] = page_id
    responce = requests.get(url, data)
    responce.raise_for_status()
    return responce.json()


def save_images(project_info):
    for image in project_info['images']:
        response = requests.get(image['from'])
        response.raise_for_status()
        with open(Path.joinpath(BASE_DIR, 'images', image['to']), 'wb') as file:
            file.write(response.content)


def save_html(page_info):
    with open(Path.joinpath(BASE_DIR, 'pages', page_info['filename']), 'wb') as file:
        file.write(page_info['html'].encode('utf-8'))
        

def main():
    configuring_logging()
    logger.info("Start program")
    tilda_publickey = env('TILDA_PUBLICKEY')
    tilda_secretkey = env('TILDA_SECRETKEY')
    projects = get_from_tilda(tilda_publickey, tilda_secretkey,
                              'https://api.tildacdn.info/v1/getprojectslist')
    print(projects)
    
    project_info = get_from_tilda(tilda_publickey, tilda_secretkey,
                                  'https://api.tildacdn.info/v1/getprojectinfo', 0)
    print(project_info)
    save_images(json.loads(project_info['result']))
    
    pages = get_from_tilda(tilda_publickey, tilda_secretkey,
                           'https://api.tildacdn.info/v1/getpageslist', 0)
    print(pages)
    
    for page in pages:
        page_info = get_from_tilda(tilda_publickey, tilda_secretkey,
                                   'https://api.tildacdn.info/v1/getpagefullexport',
                                   page['id'])
        print(page_info)
        save_images(json.loads(page_info['result']))
        save_html(json.loads(page_info['result']))
        
    logger.info("End program")
    

if __name__ == "__main__":
    main()
    