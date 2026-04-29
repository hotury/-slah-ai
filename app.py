import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.model_selection import train_test_split
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import io

# --- 1. CONFIG & DOSYA YOLLARI ---
DATA_DIR = "data"
MODEL_FILE = "biovalent.pkl"
MASTER_DATA_FILE = "biovalent_final.pkl" # Senin yüklediğin master veri seti

# --- 2. MASTER VERİYİ YÜKLEME ---
def load_master_data():
    if os.path.exists(MASTER_DATA_FILE):
        return joblib.load(MASTER_DATA_FILE)
    return None

# --- 3. TAHMİN MOTORU (MASTER KATSAYILI) ---
def predict_with_master(genotype_vector, model_data, plant_type, master_data):
    # Modelden gelen temel yapay zeka tahmini
    X = np.array([genotype_vector], dtype=float)
    X_scaled = model_data["scaler"].transform(X)
    
    raw_results = {}
    for trait, m in model_data["models"].items():
        if hasattr(m, "predict_proba"):
            raw_results[trait] = m.predict_proba(X_scaled)[0, 1] * 100
        else:
            raw_results[trait] = m.predict(X_scaled)[0]
    
    # MASTER VERİ SETİNDEN KATSAYI UYGULAMA (HESAPLAMA MODÜLÜ)
    if master_data and plant_type in master_data["bitki_parametreleri"]:
        p_params = master_data["bitki_parametreleri"][plant_type]
        ratio = p_params["oran"]
        base_yield = p_params["baz_verim"]
        
        # Biyolojik düzeltme hesabı
        refined_results = {}
        for trait, val in raw_results.items():
            if "DISEASE" in trait.upper() or "RESISTANCE" in trait.upper():
                refined_results[trait] = val # Hastalık direnci olasılıktır, katsayıdan bağımsızdır
            else:
                # Verim ve Brix gibi değerleri master katsayı ile optimize et
                refined_results[trait] = base_yield + (val * ratio)
        return refined_results
    
    return raw_results

# --- 4. ARAYÜZ (STREAMLIT) ---
st.set_page_config(page_title="Vista Seeds AI | Profesyonel Islah", layout="wide", page_icon="🌱")

master_data = load_master_data()

st.title("🧬 Biovalent AI: Modüler Dijital Islah")

# Yan Panel - Bitki Seçim Modülü
with st.sidebar:
    st.header("🌿 Bitki Seçimi")
    if master_data:
        bitki_listesi = list(master_data["bitki_parametreleri"].keys())
        secilen_bitki = st.selectbox("Analiz edilecek türü seçin:", bitki_listesi)
        st.success(f"Modül Aktif: {secilen_bitki}")
        st.write(f"🧬 Genetik Oran: {master_data['bitki_parametreleri'][secilen_bitki]['oran']}")
    else:
        st.error("Master veri seti bulunamadı!")

    st.markdown("---")
    if st.button("🚀 AI Modelini Eğit"):
        # train_and_save_model() fonksiyonu burada çağrılır
        st.info("Eğitim başlatıldı...")

# Ana Sekmeler
tab1, tab2 = st.tabs(["📂 Toplu Analiz ve Raporlama", "🔬 Tekli Test"])

if "model_data" not in st.session_state and os.path.exists(MODEL_FILE):
    st.session_state.model_data = joblib.load(MODEL_FILE)

if st.session_state.get("model_data"):
    m_data = st.session_state.model_data

    # --- TOPLU ANALİZ MODÜLÜ ---
    with tab1:
        st.subheader(f"📊 {secilen_bitki} Laboratuvar Verisi Yükleme")
        uploaded_file = st.file_uploader("CSV formatında genetik veri yükleyin", type=["csv"])
        
        if uploaded_file:
            client_data = pd.read_csv(uploaded_file)
            if st.button(f"{secilen_bitki} Analizini Başlat"):
                results = []
                for _, row in client_data.iterrows():
                    snp_vec = row.select_dtypes(include=[np.number]).values
                    if len(snp_vec) == m_data["n_features"]:
                        # Master katsayılarla hesapla
                        final_preds = predict_with_master(snp_vec, m_data, secilen_bitki, master_data)
                        final_preds["Aday_ID"] = row.get("ID", f"Aday_{_}")
                        results.append(final_preds)
                
                res_df = pd.DataFrame(results)
                st.dataframe(res_df)
                
                # Rapor İndirme
                csv = res_df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Analiz Raporunu İndir", data=csv, file_name=f"{secilen_bitki}_analiz.csv")

else:
    st.warning("Lütfen önce AI modelini eğitin.")
