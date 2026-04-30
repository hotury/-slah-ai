# BIYOLOJIK_BEYIN.py - Multi-Crop (Domates/Biber/Hıyar/Kabak/Karpuz/Kavun)
import numpy as np
from collections import Counter
from sklearn.ensemble import RandomForestRegressor
from Bio.Seq import Seq
import joblib
import os
import pandas as pd

class BiyolojikBeyin:
    def __init__(self, crop_type='Domates', custom_model_path=None):
        self.crop_type = crop_type
        self.custom_model = None
        if custom_model_path and os.path.exists(custom_model_path):
            self._load_custom_model(custom_model_path)
        else:
            self.models = self._multi_crop_models()
    
    def _load_custom_model(self, path):
        """Şirket kendi modeli yükler"""
        self.custom_model = joblib.load(path)
        self.is_custom = True
    
    def _multi_crop_models(self):
        """5 Bitki için ayrı modeller (1500 genotip/crop)"""
        np.random.seed(42)
        n_snps, n_geno = 1500, 1200
        
        snps = np.random.binomial(1, 0.3, (n_geno, n_snps))
        
        models = {}
        
        if self.crop_type == 'Domates':
            brix = np.clip(7.5 + snps[:,:300].sum(1)*0.016 + np.random.normal(0,0.9,n_geno), 6, 15)
            verim = np.clip(8.0 + snps[:,300:700].sum(1)*0.011 + np.random.normal(0,1.2,n_geno), 4, 18)
        elif self.crop_type == 'Biber':
            brix = np.clip(6.8 + snps[:,:250].sum(1)*0.018 + np.random.normal(0,0.8,n_geno), 5.5, 12)
            verim = np.clip(6.2 + snps[:,250:650].sum(1)*0.013 + np.random.normal(0,1.0,n_geno), 3.5, 14)
        elif self.crop_type == 'Hıyar':
            brix = np.clip(5.5 + snps[:,:200].sum(1)*0.02 + np.random.normal(0,0.7,n_geno), 4.5, 10)
            verim = np.clip(12.5 + snps[:,200:600].sum(1)*0.008 + np.random.normal(0,1.5,n_geno), 8, 22)
        elif self.crop_type == 'Kabak':
            brix = np.clip(6.2 + snps[:,:220].sum(1)*0.017 + np.random.normal(0,0.85,n_geno), 5, 11)
            verim = np.clip(15.0 + snps[:,220:620].sum(1)*0.009 + np.random.normal(0,2.0,n_geno), 10, 28)
        elif self.crop_type == 'Karpuz':
            brix = np.clip(8.5 + snps[:,:350].sum(1)*0.014 + np.random.normal(0,1.1,n_geno), 7, 13)
            verim = np.clip(25.0 + snps[:,350:850].sum(1)*0.006 + np.random.normal(0,3.5,n_geno), 15, 45)
        else:  # Kavun
            brix = np.clip(9.2 + snps[:,:380].sum(1)*0.013 + np.random.normal(0,1.2,n_geno), 7.5, 14)
            verim = np.clip(18.0 + snps[:,380:880].sum(1)*0.007 + np.random.normal(0,2.8,n_geno), 12, 35)
        
        model_brix = RandomForestRegressor(n_estimators=400, max_depth=12, random_state=42)
        model_verim = RandomForestRegressor(n_estimators=400, max_depth=12, random_state=42)
        
        model_brix.fit(snps, brix)
        model_verim.fit(snps, verim)
        
        return {
            'brix': model_brix, 'verim': model_verim,
            'is_trained': True
        }
    
    def train_custom(self, training_csv):
        """Şirket CSV'si ile yeniden eğit"""
        df = pd.read_csv(training_csv)
        X = np.array(df['snp_profile'].tolist())
        y_brix = df['Brix'].values
        y_verim = df['Verim'].values
        
        model_b = RandomForestRegressor(n_estimators=500, random_state=42)
        model_v = RandomForestRegressor(n_estimators=500, random_state=42)
        
        model_b.fit(X, y_brix)
        model_v.fit(X, y_verim)
        
        self.custom_model = {'brix': model_b, 'verim': model_v}
        self.is_custom = True
        return "Custom model trained!"
    
    def dna_to_snp(self, dna):
        """DNA → 1500 SNP profile"""
        profile = np.zeros(1500)
        for i, pos in enumerate(range(1500)):
            idx = int(pos * 1000) % len(dna)
            if idx < len(dna):
                profile[i] = 1 if dna[idx] in 'AG' else 0
        return profile
    
    def predict(self, dna_seq):
        """Multi-crop prediction"""
        snp_profile = self.dna_to_snp(dna_seq)
        
        if self.custom_model:
            brix = self.custom_model['brix'].predict(snp_profile.reshape(1,-1))[0]
            verim = self.custom_model['verim'].predict(snp_profile.reshape(1,-1))[0]
            source = "Custom Model"
        else:
            brix = self.models['brix'].predict(snp_profile.reshape(1,-1))[0]
            verim = self.models['verim'].predict(snp_profile.reshape(1,-1))[0]
            source = f"{self.crop_type} Base"
        
        # Protein analysis
        protein = str(Seq(dna_seq[:5000]).translate(to_stop=True))
        glu = Counter(protein).get('E', 0) / max(len(protein), 1) * 100
        
        return {
            'Brix': round(brix + glu * 0.06, 2),
            'Verim': round(verim, 2),
            'Glu': round(glu, 1),
            'SNPHit': int(snp_profile.sum()),
            'Model': source
        }

# Global instance
beyin = None  # App'de init
