from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from gevent.pywsgi import WSGIServer
from scripts import create_table
from scripts import helpers
import tensorflow as tf
from tensorflow import keras
#from skimage import transform, io
import skimage.transform
import numpy as np
import keras
import cv2
  
app = Flask(__name__)

model_file = './model/weights.epoch_02.hdf5'


@app.route('/api/recognize_image', methods=['POST'])
def recognize_image():

  username = request.headers['ID']
  password = request.headers['Authorization']
  email = request.headers['email']
  paymentflag = request.headers['flag']

  if helpers.credentials_valid(username, password, paymentflag):
  
    #img_url = request.get_json()['img_url']
    r = request
    # convert string of image data to uint8
    nparr = np.fromstring(r.data, np.uint8)
    # decode image
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    X = []
  
    # prepare image for prediction

    #img = cv2.imread(img_url)
    if img is not None:
      img = skimage.transform.resize(img, (150, 150, 3))
      img = np.asarray(img)
      X.append(img)

    X_pred = np.asarray(X)

    # predict
    prediction_array = model.predict(X_pred)
    pred = np.argmax(prediction_array,axis = 1)
      
    # prepare api response
    class_names = ['NORMAL', 'PNEUMONIA']
    result = {
        "prediction" : class_names[np.argmax(prediction_array)],
        "confidence" : '{:2.0f}%'.format(100*np.max(prediction_array))
    }
 
    return jsonify(isError= False, message= "Success", statusCode= 200, data=result), 200

  result = {
        "prediction" : 'Authentication Invalid',
        "confidence" : 'Authentication Invalid'
    }

  return jsonify(isError= True, message= "Failed", statusCode= 400, data=result), 400


if __name__ == '__main__':
    #model = keras.experimental.load_from_saved_model('fashion_mnist_classifier')
    model = keras.models.load_model(model_file)
    http_server = WSGIServer(('0.0.0.0', 5001), app)
    http_server.serve_forever()