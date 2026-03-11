import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import streamlit as st
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Brazilian E-Commerce Dashboard",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem; border-radius: 10px; color: white;
        text-align: center; margin-bottom: 0.5rem;
    }
    .metric-value { font-size: 2rem; font-weight: bold; }
    .metric-label { font-size: 0.85rem; opacity: 0.9; }
    .section-header { color: #2c3e50; border-bottom: 3px solid #3498db;
        padding-bottom: 0.3rem; margin: 1.5rem 0 1rem 0; }
</style>
""", unsafe_allow_html=True)

# ─── Load Data ───────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    orders = pd.read_csv("main_data.csv", parse_dates=[
        'order_purchase_timestamp','order_approved_at',
        'order_delivered_carrier_date','order_delivered_customer_date',
        'order_estimated_delivery_date'
    ])
    return orders

@st.cache_data
def load_supporting():
    items    = pd.read_csv("items_data.csv", parse_dates=['shipping_limit_date'])
    products = pd.read_csv("products_data.csv")
    reviews  = pd.read_csv("reviews_data.csv", parse_dates=['review_creation_date','review_answer_timestamp'])
    payments = pd.read_csv("payments_data.csv")
    customers= pd.read_csv("customers_data.csv")
    return items, products, reviews, payments, customers

try:
    orders_df = load_data()
    items_df, products_df, reviews_df, payments_df, customers_df = load_supporting()
    data_loaded = True
except Exception as e:
    data_loaded = False
    st.error(f"⚠️ Error memuat data: {e}")
    st.info("Pastikan file CSV ada di folder `dashboard/`")
    st.stop()

# ─── Feature Engineering ────────────────────────────────────────────────────
orders_df['year']       = orders_df['order_purchase_timestamp'].dt.year
orders_df['month']      = orders_df['order_purchase_timestamp'].dt.month
orders_df['year_month'] = orders_df['order_purchase_timestamp'].dt.to_period('M')
orders_df['delivery_days'] = (
    orders_df['order_delivered_customer_date'] - orders_df['order_purchase_timestamp']
).dt.days
orders_df['is_late'] = (
    orders_df['order_delivered_customer_date'] > orders_df['order_estimated_delivery_date']
)

full_df = (
    orders_df
    .merge(items_df, on='order_id', how='inner')
    .merge(products_df[['product_id','product_category_name']], on='product_id', how='left')
    .merge(customers_df, on='customer_id', how='left')
)
full_df['total_value'] = full_df['price'] + full_df['freight_value']

# ─── Sidebar ────────────────────────────────────────────────────────────────
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/Flag_of_Brazil.svg/320px-Flag_of_Brazil.svg.png", width=120)
st.sidebar.title("🛒 E-Commerce Dashboard")
st.sidebar.markdown("**Brazilian E-Commerce (Olist)**")
st.sidebar.markdown("---")

# Date filter
min_date = orders_df['order_purchase_timestamp'].min().date()
max_date = orders_df['order_purchase_timestamp'].max().date()

st.sidebar.subheader("📅 Filter Periode")
date_start = st.sidebar.date_input("Dari tanggal", min_date, min_value=min_date, max_value=max_date)
date_end   = st.sidebar.date_input("Sampai tanggal", max_date, min_value=min_date, max_value=max_date)

# Status filter
st.sidebar.subheader("📦 Status Order")
status_opts = ['Semua'] + sorted(orders_df['order_status'].unique().tolist())
selected_status = st.sidebar.selectbox("Pilih Status", status_opts)

# State filter
st.sidebar.subheader("🗺️ Wilayah")
state_opts = ['Semua'] + sorted(customers_df['customer_state'].unique().tolist())
selected_state = st.sidebar.selectbox("Pilih State", state_opts)


# ─── Apply Filters ──────────────────────────────────────────────────────────
mask_orders = (
    (orders_df['order_purchase_timestamp'].dt.date >= date_start) &
    (orders_df['order_purchase_timestamp'].dt.date <= date_end)
)
if selected_status != 'Semua':
    mask_orders &= (orders_df['order_status'] == selected_status)

filtered_orders = orders_df[mask_orders]

mask_full = (
    (full_df['order_purchase_timestamp'].dt.date >= date_start) &
    (full_df['order_purchase_timestamp'].dt.date <= date_end)
)
if selected_status != 'Semua':
    mask_full &= (full_df['order_status'] == selected_status)
if selected_state != 'Semua':
    mask_full &= (full_df['customer_state'] == selected_state)

filtered_full = full_df[mask_full]

# Payments filtered
filtered_payments = payments_df[payments_df['order_id'].isin(filtered_orders['order_id'])]
filtered_reviews  = reviews_df[reviews_df['order_id'].isin(filtered_orders['order_id'])]

# ─── Header ─────────────────────────────────────────────────────────────────
st.title("🛒 Brazilian E-Commerce Analytics Dashboard")
st.caption(f"Periode: {date_start} s/d {date_end} | Status: {selected_status} | State: {selected_state}")
st.markdown("---")

# ─── KPI Metrics ────────────────────────────────────────────────────────────
delivered = filtered_orders[filtered_orders['order_status'] == 'delivered']
total_revenue = filtered_full[filtered_full['order_status'] == 'delivered']['total_value'].sum()
avg_review    = filtered_reviews['review_score'].mean() if len(filtered_reviews) > 0 else 0
late_pct      = filtered_orders['is_late'].mean() * 100 if len(filtered_orders) > 0 else 0

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("📦 Total Order", f"{len(filtered_orders):,}", help="Total order dalam periode yang dipilih")
with col2:
    st.metric("💰 Total Revenue", f"R$ {total_revenue/1e6:.2f}M", help="Revenue dari order delivered")
with col3:
    st.metric("⭐ Avg Review Score", f"{avg_review:.2f}/5.0", help="Rata-rata skor ulasan pelanggan")
with col4:
    st.metric("🚚 Keterlambatan", f"{late_pct:.1f}%", help="Persentase order yang terlambat")

st.markdown("---")

# ─── Section 1: Tren Penjualan ──────────────────────────────────────────────
st.markdown('<h3 class="section-header">📈 Tren Penjualan Bulanan</h3>', unsafe_allow_html=True)

delivered_full = filtered_full[filtered_full['order_status'] == 'delivered'].copy()
if len(delivered_full) > 0:
    monthly = delivered_full.groupby('year_month').agg(
        revenue=('total_value', 'sum'),
        orders=('order_id', 'nunique')
    ).reset_index()
    monthly['ym_str'] = monthly['year_month'].astype(str)
    monthly = monthly.sort_values('year_month')

    tab1, tab2 = st.tabs(["💰 Revenue", "📦 Jumlah Order"])

    with tab1:
        fig, ax = plt.subplots(figsize=(13, 4))
        x = range(len(monthly))
        ax.bar(x, monthly['revenue'], color='#3498db', alpha=0.7, edgecolor='white')
        ax.plot(x, monthly['revenue'], 'o-', color='#e74c3c', lw=2, ms=4, zorder=5)
        ax.set_xticks(x)
        ax.set_xticklabels(monthly['ym_str'], rotation=45, ha='right', fontsize=8)
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'R${v/1e6:.1f}M'))
        ax.set_ylabel('Revenue (R$)')
        ax.set_title('Total Revenue Bulanan', fontweight='bold')
        ax.grid(axis='y', alpha=0.3)
        sns.despine(ax=ax)
        st.pyplot(fig, use_container_width=True)
        plt.close()

        if len(monthly) > 0:
            top_month = monthly.loc[monthly['revenue'].idxmax()]
            st.info(f"📌 **Puncak Revenue:** {top_month['ym_str']} dengan R$ {top_month['revenue']/1e6:.2f}M")

    with tab2:
        fig, ax = plt.subplots(figsize=(13, 4))
        ax.bar(x, monthly['orders'], color='#2ecc71', alpha=0.7, edgecolor='white')
        ax.plot(x, monthly['orders'], 's-', color='#e67e22', lw=2, ms=4, zorder=5)
        ax.set_xticks(x)
        ax.set_xticklabels(monthly['ym_str'], rotation=45, ha='right', fontsize=8)
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'{int(v):,}'))
        ax.set_ylabel('Jumlah Order')
        ax.set_title('Jumlah Order Bulanan', fontweight='bold')
        ax.grid(axis='y', alpha=0.3)
        sns.despine(ax=ax)
        st.pyplot(fig, use_container_width=True)
        plt.close()
else:
    st.warning("Tidak ada data delivered untuk filter yang dipilih.")

# ─── Section 2: Kategori Produk ─────────────────────────────────────────────
st.markdown('<h3 class="section-header">📦 Analisis Kategori Produk</h3>', unsafe_allow_html=True)

if len(delivered_full) > 0:
    cat_df = delivered_full.groupby('product_category_name').agg(
        revenue=('total_value', 'sum'),
        items=('order_item_id', 'count'),
        avg_price=('price', 'mean')
    ).reset_index().dropna().sort_values('revenue', ascending=False)

    n_top = st.slider("Tampilkan Top N Kategori", 5, 15, 10)
    top_cat = cat_df.head(n_top)

    col_a, col_b = st.columns(2)

    with col_a:
        fig, ax = plt.subplots(figsize=(7, 5))
        colors = sns.color_palette('Set2', len(top_cat))
        ax.barh(top_cat['product_category_name'][::-1], top_cat['revenue'][::-1], color=colors[::-1])
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'R${v/1e6:.1f}M'))
        ax.set_title(f'Top {n_top} Kategori — Revenue', fontweight='bold')
        ax.set_xlabel('Revenue (R$)')
        ax.grid(axis='x', alpha=0.3)
        sns.despine(ax=ax)
        st.pyplot(fig, use_container_width=True)
        plt.close()

    with col_b:
        top_items = cat_df.nlargest(n_top, 'items')
        fig, ax = plt.subplots(figsize=(7, 5))
        ax.barh(top_items['product_category_name'][::-1], top_items['items'][::-1],
                color=sns.color_palette('Paired', len(top_items))[::-1])
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'{int(v):,}'))
        ax.set_title(f'Top {n_top} Kategori — Volume', fontweight='bold')
        ax.set_xlabel('Jumlah Item Terjual')
        ax.grid(axis='x', alpha=0.3)
        sns.despine(ax=ax)
        st.pyplot(fig, use_container_width=True)
        plt.close()

# ─── Section 3: Ulasan Pelanggan ────────────────────────────────────────────
st.markdown('<h3 class="section-header">⭐ Analisis Ulasan Pelanggan</h3>', unsafe_allow_html=True)

col_c, col_d = st.columns(2)

with col_c:
    if len(filtered_reviews) > 0:
        score_counts = filtered_reviews['review_score'].value_counts().sort_index()
        fig, ax = plt.subplots(figsize=(6, 5))
        colors_r = ['#e74c3c','#e67e22','#f1c40f','#2ecc71','#27ae60']
        ax.pie(score_counts, labels=[f'⭐ {i}' for i in score_counts.index],
               autopct='%1.1f%%', colors=colors_r, startangle=90,
               wedgeprops={'edgecolor': 'white', 'linewidth': 2})
        ax.set_title(f'Distribusi Skor Ulasan\n(Avg: {filtered_reviews["review_score"].mean():.2f}/5.0)', fontweight='bold')
        st.pyplot(fig, use_container_width=True)
        plt.close()
    else:
        st.warning("Tidak ada data ulasan.")

with col_d:
    if len(filtered_orders) > 0:
        orders_rev = filtered_orders.merge(
            filtered_reviews[['order_id','review_score']], on='order_id', how='inner'
        )
        orders_rev = orders_rev[orders_rev['order_status'] == 'delivered']
        if len(orders_rev) > 0:
            late_rev = orders_rev.groupby(['is_late','review_score']).size().unstack(fill_value=0)
            late_pct_df = late_rev.div(late_rev.sum(axis=1), axis=0) * 100
            late_pct_df.index = ['Tepat Waktu', 'Terlambat']
            late_pct_df.columns = [f'⭐ {i}' for i in late_pct_df.columns]
            fig, ax = plt.subplots(figsize=(6, 5))
            late_pct_df.plot(kind='bar', ax=ax, color=colors_r, edgecolor='white')
            ax.set_title('Skor Ulasan vs Status Pengiriman', fontweight='bold')
            ax.set_ylabel('Persentase (%)')
            ax.set_xlabel('')
            ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
            ax.legend(title='Skor', bbox_to_anchor=(1.02,1), loc='upper left', fontsize=9)
            ax.grid(axis='y', alpha=0.3)
            sns.despine(ax=ax)
            st.pyplot(fig, use_container_width=True)
            plt.close()

# ─── Section 4: Pembayaran ──────────────────────────────────────────────────
st.markdown('<h3 class="section-header">💳 Analisis Metode Pembayaran</h3>', unsafe_allow_html=True)

col_e, col_f = st.columns(2)

with col_e:
    if len(filtered_payments) > 0:
        pay_agg = filtered_payments.groupby('payment_type').agg(
            count=('order_id','count'), total=('payment_value','sum')
        ).reset_index().sort_values('count', ascending=False)
        pay_agg['pct'] = pay_agg['count'] / pay_agg['count'].sum() * 100
        pay_colors = ['#3498db','#e74c3c','#2ecc71','#f39c12']
        labels = [f"{r['payment_type'].replace('_',' ').title()}\n({r['pct']:.1f}%)" for _, r in pay_agg.iterrows()]
        fig, ax = plt.subplots(figsize=(6, 5))
        ax.pie(pay_agg['count'], labels=labels, colors=pay_colors[:len(pay_agg)],
               startangle=90, wedgeprops={'edgecolor':'white','linewidth':2}, shadow=True)
        ax.set_title('Distribusi Metode Pembayaran', fontweight='bold')
        st.pyplot(fig, use_container_width=True)
        plt.close()

with col_f:
    if len(filtered_payments) > 0:
        cc = filtered_payments[filtered_payments['payment_type'] == 'credit_card']
        inst = cc['payment_installments'].value_counts().sort_index().head(12)
        fig, ax = plt.subplots(figsize=(6, 5))
        bars = ax.bar(inst.index, inst.values,
                      color=sns.color_palette('Blues_d', len(inst)), edgecolor='white')
        ax.set_title('Distribusi Cicilan Kartu Kredit', fontweight='bold')
        ax.set_xlabel('Jumlah Cicilan')
        ax.set_ylabel('Jumlah Transaksi')
        ax.set_xticks(inst.index)
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'{int(v):,}'))
        ax.grid(axis='y', alpha=0.3)
        sns.despine(ax=ax)
        st.pyplot(fig, use_container_width=True)
        plt.close()

# ─── Footer ─────────────────────────────────────────────────────────────────
st.markdown("---")
