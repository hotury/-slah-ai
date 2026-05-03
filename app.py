import streamlit as st
import pandas as pd
from BIYOLOJIK_BEYIN import BioValentBeyin

st.set_page_config(page_title="BioValent Elite", layout="wide")

# Marka Başlığı
st.title("🧬 BioValent")
st.markdown("*Profesyonel Dijital Islah ve Genetik Analiz Platformu*")
st.markdown("---")

if 'beyin' not in st.session_state:
    st.session_state.beyin = BioValentBeyin()

# Yan Panel
with st.sidebar:
    st.header("🏢 Kurumsal Panel")
    st.info("Brix ve Verim tahminlerini aktifleştirmek için saha verilerinizi yükleyerek sistemi eğitiniz.")
    if st.button("Model Eğitimi Başlat"):
        st.warning("Eğitim modülü için lütfen CSV formatında saha verisi yükleyin.")
    st.markdown("---")
    st.caption("BioValent v2.0")

# Ana Ekran
col1, col2 = st.columns([1, 1.3])

with col1:
    st.subheader("📥 Veri Girişi")
    seq_file = st.file_uploader("DNA veya Amino Asit Dosyası:", type=['fasta','txt','dna'])
    
    file_content = ""
    if seq_file:
        file_content = "\n".join([l for l in seq_file.read().decode().splitlines() if not l.startswith(">")])
    
    seq_input = st.text_area("Sekans (DNA/AA):", value=file_content, height=250, placeholder="ATGC... veya MVLS...")
    
    if st.button("🔍 Bilimsel Analizi Çalıştır", type="primary"):
        if len(seq_input) >= 10:
            protein, s_type = st.session_state.beyin.preprocess_sequence(seq_input)
            st.session_state.res = {
                "type": s_type,
                "sci": st.session_state.beyin.calculate_science(protein),
                "dummy": st.session_state.beyin.predict_dummy()
            }
        else:
            st.error("Lütfen geçerli bir sekans girin.")

with col2:
    st.subheader("📊 Analiz Sonuçları")
    if 'res' in st.session_state:
        r = st.session_state.res
        
        if "Error" in r["sci"]:
            st.error(r["sci"]["Error"])
        else:
            st.success(f"Tespit Edilen Format: **{r['type']}**")
            
            # BLOK 1: GERÇEK BİLİM
            st.markdown("#### 🧪 Laboratuvar Parametreleri")
            sci_data = pd.DataFrame(list(r["sci"].items()), columns=["Parametre", "Sonuç"])
            st.table(sci_data)
            
            # BLOK 2: TAHMİNLER (EĞİTİM BEKLEYENLER)
            st.markdown("#### 🎯 Saha Tahminleri")
            c1, c2 = st.columns(2)
            
            # Şık bir "Model Eğit" kutucuğu
            with c1:
                st.metric("Tahmini Brix", r["dummy"])
            with c2:
                st.metric("Tahmini Verim", r["dummy"])
            
            st.info("💡 Not: Brix ve Verim sonuçları, bitkinin yetişeceği çevreye göre değiştiği için sadece firmanıza özel verilerle eğitildikten sonra gösterilir.")

st.markdown("---")
st.caption("© 2026 BioValent Intelligence ")
