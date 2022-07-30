import requests
import json
import tablib
import sqlite3 as sq

START_REQUESTS = [
    'python',
    'python стажер',
    'python вакании',
    'python без опыта',
    'python junior',
    'python джуниор',
    'python backend',
    'python стажировка',
    'Разработчик Python',
    'Программист Python',
    'Начинающий специалист Python',
    'Python developer',

]

STOP_WORDS = [
    'аналитик',
    'Middle',
    'безопас',
    'C#',
    'Rust',
    'Go',
    'DevOps',
    'Ruby',
    'Rust',
    'Frontend',
    'QA',
    'Team Lead',
    'Scientist',
    'Big Data',
    'Fullstack',
    'Data Science',
    'Chief',
    '.Net',
    'C++',
    'Delphi',
    'middle',
    'PHP',
    'JS',
    'support',
    'Full-Stack',
    'Senior',
    'Financial',
    'С++',
    'Machine Learning',
    'Full Stack',
    'Техлид',
    'Analytic',
    'Java',
    'Data engineer',
    'нейронн',
    'research',
    'Teamlead',
    'ML-инженер',
    'Firmware',
    'маркетолог',
    'Analyst',
    'TechLead',
    'Методист',
    'HR-менеджер',
    'анализ',
    'Lead',
    'Head of',
    'Architect',
    'DevSecOps',
    'React',
    'тимлид',
    'Архитектор',
    '1C',
    'Oracle',
    'Linux',
    'Мидл',
    'Designer',
    'UnrealEngine',
    'Administrator',
    'Recruiter',
    'директор',
    'Angular',

]

all_data = []
MAIN_API_URL = 'https://api.hh.ru/'

SEARCH_PAGE_COUNT = 2
SEARCH_PER_PAGE = 3

all_vacancy_id = []


def get_vacancy_by_search(text, page):
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/102.0.5005.63 Safari/537.36'}
    url = f'{MAIN_API_URL}vacancies'
    req = requests.get(url, headers=headers, params={
        'text': text,
        'order_by': 'relevance',
        'per_page': SEARCH_PER_PAGE,
        "area": '1',
        'page': page
    })

    return req.text  # .decode('unicode_escape')


def pars_data():
    for re in START_REQUESTS:
        for page in range(SEARCH_PAGE_COUNT):
            json_string = get_vacancy_by_search(re, page=page)
            json_data = json.loads(json_string)['items']
            for vacancy_data in json_data:
                if approve_vacancy(vacancy_data):
                    if vacancy_data['id'] not in all_vacancy_id:
                        all_vacancy_id.append(vacancy_data['id'])



    # for elem in all_data:
    #     print(elem)

    # data = tablib.Dataset()
    # data.json = json.dumps(all_data)
    # print(data)
    # print(len(data))
    # # print(data.export('xls'))
    # open('vacancy.xls', 'wb').write(data.export('xlsx'))


def approve_vacancy(data):
    if data['archived'] == True:
        return False
    if any(word.lower() in data['name'].lower() for word in STOP_WORDS):
        return False
    if data.get('salary') is not None:
        if data['salary'].get('from') is not None:
            if data['salary'].get('from') > 100000:
                return False
    return True


def main():
    pars_data()


if __name__ == '__main__':
    main()

"""


def get_vacancy_id(html):
    soup = BeautifulSoup(html, 'html.parser')
    for elem in soup.find_all('a'):
        href = elem.get('href')
        if href.find('https://hh.ru/vacancy/') > -1:
            vacancy_id = int(href.split('/')[4].split('?')[0])
            if vacancy_id != 'None' and vacancy_id not in all_vacancy_id:
                all_vacancy_id.append(vacancy_id)




def set_new_session_proxy():
    proxy = FreeProxy(country_id=['RU'], timeout=0.3, rand=True).get()
    session.proxies.update({'http':proxy})

def pars_data():
    for url in START_REQUESTS:
        set_new_session_proxy()
        for page in range(SEARCH_PAGE_COUNT):

            pars_url = form_donor_url(url, page=page)
            get_vacancy_id(get_html(pars_url))
    print(len(all_vacancy_id), '\n', all_vacancy_id )


"""
