import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

class BiovalentEngine:
    def __init__(self):
        # Biyokimyasal Parametreler
        self.PARAMS = {
            "max_brix": 12.5,
            "max_yield": 160.0,
            "optimal_ph": 6.5
        }
        self.model_brix = RandomForestRegressor(n_estimators=100, random_state=42)
        self.model_yield = RandomForestRegressor(n_estimators=100, random_state=42)
        self.is_trained = False

    def calculate_biochemical_potential(self, snp_array):
        # Hata önleme: Kullanıcı 20'den az gen girerse sonunu 0 ile doldur
        if len(snp_array) < 20:
            snp_array = np.pad(snp_array, (0, 20 - len(snp_array)), 'constant')

        theo_brix = 4.5 + (np.sum(snp_array[:8]) * 0.4)
        theo_yield = 65.0 + (np.sum(snp_array[8:18]) * 4.5)
        
        # --- BİYOLOJİK KURALLAR ---
        # SNP_18: Ağır molekül cezası
        if snp_array[18] == 2:
            theo_yield *= 0.82 
        # SNP_4: pH bozulma cezası
        if snp_array[4] == 2:
            theo_brix *= 0.85 
            
        shelf_life_days = 7 + (np.sum(snp_array[15:20]) * 2)
        
        return {
            "lab_brix": round(min(theo_brix, self.PARAMS["max_brix"]), 2),
            "lab_yield": round(min(theo_yield, self.PARAMS["max_yield"]), 2),
            "shelf_life": int(shelf_life_days)
        }

    def train_field_ai(self, df):
        # Field_Brix ve Field_Yield hariç tüm sütunları DNA (SNP) olarak kabul et
        feature_cols = [col for col in df.columns if col not in ['Field_Brix', 'Field_Yield']]
        X = df[feature_cols].values
        y_b = df['Field_Brix'].values
        y_y = df['Field_Yield'].values
        
        self.model_brix.fit(X, y_b)
        self.model_yield.fit(X, y_y)
        self.is_trained = True
        
        return len(feature_cols) # Modelin kaç genle eğitildiğini döndürür

    def predict_hybrid(self, snp_array):
        lab = self.calculate_biochemical_potential(snp_array)
        
        if self.is_trained:
            field_brix = self.model_brix.predict([snp_array])[0]
            field_yield = self.model_yield.predict([snp_array])[0]
        else:
            field_brix = lab["lab_brix"] * 0.7
            field_yield = lab["lab_yield"] * 0.7
            
        return {
            "theory": lab,
            "field": {"brix": round(field_brix, 2), "yield": round(field_yield, 2)}
        }
