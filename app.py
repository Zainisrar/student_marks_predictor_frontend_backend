# -*- coding: utf-8 -*-
from flask_sqlalchemy import SQLAlchemy
import numpy as np
import pandas as pd
from datetime import datetime
from flask import Flask, request, render_template
import joblib

app = Flask(__name__)
model = joblib.load("student_mark_predictor.pkl")

df = pd.DataFrame()


#database connectivity
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/contact_form'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/prediction_marks'

db = SQLAlchemy(app)

class marks(db.Model):
    S_no = db.Column(db.Integer, primary_key=True)
    # Student_name = db.Column(db.String(12), nullable=False)
    Study_hours = db.Column(db.Float(5), nullable=False)
    Prediction_marks = db.Column(db.Float(5), nullable=False)
    date = db.Column(db.String(12), nullable=True)
class contact(db.Model):
    Name = db.Column(db.String(80), nullable=False)
    Email = db.Column(db.String(20), nullable=False)
    Phone = db.Column(db.Integer(),primary_key=True)
    Message = db.Column(db.String(120), nullable=False)


@app.route('/', methods = ['GET', 'POST'])
def front():
    if(request.method=='POST'):
        '''Add entry to the database'''
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        entry = contact(Name=name, Phone  = phone, Message = message, Email = email )
        db.session.add(entry)
        db.session.commit()
    return render_template('home.html')
@app.route('/prediction')
def home():
    return render_template('index.html')


@app.route('/predict',methods=['GET','POST'])
def predict():
    global df
    
    input_features = [int(x) for x in request.form.values()] #list comparision
    features_value = np.array(input_features)
    print(features_value)
    
    #validate input hours
    if input_features[0] <0 or input_features[0] >12:
        return render_template('index.html', prediction_text='Please enter valid hours between 1 to 12 if you live on the Earth')
      

    output = model.predict([features_value])[0][0].round(2)

    # input and predicted value store in df then save in csv file
    # df= pd.concat([df,pd.DataFrame({'Study Hours':input_features,'Predicted Output':[output]})],ignore_index=True)
    # print(df)   
    # df.to_csv('smp_data_from_app.csv')
    if(request.method=='POST'):
        '''Add entry to the database'''
        name = request.form.get('name')
        study_hours = request.form.get('study_hours')
        prediction = output
    #    Student_name=name,
        entry = marks( Study_hours = study_hours,Prediction_marks=prediction, date= datetime.now() )
        db.session.add(entry)
        db.session.commit()

    return render_template('index.html', prediction_text='You will get {} Percentage marks Dear Student, when you do study {} hours per day'.format(output, int(features_value[0])))


if __name__ == "__main__":
    app.run()
    