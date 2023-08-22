import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import numpy as np
from babel.numbers import format_currency
sns.set(style='dark')

# Fungsi untuk membuat DataFrame harian pesanan
def create_daily_orders_df(df):
    daily_orders_df = df.groupby(["yr", "mnth"]).agg({
        "casual": "sum",
        "registered": "sum"
    }).reset_index()
    daily_orders_df["total"] = daily_orders_df["casual"] + daily_orders_df["registered"]
    daily_orders_df["month_year"] = daily_orders_df["yr"].astype(str) + "-" + daily_orders_df["mnth"].astype(str).str.zfill(2)
    return daily_orders_df

# Fungsi untuk membuat DataFrame pertumbuhan pengguna per bulan
def create_growth_df(df):
    growth_df = df.groupby(["yr", "mnth"]).agg({
        "casual": "sum",
        "registered": "sum"
    }).reset_index()
    growth_df["total"] = growth_df["casual"] + growth_df["registered"]
    growth_df["month_year"] = growth_df["yr"].astype(str) + "-" + growth_df["mnth"].astype(str).str.zfill(2)
    growth_df.sort_values("month_year", inplace=True)
    growth_df["growth"] = growth_df["total"].pct_change() * 100
    return growth_df

# Fungsi untuk membuat DataFrame perbandingan pengguna berdasarkan cuaca
def create_weather_comparison_df(df):
    weather_comparison_df = df.groupby("weathersit").agg({
        "casual": "sum",
        "registered": "sum"
    }).reset_index()
    weather_comparison_df["total"] = weather_comparison_df["casual"] + weather_comparison_df["registered"]
    return weather_comparison_df


# Load data
day_df = pd.read_csv("day.csv")

# Ubah kolom 'dteday' menjadi datetime
day_df["dteday"] = pd.to_datetime(day_df["dteday"])

# Sidebar Streamlit
with st.sidebar:
    st.image("https://png.pngtree.com/png-vector/20220607/ourmid/pngtree-bicycle-logo-in-trendy-design-style-png-image_4861446.png")
    start_date = st.date_input("Rentang Waktu (Mulai)", day_df["dteday"].min())
    end_date = st.date_input("Rentang Waktu (Selesai)", day_df["dteday"].max())

# Konversi start_date dan end_date menjadi datetime64[ns]
start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

main_df = day_df[(day_df["dteday"] >= start_date) & (day_df["dteday"] <= end_date)]

# Buat DataFrame berdasarkan pertanyaan
daily_orders_df = create_daily_orders_df(main_df)
growth_df = create_growth_df(main_df)
weather_comparison_df = create_weather_comparison_df(main_df)

# Streamlit UI
st.title('Bikeshare Analysis Dashboard Secara Tanggal Input')

st.header('Perbandingan Jumlah Pengguna Casual vs. Registered per Bulan')
plt.figure(figsize=(10, 6))
plt.plot(daily_orders_df["month_year"], daily_orders_df["casual"], marker='o', label='Casual')
plt.plot(daily_orders_df["month_year"], daily_orders_df["registered"], marker='o', label='Registered')
plt.xlabel("Bulan-Tahun")
plt.ylabel("Jumlah Pengguna")
plt.title("Perbandingan Pengguna Casual vs. Registered per Bulan")
plt.xticks(rotation=45)
plt.legend()
st.pyplot(plt)

st.header('Pertumbuhan Pengguna per Bulan')
plt.figure(figsize=(10, 6))
plt.plot(growth_df["month_year"], growth_df["growth"], marker='o', color='green')
plt.xlabel("Bulan-Tahun")
plt.ylabel("Pertumbuhan (%)")
plt.title("Pertumbuhan Pengguna per Bulan")
plt.xticks(rotation=45)
st.pyplot(plt)

st.header('Perbandingan Jumlah Pengguna Berdasarkan Cuaca')
weather_labels = ["Cerah", "Berawan", "Hujan Ringan/Salju Ringan", "Hujan Lebat/Salju Lebat"]
plt.figure(figsize=(10, 6))
plt.bar(weather_comparison_df["weathersit"].map({1: "Cerah", 2: "Berawan", 3: "Hujan Ringan/Salju Ringan", 4: "Hujan Lebat/Salju Lebat"}), weather_comparison_df["total"])
plt.xlabel("Cuaca")
plt.ylabel("Jumlah Pengguna")
plt.title("Perbandingan Jumlah Pengguna Berdasarkan Cuaca")
plt.xticks(rotation=45)
st.pyplot(plt)

st.header("RFM Analisi")
# Menghitung Recency, diubah menjadi jumlah hari
tanggal_terbaru = day_df["dteday"].max()
day_df["recency"] = (tanggal_terbaru - day_df["dteday"]).dt.days

# Analisis RFM
rfm_df = day_df.groupby('casual').agg({
    'recency': 'min',    # Recency: Kapan terakhir pelanggan melakukan transaksi?
    'instant': 'count',  # Frequency: Seberapa sering seorang pelanggan melakukan pembelian?
    'cnt': 'sum'         # Monetary: Total nilai pembelian
}).reset_index()
rfm_df.columns = ["casual", "recency", "frequency", "monetary"]

# Menghitung Recency, diubah menjadi jumlah hari
tanggal_terbaru = main_df["dteday"].max()
main_df["recency"] = (tanggal_terbaru - main_df["dteday"]).dt.days

# Analisis RFM
rfm_df = main_df.groupby('casual').agg({
    'recency': 'min',    # Recency: Kapan terakhir pelanggan melakukan transaksi?
    'instant': 'count',  # Frequency: Seberapa sering seorang pelanggan melakukan pembelian?
    'cnt': 'sum'         # Monetary: Total nilai pembelian
}).reset_index()
rfm_df.columns = ["casual", "recency", "frequency", "monetary"]

# Visualisasi dengan Bar Plot
st.subheader("Top 5 Customers by Recency")
fig1, ax1 = plt.subplots()
sns.barplot(y="recency", x="casual", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette="Blues", ax=ax1)
ax1.set_ylabel("Recency (days)")
ax1.set_xlabel(None)
st.pyplot(fig1)

st.subheader("Top 5 Customers by Frequency")
fig2, ax2 = plt.subplots()
sns.barplot(y="frequency", x="casual", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette="Greens", ax=ax2)
ax2.set_ylabel("Frequency")
ax2.set_xlabel(None)
st.pyplot(fig2)

st.subheader("Top 5 Customers by Monetary")
fig3, ax3 = plt.subplots()
sns.barplot(y="monetary", x="casual", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette="Oranges", ax=ax3)
ax3.set_ylabel("Monetary")
ax3.set_xlabel(None)
st.pyplot(fig3)

# Layout grid untuk visualisasi
col1, col2, col3 = st.columns(3)

# Visualisasi dengan Bar Plot
with col1:
    st.subheader("Top 5 Customers by Recency")
    fig1, ax1 = plt.subplots()
    sns.barplot(y="recency", x="casual", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette="Blues", ax=ax1)
    ax1.set_ylabel("Recency (days)")
    ax1.set_xlabel(None)
    st.pyplot(fig1)

with col2:
    st.subheader("Top 5 Customers by Frequency")
    fig2, ax2 = plt.subplots()
    sns.barplot(y="frequency", x="casual", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette="Greens", ax=ax2)
    ax2.set_ylabel("Frequency")
    ax2.set_xlabel(None)
    st.pyplot(fig2)

with col3:
    st.subheader("Top 5 Customers by Monetary")
    fig3, ax3 = plt.subplots()
    sns.barplot(y="monetary", x="casual", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette="Oranges", ax=ax3)
    ax3.set_ylabel("Monetary")
    ax3.set_xlabel(None)
    st.pyplot(fig3)

st.title("------------------------------------------------")

st.title('Visualisasi Bikeshare Analysis Keseluruhan')
day_df = pd.read_csv("day.csv")

st.header("Perbandingan Pengguna Bikeshare Casual vs. Registered per tahun berdasarkan bulan")
# Filter data untuk tahun 2011 dan 2012
filtered_df = day_df[(day_df['yr'] == 0) | (day_df['yr'] == 1)]

# menggrupkan terhadapat tahun dan bulan
sum_casual_registered_df = filtered_df.groupby(["yr", "mnth"])[['casual', 'registered']].sum().reset_index()

# Membuat Visualisasi
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(15, 6))

# Plot untuk year 2011
sns.barplot(x="mnth", y="value", hue="variable", data=sum_casual_registered_df[sum_casual_registered_df['yr'] == 0]
            .melt(id_vars=["yr", "mnth"], value_vars=["casual", "registered"]),
            palette={"casual": "#72BCD4", "registered": "#D3D3D3"}, ax=ax[0])
ax[0].set_ylabel("Total Count")
ax[0].set_xlabel("Month")
ax[0].set_title("Year 2011")
ax[0].legend(title=None, loc='upper left')

# Plot untuk year 2012
sns.barplot(x="mnth", y="value", hue="variable", data=sum_casual_registered_df[sum_casual_registered_df['yr'] == 1]
            .melt(id_vars=["yr", "mnth"], value_vars=["casual", "registered"]),
            palette={"casual": "#72BCD4", "registered": "#D3D3D3"}, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Month")
ax[1].set_title("Year 2012")
ax[1].legend(title=None, loc='upper left')

plt.tight_layout()
st.pyplot(fig)


st.header("Pertumbuhan Pengguna Bikeshare Tiap Bulan Selama Dua Tahun")
# Menghitung total pengguna (casual + registered) per bulan
day_df['dteday'] = pd.to_datetime(day_df['dteday'])
day_df['year_month'] = day_df['dteday'].dt.to_period('M')
df_monthly = day_df.groupby('year_month')['cnt'].sum()

# Membuat plot garis untuk pertumbuhan jumlah pengguna per bulan
plt.figure(figsize=(10, 6))
df_monthly.plot(marker='o', linestyle='-', color=['b', 'g'])
plt.xlabel('Month')
plt.ylabel('Total Users')
plt.title('Pertumbuhan Pengguna Bikeshare Tiap Bulan Selama Dua Tahun')
plt.xticks(rotation=45)
plt.legend(['Casual', 'Registered'])
plt.tight_layout()
st.pyplot(plt)



st.header("Perbandingan Jumlah Pengguna Bikeshare Pada Setiap Cuaca")
# Menghitung total pengguna (casual + registered) berdasarkan kondisi cuaca
weather_df = day_df.groupby('weathersit')['cnt'].sum()

# Membuat plot dengan batang berwarna beda dan legend untuk tiap kondisi cuaca
plt.figure(figsize=(10, 6))
ax = weather_df.plot(kind='bar', width=0.4, color=['#3498db', '#2ecc71', '#d62728'])
ax.set_xticklabels(weather_df.index, rotation=0)
ax.set_xlabel('Weather Situation')
ax.set_ylabel('Count')
ax.set_title('Perbandingan Jumlah Pengguna Bikeshare Pada Setiap Cuaca')

# Menambahkan grid
ax.grid(axis='y', linestyle='--', alpha=0.7)

# Menambahkan shadow pada bar
for container in ax.containers:
    ax.bar_label(container, fmt='%d', label_type='edge', fontsize=10)

# Menambahkan tanda angka pada sumbu y
ax.set_yticklabels(['{:.0f}'.format(x) for x in ax.get_yticks()])

# Menambahkan legend untuk tiap kondisi cuaca
handles, labels = ax.get_legend_handles_labels()
weather_labels = ['Weather 1', 'Weather 2', 'Weather 3']
weather_handles = [plt.Line2D([0], [0], color=color, linewidth=3, label=label) for color, label in zip(['#3498db', '#2ecc71', '#d62728'], weather_labels)]
ax.legend(handles=handles + weather_handles, title='Weather Situation')
plt.tight_layout()
st.pyplot(plt)


st.title("Analsisi RFM")
# Menghitung Recency, diubah menjadi jumlah hari
tanggal_terbaru = main_df["dteday"].max()
main_df["recency"] = (tanggal_terbaru - main_df["dteday"]).dt.days

# Analisis RFM
rfm_df = main_df.groupby('casual').agg({
    'recency': 'min',    # Recency: Kapan terakhir pelanggan melakukan transaksi?
    'instant': 'count',  # Frequency: Seberapa sering seorang pelanggan melakukan pembelian?
    'cnt': 'sum'         # Monetary: Total nilai pembelian
}).reset_index()
rfm_df.columns = ["casual", "recency", "frequency", "monetary"]

# Visualisasi dengan Bar Plot
st.subheader("Top 5 Customers by Recency")
fig1, ax1 = plt.subplots()
sns.barplot(y="recency", x="casual", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette="Blues", ax=ax1)
ax1.set_ylabel("Recency (days)")
ax1.set_xlabel(None)
st.pyplot(fig1)

st.subheader("Top 5 Customers by Frequency")
fig2, ax2 = plt.subplots()
sns.barplot(y="frequency", x="casual", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette="Greens", ax=ax2)
ax2.set_ylabel("Frequency")
ax2.set_xlabel(None)
st.pyplot(fig2)

st.subheader("Top 5 Customers by Monetary")
fig3, ax3 = plt.subplots()
sns.barplot(y="monetary", x="casual", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette="Oranges", ax=ax3)
ax3.set_ylabel("Monetary")
ax3.set_xlabel(None)
st.pyplot(fig3)



st.caption('Bike Share Analysis by Rezki Dwi Rahmantyo')
