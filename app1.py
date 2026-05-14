import json

from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def load_data():
    with open('data/flowers.json') as file:
        flowers = json.load(file)
    return flowers


@app.route('/')
def index():
    flowers = load_data()
    addons = load_data()
    return render_template('index1.html', flower=flowers, addon=addons)


if __name__ == '__main__':
    app.run(debug=True)