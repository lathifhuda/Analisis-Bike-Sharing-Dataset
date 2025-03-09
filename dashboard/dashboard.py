import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

# Fungsi untuk menyiapkan daily_order_df
def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='dteday').agg({
        "instant_x": "count"
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "instant_x": "order_count"
    }, inplace=True)
    
    return daily_orders_df

# Load dataframe dari file yang sudah diunggah
@st.cache_data
def load_data():
    return pd.read_csv("dashboard/all_data.csv")

data = load_data()

# Judul dashboard
st.title("Dashboard Bike Rentals")

# Konversi kolom tanggal
if 'dteday' in data.columns:
    data['dteday'] = pd.to_datetime(data['dteday'])

min_date = data['dteday'].min()
max_date = data['dteday'].max()

# Sidebar untuk filter tanggal
with st.sidebar:
    st.image("https://c8.alamy.com/comp/2NAGMWM/cartoon-illustration-of-boy-character-riding-a-bicycle-2NAGMWM.jpg")
    start_date, end_date = st.date_input(
        label='Rentang Waktu', min_value=min_date, max_value=max_date, value=[min_date, max_date]
    )

# Filter data berdasarkan tanggal
main_df = data[(data['dteday'] >= pd.Timestamp(start_date)) & (data['dteday'] <= pd.Timestamp(end_date))]

daily_orders_df = create_daily_orders_df(main_df)

# Plot dengan Matplotlib
monthly_rentals_df = pd.DataFrame({
    "dteday": pd.date_range(start="2021-01-01", periods=12, freq="M"),
    "total_rentals": [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200],
    "registered_users": [80, 150, 250, 350, 450, 550, 650, 750, 850, 950, 1050, 1150],
    "casual_users": [20, 50, 70, 90, 110, 130, 150, 170, 190, 210, 230, 250]
})

# Pastikan dteday jadi kolom, bukan index
monthly_rentals_df = monthly_rentals_df.reset_index(drop=True)

# Pastikan kolom tanggal dalam format datetime
data['dteday'] = pd.to_datetime(data['dteday'])

# Resample data bulanan
monthly_rentals_df = data.resample(rule='M', on='dteday').agg({
    "cnt_x": "sum",              # Total penyewaan sepeda
    "registered_x": "sum",       # Total pengguna terdaftar
    "casual_x": "sum"            # Total pengguna kasual
}).reset_index()

# Ubah format tanggal agar lebih rapi
monthly_rentals_df['dteday'] = monthly_rentals_df['dteday'].dt.strftime('%Y-%m')

# Pastikan data sudah di-load dan tanggalnya benar
data['dteday'] = pd.to_datetime(data['dteday'])

# Buat daily orders dataframe
daily_orders_df = data.groupby('dteday').agg({
    "cnt_x": "sum",              # Total penyewaan sepeda
    "registered_x": "sum",       # Total pengguna terdaftar
    "casual_x": "sum"            # Total pengguna kasual
}).reset_index()

# Menghitung total rentals & revenue
st.subheader('Daily Bike Rentals 🚲')

col1, col2 = st.columns(2)

with col1:
    total_orders = daily_orders_df['cnt_x'].sum()
    st.metric("Total Rentals", value=total_orders)

with col2:
    total_registered = daily_orders_df['registered_x'].sum()
    st.metric("Total Registered Users", value=total_registered)

# Visualisasi daily orders
fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_orders_df["dteday"],
    daily_orders_df["cnt_x"],
    marker='o', 
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
ax.set_xlabel('Date')
ax.set_ylabel('Total Rentals')
ax.set_title('Daily Bike Rentals')

st.pyplot(fig)

# Visualisasi registered vs casual users
st.subheader('Monthly Bike Rentals - Registered vs Casual Users 🚲')

if not monthly_rentals_df.empty:
    fig, ax = plt.subplots(1, 2, figsize=(18, 6))

    # Bar chart pengguna terdaftar
    sns.barplot(x='dteday', y='registered_x', data=monthly_rentals_df, ax=ax[0], color='#1f77b4')
    ax[0].set_title('Monthly Bike Rentals - Registered Users')
    ax[0].set_xlabel('Month')
    ax[0].set_ylabel('Total Rentals')
    ax[0].tick_params(axis='x', rotation=45)

    # Bar chart pengguna kasual
    sns.barplot(x='dteday', y='casual_x', data=monthly_rentals_df, ax=ax[1], color='#ff7f0e')
    ax[1].set_title('Monthly Bike Rentals - Casual Users')
    ax[1].set_xlabel('Month')
    ax[1].set_ylabel('Total Rentals')
    ax[1].tick_params(axis='x', rotation=45)

    plt.tight_layout()
    st.pyplot(fig)
else:
    st.warning("Data tidak tersedia untuk rentang tanggal yang dipilih. Silakan pilih rentang lain.")


st.subheader("Best Customer Based on RFM Parameters 🚲")

# Fungsi untuk membuat RFM DataFrame
def create_rfm_df(df):
    if df.empty:
        return pd.DataFrame()  # Kalau data kosong, balikin dataframe kosong

    snapshot_date = df['dteday'].max() + pd.Timedelta(days=1)

    rfm_df = df.groupby('registered_x').agg(
        recency=('dteday', lambda x: (snapshot_date - x.max()).days),
        frequency=('instant_x', 'count'),
        monetary=('cnt_x', 'sum')
    ).reset_index()

    return rfm_df

# Buat RFM hanya kalau ada data yang lolos filter
if not main_df.empty:
    rfm_df = create_rfm_df(main_df)

    if not rfm_df.empty:
        st.success("Data RFM berhasil dibuat! 🚀")

        col1, col2, col3 = st.columns(3)

        with col1:
            avg_recency = round(rfm_df['recency'].mean(), 1)
            st.metric("Average Recency (days)", value=avg_recency)

        with col2:
            avg_frequency = round(rfm_df['frequency'].mean(), 2)
            st.metric("Average Frequency", value=avg_frequency)

        with col3:
            avg_monetary = round(rfm_df['monetary'].mean(), 2)
            st.metric("Average Monetary", value=f"${avg_monetary}")

        # Visualisasi RFM pakai bar chart
        fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
        colors = ["#90CAF9"] * 5

        # Recency Chart
        sns.barplot(y="recency", x="registered_x", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0])
        ax[0].set_ylabel(None)
        ax[0].set_xlabel("User ID", fontsize=30)
        ax[0].set_title("By Recency (days)", loc="center", fontsize=50)
        ax[0].tick_params(axis='y', labelsize=30)
        ax[0].tick_params(axis='x', labelsize=35)

        # Frequency Chart
        sns.barplot(y="frequency", x="registered_x", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
        ax[1].set_ylabel(None)
        ax[1].set_xlabel("User ID", fontsize=30)
        ax[1].set_title("By Frequency", loc="center", fontsize=50)
        ax[1].tick_params(axis='y', labelsize=30)
        ax[1].tick_params(axis='x', labelsize=35)

        # Monetary Chart
        sns.barplot(y="monetary", x="registered_x", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
        ax[2].set_ylabel(None)
        ax[2].set_xlabel("User ID", fontsize=30)
        ax[2].set_title("By Monetary", loc="center", fontsize=50)
        ax[2].tick_params(axis='y', labelsize=30)
        ax[2].tick_params(axis='x', labelsize=35)

        # Tampilkan plot di Streamlit
        st.pyplot(fig)

    else:
        st.warning("Data RFM kosong setelah difilter. Coba pilih rentang tanggal atau kategori lain! 🟠")
else:
    st.warning("Data utama kosong setelah filter. Pastikan ada data yang sesuai filter! 🟠")




# Jalankan dengan: streamlit run nama_file.py
