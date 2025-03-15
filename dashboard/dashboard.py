import streamlit as st  # type: ignore
import pandas as pd  # type: ignore
import matplotlib.pyplot as plt  # type: ignore
import seaborn as sns  # type: ignore
import matplotlib.dates as mdates  # type: ignore
import os

sns.set(style='dark')

# -------------------------------
# 1. Load Data
# -------------------------------
st.title("Tren Peminjaman Sepeda 🚲")
st.subheader("Analisis pola peminjaman sepeda berdasarkan musim, kecepatan angin, dan faktor lingkungan")

@st.cache_data  
def load_data():
    script_dir = os.path.dirname(os.path.abspath(__file__))  
    file_path = os.path.join(script_dir, "..", "data", "day.csv")  

    if not os.path.exists(file_path):
        st.error(f"⚠️ File data tidak ditemukan! Pastikan `{file_path}` ada di folder yang benar.")
        return None

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

    # Menambahkan filter rentang tanggal di sidebar
    start_date, end_date = st.sidebar.date_input(
        label='📅 Pilih Rentang Waktu:',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

    # Pastikan tanggal valid (start <= end)
    if start_date > end_date:
        st.sidebar.error("⚠️ Tanggal awal tidak boleh lebih besar dari tanggal akhir.")
    else:
        # Filter dataset berdasarkan rentang tanggal
        filtered_df = day_df[(day_df["dteday"] >= pd.Timestamp(start_date)) & (day_df["dteday"] <= pd.Timestamp(end_date))]
        
        # -------------------------------
        # 3. Visualisasi Data
        # -------------------------------
        
        ## 🔹 1. Tren Penggunaan Sepeda
        st.subheader('📊 Tren Penggunaan Sepeda')
        fig, ax = plt.subplots(figsize=(14,6))
        sns.set_style("whitegrid")
        for col, color in zip(['registered', 'casual'], ['royalblue', 'darkorange']):
            sns.lineplot(x=filtered_df['dteday'], y=filtered_df[col], label=f'Pengguna {col.capitalize()}', color=color, linewidth=2)

        plt.xlim(filtered_df['dteday'].min(), filtered_df['dteday'].max())
        plt.xticks(rotation=30, ha='right')
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
        plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        plt.title("Tren Penggunaan Sepeda", fontsize=14, fontweight='bold')
        plt.xlabel("Tahun")
        plt.ylabel("Jumlah Pengguna")
        plt.legend()
        plt.grid(True, linestyle='--', alpha=0.7)
        st.pyplot(fig)
        
        ## 🔹 2. Pengaruh Musim terhadap Peminjaman Sepeda
        st.subheader("🌦️ Pengaruh Musim terhadap Peminjaman Sepeda")
        filtered_df['season'] = pd.Categorical(filtered_df['season'], categories=['Spring', 'Summer', 'Fall', 'Winter'], ordered=True)
        df_grouped = filtered_df.groupby("season")[['registered', 'casual']].sum().reset_index()

        fig, ax = plt.subplots(figsize=(10,6))
        bar_width = 0.4
        x = range(len(df_grouped['season']))

        ax.bar(x, df_grouped['registered'], width=bar_width, label='Terdaftar', color='royalblue', alpha=0.7)
        ax.bar([p + bar_width for p in x], df_grouped['casual'], width=bar_width, label='Kasual', color='darkorange', alpha=0.7)

        plt.xlabel("Musim", fontsize=12)
        plt.ylabel("Jumlah Peminjaman", fontsize=12)
        plt.title("Pengaruh Musim terhadap Pengguna Terdaftar dan Kasual", fontsize=14, fontweight='bold')
        plt.xticks([p + bar_width / 2 for p in x], df_grouped['season'])
        plt.legend(title="Tipe Pengguna")
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        st.pyplot(fig)

        ## 🔹 3. Rata-rata Peminjaman Sepeda Berdasarkan Hari
        st.subheader("📅 Rata-rata Peminjaman Sepeda Berdasarkan Hari")
        filtered_df['weekday'] = filtered_df['weekday'].astype(str)
        day_labels = ['Sen', 'Sel', 'Rab', 'Kam', 'Jum', 'Sab', 'Min']
        colors = sns.color_palette("husl", 7)
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.barplot(data=filtered_df, x='weekday', y='cnt', hue='weekday', palette=colors, dodge=False, ax=ax)
        plt.xticks(ticks=range(7), labels=day_labels)
        plt.title("Rata-rata Peminjaman Sepeda Berdasarkan Hari", fontsize=14, fontweight='bold')
        plt.xlabel("Hari dalam Seminggu")
        plt.ylabel("Jumlah Peminjaman")
        plt.legend([],[], frameon=False)  
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        st.pyplot(fig)

        ## 🔹 4. Korelasi Kecepatan Angin dan Peminjaman Sepeda
        st.subheader("💨 Korelasi Kecepatan Angin dan Peminjaman Sepeda")
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.regplot(x=filtered_df['windspeed'], y=filtered_df['cnt'], scatter_kws={'alpha':0.5}, line_kws={'color':'red'}, ax=ax)
        plt.title("Korelasi Kecepatan Angin dan Peminjaman Sepeda", fontsize=14, fontweight='bold')
        plt.xlabel("Kecepatan Angin")
        plt.ylabel("Jumlah Peminjaman Sepeda")
        plt.grid(True, linestyle='--', alpha=0.7)
        st.pyplot(fig)

        ## 🔹 5. Korelasi Faktor Cuaca dengan Peminjaman Sepeda
        st.subheader("📌 Korelasi Faktor Cuaca dengan Peminjaman Sepeda")
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(filtered_df[['temp', 'atemp', 'hum', 'windspeed', 'cnt']].corr(), annot=True, cmap="coolwarm", linewidths=0.5, ax=ax)
        plt.title("Korelasi Faktor Cuaca dan Jumlah Peminjaman", fontsize=14, fontweight='bold')
        st.pyplot(fig)

        st.caption('Project Carlos Aguiar Da Costa 2025')
