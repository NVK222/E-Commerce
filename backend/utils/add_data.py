from sqlmodel import Session
from db.database import create_db,engine
from models.cart import CartItem
from models.products import Product
from models.user import User
from utils.auth_utils import get_password_hash


def seed():
    with Session(engine) as session:
        user1 = User(username = 'a', email = 'a@gmail.com', password = get_password_hash('1234'))
        user2 = User(username = 'b', email = 'b@gmail.com', password = get_password_hash('9876'))
        product1 = Product(name = 'Mango', description = 'A Mango', price = 20) # type: ignore
        product2 = Product(name = 'Banana', description = 'A Banana', price = 15)# type: ignore
        product3 = Product(name = 'Pencil', description = 'A Pencil', price = 1)# type: ignore
        session.add_all([user1, user2, product1, product2, product3])
        session.commit()
        cart1 = CartItem(user_id = 1, product_id = 1, quantity = 10, unit_price = 20)
        cart2 = CartItem(user_id = 1, product_id = 2, quantity = 20, unit_price = 15)
        cart3 = CartItem(user_id = 2, product_id = 2, quantity = 50, unit_price = 15)
        cart4 = CartItem(user_id = 2, product_id = 3, quantity = 30, unit_price = 1)
        session.add_all([cart1, cart2, cart3, cart4])
        session.commit()
        print('Seeding complete')

if __name__ == '__main__':
    create_db()
    seed()