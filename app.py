import json

from flask import Flask, render_template, request, session, flash, redirect, url_for

app = Flask(__name__)
app.secret_key = '11037'

def load_addon_data():
    with open('data/addons.json') as file:
        addons = json.load(file)
    return addons
    
def load_flower_data():
    with open('data/flowers.json') as file:
        flowers = json.load(file)
    return flowers

@app.route('/')
def index():
    flowers = load_flower_data()
    addons = load_addon_data()
    cart = session.get('cart', {})
    selected_addons = session.get('selected_addons', {})
    total = calculate_total(cart, selected_addons)

    return render_template("index.html", flowers=flowers, addons=addons, cart=cart, selected_addons=selected_addons, total=total)


@app.route('/index1')
def index1():
    flowers = load_flower_data()
    addons = load_addon_data()
    return render_template("index1.html", flowers=flowers, addons=addons)  

@app.route('/base')
def base():
    
    return render_template("base.html") 

@app.route('/invoice')
def invoice():
    
    return render_template("invoice.html")  

@app.route('/order_history')
def order_history():
    
    return render_template("order_history.html") 

@app.route('/about')
def about():
    
    return render_template("about.html") 

# Info on form data
@app.route('/add_to_cart', methods=["POST"])
def add_to_cart():
    flower = request.form['flower'] #grab flower name
    quantity = int(request.form['quantity']) # makes the quantity a number
    flowers = load_flower_data() #gets flower data from file
    cart = session.get('cart', {}) #gets a cart from session or starts a fresh one

    if flower not in flowers:
        flash("invalid flower selected")
        return redirect(url_for('index'))
    
    if flower in cart:
        cart[flower]['quantity'] += quantity # adds to existing quantity
    else:
        cart[flower] = {
            'price': flowers[flower]['price'],
            'quantity': quantity 
            }

    session['cart'] = cart #updates session
    session.modified = True #flask will save it
    flash(f"{quantity} {flower}(s) added to cart") #message sent to end user upon action
    return redirect(url_for('index')) #refreshes homepage

@app.route('/remove_from_cart/<item>')
def remove_from_cart(item):
    cart = session.get('cart', {})

    if item in cart:
        del cart[item]
        session['cart'] = cart
        session.modified = True
        flash(f"Removed all {item}('s) from the cart.")
    else:
        flash(f"{item} not found in cart.")
         
    return redirect(url_for('index'))

@app.route('/select_addon', methods=['POST'])
def select_addon():
    selected_addons = {}
    addons = load_addon_data() #only need addons

    selected_keys = request.form.getlist('addons')

    for addon in selected_keys:
        if addon in addons:     
            selected_addons[addon] = float(addons[addon]['price'])
            len(selected_addons)
            
    session['selected_addons'] = selected_addons
    session.modified = True
    return redirect(url_for('index'))

def calculate_total(cart, selected_addons):
    total = sum(item['price'] * item['quantity'] for item in cart.values())
    total += sum(price for price in selected_addons.values())
    return total

@app.route('/cancel_order', methods=['POST'])
def cancel_order():
    session.pop('cart', None)
    session.pop('selected_addons', None)
    session.modified = True

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)






