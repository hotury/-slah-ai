import streamlit as st
import pandas as pd
import joblib
import plotly.graph_objects as go
from Bio.Seq import Seq
import io

# --- 1. SAYFA VE TEMA AYARLARI ---
st.set_page_config(
    page_title="Biovalent Sentinel Pro",
    page_icon="🧬",
    layout="wide"
)

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stApp { background-color: #0e1117; }
    /* Siyah Metrik Kartları */
    .metric-card {
        background-color: #1a1c23;
        border: 1px solid #30363d;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 5px;
    }
    .metric-value { font-size: 26px; font-weight: bold; color: #58a6ff; }
    .metric-label { font-size: 13px; color: #8b949e; margin-top: 8px; text-transform: uppercase; font-weight: bold; }
    /* Açıklama Metinleri */
    .explainer-text { 
        font-size: 11.5px; 
        color: #a3a3a3; 
        text-align: center; 
        margin-bottom: 25px; 
        line-height: 1.4;
        padding: 0 10px;
        font-style: italic;
    }
    .stTabs [data-baseweb="tab-list"] { background-color: #0e1117; border-bottom: 1px solid #30363d; }
    .stTabs [aria-selected="true"] { color: #58a6ff !important; border-bottom-color: #58a6ff !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. YORUMLAMA VE ANALİZ MOTORU ---

def get_interpretation(label, value):
    """Metrikler için ziraat ve ticaret odaklı dinamik açıklamalar."""
    interpretations = {
        "Hastalık Direnci": {
            "low": "⚠️ Duyarlı: Patojen baskısına açık, sık ilaçlama gerektirebilir.",
            "mid": "✅ Toleranslı: Standart hastalıklara karşı genetik savunması aktif.",
            "high": "🛡️ Yüksek Direnç: Güçlü genetik zırh, minimum ilaç maliyeti."
        },
        "Raf Ömrü": {
            "low": "🚚 Yerel Pazar: Hasat sonrası hızla tüketime sunulmalı.",
            "mid": "🌍 Lojistik Uygun: Şehirler arası nakliyeye ve depolamaya dayanıklı.",
            "high": "✈️ İhracatlık: Uzun yol dayanımı çok yüksek, fire oranı düşük."
        },
        "Brix (Tat)": {
            "low": "🍴 Endüstriyel: Salçalık veya dondurulmuş gıda üretimine uygun.",
            "mid": "😋 Sofralık: Dengeli şeker-asit oranı, taze tüketime uygun.",
            "high": "🌟 Gurme: Yoğun aroma ve yüksek şeker, premium pazar değeri."
        },
        "Stres Toleransı": {
            "low": "🌡️ Hassas: Sadece iklim kontrollü seralar için önerilir.",
            "mid": "🌤️ Adaptif: Değişken hava ve toprak koşullarına uyumlu.",
            "high": "🦾 Dayanıklı: Ekstrem sıcak, soğuk veya tuzlu toprağa yüksek direnç."
        }
    }
    if label in interpretations:
        if value < 45: return interpretations[label]["low"]
        elif value < 70: return interpretations[label]["mid"]
        else: return interpretations[label]["high"]
    return ""

def process_genetic_input(data):
    """FASTA temizleme ve DNA -> Protein çevirimi."""
    content = data.strip()
    if content.startswith(">"):
        content = "".join(l.strip() for l in content.splitlines() if not l.startswith(">"))
    is_dna = all(c in "ATGCN " for c in content.upper()[:30])
    if is_dna:
        try:
            return str(Seq(content.upper().replace(" ", "")).translate(to_stop=True))
        except: return content.upper()
    return content.upper()

def calculate_full_traits(p_seq, bitki_turu, model_data):
    """Tüm biyofiziksel özellikleri hesaplar."""
    if not p_seq: return None
    L = len(p_seq)
    mw = L * 110.1
    m_rate = (p_seq.count('V') + p_seq.count('L') + p_seq.count('I')) / L
    
    baz_sure = model_data['bitki_parametreleri'][bitki_turu].get('baz_hasat_suresi', 90)
    hasat = baz_sure - (m_rate * 45)
    vigor = min(100, ((p_seq.count('A') + p_seq.count('G')) / L) * 400 + 35)
    hastalik = min(100, (p_seq.count('C') / L) * 550 + 40)
    stres = min(100, m_rate * 280)
    raf = 8 + ((p_seq.count('P') + p_seq.count('V')) / L * 110)
    brix = 3.8 + ((p_seq.count('E') + p_seq.count('D')) / L * 22)

    return {
        "MW": mw, "Hasat": round(hasat), "Vigor": round(vigor, 1),
        "Hastalik": round(hastalik, 1), "Stres": round(stres, 1),
        "Raf": round(raf, 1), "Brix": round(brix, 2)
    }

def show_enhanced_metric(label, value, unit="", explainer=""):
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{value}{unit}</div>
            <div class="metric-label">{label}</div>
        </div>
        <div class="explainer-text">{explainer}</div>
    """, unsafe_allow_html=True)

# --- 3. MODEL YÜKLEME ---
try:
    model_data = joblib.load('biovalent_final.pkl')
except:
    st.error("❌ 'biovalent_final.pkl' dosyası bulunamadı!")
    st.stop()

# --- 4. ANA ARAYÜZ ---
st.title("🧬 Biovalent Sentinel: Akıllı Islah Paneli")
st.write("Genetik veriyi ticari değere dönüştüren dijital ikizleme motoru.")

with st.sidebar:
    st.header("⚙️ Saha Ayarları")
    secilen_tur = st.selectbox("Bitki Türü", list(model_data['bitki_parametreleri'].keys()))
    toprak = st.select_slider("Toprak Potansiyeli", options=["Düşük", "Orta", "Yüksek"], value="Orta")
    st.markdown("---")
    st.write("v2.4 - Full Spectrum Engine")

tab1, tab2 = st.tabs(["🔍 Genetik Karakter Analizi", "🧪 Dijital F1 Hibrit Simülasyonu"])

with tab1:
    c_in1, c_in2 = st.columns(2)
    with c_in1:
        file = st.file_uploader("Dosya Yükle (.fasta, .txt)", type=['fasta', 'txt'])
    with c_in2:
        manual = st.text_area("Veya Manuel Dizi Yapıştırın:", height=68)

    input_data = file.read().decode("utf-8") if file else manual

    if input_data:
        p_seq = process_genetic_input(input_data)
        res = calculate_full_traits(p_seq, secilen_tur, model_data)
        
        if res:
            st.subheader("📊 Gelişim ve Morfoloji")
            r1c1, r1c2, r1c3 = st.columns(3)
            with r1c1:
                k = model_data['bitki_parametreleri'][secilen_tur]['oran']
                adj = 1.2 if toprak=="Yüksek" else 0.8 if toprak=="Düşük" else 1.0
                show_enhanced_metric("Potansiyel Meyve Ağırlığı", f"{res['MW'] * k * adj:.1f}", " gr", "Genetik dizinin belirlediği maksimum tek meyve ağırlığı potansiyeli.")
            with r1c2: show_enhanced_metric("Hasat Süresi", res['Hasat'], " Gün", "Ekimden itibaren meyvenin ilk hasat olgunluğuna erişeceği süre.")
            with r1c3: show_enhanced_metric("Çimlenme Gücü (Vigor)", f"%{res['Vigor']}", "", "Tohumun toprak çıkış enerjisi ve büyüme hızı katsayısı.")

            st.subheader("🛡️ Biyolojik Kalite ve Direnç Analizi")
            r2c1, r2c2, r2c3, r2c4 = st.columns(4)
            with r2c1: show_enhanced_metric("Hastalık Direnci", f"%{res['Hastalik']}", "", get_interpretation("Hastalık Direnci", res['Hastalik']))
            with r2c2: show_enhanced_metric("Raf Ömrü", res['Raf'], " Gün", get_interpretation("Raf Ömrü", res['Raf']))
            with r2c3: show_enhanced_metric("Stres Toleransı", f"%{res['Stres']}", "", get_interpretation("Stres Toleransı", res['Stres']))
            with r2c4: show_enhanced_metric("Brix (Tat Oranı)", res['Brix'], "", get_interpretation("Brix (Tat)", res['Brix']))

            # RADAR CHART
            st.markdown("---")
            categories = ['Vigor', 'Hastalık', 'Stres', 'Raf Ömrü', 'Brix']
            values = [res['Vigor'], res['Hastalik'], res['Stres'], min(100, res['Raf']*3.5), min(100, res['Brix']*10)]
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(r=values, theta=categories, fill='toself', line_color='#58a6ff', fillcolor='rgba(88, 166, 255, 0.2)'))
            fig.update_layout(polar=dict(bgcolor="#1a1c23", radialaxis=dict(visible=True, range=[0, 100], color="white")),
                              paper_bgcolor="#0e1117", font_color="white", height=450, title="Tohum Genetik Performans Radarı")
            st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Dijital F1 Hibrit Karşılaştırma")
    f1c1, f1c2 = st.columns(2)
    anne = f1c1.text_area("Anne (Ebeveyn 1):")
    baba = f1c2.text_area("Baba (Ebeveyn 2):")
    
    if st.button("HİBRİT GÜCÜNÜ (HETEROSİS) HESAPLA"):
        if anne and baba:
            pa, pb = process_genetic_input(anne), process_genetic_input(baba)
            ma, mb = calculate_full_traits(pa, secilen_tur, model_data), calculate_full_traits(pb, secilen_tur, model_data)
            f1_mw = ((ma['MW'] + mb['MW']) / 2) * 1.18
            st.success(f"🚀 Hibrit Azmanlığı Tespit Edildi! Beklenen F1 Moleküler Kütle: {f1_mw:.0f} Da")
            st.write("F1 nesli, ebeveyn ortalamasına göre %18 daha yüksek verim potansiyeline sahiptir.")
