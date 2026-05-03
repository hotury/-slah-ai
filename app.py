import streamlit as st
import pandas as pd
from BIYOLOJIK_BEYIN import BioValentBeyin

st.set_page_config(page_title="BioValent Elite", layout="wide")

st.title("🧬 BioValent")
st.markdown("*Bilimsel Veriyi Ticari Değere Dönüştüren Islah Platformu*")
st.markdown("---")

# Beyin objesini session state'e kaydet (Veri kaybolmasın)
if 'beyin' not in st.session_state:
    st.session_state.beyin = BioValentBeyin()

# --- YAN PANEL: AI EĞİTİM MERKEZİ ---
with st.sidebar:
    st.header("🧠 Kendi AI'nı Eğit")
    st.write("Firmanıza özel Brix ve Verim tahminleri için saha verilerinizi yükleyin.")
    
    training_file = st.file_uploader("Saha Verisi (CSV Yükle)", type=['csv'])
    
    if training_file is not None:
        try:
            df = pd.read_csv(training_file)
            if st.button("🚀 Modeli Eğit"):
                with st.spinner("Yapay zeka öğreniyor..."):
                    sonuc = st.session_state.beyin.train_custom_model(df)
                    st.success(sonuc)
        except Exception as e:
            st.error(f"Dosya okunamadı: {e}")
    
    st.markdown("---")
    st.caption("BioValent Intelligence v2.0")

# --- ANA EKRAN: SÜTUNLARIN TANIMLANMASI ---
# col1 ve col2 burada tanımlandığı için NameError almayacaksın.
col1, col2 = st.columns([1, 1.3])

with col1:
    st.subheader("📥 Veri Girişi")
    seq_input = st.text_area("DNA veya Amino Asit Sekansı girin:", height=200, placeholder="ATGC... veya MVLS...")
    
    if st.button("🔍 Analizi Başlat", type="primary"):
        if len(seq_input) >= 10:
            protein, s_type = st.session_state.beyin.preprocess_sequence(seq_input)
            st.session_state.res = {
                "type": s_type,
                "protein_raw": protein,
                "sci": st.session_state.beyin.calculate_science(protein),
                "pred": st.session_state.beyin.predict_phenotype(protein)
            }
        else:
            st.error("Lütfen en az 10 karakterlik bir sekans girin.")

with col2:
    st.subheader("📊 Bilimsel & Ticari Analiz")
    if 'res' in st.session_state:
        r = st.session_state.res
        
        if "Error" in r["sci"]:
            st.error(r["sci"]["Error"])
        else:
            st.success(f"Format: {r['type']}")
            
            # Bilimsel ve Ticari Veriler (Expander içinde)
            for param, data in r["sci"].items():
                with st.expander(f"🔹 {param}: {data['val']}", expanded=True):
                    st.write(f"**Açıklama:** {data['desc']}")
                    st.info(f"**Ticari Yorum:** {data['com']}")
            
            st.markdown("---")
            st.markdown("#### 🎯 Saha Tahminleri (Yapay Zeka)")
            
            if st.session_state.beyin.is_trained:
                # Model eğitildiyse tahminleri göster
                c1, c2 = st.columns(2)
                c1.metric("Tahmini Brix", r["pred"]["Brix"])
                c2.metric("Tahmini Verim", f"{r['pred']['Verim']} kg/ton")
            else:
                # Model eğitilmediyse uyarı ver
                st.warning("⚠️ Brix ve Verim tahminleri için sol panelden 'Model Eğitimi' yapmalısınız.")
                c1, c2 = st.columns(2)
                c1.metric("Tahmini Brix", "Model Eğit")
                c2.metric("Tahmini Verim", "Model Eğit")

st.markdown("---")
