import streamlit as st
import pandas as pd
from biovalent_engine import IslahAI

st.set_page_config(page_title="Islah AI v2", layout="wide")

if 'ai_engine' not in st.session_state:
    st.session_state.ai_engine = IslahAI()

st.title("🧬 Islah AI: Genetik Analiz ve Saha Adaptasyonu")

# --- SOL PANEL: GENETİK GİRİŞ VE AI EĞİTİMİ ---
with st.sidebar:
    st.header("🔬 Genetik Veri Girişi")
    # DNA veya Amino Asit dosyası yükleme alanı
    uploaded_file = st.file_uploader("Genetik/Protein Dosyası (.fasta, .txt)", type=["fasta", "txt"])
    
    st.markdown("---")
    st.header("🚜 Saha Verisi & AI Eğitimi")
    # AI Eğitme Kısmı
    field_data = st.file_uploader("Saha Performans Verisi (CSV)", type="csv")
    if field_data is not None:
        df_field = pd.read_csv(field_data)
        # BUTON ADI GÜNCELLENDİ: AI EĞİT
        if st.button("🚀 AI Modeli Eğit"):
            success = st.session_state.ai_engine.train_with_field_data(df_field)
            if success:
                st.success("AI Sizin Sahanız İçin Eğitildi!")
            else:
                st.error("Hata: CSV formatını kontrol edin.")

# --- ANA PANEL ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("⚙️ Analiz Parametreleri")
    plant_choice = st.selectbox("Bitki Türü Seçimi:", ["Domates", "Biber", "Hıyar", "Kabak", "Karpuz", "Kavun", "Patlıcan"])
    input_mode = st.radio("Yüklenen Dosya İçeriği:", ["DNA / Genetik Harita", "Amino Asit (Protein)"])
    
    # Veri Okuma Mantığı
    raw_data = ""
    if uploaded_file:
        raw_data = uploaded_file.read().decode("utf-8")
        st.info("📂 Dosya okundu, analize hazır.")
    else:
        raw_data = st.text_area("Veya Sekansı Buraya Yapıştırın:", height=200)

    if st.button("🔍 Dijital Fenotipi Analiz Et"):
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
            st.error("Veri işleme hatası.")

with col2:
    st.subheader("📊 Tahmini Performans Raporu")
    if 'results' in st.session_state:
        res = st.session_state.results
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Brix (Tat)", res["Brix"])
        c2.metric("Verim", res["Verim"])
        c3.metric("Çimlenme", f"%{res['Cimlenme']}")
        
        c4, c5, c6 = st.columns(3)
        c4.metric("Hastalık Dayanımı", f"%{res['Hastalik']}")
        c5.metric("Raf Ömrü", f"{res['RafOmru']} Gün")
        c6.metric("Vigor (Büyüme)", res["Vigor"])

        st.warning(f"🌡️ Stres Toleransı: {res['Stres']}/10")
        
        if st.session_state.ai_engine.is_trained:
            st.success("🎯 Bu sonuçlar AI tarafından saha verilerinizle kalibre edilmiştir.")
