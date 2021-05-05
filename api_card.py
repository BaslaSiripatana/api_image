import flask
from flask import request, jsonify

import pytesseract
from difflib import SequenceMatcher

import os

from PIL import Image

app = flask.Flask(__name__)
app.config["DEBUG"] = True

def load_images_from_folder(folder):
    filename = []
    for img in os.listdir(folder):
        if img.endswith("jpg"):
            filename.append(img)

    return filename

def rotateImages(rotationAmt, filename):
    img = Image.open(filename)
    img.rotate(rotationAmt).save(filename + '.jpg')
    img.close()
    

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()*100

def img_comparison(input1, input2):

    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'
    s1 = pytesseract.image_to_string(input1)

    images = load_images_from_folder(input2)

    percent_ssim = []
    i = 0

    for image in images:
        s_max = 0
        angle = 0

        s2 = pytesseract.image_to_string(input2 + '\\' + image)
        s = similar(s1, s2)
        if s>s_max:
            s_max = s

        for j in range(0,3):
            angle = angle + 90
            rotateImages(angle, input2 + '\\' + image)
            s2 = pytesseract.image_to_string(input2 + '\\' + image + '.jpg')
            s = similar(s1, s2)
            if s>s_max:
                s_max = s
        os.remove(input2 + '\\' + image + '.jpg')
        
        dic  = {'similarity' : s_max, 'path' : images[i]}
        percent_ssim.append(dic)
        i = i + 1
    
    percent_ssim = sorted(percent_ssim, key = lambda i: i['similarity'],reverse=True)
    print(percent_ssim)
    return percent_ssim

@app.route('/', methods=['GET'])
def home():
    return '''<h1>Image Similarity</h1>'''

@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404

@app.route('/image_similarity', methods=['GET'])
def api_img_similarity():
    query_parameters = request.args

    input1 = query_parameters.get('input1')
    input2 = query_parameters.get('input2')

    if not (input1 and input2):
        return page_not_found(404)
    else:
        return jsonify(img_comparison(input1, input2))

app.run(host='0.0.0.0')
