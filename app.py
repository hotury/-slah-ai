import streamlit as st
import pandas as pd
from biovalent_engine import IslahAI

st.set_page_config(page_title="Biovalent Islah AI v2", layout="wide")

if 'ai_engine' not in st.session_state:
    st.session_state.ai_engine = IslahAI()

st.title("🧬 Islah AI: Akıllı Genetik Analiz & Saha Tahmini")

# --- SOL PANEL: DOSYA VE EĞİTİM ---
with st.sidebar:
    st.header("📂 Veri Girişi")
    # Dosya Yükleme Alanı (DNA veya Amino Asit dosyası buraya yüklenebilir)
    uploaded_file = st.file_uploader("Genetik/Protein Dosyası Yükle", type=["fasta", "txt"])
    
    st.markdown("---")
    st.header("🤖 Saha Performansı")
    # AI Eğitme Kısmı
    field_data = st.file_uploader("Saha Verisi (CSV) Yükle", type="csv")
    if field_data is not None:
        df_field = pd.read_csv(field_data)
        if st.button("🚀 AI Modeli Eğit"):
            success = st.session_state.ai_engine.train_field_model(df_field)
            if success:
                st.success("AI Sizin Sahanız İçin Eğitildi!")
            else:
                st.error("Veri formatı hatalı (Protein_Seq ve Saha_Sonuc sütunlarını kontrol edin).")

# --- ANA PANEL ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("🛠️ Analiz Ayarları")
    plant_choice = st.selectbox("Bitki Türü:", ["Domates", "Biber", "Hıyar", "Kabak", "Karpuz", "Kavun", "Patlıcan"])
    input_mode = st.radio("Yüklenen Veri Tipi:", ["DNA / Genetik Harita", "Amino Asit (Protein)"])
    
    # Veri Önizleme
    raw_data = ""
    if uploaded_file:
        raw_data = uploaded_file.read().decode("utf-8")
        st.success("Dosya Hazır!")
    else:
        raw_data = st.text_area("Veya Sekansı Manuel Girin:", height=200)

    if st.button("🔍 Analizi Başlat"):
        clean_data = st.session_state.ai_engine.process_genome_file(raw_data)
        
        if input_mode == "DNA / Genetik Harita":
            final_seq = st.session_state.ai_engine.translate_dna(clean_data)
        else:
            final_seq = clean_data
            
        if final_seq:
            res_stats, res_metrics = st.session_state.ai_engine.predict_all_parameters(final_seq, plant_choice)
            st.session_state.results = res_stats
            st.session_state.metrics = res_metrics
            st.session_state.active_seq = final_seq
        else:
            st.error("Veri işlenirken bir hata oluştu.")

with col2:
    st.subheader("📊 Analiz Sonuçları")
    if 'results' in st.session_state:
        res = st.session_state.results
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Brix (Tat)", res["Brix"])
        c2.metric("Verim", res["Verim"])
        c3.metric("Çimlenme", f"%{res['Cimlenme']}")
        
        c4, c5, c6 = st.columns(3)
        c4.metric("Hastalık Dayanımı", f"%{res['Hastalik']}")
        c5.metric("Raf Ömrü", f"{res['RafOmru']} Gün")
        c6.metric("Vigor", res["Vigor"])

        st.warning(f"🌡️ Stres Toleransı: {res['Stres']}/10")
        
        with st.expander("🔬 Amino Asit Dağılım Grafiği"):
            st.bar_chart(st.session_state.metrics)
