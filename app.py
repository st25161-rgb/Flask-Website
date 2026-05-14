import json

from flask import Flask, render_template, request, session, flash, redirect, url_for

app = Flask(__name__)
app.secret_key = '11037'


def load_data():
    with open('data/addons.json') as file:
        addons = json.load(file)
    return addons

def load_data():
    with open('data/flowers.json') as file:
        flowers = json.load(file)
    return flowers

@app.route('/')
def index():
    addons = load_data()
    flowers = load_data()
    return render_template("index.html", addon=addons, flower=flowers)


@app.route('/index1')
def index1():
    flowers = load_data()
    addons = load_data()
    return render_template("index1.html", addon=addons, flower=flowers)

# Info on form data
@app.route('/add_to_cart', methods=["POST"])
def add_to_cart():
    flower = request.form['flower'] #grab flower name
    quantity = int(request.form['quantity']) # makes the quantity a number
    flowers = load_data() #gets flower data from file
    cart = session.get('cart', {}) #gets a cart from session or starts a fresh one

    if flower not in flowers:
        flash("invalid flower selected")
        return redirect(url_for('/'))
    
    if flower in cart:
        cart[flower][quantity] += quantity # adds existing quantity
    else:
        cart[flower] = {
            'price': flowers[flower]['price'],
            'quantity': quantity

        }

    session['cart'] = cart #upadtes session
    session.modified = True #flask will save it
    flash(f"{quantity} {flowers}(s) added to cart") #message sent to end user upon action
    return redirect(url_for('index')) #refreshes homepage


if __name__ == '__main__':
    app.run(debug=True)






