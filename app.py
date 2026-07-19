import datetime
import json
import sqlite3

from flask import Flask, render_template, request, session, flash, redirect, url_for

app = Flask(__name__)
app.secret_key = '11037'

def load_addon_data():
    try:
        with open('data/addons.json') as file:
            addons = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading addons data: {e}")
        addons = {}

    return addons
    
def load_flower_data():
    try:
        with open('data/flowers.json') as file:
            flowers = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading flower data: {e}")
        flowers = {}

    return flowers

def calculate_total(cart, selected_addons):
    total = sum(item['price'] * item['quantity'] for item in cart.values())
    total += sum(price for price in selected_addons.values())
    
    subtotal = total
    discount_appplied = False
    discount_amount = 0
    
    if total > 179:
        discount_appplied = True
        discount_amount = total * 0.10 #10% of the total which is the discount amount
        total = total - discount_amount #total after discount gets applied
        
        
    return total, discount_appplied

def initialise_database():
    with sqlite3.connect('flower_shop.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_number TEXT,
                customer_name TEXT,
                items TEXT,
                addons TEXT,
                total REAL,
                discount_applied BOOLEAN, 
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')


@app.route('/')
def index():
    flowers = load_flower_data()
    addons = load_addon_data()
    cart = session.get('cart', {})
    selected_addons = session.get('selected_addons', {})
    total, discount_applied = calculate_total(cart, selected_addons)
    subtotal = total
    discount_amount = 0
    
    if discount_applied:
        subtotal = total / 0.90 #calculates subtotal before discount
        discount_amount = subtotal - total #calculates discount amount

    
    cancel_order = session.get('cancel_order', False)
    checkout = session.get('checkout', False)

    return render_template("index.html", 
                           flowers=flowers,
                           addons=addons, 
                           cart=cart, 
                           selected_addons=selected_addons, 
                           total=total, 
                           subtotal=subtotal,
                           discount_amount=discount_amount,
                           discount_applied=discount_applied, 
                           checkout=checkout,
                           cancel_order=cancel_order)


@app.route('/index1')
def index1():
    flowers = load_flower_data()
    addons = load_addon_data()
    return render_template("index1.html", 
                           flowers=flowers, 
                           addons=addons)  

@app.route('/base')
def base():
    
    return render_template("base.html") 

@app.route('/invoice')
def invoice():
    cart = session.get('cart', {})
    selected_addons = session.get('selected_addons', {})
    total, discount_applied = calculate_total(cart, selected_addons)
    subtotal = total
    discount_amount = 0
    
    if discount_applied:
        subtotal = total / 0.90 #calculates subtotal before discount
        discount_amount = subtotal - total #calculates discount amount
    
    customer_name = session.get('customer_name')
    invoice_date = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
    invoice_number = f"INV_{customer_name.replace('  ','_')}_{invoice_date}"
    invoice_name=f"Invoice_{customer_name.replace('  ','_')}_{invoice_date}.txt"
    return render_template('invoice.html', 
                           cart=cart, 
                           selected_addons=selected_addons, 
                           total=total, 
                           subtotal=subtotal,
                           discount_amount=discount_amount,
                           discount_applied=discount_applied,
                           customer_name=customer_name, 
                           invoice_date=invoice_date, 
                           invoice_number=invoice_number,
                           invoice_name=invoice_name)  

@app.route('/order')
def order_history():
    with sqlite3.connect('flower_shop.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM orders ORDER BY date DESC')
        rows = cursor.fetchall()
        orders = []
        for row in rows:
            orders.append({
                'order_id': row[0],
                'invoice_number': row[1],
                'customer_name': row[2],
                'items': json.loads(row[3]),
                'addons': json.loads(row[4]),
                'total': row[5],
                'discount_applied': bool(row[6]),
                'date': row[7]
            })
            

    return render_template("order_history.html", orders=orders) 

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
    
    if flowers[flower]['stock'] < quantity:
        flash(f"Not enough stock for {flower}. Available: {flowers[flower]['stock']}")
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



@app.route('/cancel_order', methods=['POST'])
def cancel_order():
    session.pop('cart', None)
    session.pop('selected_addons', None)
    session.modified = True
    flash(f"Cart has been emptied")

    return redirect(url_for('index'))



@app.route('/checkout', methods=['POST'])
def checkout() :
    customer_name = request.form['customer_name'].strip().title() #validate customer name
    #check if the customer has entered a name, if not, displays a message
    # then it returns to index page
    if not customer_name:
        flash("Customer name is required")
        return redirect(url_for('index'))
    
    cart = session.get('cart', {}) #enters items into cart and tells route what they are
    selected_addons = session.get('selected_addons', {}) #tells route the selcted addons from the session
    

    if not cart: #to prevent an error of an empty cart
        flash("Your cart is empty.")
        return redirect(url_for('index'))
    
    
    total, discount_applied = calculate_total(cart, selected_addons) #calculates total
       #calculate subtotal and discount amount
    subtotal = total
    discount_amount = 0

    if discount_applied:
        subtotal = total / 0.90 #calculates subtotal before discount
        discount_amount = subtotal - total #calculates discount amount
    
    
    invoice_date = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')#creates invoice and date
    invoice_number = f"INV_{customer_name.replace('  ','_')}_{invoice_date}"
    
    with sqlite3.connect('flower_shop.db') as conn:  #saves to sqlite database
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO orders (invoice_number, customer_name, items, addons, total, discount_applied)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (invoice_number, customer_name, json.dumps(cart), json.dumps(selected_addons), total, discount_applied))
        conn.commit()
        
    invoice_filename = f"{invoice_number}.txt"
    
    try:
        with open(invoice_filename, 'w') as f:
            f.write(f"Invoice Number: {invoice_number}\n")
            f.write(f"Customer Name: {customer_name}\n")
            f.write(f"Invoice Date: {invoice_date}\n")
            f.write("\nItems:\n")
            
            for item, details in cart.items():
                f.write(f"  {item}: {details['quantity']} x ${details['price']:.2f} = ${details['quantity'] * details['price']:.2f}\n")
            f.write("\nAdd-ons:\n")
            
            for addon, price in selected_addons.items():
                f.write(f"  {addon}: ${price:.2f}\n")
            
            f.write(f"\nSubtotal: ${subtotal:.2f}\n")
            if discount_applied:
                f.write(f"Discount (10%): ${discount_amount:.2f}\n") 
                
            f.write(f"\nTotal: ${total:.2f}\n")
    except Exception as e:
        flash(f"Error saving invoice: {e}")
            
        with open('data/flowers.json', 'r') as file:
            flower_data = json.load(file)
            
        for flower_name, details in cart.items():
            if flower_name in flower_data:
                flower_data[flower_name]['stock'] -= details['quantity']
                if flower_data[flower_name]['stock'] < 0:
                    flower_data[flower_name]['stock'] = 0
            
        
        with open('data/flowers.json', 'w') as file:
            json.dump(flower_data, file, indent=4)
    
    session.pop('cart', None)
    session.pop('selected_addons', None)
    session.modified = True
    flash(f"Cart has been emptied")
    

    #displays invoice information on the invoice page
    return render_template('invoice.html', 
                           cart=cart, 
                           selected_addons=selected_addons,
                            total=total,
                            subtotal=subtotal,
                            discount_amount=discount_amount,
                            discount_applied=discount_applied,
                            customer_name=customer_name,
                            invoice_date=invoice_date)

    print(f"\nSaved order for: {customer_name}")
    print(f"cart: {cart}")
    print(f"Total: {total}\n")


@app.route('/cancel_saved_order/<int:order_id>', methods=['POST'])
def cancel_saved_order(order_id):
    with sqlite3.connect('flower_shop.db') as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM orders WHERE order_id = ?', (order_id,))
        conn.commit()
    
    flash(f"Order {order_id} has been cancelled.")
    return redirect(url_for('order_history'))

if __name__ == '__main__':
    initialise_database()
    app.run(debug=True)






