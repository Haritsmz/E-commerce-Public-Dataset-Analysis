import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import streamlit as st
from babel.numbers import format_currency

sns.set(style='dark')

# Load cleaned data
all_df = pd.read_csv("dashboard/cleaned_merged_df.csv")
rfm_df = pd.read_csv("dashboard\cleaned_rfm_df.csv")

datetime_columns = ["order_purchase_timestamp", "order_delivered_customer_date"]
all_df.sort_values(by="order_purchase_timestamp", inplace=True)
all_df.reset_index(drop=True, inplace=True)

for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

# Filter data
min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()

with st.sidebar:
    # Menambahkan logo 
    st.image("logo.jpeg", use_column_width=True)
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu', min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = all_df[(all_df["order_purchase_timestamp"] >= str(start_date)) & 
                  (all_df["order_purchase_timestamp"] <= str(end_date))]
merged_df = rfm_df.merge(all_df[['order_purchase_timestamp']], left_index=True, right_index=True)
rfm_df_filtered = merged_df[(merged_df["order_purchase_timestamp"] >= str(start_date)) & 
                            (merged_df["order_purchase_timestamp"] <= str(end_date))]

# Menampilkan informasi dalam Streamlit
st.title("E-Commerce Dashboard")

total_customers = main_df['customer_id'].nunique()
total_seller = main_df['seller_id'].nunique()
total_product_category = main_df['product_category_name_english'].nunique()
total_sales = int(main_df["price"].sum()) if "price" in main_df.columns else 0
average_rating = round(main_df["review_score"].mean(), 1) if "review_score" in main_df.columns else 0
average_sales_per_order = round(main_df["price"].mean(), 2) if "price" in main_df.columns else 0

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Customers", total_customers)
with col2:
    st.metric("Total Sellers", total_seller)
with col3:
    st.metric("Total Product Categories", total_product_category)
    
col4, col5, col6 = st.columns(3)
with col4:
    st.metric("Total Sales", f"R$ {total_sales:,}") 
with col5:
    st.metric("Average Rating", f"{average_rating}")
with col6:
    st.metric("Average Sales per Order", f"R$ {average_sales_per_order:,}") 

st.markdown("""---""")

# Menghitung pesanan harian
daily_orders_df = main_df.groupby(main_df['order_purchase_timestamp'].dt.date).size().reset_index(name='order_count')
daily_orders_df.rename(columns={'order_purchase_timestamp': 'order_date'}, inplace=True)

# Plotting menggunakan Plotly
fig = px.line(
    daily_orders_df,
    x='order_date',
    y='order_count',
    title='Number of Daily Orders',
    labels={'order_date': 'Order Date', 'order_count': 'Number of Daily Orders'},  
    markers=True
)

# Menyesuaikan ukuran font dan style
fig.update_layout(
    title_font=dict(size=24),  
    xaxis_title_font=dict(size=18),
    yaxis_title_font=dict(size=18),
    xaxis_tickfont=dict(size=15),
    yaxis_tickfont=dict(size=20),
    plot_bgcolor='rgba(0,0,0,0)',  
    yaxis=dict(showgrid=False),    
    xaxis=dict(showgrid=False),    
)

st.plotly_chart(fig, use_container_width=True)

# Menghitung frekuensi setiap metode pembayaran
payment_counts = main_df['payment_type'].value_counts().reset_index()
payment_counts.columns = ['payment_type', 'count']

# Mengurutkan metode pembayaran berdasarkan frekuensi dari yang terbanyak
payment_counts = payment_counts.sort_values(by='count', ascending=False)

# Membuat pie chart menggunakan Plotly
fig = px.pie(payment_counts, 
             names='payment_type', 
             values='count', 
             title='Distribution of Payment Methods')

# Menyesuaikan ukuran font dan style
fig.update_layout(
    title_font=dict(size=24),  
    xaxis_title_font=dict(size=18),
    yaxis_title_font=dict(size=18),
    xaxis_tickfont=dict(size=15),
    yaxis_tickfont=dict(size=20),
    plot_bgcolor='rgba(0,0,0,0)',  
    yaxis=dict(showgrid=False),    
    xaxis=dict(showgrid=False),    
)

# Menampilkan pie chart di Streamlit
st.plotly_chart(fig, use_container_width=True)

# Menghitung jumlah pelanggan per kota
top_cities_customers_df = (
    main_df.groupby('customer_city')['customer_id'].nunique().reset_index(name='customer_count')
    .sort_values(by='customer_count', ascending=False)
    .head(5)
)

# Menghitung jumlah penjual per kota
top_cities_sellers_df = (
    main_df.groupby('seller_city')['seller_id'].nunique().reset_index(name='seller_count')
    .sort_values(by='seller_count', ascending=False)
    .head(5)
)

# Plotting Top 5 Cities by Customers 
fig_customers = px.bar(
    top_cities_customers_df,
    x='customer_city',
    y='customer_count',
    title='Top 5 City by Customer',
    labels={'customer_city': 'City', 'customer_count': 'Number of Customer'},
    text='customer_count',
)

# Plotting Top 5 Cities by Sellers 
fig_sellers = px.bar(
    top_cities_sellers_df,
    x='seller_city',
    y='seller_count',
    title='Top 5 City by Seller',
    labels={'seller_city': 'City', 'seller_count': 'Number of Seller'},
    text='seller_count',  
)

# Menyesuaikan tampilan
for fig in [fig_customers, fig_sellers]:
    fig.update_traces(textposition='outside')  
    fig.update_layout(
        title_font=dict(size=24),  
        xaxis_title_font=dict(size=18),
        yaxis_title_font=dict(size=18),
        xaxis_tickfont=dict(size=15),
        yaxis_tickfont=dict(size=20),
        plot_bgcolor='rgba(0,0,0,0)',  
        yaxis=dict(showgrid=False),    
        xaxis=dict(showgrid=False),    
    )

col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(fig_customers, use_container_width=True)
with col2:
    st.plotly_chart(fig_sellers, use_container_width=True)

# Menghitung jumlah penjualan per kategori
sum_order_items_df = main_df.groupby('product_category_name_english')['qty'].count().sort_values(ascending=True).reset_index()

# Mengambil 10 kategori teratas
top_10_categories = sum_order_items_df.tail(10)

# Membuat bar chart menggunakan Plotly
fig = px.bar(top_10_categories,
             x='qty',
             y='product_category_name_english',
             title="Top 10 Product Categories by Number of Sales",
             labels={'qty': 'Total Sales', 'product_category_name_english': 'Product Category'},
             color='qty',
             color_continuous_scale=px.colors.sequential.Blues)

# Menyesuaikan ukuran font dan style
fig.update_layout(
    title_font=dict(size=24),  
    xaxis_title_font=dict(size=18),
    yaxis_title_font=dict(size=18),
    xaxis_tickfont=dict(size=15),
    yaxis_tickfont=dict(size=20),
    plot_bgcolor='rgba(0,0,0,0)',  
    yaxis=dict(showgrid=False),    
    xaxis=dict(showgrid=False),    
)

st.plotly_chart(fig, use_container_width=True)

# Menghitung jumlah penjualan per kategori
highest_score_category = main_df.groupby('product_category_name_english')['review_score'].mean().sort_values(ascending=True).reset_index()

# Mengambil 10 kategori dengan skor ulasan tertinggi
top_10_score_categories = highest_score_category.tail(10)

# Membuat bar chart menggunakan Plotly
fig = px.bar(top_10_score_categories,
             x='review_score',
             y='product_category_name_english',
             title="Top 10 Product Categories by Score Reviews",
             labels={'review_score': 'Score', 'product_category_name_english': 'Product Category'},
             color='review_score',
             color_continuous_scale=px.colors.sequential.Blues)

# Menyesuaikan ukuran font dan style
fig.update_layout(
    title_font=dict(size=24),  
    xaxis_title_font=dict(size=18),
    yaxis_title_font=dict(size=18),
    xaxis_tickfont=dict(size=15),
    yaxis_tickfont=dict(size=20),
    plot_bgcolor='rgba(0,0,0,0)',  
    yaxis=dict(showgrid=False),    
    xaxis=dict(showgrid=False),    
)

st.plotly_chart(fig, use_container_width=True)

# RFM Parameters
st.subheader("RFM Parameters")

col1, col2, col3 = st.columns(3)

with col1:
    avg_recency = round(rfm_df_filtered.Recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)
with col2:
    avg_frequency = round(rfm_df_filtered.Frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)
with col3:
    avg_frequency = format_currency(rfm_df_filtered.Monetary.mean(), "AUD", locale='es_CO') 
    st.metric("Average Monetary", value=avg_frequency)