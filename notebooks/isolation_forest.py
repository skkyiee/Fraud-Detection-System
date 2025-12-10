# train_isolation_forest.py
"""
Train an IsolationForest pipeline (StandardScaler + IsolationForest) on synthetic
"normal" transactions and save it.

Produces: models/iforest_pipeline.joblib

Also prints basic validation stats (percentiles of decision_function) so you can
choose an anomaly threshold.
"""

import os
import numpy as np
import pandas as pd
import joblib
import random
from datetime import datetime
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline

MODELS_DIR = "models"
MODEL_FILENAME = "iforest_pipeline.joblib"
MODEL_PATH = os.path.join(MODELS_DIR, MODEL_FILENAME)

os.makedirs(MODELS_DIR, exist_ok=True)


def synth_normal_data(n=5000, seed=42):
    """
    Generate synthetic 'normal' transaction feature rows:
      - amount: float (centered ~700, with variance)
      - hour: int (8..21)
      - loc: small int encoding of location
    Returns pandas.DataFrame with columns ["amount","hour","loc"]
    """
    random.seed(seed)
    np.random.seed(seed)
    rows = []
    for _ in range(n):
        amount = max(1.0, np.random.normal(loc=700.0, scale=400.0))
        hour = int(np.random.choice(list(range(8, 22)), p=[1/14] * 14))
        loc = int(np.random.randint(0, 10))
        rows.append([amount, hour, loc])
    return pd.DataFrame(rows, columns=["amount", "hour", "loc"])


def train_pipeline(X_train, contamination=0.01, random_state=42):
    """
    Train a pipeline: StandardScaler -> IsolationForest
    """
    clf = IsolationForest(
        n_estimators=200,
        contamination=contamination,
        random_state=random_state,
        verbose=0
    )
    pipeline = make_pipeline(StandardScaler(), clf)
    pipeline.fit(X_train)
    return pipeline


def evaluate_on_validation(pipeline, X_val):
    """
    Compute decision_function scores on validation set and print percentiles.
    Higher score => more normal. Lower => more anomalous.
    """
    scores = pipeline.decision_function(X_val)
    pct = [0.5, 1, 2, 5, 10, 25, 50]  # percentiles to inspect
    vals = np.percentile(scores, pct)
    print("\nValidation decision_function percentiles (higher => more normal):")
    for p, v in zip(pct, vals):
        print(f"  {p:>3}th percentile: {v:.6f}")
    print(f"  mean score: {np.mean(scores):.6f}, std: {np.std(scores):.6f}")
    return scores


def train_and_save(contamination=0.01):
    print("Generating synthetic training data...")
    X = synth_normal_data(n=12000, seed=42)   # more training samples for stability

    # split train / validation
    val_frac = 0.2
    n_val = int(len(X) * val_frac)
    X_train = X.iloc[n_val:].reset_index(drop=True)
    X_val = X.iloc[:n_val].reset_index(drop=True)

    print(f"Training samples: {len(X_train)}, validation samples: {len(X_val)}")
    print(f"Training IsolationForest pipeline (contamination={contamination})...")
    pipeline = train_pipeline(X_train, contamination=contamination, random_state=42)

    print("Evaluating on validation (synthetic normal) dataset...")
    scores = evaluate_on_validation(pipeline, X_val)

    # Save pipeline
    joblib.dump(pipeline, MODEL_PATH)
    print(f"\nModel pipeline saved to: {MODEL_PATH}")

    # Suggest a starting threshold (1st or 2nd percentile of validation scores)
    p1 = float(np.percentile(scores, 1))
    p2 = float(np.percentile(scores, 2))
    print("\nSuggested starting anomaly thresholds (decision_function):")
    print(f"  1st percentile: {p1:.6f}")
    print(f"  2nd percentile: {p2:.6f}")
    print("Choose a threshold <= these values to flag approx 1-2% of 'normal' as anomalies.")


if __name__ == "__main__":
    # You can change contamination here if you want
    train_and_save(contamination=0.01)
