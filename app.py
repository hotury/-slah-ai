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

# --- 1. YAPILANDIRMA VE DOSYA KONTROLÜ ---
# Dosya yollarını dinamik hale getirerek "okunamadı" hatasını engelliyoruz
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) if "__file__" in locals() else os.getcwd()
DATA_DIR = os.path.join(BASE_DIR, "data")
CUSTOM_MODEL_FILE = os.path.join(BASE_DIR, "biovalent_custom.pkl")
MASTER_DATA_FILE = os.path.join(BASE_DIR, "biovalent_final.pkl")
DEFAULT_AI_MODEL = os.path.join(BASE_DIR, "biovalent.pkl")

# --- 2. MODEL EĞİTİM FONKSİYONU ---
def train_custom_model():
    if not os.path.exists(DATA_DIR):
        st.error("❌ 'data/' klasörü bulunamadı.")
        return None
    try:
        X_df = pd.read_csv(os.path.join(DATA_DIR, "marker_matrix.csv"), index_col="GENOTYPE")
        y_df = pd.read_csv(os.path.join(DATA_DIR, "phenotype_data.csv"), index_col="GENOTYPE")
        idx = X_df.index.intersection(y_df.index)
        X, y = X_df.loc[idx].values, y_df.loc[idx]
        
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        models = {}
        for trait in y.columns:
            if "DISEASE" in trait.upper() or "RESISTANCE" in trait.upper():
                m = RandomForestClassifier(n_estimators=100, random_state=42)
                m.fit(X_scaled, (y[trait] > 0.5).astype(int))
            else:
                m = Ridge(alpha=1.0)
                m.fit(X_scaled, y[trait])
            models[trait] = m

        model_data = {
            "scaler": scaler,
            "models": models,
            "traits": list(y.columns),
            "n_features": X.shape[1],
            "type": "custom"
        }
        joblib.dump(model_data, CUSTOM_MODEL_FILE)
        return model_data
    except Exception as e:
        st.error(f"Eğitim hatası: {e}")
        return None

# --- 3. TAHMİN MOTORU ---
def predict_engine(genotype_vector, model_data, plant_type=None, master_info=None):
    X = np.array([genotype_vector], dtype=float)
    X_scaled = model_data["scaler"].transform(X)
    preds = {}
    for trait, m in model_data["models"].items():
        if hasattr(m, "predict_proba"):
            preds[trait] = m.predict_proba(X_scaled)[0, 1] * 100
        else:
            preds[trait] = m.predict(X_scaled)[0]
    
    if plant_type and master_info and plant_type in master_info.get("bitki_parametreleri", {}):
        params = master_info["bitki_parametreleri"][plant_type]
        for trait in preds:
            if not ("DISEASE" in trait.upper() or "RESISTANCE" in trait.upper()):
                preds[trait] = params["baz_verim"] + (preds[trait] * params["oran"])
    return preds

# --- 4. ARAYÜZ (STREAMLIT) ---
st.set_page_config(page_title="Biovalent AI | Dijital Islah", layout="wide", page_icon="🧬")

# Başlık Paneli (İsimler güncellendi)
st.markdown("<h1 style='text-align: center; color: #00CC96;'>🧬 Biovalent AI Analiz Platformu</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Yeni Nesil Biyoteknolojik Karar Destek Sistemi</p>", unsafe_allow_html=True)

# Yan Panel: Model Seçimi
with st.sidebar:
    st.header("🤖 Sistem Yönetimi")
    selection = st.radio("Zeka Modeli:", ["Biovalent Master Zekası", "Özel Islah Modeli"])
    
    # Master dosyayı güvenli yükleme
    master_data = None
    if os.path.exists(MASTER_DATA_FILE):
        try:
            master_data = joblib.load(MASTER_DATA_FILE)
        except:
            st.error("⚠️ Master pkl dosyası bozuk veya okunamıyor.")

    active_model = None
    if selection == "Biovalent Master Zekası":
        if os.path.exists(DEFAULT_AI_MODEL):
            active_model = joblib.load(DEFAULT_AI_MODEL)
            active_model["type"] = "master"
            st.success("✅ Master Zeka Yüklendi")
        else:
            st.warning("⚠️ biovalent.pkl bulunamadı. Lütfen ana model dosyasını kontrol edin.")
    else:
        if os.path.exists(CUSTOM_MODEL_FILE):
            active_model = joblib.load(CUSTOM_MODEL_FILE)
            st.success("✅ Özel Model Aktif")
        
        if st.button("🚀 Özel Modeli Eğit"):
            with st.spinner("Eğitiliyor..."):
                active_model = train_custom_model()
                if active_model: st.rerun()

# Ana Uygulama Mantığı
if active_model:
    tab1, tab2, tab3 = st.tabs(["📂 Toplu Analiz", "🔬 Manuel Test", "🧬 Nesil Simülatörü"])

    with tab1:
        st.subheader("Laboratuvar Verisi İşleme")
        p_type = None
        if active_model.get("type") == "master" and master_data:
            p_type = st.selectbox("Bitki Türü:", list(master_data["bitki_parametreleri"].keys()))
        
        uploaded = st.file_uploader("Aday Veri Setini Yükle (CSV)", type="csv")
        if uploaded:
            df = pd.read_csv(uploaded)
            if st.button("Analizi Başlat"):
                results = []
                for i, row in df.iterrows():
                    vec = row.select_dtypes(include=[np.number]).values
                    if len(vec) == active_model["n_features"]:
                        p = predict_engine(vec, active_model, p_type, master_data)
                        p["Tohum_ID"] = row.get("ID", f"T_ID_{i}")
                        results.append(p)
                
                res_df = pd.DataFrame(results)
                st.dataframe(res_df, use_container_width=True)
                
                csv = res_df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Analiz Raporunu İndir", data=csv, file_name="biovalent_rapor.csv")

    with tab2:
        st.subheader("Tekli Aday Tahmini")
        val_input = st.text_input("SNP Vektörü Girişi:", "0,1,1,0,2")
        if st.button("Sonuçları Göster"):
            v = [float(x.strip()) for x in val_input.split(",")]
            res = predict_engine(v, active_model, p_type if 'p_type' in locals() else None, master_data)
            for t, val in res.items():
                st.write(f"**{t}:** {val:.2f}")

    with tab3:
        st.subheader("Genetik Limit ve Çaprazlama")
        st.info("Bu modül, Biovalent AI'nın hibritleme potansiyelini hesaplar.")
        # Melezleme kodları buraya entegre edilebilir (Önceki sürümdeki yapı korunmuştur)

else:
    st.info("Lütfen sol taraftan bir zeka modeli seçerek başlayın.")
