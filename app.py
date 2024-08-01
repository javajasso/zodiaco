from bson import ObjectId
import tensorflow as tf
import joblib
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import database as dbase

# Configuración del modelo y normalizadores
model_path = 'recursos_model/Defsigno_model.h5'
model = tf.keras.models.load_model(model_path)

# Cargar el scaler y el label encoder (debes asegurarte de que estos se guardan y cargan correctamente)
scaler = joblib.load('recursos_model/scaler.joblib')
label_encoder = joblib.load('recursos_model/label_encoder.joblib')

# Debes cargar el scaler y el label encoder con los datos que usaste para el entrenamiento
# Aquí solo para ilustrar. En la práctica, deberías guardar y cargar estos objetos.
# Ejemplo:
# scaler.mean_ = np.array([0, 0])  # Valores de media usados para normalizar
# scaler.scale_ = np.array([1, 1])  # Valores de escala usados para normalizar
# label_encoder.classes_ = np.array(['Aries', 'Tauro', ...])  # Clases de etiquetas

db = dbase.dbConnection()

app = Flask(__name__)
app.secret_key = 'adminJasso'

@app.route('/')
def home():
    fechasNuevas = db['fechasnuevas'].find()
    return render_template('index.html', fechasNuevas=fechasNuevas)

@app.route('/fechas', methods=['POST'])
def addNewFechas():
    fechasNuevas = db['fechasnuevas']
    dia = request.form['dias']
    mes = request.form['meses']

    if dia and mes:
        fechaNew = {'dia': dia, 'mes': mes}

        # Normalizar la entrada para la predicción
        X_input = np.array([[float(dia), float(mes)]])
        X_input = scaler.transform(X_input)

        # Realizar predicción
        predicciones = model.predict(X_input)
        predicciones_clases = np.argmax(predicciones, axis=1)
        predicciones_etiquetas = label_encoder.inverse_transform(predicciones_clases)

        # Agregar el signo predicho al documento
        fechaNew['signo'] = predicciones_etiquetas[0]

        # Insertar en la base de datos
        fechasNuevas.insert_one(fechaNew)
        flash('Fecha agregada exitosamente')
        return redirect(url_for('home'))
    else:
        return notFound()

@app.route('/delete/<string:doc_id>', methods=['GET'])
def deleteFechas(doc_id):
    fechasNuevas = db['fechasnuevas']

    try:
        object_id = ObjectId(doc_id)
        fechasNuevas.delete_one({'_id': object_id})
    except Exception as e:
        flash('ID de documento inválido.')
        return redirect(url_for('home'))
    
    return redirect(url_for('home'))

@app.route('/edit/<string:_id>', methods=['POST'])
def editFechas(_id):
    fechasNuevas = db['fechasnuevas']
    dia = request.form['dias']
    mes = request.form['meses']

    try:
        object_id = ObjectId(_id)
    except Exception as e:
        flash('ID de documento inválido.')
        return redirect(url_for('home'))

    if dia and mes:
        fechasNuevas.update_one({'_id': object_id}, {'$set': {'dia': dia, 'mes': mes}})
        response = jsonify({'message': 'La fecha ha sido actualizada'})
        return redirect(url_for('home'))
    else:
        return notFound()

@app.errorhandler(404)
def notFound(error=None):
    message = {
        'message': 'No encontrado ' + request.url,
        'status': '404 Not Found'
    }
    response = jsonify(message)
    response.status_code = 404
    return response

if __name__ == '__main__':
    app.run(debug=True, port=4000)
