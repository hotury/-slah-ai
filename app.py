# 1. gerekli paketler
import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, roc_auc_score
import joblib

# 2. dosya yolları
DATA_DIR = "data"
OWN_MODEL_FILE = "own_biovalent.pkl"
LIBRARY_MODEL_FILE = "lib_biovalent.pkl"  # bizim kendi eğittiğimiz model

# 3. veri yükle
def load_data():
    X_df = pd.read_csv(os.path.join(DATA_DIR, "marker_matrix.csv"), index_col="GENOTYPE")
    y_df = pd.read_csv(os.path.join(DATA_DIR, "phenotype_data.csv"), index_col="GENOTYPE")
    idx = X_df.index.intersection(y_df.index)
    X = X_df.loc[idx].values
    y = y_df.loc[idx]
    return X, y, list(y.columns)

# 4. model eğitimi (kendi modeli)
def train_own_model():
    X, y, trait_names = load_data()

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

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

    model_data = {
        "scalers": {"X_scaler": scaler},
        "traits_model": models,
        "trait_names": trait_names,
        "metrics": metrics,
    }
    joblib.dump(model_data, OWN_MODEL_FILE)
    print("✅ Firma kendi AI modeli eğitildi ve own_biovalent.pkl kaydedildi.")
    print("Metrics:", metrics)

# 5. model eğitimi (kütüphane modeli)
def train_library_model():
    X, y, trait_names = load_data()

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

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

    model_data = {
        "scalers": {"X_scaler": scaler},
        "traits_model": models,
        "trait_names": trait_names,
        "metrics": metrics,
    }
    joblib.dump(model_data, LIBRARY_MODEL_FILE)
    print("✅ Kütüphane AI modeli eğitildi ve lib_biovalent.pkl kaydedildi.")
    print("Metrics:", metrics)

# 6. tahmin (kendi modelle)
def predict_own(genotype_vector):
    model_data = joblib.load(OWN_MODEL_FILE)
    X = np.array([genotype_vector], dtype=float)
    X_scaled = model_data["scalers"]["X_scaler"].transform(X)

    preds = {}
    for trait, m in model_data["traits_model"].items():
        if "DISEASE" in trait.upper():
            prob = m.predict_proba(X_scaled)[0, 1]
            preds[trait] = prob * 100
        else:
            pred = m.predict(X_scaled)[0]
            preds[trait] = pred
    return preds

# 7. tahmin (kütüphane modelle)
def predict_lib(genotype_vector):
    model_data = joblib.load(LIBRARY_MODEL_FILE)
    X = np.array([genotype_vector], dtype=float)
    X_scaled = model_data["scalers"]["X_scaler"].transform(X)

    preds = {}
    for trait, m in model_data["traits_model"].items():
        if "DISEASE" in trait.upper():
            prob = m.predict_proba(X_scaled)[0, 1]
            preds[trait] = prob * 100
        else:
            pred = m.predict(X_scaled)[0]
            preds[trait] = pred
    return preds

# 8. program çalıştır
if __name__ == "__main__":
    train_library_model()  # senin kendi AI modeli
    train_own_model()      # firma kendi AI modeli

    example_markevector = [0, 1, 2, 0, 1]
    own_results = predict_own(example_markevector)
    lib_results = predict_lib(example_markevector)

    print("Firma kendi AI modeliyle tahmin:")
    for trait, value in own_results.items():
        print(f"  {trait}: {value:.2f}")

    print("Kütüphane AI modeliyle tahmin:")
    for trait, value in lib_results.items():
        print(f"  {trait}: {value:.2f}")
