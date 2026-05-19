import sys
import os
import pickle
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score, classification_report, confusion_matrix, roc_auc_score
)
from sklearn.preprocessing import label_binarize
from sqlalchemy import text

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.core.database import engine

FALLBACK_FEATURES = [
    'home_wins_last_10', 'home_draws_last_10', 'home_losses_last_10',
    'away_wins_last_10', 'away_draws_last_10', 'away_losses_last_10',
    'home_goals_scored_avg', 'home_goals_conceded_avg',
    'away_goals_scored_avg', 'away_goals_conceded_avg',
    'home_points_last_10', 'away_points_last_10', 'PointsDifference',
    'HomeElo', 'AwayElo', 'EloDifference', 'HomeTeamCode', 'AwayTeamCode',
    'home_sot_avg', 'home_corners_avg', 'away_sot_avg', 'away_corners_avg'
]

RENAME_MAP = {
    'home_elo': 'HomeElo',
    'away_elo': 'AwayElo',
    'elo_difference': 'EloDifference',
    'points_difference': 'PointsDifference',
    'home_team_code': 'HomeTeamCode',
    'away_team_code': 'AwayTeamCode',
}

CLASS_NAMES = ['Away Win', 'Draw', 'Home Win']
FTR_MAP = {'A': 0, 'D': 1, 'H': 2}


def run_benchmark(league: str = 'PL'):
    print(f"\n{'='*60}")
    print(f"  BENCHMARK — {league}")
    print(f"{'='*60}\n")

    # 1. Load stored model from DB
    print("Loading stored model from database...")
    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT model_binary, encoder_binary FROM model_store WHERE league=:l ORDER BY id DESC LIMIT 1"),
            {"l": league}
        ).fetchone()

    if not row:
        print(f"No trained model found for '{league}'. Run retrain first.")
        return

    model = pickle.loads(row[0])
    le = pickle.loads(row[1])
    print("Model loaded.\n")

    # 2. Resolve feature columns from the stored model if possible
    if hasattr(model, 'feature_names_in_') and model.feature_names_in_ is not None:
        features = list(model.feature_names_in_)
        print(f"Feature columns ({len(features)}): from stored model")
    else:
        features = FALLBACK_FEATURES
        print(f"Feature columns ({len(features)}): fallback list")

    # 3. Load finished match data
    df = pd.read_sql(
        f"SELECT * FROM matches WHERE league='{league}' AND ftr IN ('H','D','A') ORDER BY date ASC",
        engine
    )
    print(f"Loaded {len(df)} finished matches.\n")

    df = df.rename(columns=RENAME_MAP)

    # 4. Encode teams with the stored LabelEncoder
    try:
        df['HomeTeamCode'] = le.transform(df['home_team'])
        df['AwayTeamCode'] = le.transform(df['away_team'])
    except ValueError as e:
        print(f"Team encoding error: {e}")
        return

    # 5. Drop rows missing any feature (warm-up period at start of history)
    non_code_features = [f for f in features if f not in ('HomeTeamCode', 'AwayTeamCode')]
    df = df.dropna(subset=non_code_features).reset_index(drop=True)

    if len(df) < 100:
        print(f"Only {len(df)} usable rows — run backfill first.")
        return

    # 6. Temporal split — last 20% as test set
    split_idx = int(len(df) * 0.80)
    test_df = df.iloc[split_idx:].copy()
    date_min = pd.to_datetime(test_df['date']).min().date()
    date_max = pd.to_datetime(test_df['date']).max().date()
    print(f"Test set: {len(test_df)} matches  [{date_min} → {date_max}]\n")

    X_test = test_df[features]
    y_true = test_df['ftr'].map(FTR_MAP).values

    # 7. Run predictions
    y_pred = model.predict(X_test)
    probs = model.predict_proba(X_test)

    # ── REPORT ────────────────────────────────────────────────────────────────

    acc = accuracy_score(y_true, y_pred)
    print(f"Overall Accuracy:  {acc:.4f}  ({acc:.2%})\n")

    # Classification report
    print("CLASSIFICATION REPORT")
    print("-" * 60)
    print(classification_report(y_true, y_pred, target_names=CLASS_NAMES))

    # AUC-ROC
    print("AUC-ROC (one-vs-rest)")
    print("-" * 60)
    y_bin = label_binarize(y_true, classes=[0, 1, 2])
    macro_auc = roc_auc_score(y_bin, probs, multi_class='ovr', average='macro')
    print(f"  Macro:            {macro_auc:.4f}")
    for i, name in enumerate(CLASS_NAMES):
        auc_i = roc_auc_score(y_bin[:, i], probs[:, i])
        print(f"  {name:<14}  {auc_i:.4f}")
    print()

    # Confusion matrix
    print("CONFUSION MATRIX (rows=Actual, cols=Predicted)")
    print("-" * 60)
    cm = confusion_matrix(y_true, y_pred)
    col_w = 12
    header = f"{'':>14}" + "".join(f" {'Pred ' + n:>{col_w}}" for n in ['Away', 'Draw', 'Home'])
    print(header)
    print("-" * len(header))
    for i, name in enumerate(CLASS_NAMES):
        row = f"{'Act ' + name:>14}" + "".join(f" {cm[i][j]:>{col_w}}" for j in range(3))
        print(row)
    print()

    # Confidence threshold analysis
    print("CONFIDENCE THRESHOLD ANALYSIS")
    print("-" * 60)
    confidences = probs.max(axis=1)
    correct = (y_pred == y_true)
    total = len(correct)
    for t in [0.40, 0.45, 0.50, 0.55, 0.60, 0.70]:
        mask = confidences > t
        n = int(mask.sum())
        if n > 0:
            t_acc = correct[mask].mean()
            print(f"  > {t:.2f} | {n:4d} matches ({n/total*100:4.1f}%) | Accuracy: {t_acc:.2%}")
        else:
            print(f"  > {t:.2f} |    0 matches          | Accuracy: N/A")
    print()

    # Feature importances (top 10)
    print("TOP 10 FEATURE IMPORTANCES")
    print("-" * 60)
    feat_imp = sorted(zip(features, model.feature_importances_), key=lambda x: x[1], reverse=True)
    for feat, imp in feat_imp[:10]:
        bar = '█' * max(1, int(imp * 300))
        print(f"  {feat:<35} {imp:.4f}  {bar}")
    print()
    print("=" * 60 + "\n")


if __name__ == "__main__":
    league = sys.argv[1] if len(sys.argv) > 1 else 'PL'
    run_benchmark(league)
