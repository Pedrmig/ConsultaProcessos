# from flask import Flask, render_template, request
import os

import cons_api
import pandas as pd
#
# app = Flask(__name__)
#
# @app.route("/",  methods=['GET', 'POST'])
# def homepage():
#     #if request.method == 'POST':
#     #    numero_processo = float(request.form['numero_processo'])
#     #return (numero_processo)
#     return render_template("homepage.html")
#
# @app.route('/submit', methods=['POST'])
# def submit():
#     numero_processo = request.form["numero_processo"]
#     result = cons_api.consulta_tribunal("numero_processo")
#     return render_template('resultado.html', result=result)
#
#
# # colocar o site no ar
# if __name__ == "__main__":
#     app.run(debug=True)

data = cons_api.consulta_tribunal('10106810720138260309')

if data:
    df = cons_api.json_to_dataframe(data)
    if os.path.isfile('teste.xlsx'):
        os.remove('teste.xlsx')
    df.to_excel('teste.xlsx')
else:
    print("Nenhum dado encontrado.")
