import csv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///e-vendors.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(255), nullable=True)
    specifications = db.Column(db.String(255), nullable=True)
    features = db.Column(db.String(255), nullable=True)
    warranty = db.Column(db.String(255), nullable=True)

def create_products_from_csv(filename='items.csv'):
    try:
        with app.app_context():
            db.create_all()
            
            with open(filename, 'r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    product = Product(**row)
                    db.session.add(product)
                db.session.commit()
                
            print("Products added successfully.")
    except Exception as e:
        print(f"Error adding products: {e}")

if __name__ == '__main__':
    # Create products from CSV file
    create_products_from_csv()
