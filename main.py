import requests
import json
import datetime

from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template
from sqlalchemy import desc
import langid

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vacancy.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SQLALCHEMY_ECHO"] = True

db = SQLAlchemy(app)

START_REQUESTS = (
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

)

STOP_WORDS_IN_TITLE = (
    'аналитик', 'Middle', 'безопас', 'C#', 'Rust', 'Go', 'DevOps', 'Ruby', 'Rust', 'Frontend', 'QA', 'Team Lead',
    'Scientist', 'Big Data', 'Fullstack', 'Data Science', 'Chief', '.Net', 'C++', 'Delphi', 'middle', 'PHP', 'JS',
    'support', 'Full-Stack', 'Senior', 'Financial', 'С++', 'Machine Learning', 'Full Stack', 'Техлид', 'Analytic',
    'Java', 'Data engineer', 'нейронн', 'research', 'Teamlead', 'ML-инженер', 'Firmware', 'маркетолог', 'Analyst',
    'TechLead', 'Методист', 'HR-менеджер', 'анализ', 'Lead', 'Head of', 'Architect', 'DevSecOps', 'React', 'тимлид',
    'Архитектор',  'Oracle', 'Linux', 'Мидл', 'Designer', 'UnrealEngine', 'Administrator', 'Recruiter', 'директор',
    'Angular', 'Perl', '1C', '1C', 'HR менеджер','микроэлектроника', 'linux', 'node.js',
)
WHITE_WORDS_IN_TITLE = (
    'стажер', 'джун', 'junior'
)

STOP_WORDS_IN_SKILLS = (
    'C#', 'Rust', 'Go', 'DevOps', 'Ruby', 'Rust', 'QA', 'Team Lead', 'Fullstack', '.Net', 'C++', 'Delphi',
    'middle', 'Full-Stack', 'Senior', 'С++', 'Full Stack', 'Техлид','Teamlead', 'TechLead', 'Методист',
    'анализ', 'Lead', 'Head of', 'Architect', 'DevSecOps', 'React', 'тимлид', '1C', '1C', 'Oracle', 'Designer',
    'UnrealEngine', 'Recruiter', 'директор', 'Angular',
)

all_vacancy = []
MAIN_API_URL = 'https://api.hh.ru/'

SEARCH_PAGE_COUNT = 2
SEARCH_PER_PAGE = 100

all_vacancy_id = []


class Vacancy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hh_id = db.Column(db.Integer, unique=True, nullable=True)
    name = db.Column(db.String(255))
    area_id = db.Column(db.Integer)
    my_score = db.Column(db.Integer)
    area_name = db.Column(db.String(100))
    url = db.Column(db.String(255))
    archived = db.Column(db.Boolean)
    score_points = db.Column(db.Integer)
    update_data_time = db.Column(db.DateTime)
    description = db.Column(db.String(5000))
    branded_description = db.Column(db.String(5000))
    key_skills_names = db.Column(db.String(1000))
    experience_name = db.Column(db.String(100))
    salary = db.Column(db.Integer)
    currency = db.Column(db.String(10))
    has_test = db.Column(db.Boolean)
    test = db.Column(db.String(2000))
    contacts_name = db.Column(db.String(300))
    contacts_email = db.Column(db.String(15))
    contacts_phones = db.Column(db.String(15))

    def vacancy_score_points(self):
        self.score_points = 0
        if any(word.lower() in self.name.lower() for word in STOP_WORDS_IN_TITLE):
            self.score_points -= 30

        if any(word.lower() in self.name.lower() for word in WHITE_WORDS_IN_TITLE):
            self.score_points += 20

        if self.key_skills_names is not None and self.key_skills_names != '':
            if any(word.lower() in self.key_skills_names.lower() for word in STOP_WORDS_IN_SKILLS):
                self.score_points -= 30
        if self.description is not None:
            lang = langid.classify(self.description)
            if lang[0] != 'ru':
                self.score_points -= 60


        return False

    def check_uniq_vacancy(self):
        check_vacancy = Vacancy.query.filter_by(hh_id=self.hh_id).first()
        if check_vacancy is not None:
            return False
        return True

    def get_full_vacancy_details(self):
        headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) '
                                 'Chrome/102.0.5005.63 Safari/537.36'}
        url = f'{MAIN_API_URL}vacancies/{self.hh_id}'
        req = requests.get(url, headers=headers)
        vacancy_data = json.loads(req.text)

        self.update_data_time = datetime.datetime.now()
        if vacancy_data.get('errors') is None:

            self.name = vacancy_data['name']
            self.area_id = vacancy_data['area']['id']
            self.area_name = vacancy_data['area']['name']
            self.url = vacancy_data['alternate_url']
            self.archived = vacancy_data['archived']
            self.description = vacancy_data['description']
            self.branded_description = vacancy_data['branded_description']
            self.key_skills_names = ''
            if vacancy_data['key_skills'] is not None:
                for skill in vacancy_data['key_skills']:
                    self.key_skills_names += f'{list(skill.values())[0]} '
            self.experience_name = vacancy_data['experience']['name']

            self.salary = 0
            if vacancy_data.get('salary') is not None:
                if vacancy_data['salary'].get('from') is not None:
                    self.salary = vacancy_data['salary']['from']
                self.currency = ''
                if vacancy_data['salary']['currency'] is not None:
                    self.currency = vacancy_data['salary']['currency']

            if vacancy_data['contacts'] is not None:
                if vacancy_data['contacts']['name'] is not None:
                    self.contacts_name = vacancy_data['contacts']['name']
                if vacancy_data['contacts']['phones'] is not None:
                    self.contacts_name = vacancy_data['contacts']['phones']
                if vacancy_data['contacts']['email'] is not None:
                    self.contacts_name = vacancy_data['contacts']['email']
                    self.vacancy_score_points()

        db.session.commit()
        return True

    def __repr__(self):
        return f"<vacancy id={self.id}>"


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
    return req.text


@app.route('/updatescore', methods=['GET'])
def update_score_points():
    vacansies = Vacancy.query.all()
    for vacancy in vacansies:
        vacancy.vacancy_score_points()
    db.session.commit()
    return render_template('update_score_points.html', title='Обновляем скор баллы')


@app.route('/updatedetails', methods=['GET'])
def update_full_details():
    updated_vacansies = Vacancy.query.all()
    for vacancy in updated_vacansies:
        print(vacancy.update_data_time)
        if vacancy.update_data_time is not None:
            if datetime.datetime.now() - vacancy.update_data_time < datetime.timedelta(days=3):
                continue
        print('надо бы обновить данные')
        vacancy.get_full_vacancy_details()
    return render_template('update_vacancies.html', title='Обновляем полную информацию о вакансиях',
                           vacanсies=updated_vacansies)


@app.route('/findnewvacancy', methods=['GET'])
def find_new_vacancy():
    # Перебираем все запросы для вакансий и заданное кол-во страниц
    try:
        for re in START_REQUESTS:
            for page in range(SEARCH_PAGE_COUNT):
                # запрос к API
                json_string = get_vacancy_by_search(re, page=page)
                json_data = json.loads(json_string)['items']
                # перебираем полученные данные о вакансиях и сохраняем в модель

                for vacancy_data in json_data:
                    vacancy = Vacancy()
                    vacancy.hh_id = vacancy_data['id']
                    vacancy.name = vacancy_data['name']
                    vacancy.area_id = vacancy_data['area']['id']
                    vacancy.area_name = vacancy_data['area']['name']
                    vacancy.url = vacancy_data['alternate_url']
                    vacancy.archived = vacancy_data['archived']

                    vacancy.salary = 0
                    if vacancy_data.get('salary') is not None:
                        if vacancy_data['salary'].get('from') is not None:
                            vacancy.salary = vacancy_data['salary']['from']
                    if vacancy.check_uniq_vacancy():
                        db.session.add(vacancy)
                        db.session.flush()
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        print(f'Ошибка добавления в БД\n Ошибка: {e}')

    return render_template('find_vacancy.html', title='Поиск новых вакансий')


@app.route('/', methods=['GET'])
def show_all_vacancy():
    all_vacancies = []
    try:
        all_vacancies = Vacancy.query.order_by(desc(Vacancy.score_points)).all()
    except Exception as e:
        print(f'Ошибка чтения из БД {e}')
    return render_template('index.html', title='Все вакансии', vacancies=all_vacancies)


if __name__ == '__main__':
    app.run(debug=True)
