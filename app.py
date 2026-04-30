import streamlit as st
import pandas as pd
import numpy as np
from biovalent_algo import BiovalentEngine

st.set_page_config(page_title="Biovalent AI | Admin", layout="wide")

# Sistemi sadece ilk açılışta yükle
if 'engine' not in st.session_state:
    st.session_state.engine = BiovalentEngine()

st.title("🛡️ Biovalent AI - Islah Kontrol Paneli")

# 1. VERİ YÜKLEME BÖLÜMÜ
with st.expander("📁 Şirket Veri Entegrasyonu (AI Eğitimi)", expanded=True):
    st.markdown("Saha verilerinizi içeren CSV dosyasını yükleyin. CSV içinde **Field_Brix** ve **Field_Yield** adlı iki sütun olması zorunludur.")
    uploaded_file = st.file_uploader("CSV Dosyası Yükle", type="csv")
    
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            st.dataframe(df.head(3), use_container_width=True)
            if st.button("Saha Verisiyle Modeli Güncelle"):
                expected_snps = st.session_state.engine.train_field_ai(df)
                st.session_state.expected_snps = expected_snps
                st.success(f"✅ Yapay Zeka tarlanızı tanıdı! Model {expected_snps} adet SNP genotipi için kalibre edildi.")
        except Exception as e:
            st.error(f"Veri yükleme hatası. Sütun adlarını kontrol edin. Hata detayı: {e}")

# 2. GENETİK YORUMLAMA BÖLÜMÜ
st.subheader("🧬 Gen Haritası Yorumlama")
st.markdown("Örnek 20 SNP formatı: `1,2,0,1,2,0,1,1,2,0,1,0,2,1,0,2,1,0,2,1`")
raw_dna = st.text_input("Tohum SNP Verisi (Virgülle ayırın):", "1,2,0,1,2,0,1,1,2,0,1,0,2,1,0,2,1,0,2,1")

if st.button("Analiz Et"):
    try:
        # Gelen metni rakam dizisine çevir
        dna_vec = np.array([int(x.strip()) for x in raw_dna.split(",")])
        
        # Eğer AI eğitilmişse, DNA uzunluğu CSV'deki kolon sayısına eşit olmalı
        if 'expected_snps' in st.session_state and len(dna_vec) != st.session_state.expected_snps:
            st.warning(f"⚠️ Eğittiğiniz CSV dosyasında {st.session_state.expected_snps} adet SNP kolonu vardı. Siz analize {len(dna_vec)} adet girdiniz. Lütfen sayıları eşitleyin.")
        else:
            res = st.session_state.engine.predict_hybrid(dna_vec)
            
            st.markdown("### 📊 Analiz Sonuçları")
            col1, col2, col3 = st.columns(3)
            
            # Kayıp hesaplamaları
            diff_brix = res['theory']['lab_brix'] - res['field']['brix']
            col1.metric(
                label="Laboratuvar (Brix) -> Saha", 
                value=f"{res['field']['brix']} Brix", 
                delta=f"-{round(diff_brix, 2)} Kayıp", 
                delta_color="inverse"
            )
            
            diff_yield = res['theory']['lab_yield'] - res['field']['yield']
            col2.metric(
                label="Laboratuvar (Verim) -> Saha", 
                value=f"{res['field']['yield']} Ton/Ha", 
                delta=f"-{round(diff_yield, 2)} Kayıp", 
                delta_color="inverse"
            )
            
            col3.metric("Teorik Raf Ömrü", f"{res['theory']['shelf_life']} Gün")

            # BURSA GEN YORUMLAMA
            st.markdown("---")
            st.markdown("### 🔬 Bursa Gen Yorumlama / Darboğaz Analizi")
            
            if len(dna_vec) >= 19 and dna_vec[18] == 2:
                st.error("⚠️ **Biyokimyasal Uyarı (SNP_18):** Molekül ağırlığı eşiği aşıldı. Protein katlanmasındaki metabolik yük nedeniyle verimde %18 biyolojik ceza uygulandı.")
            elif len(dna_vec) >= 5 and dna_vec[4] == 2:
                st.warning("⚠️ **Asidite Uyarısı (SNP_4):** pH dengesinde kayma tespit edildi. Şeker/Asit oranı bozulduğu için Brix potansiyelinde %15 biyolojik kayıp var.")
            elif diff_brix > 2.0 or diff_yield > 20.0:
                st.info("📉 **Saha İklim Uyarısı:** Biyolojik tavanınız yüksek olmasına rağmen yapay zeka saha verilerinizde ciddi bir düşüş öngörüyor. Tarlanızdaki çevresel stres (sıcaklık/su) genetiği baskılıyor.")
            else:
                st.success("✅ **Genotip Onayı:** Bu genetik dizilim tarlanızın çevresel şartlarıyla yüksek uyum gösteriyor. Stabilite mükemmel.")
                
    except ValueError:
        st.error("Hata: Lütfen harf kullanmayın, sadece rakamları aralarında virgül bırakarak yazın.")
