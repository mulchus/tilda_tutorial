import requests
import logging
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


def save_page_assets(page_info, html_dir):
    def save_element(element, element_dir):
        response = requests.get(element['from'])
        response.raise_for_status()
        with open(Path.joinpath(html_dir, element_dir.replace('/', ''), element['to']), 'wb+') as file:
            file.write(response.content)

    for image in page_info['images']:
        save_element(image, page_info['export_imgpath'])
    for js in page_info['js']:
        save_element(js, page_info['export_jspath'])
    for css in page_info['css']:
        save_element(css, page_info['export_csspath'])


def save_html(page_info, html_dir):
    with open(Path.joinpath(html_dir, page_info['filename']), 'wb+') as file:
        file.write(page_info['html'].encode('utf-8'))
        

def main():
    configuring_logging()
    logger.info("Start program")
    tilda_publickey = env('TILDA__PUBLIC_KEY')
    tilda_secretkey = env('TILDA__SECRET_KEY')
    project_id = env('TILDA__PROJECT_ID')

    # projects = get_from_tilda(tilda_publickey, tilda_secretkey,
    #                           'https://api.tildacdn.info/v1/getprojectslist')
    # print(projects)
    
    # getprojectinfo getprojectexport
    project_info = get_from_tilda(tilda_publickey, tilda_secretkey,
                                  'https://api.tildacdn.info/v1/getprojectexport', project_id)
    print(project_info)
    save_page_assets(project_info['result'], Path.joinpath(BASE_DIR, f'project{project_id}'))

    # pages = get_from_tilda(tilda_publickey, tilda_secretkey,
    #                        'https://api.tildacdn.info/v1/getpageslist', project_id)
    # print(len(pages['result']))
    # for page in pages['result']:
    #     print(page['id'], page['alias'], page['filename'])
    # print(pages)

    # getpage getpagefull getpageexport getpagefullexport
    # page_id = '35998050'  # 48391979 48420283 48391945
    # page = get_from_tilda(tilda_publickey, tilda_secretkey,
    #                        'https://api.tildacdn.info/v1/getpagefullexport', None, page_id)
    # print(page)

    # for page in pages['result']:
    #     page_info = get_from_tilda(
    #         tilda_publickey, tilda_secretkey,
    #         'https://api.tildacdn.info/v1/getpagefullexport',
    #         None, page['id'],
    #     )
    #
    #     html_dir = Path.joinpath(BASE_DIR, 'pages', page_info['result']['id'])
    #     Path.mkdir(html_dir, parents=True, exist_ok=True)
    #     save_html(page_info['result'], html_dir)
    #
    #     for end_path in ['export_imgpath', 'export_jspath', 'export_csspath']:
    #         Path.mkdir(Path.joinpath(html_dir, (page_info['result'][end_path]).replace('/', '')),
    #                    parents=True, exist_ok=True)
    #     save_page_assets(page_info['result'], html_dir)

    logger.info("End program")
    

if __name__ == "__main__":
    main()
    