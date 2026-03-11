import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

np.random.seed(42)
random.seed(42)

n_orders = 99441
order_ids = [f"order_{i:06d}" for i in range(n_orders)]
customer_ids = [f"cust_{random.randint(1,90000):06d}" for _ in range(n_orders)]

start_date = datetime(2016, 9, 1)
end_date = datetime(2018, 8, 31)
delta = (end_date - start_date).days
purchase_dates = sorted([
    start_date + timedelta(days=random.randint(0, delta), hours=random.randint(0,23), minutes=random.randint(0,59))
    for _ in range(n_orders)
])

statuses = np.random.choice(
    ['delivered','shipped','canceled','unavailable','invoiced','processing','created','approved'],
    n_orders, p=[0.970, 0.010, 0.006, 0.004, 0.005, 0.002, 0.002, 0.001]
)
orders_df = pd.DataFrame({
    'order_id': order_ids, 'customer_id': customer_ids, 'order_status': statuses,
    'order_purchase_timestamp': purchase_dates,
    'order_approved_at': [d + timedelta(hours=random.uniform(0.1,24)) for d in purchase_dates],
    'order_delivered_carrier_date': [d + timedelta(days=random.uniform(1,5)) for d in purchase_dates],
    'order_delivered_customer_date': [d + timedelta(days=random.uniform(5,20)) for d in purchase_dates],
    'order_estimated_delivery_date': [d + timedelta(days=random.uniform(15,40)) for d in purchase_dates],
})
orders_df.to_csv('olist_orders_dataset.csv', index=False)
print("Orders done")

categories = ['beleza_saude','informatica_acessorios','automotivo','cama_mesa_banho','moveis_decoracao',
              'esporte_lazer','perfumaria','utilidades_domesticas','telefonia','relogios_presentes',
              'ferramentas_jardim','brinquedos','cool_stuff','eletronicos','eletrodomesticos']
product_ids = [f"prod_{i:05d}" for i in range(1000)]
seller_ids = [f"seller_{i:04d}" for i in range(200)]
products_df = pd.DataFrame({
    'product_id': product_ids,
    'product_category_name': np.random.choice(categories, len(product_ids)),
    'product_name_lenght': np.random.randint(20,70,len(product_ids)),
    'product_description_lenght': np.random.randint(100,1000,len(product_ids)),
    'product_photos_qty': np.random.randint(1,6,len(product_ids)),
    'product_weight_g': np.random.randint(50,5000,len(product_ids)),
    'product_length_cm': np.random.randint(10,60,len(product_ids)),
    'product_height_cm': np.random.randint(5,40,len(product_ids)),
    'product_width_cm': np.random.randint(10,50,len(product_ids)),
})
products_df.to_csv('olist_products_dataset.csv', index=False)
print("Products done")

items_data = []
for i, oid in enumerate(order_ids):
    n_items = np.random.choice([1,2,3,4], p=[0.85,0.10,0.03,0.02])
    for j in range(n_items):
        items_data.append({
            'order_id': oid, 'order_item_id': j+1,
            'product_id': random.choice(product_ids),
            'seller_id': random.choice(seller_ids),
            'shipping_limit_date': purchase_dates[i] + timedelta(days=random.uniform(2,7)),
            'price': round(np.random.lognormal(4.0,0.8),2),
            'freight_value': round(np.random.lognormal(2.5,0.5),2),
        })
items_df = pd.DataFrame(items_data)
items_df.to_csv('olist_order_items_dataset.csv', index=False)
print("Items done")

reviews_df = pd.DataFrame({
    'review_id': [f"rev_{i:06d}" for i in range(n_orders)],
    'order_id': order_ids,
    'review_score': np.random.choice([1,2,3,4,5], n_orders, p=[0.05,0.05,0.08,0.19,0.63]),
    'review_creation_date': [d + timedelta(days=random.uniform(10,25)) for d in purchase_dates],
    'review_answer_timestamp': [d + timedelta(days=random.uniform(11,30)) for d in purchase_dates],
})
reviews_df.to_csv('olist_order_reviews_dataset.csv', index=False)
print("Reviews done")

states = ['SP','RJ','MG','RS','PR','SC','BA','GO','ES','PE','CE','MT','MS','PB','AM','RN','AL','PI','MA','DF']
state_w_raw = [42,13,11,5.7,5,3.6,3.5,2,2,1.8,1.5,1.3,1.2,1,0.9,0.8,0.7,0.6,0.5,0.5]
total = sum(state_w_raw)
state_w = [w/total for w in state_w_raw]
unique_customers = list(set(customer_ids))
customers_df = pd.DataFrame({
    'customer_id': unique_customers,
    'customer_unique_id': [f"ucust_{i:06d}" for i in range(len(unique_customers))],
    'customer_zip_code_prefix': np.random.randint(10000,99999,len(unique_customers)),
    'customer_city': np.random.choice(['sao paulo','rio de janeiro','belo horizonte','brasilia','curitiba'], len(unique_customers)),
    'customer_state': np.random.choice(states, len(unique_customers), p=state_w),
})
customers_df.to_csv('olist_customers_dataset.csv', index=False)
print("Customers done")

inst_w_raw = [35,15,10,8,6,5,5,4,4,3,3,2]
inst_total = sum(inst_w_raw)
inst_w = [w/inst_total for w in inst_w_raw]
payments_data = []
for oid in order_ids:
    payments_data.append({
        'order_id': oid, 'payment_sequential': 1,
        'payment_type': np.random.choice(['credit_card','boleto','voucher','debit_card'], p=[0.74,0.19,0.05,0.02]),
        'payment_installments': np.random.choice(range(1,13), p=inst_w),
        'payment_value': round(np.random.lognormal(4.5,0.7),2),
    })
payments_df = pd.DataFrame(payments_data)
payments_df.to_csv('olist_order_payments_dataset.csv', index=False)
print("Payments done")

print("\nAll datasets created!")
for f in ['olist_orders_dataset.csv','olist_order_items_dataset.csv','olist_products_dataset.csv',
          'olist_order_reviews_dataset.csv','olist_customers_dataset.csv','olist_order_payments_dataset.csv']:
    df = pd.read_csv(f)
    print(f"  {f}: {df.shape}")
