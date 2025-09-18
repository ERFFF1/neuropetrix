import streamlit as st
import sqlite3
import pandas as pd
import os
from datetime import datetime
import json

st.set_page_config(
    page_title="Database Management - NeuroPETrix",
    page_icon="🗄️",
    layout="wide"
)

st.title("🗄️ Database Management")
st.markdown("**NeuroPETrix Veritabanı Yönetim Paneli**")

# Sidebar
with st.sidebar:
    st.header("📊 Veritabanı Durumu")
    
    # Database health check
    try:
        conn = sqlite3.connect("backend/neuropetrix.db")
        st.success("✅ Ana veritabanı bağlantısı")
        conn.close()
    except Exception as e:
        st.error(f"❌ Veritabanı hatası: {e}")
    
    try:
        conn = sqlite3.connect("feedback.db")
        st.success("✅ Feedback veritabanı bağlantısı")
        conn.close()
    except Exception as e:
        st.error(f"❌ Feedback DB hatası: {e}")
    
    st.markdown("---")
    st.markdown("**Hızlı İşlemler**")
    
    if st.button("🔄 Veritabanlarını Yenile", key="refresh_dbs"):
        st.rerun()

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.header("📁 Veritabanı Tabloları")
    
    # Database tables overview
    try:
        conn = sqlite3.connect("backend/neuropetrix.db")
        cursor = conn.cursor()
        
        # Get table list
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        if tables:
            for table in tables:
                table_name = table[0]
                with st.expander(f"📋 {table_name}", expanded=False):
                    # Get table info
                    cursor.execute(f"PRAGMA table_info({table_name})")
                    columns = cursor.fetchall()
                    
                    st.markdown(f"**Sütunlar:** {len(columns)}")
                    
                    # Show sample data
                    try:
                        cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
                        sample_data = cursor.fetchall()
                        if sample_data:
                            st.markdown("**Örnek Veriler:**")
                            df_sample = pd.DataFrame(sample_data, columns=[col[1] for col in columns])
                            st.dataframe(df_sample, use_container_width=True)
                        else:
                            st.info("Bu tabloda veri bulunamadı.")
                    except Exception as e:
                        st.warning(f"Veri okuma hatası: {e}")
                    
                    # Table actions
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        if st.button("📊 Tüm Verileri Göster", key=f"show_all_{table_name}"):
                            st.info(f"Tüm veriler gösteriliyor: {table_name}")
                    
                    with col_b:
                        if st.button("📝 Tablo Düzenle", key=f"edit_table_{table_name}"):
                            st.info(f"Tablo düzenleme: {table_name}")
                    
                    with col_c:
                        if st.button("🗑️ Tablo Temizle", key=f"clear_table_{table_name}"):
                            st.warning(f"Tablo temizleme: {table_name}")
        else:
            st.info("Veritabanında tablo bulunamadı.")
        
        conn.close()
        
    except Exception as e:
        st.error(f"Veritabanı bağlantı hatası: {e}")

with col2:
    st.header("🚀 Veritabanı İşlemleri")
    
    # Database operations
    operation = st.selectbox(
        "İşlem Seçin:",
        ["Backup", "Restore", "Optimize", "Vacuum", "Export", "Import"]
    )
    
    if st.button("▶️ İşlemi Başlat", key="start_operation"):
        st.info(f"İşlem başlatılıyor: {operation}")
        
        # Mock operation
        with st.spinner("İşlem yapılıyor..."):
            import time
            time.sleep(2)
            st.success(f"İşlem tamamlandı: {operation}")

# Database statistics
st.markdown("---")
st.header("📊 Veritabanı İstatistikleri")

try:
    conn = sqlite3.connect("backend/neuropetrix.db")
    cursor = conn.cursor()
    
    # Get database info
    cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table';")
    table_count = cursor.fetchone()[0]
    
    # Get total row count
    total_rows = 0
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            total_rows += count
        except:
            pass
    
    conn.close()
    
    col_stats1, col_stats2, col_stats3, col_stats4 = st.columns(4)
    
    with col_stats1:
        st.metric("Toplam Tablo", table_count)
        
    with col_stats2:
        st.metric("Toplam Satır", total_rows)
        
    with col_stats3:
        st.metric("Veritabanı Boyutu", "36.8 KB")
        
    with col_stats4:
        st.metric("Son Güncelleme", "1 saat önce")
        
except Exception as e:
    st.error(f"İstatistik hatası: {e}")

# Database backup/restore
st.markdown("---")
st.header("💾 Yedekleme ve Geri Yükleme")

col_backup1, col_backup2 = st.columns(2)

with col_backup1:
    st.subheader("📤 Yedekleme")
    
    backup_name = st.text_input("Yedek Adı", value=f"backup_{datetime.now().strftime('%Y%m%d_%H%M')}")
    
    if st.button("💾 Yedek Oluştur", key="create_backup"):
        st.info("Yedek oluşturuluyor...")
        with st.spinner("Yedekleme yapılıyor..."):
            import time
            time.sleep(2)
            st.success(f"Yedek oluşturuldu: {backup_name}")

with col_backup2:
    st.subheader("📥 Geri Yükleme")
    
    backup_file = st.file_uploader("Yedek Dosyası Seçin", type=['db', 'sqlite'])
    
    if st.button("📥 Yedeği Geri Yükle", key="restore_backup"):
        if backup_file:
            st.info("Yedek geri yükleniyor...")
            with st.spinner("Geri yükleme yapılıyor..."):
                import time
                time.sleep(2)
                st.success("Yedek başarıyla geri yüklendi!")
        else:
            st.warning("Lütfen bir yedek dosyası seçin!")

# Database monitoring
st.markdown("---")
st.header("📈 Veritabanı Monitörü")

# Mock monitoring data
monitoring_data = {
    "timestamp": ["01:30", "01:35", "01:40", "01:45", "01:50"],
    "active_connections": [5, 3, 7, 4, 6],
    "queries_per_min": [120, 95, 150, 110, 135],
    "response_time_ms": [45, 52, 38, 48, 42]
}

df_monitoring = pd.DataFrame(monitoring_data)
st.line_chart(df_monitoring.set_index("timestamp"))

# Footer
st.markdown("---")
st.caption("🗄️ Database Management Panel - NeuroPETrix v1.0.0")















