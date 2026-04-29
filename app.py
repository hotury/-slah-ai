import streamlit as st
import pandas as pd
import joblib
import plotly.graph_objects as go
from Bio.Seq import Seq

# Sayfa Ayarları
st.set_page_config(page_title="Biovalent Sentinel Pro", page_icon="🧬", layout="wide")

# --- ÖZEL TASARIM (CSS) ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stApp { background-color: #0e1117; }
    .metric-card {
        background-color: #1a1c23;
        border: 1px solid #30363d;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 10px;
        min-height: 100px;
    }
    .metric-value { font-size: 22px; font-weight: bold; color: #ffffff; }
    .metric-label { font-size: 12px; color: #8b949e; margin-top: 5px; text-transform: uppercase; }
    .stTabs [data-baseweb="tab-list"] { background-color: #0e1117; }
    .stTabs [data-baseweb="tab"] { color: #8b949e; font-weight: 600; }
    .stTabs [aria-selected="true"] { color: #58a6ff !important; }
    </style>
    """, unsafe_allow_html=True)

# --- GELİŞMİŞ ANALİZ MOTORU ---
def analyze_comprehensive_metrics(protein_seq, bitki_turu, model_data):
    if not protein_seq: return None
    L = len(protein_seq)
    
    # 1. TEMEL VERİLER (Biyofiziksel)
    mw = L * 110.1
    
    # 2. HASAT VE GELİŞİM (V, L, I Amino Asitleri - Metabolizma Hızı)
    metabolic_rate = (protein_seq.count('V') + protein_seq.count('L') + protein_seq.count('I')) / L
    baz_hasat = model_data['bitki_parametreleri'][bitki_turu].get('baz_hasat_suresi', 90)
    hasat_suresi = baz_hasat - (metabolic_rate * 40)
    
    # 3. ÇİMLENME GÜCÜ (Vigor - Alanin ve Glisin Yoğunluğu)
    vigor = min(100, ((protein_seq.count('A') + protein_seq.count('G')) / L) * 400 + 30)
    
    # 4. RAF ÖMRÜ (İnstabilite İndeksi Yaklaşımı)
    stability = (protein_seq.count('P') + protein_seq.count('V')) / L
    raf_omru = 7 + (stability * 100)
    
    # 5. DİRENÇLER (Sistein ve Hidropati)
    hastalik = min(100, (protein_seq.count('C') / L) * 500 + 40)
    stres_toleransi = min(100, metabolic_rate * 250) # Soğuk/Tuz direnci
    
    # 6. KALİTE (Brix ve Aroma)
    aroma = (protein_seq.count('E') + protein_seq.count('D')) / L
    brix = 3.5 + (aroma * 25)

    return {
        "MW": mw, "Hasat_Suresi": round(hasat_suresi), "Vigor": round(vigor, 1),
        "Raf_Omru": round(raf_omru, 1), "Hastalik": round(hastalik, 1),
        "Brix": round(brix, 2), "Stres": round(stres_toleransi, 1)
    }

def show_card(label, value, unit=""):
    st.markdown(f"""<div class="metric-card"><div class="metric-value">{value}{unit}</div><div class="metric-label">{label}</div></div>""", unsafe_allow_html=True)

# --- MODEL YÜKLEME ---
try:
    model_data = joblib.load('biovalent_final.pkl')
except:
    st.error("Model dosyası bulunamadı!")
    st.stop()

# --- ARAYÜZ ---
st.title("🧬 Biovalent Sentinel: Full Spectrum")
st.markdown("Bir tohumun genetik kaderini tüm detaylarıyla görün.")

# Yan Panel (Saha Koşulları)
with st.sidebar:
    st.header("⚙️ Saha Parametreleri")
    tur = st.selectbox("Bitki Türü", list(model_data['bitki_parametreleri'].keys()))
    alan = st.number_input("Ekili Alan (Dönüm)", value=1)
    toprak_kalitesi = st.select_slider("Toprak Verimliliği", options=["Düşük", "Orta", "Yüksek"], value="Orta")

# Ana Ekran
raw_input = st.text_area("Genetik Diziyi (DNA/Protein) Yapıştırın:", height=100)

if raw_input:
    # DNA -> Protein Çevrimi
    is_dna = all(c in "ATGCN " for c in raw_input.strip().upper()[:20])
    p_seq = str(Seq(raw_input.strip().upper()).translate(to_stop=True)) if is_dna else raw_input.strip().upper()
    
    m = analyze_comprehensive_metrics(p_seq, tur, model_data)
    
    if m:
        # SATIR 1: HASAT VE VERİM
        st.subheader("🗓️ Üretim ve Hasat Takvimi")
        r1_c1, r1_c2, r1_c3, r1_c4 = st.columns(4)
        with r1_c1: show_card("Hasat Süresi", m['Hasat_Suresi'], " Gün")
        with r1_c2: show_card("Çimlenme Gücü (Vigor)", f"%{m['Vigor']}")
        with r1_c3: 
            katsayi = model_data['bitki_parametreleri'][tur]['oran']
            gramaj = m['MW'] * katsayi * (1.2 if toprak_kalitesi=="Yüksek" else 0.8 if toprak_kalitesi=="Düşük" else 1.0)
            show_card("Meyve Ağırlığı", f"{gramaj:.1f}", " gr")
        with r1_c4:
            toplam_tonaj = (model_data['bitki_parametreleri'][tur]['baz_verim'] * alan * (gramaj/100)) / 10
            show_card("Toplam Rekolte", f"{toplam_tonaj:.2f}", " Ton")

        # SATIR 2: DAYANIKLILIK VE STRES
        st.subheader("🛡️ Dayanıklılık ve Adaptasyon")
        r2_c1, r2_c2, r2_c3, r2_c4 = st.columns(4)
        with r2_c1: show_card("Hastalık Direnci", f"%{m['Hastalik']}")
        with r2_c2: show_card("Raf Ömrü", m['Raf_Omru'], " Gün")
        with r2_c3: show_card("Çevresel Stres Toleransı", f"%{m['Stres']}")
        with r2_c4: show_card("Brix (Tat Oranı)", m['Brix'])

        # GÖRSELLEŞTİRME (RADAR)
        categories = ['Çimlenme Gücü', 'Hastalık Direnci', 'Stres Toleransı', 'Raf Ömrü', 'Brix (Tat)']
        values = [m['Vigor'], m['Hastalik'], m['Stres'], min(100, m['Raf_Omru']*3), min(100, m['Brix']*10)]
        
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(r=values, theta=categories, fill='toself', line_color='#58a6ff'))
        fig.update_layout(
            polar=dict(bgcolor="#1a1c23", radialaxis=dict(visible=True, range=[0, 100], color="white")),
            paper_bgcolor="#0e1117", font_color="white", showlegend=False, height=450
        )
        st.plotly_chart(fig, use_container_width=True)
