# -*- coding: utf-8 -*-
"""
Created on Tue Jul 24 05:51:03 2018

@author: my pc
"""

import os
from flask import Flask, request, redirect, url_for, render_template
from werkzeug import secure_filename
import pandas as pd

import weibull
import json

import logging
logging.basicConfig(level=logging.DEBUG)

UPLOAD_FOLDER = 'tmp'
STATIC_FOLDER = 'static'
ALLOWED_EXTENSIONS = set(['csv'])

app = Flask(__name__, static_url_path='/static')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#            return redirect(url_for('index'))
            
            df = pd.read_csv(os.path.join(UPLOAD_FOLDER, filename))
            assetIds = df['Asset'].unique().tolist()
            return render_template('show_drop_down_final.html', assetIds = assetIds , filename = filename)
    return """
    <!doctype html>
    <title>Upload Dataset</title>
    <h1>Upload a File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>"""

@app.route("/assetIds", methods = ['GET']) 
def getAssetIds():
    fileName = request.args.get('fileName')
    df = pd.read_csv(os.path.join(UPLOAD_FOLDER, fileName))
    assetIds = df['Asset'].unique().tolist()
    return json.dumps(assetIds)

@app.route("/graphs", methods=['GET'])
def generate_graphs():
    assetId = request.args.get('assetId')
    fileName = request.args.get('fileName')    
    df = pd.read_csv(os.path.join(UPLOAD_FOLDER,fileName))
    data = df[df['Asset'] == assetId]['Time']
    data_list = data.values.tolist()
    print(data_list)
    
    analysis = weibull.Analysis(data_list, unit='hour')
    analysis.fit()
    
    directory = os.path.join(STATIC_FOLDER, assetId)
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    file_paths = []
    
    prob_plot_path = os.path.join(directory, 'probability_plot.png')
    analysis.probplot(file_name=prob_plot_path, show = False)
    file_paths.append(prob_plot_path)
    
    prob_density_path = os.path.join(directory, 'prob_density_function.png')
    analysis.pdf(file_name=prob_density_path, show = False)
    file_paths.append(prob_density_path)
    
    surv_path = os.path.join(directory,'survival_function.png')
    analysis.sf(file_name=surv_path, show = False)
    file_paths.append(surv_path)
    
    hazard_path = os.path.join(directory, 'hazard_function.png')
    analysis.hazard(file_name=hazard_path, show = False)  
    file_paths.append(hazard_path)
    stats = "Mean Life: " + str(analysis.stats['mean life']) + "           " + "Median Life: " + str(analysis.stats['median life'])
#    return json.dumps(file_paths )
    return render_template('show_graphs_final_1.html', file_paths = file_paths, filename = fileName, assetId = assetId, stats= stats)


@app.route("/BLife", methods=['GET'])
def get_B_Life():
    assetId = request.args.get('assetId')
    fileName = request.args.get('fileName')
    percent =  request.args.get('percent')   
    df = pd.read_csv(os.path.join(UPLOAD_FOLDER,fileName))
    data = df[df['Asset'] == assetId]['Time']
    data_list = data.values.tolist()
#    print(data_list)
    
    analysis = weibull.Analysis(data_list, unit='hour')
    analysis.fit()
    
    file_paths = []
    assetId = os.path.join('static', assetId)
    prob_plot_path = os.path.join(assetId, 'probability_plot.png')
    file_paths.append(prob_plot_path)
    prob_density_path = os.path.join(assetId, 'prob_density_function.png')
    file_paths.append(prob_density_path)
    surv_path = os.path.join(assetId,'survival_function.png')
    file_paths.append(surv_path)
    hazard_path = os.path.join(assetId, 'hazard_function.png')
    file_paths.append(hazard_path)
    stats = "Mean Life: " + str(analysis.stats['mean life']) + "           " + "Median Life: " + str(analysis.stats['median life'])
#    return str(int(analysis.b(percent)))
    return render_template('show_life_statistics.html', file_paths=file_paths, filename = fileName, percent = percent, bLife = analysis.b(percent), stats= stats)
    

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)