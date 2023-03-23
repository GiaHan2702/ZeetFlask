# app.py

from flask import Flask, render_template, flash, redirect, url_for, request, Response, current_app
from flask_mongoengine import \
    MongoEngine  # ModuleNotFoundError: No module named 'flask_mongoengine' = (venv) C:\flaskmyproject>pip install flask-mongoengine
from werkzeug.utils import secure_filename
import os
#from bson.json_util import dumps
import codecs
import bson.json_util
# import magic
import urllib.request
import json
import io
from io import BytesIO
import processecg
import tensorflow as tf
import tensorflow_addons as tfa
import re
app = Flask(__name__)
app.secret_key = "caircocoders-ednalan-2020"
#!/usr/bin/env python3
#-*- coding: utf-8 -*-
# this code for displaying all json from database in webbrowser
# import the MongoClient class
from pymongo import MongoClient
from bson.objectid import ObjectId
import matplotlib.pyplot as plt
import base64
import tensorflow as tf
from biosppy.signals import ecg
from wfdb import processing
import collections
import numpy as np
import threading
# build a new client instance of MongoClient
#mongo_client = MongoClient('192.168.26.177', 27017)
mongo_client = MongoClient('mongodb+srv://admin:admin@cluster0.apg0dos.mongodb.net/?retryWrites=true&w=majority')
# create new database and collection instance
db = mongo_client.ecg_cap
col = db.test

@app.route('/download', methods=['GET'])
def index():
    return render_template('download_page.html')

@app.route('/')
def indexx():
    #return render_template('ABOUT.html')
    return render_template('aboutt.html')

@app.route('/doctor.html')
def doctor():
    return render_template('doctor.html')
#// Query the doctors collection for all documents
#   results = doctors.find()
    # // Pass the results to the template
#   return render_template('list_doctors.html', results=results)

@app.route('/testgpt.html') #not use
def index2():
    # Query the collection for all documents
    documents = col.find()

    # Pass the documents to the HTML template
    return render_template('testgpt.html', documents=documents)

@app.route('/interface_upload_test.html')  #not use
def about():
    return render_template('interface_upload_test.html')

@app.route('/data/<id>') # not use
def display(id):
    # Query the collection for the document with the matching ID
    document1 = col.find_one({'_id': id})

    # Pass the document to the HTML template
    return render_template('test.html', document1=document1)


# Define a route to display a list of documents in a collection / not use
@app.route('/collection/<testzip>')
def display_collection(testzip):
    # Query the collection for all documents
    documents = list(db[testzip].find())

    # Render the collection template with the list of documents
    return render_template('emptyfile.html', documents=documents)

# Define a route to download a document
# Define a route to download a document
@app.route('/download/<id>') # use
def download_document(id):
    # Fetch document using id
    document = col.find_one({'_id': bson.ObjectId(id)})

    if not document:
        # Handle document not found error
        return 'Document not found', 404

    # Convert document to JSON format
    json_data = bson.json_util.dumps(document)

    # Create a file-like object from the string data
    file = io.StringIO(json_data)

    # Create a response object
    response = Response(file.read(), mimetype='application/json')
    response.headers.set('Content-Disposition', 'attachment', filename=f'{id}.json')

    return response

@app.route('/document/<id>') # use
def document(id):
    # Retrieve document by ObjectId
    document = col.find_one({'_id': ObjectId(id)})

    # Retrieve desired fields from the document
    time = document.get('time', 'N/A')
    #CVDtype = document.get('CVDtype', 'N/A')

    return render_template('document.html', document=document, time=time)


#use
@app.route('/document_links/')
def document_links():
    # Retrieving all document IDs from MongoDB
    document_ids = [str(document['_id']) for document in col.find({}, {'_id'})]

    # Generating URLs
    urls = [url_for('document', id=document_id) for document_id in document_ids]

    # Passing URLs to the template
    return render_template('document_links.html', urls=urls)


# Route function for displaying ECG plot for document with a given ID
@app.route('/document/<id>/plot')
def document_plot(id):
    # Retrieve document by ObjectId
    document = col.find_one({'_id': ObjectId(id)})
    label = ""

    # Generate plot and output predictions if ECGsignal field exists in document
    if 'ECGsignal' in document:
        ecg_values = document['ECGsignal']
        values = processecg.process_data(ecg_values)
        nor_values = processecg.normalize_ECG(values)
        data = processecg.data_convert(nor_values)
        output = processecg.predict(signal=data, file='LSTM.h5')
        try:
            counts = {
                "Supraventricular premature disease": output.count(1),
                "Premature ventricular disease": output.count(2),
                "Fusion of ventricular disease": output.count(3),
                "Unclassifiable disease": output.count(4),
                "Normal": output.count(0)
            }
            label = max(counts, key=counts.get) if counts.values() else "Can not predict"
            if counts[label] < 3:
                label = "Can not predict"
        except:
            label = "Can not predict"

        # Generate data dictionary containing CVD type counts
        data = {
            "Supraventricular premature disease": output.count(1),
            "Premature ventricular disease": output.count(2),
            "Fusion of ventricular disease": output.count(3),
            "Unclassifiable disease": output.count(4),
            "Normal": output.count(0)
        }

        # Generate plot image
        fig, ax = plt.subplots()
        ax.plot(ecg_values)
        ax.set_xlabel('Time')
        ax.set_ylabel('Amplitude')
        ax.set_title('ECG Signal')
        image = BytesIO()
        fig.savefig(image, format='png')
        image.seek(0)
        img_data = base64.b64encode(image.getvalue()).decode()
        plt.clf()  # Clear plot for next iteration

        # Render HTML page with plot image, label, and data
        return render_template('document_plot2.html',
                               document=document,
                               plot_image=img_data,
                               label=label,
                               data=data)

    else:
        return render_template('document_plot2.html',
                               document=document,
                               plot_image="",
                               label="No ECG data found",
                               data={})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port= 5000, debug= True)

