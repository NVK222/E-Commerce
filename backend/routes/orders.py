from decimal import Decimal
from os import getenv
from typing import List
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException
import httpx
from sqlmodel import Session, select
from db.database import get_session
from models.cart import CartItem
from models.order import Order, OrderItem, OrderRead
from models.user import User
from utils.auth_utils import get_current_user

orders_router = APIRouter()
load_dotenv()

PAYPAL_API_BASE_URL = "https://api-m.sandbox.paypal.com"
ACCESS_TOKEN = getenv('PAYPAL_ACCESS_TOKEN')


@orders_router.get('/', response_model = List[OrderRead])
def get_orders(session : Session = Depends(get_session), user : User = Depends(get_current_user)):
    orders = session.exec(select(Order).where(Order.user_id == user.id)).all()
    return [OrderRead.model_validate(order.model_dump) for order in orders]

@orders_router.post('/create-order', response_model = dict)
async def create_paypal_order(session : Session = Depends(get_session), user : User = Depends(get_current_user)):
    if not user:
        raise HTTPException(404, 'Invalid credentials')
    
    cart = session.exec(select(CartItem).where(CartItem.user_id == user.id)).all()

    if not cart:
        raise HTTPException(404, 'Cart is empty')
    
    total_price = Decimal(0)
    purchase_units = []
    for item in cart:
        item_total = item.unit_price * item.quantity
        total_price += item_total
        purchase_units.append({
            'amount' : {
                'currency_code' : 'USD',
                'value' : str(item_total),
                'breakdown' : {
                    'item_total' : {
                        'currency_code' : "USD",
                        'value' : str(item_total)
                    }
                }
            },
            'items' : [
                {
                    'name' : f'Product ID :  {item.product_id}',
                    'quantity' : str(item.quantity),
                    'unit_amount' : {
                        'currency_code' : 'USD',
                        'value' : str(item.unit_price)
                    }
                }
            ],
            'reference_id' : f'product_{item.product_id}_user_{user.id}',
            'description' : f'Item :  {item.product_id}, Quantity :  {item.quantity}'
        })
    
    paypal_order_payload = {
        'intent' : 'CAPTURE',
        'purchase_units' : purchase_units,
        'application_context' : {
            'return_url' : 'http://localhost:8000/order/capture-order',
            'cancel_url' : 'http://localhost:8000/order/cancel-order',
            'brand_name' : 'E Commerce',
            'shipping_preference' : 'NO_SHIPPING'
        }
    }

    headers = {
        'Content-Type' : 'application/json',
        'Authorization' : f'Bearer {ACCESS_TOKEN}'
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f'{PAYPAL_API_BASE_URL}/v2/checkout/orders', json = paypal_order_payload, headers = headers)
            response.raise_for_status()
            paypal_order_response = response.json()

            approve_link = next((link['href'] for link in paypal_order_response['links'] if link['rel'] == 'approve'), None)

            if approve_link:
                pending_order = Order(user_id = user.id, total_price = total_price, paypal_order_id = paypal_order_response['id'], status = 'pending') #type: ignore
                session.add(pending_order)
                session.commit()
                session.refresh(pending_order)

                for item in cart:
                    order_item = OrderItem(order_id = pending_order.id, product_id = item.product_id, quantity = item.quantity) #type: ignore
                    session.add(order_item)
                session.commit()
                return {
                    'paypal_order_id' : paypal_order_response['id'],
                    'approve_url' : approve_link
                }
            else:
                raise HTTPException(500, 'Failed to get paypal approve url')
        except httpx.HTTPStatusError as e:
            session.rollback()
            raise HTTPException(e.response.status_code, f'Paypal API Error :  {e.response.text}')
        except Exception as e:
            session.rollback()
            raise HTTPException(500, f'An Error Occured {str(e)}')

@orders_router.get('/capture-order')
async def capture_paypal_order(token : str, session : Session = Depends(get_session)):
    paypal_order_id = token
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }

    pending_order = session.exec(select(Order).where(Order.paypal_order_id == paypal_order_id)).first()
    if not pending_order:
        raise HTTPException(404, 'Pending order not found or already processed')
    
    if pending_order.status in ['completed', 'cancelled', 'failed']:
        return {
            'message' : f"Order {pending_order.id} is in status : {pending_order.status}"
        }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f'{PAYPAL_API_BASE_URL}/v2/checkout/orders/{paypal_order_id}/capture', headers = headers)
            response.raise_for_status()
            response = response.json()

            if response.get('status') == 'COMPLETED':
                pending_order.status = 'completed'

                user_id = pending_order.user_id
                cart_item = session.exec(select(CartItem).where(CartItem.user_id == user_id)).all()
                for item in cart_item:
                    session.delete(item)
                session.commit()
                return {"message": "Payment successful and order placed!", "order_id": pending_order.id, "paypal_capture_details": response}
            else:
                pending_order.status = 'failed'
                session.commit()
                raise HTTPException(status_code=400, detail=f"PayPal payment not completed: {response.get('status')}")
        except httpx.HTTPStatusError as e:
            if pending_order:
                pending_order.status = 'failed'
                session.commit()
            raise HTTPException(status_code=e.response.status_code, detail=f"PayPal API error during capture: {e.response.text}")
        except Exception as e:
            if pending_order:
                pending_order.status = 'failed'
                session.commit()
            raise HTTPException(status_code=500, detail=f"An error occurred during payment capture: {str(e)}")

@orders_router.get('/cancel-order', response_model = dict)
async def cancel_paypal_order(token : str, session : Session = Depends(get_session)):
    paypal_order_id = token
    pending_order = session.exec(select(Order).where(Order.paypal_order_id == paypal_order_id)).first()

    if pending_order:
        if pending_order.status == 'pending':
            pending_order.status = 'cancelled'
            session.commit()
            return {
                'message' : f"Order {pending_order.id} has been cancelled"
            }
        else:
            return {
                'message' : f"Order {pending_order.id} is already {pending_order.status}"
            }
    else:
        raise HTTPException(404, 'Pending order not found')

@orders_router.get('/{id}', response_model = dict)
def get_order_by_id(id : int, session : Session = Depends(get_session), user : User = Depends(get_current_user)):
    order = session.exec(select(Order).where(Order.id == id, Order.user_id == user.id)).first()
    items = session.exec(select(OrderItem).where(OrderItem.order_id == order.id)).all() # type: ignore
    return {
        'order' : order,
        'items' : items
    }

@orders_router.get('/{id}', response_model = List[OrderRead])
def admin_get_orders(id : int, session : Session = Depends(get_session), user : User = Depends(get_current_user)):
    if not user.isadmin:
        raise HTTPException(400, 'No permission')
    user_ = session.get(User, id)
    if not user_:
        raise HTTPException(404, 'No such user found')
    orders = session.exec(select(Order).where(Order.user_id == user_.id)).all()
    return [OrderRead.model_validate(order.model_dump) for order in orders]
