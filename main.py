
from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import joblib
import numpy as np
from tensorflow.keras.models import model_from_json
from sklearn.preprocessing import StandardScaler
from datetime import datetime





app = FastAPI()

'''
csv_path = '/content/drive/MyDrive/hybrid_IDS/encoder/network_v.csv'
config_path = '/content/drive/MyDrive/hybrid_IDS/encoder/network/model/autoencoder_model/config.json'
weights_path = '/content/drive/MyDrive/hybrid_IDS/encoder/network/model/autoencoder_model/model.weights.h5'
attack_cat_path = '/content/drive/MyDrive/hybrid_IDS/encoder/network/dataset/attack_cat__encoder.pkl'
state_path = '/content/drive/MyDrive/hybrid_IDS/encoder/network/dataset/state__encoder.pkl'
threshold = 0.075
'''

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

    features = ['ct_src_dport_ltm', 'rate', 'dwin', 'dload', 'swin',
                'ct_dst_sport_ltm', 'ct_state_ttl', 'id',
                'attack_cat', 'sttl', 'label']

    print("⚙️ Scaling features...")
    scaler = StandardScaler()
    scaler.fit(df[features])

    results = []

    if isinstance(row_indices, int):
        row_indices = [row_indices]

    for row_index in row_indices:
        input_row = df.iloc[[row_index]].copy()
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
        for feature in features:
            if feature in input_row.columns:
                value = input_row[feature].values[0]
                if isinstance(value, (np.integer, np.floating)):
                    value = value.item()
                selected_features[feature] = value

        selected_features['attack_cat'] = str(attack_cat_label)
        
        for col in ['src', 'proto']: ##
            if col in input_row.columns: ##
                selected_features[col] = input_row[col].values[0] ##

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
