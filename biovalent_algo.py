import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

class BiovalentEngine:
    def __init__(self):
        # 🧬 PROTEİN SÖZLÜĞÜ: SNP'den Amino Asit Değişimine ve Biyolojik Etkiye Geçiş
        # Bu kısım senin "+1 Tarım" vizyonunla akademik olarak dolacak yerdir.
        self.GENE_MAP = {
            0: {"gene": "LIN5", "protein": "Apoplastic Invertase", "aa_change": "Asn -> Asp", "effect": "brix", "power": 0.4},
            4: {"gene": "ALMT9", "protein": "Malate Transporter", "aa_change": "Glu -> Val", "effect": "acidity", "power": -0.15},
            10: {"gene": "FW2.2", "protein": "Cell Division Regulator", "aa_change": "Cys -> Tyr", "effect": "weight", "power": 12.0},
            18: {"gene": "HSP70", "protein": "Heat Shock Protein", "aa_change": "Pro -> Leu", "effect": "tolerance", "power": 0.20}
        }
        
        self.model_brix = RandomForestRegressor(n_estimators=100, random_state=42)
        self.model_yield = RandomForestRegressor(n_estimators=100, random_state=42)
        self.is_trained = False

    def calculate_biochemical_potential(self, snp_array):
        """SNP'den Amino Asit ve Hücre Fonksiyonu Yorumlaması Yapan Motor"""
        results = {
            "lab_brix": 5.0,
            "lab_yield": 70.0,
            "tolerance_score": 1.0,
            "protein_reports": []
        }

        for idx, val in enumerate(snp_array):
            if idx in self.GENE_MAP and val > 0:
                gene_info = self.GENE_MAP[idx]
                impact = gene_info["power"] * val
                
                # Amino Asit Seviyesinde Yorumlama
                report = {
                    "gene": gene_info["gene"],
                    "protein": gene_info["protein"],
                    "change": gene_info["aa_change"],
                    "impact": impact
                }
                
                # Etkiyi ilgili parametreye işle
                if gene_info["effect"] == "brix":
                    results["lab_brix"] += impact
                elif gene_info["effect"] == "weight":
                    results["lab_yield"] += (impact * 5) # Ağırlık verimi artırır
                elif gene_info["effect"] == "acidity":
                    results["lab_brix"] *= (1 + impact) # Asidite lezzeti (brix algısını) bozar
                elif gene_info["effect"] == "tolerance":
                    results["tolerance_score"] += impact

                results["protein_reports"].append(report)

        return results

    def predict_hybrid(self, snp_array):
        # 1. Biyokimyasal Analiz (AA Tabanlı)
        bio_data = self.calculate_biochemical_potential(snp_array)
        
        # 2. Saha Kalibrasyonu (Eğer eğitilmişse AI devreye girer)
        if self.is_trained:
            field_brix = self.model_brix.predict([snp_array])[0]
            field_yield = self.model_yield.predict([snp_array])[0]
        else:
            # Saha verisi yoksa biyokimyasal potansiyelin %75'ini gerçekçi kabul et
            field_brix = bio_data["lab_brix"] * 0.75
            field_yield = bio_data["lab_yield"] * 0.75
            
        return {
            "theory": bio_data,
            "field": {"brix": round(field_brix, 2), "yield": round(field_yield, 2)}
        }

    def train_field_ai(self, df):
        feature_cols = [col for col in df.columns if col not in ['Field_Brix', 'Field_Yield']]
        X = df[feature_cols].values
        y_b = df['Field_Brix'].values
        y_y = df['Field_Yield'].values
        self.model_brix.fit(X, y_b)
        self.model_yield.fit(X, y_y)
        self.is_trained = True
