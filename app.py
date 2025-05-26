from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
import pandas as pd
import joblib
import numpy as np
from tensorflow.keras.models import model_from_json, Model
from sklearn.preprocessing import StandardScaler
from datetime import datetime
from typing import List
from fastapi.responses import JSONResponse
from fastapi import FastAPI, UploadFile, File
import matplotlib.pyplot as plt
import seaborn as sns
import os
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, f1_score, classification_report, confusion_matrix
import tensorflow as tf
from tensorflow.keras.layers import Input, Dense
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from fastapi.staticfiles import StaticFiles
import json

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


csv_path = '/home/hanan/Desktop/Hybrid_IDS/AI_IDS/network/dataset/bin_data.csv'
config_path = '/home/hanan/Desktop/Hybrid_IDS/AI_IDS/network/autoencoder_model/config.json'
weights_path = '/home/hanan/Desktop/Hybrid_IDS/AI_IDS/network/model/autoencoder_model/model.weights.h5'
attack_cat_path = '/home/hanan/Desktop/Hybrid_IDS/AI_IDS/network/dataset/attack_cat__encoder.pkl'
state_path = '/home/hanan/Desktop/Hybrid_IDS/AI_IDS/network/dataset/state__encoder.pkl'
threshold = 0.075

def predict_with_autoencoder(csv_file_path, config_path, weights_path,
                              attack_cat_path, state_path, row_indices, threshold=0.075):
    print("📦 Loading Autoencoder model...")
    with open(config_path, 'r') as f:
        model_json = f.read()
    autoencoder = model_from_json(model_json)
    autoencoder.load_weights(weights_path)
    print("✅ Model and weights loaded successfully!")

    print("📦 Loading encoders...")
    attack_cat_encoder = joblib.load(attack_cat_path)
    state_encoder = joblib.load(state_path)

    print(f"📄 Reading data from: {csv_file_path}")
    df = pd.read_csv(csv_file_path)

    if not np.issubdtype(df['attack_cat'].dtype, np.number):
        print("⚠️ Column 'attack_cat' is not encoded. Encoding now...")
        df['attack_cat'] = attack_cat_encoder.transform(df['attack_cat'])

    if 'state' in df.columns and not np.issubdtype(df['state'].dtype, np.number):
        print("⚠️ Column 'state' is not encoded. Encoding now...")
        df['state'] = state_encoder.transform(df['state'])

    # Remove 'label' from the features list as it is not an input to the autoencoder
    features = ['ct_src_dport_ltm', 'rate', 'dwin', 'dload', 'swin',
                'ct_dst_sport_ltm', 'ct_state_ttl', 'id',
                'attack_cat', 'sttl', 'state'] # 'label' removed here

    print("⚙️ Scaling features...")
    scaler = StandardScaler()
    scaler.fit(df[features])

    results = []

    if isinstance(row_indices, int):
        row_indices = [row_indices]

    for row_index in row_indices:
        input_row = df.iloc[[row_index]].copy()
        # Scale only the features used for the autoencoder
        input_scaled = scaler.transform(input_row[features])
        reconstructed = autoencoder.predict(input_scaled, verbose=0)
        mse = np.mean(np.power(input_scaled - reconstructed, 2), axis=1)[0]

        try:
            attack_cat_label = attack_cat_encoder.inverse_transform(
                [int(input_row['attack_cat'].values[0])])[0]
        except:
            attack_cat_label = input_row['attack_cat'].values[0]

        result = "NORMAL" if mse > threshold else "ATTACK"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        selected_features = {}
        # Include all relevant features in the output dictionary
        all_output_features = features + ['label'] # Add 'label' back for output
        for feature in all_output_features:
            if feature in input_row.columns:
                value = input_row[feature].values[0]
                if isinstance(value, (np.integer, np.floating)):
                    value = value.item()
                selected_features[feature] = value

        selected_features['attack_cat'] = str(attack_cat_label)

        for col in ['src', 'proto']:
            if col in input_row.columns:
                selected_features[col] = input_row[col].values[0]

        selected_features.update({
            'row_index': int(row_index),
            'mse': float(mse),
            'result': str(result),
            'timestamp': str(timestamp),
        })

        print(f"\n🔽 Row {row_index}")
        for key, value in selected_features.items():
            print(f"   {key}: {value}")

        results.append(selected_features)

    return results


class RowInput(BaseModel):
    row_index: int

@app.get("/predict_all")
def predict_all():
    # Read the dataset
    print(f"📄 Reading data from: {csv_path}")
    df = pd.read_csv(csv_path)
    
    results = []  # To store results for all rows

    for row_index in range(len(df)):
        result = predict_with_autoencoder(
            csv_file_path=csv_path,
            config_path=config_path,
            weights_path=weights_path,
            attack_cat_path=attack_cat_path,
            state_path=state_path,
            row_indices=[row_index],
            threshold=threshold
        )
        results.append(result)

    return {'results': results}










@app.post("/train")
async def train_from_csv(file: UploadFile = File(...)):
    try:
        # ========== إعدادات ==========
        PLOT_DIR = "static/plots"
        MODEL_PATH = "static/model/autoencoder_model.h5" #"static/model/autoencoder_model.keras"
        OUTPUT_CSV = "static/model/anomaly_detection_results.csv"

        os.makedirs(PLOT_DIR, exist_ok=True)
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)

        REQUIRED_COLUMNS = [
            'ct_src_dport_ltm', 'rate', 'dwin', 'dload', 'swin', 'ct_dst_sport_ltm',
            'state', 'ct_state_ttl',  'sttl', 'label'
        ]
        
        df = pd.read_csv(file.file)

        print("Original columns:", df.columns.tolist())
        df.dropna(inplace=True)

        # حذف عمود id إن وُجد
        if 'id' in df.columns:
            df.drop(columns=['id'], inplace=True)

        # إعادة تسمية result إلى label إن وُجد
        if 'result' in df.columns:
            df.rename(columns={'result': 'label'}, inplace=True)

        # التأكد من توفر الأعمدة المطلوبة بعد التعديلات
        missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
        if missing_cols:
            return JSONResponse(
                content={"error": f"Missing required columns: {missing_cols}"},
                status_code=400
            )

        # استخراج الأعمدة النهائية فقط
        df = df[REQUIRED_COLUMNS]

        print("Filtered DataFrame:")
        print(df.head())
        print(df.info())
        # تحويل القيم النصية إلى أرقام
        df['label'] = df['label'].map({'NORMAL': 0, 'ATTACK': 1})

        # حذف الصفوف التي لم يتم تحويلها (قيم غير معروفة)
        df = df.dropna(subset=['label'])

        # تحويل label إلى int
        df['label'] = df['label'].astype(int)

        X = df.drop(columns=['label'])
        y = df['label']
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        X_normal = X_scaled[y == 0]
        X_train, X_val = train_test_split(X_normal, test_size=0.2, random_state=42)
        print(f"train: {X_train.shape}")
        print(f"X_val: {X_val.shape}")

        input_dim = X_train.shape[1]

        input_layer = Input(shape=(input_dim,))
        encoded = Dense(128, activation='relu')(input_layer)
        encoded = Dense(64, activation='relu')(encoded)
        encoded = Dense(32, activation='relu')(encoded)
        decoded = Dense(64, activation='relu')(encoded)
        decoded = Dense(128, activation='relu')(decoded)
        decoded = Dense(input_dim, activation='linear')(decoded)

        autoencoder = Model(inputs=input_layer, outputs=decoded)
        autoencoder.compile(optimizer='adam', loss='mse')
        print(autoencoder.summary())

        early_stop = EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)
        model_checkpoint = ModelCheckpoint(MODEL_PATH, save_best_only=True, monitor='val_loss', verbose=1)
        print(f"autoencoder: {autoencoder.summary()}")
        history = autoencoder.fit(
            X_train, X_train,
            epochs=100,
            batch_size=8,
            validation_data=(X_val, X_val),
            shuffle=True,
            verbose=0,
            callbacks=[early_stop, model_checkpoint]
        )

        X_pred = autoencoder.predict(X_scaled)
        mse = np.mean(np.power(X_pred - X_scaled, 2), axis=1)
        threshold = np.percentile(mse[y == 0], 95)
        predictions = (mse > threshold).astype(int)

        print(f'threshold: {threshold}')
        print(f'mse: {mse}')

        output_df = df.copy()
        output_df['reconstruction_error'] = mse
        output_df['predicted'] = predictions
        output_df.to_csv(OUTPUT_CSV, index=False)

        print(f'output_df: {output_df}')

        # ====== الصور ======
        # Confusion Matrix
        conf_mat = confusion_matrix(y, predictions)
        plt.figure(figsize=(6, 4))
        sns.heatmap(conf_mat, annot=True, fmt='d', cmap='Blues',
                    xticklabels=['Normal', 'Anomaly'], yticklabels=['Normal', 'Anomaly'])
        plt.xlabel('Predicted')
        plt.ylabel('True')
        plt.title('Confusion Matrix')
        conf_path = os.path.join(PLOT_DIR, 'confusion_matrix.png')
        plt.savefig(conf_path)
        plt.close()

        # Training Loss
        plt.figure(figsize=(8, 4))
        plt.plot(history.history['loss'], label='Train Loss')
        plt.plot(history.history['val_loss'], label='Validation Loss')
        plt.title('Autoencoder Training Loss')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        loss_path = os.path.join(PLOT_DIR, 'training_loss.png')
        plt.savefig(loss_path)
        plt.close()

        # Reconstruction Error Distribution
        error_df = pd.DataFrame({'reconstruction_error': mse, 'true_label': y.values})
        normal_errors = error_df[error_df['true_label'] == 0]['reconstruction_error']
        attack_errors = error_df[error_df['true_label'] == 1]['reconstruction_error']
        bins = np.linspace(0, max(attack_errors.max(), normal_errors.max()), 100)
        plt.hist(attack_errors, bins=bins, color='red', alpha=0.5, label='Attack')
        plt.hist(normal_errors, bins=bins, color='blue', alpha=0.5, label='Normal')
        plt.axvline(threshold, color='black', linestyle='--', linewidth=2, label='Threshold')
        plt.title('Reconstruction Error Distribution')
        plt.xlabel('Reconstruction Error')
        plt.ylabel('Number of Samples')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        error_path = os.path.join(PLOT_DIR, 'error_distribution.png')
        plt.savefig(error_path)
        plt.close()

        # ====== المقاييس ======
        if len(np.unique(y)) < 2:
            print("❗ ROC AUC and F1 cannot be calculated because y contains only one class.")
            auc = None
            f1 = None
            report = None
        else:
            auc = roc_auc_score(y, mse)
            f1 = f1_score(y, predictions)
            report = classification_report(y, predictions, output_dict=True)
            print(f'report: {report}')

        print("✅ الصور الناتجة:")
        print(f"- Confusion Matrix: /static/plots/confusion_matrix.png")
        print(f"- Training Loss: /static/plots/training_loss.png")
        print(f"- Error Distribution: /static/plots/error_distribution.png")
        print(f"📄 ملف النتائج CSV: /static/model/anomaly_detection_results.csv")

         # ====== العودة للواجهة ======
        return JSONResponse(
            content={
                "message": "Training completed",
                "rows": len(df),
                "auc": round(auc, 4) if auc is not None else None,
                "f1": round(f1, 4) if f1 is not None else None,
                "report": report,
                "images": {
                    "confusion_matrix": "/static/plots/confusion_matrix.png",
                    "training_loss": "/static/plots/training_loss.png",
                    "error_distribution": "/static/plots/error_distribution.png"
                },
                "csv_result": "/static/model/anomaly_detection_results.csv"
            },
            status_code=200
        )


       

    except Exception as e:
        import traceback
        print("❌ Exception occurred during training:")
        traceback.print_exc()
        return JSONResponse(content={"error": str(e)}, status_code=500)




