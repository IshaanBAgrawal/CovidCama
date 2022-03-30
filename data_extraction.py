import requests
from bs4 import BeautifulSoup
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


def split_string_upto_a_char(element: str, char: str):
    removal_index = list(element).index(char)
    return element[:removal_index]


DATA_URL = 'https://www.vaidam.com/hospitals/india'
CHROME_DRIVER_PATH = r'C:\Users\Hello\AppData\Browser Drivers\chromedriver.exe'

response = requests.get(DATA_URL)

soup = BeautifulSoup(response.text, 'html.parser')

city_tags = soup.select('ul.doctor-city-filter li a')
city_tags.pop(6)
city_with_hospitals_dict = {}
city_without_hospitals = []

for tag in city_tags:
    url = tag.get('href')
    try:
        city = split_string_upto_a_char(element=split_string_upto_a_char(element=str(tag.text), char='('), char=',')
    except ValueError:
        city = split_string_upto_a_char(element=str(tag.text), char='(')
    if url != "https://www.vaidam.com/hospitals/india":
        reps = 1
        webpage_left = True
        all_hospital_tags = []
        all_hospital_img_tags = []
        while webpage_left:
            new_response = requests.get(f"{url}?page={reps}")
            new_soup = BeautifulSoup(new_response.text, 'html.parser')
            hospital_tags = new_soup.select('h2.primary-heading-md a')
            hospital_img_tags = new_soup.select('div.list-card-media a img')
            if not hospital_tags:
                webpage_left = False
            all_hospital_tags.extend(hospital_tags)
            all_hospital_img_tags.extend(hospital_img_tags)
            reps += 1
        city_with_hospitals_dict[city] = {}
        for one_hospital_tag in all_hospital_tags:
            try:
                hospital_name = split_string_upto_a_char(str(one_hospital_tag.text), ',')
            except ValueError:
                hospital_name = str(one_hospital_tag.text)
            hospital_url = str(one_hospital_tag.get('href'))
            hospital_requests = requests.get(hospital_url)
            hospital_soup = BeautifulSoup(hospital_requests.text, 'html.parser')
            about_hospital = [point.text for point in hospital_soup.select('div#about-hospital div ul li')]
            team_speciality = [point.text for point in hospital_soup.select('div#team-specialities div ul li')]
            address = [adr_sect.text for adr_sect in hospital_soup.select('#section-address div p') if
                       adr_sect.text != '']
            infrastructure = [point.text for point in hospital_soup.select('div#section-infras div ul li')]
            facilities = hospital_soup.select('div.facility-list')
            facility_dict = {}
            for facility_element in facilities:
                facility_head = facility_element.find(class_='text-block-list-title').text
                facility_content = [content.text for content in facility_element.select('div.text-body ul li')]
                facility_dict[facility_head] = facility_content
            city_with_hospitals_dict[city][hospital_name] = {
                'About Hospital': about_hospital,
                'Hospital Address': address,
                'Team and Speciality': team_speciality,
                'Infrastructure': infrastructure,
                'Facilities': facility_dict,
            }
    else:
        city_without_hospitals.append(str(city))


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hospitals.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

db.drop_all()


class Hospital(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hospital_name = db.Column(db.String, unique=True)
    city = db.Column(db.String)
    hospital_data = db.Column(db.JSON)


db.create_all()

all_hospitals_in_db = Hospital.query.all()
for hospital_in_db in all_hospitals_in_db:
    db.session.delete(hospital_in_db)
    db.session.commit()

for city in city_with_hospitals_dict:
    for hospital in city_with_hospitals_dict[city]:
        hospital_record = Hospital(
            hospital_name=str(hospital),
            city=str(city),
            hospital_data={
                'About Hospital': city_with_hospitals_dict[city][hospital]['About Hospital'],
                'Hospital Address': city_with_hospitals_dict[city][hospital]['Hospital Address'],
                'Team and Speciality': city_with_hospitals_dict[city][hospital]['Team and Speciality'],
                'Infrastructure': city_with_hospitals_dict[city][hospital]['Infrastructure'],
                'Facilities': city_with_hospitals_dict[city][hospital]['Facilities']
            },
            )
        db.session.add(hospital_record)
        db.session.commit()
        print(f"{city}: {hospital}")
