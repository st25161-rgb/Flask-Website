# @app.route('/about')
# def about():
#     return render_template('about.html')


# @app.route('/checkout')
# def checkout():
#     return render_template('invoice.html')


# @app.route('/orders')
# def order_history():
#     return render_template('order_history.html')


import json

from flask import Flask, render_template, request, session, flash, redirect, url_for

app = Flask(__name__)
app.secret_key = 'your_secret_key'


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
    flowers = load_data()
    addons = load_data()
    return render_template("index.html", addon=addons, flower=flowers)

# Info on form data
@app.route('/add_to_cart', methods=["POST"])
def add_to_cart():
    flower = request.form[flower] #flower name
    quantity = int(request.form['quantity']) #quantity in numbers
    flowers, addons = load_data() #aqquires flower data - the addon data
    cart = session.get('cart', {}) # get cart from the session or a fresh one

    if flower not in flowers:
        flash("invalid flower selected.")
        return redirect(url_for('home')) 
    
    if flower in cart:
        cart[flower] [quantity] += quantity #add existing quantity
    else:
        cart[flower] = {
            'price': flower[flower]['price'],
            'quantity': quantity
        }

    session ['cart'] = cart # update the session
    session.modified = True # flask will save the data
    flash(f"{quantity} {flower}(s) added to cart.") #says the [flower name] [amount] is added to the end users cart
    return redirect(url_for('home'))






if __name__ == '__main__':
    app.run(debug=True)


