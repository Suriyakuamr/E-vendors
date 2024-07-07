from flask import Flask, render_template, request, redirect, url_for, session,flash,current_app
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField 
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask import jsonify, request
from models import Cart, PurchaseHistory, db,Product,User, DeliveryAddress
import csv
import sqlite3   
from form import UserForm
from forms import DeliveryForm
from datetime import datetime
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os    
from werkzeug.utils import secure_filename
from forma import ProductForm
 




app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///e-vendors.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] ='\Downloads\E-Vendors\static\pro'

 
db.init_app(app)  

 
 
login_manager = LoginManager(app)
login_manager.login_view = 'login'
migrate = Migrate(app, db) 

@login_manager.user_loader
def load_user(user_id):

    with app.app_context():
        session = db.session
        return session.get(User, int(user_id))
   
# Cart items will be stored in this dictionary
cart_items={}
 
#upload a product By User itself 
@app.route('/upload_product', methods=['GET', 'POST'])
@login_required
def upload_product():
    form = ProductForm()

    if form.validate_on_submit():
        name = form.name.data
        price = form.price.data
        image = form.image.data
        specifications = form.specifications.data
        features = form.features.data
        warranty = form.warranty.data

        # Save the image file and get the path
        image = save_image(image)

        # Create a new product instance with the form data
        new_product = Product(
            name=name,
            price=price,
            image=image,
            specifications=specifications,
            features=features,
            warranty=warranty
        )

        # Add the new product to the database
        db.session.add(new_product)
        db.session.commit()

        flash('Product uploaded successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('upload_product.html', form=form)
    
 
def save_image(image):
   
    if image:
        filename = secure_filename(image.filename)
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return os.path.join('static', 'pro', filename)
    else:
        return None 

 
 

#register
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = UserForm()  # Instantiate the UserForm

    if form.validate_on_submit():  # Check if the form is submitted and valid
        username = form.username.data
        password = form.password.data
        email    =form.email.data
        phone_number = form.phone_number.data

        # No need to re-validate phone number length here since it's already handled by the form

        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            flash('Username already exists. Please choose a different one.', 'error')
        else:
            existing_phone_user = User.query.filter_by(phone_number=phone_number).first()
            if existing_phone_user:
                flash('Phone number already registered. Please use a different one.', 'error')
            existing_mail = User.query.filter_by(email=email).first()
            if existing_mail:
                flash(' e mail already registered. Please use a different one.', 'error')
            else:
                new_user = User(username=username,email=email,  password=password, phone_number=phone_number)
                db.session.add(new_user)
                db.session.commit()

                flash('Registration successful! You can now log in.', 'success')
                return redirect(url_for('login'))

    return render_template('register.html', form=form)


#login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone_number = request.form.get('phone_number')
        password = request.form.get('password')

        user = User.query.filter_by(phone_number=phone_number).first()

        if user and user.password == password:
            login_user(user)
            flash('Logged in successfully!', 'success')          
            return redirect(url_for('index'))

        flash('Login failed. Check your phone number and password.', 'error')

    return render_template('login.html', current_user=current_user)    


#logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))

#userprofile  
@app.route('/profile/<int:user_id>')
def profile(user_id):
    with app.app_context():
        session = db.session
        user = session.get(User, user_id)  # Use session.get() instead of session.query().get()

    return render_template('user.html', user=user)
 
    
 

#search bar for pc
@app.route('/search',methods=['GET'])
def search():
    search_query = request.args.get('search', '')
    
    if search_query:
        # Perform a database query to find products based on the search query
        # You might need to adjust this query based on your Product model structure
        products = Product.query.filter(Product.name.ilike(f'%{search_query}%')).all()
    else:
        # If no search query provided, show all products (or an empty list)
        products = Product.query.all()

    return render_template('search.html', products=products, search_query=search_query)
    
#search bar for mobiles 
@app.route('/searchbar',methods=['GET'])
def searchbar():
    search_query = request.args.get('search', '')
    
    if search_query:
        # Perform a database query to find products based on the search query
        # You might need to adjust this query based on your Product model structure
        products = Product.query.filter(Product.name.ilike(f'%{search_query}%')).all()
    else:
        # If no search query provided, show all products (or an empty list)
        products = Product.query.all()

    return render_template('searchbar.html', products=products, search_query=search_query)  

 
#filter out and show the products by product name
@app.route('/filter_products/<product_name>')
def filter_products(product_name):
  
    products = Product.query.filter(func.lower(Product.name).contains(func.lower(product_name))).all()

    # Render a new template to display the filtered products
    return render_template('brands.html', products=products, product_name=product_name)
    
#filter out and show the products by specifications
@app.route('/filter_speci/<speci_name>')
def filter_speci(speci_name):
  
    products = Product.query.filter(func.lower(Product.specifications).contains(func.lower(speci_name))).all()

    return render_template('brands.html', products=products,  speci_name= speci_name)    


#filter out and show the products by product name pass the 2 product name
@app.route('/filter_args/<product_name1>/<product_name2>')
def filter_args(product_name1, product_name2):
     
    products = Product.query.filter(
        (func.lower(Product.name).contains(func.lower(product_name1))) |
        (func.lower(Product.name).contains(func.lower(product_name2)))
    ).all()

     
    return render_template('brands.html', products=products, product_name1=product_name1, product_name2=product_name2)

#filter out and show the products by product name pass the 3 product name
@app.route('/filter_arguments/<product_name1>/<product_name2>/<product_name3>')
def filter_arguments(product_name1, product_name2, product_name3):
     
    products = Product.query.filter(
        (func.lower(Product.name).contains(func.lower(product_name1))) |
        (func.lower(Product.name).contains(func.lower(product_name2))) |
        (func.lower(Product.name).contains(func.lower(product_name3)))
        
    ).all()
 
    return render_template('brands.html', products=products, product_name1=product_name1, product_name2=product_name2,product_name3 = product_name3)

 
from sqlalchemy import or_,and_
#for furniture.html
@app.route('/filter_furn/<specifications_text1>/<specifications_text2>')
def filter_furn(specifications_text1,specifications_text2):
     
    products = Product.query.filter(
        (func.lower(Product.name).contains(func.lower(specifications_text1))) |
        (func.lower(Product.name).contains(func.lower(specifications_text2))),
        and_(Product.price >= 500, Product.price <= 30000)
    ).all()
    
     
    return render_template('brands.html', products=products, specifications_text1=specifications_text1 , specifications_text2=specifications_text2)
    
#for furniture.html
@app.route('/filter_furn1/<specifications_text1>/<specifications_text2>')
def filter_furn1(specifications_text1,specifications_text2):
    # Filter products by specifications containing the provided text and price less than 15,000
    products = Product.query.filter(
        (func.lower(Product.name).contains(func.lower(specifications_text1))) |
        (func.lower(Product.name).contains(func.lower(specifications_text2))),
        and_(Product.price >= 500, Product.price <= 1500)
    ).all()
    
    # Render a new template to display the filtered products
    return render_template('brands.html', products=products, specifications_text1=specifications_text1 , specifications_text2=specifications_text2)    


#filter out and show the products by product name  by price range for mobiles.html
@app.route('/filter_fas1/<specifications_text>')
def filter_fas1(specifications_text):
     
    products = Product.query.filter(
        func.lower(Product.specifications).contains(func.lower(specifications_text)),
        and_(Product.price >= 500, Product.price <= 1000)
    ).all()
    
    # Render a new template to display the filtered products
    return render_template('brands.html', products=products, specifications_text=specifications_text)

#filter out and show the products by product name  by price range for mobiles.html
@app.route('/filter_fas/<specifications_text>')
def filter_fas(specifications_text):
    # Filter products by specifications containing the provided text and price less than 15,000
    products = Product.query.filter(
        func.lower(Product.specifications).contains(func.lower(specifications_text)),
        Product.price <= 500
    ).all()
    
    # Render a new template to display the filtered products
    return render_template('brands.html', products=products, specifications_text=specifications_text)

#filter out and show the products by product name  by price range for mobiles.html
@app.route('/filter_price/<specifications_text>')
def filter_price(specifications_text):
    # Filter products by specifications containing the provided text and price less than 15,000
    products = Product.query.filter(
        func.lower(Product.specifications).contains(func.lower(specifications_text)),
        Product.price < 15000
    ).all()
        
    return render_template('brands.html', products=products, specifications_text=specifications_text)

#filter out and show the products by product name  by price range for mobiles.html
@app.route('/filter_ten/<specifications_text>')
def filter_ten(specifications_text):
    # Filter products by specifications containing the provided text and price less than 15,000
    products = Product.query.filter(
        func.lower(Product.specifications).contains(func.lower(specifications_text)),
        and_(Product.price >= 80000, Product.price <= 100000)
    ).all()
    
     
    return render_template('brands.html', products=products, specifications_text=specifications_text)

#filter out and show the products by product name  by price range     
@app.route('/filter_twenty/<specifications_text>')
def filter_twenty(specifications_text):
    # Filter products by specifications containing the provided text and price less than 15,000
    products = Product.query.filter(
        func.lower(Product.specifications).contains(func.lower(specifications_text)),
        Product.price < 25000
    ).all()
    
    # Render a new template to display the filtered products
    return render_template('brands.html', products=products, specifications_text=specifications_text)    
 
 
@app.route('/partners')
@login_required
def partners( ):
     
    products = Product.query.all()
 
    return render_template('new.html', products=products) 

  
 
 

#purchase a item
@app.route('/purchase/<int:product_id>')
def purchase(product_id):
     
    product = Product.query.get(product_id)

    if product:
        # Create a new PurchaseHistory entry
        purchase_entry = PurchaseHistory(user_id=current_user.id, product_id=product.id)
        db.session.add(purchase_entry)
        db.session.commit()

        flash('Purchase successful!', 'success')
    else:
        flash('Product not found', 'error')

    return redirect(url_for('index')) 

   
#user orders history    
@app.route('/dashboard')
def dashboard():
    if current_user.is_authenticated:
         
        purchase_history = PurchaseHistory.query.filter_by(user_id=current_user.id).all()
        return render_template('dashboard.html', purchase_history=purchase_history)
    else:
        flash('Please log in to view your dashboard.', 'info')
        return redirect(url_for('login'))    
     

#index page 
@app.route('/')
def index():
    products =Product.query.all()
    return render_template('index.html', products=products)
 
    

@app.route('/mobiles')
def mobiles():
    products = Product.query.all()
    return render_template('mobiles.html',products=products)
    
@app.route('/furniture')
def furniture():
    products = Product.query.all()
    return render_template('furniture.html',products=products)

@app.route('/fashion')
def fashion():
    products = Product.query.all()
    return render_template('fashion.html',products=products)
    
@app.route('/beauty')
def beauty():
    products = Product.query.all()
    return render_template('beauty.html',products=products)    

@app.route('/electronics')
def electronics():
    products = Product.query.all()
    return render_template('acceries.html',products=products)
    
@app.route('/toys')
def toys():
    products = Product.query.all()
    return render_template('toys.html',products=products)    
    

@app.route('/sports')
def sports():
    products = Product.query.all()
    return render_template('sports.html',products=products)    

#view a cart page
@app.route('/view')
def view():
    total_price = sum(item['quantity'] * item['product'].price for item in cart_items.values())
     
    return render_template('cart.html', cart_items=cart_items, total_price=total_price)   
    
#if click the specific product show, product features
@app.route('/product/<int:product_id>')
def product_details(product_id):
     
    products = Product.query.all()
    product = next((p for p in products if p.id == product_id))
    if product:
        return render_template('product_details.html', product=product)
    else:
        return "Product not found" 

 

#add a products in cart
@app.route('/add_to_cart/<int:product_id>' )
@login_required
def add_to_cart(product_id):
    
    with app.app_context():
        session = db.session
        product = session.get(Product, product_id)
    
    
    #ORIGINAL LINE
    #product = Product.query.get(product_id)
     
    cart = Cart.query.filter_by(user_id=current_user.id).first()
     
    if product:
         
         
        quantity = request.form.get('quantity', type=int, default=1)

         
        existing_item = Cart.query.filter_by(user_id=current_user.id, product_id=product_id ).first()

        if existing_item:
            # If the product is already in the cart, increment the quantity
            existing_item.quantity += quantity
        else:
            total_price = quantity * product.price
            new_item = Cart(
                user_id=current_user.id,
                product_id=product_id,
                quantity=quantity,
                product_name=product.name,
                product_image=product.image,
                product_price=product.price,
                total_price=total_price
            )
            
            
             
            db.session.add(new_item)

        db.session.commit()
        flash("Product added to cart successfully!", "success")
    else:
         
        print(f"Product with id {product_id} not found.")

    return redirect(url_for('cart'))   
    

def get_or_create_cart(user_id):
    cart = Cart.query.filter_by(user_id=user_id).first()

    if cart is None:
        # Create a new cart if none exists
        cart = Cart(user_id=user_id)
        db.session.add(cart)
        db.session.commit()

    return cart
 

#update a quantity in cart 
@app.route('/update_quantity/<int:product_id>', methods=['POST'])
def update_quantity(product_id):
    quantity = request.form.get('quantity_' + str(product_id), type=int, default=1)

     
    cart_item = Cart.query.filter_by(user_id=current_user.id, product_id=product_id).first()

    if cart_item:
         
        cart_item.quantity = quantity
        db.session.commit()
        flash('Quantity updated successfully!', 'success')
    else:
        flash('Cart item not found!', 'error')

    return redirect(url_for('cart'))     

 
#delete a product in cart
@app.route('/delete_product/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
     
    cart_item = Cart.query.filter_by(user_id=current_user.id, product_id=product_id).first()

    if cart_item:
         
        db.session.delete(cart_item)
        db.session.commit()
        flash('Product deleted successfully!', 'success')
    else:
        flash('Cart item not found!', 'error')

    return jsonify({'message': 'Product deleted successfully!'})

 
#cart page
@app.route('/cart')
@login_required
def cart():

    products = Product.query.all()     

    existing_delivery_address = DeliveryAddress.query.filter_by(user_id=current_user.id).first()
     
    cart_items = Cart.query.filter_by(user_id=current_user.id).all()

    total_price = sum(item.quantity * item.product.price for item in cart_items)

    return render_template('cart.html',products = products, existing_delivery_address = existing_delivery_address ,cart_items=cart_items, total_price=total_price)    
    
 
    
def safe_get(dictionary, *keys):
    for key in keys:
        try:
            dictionary = dictionary[key]
        except (TypeError, KeyError):
            return None
    return dictionary

 
 
 

#required to fill a address by user  
@app.route('/delivery_address', methods=['GET', 'POST'])
@login_required
def delivery_address():
    existing_delivery_address = DeliveryAddress.query.filter_by(user_id=current_user.id).first()

    if request.method == 'POST':
        door_no = request.form.get('door_no')
        street_name = request.form.get('street_name')
        area = request.form.get('area')
        landmark = request.form.get('landmark')
        pincode = request.form.get('pincode')
        district = request.form.get('district')
        mobile_number = request.form.get('mobile_number')

        if door_no and street_name and area and pincode and district and mobile_number:
            # If an existing delivery address exists, update it
            if existing_delivery_address:
                existing_delivery_address.door_no = door_no
                existing_delivery_address.street_name = street_name
                existing_delivery_address.area = area
                existing_delivery_address.landmark = landmark
                existing_delivery_address.pincode = pincode
                existing_delivery_address.district = district
                existing_delivery_address.mobile_number = mobile_number
            else:
                # Otherwise, create a new delivery address
                new_address = DeliveryAddress(
                    user_id=current_user.id,
                    door_no=door_no,
                    street_name=street_name,
                    area=area,
                    landmark=landmark,
                    pincode=pincode,
                    district=district,
                    mobile_number=mobile_number
                )
                db.session.add(new_address)

            db.session.commit()
            flash('Delivery address updated successfully!', 'success')
            return redirect(url_for('cart'))  # Redirect to cart after updating the address
        else:
            flash('Please fill in all the required fields.', 'error')

    return render_template('delivery.html', existing_delivery_address=existing_delivery_address)

    

#confirm a order 
@app.route('/place_order', methods=['POST'])
@login_required
def place_order():
     
    existing_delivery_address = DeliveryAddress.query.filter_by(user_id=current_user.id).first()

    if not existing_delivery_address:
        flash('Please provide a delivery address before placing an order.', 'info')
        return redirect(url_for('delivery_address'))

    if request.method == 'POST':
         
        selected_product_ids = request.form.getlist('selected_products')

         
        cart_items = Cart.query.filter_by(user_id=current_user.id).filter(Cart.product_id.in_(selected_product_ids)).all()

        if not cart_items:
            flash('No items selected for order.', 'error')
            return redirect(url_for('cart'))

        selected_items = {}   

        try:
             
            for cart_item in cart_items:
                total_price = cart_item.quantity * cart_item.product.price
                purchase = PurchaseHistory(
                    user_id=current_user.id,
                    product_id=cart_item.product_id,
                    quantity=cart_item.quantity,
                    total_price=total_price,
                    product_name=cart_item.product.name,
                    product_image=cart_item.product.image,
                    product_price=cart_item.product.price,
                    purchase_date=datetime.utcnow()
                )
                db.session.add(purchase)

                 
                selected_items[cart_item.product_id] = {
                    'product': cart_item.product,
                    'quantity': cart_item.quantity,
                    'total_price': total_price
                }

                 
                db.session.delete(cart_item)

             
            db.session.commit()

            

            flash('Order placed successfully!', 'success')
            return render_template('order.html', selected_items=selected_items)

        except Exception as e:
            flash(f'Unable to place order. Error: {str(e)}', 'error')
            db.session.rollback()
            return redirect(url_for('index'))

    return redirect(url_for('cart'))   
    
  
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
