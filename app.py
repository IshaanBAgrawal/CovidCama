from flask import Flask, render_template, redirect, request, url_for, flash
from flask_bootstrap import Bootstrap
import datetime
from flask_sqlalchemy import SQLAlchemy


def all_index_of_an_element_in_list(given_list: list, given_element):
    indexes_of_element = []
    reps = 0
    while reps < len(given_list):
        if given_list[reps] == given_element:
            indexes_of_element.append(reps)
        reps += 1
    return indexes_of_element


app = Flask(__name__)
Bootstrap(app)
app.config['SECRET_KEY'] = ";76=j;=67j.[p76ul67j.=6;76pj-=6lu"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hospitals.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Hospital(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hospital_name = db.Column(db.String, unique=True)
    city = db.Column(db.String)
    hospital_data = db.Column(db.JSON)
    hospital_img_url = db.Column(db.String)


@app.route('/')
def home_page():
    year = datetime.datetime.now().year
    return render_template('index.html', year=year)


@app.route('/precautions')
def precautions():
    year = datetime.datetime.now().year
    return render_template('covid-precautions.html', year=year)


@app.route('/search_hospital', methods=['POST'])
def search_hospital():
    all_hospitals = Hospital.query
    if request.method == 'POST':
        query_text = request.form.get('query')
        all_hospitals_by_city = all_hospitals.filter(Hospital.city.like(f'%{query_text}%')).order_by(Hospital.id).all()
        all_hospitals_by_name = all_hospitals.filter(Hospital.hospital_name.like(f'%{query_text}%')).order_by(
            Hospital.id).all()
        all_query_hospitals = []
        print(all_hospitals_by_name)
        print(all_hospitals_by_city)
        all_query_hospitals.extend(all_hospitals_by_name)
        all_query_hospitals.extend(all_hospitals_by_city)
        year = datetime.datetime.now().year
        return render_template('search_hospital.html', year=year, all_query_hospitals=all_query_hospitals)


@app.route('/hospital/<int:hospital_id>')
def hospital(hospital_id):
    year = datetime.datetime.now().year
    chosen_hospital = Hospital.query.get(hospital_id)
    num_in_word = ['One', 'Two', "Three", 'Four', "Five" 'Six', 'Seven']
    print(chosen_hospital.hospital_data['Facilities'][list(chosen_hospital.hospital_data['Facilities'].keys())[1]])
    return render_template('hospital.html', chosen_hospital=chosen_hospital, year=year, num_in_word=num_in_word,
                           len=len, list=list)


if __name__ == '__main__':
    app.run(debug=True)
