import streamlit as st
import pandas as pd
import joblib
import plotly.graph_objects as go
from Bio.Seq import Seq
import io

# Sayfa Ayarları
st.set_page_config(page_title="Biovalent Sentinel Pro", page_icon="🧬", layout="wide")

# --- ÖZEL TASARIM (CSS) ---
# Siyah kutular ve beyaz yazılar için özelleştirilmiş tasarım
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stApp { background-color: #0e1117; }
    
    /* Veri Kutucukları (Cards) */
    .metric-card {
        background-color: #1a1c23;
        border: 1px solid #30363d;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 10px;
    }
    .metric-value {
        font-size: 24px;
        font-weight: bold;
        color: #ffffff;
    }
    .metric-label {
        font-size: 14px;
        color: #8b949e;
        margin-top: 5px;
    }
    
    /* Tablo ve Sekme Düzenlemeleri */
    .stTabs [data-baseweb="tab-list"] { gap: 24px; background-color: #0e1117; }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        color: #8b949e;
        font-weight: 600;
    }
    .stTabs [data-baseweb="tab"]:hover { color: white; }
    .stTabs [aria-selected="true"] { color: #58a6ff !important; border-bottom-color: #58a6ff !important; }
    
    /* Input Alanları */
    .stTextArea textarea { background-color: #0d1117; color: white; border: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

# --- FONKSİYONLAR ---

def dna_to_protein(dna_sequence):
    """DNA dizisini proteine çevirir."""
    try:
        dna_seq = Seq(dna_sequence.strip().upper().replace(" ", ""))
        return str(dna_seq.translate(to_stop=True))
    except Exception:
        return None

def calculate_biological_metrics(protein_seq):
    """Biyofiziksel kurallarla bitki parametrelerini hesaplar."""
    if not protein_seq: return None
    
    length = len(protein_seq)
    # 1. Moleküler Ağırlık (Dalton)
    mw = length * 110.1
    
    # 2. Raf Ömrü (İnstabilite İndeksi Yaklaşımı)
    # Prolin ve Valin dengesi üzerinden stabilite tahmini
    stability = (protein_seq.count('P') + protein_seq.count('V')) / length
    raf_omru = 10 + (stability * 120)
    
    # 3. Hastalık Dayanımı (Sistein ve Disülfit Köprüleri)
    cys_count = protein_seq.count('C')
    hastalik_skoru = min(100, (cys_count / length) * 600 + 35)
    
    # 4. Kuraklık Toleransı (Hidropati/Alifatik İndeks)
    alifatik = (protein_seq.count('A') + protein_seq.count('I') + protein_seq.count('L')) / length
    kuraklik_skoru = min(100, alifatik * 300)
    
    # 5. Brix (Tat ve Aroma Potansiyeli)
    aroma_factor = (protein_seq.count('E') + protein_seq.count('D') + protein_seq.count('Q')) / length
    brix_potansiyeli = 3.5 + (aroma_factor * 25)
    
    return {
        "MW": mw,
        "Raf_Omru": round(raf_omru, 1),
        "Hastalik": round(hastalik_skoru, 1),
        "Kuraklik": round(kuraklik_skoru, 1),
        "Brix": round(brix_potansiyeli, 2)
    }

def show_metric_card(label, value, unit=""):
    """Havalı siyah kutucuk tasarımı."""
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{value}{unit}</div>
            <div class="metric-label">{label}</div>
        </div>
    """, unsafe_allow_html=True)

# --- MODEL YÜKLEME ---
try:
    model_data = joblib.load('biovalent_final.pkl')
    st.sidebar.success("✅ Islah Motoru Hazır")
except:
    st.sidebar.error("❌ 'biovalent_final.pkl' dosyası eksik!")
    st.stop()

# --- ANA EKRAN ---
st.title("🧬 Biovalent Sentinel")
st.markdown("Genetik Haritadan Geleceğin Hasadına: Dijital Islah İstasyonu")

tab1, tab2, tab3 = st.tabs(["🔍 Genetik Analiz", "🧪 F1 Melezleme (Hibrit)", "📊 Verim Tahmini"])

with tab1:
    st.subheader("Biyolojik Profil Çıkarımı")
    input_type = st.radio("Veri Giriş Yöntemi:", ["Dosya Yükle (.txt, .fasta)", "Manuel Giriş"], horizontal=True)
    
    raw_data = ""
    if input_type == "Dosya Yükle (.txt, .fasta)":
        uploaded_file = st.file_uploader("Laboratuvar Dosyasını Seçin", type=['txt', 'fasta'])
        if uploaded_file:
            raw_data = uploaded_file.read().decode("utf-8")
            if ">" in raw_data: # FASTA formatı kontrolü
                raw_data = raw_data.split('\n', 1)[-1].replace('\n', '').replace('\r', '')
    else:
        raw_data = st.text_area("DNA veya Protein Dizisini Buraya Yapıştırın:", height=150)

    if raw_data:
        # DNA/Protein Tespiti ve Çeviri
        is_dna = all(c in "ATGCN " for c in raw_data.strip().upper()[:20])
        if is_dna:
            p_seq = dna_to_protein(raw_data)
            st.info("🧬 DNA dizisi tespit edildi, proteine çevrildi.")
        else:
            p_seq = raw_data.strip().upper()
        
        metrics = calculate_biological_metrics(p_seq)
        
        if metrics:
            # Havalı Veri Kutucukları
            m1, m2, m3, m4, m5 = st.columns(5)
            with m1: show_metric_card("Mol. Ağırlık", f"{metrics['MW']:.0f}", " Da")
            with m2: show_metric_card("Raf Ömrü", metrics['Raf_Omru'], " Gün")
            with m3: show_metric_card("Hastalık Direnci", f"%{metrics['Hastalik']}")
            with m4: show_metric_card("Kuraklık Eşiği", f"%{metrics['Kuraklik']}")
            with m5: show_metric_card("Brix (Tat)", metrics['Brix'])

            # Radar Grafiği
            categories = ['Raf Ömrü', 'Hastalık Dayanımı', 'Kuraklık Toleransı', 'Brix (Tat)']
            values = [min(100, metrics['Raf_Omru']*3), metrics['Hastalik'], metrics['Kuraklik'], min(100, metrics['Brix']*10)]
            
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(r=values, theta=categories, fill='toself', line_color='#58a6ff'))
            fig.update_layout(
                polar=dict(bgcolor="#1a1c23", radialaxis=dict(visible=True, range=[0, 100], color="white")),
                paper_bgcolor="#0e1117", font_color="white", showlegend=False, title="Genetik Karakter Radarı"
            )
            st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Dijital F1 Hibrit Simülasyonu")
    st.write("Anne ve Baba hatlarını sanal ortamda çaprazlayarak melez gücünü (heterosis) ölçün.")
    
    col_a, col_b = st.columns(2)
    a_dna = col_a.text_area("Anne (Saf Hat) Dizisi:", key="a_dna")
    b_dna = col_b.text_area("Baba (Saf Hat) Dizisi:", key="b_dna")
    
    if st.button("HİBRİT ANALİZİ YAP"):
        if a_dna and b_dna:
            # Basit F1 Mantığı: Ebeveyn MW ortalaması + %18 Heterosis
            p_a = dna_to_protein(a_dna) if "A" in a_dna[:5].upper() else a_dna
            p_b = dna_to_protein(b_dna) if "A" in b_dna[:5].upper() else b_dna
            
            mw_a = len(p_a) * 110.1
            mw_b = len(p_b) * 110.1
            f1_mw = ((mw_a + mw_b) / 2) * 1.18 # %18 hibrit azmanlığı
            
            st.markdown(f"""
                <div style="background-color: #1a1c23; padding: 20px; border-radius: 10px; border-left: 5px solid #58a6ff;">
                    <h3 style="color: white; margin: 0;">F1 Melezi Öngörüsü</h3>
                    <p style="color: #8b949e;">Bu çaprazlama sonucu beklenen Moleküler Ağırlık: <b>{f1_mw:.0f} Da</b></p>
                    <p style="color: #58a6ff;">🚀 Tahmini Verim Artışı (Heterosis): %18</p>
                </div>
            """, unsafe_allow_html=True)

with tab3:
    st.subheader("Saha Projeksiyonu")
    if 'metrics' in locals():
        with st.sidebar:
            st.header("🌍 Saha Koşulları")
            tür = st.selectbox("Bitki Türü", list(model_data['bitki_parametreleri'].keys()))
            alan = st.number_input("Ekili Alan (Dönüm)", value=1, min_value=1)
            is_good_soil = st.checkbox("Yüksek Verimli Toprak", value=True)

        katsayı = model_data['bitki_parametreleri'][tür]['oran']
        baz = model_data['bitki_parametreleri'][tür]['baz_verim']
        
        gramaj = metrics['MW'] * katsayı
        if is_good_soil: gramaj *= 1.1
        
        toplam_tonaj = (baz * alan * (gramaj/100)) / 10

        c1, c2 = st.columns(2)
        with c1: show_metric_card("Tahmini Meyve Ağırlığı", f"{gramaj:.1f}", " gr")
        with c2: show_metric_card("Toplam Rekolte", f"{toplam_tonaj:.2f}", " Ton")
    else:
        st.warning("Lütfen önce 'Genetik Analiz' sekmesinden bir dizi yükleyin.")
