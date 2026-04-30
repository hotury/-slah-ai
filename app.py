import streamlit as st
import numpy as np
import pandas as pd
from biovalent_algo import BiovalentEngine

st.set_page_config(page_title="Biovalent AI | Protein-Aware Breeding", layout="wide")

if 'engine' not in st.session_state:
    st.session_state.engine = BiovalentEngine()

st.title("🧬 Biovalent AI: Amino Asit Tabanlı Islah Analizi")
st.markdown("---")

# 1. ÜRÜN SEÇİMİ (Biyolojik Anayasa)
col_a, col_b = st.columns(2)
product = col_a.selectbox("Çalışılacak Ürün:", ["Domates (Solanum lycopersicum)", "Biber (Capsicum annuum)"])
st.info(f"Seçilen ürün için **{product}** genetik referans kütüphanesi yüklendi.")

# 2. GENETİK GİRDİ
st.subheader("🔬 Aday Tohum Analizi")
raw_dna = st.text_input("SNP Dizilimi (20 Adet):", "2,0,1,0,2,1,0,1,0,0,2,1,0,0,2,1,0,0,2,1")

if st.button("Hücre Seviyesinde Analiz Et"):
    dna_vec = np.array([int(x.strip()) for x in raw_dna.split(",")])
    res = st.session_state.engine.predict_hybrid(dna_vec)
    
    # SONUÇ GÖSTERİMİ
    c1, c2, c3 = st.columns(3)
    c1.metric("Tahmini Brix", f"{res['field']['brix']}")
    c2.metric("Tahmini Verim", f"{res['field']['yield']} Ton/Ha")
    c3.metric("Tolerans Katsayısı", f"{round(res['theory']['tolerance_score'], 2)}")

    # 🧬 BURSA GEN YORUMLAMA (Hücre Analizi Bölümü)
    st.subheader("📂 Bursa Gen Yorumlama Raporu (AA Değişim Analizi)")
    
    for report in res['theory']['protein_reports']:
        with st.expander(f"📌 Gen: {report['gene']} | Protein: {report['protein']}"):
            st.write(f"**Amino Asit Değişimi:** `{report['change']}`")
            st.write(f"**Biyokimyasal Etki:** Bu değişim proteinin üç boyutlu yapısında stabiliteyi değiştirerek fenotipte **{report['impact']:.2f}** birimlik bir fark yaratmaktadır.")
            if "Tolerance" in report['protein'] or report['impact'] > 0.3:
                st.success("Bu değişim bitkinin çevresel stres direncini pozitif yönde etkiler.")

# 3. AI EĞİTİM (Gelecek İçin)
with st.sidebar:
    st.header("⚙️ AI Kalibrasyonu")
    st.write("Saha veriniz varsa buraya yükleyerek biyokimyasal modeli tarlanıza özel eğitebilirsiniz.")
    uploaded = st.file_uploader("Saha Verisi (CSV)", type="csv")
    if uploaded:
        df = pd.read_csv(uploaded)
        if st.button("Modeli Eğit"):
            st.session_state.engine.train_field_ai(df)
            st.success("AI, Amino Asit verilerini sahanızla eşleştirdi!")
