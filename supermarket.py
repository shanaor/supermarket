import os
from flask import Flask, jsonify, request, render_template, redirect, url_for
from sqlalchemy import create_engine, Column, Integer, String, Float, Enum
from sqlalchemy.orm import sessionmaker, declarative_base
import enum

# Initialize Flask app
app = Flask(__name__)

# Define the current directory and database file
current_directory = os.path.dirname(os.path.abspath(__file__))  # Current script directory
db_file = os.path.join(current_directory, 'supermarket.db')  # Path to the DB file

# Check if the database file exists
db_exists = os.path.exists(db_file)

# Create an engine and base
engine = create_engine(f'sqlite:///{db_file}', echo=False)
Base = declarative_base()

# Define an ENUM for product categories
class ProductCategory(enum.Enum):
    BEVERAGES = 'Beverages'
    SNACKS = 'Snacks'
    DAIRY = 'Dairy'
    FRUITS = 'Fruits'
    VEGETABLES = 'Vegetables'

# Define an ENUM for product quality
class ProductQuality(enum.Enum):
    LOW = 'Low'
    MEDIUM = 'Medium'
    HIGH = 'High'

# Define the Product model
class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    price = Column(Float, nullable=False)
    quality = Column(Enum(ProductQuality), nullable=False)
    category = Column(Enum(ProductCategory), nullable=False)

# Automatically create the tables if the database doesn't exist
if not db_exists:
    Base.metadata.create_all(engine)
    print(f"Database created at: {db_file}")

# Create a session factory
Session = sessionmaker(bind=engine)
session = Session()

# Route to render the main HTML page for adding products
@app.route('/')
def index():
    return render_template('index.html')

# Route to display all products by category in HTML
@app.route('/products')
def view_products():
    return render_template('products.html')

# Route to create a new product (POST)
@app.route('/products', methods=['POST'])
def create_product():
    data = request.json
    try:
        new_product = Product(
            name=data['name'],
            description=data['description'],
            price=data['price'],
            quality=ProductQuality[data['quality']],
            category=ProductCategory[data['category']]
        )
        session.add(new_product)
        session.commit()
        return jsonify({'message': 'Product created successfully'}), 201
    except KeyError as e:
        return jsonify({'error': f'Invalid field: {str(e)}'}), 400

# Route to read all products by category (GET)
@app.route('/products/category/<string:category>', methods=['GET'])
def read_products_by_category(category):
    try:
        products = session.query(Product).filter_by(category=ProductCategory[category]).all()
        if not products:
            return jsonify({'message': 'No products found in this category'}), 404
        return jsonify([{
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'price': product.price,
            'quality': product.quality.value,
            'category': product.category.value
        } for product in products]), 200
    except KeyError:
        return jsonify({'error': 'Invalid category'}), 400

# Route to update a product (PUT)
@app.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    data = request.json
    product = session.query(Product).filter_by(id=product_id).first()
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    # Update fields if provided
    if 'name' in data:
        product.name = data['name']
    if 'description' in data:
        product.description = data['description']
    if 'price' in data:
        product.price = data['price']
    if 'quality' in data:
        product.quality = ProductQuality[data['quality']]
    if 'category' in data:
        product.category = ProductCategory[data['category']]

    session.commit()
    return jsonify({'message': 'Product updated successfully'}), 200

# Route to delete a product (DELETE)
@app.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    product = session.query(Product).filter_by(id=product_id).first()
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    session.delete(product)
    session.commit()
    return jsonify({'message': 'Product deleted successfully'}), 200

# Route to get a specific product by ID (GET)
@app.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = session.query(Product).filter_by(id=product_id).first()
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    return jsonify({
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'price': product.price,
        'quality': product.quality.value,
        'category': product.category.value
    }), 200

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
