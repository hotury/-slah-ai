import numpy as np
import pandas as pd
from Bio.Seq import Seq
from sklearn.ensemble import RandomForestRegressor

class IslahAI:
    def __init__(self):
        # Ürün Bazlı Katsayılar (Örn: Domates için şeker katsayısı farklıdır)
        self.PLANT_CONFIG = {
            "Domates": {"brix_weight": 0.45, "yield_weight": 12.0, "shelf_weight": 2.5},
            "Biber": {"brix_weight": 0.35, "yield_weight": 8.0, "shelf_weight": 3.0},
            "Hıyar": {"brix_weight": 0.20, "yield_weight": 15.0, "shelf_weight": 1.5},
            # Diğer bitkiler (Kavun, Karpuz vb.) buraya eklenebilir
        }
        self.model = None
        self.is_trained = False

    def translate_dna(self, dna_sequence):
        """DNA dizisini Protein dizisine çevirir."""
        try:
            coding_dna = Seq(dna_sequence.strip().upper())
            return str(coding_dna.translate(to_stop=True))
        except:
            return None

    def calculate_aa_metrics(self, protein_seq):
        """Amino asit frekanslarından biyokimyasal metrikler üretir."""
        if not protein_seq: return None
        
        seq_len = len(protein_seq)
        # Kritik AA Grupları
        sugar_aa = sum(protein_seq.count(x) for x in "ST") # Serin, Treonin (Glikozilasyon)
        growth_aa = sum(protein_seq.count(x) for x in "LIV") # Hidrofobik (Yapısal güç)
        stress_aa = sum(protein_seq.count(x) for x in "P") # Prolin (Stres direnci)
        
        return {
            "freq_sugar": sugar_aa / seq_len,
            "freq_growth": growth_aa / seq_len,
            "freq_stress": stress_aa / seq_len,
            "length": seq_len
        }

    def train_field_model(self, df):
        """Şirketin kendi saha verisiyle AI'yı eğitir."""
        # Veride 'Protein_Seq' ve 'Saha_Brix' gibi sütunlar beklenir
        X = []
        for seq in df['Protein_Seq']:
            metrics = self.calculate_aa_metrics(seq)
            X.append(list(metrics.values()))
        
        y = df['Saha_Sonuc'].values
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.model.fit(X, y)
        self.is_trained = True

    def predict_performance(self, protein_seq, plant_type):
        """Teorik potansiyel vs Saha performansı karşılaştırması."""
        metrics = self.calculate_aa_metrics(protein_seq)
        cfg = self.PLANT_CONFIG.get(plant_type, self.PLANT_CONFIG["Domates"])
        
        # 1. Laboratuvar (Teorik) Hesaplama
        theory_brix = 4.0 + (metrics["freq_sugar"] * 20 * cfg["brix_weight"])
        theory_yield = 50.0 + (metrics["freq_growth"] * 100 * cfg["yield_weight"] / 10)
        
        # 2. AI (Saha) Tahmini
        field_prediction = None
        if self.is_trained:
            features = np.array(list(metrics.values())).reshape(1, -1)
            field_prediction = self.model.predict(features)[0]
        
        return {
            "theory": {"Brix": round(theory_brix, 2), "Verim": round(theory_yield, 2)},
            "field_ai": round(field_prediction, 2) if field_prediction else None,
            "metrics": metrics
        }
