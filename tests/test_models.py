# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import os
import logging
import unittest
from decimal import Decimal
from service.models import Product, Category, db, DataValidationError
from service import app
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""
    logger = logging.getLogger("test.test_routes.ProductModel")

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(name="Fedora", description="A red hat", price=12.50, available=True, category=Category.CLOTHS)
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    #
    # ADD YOUR TEST CASES HERE
    #
    def test_read_a_product(self):
        """It should read a product and assert that it exists"""
        product = ProductFactory()
        self.logger.info("New product from Factory %s", product)
        product.id = None
        # Creating a product to database
        product.create()
        self.assertTrue(product.id is not None)

        # Fetch the product from database
        found_product = Product.find(product.id)
        self.assertTrue(found_product is not None)
        self.assertEqual(found_product.id, product.id)
        self.assertEqual(found_product.name, product.name)
        self.assertEqual(found_product.description, product.description)
        self.assertEqual(Decimal(found_product.price), product.price)
        self.assertEqual(found_product.available, product.available)
        self.assertEqual(found_product.category, product.category)

    def test_update_a_product(self):
        """It should update a product and assert that it is updated"""
        product = ProductFactory()
        self.logger.info("New product from Factory %s", product)
        product.id = None
        product.create()

        self.logger.info("Product %s created", product)
        self.assertTrue(product.id is not None)

        # Update the product to database
        product.description = "My new description"
        product.update()

        # Fetch all products from the database
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product id but updated description.
        new_product = products[0]
        self.assertEqual(new_product.id, product.id)
        self.assertEqual(new_product.description, "My new description")

    def test_update_a_product_with_no_id(self):
        """It should raise DataValidationError when a product with None id is updated"""
        product = ProductFactory()
        self.logger.info("New product from Factory %s", product)
        product.id = None
        product.create()

        self.logger.info("Product %s created", product)
        self.assertTrue(product.id is not None)

        # Update the product to database
        product.id = None
        self.assertRaises(DataValidationError, product.update)
        # self.assertFalse(db.session.commit.called)

    def test_delete_a_product(self):
        """It should delete a product and assert that it no longer exists"""
        product = ProductFactory()
        self.logger.info("New product from Factory %s", product)
        product.id = None
        product.create()
        self.logger.info("Product %s created", product)
        self.assertTrue(product.id is not None)
        # Fetch all products from the database
        self.assertEqual(len(Product.all()), 1)

        # Delete the product to database
        product.delete()
        self.assertEqual(len(Product.all()), 0)

    def test_fetch_all_product(self):
        """It should fetch all products in the database"""
        products = Product.all()
        self.assertEqual(len(products), 0)

        for _ in range(5):
            product = ProductFactory()
            product.create()
            self.assertTrue(product.id is not None)

        self.assertEqual(len(Product.all()), 5)

    def test_find_a_product_by_name(self):
        """It should Find a Product by Name from the database"""
        products = ProductFactory.create_batch(5)
        for prod in products:
            prod.create()
            self.assertTrue(prod.id is not None)

        products = Product.all()
        self.assertEqual(len(products), 5)
        # Check that it matches the original product
        first_product = products[0]
        self.assertTrue(first_product is not None)
        filtered_objects = [obj for obj in products if obj.name == first_product.name]
        count = len(filtered_objects)

        # Check count of the found products matches the expected count
        found_products = Product.find_by_name(first_product.name)
        self.assertEqual(found_products.count(), count)
        for obj in found_products:
            self.assertEqual(obj.name, first_product.name)

    def test_find_a_product_by_availability(self):
        """It should Find a Product by Availability from the database"""
        products = ProductFactory.create_batch(10)
        for prod in products:
            prod.create()
            self.assertTrue(prod.id is not None)

        products = Product.all()
        self.assertEqual(len(products), 10)
        # Check that it matches the original product
        first_product = products[0]
        self.assertTrue(first_product is not None)
        filtered_objects = [obj for obj in products if obj.available == first_product.available]
        count = len(filtered_objects)

        # Check count of the found products matches the expected count
        found_products = Product.find_by_availability(first_product.available)
        self.assertEqual(found_products.count(), count)
        for obj in found_products:
            self.assertEqual(obj.available, first_product.available)

    def test_find_a_product_by_category(self):
        """It should Find a Product by Category from the database"""
        products = ProductFactory.create_batch(10)
        for prod in products:
            prod.create()
            self.assertTrue(prod.id is not None)

        products = Product.all()
        self.assertEqual(len(products), 10)
        # Check that it matches the original product
        first_product = products[0]
        self.assertTrue(first_product is not None)
        filtered_objects = [obj for obj in products if obj.category == first_product.category]
        count = len(filtered_objects)

        # Check count of the found products matches the expected count
        found_products = Product.find_by_category(first_product.category)
        self.assertEqual(found_products.count(), count)
        for obj in found_products:
            self.assertEqual(obj.category, first_product.category)

    def test_find_by_price(self):
        """It should Find a Product by Price from the database"""
        products = ProductFactory.create_batch(5)
        for prod in products:
            prod.create()
            self.assertTrue(prod.id is not None)

        products = Product.all()
        self.assertEqual(len(products), 5)
        # Check that it matches the original product
        first_product = products[0]
        self.assertTrue(first_product is not None)
        filtered_objects = [obj for obj in products if obj.price == first_product.price]
        count = len(filtered_objects)

        # Check count of the found products matches the expected count
        found_products = Product.find_by_price(first_product.price)
        self.assertEqual(found_products.count(), count)
        for obj in found_products:
            self.assertEqual(obj.price, first_product.price)

    def test_find_by_price_of_type_str(self):
        """It should Find a Product by Price of type str from the database"""
        products = ProductFactory.create_batch(5)
        for prod in products:
            prod.create()
            self.assertTrue(prod.id is not None)

        products = Product.all()
        self.assertEqual(len(products), 5)
        # Check that it matches the original product
        first_product = products[0]
        self.assertTrue(first_product is not None)
        filtered_objects = [obj for obj in products if obj.price == first_product.price]
        count = len(filtered_objects)

        # Check count of the found products matches the expected count
        found_products = Product.find_by_price(str(first_product.price))
        self.assertEqual(found_products.count(), count)
        for obj in found_products:
            self.assertEqual(obj.price, first_product.price)
