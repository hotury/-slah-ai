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

# --- 1. YAPILANDIRMA VE DOSYA YOLLARI ---
DATA_DIR = "data"
CUSTOM_MODEL_FILE = "biovalent_custom.pkl" # Kullanıcının kendi eğittiği
MASTER_DATA_FILE = "biovalent_final.pkl"  # Senin hazır ana verilerin

# --- 2. MODEL EĞİTİM FONKSİYONU (Özel Model İçin) ---
def train_custom_model():
    if not os.path.exists(DATA_DIR):
        st.error("❌ 'data/' klasörü bulunamadı. Lütfen eğitim verilerini yükleyin.")
        return None

    try:
        X_df = pd.read_csv(os.path.join(DATA_DIR, "marker_matrix.csv"), index_col="GENOTYPE")
        y_df = pd.read_csv(os.path.join(DATA_DIR, "phenotype_data.csv"), index_col="GENOTYPE")
        idx = X_df.index.intersection(y_df.index)
        X, y = X_df.loc[idx].values, y_df.loc[idx]
        trait_names = list(y.columns)

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        models = {}
        for trait in trait_names:
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
            "traits": trait_names,
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
            preds[trait] = m.predict_proba(X_scaled)[0, 1] * 100 # % Olasılık
        else:
            preds[trait] = m.predict(X_scaled)[0]
    
    # Eğer Master Model seçiliyse biyolojik katsayıları uygula
    if plant_type and master_info and plant_type in master_info["bitki_parametreleri"]:
        params = master_info["bitki_parametreleri"][plant_type]
        for trait in preds:
            if not ("DISEASE" in trait.upper() or "RESISTANCE" in trait.upper()):
                preds[trait] = params["baz_verim"] + (preds[trait] * params["oran"])
                
    return preds

# --- 4. MELEZLEME SİMÜLASYONU ---
def simulate_cross(p1, p2, n_offspring=100):
    n_snps = len(p1)
    offspring = np.zeros((n_offspring, n_snps))
    for i in range(n_offspring):
        cross_points = sorted(np.random.choice(range(1, n_snps), size=np.random.randint(1, 4), replace=False))
        cross_points = [0] + cross_points + [n_snps]
        curr = np.random.choice([0, 1])
        for j in range(len(cross_points)-1):
            s, e = cross_points[j], cross_points[j+1]
            offspring[i, s:e] = p1[s:e] if curr == 0 else p2[s:e]
            curr = 1 - curr
    return offspring

# --- 5. ARAYÜZ (STREAMLIT) ---
st.set_page_config(page_title="Vista Seeds | Biovalent AI", layout="wide", page_icon="🌱")

# Başlık Paneli
st.markdown("<h1 style='text-align: center; color: #00CC96;'>🌱 Vista Seeds AI Analiz Platformu</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Dijital Islah ve Genetik Karar Destek Sistemi</p>", unsafe_allow_html=True)

# Yan Panel: Model Seçimi
with st.sidebar:
    st.header("🤖 Model ve Zeka Seçimi")
    selection = st.radio("Kullanılacak Yapay Zeka:", ["Hazır Biovalent Master", "Kendi Özel Modelim"])
    
    master_data = None
    if os.path.exists(MASTER_DATA_FILE):
        master_data = joblib.load(MASTER_DATA_FILE)

    active_model = None
    if selection == "Hazır Biovalent Master":
        if master_data:
            # Master veri aslında bir model değil katsayı setidir, 
            # ancak biz burada 'biovalent.pkl' (eğitilmiş model) ile birleştirerek kullanıyoruz.
            if os.path.exists("biovalent.pkl"):
                active_model = joblib.load("biovalent.pkl")
                active_model["type"] = "master"
                st.success("✅ Master Zeka Aktif")
            else:
                st.error("biovalent.pkl (Model) bulunamadı!")
        else:
            st.error("Master katsayı dosyası bulunamadı!")
    else:
        if os.path.exists(CUSTOM_MODEL_FILE):
            active_model = joblib.load(CUSTOM_MODEL_FILE)
            st.success("✅ Özel Model Aktif")
        
        if st.button("🚀 Özel Modeli Şimdi Eğit"):
            with st.spinner("Eğitiliyor..."):
                active_model = train_custom_model()
                if active_model: st.rerun()

# Ana Ekran
if active_model:
    tab1, tab2, tab3 = st.tabs(["📂 Toplu Analiz", "🔬 Tekli Tahmin", "🧬 Melezleme Planlayıcı"])

    # --- TOPLU ANALİZ ---
    with tab1:
        st.subheader("Laboratuvar Verisi Analizi")
        
        # Bitki Modül Seçimi (Sadece Master Modelde aktif)
        p_type = None
        if active_model.get("type") == "master" and master_data:
            p_type = st.selectbox("Bitki Türü Seçin:", list(master_data["bitki_parametreleri"].keys()))
        
        uploaded = st.file_uploader("Genotip CSV Dosyası", type="csv")
        if uploaded:
            df = pd.read_csv(uploaded)
            if st.button("Tüm Adayları Tara"):
                res_list = []
                for i, row in df.iterrows():
                    vec = row.select_dtypes(include=[np.number]).values
                    if len(vec) == active_model["n_features"]:
                        p = predict_engine(vec, active_model, p_type, master_data)
                        p["Aday_ID"] = row.get("ID", f"ID_{i}")
                        res_list.append(p)
                
                res_df = pd.DataFrame(res_list)
                st.dataframe(res_df, use_container_width=True)
                
                # Rapor İndir
                csv = res_df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Analiz Raporunu İndir", data=csv, file_name="vista_analiz.csv")

    # --- TEKLİ TAHMİN ---
    with tab2:
        st.subheader("Manuel Aday Analizi")
        val_input = st.text_input("SNP Vektörü (Örn: 0,1,2...):", "0,1,1,0,2")
        if st.button("Tahmin Et"):
            v = [float(x.strip()) for x in val_input.split(",")]
            res = predict_engine(v, active_model, p_type if 'p_type' in locals() else None, master_data)
            cols = st.columns(len(res))
            for i, (t, val) in enumerate(res.items()):
                cols[i].metric(t, f"{val:.2f}")

    # --- MELEZLEME ---
    with tab3:
        st.subheader("F1 & F2 Nesil Simülatörü")
        c1, c2 = st.columns(2)
        p1_v = c1.text_input("Ebeveyn 1 (Anne):", "0,1,0,1,1")
        p2_v = c2.text_input("Ebeveyn 2 (Baba):", "1,0,1,0,0")
        
        if st.button("🧬 Çaprazla ve Genetik Limiti Gör"):
            p1 = [float(x.strip()) for x in p1_v.split(",")]
            p2 = [float(x.strip()) for x in p2_v.split(",")]
            
            f2_pop = simulate_cross(p1, p2, 200)
            f2_preds = [predict_engine(ind, active_model, p_type if 'p_type' in locals() else None, master_data) for ind in f2_pop]
            f2_df = pd.DataFrame(f2_preds)
            
            target = active_model["traits"][0]
            fig = px.histogram(f2_df, x=target, title=f"F2 Nesli {target} Dağılımı", color_discrete_sequence=['#00CC96'])
            st.plotly_chart(fig, use_container_width=True)
            
            st.write(f"**Teorik Genetik Limit (Maksimum):** {f2_df[target].max():.2f}")

else:
    st.warning("⚠️ Lütfen yan panelden bir model seçin veya kendi modelinizi eğitin.")
