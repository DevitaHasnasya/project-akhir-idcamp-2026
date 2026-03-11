# Brazilian E-Commerce Analytics Dashboard

Proyek analisis data menggunakan **Brazilian E-Commerce Public Dataset (Olist)** sebagai bagian dari proyek akhir kelas **Belajar Analisis Data dengan Python** di Dicoding.

---

## 📁 Struktur Direktori

```
submission/
├── dashboard/
│   ├── dashboard.py          # Aplikasi Streamlit
│   ├── main_data.csv         # Data orders
│   ├── items_data.csv        # Data order items
│   ├── products_data.csv     # Data produk
│   ├── reviews_data.csv      # Data ulasan pelanggan
│   ├── payments_data.csv     # Data pembayaran
│   └── customers_data.csv    # Data pelanggan
├── data/
│   ├── olist_orders_dataset.csv
│   ├── olist_order_items_dataset.csv
│   ├── olist_products_dataset.csv
│   ├── olist_order_reviews_dataset.csv
│   ├── olist_order_payments_dataset.csv
│   └── olist_customers_dataset.csv
├── notebook.ipynb            # Jupyter Notebook analisis lengkap
├── requirements.txt          # Library yang digunakan
└── README.md                 # Panduan ini
```

---

## 🚀 Cara Menjalankan Dashboard

### 1. Clone / Ekstrak Folder

Ekstrak file ZIP submission ke direktori lokal Anda.

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Jalankan Dashboard

```bash
cd dashboard
streamlit run dashboard.py
```

Dashboard akan terbuka otomatis di browser pada `http://localhost:8501`

---

## 📊 Pertanyaan Bisnis yang Dijawab

1. **Tren Penjualan** — Bagaimana tren revenue bulanan dari 2016–2018?
2. **Kategori Produk** — Kategori apa yang menghasilkan revenue & volume terbesar?
3. **Ulasan Pelanggan** — Bagaimana distribusi skor ulasan dan hubungannya dengan ketepatan pengiriman?
4. **Metode Pembayaran** — Metode apa yang paling populer dan bagaimana pola cicilan?

---

## 🔍 Fitur Dashboard

- **Filter Interaktif** — Filter berdasarkan periode, status order, dan wilayah (state)
- **KPI Metrics** — Total order, revenue, avg review score, dan persentase keterlambatan
- **Visualisasi Dinamis** — Semua grafik merespons filter yang dipilih
- **Multi-tab** — Revenue dan jumlah order dalam tab terpisah

---

## 👤 Informasi Proyek

- **Dataset:** Brazilian E-Commerce Public Dataset (Olist)
- **Tools:** Python, Pandas, Matplotlib, Seaborn, Streamlit
- **Kelas:** Belajar Analisis Data dengan Python — Dicoding
