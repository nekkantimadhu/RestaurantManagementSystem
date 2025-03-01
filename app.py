from flask import Flask, render_template, request, redirect, flash, url_for, request, session, jsonify
import sqlite3
import datetime

app = Flask(__name__)
app.secret_key = 'restaurant_app_secret'


# Database connection
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return redirect(url_for('login'))

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         role = request.form['role']
#         username = request.form['username']
#         password = request.form['password']

#         conn = sqlite3.connect('database.db')
#         cursor = conn.cursor()

#         # Sample query based on role
#         if role == 'admin':
#             cursor.execute("SELECT * FROM Admin WHERE username=? AND password=?", (username, password))
#         elif role == 'chef':
#             cursor.execute("SELECT * FROM Chef WHERE username=? AND password=?", (username, password))
#         elif role == 'staff':
#             cursor.execute("SELECT * FROM Employee WHERE username=? AND password=?", (username, password))
#         elif role == 'customer':
#             cursor.execute("SELECT * FROM Customer WHERE username=? AND password=?", (username, password))

#         user = cursor.fetchone()
#         conn.close()

#         if user:
#             # User authenticated, redirect to their dashboard
#             if role == 'admin':
#                 return redirect(url_for('admin_dashboard'))
#             elif role == 'chef':
#                 return redirect(url_for('chef_dashboard'))
#             elif role == 'staff':
#                 return redirect(url_for('staff_dashboard'))
#             elif role == 'customer':
#                 return redirect(url_for('customer_dashboard'))
#         else:
#             flash('Invalid credentials. Please try again.')
#             return redirect(url_for('login'))

#     return render_template('login.html')

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         role = request.form['role'].strip().lower()
#         username = request.form['username']
#         password = request.form['password']


#         conn = sqlite3.connect('database.db')
#         cursor = conn.cursor()
        
#         try:
#             # Query Users table for matching username and password
#             cursor.execute("SELECT * FROM Users WHERE username=? AND password=? AND role=?", (username, password, role))
#             user = cursor.fetchone()
#             print("user",user)

#             if user:
#                 # If the user is found, check their role and redirect accordingly
#                 #role = user[5].lower()  # Assuming role is the 6th column in Users table
#                 user_id = user[0]  # Assuming user_id is the 1st column

#                 print(role)

#                 if role == 'customer':
#                     return redirect(url_for('customer_dashboard', user_id=user_id))
#                 elif role == 'chef':
#                     return redirect(url_for('chef_dashboard', user_id=user_id))
#                 elif role == 'admin':
#                     return redirect(url_for('admin_dashboard', user_id=user_id))
#                 elif role == 'staff':
#                     return redirect(url_for('staff_dashboard', user_id=user_id))
#                 else:
#                     return "Invalid role"

#             else:
#                 return "Invalid username or password"
#         except Exception as e:
#             return f"An error occurred: {str(e)}"
    
#     return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role'].strip().lower()  # Move role after username and password

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        try:
            # Query Users table for matching username and password
            cursor.execute("SELECT * FROM Users WHERE username=? AND password=? AND role=?", (username, password, role))
            user = cursor.fetchone()
            print("user:", user)

            if user:
                # If the user is found, check their role and redirect accordingly
                user_id = user[0]  # Assuming user_id is the 1st column

                # Store user ID in session
                # session['employee_id'] = user_id  # Set session variable
                # print(f"User logged in: {username} with ID: {user_id} and role: {role}")


                if role == 'staff':
                    cursor.execute("SELECT employee_id FROM Employee WHERE user_id=?", (user_id,))
                    employee = cursor.fetchone()
                    if employee:
                        employee_id = employee[0]  # Assuming employee_id is the first column
                        session['employee_id'] = employee_id  # Store employee_id in session
                    else:
                        return "Employee not found."
                elif role == 'customer':
                    cursor.execute("SELECT customer_id FROM Customer WHERE user_id=?", (user_id,))
                    customer = cursor.fetchone()
                    if customer:
                        session['customer_id'] = customer[0]  # Store customer_id in session
                    else:
                        return "Customer not found."
                
                session['user_id'] = user_id

                # Redirect to the appropriate dashboard based on role
                if role == 'customer':
                    return redirect(url_for('customer_dashboard', user_id=user_id))
                elif role == 'chef':
                    return redirect(url_for('chef_dashboard', user_id=user_id))
                elif role == 'admin':
                    return redirect(url_for('admin_dashboard', user_id=user_id))
                elif role == 'staff':
                    return redirect(url_for('staff_dashboard'))  # No need to pass user_id again
                else:
                    return "Invalid role"
            else:
                return "Invalid username or password"
        except Exception as e:
            return f"An error occurred: {str(e)}"
        finally:
            conn.close()  # Ensure connection is closed
    return render_template('login.html')




@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
        email = request.form['email']
        role = request.form['role'].strip().lower()

        try:
            conn = sqlite3.connect('database.db', check_same_thread=False, timeout=10)
            cursor = conn.cursor()

            # Insert into Users table
            cursor.execute("INSERT INTO Users (username, password, name, email, role) VALUES (?, ?, ?, ?, ?)",
                           (username, password, name, email, role))  # Save plain text password

            # Get the last inserted user_id
            user_id = cursor.lastrowid

            # Insert into respective role table based on the role
            if role == 'customer':
                cursor.execute("INSERT INTO Customer (user_id, name, email) VALUES (?, ?, ?)", (user_id, name, email))
            elif role == 'chef':
                cursor.execute("INSERT INTO Chef (user_id, name, email) VALUES (?, ?, ?)", (user_id, name, email))
            elif role == 'admin':
                cursor.execute("INSERT INTO Admin (user_id, name, email) VALUES (?, ?, ?)", (user_id, name, email))
            elif role == 'staff':
                cursor.execute("INSERT INTO Employee (user_id, name, email) VALUES (?, ?, ?)", (user_id, name, email))
            else:
                raise ValueError("Invalid role selected")

            conn.commit()  # Commit the transaction

            # Redirect to login page upon successful registration
            return redirect(url_for('login'))

        except sqlite3.IntegrityError:
            # Handle unique constraint violations (e.g., username already exists)
            return "Error: The username or email already exists. Please try again with a different one."

        except ValueError as ve:
            # Handle invalid role selection
            return f"Error: {ve}"

        except Exception as e:
            # Catch any other exceptions
            return f"An error occurred: {e}"
        finally:
            if conn:
                conn.close()

    return render_template('register.html')



# Admin can see inventory and employee management
# @app.route('/admin')
# def admin_dashboard():
#     conn = get_db_connection()
#     employees = conn.execute('SELECT * FROM Employee').fetchall()
#     inventory = conn.execute('SELECT * FROM Inventory').fetchall()
#     payments = conn.execute('SELECT * FROM Payments').fetchall()
#     menu = conn.execute('SELECT * FROM Menu').fetchall()
#     orders = conn.execute('SELECT * FROM Orders').fetchall()
#     print(menu)
#     menu = [dict(row) for row in menu]

#     conn.close()
#     return render_template('admin.html', employees=employees, inventory=inventory, payments=payments, menu=menu, orders=orders)


@app.route('/admin')
def admin_dashboard():
    conn = get_db_connection()

    # Fetching all necessary data from the database
    employees = conn.execute('SELECT * FROM Employee').fetchall()
    inventory = conn.execute('SELECT * FROM Inventory').fetchall()
    payments = conn.execute('SELECT * FROM Payments').fetchall()
    menu = conn.execute('SELECT * FROM Menu').fetchall()
    orders = conn.execute('SELECT * FROM Orders').fetchall()

    # Convert each row to a dictionary for the menu
    menu = [dict(row) for row in menu]

    # Convert rows to dictionaries for other tables if necessary
    employees = [dict(row) for row in employees]
    inventory = [dict(row) for row in inventory]
    payments = [dict(row) for row in payments]
    orders = [dict(row) for row in orders]

    conn.close()
    
    # Passing all data to the template
    return render_template('admin.html', employees=employees, inventory=inventory, payments=payments, menu=menu, orders=orders)


# Other routes follow...
# Customer can book a table
# @app.route('/book_table', methods=['GET', 'POST'])
# def book_table():
#     if request.method == 'POST':
#         customer_id = request.form['customer_id']
#         table_number = request.form['table_number']
#         date = request.form['date']
#         time = request.form['time']

#         conn = get_db_connection()
#         conn.execute('INSERT INTO Table_Booking (customer_id, table_number, date, time) VALUES (?, ?, ?, ?)',
#                      (customer_id, table_number, date, time))
#         conn.commit()
#         conn.close()

#         flash('Table booked successfully!')
#         return redirect(url_for('customer_dashboard', user_id=customer_id))

#     return render_template('book_table.html')


# @app.route('/book_table', methods=['POST'])
# def book_table():
#     try:
#         customer_name = request.form['customer_name']
#         number_of_people = request.form['number_of_people']
#         booking_date = request.form['booking_date']
#         booking_time = request.form['booking_time']
        
#         # Make sure to convert number_of_people to an integer
#         number_of_people = int(number_of_people)

#         # Assuming the customer is logged in, and their ID is retrieved
#         customer_id = get_customer_id(customer_name)
        
#         if not customer_id:
#             return jsonify({'message': 'Customer not found'}), 400

#         conn = get_db_connection()
#         conn.execute('INSERT INTO Table_Booking (customer_id, number_of_people, booking_date, booking_time) VALUES (?, ?, ?, ?)',
#                      (customer_id, number_of_people, booking_date, booking_time))
#         conn.commit()
#         conn.close()

#         return jsonify({'message': 'Table booked successfully!'}), 200

#     except Exception as e:
#         print(f"Error booking table: {e}")
#         return jsonify({'message': 'Error booking table'}), 400


# @app.route('/book_table', methods=['POST'])
# def book_table():
#     try:
#         customer_name = request.form['customer_name']
#         number_of_people = request.form['number_of_people']
#         booking_date = request.form['booking_date']
#         booking_time = request.form['booking_time']
        
#         # Validate that customer_name is provided
#         if not customer_name:
#             return jsonify({'message': 'Customer name is required!'}), 400

#         # Make sure to convert number_of_people to an integer
#         number_of_people = int(number_of_people)

#         # Assuming the customer is logged in, and their ID is retrieved
#         customer_id = get_customer_id(session['user_id'])
        
#         if customer_id is None:
#             return jsonify({'message': 'User not logged in'}), 400
        
#         conn = get_db_connection()
#         conn.execute('INSERT INTO Table_Booking (customer_id, customer_name, number_of_people, booking_date, booking_time) VALUES (?, ?, ?, ?, ?)',
#                      (customer_id, customer_name, number_of_people, booking_date, booking_time))
#         conn.commit()
#         conn.close()

#         return jsonify({'message': 'Table booked successfully!'}), 200

#     except Exception as e:
#         print(f"Error booking table: {e}")
#         return jsonify({'message': 'Error booking table'}), 400

@app.route('/book_table', methods=['POST'])
def book_table():
    try:
        # Retrieve user ID from the session
        customer_id = session.get('customer_id')  # or session.get('user_id') if you're using that

        # Check if user ID exists in session
        if not customer_id:
            return jsonify({'message': 'User not logged in'}), 400
        
        # Retrieve booking details from form
        customer_name = request.form['customer_name']  # Assuming you still want to take a name input
        number_of_people = int(request.form['number_of_people'])
        booking_date = request.form['booking_date']
        booking_time = request.form['booking_time']

        # Insert booking into the database
        conn = get_db_connection()
        conn.execute('INSERT INTO Table_Booking (customer_id, customer_name, number_of_people, booking_date, booking_time) VALUES (?, ?, ?, ?, ?)',
                     (customer_id, customer_name, number_of_people, booking_date, booking_time))
        conn.commit()
        conn.close()

        return jsonify({'message': 'Table booked successfully!'}), 200

    except Exception as e:
        print(f"Error booking table: {e}")
        return jsonify({'message': 'Error booking table'}), 400



def get_customer_id(customer_name):
    conn = get_db_connection()
    customer = conn.execute('SELECT customer_id FROM Customer WHERE name = ?', (customer_name,)).fetchone()
    conn.close()
    return customer['customer_id'] if customer else None


# # Customer dashboard (view menu, make orders)
# @app.route('/customer_dashboard/<int:user_id>')
# def customer_dashboard(user_id):
#     print(f"Welcome Cusomter {user_id}!")
#     conn = get_db_connection()
#     menu_items = conn.execute('SELECT * FROM Menu').fetchall()
#     conn.close()
#     return render_template('customer.html', menu=menu_items)

# @app.route('/customer_dashboard')
# def customer_dashboard():
#     with sqlite3.connect('database.db') as conn:
#         cursor = conn.cursor()
#         cursor.execute("SELECT * FROM Menu")
#         menu_items = cursor.fetchall()
#         # Convert fetched data to a list of dictionaries for easier rendering
#         menu_items = [
#             {'menu_id': item[0], 'name': item[1], 'description': item[2], 'price': item[3], 'image_url': item[4]}
#             for item in menu_items
#         ]
#     return render_template('customer.html', menu_items=menu_items)


@app.route('/customer_dashboard')
def customer_dashboard():
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Menu")
        menu_items = cursor.fetchall()

        # Convert fetched data to a list of dictionaries for easier rendering
        menu_items = [
            {'menu_id': item[0], 'name': item[1], 'description': item[2], 'price': item[3], 'image_url': item[4]}
            for item in menu_items
        ]

    # Retrieve the cart from the session
    cart = session.get('cart', {})

    # Optionally, you can enhance the cart to include item details if needed
    cart_items = []
    for menu_id, quantity in cart.items():
        # Assuming you want to fetch item details for the cart
        item_details = next((item for item in menu_items if item['menu_id'] == int(menu_id)), None)
        if item_details:
            cart_items.append({
                'menu_id': item_details['menu_id'],
                'name': item_details['name'],
                'quantity': quantity,
                'price': item_details['price'],
            })

    return render_template('customer.html', menu_items=menu_items, cart=cart_items)


# # Staff dashboard (manage orders, notify when food is prepared)
# @app.route('/staff_dashboard')
# def staff_dashboard():
#     conn = get_db_connection()
#     orders = conn.execute('SELECT * FROM Orders WHERE status = "Pending"').fetchall()
#     conn.close()
#     return render_template('staff.html', orders=orders)

# Update order status (food is prepared)
@app.route('/update_order_status/<int:order_id>', methods=['POST'])
def update_order_status(order_id):
    conn = get_db_connection()
    conn.execute('UPDATE Orders SET status = "Prepared" WHERE order_id = ?', (order_id,))
    conn.commit()
    conn.close()

    # JS alert for food prepared
    flash('Food is prepared!')
    return redirect(url_for('staff_dashboard'))

# # Make payment through QR or reception
# @app.route('/make_payment', methods=['GET', 'POST'])
# def make_payment():
#     if request.method == 'POST':
#         customer_id = request.form['customer_id']
#         order_id = request.form['order_id']
#         amount = request.form['amount']
#         payment_method = request.form['payment_method']

#         conn = get_db_connection()
#         conn.execute('INSERT INTO Payments (customer_id, order_id, amount, payment_method, status) VALUES (?, ?, ?, ?, "Paid")',
#                      (customer_id, order_id, amount, payment_method))
#         conn.commit()
#         conn.close()

#         flash('Payment successful!')
#         return redirect(url_for('order_history', user_id=customer_id))

#     return render_template('payment.html')

# @app.route('/make_payment', methods=['POST'])
# def make_payment():
#     try:
#         order_id = request.form['order_id']
#         amount = request.form['amount']
#         payment_method = request.form['payment_method']

#         # Get customer ID based on the order
#         conn = get_db_connection()
#         customer = conn.execute('SELECT customer_id FROM Orders WHERE order_id = ?', (order_id,)).fetchone()

#         if not customer:
#             return jsonify({'message': 'Order not found'}), 400
        
#         customer_id = customer['customer_id']

#         # Insert payment record
#         conn.execute('INSERT INTO Payments (customer_id, order_id, amount, payment_method, status) VALUES (?, ?, ?, ?, ?)',
#                      (customer_id, order_id, amount, payment_method, 'Completed'))
#         conn.commit()
#         conn.close()

#         return jsonify({'message': 'Payment successful!'}), 200

#     except Exception as e:
#         print(f"Error making payment: {e}")
#         return jsonify({'message': 'Error processing payment'}), 400


# @app.route('/make_payment', methods=['POST'])
# def make_payment():
#     try:
#         order_id = request.form['order_id']
#         amount = request.form['amount']
#         payment_method = request.form['payment_method']

#         # Get customer ID based on the order
#         conn = get_db_connection()
#         customer = conn.execute('SELECT customer_id FROM Orders WHERE order_id = ?', (order_id,)).fetchone()

#         if not customer:
#             flash('Order not found', 'error')
#             return redirect(url_for('customer_dashboard'))
        
#         customer_id = customer['customer_id']

#         # Insert payment record
#         conn.execute('INSERT INTO Payments (customer_id, order_id, amount, payment_method, status) VALUES (?, ?, ?, ?, ?)',
#                      (customer_id, order_id, amount, payment_method, 'Completed'))
#         conn.commit()
#         conn.close()

#         flash('Payment successful!', 'success')
#         return redirect(url_for('customer_dashboard'))

#     except Exception as e:
#         print(f"Error making payment: {e}")
#         flash('Error processing payment', 'error')
#         return redirect(url_for('customer_dashboard'))

# @app.route('/make_payment', methods=['POST'])
# def make_payment():
#     try:
#         order_id = request.form['order_id']
#         amount = request.form['amount']
#         payment_method = request.form['payment_method']

#         # Get customer ID based on the order
#         conn = get_db_connection()
#         order = conn.execute('SELECT customer_id FROM Orders WHERE order_id = ?', (order_id,)).fetchone()

#         if not order:
#             return jsonify({'message': 'Order not found'}), 400
        
#         customer_id = order['customer_id']

#         # Insert payment record
#         conn.execute('INSERT INTO Payments (customer_id, order_id, amount, payment_method, status) VALUES (?, ?, ?, ?, ?)',
#                      (customer_id, order_id, amount, payment_method, 'Completed'))
#         conn.commit()
#         conn.close()

#         return jsonify({'message': 'Payment successful!'}), 200

#     except Exception as e:
#         print(f"Error making payment: {e}")
#         return jsonify({'message': 'Error processing payment'}), 400

# @app.route('/make_payment', methods=['POST'])
# def make_payment():
#     try:
#         order_ids = request.form.getlist('order_ids')  # Get order IDs as a list
#         amount = request.form['amount']
#         payment_method = request.form['payment_method']

#         # You can add logic here to calculate the total amount based on the order IDs
#         # and check if they are valid orders.

#         for order_id in order_ids:
#             # Get customer ID based on the order
#             conn = get_db_connection()
#             order = conn.execute('SELECT customer_id FROM Orders WHERE order_id = ?', (order_id,)).fetchone()

#             if not order:
#                 return jsonify({'message': f'Order ID {order_id} not found'}), 400
            
#             customer_id = order['customer_id']

#             # Insert payment record
#             conn.execute('INSERT INTO Payments (customer_id, order_id, amount, payment_method, status) VALUES (?, ?, ?, ?, ?)',
#                          (customer_id, order_id, amount, payment_method, 'Completed'))

#         conn.commit()
#         conn.close()

#         return jsonify({'message': 'Payment successful!'}), 200

#     except Exception as e:
#         print(f"Error making payment: {e}")
#         return jsonify({'message': 'Error processing payment'}), 400

@app.route('/make_payment', methods=['POST'])
def make_payment():
    order_id = request.form['order_id']
    amount = request.form['amount']
    payment_method = request.form['payment_method']
    
    # Check if the order exists
    conn = get_db_connection()
    order = conn.execute('SELECT * FROM Orders WHERE order_id = ?', (order_id,)).fetchone()

    if not order:
        return jsonify({'message': 'Order not found'}), 400

    # Insert payment record
    insert_payment(order_id, amount, payment_method)
    return jsonify({'message': 'Payment successful!'}), 200

def insert_payment(order_id, amount, payment_method):
    customer_id = session['customer_id']
    conn = get_db_connection()
    conn.execute('INSERT INTO Payments (customer_id, order_id, amount, payment_method) VALUES (?, ?, ?, ?)', 
                 (customer_id, order_id, amount, payment_method))
    conn.commit()
    conn.close()



# @app.route('/chef_dashboard')
# def chef_dashboard():
#     # Logic for chef to view current orders
#     return render_template('chef_dashboard.html')

@app.route('/chef_dashboard')
def chef_dashboard():
    conn = get_db_connection()

    # Fetch pending orders
    pending_orders = conn.execute('''
        SELECT o.order_id, c.name AS customer_name, m.name AS menu_item_name, o.quantity 
        FROM Orders o 
        JOIN Customer c ON o.customer_id = c.customer_id 
        JOIN Menu m ON o.menu_id = m.menu_id 
        WHERE o.status = "Pending"
    ''').fetchall()

    # Fetch available menu items
    available_items = conn.execute('SELECT * FROM Menu').fetchall()

    # Fetch inventory stock
    inventory_stock = conn.execute('SELECT item_name, quantity FROM Inventory').fetchall()
    #print(inventory_stock)

    if inventory_stock:
        print(dict(inventory_stock[0]))

    conn.close()
    return render_template('chef_dashboard.html', 
                           pending_orders=pending_orders, 
                           available_items=available_items, 
                           inventory_stock=inventory_stock)



@app.route('/delete_menu_item/<int:menu_id>', methods=['POST'])
def delete_menu_item(menu_id):
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Menu WHERE menu_id=?", (menu_id,))
        conn.commit()
    return redirect('/admin')

@app.route('/order_history/<int:user_id>')
def order_history(user_id):
    conn = get_db_connection()
    orders = conn.execute('''
        SELECT Orders.order_id, Menu.name AS menu_item_name, Orders.quantity, Orders.status
        FROM Orders
        JOIN Menu ON Orders.menu_id = Menu.menu_id
        WHERE Orders.customer_id = ?
    ''', (user_id,)).fetchall()
    conn.close()

    return render_template('order_history.html', orders=orders)

# @app.route('/order/<int:menu_id>', methods=['GET', 'POST'])
# def place_order1(menu_id):
#     if request.method == 'POST':
#         customer_id = request.form['customer_id']
#         quantity = request.form['quantity']

#         conn = get_db_connection()
#         conn.execute('INSERT INTO Orders (customer_id, menu_id, quantity, status) VALUES (?, ?, ?, ?)',
#                      (customer_id, menu_id, quantity, 'Pending'))
#         conn.commit()
#         conn.close()

#         flash('Order placed successfully!')
#         return redirect(url_for('customer_dashboard', user_id=customer_id))

#     conn = get_db_connection()
#     menu_items = conn.execute('SELECT * FROM Menu WHERE menu_id = ?', (menu_id,)).fetchone()
#     conn.close()

#     return render_template('order.html', menu_items=menu_items)

# @app.route('/place_order/<int:menu_id>', methods=['GET', 'POST'])
# def place_order(menu_id):
#     if request.method == 'POST':
#         customer_id = request.form['customer_id']
#         quantity = request.form['quantity']

#         # Insert order into the database (this is a placeholder)
#         # conn.execute('INSERT INTO Orders (...)')

#         flash('Order placed successfully!')
#         return redirect(url_for('customer_dashboard', user_id=customer_id))

#     # Fetch menu details to show on the page
#     # menu_item = conn.execute('SELECT * FROM Menu WHERE menu_id = ?', (menu_id,)).fetchone()

#     return render_template('order.html', menu_id=menu_id)

# @app.route('/place_order', methods=['POST'])
# def place_order():
#     try:
#         customer_id = request.form['customer_id']  # Get customer ID from session or form
#         menu_id = request.form['menu_id']  # ID of the item being ordered
#         quantity = request.form['quantity']
#         table_number = request.form['table_number']  # Include table number for the order

#         conn = get_db_connection()
        
#         # Insert order into Orders table
#         conn.execute('INSERT INTO Orders (customer_id, menu_id, quantity) VALUES (?, ?, ?)',
#                     (customer_id, menu_id, quantity))
        
#         # Optionally update inventory
#         conn.execute('UPDATE Inventory SET quantity = quantity - ? WHERE item_name = (SELECT name FROM Menu WHERE menu_id = ?)', (quantity, menu_id))
        
#         conn.commit()
#         conn.close()
        
#         # You may also want to add functionality to notify staff and chef here
#         return jsonify({'message': 'Order placed successfully!'}), 200
#     except Exception as e:
#         return jsonify({"message": "Error placing order"}), 400

# @app.route('/place_order', methods=['POST'])
# def place_order():
#     try:
#         customer_id = request.form['customer_id']
#         menu_id = request.form['menu_id']
#         quantity = request.form['quantity']
#         table_number = request.form['table_number']  # Include table number

#         conn = get_db_connection()

#         # Insert the order with table number
#         conn.execute('INSERT INTO Orders (customer_id, menu_id, quantity, status, table_number) VALUES (?, ?, ?, ?, ?)',
#                      (customer_id, menu_id, quantity, 'Pending', table_number))
#         conn.commit()
#         conn.close()

#         flash('Order placed successfully!', 'success')
#         return redirect(url_for('customer_dashboard'))

#     except Exception as e:
#         print(f"Error placing order: {e}")
#         flash('Error placing order', 'error')
#         return redirect(url_for('customer_dashboard'))

# @app.route('/place_order', methods=['POST'])
# def place_order():
#     try:
#         customer_id = get_customer_id()  # Fetch the logged-in customer ID
#         cart = session.get('cart', {})

#         if not cart:
#             return jsonify({'message': 'Cart is empty'}), 400

#         # Insert orders into the database for each item in the cart
#         conn = get_db_connection()
#         cursor = conn.cursor()

#         order_ids = []  # Store the order IDs for payment later

#         for menu_id, quantity in cart.items():
#             cursor.execute('INSERT INTO Orders (customer_id, menu_id, quantity, status) VALUES (?, ?, ?, ?)',
#                            (customer_id, menu_id, quantity, 'Pending'))
#             order_ids.append(cursor.lastrowid)  # Get the last inserted order ID

#         conn.commit()
#         conn.close()

#         session.pop('cart', None)  # Clear the cart after placing the order
#         return jsonify({'message': 'Order placed successfully!', 'order_ids': order_ids}), 200
#     except Exception as e:
#         print(f"Error placing order: {e}")
#         return jsonify({'message': 'Error placing order'}), 400

# Fetch customer ID by customer_name
def get_customer_id(customer_name):
    conn = get_db_connection()
    customer = conn.execute('SELECT customer_id FROM Customer WHERE name = ?', (customer_name,)).fetchone()
    conn.close()
    if customer:
        return customer['customer_id']
    else:
        raise Exception(f"Customer with name '{customer_name}' not found")

# Insert order into the Orders table
# def insert_order(customer_id, total_amount):
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute('INSERT INTO Orders (customer_id, total_amount) VALUES (?, ?)', (customer_id, total_amount))
#     order_id = cursor.lastrowid  # Get the last inserted order ID
#     conn.commit()
#     conn.close()
#     return order_id

# # Insert order items into the OrderItems table
# def insert_order_item(order_id, menu_id, quantity):
#     conn = get_db_connection()
#     conn.execute('INSERT INTO OrderItems (order_id, menu_id, quantity) VALUES (?, ?, ?)', (order_id, menu_id, quantity))
#     conn.commit()
#     conn.close()

# Insert payment details into the Payments table
def insert_payment(order_id, total_amount, payment_method):
    conn = get_db_connection()
    conn.execute('INSERT INTO Payments (order_id, amount, payment_method, status) VALUES (?, ?, ?, ?)',
                 (order_id, total_amount, payment_method, 'Completed'))
    conn.commit()
    conn.close()

# Calculate total amount based on the items in the cart
def calculate_total(cart_items):
    total_amount = 0
    conn = get_db_connection()
    for menu_id, quantity in cart_items.items():
        item = conn.execute('SELECT price FROM Menu WHERE menu_id = ?', (menu_id,)).fetchone()
        total_amount += item['price'] * quantity
    conn.close()
    return total_amount

# @from flask import request, jsonify

# @app.route('/place_order', methods=['POST'])
# def place_order():
#     try:
#         # Parse JSON data from the request body
#         data = request.get_json()
#         print(request.get_json())

#         # Check if the required fields are present
#         if 'customer_name' not in data or 'cart' not in data or 'total_amount' not in data:
#             return jsonify({'message': 'Missing required fields'}), 400

#         # Fetch customer ID
#         customer_name = data['customer_name']
#         customer_id = get_customer_id(customer_name)  # Assumes function returns customer_id based on name
        
#         # Insert order
#         total_amount = data['total_amount']
#         order_id = insert_order(customer_id, total_amount)  # Assumes function inserts order and returns order_id
        
#         # Insert each item in the cart into the order_items table
#         cart = data['cart']
#         for menu_id, quantity in cart.items():
#             insert_order_item(order_id, menu_id, quantity)  # Insert each item into the DB
        
#         # Insert payment
#         insert_payment(order_id, total_amount)  # Assumes function inserts payment

#         return jsonify({'message': 'Order placed successfully'}), 200

#     except Exception as e:
#         print(f"Error placing order: {e}")
#         return jsonify({'message': 'Failed to place order'}), 500

# @app.route('/place_order', methods=['POST'])
# def place_order():
#     if 'customer_id' not in session:
#         return jsonify({'message': 'Please log in first.'}), 400

#     customer_id = session['customer_id']
    
#     cart = session.get('cart', {})
#     print("Cart contents:", cart) 
#     if not cart:
#         return jsonify({'message': 'Your cart is empty!'}), 400

#     # Calculate the total amount from the cart
#     total_amount = 0
#     for menu_id, item in cart.items():
#         menu_id = int(menu_id)
#         price = get_item_price(menu_id)  # Implement this function to fetch the price
#         total_amount += price * item['quantity']  # Calculate total

#     try:
#         # Insert the order
#         order_id = insert_order(customer_id, total_amount)

#         # Insert each item in the order
#         for menu_id, item in cart.items():
#             insert_order_item(order_id, menu_id, item['quantity'])

#         # Clear the cart after placing the order
#         session.pop('cart', None)

#         return jsonify({'message': 'Order placed successfully!'}), 200
#     except Exception as e:
#         return jsonify({'message': f"Error placing order: {str(e)}"}), 500

# @app.route('/place_order', methods=['POST'])
# def place_order():
#     if 'customer_id' not in session:
#         return jsonify({'message': 'Please log in first.'}), 400

#     customer_id = session['customer_id']
    
#     cart = session.get('cart', {})
#     if not cart:
#         return jsonify({'message': 'Your cart is empty!'}), 400

#     # Calculate the total amount from the cart
#     total_amount = sum(get_item_price(int(menu_id)) * quantity for menu_id, quantity in cart.items())

#     try:
#         # Insert the order
#         order_id = insert_order(customer_id, total_amount)

#         # Insert each item in the order
#         for menu_id_str, quantity in cart.items():
#             insert_order_item(order_id, int(menu_id_str), quantity)

#         # Clear the cart after placing order
#         session.pop('cart', None)

#         return jsonify({'message': 'Order placed successfully!'}), 200
#     except Exception as e:
#         return jsonify({'message': f"Error placing order: {str(e)}"}), 500


@app.route('/place_order', methods=['POST'])
def place_order():
    if 'customer_id' not in session:
        return jsonify({'message': 'Please log in first.'}), 400

    customer_id = session['customer_id']
    cart = session.get('cart', {})
    
    if not cart:
        return jsonify({'message': 'Your cart is empty!'}), 400

    total_amount = 0
    try:
        # Insert each item in the order
        for menu_id_str, quantity in cart.items():
            menu_id = int(menu_id_str)  # Convert menu_id to int
            price = get_item_price(menu_id)  # Ensure this function fetches the price correctly
            total_amount += price * quantity  # Calculate the total amount

            # Insert the order for each menu item
            insert_order(customer_id, menu_id, quantity, price * quantity)  # Insert with item details

        # Clear the cart after placing order
        session.pop('cart', None)

        return jsonify({'message': 'Order placed successfully!', 'total_amount': total_amount}), 200
    except Exception as e:
        return jsonify({'message': f"Error placing order: {str(e)}"}), 500


# def insert_order(customer_id, total_amount):
#     # Assuming you have a connection to the database
#     connection = get_db_connection()  # Implement this function to get your DB connection
#     cursor = connection.cursor()
    
#     # Adjust your SQL to include the total_amount column
#     cursor.execute('''
#         INSERT INTO Orders (customer_id, total_amount, order_date)
#         VALUES (?, ?, ?)
#     ''', (customer_id, total_amount, datetime.now()))  # Make sure to import datetime if using

#     connection.commit()
#     return cursor.lastrowid  # Return the order ID

# def insert_order(customer_id, total_amount):
#     # Assuming you have a connection to the database
#     connection = get_db_connection()  # Implement this function to get your DB connection
#     cursor = connection.cursor()
    
#     # Adjust your SQL to include the total_amount column
#     cursor.execute('''
#         INSERT INTO Orders (customer_id, total_amount, order_date)
#         VALUES (?, ?, ?)
#     ''', (customer_id, total_amount, datetime.now()))  # Make sure to import datetime if using

#     connection.commit()
#     return cursor.lastrowid  # Return the order ID

def get_cart_items_from_session():
    return session.get('cart', {})



def get_item_price(menu_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    try:
        # Query to get the price of the item based on menu_id
        cursor.execute("SELECT price FROM Menu WHERE menu_id=?", (menu_id,))
        result = cursor.fetchone()
        if result:
            return result[0]  # Return the price
        else:
            raise ValueError("Menu item not found.")
    finally:
        conn.close()

def get_item_details(menu_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT name, price FROM Menu WHERE menu_id=?", (menu_id,))
        result = cursor.fetchone()
        if result:
            return {'name': result[0], 'price': result[1]}
        else:
            raise ValueError("Menu item not found.")
    finally:
        conn.close()


# def insert_order(customer_id, total_amount):
#     conn = get_db_connection()
#     conn.execute('INSERT INTO Orders (customer_id, total_amount) VALUES (?, ?)', (customer_id, total_amount))
#     order_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
#     conn.commit()
#     conn.close()
#     return order_id

# def insert_order_item(order_id, menu_id, quantity):
#     conn = get_db_connection()
#     conn.execute('INSERT INTO Order_Items (order_id, menu_id, quantity) VALUES (?, ?, ?)', (order_id, menu_id, quantity))
#     conn.commit()
#     conn.close()

from datetime import datetime

# def insert_order(customer_id, total_amount):
#     # Get the database connection
#     conn = get_db_connection()  
#     try:
#         # Insert the order into the Orders table
#         cursor = conn.cursor()
#         cursor.execute('''
#             INSERT INTO Orders (customer_id, total_amount, order_date, status)
#             VALUES (?, ?, ?, ?)
#         ''', (customer_id, total_amount, datetime.now(), 'Pending'))  # Assuming 'Pending' is the initial status

#         order_id = cursor.lastrowid  # Get the last inserted order ID
#         conn.commit()  # Commit the transaction
#         return order_id  # Return the order ID
#     finally:
#         conn.close()  # Ensure the connection is closed

def insert_order(customer_id, menu_id, quantity, total_amount):
    connection = get_db_connection()
    cursor = connection.cursor()
    
    cursor.execute('''
        INSERT INTO Orders (customer_id, menu_id, quantity, total_amount, order_date)
        VALUES (?, ?, ?, ?, ?)
    ''', (customer_id, menu_id, quantity, total_amount, datetime.now()))  # Make sure to import datetime if using

    connection.commit()
    return cursor.lastrowid  # Return the order ID


def insert_order_item(order_id, menu_id, quantity):
    conn = get_db_connection()
    try:
        # Insert the order item into the Order_Items table
        conn.execute('INSERT INTO Order_Items (order_id, menu_id, quantity) VALUES (?, ?, ?)', 
                     (order_id, menu_id, quantity))
        conn.commit()  # Commit the transaction
    finally:
        conn.close()  # Ensure the connection is closed



# Route to fetch menu items
@app.route('/get_menu_items', methods=['GET'])
def get_menu_items():
    conn = get_db_connection()
    menu_items = conn.execute('SELECT * FROM Menu').fetchall()
    conn.close()
    
    return jsonify([dict(item) for item in menu_items]), 200

@app.route('/add_employee', methods=['POST'])
def add_employee():
    try:
        employee_name = request.form['employee_name']
        employee_email = request.form['employee_email']
        employee_id = request.form['employee_id']

        conn = get_db_connection()
        conn.execute('INSERT INTO Employee (user_id, name, email) VALUES (?, ?, ?)', 
                     (employee_id, employee_name, employee_email))
        conn.commit()
        conn.close()
        return redirect('/admin')  # Redirect to the admin dashboard
    except Exception as e:
        print(f"Error adding employee: {e}")
        return "An error occurred while adding the employee", 400


# Route to add a new menu item
@app.route('/add_menu_item', methods=['POST'])
def add_menu_item():
    item_name = request.form['item_name']
    item_price = request.form['item_price']
    item_description = request.form['item_description']
    
    conn = get_db_connection()
    #conn.execute('INSERT INTO Menu (name, price) VALUES (?, ?)', (item_name, item_price))
    conn.execute('INSERT INTO Menu (name, price, description) VALUES (?, ?, ?)', (item_name, item_price, item_description))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_dashboard'))


# Fetch employee details
def get_employee_details(employee_id):
    conn = get_db_connection()
    employee = conn.execute('SELECT * FROM Employee WHERE employee_id = ?', (employee_id,)).fetchone()
    conn.close()
    return employee

# Fetch all orders
def get_all_orders():
    conn = get_db_connection()
    orders = conn.execute('SELECT o.order_id, c.name AS customer_name, o.status FROM Orders o JOIN Customer c ON o.customer_id = c.customer_id').fetchall()
    conn.close()
    return orders

# Fetch pending orders
def get_pending_orders():
    conn = get_db_connection()
    pending_orders = conn.execute('SELECT o.order_id, c.name AS customer_name FROM Orders o JOIN Customer c ON o.customer_id = c.customer_id WHERE o.status = "Pending"').fetchall()
    conn.close()
    return pending_orders

# Fetch vacant tables (Assuming you have a logic for this, e.g., based on current bookings)
def get_vacant_tables():
    # This example assumes there are 10 tables, you can modify based on your logic
    conn = get_db_connection()
    booked_tables = conn.execute('SELECT DISTINCT booking_id FROM Table_Booking').fetchall()
    # Assuming table numbers range from 1 to 10
    total_tables = {i for i in range(1, 11)}
    booked_table_ids = {row['booking_id'] for row in booked_tables}  # Modify based on your actual table booking logic
    vacant_tables = total_tables - booked_table_ids
    conn.close()
    return [{'table_number': table, 'seats': 4} for table in vacant_tables]  # Assuming each table has 4 seats

# Fetch order notifications (For demonstration, it will fetch all pending orders)
def get_order_notifications():
    conn = get_db_connection()
    notifications = conn.execute('SELECT order_id, status FROM Orders WHERE status = "Pending"').fetchall()
    conn.close()
    return [{'order_id': n['order_id'], 'message': f"Order ID {n['order_id']} is pending."} for n in notifications]

# Route for staff dashboard
# @app.route('/staff', methods=['GET'])
# def staff_dashboard():
#     employee_id = session.get('employee_id')  # Assuming employee_id is stored in the session
#     print(f"Session data before accessing staff: {session}")

#     if not employee_id:
#         print("Redirecting to login; employee_id not found in session.")
#         return redirect(url_for('login'))  # Redirect to login if not logged in

#     employee = get_employee_details(employee_id)
#     if not employee:  # Check if the employee was found
#         print("Redirecting to login; employee not found.")
#         return redirect(url_for('login'))  # Redirect if no employee found
    

#     prepared_orders = conn.execute('''
#         SELECT o.order_id, c.name AS customer_name, m.name AS menu_item_name, o.quantity, o.status 
#         FROM Orders o 
#         JOIN Customer c ON o.customer_id = c.customer_id 
#         JOIN Menu m ON o.menu_id = m.menu_id 
#         WHERE o.status = "Prepared"
#     ''').fetchall()

#     print(f"Employee ID in session: {employee_id}")
#     print(f"Employee Details: {employee}")

#     orders = get_all_orders()
#     pending_orders = get_pending_orders()
#     vacant_tables = get_vacant_tables()
#     notifications = get_order_notifications()

#     return render_template('staff.html', employee=employee, orders=orders, 
#                            pending_orders=pending_orders, vacant_tables=vacant_tables,
#                            notifications=notifications)


@app.route('/staff', methods=['GET', 'POST'])
def staff_dashboard():
    employee_id = session.get('employee_id')

    if not employee_id:
        return redirect(url_for('login'))  # Redirect to login if not logged in

    employee = get_employee_details(employee_id)
    if not employee:
        return redirect(url_for('login'))

    conn = get_db_connection()

    # Fetch prepared orders for serving
    prepared_orders = conn.execute('''
        SELECT o.order_id, c.name AS customer_name, m.name AS menu_item_name, o.quantity, o.status
        FROM Orders o 
        JOIN Customer c ON o.customer_id = c.customer_id
        JOIN Menu m ON o.menu_id = m.menu_id
        WHERE o.status = "Prepared"
    ''').fetchall()

    # Fetch served orders waiting for payment
    served_orders = conn.execute('''
        SELECT o.order_id, c.name AS customer_name, m.name AS menu_item_name, o.quantity, o.status, IFNULL(p.amount, 0) AS amount FROM Orders o 
        JOIN Customer c ON o.customer_id = c.customer_id
        JOIN Menu m ON o.menu_id = m.menu_id
        LEFT JOIN Payments p ON o.order_id = p.order_id
        WHERE o.status = "Served"

    ''').fetchall()

    conn.close()

    return render_template('staff.html', employee=employee, prepared_orders=prepared_orders, served_orders=served_orders)

@app.route('/mark_as_served/<int:order_id>', methods=['POST'])
def mark_as_served(order_id):
    conn = get_db_connection()
    conn.execute('UPDATE Orders SET status = "Served" WHERE order_id = ?', (order_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Order marked as served!'})


@app.route('/mark_as_completed/<int:order_id>', methods=['POST'])
def mark_as_completed(order_id):
    data = request.get_json()
    payment_id = data.get('payment_id')
    payment_method = data.get('payment_method')
    amount = data.get('amount')

    conn = get_db_connection()

    # Fetch the customer_id for the order
    order = conn.execute('SELECT customer_id FROM Orders WHERE order_id = ?', (order_id,)).fetchone()
    if not order:
        return jsonify({'success': False, 'message': 'Order not found.'}), 404

    customer_id = order['customer_id']

    # Insert payment details into Payments table
    conn.execute('''
        INSERT INTO Payments (payment_id, customer_id, order_id, amount, payment_method, status)
        VALUES (?, ?, ?, ?, ?, 'Completed')
    ''', (payment_id, customer_id, order_id, amount, payment_method))

    # Mark the order as completed
    conn.execute('UPDATE Orders SET status = "Completed" WHERE order_id = ?', (order_id,))
    conn.commit()
    conn.close()

    return jsonify({'success': True, 'message': f'Order #{order_id} marked as completed with payment.'})


# Route to prepare an order
@app.route('/prepare_order/<int:order_id>', methods=['POST'])
def prepare_order(order_id):
    try:
        conn = get_db_connection()
        conn.execute('UPDATE Orders SET status = "Prepared" WHERE order_id = ?', (order_id,))
        conn.commit()
        return '', 204  # No content response
    except Exception as e:
        return str(e), 500  # Internal Server Error
    finally:
        conn.close()

@app.route('/serve_order/<int:order_id>', methods=['POST'])
def serve_order(order_id):
    conn = get_db_connection()

    # Update the order status to 'Served'
    conn.execute('UPDATE Orders SET status = "Served" WHERE order_id = ?', (order_id,))
    conn.commit()
    conn.close()

    return '', 204  # No content response

@app.route('/get_order_details/<int:order_id>', methods=['GET'])
def get_order_details(order_id):
    conn = get_db_connection()
    
    # Fetch the order and payment details based on the order ID
    order = conn.execute('''
        SELECT o.order_id, o.total_amount, c.name AS customer_name
        FROM Orders o 
        JOIN Customer c ON o.customer_id = c.customer_id
        WHERE o.order_id = ?
    ''', (order_id,)).fetchone()
    
    conn.close()
    
    if order:
        return jsonify({
            'success': True,
            'order_id': order['order_id'],
            'amount': order['total_amount'],
            'customer_name': order['customer_name']
        })
    else:
        return jsonify({'success': False, 'message': 'Order not found.'}), 404



@app.route('/logout')
def logout():
    # Here you would implement your logout logic.
    return redirect(url_for('login'))  # Redirect to the login page

# @app.route('/add_to_cart', methods=['POST'])
# def add_to_cart():
#     try:
#         menu_id = request.form['menu_id']
#         quantity = int(request.form['quantity'])  # Quantity of the menu item
        
#         # Initialize the cart in the session if it doesn't exist
#         if 'cart' not in session:
#             session['cart'] = {}

#         # Update the cart with the new item or increment the quantity
#         if menu_id in session['cart']:
#             session['cart'][menu_id] += quantity
#         else:
#             session['cart'][menu_id] = quantity

#         session.modified = True  # Mark the session as modified
#         return jsonify({'message': 'Item added to cart successfully!'}), 200
#     except Exception as e:
#         print(f"Error adding to cart: {e}")
#         return jsonify({'message': 'Error adding to cart'}), 400

# @app.route('/add_to_cart', methods=['POST'])
# def add_to_cart():
#     menu_id = request.form['menu_id']
#     item_name = request.form['item_name']  # Get the item name
#     item_price = float(request.form['item_price'])  # Get the item price

#     cart = session.get('cart', {})

#     if menu_id in cart:
#         cart[menu_id]['quantity'] += 1  # Increase quantity if already in cart
#     else:
#         cart[menu_id] = {'name': item_name, 'price': item_price, 'quantity': 1}  # Add new item

#     session['cart'] = cart  # Update session
#     session.modified = True
#     return jsonify({'message': 'Item added to cart successfully!'})

# @app.route('/add_to_cart', methods=['POST'])
# def add_to_cart():
#     menu_id = request.form['menu_id']
#     item_name = request.form['item_name']  # Get the item name from the request
#     cart = session.get('cart', {})

#     if menu_id in cart:
#         cart[menu_id]['quantity'] += 1  # Increase quantity if item already in cart
#     else:
#         cart[menu_id] = {'quantity': 1, 'name': item_name}  # Add new item with quantity and name

#     session['cart'] = cart
#     session.modified = True
#     return jsonify({'message': 'Item added to cart successfully!'})


# @app.route('/add_to_cart', methods=['POST'])
# def add_to_cart():
#     menu_id = request.form['menu_id']
#     quantity = int(request.form['quantity'])

#     # Fetch item details (name and price) from the database
#     item_details = get_item_details(menu_id)  # Implement this function

#     # Update cart in session
#     cart = session.get('cart', {})
#     if menu_id in cart:
#         cart[menu_id]['quantity'] += quantity
#     else:
#         cart[menu_id] = {
#             'name': item_details['name'],
#             'price': item_details['price'],
#             'quantity': quantity
#         }
    
#     session['cart'] = cart
#     session.modified = True
#     return jsonify({'message': 'Item added to cart successfully!'})

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    menu_id = request.form.get('menu_id')
    quantity = request.form.get('quantity')

    # Assuming you have a session to store cart items
    if 'cart' not in session:
        session['cart'] = {}

    # Add or update the item in the cart
    if menu_id in session['cart']:
        session['cart'][menu_id] += int(quantity)  # Update quantity if item already in cart
    else:
        session['cart'][menu_id] = int(quantity)  # Add new item to cart

    session.modified = True  # Mark session as modified
    return jsonify({'message': 'Item added to cart successfully!'}), 200



@app.route('/view_cart', methods=['GET'])
def view_cart():
    cart_items = get_cart_items_from_session()  # Get cart items from session
    if not cart_items:
        return jsonify({'message': 'Your cart is empty!'}), 200

    # Fetch menu items from DB based on the IDs in the cart
    menu_items = fetch_menu_items_by_ids(cart_items.keys())

    # Prepare the response data
    response_data = []
    for item in menu_items:
        # Ensure the item is present in the cart
        menu_id = str(item['menu_id'])  # Ensure menu_id is a string for comparison
        if menu_id in cart_items:
            response_data.append({
                'name': item['name'],
                'menu_id': menu_id,
                'quantity': cart_items[menu_id],  # Get quantity from the cart
                'price': item['price'],
                'total_price': item['price'] * cart_items[menu_id]  # Calculate total price for the item
            })

    return jsonify(response_data), 200

def fetch_menu_items_by_ids(menu_ids):
    # Convert menu_ids to a list of integers
    menu_ids = [int(menu_id) for menu_id in menu_ids]
    
    # Create a connection to the database
    conn = get_db_connection()  # Make sure you have this function defined
    cursor = conn.cursor()

    # Create a SQL query to fetch menu items by their IDs
    placeholders = ', '.join('?' for _ in menu_ids)  # Create placeholders for the query
    query = f'SELECT menu_id, name, price FROM Menu WHERE menu_id IN ({placeholders})'
    
    try:
        # Execute the query
        cursor.execute(query, menu_ids)
        menu_items = cursor.fetchall()

        # Convert the result into a list of dictionaries
        return [{'menu_id': item[0], 'name': item[1], 'price': item[2]} for item in menu_items]
    except Exception as e:
        print(f"Error fetching menu items: {str(e)}")
        return []  # Return an empty list if there's an error
    finally:
        cursor.close()
        conn.close()  # Always close the connection




# @app.route('/remove_from_cart', methods=['POST'])
# def remove_from_cart():
#     menu_id = request.form['menu_id']

#     cart = session.get('cart', {})

#     if menu_id in cart:
#         del cart[menu_id]
#         session.modified = True
#         return jsonify({'message': 'Item removed from cart successfully!'})
#     else:
#         return jsonify({'message': 'Item not found in cart!'}), 404

# @app.route('/update_cart', methods=['POST'])
# def update_cart():
#     menu_id = request.form['menu_id']
#     action = request.form['action']

#     cart = session.get('cart', {})

#     if menu_id in cart:
#         if action == 'increase':
#             cart[menu_id] += 1
#         elif action == 'decrease' and cart[menu_id] > 1:
#             cart[menu_id] -= 1
#         elif action == 'decrease' and cart[menu_id] == 1:
#             del cart[menu_id]  # If quantity is 1 and decreased, remove item
#         session.modified = True
#         return jsonify({'message': 'Cart updated successfully!'})
#     else:
#         return jsonify({'message': 'Item not found in cart!'}), 404

@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    menu_id = request.form['menu_id']
    cart = session.get('cart', {})

    if menu_id in cart:
        del cart[menu_id]  # Remove the item from cart
        session.modified = True
        return jsonify({'message': 'Item removed from cart successfully!'})
    else:
        return jsonify({'message': 'Item not found in cart!'}), 404

@app.route('/update_cart', methods=['POST'])
def update_cart():
    menu_id = request.form.get('menu_id')
    action = request.form.get('action')

    # Check if the cart exists in the session
    if 'cart' not in session:
        return jsonify({'message': 'Your cart is empty!'}), 400

    # Convert menu_id to string for the session dictionary
    menu_id = str(menu_id)

    if menu_id not in session['cart']:
        return jsonify({'message': 'Item not found in cart!'}), 404

    if action == 'increase':
        session['cart'][menu_id] += 1  # Increment quantity
    elif action == 'decrease':
        if session['cart'][menu_id] > 1:
            session['cart'][menu_id] -= 1  # Decrement quantity
        else:
            return jsonify({'message': 'Cannot decrease quantity below 1!'}), 400

    session.modified = True  # Mark session as modified
    return jsonify({'message': 'Cart updated successfully!'}), 200






@app.route('/update_employee/<int:employee_id>', methods=['POST'])
def update_employee(employee_id):
    try:
        employee_name = request.form['employee_name']
        employee_email = request.form['employee_email']

        conn = get_db_connection()
        conn.execute('UPDATE Employee SET name = ?, email = ? WHERE user_id = ?', 
                     (employee_name, employee_email, employee_id))
        conn.commit()
        conn.close()
        return redirect('/admin')  # Redirect to the admin dashboard
    except Exception as e:
        print(f"Error updating employee: {e}")
        return "An error occurred while updating the employee", 400


@app.route('/update_menu/<int:menu_id>', methods=['POST'])
def update_menu(menu_id):
    name = request.form['item_name']
    price = request.form['item_price']
    description = request.form['item_description']
    # Update the menu item in the database
    conn = get_db_connection()
    conn.execute('UPDATE Menu SET name = ?, price = ?, description = ? WHERE menu_id = ?',
                 (name, price, description, menu_id))
    conn.commit()
    conn.close()
    return redirect('/admin')

@app.route('/update_order/<int:order_id>', methods=['POST'])
def update_order(order_id):
    status = request.form['order_status']
    # Update the order status in the database
    conn = get_db_connection()
    conn.execute('UPDATE Orders SET status = ? WHERE order_id = ?',
                 (status, order_id))
    conn.commit()
    conn.close()
    return redirect('/admin')

# @app.route('/update_inventory/<int:item_id>', methods=['POST'])
# def update_inventory(item_id):
#     try:
#         quantity = request.form['quantity']

#         conn = get_db_connection()
#         conn.execute('UPDATE Inventory SET quantity = ? WHERE item_id = ?', 
#                      (quantity, item_id))
#         conn.commit()
#         conn.close()
#         return redirect('/admin')  # Redirect to the admin dashboard after updating
#     except Exception as e:
#         print(f"Error updating inventory: {e}")
#         return "An error occurred while updating the inventory", 400

# @app.route('/update_inventory/<string:item_name>', methods=['POST'])
# def update_inventory(item_name):
#     quantity = request.form['quantity']

#     conn = get_db_connection()
#     conn.execute('UPDATE Inventory SET quantity = ? WHERE item_name = ?', 
#                  (quantity, item_name))
#     conn.commit()
#     conn.close()
#     return redirect('/admin')  # Redirect back to admin page or any page you prefer

@app.route('/update_inventory/<string:item_name>', methods=['POST'])
def update_inventory(item_name):
    quantity = request.form['quantity']

    conn = get_db_connection()
    conn.execute('UPDATE Inventory SET quantity = ? WHERE item_name = ?', 
                 (quantity, item_name))
    conn.commit()
    conn.close()

    return jsonify({'status': 'success'}), 200  # Return JSON response to indicate success



def get_inventory():
    conn = get_db_connection()  # Your function to get a database connection
    cursor = conn.cursor()
    cursor.execute("SELECT item_name, quantity FROM Inventory")  # Adjust your query as needed
    items = cursor.fetchall()
    conn.close()
    return items



if __name__ == '__main__':
    app.run(debug=True)


