import streamlit as st
import pandas as pd
import sqlite3
import base64
from datetime import datetime

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Portal Resmi Desa LAILARA",
    page_icon="hamane.jpg",
    layout="wide"
)

# --- HELPER KONVERSI GAMBAR KE BASE64 ---
def convert_image_to_base64(uploaded_file):
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        base64_encoded = base64.b64encode(bytes_data).decode('utf-8')
        mime_type = uploaded_file.type
        return f"data:{mime_type};base64,{base64_encoded}"
    return None

# --- 2. INISIALISASI DATABASE SQLITE ---
def init_db():
    conn = sqlite3.connect('desa_lengkap.db')
    cursor = conn.cursor()
    
    # 1. Tabel Users / Hak Akses (1 Admin Utama)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            nama TEXT,
            role TEXT
        )
    ''')
    
    # 2. Tabel Penduduk
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS penduduk (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nik TEXT UNIQUE,
            nama TEXT,
            jenis_kelamin TEXT,
            dusun TEXT,
            pekerjaan TEXT,
            rt_rw TEXT
        )
    ''')
    
    # 3. Tabel Pemerintah Desa
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pemerintah (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT,
            jabatan TEXT,
            kategori TEXT,
            kontak TEXT,
            foto_url TEXT
        )
    ''')
    
    # 4. Tabel Pengumuman
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pengumuman (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tanggal TEXT,
            judul TEXT,
            isi TEXT,
            penulis TEXT
        )
    ''')

    # 5. Tabel Stunting
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stunting (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama_balita TEXT,
            nama_ortu TEXT,
            usia_bulan INTEGER,
            tinggi_badan REAL,
            berat_badan REAL,
            status TEXT,
            tahun_perolehan TEXT
        )
    ''')
    
    # 6. Tabel Bantuan
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bantuan (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nik TEXT,
            nama_penerima TEXT,
            jenis_bantuan TEXT,
            rincian_bantuan TEXT,
            status_penyaluran TEXT,
            tahun_perolehan TEXT
        )
    ''')
    
    # 7. Tabel APBDES
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS apbdes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tahun TEXT,
            kategori TEXT,
            sub_kategori TEXT,
            jumlah_anggaran REAL
        )
    ''')
    
    # 8. Tabel Layanan Surat
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS layanan_surat (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tanggal TEXT,
            nik TEXT,
            nama TEXT,
            jenis_surat TEXT,
            keperluan TEXT,
            no_hp TEXT,
            status TEXT DEFAULT 'Diproses'
        )
    ''')
    
    # 9. Tabel Kritik & Saran
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS kritik_saran (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tanggal TEXT,
            nama TEXT,
            email_hp TEXT,
            kategori TEXT,
            pesan TEXT,
            tanggapan TEXT DEFAULT 'Belum Ditanggapi'
        )
    ''')

    # 10. Tabel Profil & Lokasi Desa
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS profil_desa (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama_desa TEXT,
            latitude REAL,
            longitude REAL,
            alamat TEXT
        )
    ''')

    # SEEDING DATA USER DEFAULT (1 Admin Utama)
    cursor.execute('SELECT COUNT(*) FROM users')
    if cursor.fetchone()[0] == 0:
        default_users = [
            ('admin', 'admin123', 'Admin Pengelola Desa', 'Admin Desa')
        ]
        cursor.executemany('INSERT INTO users (username, password, nama, role) VALUES (?, ?, ?, ?)', default_users)

    # SEEDING DATA PENDUDUK DEFAULT
    cursor.execute('SELECT COUNT(*) FROM penduduk')
    if cursor.fetchone()[0] == 0:
        penduduk_awal = [
            ("5302011501850001", "Ahmad Sutisna", "Laki-laki", "Dusun I", "Petani", "001/001"),
            ("5302015203900002", "Siti Aminah", "Perempuan", "Dusun I", "Ibu Rumah Tangga", "001/001"),
            ("5302011205880003", "Budi Santoso", "Laki-laki", "Dusun II", "Petani", "002/001"),
            ("5302016408920004", "Maria Ndapa", "Perempuan", "Dusun II", "Guru", "002/002"),
            ("5302011010950005", "Yohanis Umbu", "Laki-laki", "Dusun III", "Wiraswasta", "003/002")
        ]
        cursor.executemany('INSERT INTO penduduk (nik, nama, jenis_kelamin, dusun, pekerjaan, rt_rw) VALUES (?, ?, ?, ?, ?, ?)', penduduk_awal)

    # Data Default Profil & Lokasi Desa
    cursor.execute('SELECT COUNT(*) FROM profil_desa')
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            'INSERT INTO profil_desa (nama_desa, latitude, longitude, alamat) VALUES (?, ?, ?, ?)',
            ("Desa Lailara", -9.7342, 120.2541, "Kec. Katala Hamu Lingu, Kab. Sumba Timur, Nusa Tenggara Timur")
        )

    # Data Default APBDES
    cursor.execute('SELECT COUNT(*) FROM apbdes')
    if cursor.fetchone()[0] == 0:
        apbdes_awal = [
            ("2026", "Pendapatan", "Dana Desa (DD)", 1200000000),
            ("2026", "Pendapatan", "Alokasi Dana Desa (ADD)", 450000000),
            ("2026", "Belanja", "Bidang Pembangunan Desa", 850000000),
            ("2026", "Belanja", "Bidang Pemberdayaan Masyarakat", 350000000),
            ("2026", "Belanja", "Bidang Penyelenggaraan Pemerintahan", 400000000)
        ]
        cursor.executemany('INSERT INTO apbdes (tahun, kategori, sub_kategori, jumlah_anggaran) VALUES (?, ?, ?, ?)', apbdes_awal)

    # Data Default Bantuan Awal
    cursor.execute('SELECT COUNT(*) FROM bantuan')
    if cursor.fetchone()[0] == 0:
        bantuan_awal = [
            ("5302011501850001", "Ahmad Sutisna", "Bantuan Alat Pertanian", "Mesin Traktor Tangan & Pompa Air", "Tersalurkan", "2026"),
            ("5302015203900002", "Siti Aminah", "Bantuan Rumah Tidak Layak Huni (RTLH)", "Rehabilitasi Atap dan Dinding Rumah", "Proses Verifikasi", "2026"),
            ("5302011205880003", "Budi Santoso", "Bantuan Bibit & Pupuk", "50 kg Bibit Padi Unggul & Pupuk Organik", "Tersalurkan", "2026")
        ]
        cursor.executemany('INSERT INTO bantuan (nik, nama_penerima, jenis_bantuan, rincian_bantuan, status_penyaluran, tahun_perolehan) VALUES (?, ?, ?, ?, ?, ?)', bantuan_awal)

    # Data Default Aparat
    cursor.execute('SELECT COUNT(*) FROM pemerintah')
    if cursor.fetchone()[0] == 0:
        pem_awal = [
            ("H. Ahmad Subagja, S.IP.", "Pimpinan Desa", "Pemerintah Desa", "081234567801", "https://img.icons8.com/color/120/user-female-circle.png"),
            ("Rian Hidayat, S.T.", "Sekretaris Desa", "Sekretariat", "081234567802", "https://img.icons8.com/color/120/user-male-circle.png"),
            ("Eko Prasetyo", "Kasi Pemerintahan", "Seksi", "081234567803", "https://img.icons8.com/color/120/user-male-circle.png"),
            ("Dewi Lestari", "Kasi Kesejahteraan", "Seksi", "081234567804", "https://img.icons8.com/color/120/user-female-circle.png")
        ]
        cursor.executemany('INSERT INTO pemerintah (nama, jabatan, kategori, kontak, foto_url) VALUES (?, ?, ?, ?, ?)', pem_awal)

    conn.commit()
    conn.close()

init_db()

# --- 3. HELPER FUNCTIONS ---
def get_df(query, params=()):
    conn = sqlite3.connect('desa_lengkap.db')
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

def execute_query(query, params=()):
    conn = sqlite3.connect('desa_lengkap.db')
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    conn.close()

def is_valid_nik(nik):
    return nik.isdigit() and len(nik) == 16

# --- 4. SESSION STATE / LOGIN SYSTEM ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_role' not in st.session_state:
    st.session_state['user_role'] = 'Publik'
if 'user_name' not in st.session_state:
    st.session_state['user_name'] = ''

# --- 5. SIDEBAR MODE AKSES & NAVIGASI ---
st.sidebar.image("hamane.jpg", use_container_width=True)
st.sidebar.title("🏡 Portal Desa Lailara")

st.sidebar.markdown("---")
st.sidebar.subheader("🔒 Status Akses Sistem")

if not st.session_state['logged_in']:
    mode_akses = st.sidebar.radio("Mode Pengguna:", ["🌐 Publik / Warga", "🔑 Login Admin Pengelola"])
else:
    st.sidebar.success(f"👤 **{st.session_state['user_name']}**")
    st.sidebar.info(f"🔰 Akses: **Pengelola Aplikasi**")
    if st.sidebar.button("🚪 Logout / Keluar"):
        st.session_state['logged_in'] = False
        st.session_state['user_role'] = 'Publik'
        st.session_state['user_name'] = ''
        st.rerun()

st.sidebar.markdown("---")

# Menu Navigasi
if not st.session_state['logged_in'] and mode_akses == "🌐 Publik / Warga":
    menu = st.sidebar.radio(
        "Menu Portal Warga:",
        [
            "🏠 Beranda & Pengumuman",
            "🗺️ Peta & Lokasi Desa",
            "👥 Aparat Desa",
            "📊 Data Penduduk",
            "💰 Transparansi APBDES",
            "🩺 Cek Bantuan & Stunting",
            "📜 Layanan Surat Online",
            "💬 Kritik & Saran Warga"
        ]
    )
elif not st.session_state['logged_in'] and mode_akses == "🔑 Login Admin Pengelola":
    menu = "🔑 Login Form"
else:
    menu_options = [
        "📊 Dashboard Ringkasan",
        "📜 Kelola Surat Masuk",
        "📢 Kelola Pengumuman",
        "👥 Data Penduduk",
        "🩺 Kelola Bantuan & Stunting",
        "💬 Tanggapi Aspirasi",
        "💰 Kelola Keuangan APBDES",
        "🏛️ Kelola Aparat & Profil Desa",
        "👤 Manajemen Akun User"
    ]
    menu = st.sidebar.radio("Panel Pengelola Aplikasi:", menu_options)


# --- 6. HALAMAN AKSES PUBLIK / WARGA ---

if menu == "🔑 Login Form":
    st.title("🔑 Form Login Admin Pengelola Desa")
    st.write("Silakan masukkan akun pengelola utama Anda.")
    st.divider()

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("form_login"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit_login = st.form_submit_button("Masuk ke Panel")

            if submit_login:
                df_u = get_df("SELECT * FROM users WHERE username=? AND password=?", (username, password))
                if not df_u.empty:
                    st.session_state['logged_in'] = True
                    st.session_state['user_role'] = df_u.iloc[0]['role']
                    st.session_state['user_name'] = df_u.iloc[0]['nama']
                    st.success("✅ Login Berhasil!")
                    st.rerun()
                else:
                    st.error("❌ Username atau Password salah.")

elif menu == "🏠 Beranda & Pengumuman":
    # Foto banner di atas judul telah dihapus
    st.title("🏡 Selamat Datang di Portal Resmi Desa LAILARA")
    st.subheader("Pusat Informasi & Layanan Digital Terpadu")
    st.divider()

    col1, col2 = st.columns([2, 1])

    with col1:
        st.header("📢 Pengumuman & Informasi Desa")
        df_pengumuman = get_df("SELECT tanggal, judul, isi, penulis FROM pengumuman ORDER BY id DESC LIMIT 5")
        
        if not df_pengumuman.empty:
            for _, row in df_pengumuman.iterrows():
                with st.expander(f"📌 {row['judul']} ({row['tanggal']})", expanded=True):
                    st.write(row['isi'])
                    st.caption(f"✍️ Diterbitkan oleh: {row['penulis']}")
        else:
            st.info("Belum ada pengumuman terbaru dari pemerintah desa.")

    with col2:
        st.header("📌 Ringkasan Statistik")
        total_p = len(get_df('SELECT * FROM penduduk'))
        total_surat = len(get_df('SELECT * FROM layanan_surat WHERE status=\'Diproses\''))
        st.metric("Total Penduduk Terdaftar", f"{total_p} Jiwa")
        st.metric("Surat Sedang Diproses", f"{total_surat} Pengajuan")
        st.metric("Pengumuman Aktif", f"{len(df_pengumuman)} Info")

        st.divider()
        st.subheader("📍 Lokasi Kantor Desa")
        df_prof = get_df("SELECT latitude, longitude, alamat FROM profil_desa LIMIT 1")
        if not df_prof.empty:
            lat = df_prof.iloc[0]['latitude']
            lon = df_prof.iloc[0]['longitude']
            map_data = pd.DataFrame({'lat': [lat], 'lon': [lon]})
            st.map(map_data, zoom=12)
            st.caption(f"🏠 {df_prof.iloc[0]['alamat']}")

elif menu == "🗺️ Peta & Lokasi Desa":
    st.title("🗺️ Peta Geografis & Lokasi Desa Lailara")
    st.divider()

    df_prof = get_df("SELECT * FROM profil_desa LIMIT 1")
    if not df_prof.empty:
        lat = df_prof.iloc[0]['latitude']
        lon = df_prof.iloc[0]['longitude']
        alamat = df_prof.iloc[0]['alamat']
        nama_desa = df_prof.iloc[0]['nama_desa']

        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader(f"📍 Peta Wilayah {nama_desa}")
            map_data = pd.DataFrame({'lat': [lat], 'lon': [lon]})
            st.map(map_data, zoom=13)
        
        with col2:
            st.subheader("ℹ️ Informasi Wilayah")
            st.markdown(f"**Nama Wilayah:**\n{nama_desa}")
            st.markdown(f"**Alamat Kantor:**\n{alamat}")
            st.markdown(f"**Koordinat:**\n- Latitude: `{lat}`\n- Longitude: `{lon}`")
            
            gmaps_url = f"https://www.google.com/maps?q={lat},{lon}"
            st.markdown(f"[🗺️ Buka di Google Maps]({gmaps_url})", unsafe_allow_html=True)

elif menu == "👥 Aparat Desa":
    st.title("👥 Struktur Pemerintah Desa Lailara")
    st.divider()
    
    df_pem = get_df("SELECT nama, jabatan, kategori, kontak, foto_url FROM pemerintah")
    
    if not df_pem.empty:
        cols = st.columns(3)
        for idx, row in df_pem.iterrows():
            with cols[idx % 3]:
                if row['foto_url']:
                    st.image(row['foto_url'], width=120)
                st.subheader(row['nama'])
                st.caption(f"**{row['jabatan']}** ({row['kategori']})")
                st.write(f"📞 Kontak: {row['kontak']}")
                st.divider()
    else:
        st.info("Data aparat desa belum terisi.")

elif menu == "📊 Data Penduduk":
    st.title("📊 Demografi & Data Penduduk Desa")
    st.divider()

    df_p = get_df("SELECT nik, nama, jenis_kelamin, dusun, rt_rw, pekerjaan FROM penduduk")

    if not df_p.empty:
        total_keseluruhan = len(df_p)
        total_laki = len(df_p[df_p['jenis_kelamin'] == 'Laki-laki'])
        total_perempuan = len(df_p[df_p['jenis_kelamin'] == 'Perempuan'])

        c_m1, c_m2, c_m3 = st.columns(3)
        c_m1.metric("Total Keseluruhan", f"{total_keseluruhan} Jiwa")
        c_m2.metric("Jumlah Laki-laki", f"{total_laki} Jiwa")
        c_m3.metric("Jumlah Perempuan", f"{total_perempuan} Jiwa")

        st.divider()

        st.subheader("🔍 Cari Data Penduduk")
        col_sch1, col_sch2 = st.columns([4, 1])
        keyword = col_sch1.text_input("Ketik Nama, NIK, Dusun, atau Pekerjaan:", placeholder="Contoh: Ahmad, Dusun I, Petani...", key="pub_search_kw")
        btn_cari_pub = col_sch2.button("🔎 Cari", key="btn_pub_search")

        df_tampil = df_p.copy()
        if keyword.strip() != "":
            df_tampil = df_p[
                df_p['nama'].str.contains(keyword, case=False, na=False) |
                df_p['nik'].str.contains(keyword, case=False, na=False) |
                df_p['dusun'].str.contains(keyword, case=False, na=False) |
                df_p['pekerjaan'].str.contains(keyword, case=False, na=False)
            ]
            st.info(f"Ditemukan {len(df_tampil)} hasil pencarian untuk kata kunci **'{keyword}'**")

        st.subheader("📋 Daftar Seluruh Penduduk")
        st.dataframe(df_tampil, use_container_width=True)

        st.divider()

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Sebaran Jenis Kelamin")
            st.bar_chart(df_p['jenis_kelamin'].value_counts())
        with col2:
            st.subheader("Sebaran Per Dusun")
            st.bar_chart(df_p['dusun'].value_counts())

        st.subheader("Sebaran Mata Pencaharian / Pekerjaan")
        st.dataframe(df_p['pekerjaan'].value_counts(), use_container_width=True)
    else:
        st.info("Data demografi penduduk belum terisi di database.")

elif menu == "💰 Transparansi APBDES":
    st.title("💰 Transparansi Anggaran Desa (APBDES)")
    st.divider()

    df_apb = get_df("SELECT tahun, kategori, sub_kategori, jumlah_anggaran FROM apbdes")

    if not df_apb.empty:
        tahun_pilih = st.selectbox("Pilih Tahun Anggaran:", df_apb['tahun'].unique())
        df_filtered = df_apb[df_apb['tahun'] == tahun_pilih]

        tot_pendapatan = df_filtered[df_filtered['kategori'] == 'Pendapatan']['jumlah_anggaran'].sum()
        tot_belanja = df_filtered[df_filtered['kategori'] == 'Belanja']['jumlah_anggaran'].sum()

        col1, col2 = st.columns(2)
        col1.metric("Total Pendapatan Desa", f"Rp {tot_pendapatan:,.0f}")
        col2.metric("Total Belanja Desa", f"Rp {tot_belanja:,.0f}")

        st.subheader("Rincian Postur APBDES")
        st.dataframe(df_filtered, use_container_width=True)
    else:
        st.info("Belum ada data APBDES.")

elif menu == "🩺 Cek Bantuan & Stunting":
    st.title("🩺 Cek Data Bantuan & Program Stunting")
    st.divider()

    tab_b1, tab_b2 = st.tabs(["🔍 Cek Penerima Bantuan", "👶 Data Pemantauan Stunting"])

    with tab_b1:
        st.subheader("Pencarian Penerima Program Bantuan Desa")
        nik_cari = st.text_input("Masukkan NIK Pemohon:", max_chars=16)
        if st.button("Cek Status Bantuan"):
            if not is_valid_nik(nik_cari):
                st.error("❌ NIK tidak valid! NIK harus berupa 16 digit angka.")
            else:
                df_b = get_df("SELECT nik, nama_penerima, jenis_bantuan, rincian_bantuan, status_penyaluran, tahun_perolehan FROM bantuan WHERE nik=?", (nik_cari,))
                if not df_b.empty:
                    st.success("✅ Data Penerima Bantuan Ditemukan!")
                    st.dataframe(df_b, use_container_width=True)
                else:
                    st.warning("❌ NIK tidak terdaftar dalam skema penerima Bantuan Desa.")

    with tab_b2:
        st.subheader("Rekapitulasi Pemantauan Balita (Stunting)")
        df_s = get_df("SELECT nama_balita, usia_bulan, tinggi_badan, berat_badan, status, tahun_perolehan FROM stunting")
        if not df_s.empty:
            st.dataframe(df_s, use_container_width=True)
        else:
            st.info("Belum ada data rekapitulasi stunting.")

elif menu == "📜 Layanan Surat Online":
    st.title("📜 Pengajuan Layanan Surat Online")
    st.write("Silakan isi formulir di bawah ini untuk mengajukan permohonan surat.")
    st.divider()

    with st.form("form_surat", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nik = st.text_input("NIK Pemohon (16 Digit)", max_chars=16)
            nama = st.text_input("Nama Lengkap")
            no_hp = st.text_input("Nomor WA / HP")
        with col2:
            jenis_surat = st.selectbox("Jenis Surat", [
                "Surat Keterangan Usaha (SKU)",
                "Surat Keterangan Tidak Mampu (SKTM)",
                "Surat Keterangan Domisili",
                "Surat Pengantar SKCK",
                "Surat Keterangan Belum Menikah"
            ])
            keperluan = st.text_area("Keperluan / Alasan Permohonan")

        submit_surat = st.form_submit_button("Kirim Pengajuan")

        if submit_surat:
            if not is_valid_nik(nik):
                st.error("❌ NIK tidak valid! NIK harus berupa 16 digit angka.")
            elif nik and nama and keperluan:
                tgl_sekarang = datetime.now().strftime("%Y-%m-%d %H:%M")
                execute_query(
                    "INSERT INTO layanan_surat (tanggal, nik, nama, jenis_surat, keperluan, no_hp) VALUES (?, ?, ?, ?, ?, ?)",
                    (tgl_sekarang, nik, nama, jenis_surat, keperluan, no_hp)
                )
                st.success("✅ Pengajuan berhasil dikirim! Silakan hubungi perangkat desa untuk proses selanjutnya.")
            else:
                st.warning("⚠️ Mohon isi seluruh kolom formulir.")

elif menu == "💬 Kritik & Saran Warga":
    st.title("💬 Layanan Aspirasi & Saran Warga")
    st.divider()

    with st.form("form_kritik", clear_on_submit=True):
        nama = st.text_input("Nama (Isi Anonim jika dirahasiakan)", value="Anonim")
        email_hp = st.text_input("Kontak WA/Email")
        kategori = st.selectbox("Kategori Aspirasi", ["Infrastruktur", "Pelayanan Publik", "Transparansi Anggaran", "Keamanan", "Lainnya"])
        pesan = st.text_area("Isi Pesan Aspirasi / Saran")

        submit_aspirasi = st.form_submit_button("Kirim Aspirasi")

        if submit_aspirasi:
            if pesan:
                tgl_sekarang = datetime.now().strftime("%Y-%m-%d %H:%M")
                execute_query(
                    "INSERT INTO kritik_saran (tanggal, nama, email_hp, kategori, pesan) VALUES (?, ?, ?, ?, ?)",
                    (tgl_sekarang, nama, email_hp, kategori, pesan)
                )
                st.success("✅ Terima kasih! Aspirasi Anda berhasil disampaikan.")
            else:
                st.warning("⚠️ Pesan aspirasi tidak boleh kosong.")


# --- 7. PANEL ADMIN PENGELOLA UTAMA ---

elif menu == "📊 Dashboard Ringkasan":
    st.title("📊 Dashboard Pengelola Desa")
    st.write(f"Selamat datang, **{st.session_state['user_name']}**!")
    st.divider()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Penduduk", len(get_df("SELECT * FROM penduduk")))
    c2.metric("Surat Diproses", len(get_df("SELECT * FROM layanan_surat WHERE status='Diproses'")))
    c3.metric("Penerima Bantuan", len(get_df("SELECT * FROM bantuan")))
    c4.metric("Balita Stunting", len(get_df("SELECT * FROM stunting WHERE status='Stunting'")))

elif menu == "📜 Kelola Surat Masuk":
    st.title("📜 Pengelolaan Layanan Surat")
    st.divider()

    df_surat = get_df("SELECT * FROM layanan_surat ORDER BY id DESC")

    if not df_surat.empty:
        col_c1, col_c2 = st.columns([4, 1])
        search_surat = col_c1.text_input("🔍 Ketik Kata Kunci Surat (Nama, NIK, Jenis, Status):", key="search_surat_input")
        btn_cari_surat = col_c2.button("🔎 Cari Surat", key="btn_surat_search")

        df_surat_filtered = df_surat.copy()
        if search_surat.strip() != "":
            df_surat_filtered = df_surat[
                df_surat['nama'].str.contains(search_surat, case=False, na=False) |
                df_surat['nik'].str.contains(search_surat, case=False, na=False) |
                df_surat['jenis_surat'].str.contains(search_surat, case=False, na=False) |
                df_surat['status'].str.contains(search_surat, case=False, na=False)
            ]
            st.caption(f"Ditemukan **{len(df_surat_filtered)}** pengajuan surat.")

        st.dataframe(df_surat_filtered, use_container_width=True)

        list_s_opts = df_surat_filtered['id'].tolist() if not df_surat_filtered.empty else df_surat['id'].tolist()

        col_s1, col_s2, col_s3 = st.columns([2, 2, 1])
        id_s = col_s1.selectbox("Pilih ID Surat:", list_s_opts, format_func=lambda x: f"ID: {x} - {df_surat[df_surat['id']==x]['nama'].values[0]} ({df_surat[df_surat['id']==x]['jenis_surat'].values[0]})")
        st_s = col_s2.selectbox("Ubah Status:", ["Diproses", "Selesai", "Ditolak"])
        if col_s3.button("Simpan Status"):
            execute_query("UPDATE layanan_surat SET status=? WHERE id=?", (st_s, id_s))
            st.success("✅ Status diperbarui!")
            st.rerun()

        if st.button("🗑️ Hapus Pengajuan Surat"):
            execute_query("DELETE FROM layanan_surat WHERE id=?", (id_s,))
            st.success("✅ Permohonan surat dihapus!")
            st.rerun()
    else:
        st.info("Belum ada permohonan surat masuk.")

elif menu == "📢 Kelola Pengumuman":
    st.title("📢 Pengelolaan Pengumuman Desa")
    st.divider()

    with st.expander("➕ Tambah Pengumuman Baru"):
        with st.form("f_pengumuman", clear_on_submit=True):
            judul = st.text_input("Judul Pengumuman")
            isi = st.text_area("Isi Pengumuman")
            penulis = st.text_input("Penulis", value=st.session_state['user_name'])
            tgl = st.date_input("Tanggal").strftime("%Y-%m-%d")
            if st.form_submit_button("Publikasikan"):
                if judul and isi:
                    execute_query("INSERT INTO pengumuman (tanggal, judul, isi, penulis) VALUES (?, ?, ?, ?)", (tgl, judul, isi, penulis))
                    st.success("✅ Pengumuman berhasil diterbitkan!")
                    st.rerun()

    df_p = get_df("SELECT * FROM pengumuman ORDER BY id DESC")
    
    if not df_p.empty:
        col_c1, col_c2 = st.columns([4, 1])
        search_p = col_c1.text_input("🔍 Ketik Kata Kunci Pengumuman (Judul, Isi, Penulis):", key="search_pengumuman_input")
        btn_cari_p = col_c2.button("🔎 Cari Info", key="btn_p_search")

        df_p_filtered = df_p.copy()
        if search_p.strip() != "":
            df_p_filtered = df_p[
                df_p['judul'].str.contains(search_p, case=False, na=False) |
                df_p['isi'].str.contains(search_p, case=False, na=False) |
                df_p['penulis'].str.contains(search_p, case=False, na=False)
            ]
            st.caption(f"Ditemukan **{len(df_p_filtered)}** pengumuman.")

        st.dataframe(df_p_filtered, use_container_width=True)

        st.subheader("✏️ Ubah / 🗑️ Hapus Pengumuman")
        list_p_opts = df_p_filtered['id'].tolist() if not df_p_filtered.empty else df_p['id'].tolist()
        id_h = st.selectbox("Pilih ID Pengumuman:", list_p_opts, format_func=lambda x: f"ID: {x} - {df_p[df_p['id']==x]['judul'].values[0]}")
        row_curr = df_p[df_p['id'] == id_h].iloc[0]

        with st.form("f_edit_pengumuman"):
            e_judul = st.text_input("Judul Pengumuman", value=row_curr['judul'])
            e_isi = st.text_area("Isi Pengumuman", value=row_curr['isi'])
            e_penulis = st.text_input("Penulis", value=row_curr['penulis'])
            
            c_u1, c_u2 = st.columns(2)
            btn_update = c_u1.form_submit_button("✏️ Simpan Perubahan")
            
            if btn_update:
                execute_query("UPDATE pengumuman SET judul=?, isi=?, penulis=? WHERE id=?", (e_judul, e_isi, e_penulis, id_h))
                st.success("✅ Pengumuman diperbarui!")
                st.rerun()

        if st.button("🗑️ Hapus Pengumuman Ini"):
            execute_query("DELETE FROM pengumuman WHERE id=?", (id_h,))
            st.success("✅ Pengumuman terhapus!")
            st.rerun()
    else:
        st.info("Belum ada data pengumuman.")

elif menu == "👥 Data Penduduk":
    st.title("👥 Kelola Data Penduduk")
    st.divider()

    with st.expander("➕ Tambah Data Penduduk Baru"):
        with st.form("f_penduduk", clear_on_submit=True):
            c1, c2 = st.columns(2)
            nik_p = c1.text_input("NIK (16 Digit)", max_chars=16)
            nama_p = c1.text_input("Nama Lengkap")
            jk_p = c1.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])
            dusun_p = c2.text_input("Dusun")
            rt_p = c2.text_input("RT / RW")
            kerja_p = c2.text_input("Pekerjaan")
            if st.form_submit_button("Simpan Data Penduduk"):
                if not is_valid_nik(nik_p):
                    st.error("❌ NIK tidak valid! NIK harus berupa 16 digit angka.")
                else:
                    execute_query("INSERT INTO penduduk (nik, nama, jenis_kelamin, dusun, pekerjaan, rt_rw) VALUES (?, ?, ?, ?, ?, ?)", (nik_p, nama_p, jk_p, dusun_p, kerja_p, rt_p))
                    st.success("✅ Penduduk Berhasil Ditambahkan!")
                    st.rerun()

    df_pen = get_df("SELECT * FROM penduduk")

    if not df_pen.empty:
        st.subheader("🔍 Cari & Saring Data Penduduk")
        col_c1, col_c2 = st.columns([4, 1])
        admin_search = col_c1.text_input("Ketik Nama, NIK, Dusun, atau Pekerjaan:", key="admin_search_input")
        btn_cari_adm_p = col_c2.button("🔎 Cari Penduduk", key="btn_admin_p_search")

        df_pen_filtered = df_pen.copy()
        if admin_search.strip() != "":
            df_pen_filtered = df_pen[
                df_pen['nama'].str.contains(admin_search, case=False, na=False) |
                df_pen['nik'].str.contains(admin_search, case=False, na=False) |
                df_pen['dusun'].str.contains(admin_search, case=False, na=False) |
                df_pen['pekerjaan'].str.contains(admin_search, case=False, na=False)
            ]
            st.caption(f"Ditemukan **{len(df_pen_filtered)}** dari total **{len(df_pen)}** data penduduk.")

        st.dataframe(df_pen_filtered, use_container_width=True)

        st.divider()
        st.subheader("✏️ Ubah / 🗑️ Hapus Data Penduduk")
        
        list_pilihan = df_pen_filtered['id'].tolist() if not df_pen_filtered.empty else df_pen['id'].tolist()
        
        id_p_sel = st.selectbox(
            "Pilih Penduduk untuk Diubah/Dihapus:",
            list_pilihan,
            format_func=lambda x: f"ID: {x} - {df_pen[df_pen['id']==x]['nama'].values[0]} (NIK: {df_pen[df_pen['id']==x]['nik'].values[0]})"
        )
        p_data = df_pen[df_pen['id'] == id_p_sel].iloc[0]

        with st.form("f_edit_penduduk"):
            ce1, ce2 = st.columns(2)
            u_nik = ce1.text_input("NIK (16 Digit)", value=p_data['nik'], max_chars=16)
            u_nama = ce1.text_input("Nama Lengkap", value=p_data['nama'])
            u_jk = ce1.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"], index=0 if p_data['jenis_kelamin']=="Laki-laki" else 1)
            u_dusun = ce2.text_input("Dusun", value=p_data['dusun'])
            u_rt = ce2.text_input("RT / RW", value=p_data['rt_rw'])
            u_kerja = ce2.text_input("Pekerjaan", value=p_data['pekerjaan'])
            
            if st.form_submit_button("✏️ Simpan Perubahan Penduduk"):
                if not is_valid_nik(u_nik):
                    st.error("❌ NIK tidak valid! NIK harus berupa 16 digit angka.")
                else:
                    execute_query("UPDATE penduduk SET nik=?, nama=?, jenis_kelamin=?, dusun=?, pekerjaan=?, rt_rw=? WHERE id=?", (u_nik, u_nama, u_jk, u_dusun, u_kerja, u_rt, id_p_sel))
                    st.success("✅ Data Penduduk Diperbarui!")
                    st.rerun()

        if st.button("🗑️ Hapus Data Penduduk Ini"):
            execute_query("DELETE FROM penduduk WHERE id=?", (id_p_sel,))
            st.success("✅ Data Penduduk Dihapus!")
            st.rerun()
    else:
        st.info("Belum ada data penduduk di database.")

elif menu == "🩺 Kelola Bantuan & Stunting":
    st.title("🩺 Pengelolaan Bantuan Desa & Stunting")
    st.divider()

    t_b1, t_b2 = st.tabs(["📦 Data Bantuan Desa", "👶 Data Stunting"])

    with t_b1:
        with st.expander("➕ Tambah Data Penerima Bantuan"):
            with st.form("f_bantuan", clear_on_submit=True):
                col_b1, col_b2 = st.columns(2)
                b_nik = col_b1.text_input("NIK Penerima (16 Digit)", max_chars=16)
                b_nama = col_b1.text_input("Nama Penerima")
                b_jenis = col_b2.selectbox("Jenis Bantuan", [
                    "Bantuan Alat Pertanian",
                    "Bantuan Rumah Tidak Layak Huni (RTLH)",
                    "Bantuan Bibit & Pupuk",
                    "BLT Dana Desa",
                    "Bantuan Sembako",
                    "Bantuan Usaha UMKM",
                    "Lain-lain"
                ])
                b_status = col_b2.selectbox("Status Penyaluran", ["Tersalurkan", "Proses Verifikasi", "Pending"])
                b_tahun = col_b1.text_input("Tahun Perolehan", value="2026")
                b_rincian = st.text_area("Rincian Bantuan / Keterangan")
                
                if st.form_submit_button("Simpan Data Bantuan"):
                    if not is_valid_nik(b_nik):
                        st.error("❌ NIK tidak valid! NIK harus berupa 16 digit angka.")
                    else:
                        execute_query(
                            "INSERT INTO bantuan (nik, nama_penerima, jenis_bantuan, rincian_bantuan, status_penyaluran, tahun_perolehan) VALUES (?, ?, ?, ?, ?, ?)",
                            (b_nik, b_nama, b_jenis, b_rincian, b_status, b_tahun)
                        )
                        st.success("✅ Data Bantuan Disimpan!")
                        st.rerun()

        df_bantuan = get_df("SELECT * FROM bantuan")
        
        if not df_bantuan.empty:
            col_c1, col_c2 = st.columns([4, 1])
            search_b = col_c1.text_input("🔍 Cari Data Bantuan (Nama, NIK, Jenis):", key="search_bantuan_input")
            btn_cari_b = col_c2.button("🔎 Cari Bantuan", key="btn_bantuan_search")

            df_b_filtered = df_bantuan.copy()
            if search_b.strip() != "":
                df_b_filtered = df_bantuan[
                    df_bantuan['nama_penerima'].str.contains(search_b, case=False, na=False) |
                    df_bantuan['nik'].str.contains(search_b, case=False, na=False) |
                    df_bantuan['jenis_bantuan'].str.contains(search_b, case=False, na=False)
                ]
                st.caption(f"Ditemukan **{len(df_b_filtered)}** data bantuan.")

            st.dataframe(df_b_filtered, use_container_width=True)

            st.subheader("✏️ Ubah / 🗑️ Hapus Data Bantuan")
            list_b_opts = df_b_filtered['id'].tolist() if not df_b_filtered.empty else df_bantuan['id'].tolist()
            id_b_sel = st.selectbox("Pilih ID Bantuan:", list_b_opts, format_func=lambda x: f"ID: {x} - {df_bantuan[df_bantuan['id']==x]['nama_penerima'].values[0]}")
            b_row = df_bantuan[df_bantuan['id'] == id_b_sel].iloc[0]

            with st.form("f_edit_bantuan"):
                eb_c1, eb_c2 = st.columns(2)
                eb_nik = eb_c1.text_input("NIK Penerima (16 Digit)", value=b_row['nik'], max_chars=16)
                eb_nama = eb_c1.text_input("Nama Penerima", value=b_row['nama_penerima'])
                
                options_j = ["Bantuan Alat Pertanian", "Bantuan Rumah Tidak Layak Huni (RTLH)", "Bantuan Bibit & Pupuk", "BLT Dana Desa", "Bantuan Sembako", "Bantuan Usaha UMKM", "Lain-lain"]
                idx_j = options_j.index(b_row['jenis_bantuan']) if b_row['jenis_bantuan'] in options_j else 0
                eb_jenis = eb_c2.selectbox("Jenis Bantuan", options_j, index=idx_j)
                
                options_s = ["Tersalurkan", "Proses Verifikasi", "Pending"]
                idx_s = options_s.index(b_row['status_penyaluran']) if b_row['status_penyaluran'] in options_s else 0
                eb_status = eb_c2.selectbox("Status Penyaluran", options_s, index=idx_s)
                
                eb_tahun = eb_c1.text_input("Tahun Perolehan", value=str(b_row['tahun_perolehan']) if b_row['tahun_perolehan'] else "2026")
                eb_rincian = st.text_area("Rincian Bantuan", value=b_row['rincian_bantuan'])

                if st.form_submit_button("✏️ Simpan Perubahan Bantuan"):
                    if not is_valid_nik(eb_nik):
                        st.error("❌ NIK tidak valid! NIK harus berupa 16 digit angka.")
                    else:
                        execute_query("UPDATE bantuan SET nik=?, nama_penerima=?, jenis_bantuan=?, rincian_bantuan=?, status_penyaluran=?, tahun_perolehan=? WHERE id=?", (eb_nik, eb_nama, eb_jenis, eb_rincian, eb_status, eb_tahun, id_b_sel))
                        st.success("✅ Data Bantuan Diperbarui!")
                        st.rerun()

            if st.button("🗑️ Hapus Data Bantuan Ini"):
                execute_query("DELETE FROM bantuan WHERE id=?", (id_b_sel,))
                st.success("✅ Data Bantuan Dihapus!")
                st.rerun()
        else:
            st.info("Belum ada data penerima bantuan.")

    with t_b2:
        with st.expander("➕ Tambah Pemantauan Stunting"):
            with st.form("f_stunting", clear_on_submit=True):
                s_balita = st.text_input("Nama Balita")
                s_ortu = st.text_input("Nama Orang Tua")
                s_usia = st.number_input("Usia (Bulan)", min_value=0, value=12)
                s_tb = st.number_input("Tinggi Badan (cm)", value=70.0)
                s_bb = st.number_input("Berat Badan (kg)", value=8.5)
                s_status = st.selectbox("Status Gizi", ["Normal", "Beresiko Stunting", "Stunting", "Gizi Kurang"])
                s_tahun = st.text_input("Tahun Perolehan", value="2026")
                
                if st.form_submit_button("Simpan Data Stunting"):
                    execute_query("INSERT INTO stunting (nama_balita, nama_ortu, usia_bulan, tinggi_badan, berat_badan, status, tahun_perolehan) VALUES (?, ?, ?, ?, ?, ?, ?)", (s_balita, s_ortu, s_usia, s_tb, s_bb, s_status, s_tahun))
                    st.success("✅ Data Stunting Disimpan!")
                    st.rerun()
        
        df_st = get_df("SELECT * FROM stunting")
        
        if not df_st.empty:
            col_c1, col_c2 = st.columns([4, 1])
            search_st = col_c1.text_input("🔍 Cari Data Stunting (Balita, Ortu, Status):", key="search_stunting_input")
            btn_cari_st = col_c2.button("🔎 Cari Stunting", key="btn_stunting_search")

            df_st_filtered = df_st.copy()
            if search_st.strip() != "":
                df_st_filtered = df_st[
                    df_st['nama_balita'].str.contains(search_st, case=False, na=False) |
                    df_st['nama_ortu'].str.contains(search_st, case=False, na=False) |
                    df_st['status'].str.contains(search_st, case=False, na=False)
                ]
                st.caption(f"Ditemukan **{len(df_st_filtered)}** data balita stunting.")

            st.dataframe(df_st_filtered, use_container_width=True)

            st.subheader("✏️ Ubah / 🗑️ Hapus Data Stunting")
            list_st_opts = df_st_filtered['id'].tolist() if not df_st_filtered.empty else df_st['id'].tolist()
            id_st_sel = st.selectbox("Pilih ID Stunting:", list_st_opts, format_func=lambda x: f"ID: {x} - Balita: {df_st[df_st['id']==x]['nama_balita'].values[0]}")
            st_row = df_st[df_st['id'] == id_st_sel].iloc[0]

            with st.form("f_edit_stunting"):
                es_balita = st.text_input("Nama Balita", value=st_row['nama_balita'])
                es_ortu = st.text_input("Nama Orang Tua", value=st_row['nama_ortu'])
                es_usia = st.number_input("Usia (Bulan)", value=int(st_row['usia_bulan']))
                es_tb = st.number_input("Tinggi Badan (cm)", value=float(st_row['tinggi_badan']))
                es_bb = st.number_input("Berat Badan (kg)", value=float(st_row['berat_badan']))
                
                st_opts = ["Normal", "Beresiko Stunting", "Stunting", "Gizi Kurang"]
                idx_st = st_opts.index(st_row['status']) if st_row['status'] in st_opts else 0
                es_status = st.selectbox("Status Gizi", st_opts, index=idx_st)
                es_tahun = st.text_input("Tahun Perolehan", value=str(st_row['tahun_perolehan']) if st_row['tahun_perolehan'] else "2026")

                if st.form_submit_button("✏️ Simpan Perubahan Stunting"):
                    execute_query("UPDATE stunting SET nama_balita=?, nama_ortu=?, usia_bulan=?, tinggi_badan=?, berat_badan=?, status=?, tahun_perolehan=? WHERE id=?", (es_balita, es_ortu, es_usia, es_tb, es_bb, es_status, es_tahun, id_st_sel))
                    st.success("✅ Data Stunting Diperbarui!")
                    st.rerun()

            if st.button("🗑️ Hapus Data Stunting Ini"):
                execute_query("DELETE FROM stunting WHERE id=?", (id_st_sel,))
                st.success("✅ Data Stunting Dihapus!")
                st.rerun()
        else:
            st.info("Belum ada data stunting.")

elif menu == "💬 Tanggapi Aspirasi":
    st.title("💬 Kelola Aspirasi Warga")
    st.divider()

    df_k = get_df("SELECT * FROM kritik_saran ORDER BY id DESC")
    
    if not df_k.empty:
        col_c1, col_c2 = st.columns([4, 1])
        search_k = col_c1.text_input("🔍 Cari Aspirasi Warga (Nama, Kategori, Pesan):", key="search_aspirasi_input")
        btn_cari_k = col_c2.button("🔎 Cari Aspirasi", key="btn_aspirasi_search")

        df_k_filtered = df_k.copy()
        if search_k.strip() != "":
            df_k_filtered = df_k[
                df_k['nama'].str.contains(search_k, case=False, na=False) |
                df_k['kategori'].str.contains(search_k, case=False, na=False) |
                df_k['pesan'].str.contains(search_k, case=False, na=False)
            ]
            st.caption(f"Ditemukan **{len(df_k_filtered)}** aspirasi.")

        st.dataframe(df_k_filtered, use_container_width=True)

        st.subheader("Beri Tanggapan / Jawaban & Kelola Aspirasi")
        list_k_opts = df_k_filtered['id'].tolist() if not df_k_filtered.empty else df_k['id'].tolist()
        id_k = st.selectbox("Pilih ID Aspirasi:", list_k_opts, format_func=lambda x: f"ID: {x} - {df_k[df_k['id']==x]['nama'].values[0]} ({df_k[df_k['id']==x]['kategori'].values[0]})")
        row_k = df_k[df_k['id'] == id_k].iloc[0]
        
        tanggapan = st.text_area("Tanggapan Resmi Desa", value=row_k['tanggapan'] if row_k['tanggapan'] != 'Belum Ditanggapi' else '')
        
        col_t1, col_t2 = st.columns(2)
        if col_t1.button("💾 Simpan Tanggapan"):
            execute_query("UPDATE kritik_saran SET tanggapan=? WHERE id=?", (tanggapan, id_k))
            st.success("✅ Tanggapan berhasil disimpan!")
            st.rerun()

        if col_t2.button("🗑️ Hapus Aspirasi Ini"):
            execute_query("DELETE FROM kritik_saran WHERE id=?", (id_k,))
            st.success("✅ Aspirasi terhapus!")
            st.rerun()
    else:
        st.info("Belum ada saran atau aspirasi dari warga.")

elif menu == "💰 Kelola Keuangan APBDES":
    st.title("💰 Pengelolaan APBDES")
    st.divider()

    with st.expander("➕ Tambah Pos Anggaran Baru"):
        with st.form("f_apbdes", clear_on_submit=True):
            ap_tahun = st.text_input("Tahun Anggaran", value="2026")
            ap_kat = st.selectbox("Kategori", ["Pendapatan", "Belanja", "Pembiayaan"])
            ap_sub = st.text_input("Nama Sub Pos / Kegiatan")
            ap_jumlah = st.number_input("Jumlah Anggaran (Rp)", min_value=0.0, step=1000000.0)
            if st.form_submit_button("Tambah Postur Anggaran"):
                execute_query("INSERT INTO apbdes (tahun, kategori, sub_kategori, jumlah_anggaran) VALUES (?, ?, ?, ?)", (ap_tahun, ap_kat, ap_sub, ap_jumlah))
                st.success("✅ Pos Anggaran Ditambahkan!")
                st.rerun()

    df_apb = get_df("SELECT * FROM apbdes")

    if not df_apb.empty:
        col_c1, col_c2 = st.columns([4, 1])
        search_apb = col_c1.text_input("🔍 Cari Pos Anggaran (Tahun, Kategori, Sub Pos):", key="search_apb_input")
        btn_cari_apb = col_c2.button("🔎 Cari Pos", key="btn_apb_search")

        df_apb_filtered = df_apb.copy()
        if search_apb.strip() != "":
            df_apb_filtered = df_apb[
                df_apb['tahun'].str.contains(search_apb, case=False, na=False) |
                df_apb['kategori'].str.contains(search_apb, case=False, na=False) |
                df_apb['sub_kategori'].str.contains(search_apb, case=False, na=False)
            ]
            st.caption(f"Ditemukan **{len(df_apb_filtered)}** pos anggaran.")

        st.dataframe(df_apb_filtered, use_container_width=True)

        st.subheader("✏️ Ubah / 🗑️ Hapus Pos Anggaran APBDES")
        list_apb_opts = df_apb_filtered['id'].tolist() if not df_apb_filtered.empty else df_apb['id'].tolist()
        id_apb_sel = st.selectbox("Pilih ID APBDES:", list_apb_opts, format_func=lambda x: f"ID: {x} - {df_apb[df_apb['id']==x]['sub_kategori'].values[0]}")
        ap_row = df_apb[df_apb['id'] == id_apb_sel].iloc[0]

        with st.form("f_edit_apbdes"):
            e_tahun = st.text_input("Tahun Anggaran", value=ap_row['tahun'])
            kat_opts = ["Pendapatan", "Belanja", "Pembiayaan"]
            e_kat = st.selectbox("Kategori", kat_opts, index=kat_opts.index(ap_row['kategori']) if ap_row['kategori'] in kat_opts else 0)
            e_sub = st.text_input("Nama Sub Pos / Kegiatan", value=ap_row['sub_kategori'])
            e_jumlah = st.number_input("Jumlah Anggaran (Rp)", value=float(ap_row['jumlah_anggaran']), step=1000000.0)

            if st.form_submit_button("✏️ Simpan Perubahan APBDES"):
                execute_query("UPDATE apbdes SET tahun=?, kategori=?, sub_kategori=?, jumlah_anggaran=? WHERE id=?", (e_tahun, e_kat, e_sub, e_jumlah, id_apb_sel))
                st.success("✅ Pos Anggaran APBDES Diperbarui!")
                st.rerun()

        if st.button("🗑️ Hapus Pos Anggaran Ini"):
            execute_query("DELETE FROM apbdes WHERE id=?", (id_apb_sel,))
            st.success("✅ Pos Anggaran Dihapus!")
            st.rerun()
    else:
        st.info("Belum ada data anggaran APBDES.")

elif menu == "🏛️ Kelola Aparat & Profil Desa":
    st.title("🏛️ Kelola Aparat & Profil/Lokasi Desa")
    st.divider()

    tab_ap1, tab_ap2 = st.tabs(["👥 Kelola Data Aparat Desa", "📍 Pengaturan Koordinat Peta Desa"])

    with tab_ap1:
        with st.expander("➕ Tambah Aparat Baru"):
            with st.form("f_aparat", clear_on_submit=True):
                nama_a = st.text_input("Nama & Gelar")
                jab_a = st.text_input("Jabatan")
                kat_a = st.selectbox("Kategori", ["Pemerintah Desa", "Sekretariat", "Kepala Seksi", "Kepala Urusan", "Kepala Dusun", "RW", "RT"])
                kontak_a = st.text_input("No HP/WA")
                foto_file = st.file_uploader("Unggah Foto Profil Aparat", type=["jpg", "jpeg", "png"])
                
                if st.form_submit_button("Simpan Aparat"):
                    foto_b64 = convert_image_to_base64(foto_file) if foto_file else ""
                    execute_query("INSERT INTO pemerintah (nama, jabatan, kategori, kontak, foto_url) VALUES (?, ?, ?, ?, ?)", (nama_a, jab_a, kat_a, kontak_a, foto_b64))
                    st.success("✅ Aparat Desa Disimpan!")
                    st.rerun()

        df_aparat = get_df("SELECT * FROM pemerintah")

        if not df_aparat.empty:
            col_c1, col_c2 = st.columns([4, 1])
            search_ap = col_c1.text_input("🔍 Cari Aparat Desa (Nama, Jabatan, Kategori):", key="search_aparat_input")
            btn_cari_ap = col_c2.button("🔎 Cari Aparat", key="btn_aparat_search")

            df_ap_filtered = df_aparat.copy()
            if search_ap.strip() != "":
                df_ap_filtered = df_aparat[
                    df_aparat['nama'].str.contains(search_ap, case=False, na=False) |
                    df_aparat['jabatan'].str.contains(search_ap, case=False, na=False) |
                    df_aparat['kategori'].str.contains(search_ap, case=False, na=False)
                ]
                st.caption(f"Ditemukan **{len(df_ap_filtered)}** aparat desa.")

            st.dataframe(df_ap_filtered, use_container_width=True)

            st.subheader("✏️ Ubah / 🗑️ Hapus Data Aparat Desa")
            list_ap_opts = df_ap_filtered['id'].tolist() if not df_ap_filtered.empty else df_aparat['id'].tolist()
            id_ap_sel = st.selectbox("Pilih Aparat:", list_ap_opts, format_func=lambda x: f"ID: {x} - {df_aparat[df_aparat['id']==x]['nama'].values[0]}")
            ap_row = df_aparat[df_aparat['id'] == id_ap_sel].iloc[0]

            with st.form("f_edit_aparat"):
                ea_nama = st.text_input("Nama & Gelar", value=ap_row['nama'])
                ea_jab = st.text_input("Jabatan", value=ap_row['jabatan'])
                kat_opts = ["Pemerintah Desa", "Sekretariat", "Kepala Seksi", "Kepala Urusan", "Kepala Dusun", "RW", "RT"]
                ea_kat = st.selectbox("Kategori", kat_opts, index=kat_opts.index(ap_row['kategori']) if ap_row['kategori'] in kat_opts else 0)
                ea_kontak = st.text_input("No HP/WA", value=ap_row['kontak'])
                
                if ap_row['foto_url']:
                    st.caption("Foto Saat Ini:")
                    st.image(ap_row['foto_url'], width=100)
                
                ea_foto_file = st.file_uploader("Unggah Foto Baru (Biarkan kosong jika tidak diubah)", type=["jpg", "jpeg", "png"])

                if st.form_submit_button("✏️ Simpan Perubahan Aparat"):
                    if ea_foto_file is not None:
                        foto_b64_new = convert_image_to_base64(ea_foto_file)
                    else:
                        foto_b64_new = ap_row['foto_url']
                        
                    execute_query("UPDATE pemerintah SET nama=?, jabatan=?, kategori=?, kontak=?, foto_url=? WHERE id=?", (ea_nama, ea_jab, ea_kat, ea_kontak, foto_b64_new, id_ap_sel))
                    st.success("✅ Data Aparat Diperbarui!")
                    st.rerun()

            if st.button("🗑️ Hapus Data Aparat Ini"):
                execute_query("DELETE FROM pemerintah WHERE id=?", (id_ap_sel,))
                st.success("✅ Data Aparat Dihapus!")
                st.rerun()
        else:
            st.info("Belum ada data aparat desa.")

    with tab_ap2:
        st.subheader("⚙️ Atur Koordinat Peta Lokasi Desa")
        df_prof_edit = get_df("SELECT * FROM profil_desa LIMIT 1")
        
        if not df_prof_edit.empty:
            p_curr = df_prof_edit.iloc[0]
            with st.form("f_edit_profil_desa"):
                ep_nama = st.text_input("Nama Desa", value=p_curr['nama_desa'])
                ep_alamat = st.text_area("Alamat Lengkap Kantor Desa", value=p_curr['alamat'])
                col_lat, col_lon = st.columns(2)
                ep_lat = col_lat.number_input("Latitude", value=float(p_curr['latitude']), format="%.6f")
                ep_lon = col_lon.number_input("Longitude", value=float(p_curr['longitude']), format="%.6f")

                if st.form_submit_button("💾 Simpan Pengaturan Lokasi"):
                    execute_query(
                        "UPDATE profil_desa SET nama_desa=?, latitude=?, longitude=?, alamat=? WHERE id=?",
                        (ep_nama, ep_lat, ep_lon, ep_alamat, int(p_curr['id']))
                    )
                    st.success("✅ Koordinat & Lokasi Desa Berhasil Diperbarui!")
                    st.rerun()

elif menu == "👤 Manajemen Akun User":
    st.title("👤 Pengelolaan Akun Pengguna")
    st.divider()

    with st.expander("➕ Buat Akun Baru"):
        with st.form("f_user", clear_on_submit=True):
            u_user = st.text_input("Username")
            u_pass = st.text_input("Password", type="password")
            u_nama = st.text_input("Nama Lengkap / Jabatan")
            u_role = st.selectbox("Akses", ["Admin Desa", "Operator"])
            if st.form_submit_button("Buat User"):
                execute_query("INSERT INTO users (username, password, nama, role) VALUES (?, ?, ?, ?)", (u_user, u_pass, u_nama, u_role))
                st.success("✅ Akun Baru Berhasil Dibuat!")
                st.rerun()

    df_user = get_df("SELECT id, username, nama, role FROM users")

    if not df_user.empty:
        col_c1, col_c2 = st.columns([4, 1])
        search_u = col_c1.text_input("🔍 Cari Akun Pengguna (Username, Nama):", key="search_user_input")
        btn_cari_u = col_c2.button("🔎 Cari User", key="btn_user_search")

        df_u_filtered = df_user.copy()
        if search_u.strip() != "":
            df_u_filtered = df_user[
                df_user['username'].str.contains(search_u, case=False, na=False) |
                df_user['nama'].str.contains(search_u, case=False, na=False)
            ]
            st.caption(f"Ditemukan **{len(df_u_filtered)}** akun pengguna.")

        st.dataframe(df_u_filtered, use_container_width=True)

        st.subheader("✏️ Ubah / 🗑️ Hapus Akun Pengguna")
        list_u_opts = df_u_filtered['id'].tolist() if not df_u_filtered.empty else df_user['id'].tolist()
        id_u_sel = st.selectbox("Pilih Akun User:", list_u_opts, format_func=lambda x: f"ID: {x} - {df_user[df_user['id']==x]['username'].values[0]} ({df_user[df_user['id']==x]['nama'].values[0]})")
        u_row = df_user[df_user['id'] == id_u_sel].iloc[0]

        with st.form("f_edit_user"):
            eu_user = st.text_input("Username", value=u_row['username'])
            eu_pass = st.text_input("Password Baru (Kosongkan jika tidak diubah)", type="password")
            eu_nama = st.text_input("Nama Lengkap / Jabatan", value=u_row['nama'])
            r_opts = ["Admin Desa", "Operator"]
            eu_role = st.selectbox("Akses Level", r_opts, index=r_opts.index(u_row['role']) if u_row['role'] in r_opts else 0)

            if st.form_submit_button("✏️ Simpan Perubahan User"):
                if eu_pass.strip() != "":
                    execute_query("UPDATE users SET username=?, password=?, nama=?, role=? WHERE id=?", (eu_user, eu_pass, eu_nama, eu_role, id_u_sel))
                else:
                    execute_query("UPDATE users SET username=?, nama=?, role=? WHERE id=?", (eu_user, eu_nama, eu_role, id_u_sel))
                st.success("✅ Akun User Diperbarui!")
                st.rerun()

        if st.button("🗑️ Hapus Akun User Ini"):
            execute_query("DELETE FROM users WHERE id=?", (id_u_sel,))
            st.success("✅ Akun User Dihapus!")
            st.rerun()
    else:
        st.info("Belum ada data pengguna.")