import streamlit as st  # type: ignore
import pandas as pd  # type: ignore
import matplotlib.pyplot as plt  # type: ignore
import seaborn as sns  # type: ignore
import os

sns.set(style='dark')

# -------------------------------
# 1. Load Data
# -------------------------------
st.title("Tren Peminjaman Sepeda 🚲")
st.subheader("Analisis pola peminjaman sepeda berdasarkan musim, kecepatan angin, dan faktor lingkungan")

@st.cache_data  
def load_data():
    file_path = "./data/day.csv"  # Mengarahkan ke folder "data" (huruf kecil)
    df = pd.read_csv(file_path)
    df['dteday'] = pd.to_datetime(df['dteday'])
    df['season'] = df['season'].map({1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'})
    return df

day_df = load_data()

if day_df is not None and not day_df.empty:
    # -------------------------------
    # 2. Sidebar Filters
    # -------------------------------
    
    # Mengambil rentang tanggal dari dataset
    min_date = day_df["dteday"].min()
    max_date = day_df["dteday"].max()
    start_date, end_date = st.sidebar.date_input(
        label='Rentang Waktu', min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )
    
    # Filter berdasarkan rentang tanggal
    day_df = day_df[(day_df["dteday"] >= pd.to_datetime(start_date)) & (day_df["dteday"] <= pd.to_datetime(end_date))]
    
    if not day_df.empty:
        # -------------------------------
        # 3. Tren Penggunaan Sepeda
        # -------------------------------
        st.subheader('📊 Tren Penggunaan Sepeda')
        fig, ax = plt.subplots(figsize=(12,6))
        day_df_grouped = day_df.groupby(day_df['dteday'].dt.to_period("M")).sum(numeric_only=True)
        sns.barplot(x=day_df_grouped.index.astype(str), y=day_df_grouped['registered'], color='blue', label='Registered Users', ax=ax)
        sns.barplot(x=day_df_grouped.index.astype(str), y=day_df_grouped['casual'], bottom=day_df_grouped['registered'], color='orange', label='Casual Users', ax=ax)
        plt.xticks(rotation=45, fontsize=10)
        plt.title("Tren Penggunaan Sepeda oleh Pengguna Terdaftar vs Kasual (2011-2012)", fontsize=14)
        plt.xlabel("Bulan", fontsize=12)
        plt.ylabel("Jumlah Pengguna", fontsize=12)
        plt.legend()
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        st.pyplot(fig)

        # -------------------------------
        # 4. Faktor Musim terhadap Penggunaan Sepeda
        # -------------------------------
        st.subheader("🌦️ Pengaruh Musim terhadap Peminjaman Sepeda")
        fig, ax = plt.subplots(figsize=(8,6))
        avg_usage_by_season = day_df.groupby('season')[['registered', 'casual']].mean()
        avg_usage_by_season.plot(kind='bar', stacked=True, color=['blue', 'orange'], ax=ax)
        plt.xlabel("Musim")
        plt.ylabel("Rata-rata Jumlah Pengguna")
        plt.title("Pengaruh Musim terhadap Penggunaan Sepeda")
        st.pyplot(fig)

        # -------------------------------
        # 5. Korelasi antara Kecepatan Angin dan Peminjaman Sepeda
        # -------------------------------
        st.subheader("💨 Korelasi Kecepatan Angin dan Peminjaman Sepeda")
        fig, ax = plt.subplots(figsize=(8,6))
        windspeed_bins = pd.cut(day_df['windspeed'], bins=5)
        windspeed_usage = day_df.groupby(windspeed_bins, observed=False)['cnt'].mean()  # Tambah observed=False
        sns.barplot(x=windspeed_usage.index.astype(str), y=windspeed_usage, color='green', edgecolor='black', ax=ax)
        plt.xlabel("Kecepatan Angin (Binned)", fontsize=12)
        plt.ylabel("Rata-rata Peminjaman Sepeda", fontsize=12)
        plt.title("Korelasi antara Kecepatan Angin dan Peminjaman Sepeda", fontsize=14)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        st.pyplot(fig)

        # -------------------------------
        # 6. Heatmap Korelasi Faktor Lingkungan
        # -------------------------------
        st.subheader("📌 Korelasi Faktor Lingkungan dengan Peminjaman Sepeda")
        fig, ax = plt.subplots(figsize=(10,7))
        sns.heatmap(day_df[['temp', 'atemp', 'hum', 'windspeed', 'cnt']].corr(), annot=True, cmap='coolwarm', fmt='.2f', linewidths=0.8, linecolor='black', cbar_kws={'shrink': 0.8}, ax=ax)
        plt.title("Matriks Korelasi antara Faktor Lingkungan dan Peminjaman Sepeda", fontsize=14, pad=15)
        plt.xticks(fontsize=12, rotation=45)
        plt.yticks(fontsize=12)
        st.pyplot(fig)

        st.caption('Project Carlos Aguiar Da Costa 2025')
