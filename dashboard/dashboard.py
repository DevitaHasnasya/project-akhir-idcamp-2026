import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from scipy.stats import skew
import streamlit as st
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="E-Commerce Dashboard", page_icon="🛒", layout="wide")

st.markdown("""
<style>
    [data-testid="stMetric"] { background:#f0f4ff; border-radius:10px; padding:12px; }
    .section-title { font-size:1.2rem; font-weight:700; color:#1a237e;
        border-left:5px solid #3498db; padding-left:10px; margin:1.2rem 0 0.8rem 0; }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_all():
    orders    = pd.read_csv("main_data.csv")
    items     = pd.read_csv("items_data.csv")
    products  = pd.read_csv("products_data.csv")
    reviews   = pd.read_csv("reviews_data.csv")
    payments  = pd.read_csv("payments_data.csv")
    customers = pd.read_csv("customers_data.csv")

    for col in ['order_purchase_timestamp','order_approved_at',
                'order_delivered_carrier_date','order_delivered_customer_date',
                'order_estimated_delivery_date']:
        orders[col] = pd.to_datetime(orders[col])

    orders['year_month']    = orders['order_purchase_timestamp'].dt.to_period('M')
    orders['delivery_days'] = (orders['order_delivered_customer_date'] -
                                orders['order_purchase_timestamp']).dt.days
    orders['is_late']       = (orders['order_delivered_customer_date'] >
                                orders['order_estimated_delivery_date'])

    full = (orders
        .merge(items, on='order_id', how='inner')
        .merge(products[['product_id','product_category_name']], on='product_id', how='left')
        .merge(customers, on='customer_id', how='left'))
    full['total_value'] = full['price'] + full['freight_value']

    return orders, items, products, reviews, payments, customers, full


try:
    orders_df, items_df, products_df, reviews_df, payments_df, customers_df, full_df = load_all()
except Exception as e:
    st.error(f"Gagal memuat data: {e}")
    st.stop()

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🛒 E-Commerce Dashboard")
    st.caption("Brazilian E-Commerce (Olist) | 2016–2018")
    st.markdown("---")

    st.subheader("📅 Filter Periode")
    min_d = orders_df['order_purchase_timestamp'].min().date()
    max_d = orders_df['order_purchase_timestamp'].max().date()
    d_start = st.date_input("Dari", min_d, min_value=min_d, max_value=max_d)
    d_end   = st.date_input("Sampai", max_d, min_value=min_d, max_value=max_d)

    st.subheader("📦 Status Order")
    status_opts = ['Semua'] + sorted(orders_df['order_status'].unique().tolist())
    sel_status  = st.selectbox("Status", status_opts)

    st.subheader("🗺️ State Pelanggan")
    state_opts = ['Semua'] + sorted(customers_df['customer_state'].unique().tolist())
    sel_state  = st.selectbox("State", state_opts)

    st.subheader("📊 Analisis EDA")
    show_eda = st.checkbox("Tampilkan EDA Detail", value=False)

    st.markdown("---")
    st.caption("Proyek Akhir — Dicoding\nBelajar Analisis Data dengan Python")

# ── Filter ───────────────────────────────────────────────────────────────────
m_ord = ((orders_df['order_purchase_timestamp'].dt.date >= d_start) &
         (orders_df['order_purchase_timestamp'].dt.date <= d_end))
if sel_status != 'Semua':
    m_ord &= (orders_df['order_status'] == sel_status)

f_orders   = orders_df[m_ord]
f_payments = payments_df[payments_df['order_id'].isin(f_orders['order_id'])]
f_reviews  = reviews_df[reviews_df['order_id'].isin(f_orders['order_id'])]

m_full = ((full_df['order_purchase_timestamp'].dt.date >= d_start) &
          (full_df['order_purchase_timestamp'].dt.date <= d_end))
if sel_status != 'Semua':
    m_full &= (full_df['order_status'] == sel_status)
if sel_state != 'Semua':
    m_full &= (full_df['customer_state'] == sel_state)

f_full     = full_df[m_full]
f_deliv    = f_full[f_full['order_status'] == 'delivered']

# ── Header ───────────────────────────────────────────────────────────────────
st.title("🛒 Brazilian E-Commerce Analytics Dashboard")
st.caption(f"Periode: {d_start} s/d {d_end}  |  Status: {sel_status}  |  State: {sel_state}")
st.markdown("---")

# ── KPI ──────────────────────────────────────────────────────────────────────
total_rev   = f_deliv['total_value'].sum()
avg_rev_sc  = f_reviews['review_score'].mean() if len(f_reviews) > 0 else 0
late_pct    = f_orders['is_late'].mean() * 100 if len(f_orders) > 0 else 0
avg_deliv   = f_orders['delivery_days'].mean() if len(f_orders) > 0 else 0

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("📦 Total Order",      f"{len(f_orders):,}")
c2.metric("💰 Revenue",          f"R${total_rev/1e6:.2f}M")
c3.metric("⭐ Avg Review",       f"{avg_rev_sc:.2f}/5.0")
c4.metric("🚚 Keterlambatan",    f"{late_pct:.1f}%")
c5.metric("⏱ Rata-rata Kirim",  f"{avg_deliv:.1f} hari")

st.markdown("---")

# ════════════════════════════════════════════════════════════════════════════
# PERTANYAAN 1: TREN PENJUALAN
# ════════════════════════════════════════════════════════════════════════════
st.markdown('<p class="section-title">📈 Pertanyaan 1: Tren Penjualan Bulanan (Sep 2016 – Ags 2018)</p>', unsafe_allow_html=True)

if len(f_deliv) > 0:
    monthly = (f_deliv.groupby('year_month')
               .agg(revenue=('total_value','sum'), orders=('order_id','nunique'))
               .reset_index())
    monthly['ym_str'] = monthly['year_month'].astype(str)
    monthly = monthly.sort_values('year_month')

    tab1, tab2 = st.tabs(["💰 Revenue Bulanan", "📦 Jumlah Order"])
    x = range(len(monthly))

    with tab1:
        fig, ax = plt.subplots(figsize=(13, 4))
        ax.bar(x, monthly['revenue'], color='#3498db', alpha=0.7, edgecolor='white')
        ax.plot(x, monthly['revenue'], 'o-', color='#e74c3c', lw=2, ms=4, zorder=5)
        if len(monthly) > 0:
            mi = monthly['revenue'].idxmax()
            ax.bar(mi, monthly.loc[mi,'revenue'], color='#e74c3c',
                   label=f"Puncak: {monthly.loc[mi,'ym_str']}")
            ax.legend()
        ax.set_xticks(x); ax.set_xticklabels(monthly['ym_str'], rotation=45, ha='right', fontsize=8)
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f'R${v/1e6:.1f}M'))
        ax.set_ylabel('Revenue (R$)'); ax.set_title('Total Revenue Bulanan', fontweight='bold')
        ax.grid(axis='y', alpha=0.3); sns.despine(ax=ax)
        st.pyplot(fig, use_container_width=True); plt.close()

    with tab2:
        fig, ax = plt.subplots(figsize=(13, 4))
        ax.bar(x, monthly['orders'], color='#2ecc71', alpha=0.7, edgecolor='white')
        ax.plot(x, monthly['orders'], 's-', color='#e67e22', lw=2, ms=4, zorder=5)
        ax.set_xticks(x); ax.set_xticklabels(monthly['ym_str'], rotation=45, ha='right', fontsize=8)
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f'{int(v):,}'))
        ax.set_ylabel('Jumlah Order'); ax.set_title('Jumlah Order Bulanan', fontweight='bold')
        ax.grid(axis='y', alpha=0.3); sns.despine(ax=ax)
        st.pyplot(fig, use_container_width=True); plt.close()

    st.info("💡 **Insight:** Platform mengalami pertumbuhan konsisten 2016–2018. Puncak penjualan terjadi November 2017 (Black Friday). Pola Q4 meningkat setiap tahun.")
else:
    st.warning("Tidak ada data untuk filter yang dipilih.")

st.markdown('<p class="section-title">📦 Pertanyaan 2: Kategori Produk Terlaris (2016–2018)</p>', unsafe_allow_html=True)

if len(f_deliv) > 0:
    cat_df = (f_deliv.groupby('product_category_name')
              .agg(revenue=('total_value','sum'), items=('order_item_id','count'))
              .reset_index().dropna().sort_values('revenue', ascending=False))

    n_top = st.slider("Tampilkan Top N Kategori", 5, 15, 10, key='cat_slider')
    col_a, col_b = st.columns(2)

    with col_a:
        t = cat_df.head(n_top)
        fig, ax = plt.subplots(figsize=(7, 5))
        ax.barh(t['product_category_name'][::-1], t['revenue'][::-1],
                color=sns.color_palette('Set2', n_top)[::-1])
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f'R${v/1e6:.1f}M'))
        ax.set_title(f'Top {n_top} — Revenue', fontweight='bold')
        ax.grid(axis='x', alpha=0.3); sns.despine(ax=ax)
        st.pyplot(fig, use_container_width=True); plt.close()

    with col_b:
        t2 = cat_df.nlargest(n_top,'items')
        fig, ax = plt.subplots(figsize=(7, 5))
        ax.barh(t2['product_category_name'][::-1], t2['items'][::-1],
                color=sns.color_palette('Paired', n_top)[::-1])
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f'{int(v):,}'))
        ax.set_title(f'Top {n_top} — Volume', fontweight='bold')
        ax.grid(axis='x', alpha=0.3); sns.despine(ax=ax)
        st.pyplot(fig, use_container_width=True); plt.close()

    st.info("💡 **Insight:** beleza_saude dan informatica_acessorios mendominasi revenue dan volume. Kedua kategori ini menjadi prioritas strategi bisnis.")

st.markdown('<p class="section-title">⭐ Pertanyaan 3: Ulasan Pelanggan & Ketepatan Pengiriman (2016–2018)</p>', unsafe_allow_html=True)

colors_r = ['#e74c3c','#e67e22','#f1c40f','#2ecc71','#27ae60']
orv = f_orders.merge(f_reviews[['order_id','review_score']], on='order_id', how='inner')
orv = orv[orv['order_status'] == 'delivered']

col_c, col_d = st.columns(2)

with col_c:
    if len(orv) > 0:
        sc = orv['review_score'].value_counts().sort_index()
        fig, ax = plt.subplots(figsize=(6, 5))
        ax.pie(sc, labels=[f'⭐ {i}' for i in sc.index], autopct='%1.1f%%',
               colors=colors_r, startangle=90, wedgeprops={'edgecolor':'white','linewidth':2})
        ax.set_title(f'Distribusi Skor Ulasan\n(Avg: {orv["review_score"].mean():.2f}/5.0)', fontweight='bold')
        st.pyplot(fig, use_container_width=True); plt.close()

with col_d:
    if len(orv) > 0:
        lr = orv.groupby(['is_late','review_score']).size().unstack(fill_value=0)
        lp = lr.div(lr.sum(axis=1), axis=0) * 100
        lp.index = ['Tepat Waktu','Terlambat']
        lp.columns = [f'⭐ {i}' for i in lp.columns]
        fig, ax = plt.subplots(figsize=(6, 5))
        lp.plot(kind='bar', ax=ax, color=colors_r, edgecolor='white')
        ax.set_title('Skor vs Status Pengiriman', fontweight='bold')
        ax.set_ylabel('Persentase (%)'); ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
        ax.legend(title='Skor', bbox_to_anchor=(1.02,1), fontsize=9)
        ax.grid(axis='y', alpha=0.3); sns.despine(ax=ax)
        st.pyplot(fig, use_container_width=True); plt.close()

st.info("💡 **Insight:** 63% pelanggan memberi skor 5★ (avg 4.09/5.0). Keterlambatan pengiriman terbukti menurunkan kepuasan secara signifikan.")

st.markdown('<p class="section-title">💳 Pertanyaan 4: Metode Pembayaran (2016–2018)</p>', unsafe_allow_html=True)

col_e, col_f = st.columns(2)

with col_e:
    if len(f_payments) > 0:
        pa = (f_payments.groupby('payment_type').agg(count=('order_id','count'))
              .reset_index().sort_values('count', ascending=False))
        pa['pct'] = pa['count'] / pa['count'].sum() * 100
        pay_colors = ['#3498db','#e74c3c','#2ecc71','#f39c12']
        labels = [f"{r['payment_type'].replace('_',' ').title()}\n({r['pct']:.1f}%)" for _,r in pa.iterrows()]
        fig, ax = plt.subplots(figsize=(6, 5))
        ax.pie(pa['count'], labels=labels, colors=pay_colors[:len(pa)],
               startangle=90, wedgeprops={'edgecolor':'white','linewidth':2}, shadow=True)
        ax.set_title('Distribusi Metode Pembayaran', fontweight='bold')
        st.pyplot(fig, use_container_width=True); plt.close()

with col_f:
    if len(f_payments) > 0:
        cc   = f_payments[f_payments['payment_type'] == 'credit_card']
        inst = cc['payment_installments'].value_counts().sort_index().head(12)
        fig, ax = plt.subplots(figsize=(6, 5))
        ax.bar(inst.index, inst.values, color=sns.color_palette('Blues_d', len(inst)), edgecolor='white')
        ax.set_title('Distribusi Cicilan Kartu Kredit', fontweight='bold')
        ax.set_xlabel('Jumlah Cicilan'); ax.set_ylabel('Jumlah Transaksi')
        ax.set_xticks(inst.index)
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f'{int(v):,}'))
        ax.grid(axis='y', alpha=0.3); sns.despine(ax=ax)
        st.pyplot(fig, use_container_width=True); plt.close()

st.info("💡 **Insight:** Kartu kredit mendominasi (74%). Mayoritas pelanggan memilih 1x cicilan (tanpa cicilan).")

if show_eda:
    st.markdown("---")
    st.markdown('<p class="section-title">🔍 EDA Detail — Distribusi & Korelasi</p>', unsafe_allow_html=True)

    tab_uni, tab_corr, tab_box = st.tabs(["Histogram & KDE", "Korelasi", "Box & Violin"])

    with tab_uni:
        num_vars = {'price': items_df['price'], 'freight_value': items_df['freight_value'],
                    'delivery_days': orders_df['delivery_days'].dropna(),
                    'payment_value': payments_df['payment_value']}
        fig, axes = plt.subplots(2, 4, figsize=(16, 7))
        fig.suptitle('Histogram & KDE Variabel Numerik', fontweight='bold')
        for i, (name, data) in enumerate(num_vars.items()):
            dv = data[data <= data.quantile(0.99)].dropna()
            c = sns.color_palette('Set2')[i]
            axes[0,i].hist(dv, bins=35, color=c, edgecolor='white', alpha=0.8)
            axes[0,i].set_title(f'Histogram: {name}', fontsize=9, fontweight='bold')
            axes[0,i].grid(axis='y', alpha=0.3)
            sns.kdeplot(dv, ax=axes[1,i], fill=True, color=c)
            axes[1,i].set_title(f'KDE: {name}', fontsize=9, fontweight='bold')
            axes[1,i].grid(axis='y', alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig, use_container_width=True); plt.close()

    with tab_corr:
        corr_df = f_deliv.merge(reviews_df[['order_id','review_score']], on='order_id', how='left')\
                         [['price','freight_value','total_value','delivery_days','review_score']].dropna()
        if len(corr_df) > 10:
            fig, axes = plt.subplots(1, 2, figsize=(14, 5))
            sns.heatmap(corr_df.corr(), annot=True, fmt='.2f', cmap='coolwarm',
                        ax=axes[0], vmin=-1, vmax=1, linewidths=0.5, square=True,
                        mask=np.triu(np.ones_like(corr_df.corr(), dtype=bool)))
            axes[0].set_title('Correlation Matrix', fontweight='bold')

            samp = corr_df.sample(min(2000, len(corr_df)), random_state=42)
            axes[1].scatter(samp['delivery_days'], samp['review_score'], alpha=0.1, s=8, color='#3498db')
            m, b = np.polyfit(samp['delivery_days'], samp['review_score'], 1)
            xl = np.linspace(samp['delivery_days'].min(), samp['delivery_days'].max(), 100)
            axes[1].plot(xl, m*xl+b, 'r-', lw=2, label=f'slope={m:.3f}')
            axes[1].set_title('Delivery Days vs Review Score', fontweight='bold')
            axes[1].set_xlabel('Hari Kirim'); axes[1].set_ylabel('Skor')
            axes[1].legend(); axes[1].grid(alpha=0.3)
            plt.tight_layout()
            st.pyplot(fig, use_container_width=True); plt.close()

    with tab_box:
        top8 = (f_deliv.groupby('product_category_name')['total_value']
                .sum().nlargest(8).index.tolist())
        cd = f_deliv[f_deliv['product_category_name'].isin(top8)]
        if len(cd) > 0:
            fig, ax = plt.subplots(figsize=(12, 5))
            cap = cd['price'].quantile(0.95)
            sns.violinplot(data=cd[cd['price']<=cap], y='product_category_name', x='price',
                           order=top8, palette='Set2', ax=ax, inner='quartile')
            ax.set_title('Violin Plot: Distribusi Harga per Kategori', fontweight='bold')
            ax.set_xlabel('Harga (R$)'); ax.set_ylabel('Kategori')
            plt.tight_layout()
            st.pyplot(fig, use_container_width=True); plt.close()

# ── Footer ───────────────────────────────────────────────────────────────────
st.markdown("---")
