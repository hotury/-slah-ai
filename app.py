# app.py
import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, roc_auc_score
import joblib

# 1. dosya yolları
DATA_DIR = "data"
MODEL_FILE = "biovalent.pkl"

# 2. veri yükle
def load_data():
    X_df = pd.read_csv(os.path.join(DATA_DIR, "marker_matrix.csv"), index_col="GENOTYPE")
    y_df = pd.read_csv(os.path.join(DATA_DIR, "phenotype_data.csv"), index_col="GENOTYPE")
    idx = X_df.index.intersection(y_df.index)
    X = X_df.loc[idx].values
    y = y_df.loc[idx]
    return X, y, list(y.columns)

# 3. model eğitimi + tahmin fonksiyonu
def train_and_save_model():
    X, y, trait_names = load_data()

    # 3.1. test/train split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # 3.2. scaler
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # 3.3. modeller ve metrikler
    models = {}
    metrics = {}

    for trait in trait_names:
        if "DISEASE" in trait.upper():
            m = RandomForestClassifier(n_estimators=100, random_state=42)
            m.fit(X_train_scaled, (y_train[trait] > 0.5).astype(int))
            prob = m.predict_proba(X_test_scaled)[:, 1]
            a = (y_test[trait] > 0.5).astype(int)
            auc = roc_auc_score(a, prob)
            metrics[trait] = {"auc": auc}
        else:
            m = Ridge(alpha=1.0)
            m.fit(X_train_scaled, y_train[trait])
            pred = m.predict(X_test_scaled)
            r2 = r2_score(y_test[trait], pred)
            metrics[trait] = {"r2": r2}
        models[trait] = m

    # 3.4. modeli kaydet (AI modeli)
    model_data = {
        "scalers": {"X_scaler": scaler},
        "traits_model": models,
        "trait_names": trait_names,
        "metrics": metrics,
    }
    joblib.dump(model_data, MODEL_FILE)
    print("✅ Model eğitildi ve biovalent.pkl olarak kaydedildi.")
    print("Metrics:", metrics)

# 4. tahmin fonksiyonu
def predict(genotype_vector):
    """
    genotype_vector: [SNP1, SNP2, ...] şeklinde bir liste (SNP sayısı: X.shape[1])
    """
    model_data = joblib.load(MODEL_FILE)
    X = np.array([genotype_vector], dtype=float)
    X_scaled = model_data["scalers"]["X_scaler"].transform(X)

    preds = {}
    for trait, m in model_data["traits_model"].items():
        if "DISEASE" in trait.upper():
            prob = m.predict_proba(X_scaled)[0, 1]
            preds[trait] = prob * 100  # 0–100
        else:
            pred = m.predict(X_scaled)[0]
            preds[trait] = pred

    return preds

# 5. programı çalıştır
if __name__ == "__main__":
    # 5.1. modeli eğit (firma ilk kez çalıştırdığında)
    train_and_save_model()
    # 5.2. örnek genotip tahmini
    example_markevector = [0, 1, 2, 0, 1]  # marker_matrix.csv’deki 5 SNP’ler için örnek
    results = predict(example_markevector)
    print("🌈 Örnek Tahmin Sonuçları:")
    for trait, value in results.items():
        print(f"  {trait}: {value:.2f}")
Bu sistem nasıl
