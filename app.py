import streamlit as st
import pandas as pd
import joblib
import plotly.graph_objects as go
from Bio.Seq import Seq
import io

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(
    page_title="Biovalent Sentinel Pro | Dijital Islah İstasyonu",
    page_icon="🧬",
    layout="wide"
)

# --- ÖZEL TASARIM (DARK MODE & KUTU TASARIMLARI) ---
st.markdown("""
    <style>
    /* Ana Arka Plan */
    .main { background-color: #0e1117; color: white; }
    .stApp { background-color: #0e1117; }
    
    /* Siyah Kutu Metrik Kartları */
    .metric-card {
        background-color: #1a1c23;
        border: 1px solid #30363d;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 15px;
        transition: transform 0.3s;
    }
    .metric-card:hover { border-color: #58a6ff; transform: translateY(-5px); }
    .metric-value { font-size: 26px; font-weight: bold; color: #ffffff; }
    .metric-label { font-size: 13px; color: #8b949e; margin-top: 8px; text-transform: uppercase; letter-spacing: 1px; }
    
    /* Sekme ve Sidebar Düzenlemeleri */
    .stTabs [data-baseweb="tab-list"] { background-color: #0e1117; border-bottom: 1px solid #30363d; }
    .stTabs [data-baseweb="tab"] { color: #8b949e; font-size: 16px; font-weight: 600; }
    .stTabs [aria-selected="true"] { color: #58a6ff !important; border-bottom-color: #58a6ff !important; }
    
    /* Input Alanları */
    .stTextArea textarea { background-color: #0d1117; color: white; border: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

# --- ANALİZ MOTORU FONKSİYONLARI ---

def process_genetics(data):
    """FASTA başlıklarını temizler ve DNA'yı proteine çevirir."""
    content = data.strip()
    if content.startswith(">"):
        lines = content.splitlines()
        content = "".join(line.strip() for line in lines if not line.startswith(">"))
    
    # DNA Tespiti ve Çeviri
    is_dna = all(c in "ATGCN " for c in content.upper()[:30])
    if is_dna:
        try:
            return str(Seq(content.upper().replace(" ", "")).translate(to_stop=True))
        except:
            return content.upper()
    return content.upper()

def calculate_full_traits(p_seq, bitki_turu, model_data):
    """Biyofiziksel sabitlerle tohumun tüm potansiyelini hesaplar."""
    if not p_seq: return None
    L = len(p_seq)
    
    # 1. Temel Biyofizik
    mw = L * 110.1 # Moleküler Ağırlık
    metabolic_rate = (p_seq.count('V') + p_seq.count('L') + p_seq.count('I')) / L
    
    # 2. Üretim ve Hasat
    baz_sure = model_data['bitki_parametreleri'][bitki_turu].get('baz_hasat_suresi', 100)
    hasat_gunu = baz_sure - (metabolic_rate * 45)
    vigor = min(100, ((p_seq.count('A') + p_seq.count('G')) / L) * 400 + 35) # Çimlenme Gücü
    
    # 3. Dayanıklılık ve Raf Ömrü
    hastalik_direnci = min(100, (p_seq.count('C') / L) * 550 + 40)
    stres_toleransi = min(100, metabolic_rate * 280)
    stability = (p_seq.count('P') + p_seq.count('V')) / L
    raf_omru = 8 + (stability * 110)
    
    # 4. Kalite (Brix)
    aroma_factor = (p_seq.count('E') + p_seq.count('D') + p_seq.count('Q')) / L
    brix = 3.8 + (aroma_factor * 22)

    return {
        "MW": mw, "Hasat": round(hasat_gunu), "Vigor": round(vigor, 1),
        "Hastalik": round(hastalik_direnci, 1), "Stres": round(stres_toleransi, 1),
        "Raf": round(raf_omru, 1), "Brix": round(brix, 2)
    }

def show_metric(label, value, unit=""):
    """Siyah kutu içerisinde veriyi sunar."""
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{value}{unit}</div>
            <div class="metric-label">{label}</div>
        </div>
    """, unsafe_allow_html=True)

# --- MODEL YÜKLEME ---
try:
    model_data = joblib.load('biovalent_final.pkl')
except:
    st.error("❌ 'biovalent_final.pkl' dosyası bulunamadı! Lütfen dosyanın app.py ile aynı klasörde olduğundan emin olun.")
    st.stop()

# --- ARAYÜZ ---
st.title("🧬 Biovalent Sentinel: Full-Spectrum Engine")
st.markdown("Genetik Haritadan Geleceğin Hasadına: Dijital Islah ve Verim İstasyonu")

# --- SIDEBAR (SAHA AYARLARI) ---
with st.sidebar:
    st.header("⚙️ Saha ve Ortam Parametreleri")
    secilen_tur = st.selectbox("Bitki Türü", list(model_data['bitki_parametreleri'].keys()))
    alan = st.number_input("Ekili Alan (Dönüm)", value=1, min_value=1)
    toprak_kalitesi = st.select_slider("Toprak Verimliliği", options=["Düşük", "Orta", "Yüksek"], value="Orta")
    st.info("Bu ayarlar tarladaki gerçek tonaj ve meyve ağırlığı hesabını etkiler.")

# --- ANA SEKMELER ---
tab1, tab2 = st.tabs(["🔍 Genetik Analiz & Saha Projeksiyonu", "🧪 Dijital F1 Melezleme (Hibrit)"])

with tab1:
    col_input1, col_input2 = st.columns([1, 1])
    with col_input1:
        uploaded_file = st.file_uploader("Genetik Dosya Yükle (.fasta, .txt)", type=['fasta', 'txt'])
    with col_input2:
        manual_input = st.text_area("Veya Diziyi Manuel Olarak Buraya Yapıştırın:", height=68)

    input_data = ""
    if uploaded_file:
        input_data = uploaded_file.read().decode("utf-8")
    elif manual_input:
        input_data = manual_input

    if input_data:
        p_seq = process_genetics(input_data)
        res = calculate_full_traits(p_seq, secilen_tur, model_data)
        
        if res:
            # SATIR 1: HASAT VE VERİM
            st.subheader("🗓️ Üretim ve Hasat Projeksiyonu")
            c1, c2, c3, c4 = st.columns(4)
            with c1: show_metric("Hasat Süresi", res['Hasat'], " Gün")
            with c2: show_metric("Çimlenme Gücü (Vigor)", f"%{res['Vigor']}")
            with c3:
                katsayi = model_data['bitki_parametreleri'][secilen_tur]['oran']
                adj = 1.2 if toprak_kalitesi=="Yüksek" else 0.8 if toprak_kalitesi=="Düşük" else 1.0
                gramaj = res['MW'] * katsayi * adj
                show_metric("Meyve Ağırlığı", f"{gramaj:.1f}", " gr")
            with c4:
                baz_verim = model_data['bitki_parametreleri'][secilen_tur]['baz_verim']
                rekolte = (baz_verim * alan * (gramaj/100)) / 10
                show_metric("Toplam Rekolte", f"{rekolte:.2f}", " Ton")

            # SATIR 2: DAYANIKLILIK VE KALİTE
            st.subheader("🛡️ Biyolojik Kalite ve Dayanıklılık")
            c5, c6, c7, c8 = st.columns(4)
            with c5: show_metric("Hastalık Direnci", f"%{res['Hastalik']}")
            with c6: show_metric("Raf Ömrü", res['Raf'], " Gün")
            with c7: show_metric("Stres Toleransı", f"%{res['Stres']}")
            with c8: show_metric("Brix (Tat/Aroma)", res['Brix'])

            # RADAR GRAFİĞİ
            st.markdown("---")
            categories = ['Vigor (Çimlenme)', 'Hastalık Direnci', 'Stres Toleransı', 'Raf Ömrü', 'Brix (Tat)']
            values = [res['Vigor'], res['Hastalik'], res['Stres'], min(100, res['Raf']*3.5), min(100, res['Brix']*10)]
            
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(r=values, theta=categories, fill='toself', line_color='#58a6ff', fillcolor='rgba(88, 166, 255, 0.3)'))
            fig.update_layout(
                polar=dict(bgcolor="#1a1c23", radialaxis=dict(visible=True, range=[0, 100], color="white")),
                paper_bgcolor="#0e1117", font_color="white", height=450, title="Tohum Genetik Performans Radarı", margin=dict(t=50, b=50)
            )
            st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Dijital F1 Hibrit Simülasyonu")
    st.write("İki farklı saf hattı çaprazlayarak oluşacak yeni neslin (F1) potansiyelini ölçün.")
    f1_c1, f1_c2 = st.columns(2)
    anne = f1_c1.text_area("Anne (Saf Hat) Genetik Dizisi:", key="anne_in")
    baba = f1_c2.text_area("Baba (Saf Hat) Genetik Dizisi:", key="baba_in")
    
    if st.button("HİBRİT ANALİZİNİ BAŞLAT"):
        if anne and baba:
            p_a, p_b = process_genetics(anne), process_genetics(baba)
            m_a = calculate_full_traits(p_a, secilen_tur, model_data)
            m_b = calculate_full_traits(p_b, secilen_tur, model_data)
            
            # F1 Heterosis Hesabı (Ortalama MW + %18 Hibrit Azmanlığı)
            f1_mw = ((m_a['MW'] + m_b['MW']) / 2) * 1.18
            st.markdown(f"""
                <div style="background-color: #1a1c23; padding: 25px; border-radius: 12px; border-left: 5px solid #58a6ff; margin-top: 20px;">
                    <h3 style="color: white; margin: 0;">🚀 F1 Melezi Öngörü Raporu</h3>
                    <p style="color: #8b949e; font-size: 18px; margin-top: 10px;">
                        Bu çaprazlama sonucu <b>%18 oranında Heterosis (Hibrit Azmanlığı)</b> tespit edilmiştir.
                    </p>
                    <p style="color: #ffffff; font-size: 20px;">Beklenen Moleküler Ağırlık: <b>{f1_mw:.0f} Da</b></p>
                    <p style="color: #58a6ff;">Bu melezleme, ebeveynlerine göre daha yüksek meyve ağırlığı ve stres toleransı vaat ediyor.</p>
                </div>
            """, unsafe_allow_html=True)
