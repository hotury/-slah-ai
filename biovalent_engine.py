import numpy as np
from Bio.Seq import Seq
from sklearn.ensemble import RandomForestRegressor

class IslahAI:
    def __init__(self):
        self.PLANT_CONFIG = {
            "Domates": {"brix_weight": 0.45, "yield_weight": 12.0, "shelf_weight": 2.5},
            "Biber": {"brix_weight": 0.35, "yield_weight": 8.0, "shelf_weight": 3.0},
            "Hıyar": {"brix_weight": 0.20, "yield_weight": 15.0, "shelf_weight": 1.5},
            "Kabak": {"brix_weight": 0.25, "yield_weight": 14.0, "shelf_weight": 1.2},
            "Karpuz": {"brix_weight": 0.50, "yield_weight": 18.0, "shelf_weight": 2.0},
            "Kavun": {"brix_weight": 0.55, "yield_weight": 13.0, "shelf_weight": 1.8},
            "Patlıcan": {"brix_weight": 0.30, "yield_weight": 10.0, "shelf_weight": 2.2}
        }
        self.model = None
        self.is_trained = False

    def translate_dna(self, dna_sequence):
        try:
            coding_dna = Seq(dna_sequence.strip().upper().replace("\n", "").replace(" ", ""))
            return str(coding_dna.translate(to_stop=True))
        except Exception:
            return None

    def calculate_aa_metrics(self, protein_seq):
        if not protein_seq: return None
        seq_len = len(protein_seq)
        if seq_len == 0: return None
        
        # AA Frekans Analizi
        metrics = {
            "freq_sugar": sum(protein_seq.count(x) for x in "ST") / seq_len,
            "freq_growth": sum(protein_seq.count(x) for x in "LIV") / seq_len,
            "freq_stress": sum(protein_seq.count(x) for x in "P") / seq_len,
            "freq_defense": sum(protein_seq.count(x) for x in "RK") / seq_len,
            "length": seq_len
        }
        return metrics

    def train_field_model(self, df):
        # Eğitim için Protein_Seq ve Saha_Sonuc sütunları gerekir
        X = []
        for seq in df['Protein_Seq']:
            metrics = self.calculate_aa_metrics(seq)
            X.append(list(metrics.values()))
        
        y = df['Saha_Sonuc'].values
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.model.fit(X, y)
        self.is_trained = True

    def predict_performance(self, protein_seq, plant_type):
        metrics = self.calculate_aa_metrics(protein_seq)
        cfg = self.PLANT_CONFIG.get(plant_type, self.PLANT_CONFIG["Domates"])
        
        # Teorik Hesaplama
        theory_brix = 4.0 + (metrics["freq_sugar"] * 20 * cfg["brix_weight"])
        theory_yield = 50.0 + (metrics["freq_growth"] * 100 * cfg["yield_weight"] / 10)
        
        field_prediction = None
        if self.is_trained:
            features = np.array(list(metrics.values())).reshape(1, -1)
            field_prediction = self.model.predict(features)[0]
        
        return {
            "theory": {"Brix": round(theory_brix, 2), "Verim": round(theory_yield, 2)},
            "field_ai": round(field_prediction, 2) if field_prediction else None,
            "metrics": metrics
        }
