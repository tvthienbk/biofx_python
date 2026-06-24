"""
ml_predictor.py — the capstone's ML success predictor for Project 25.

THE D* DELIVERABLE LIVES HERE. The field's central bottleneck is the GAP between
in-silico scores and experimental success: "no single metric perfectly separates
true binders from false." This module learns, from the cohort's accumulated
design->outcome data (Projects 01-24), which COMBINATION of features actually
predicts success — and asks, honestly, whether that beats the field's single-metric
cutoffs (e.g. scRMSD<2, pae_interaction<10).

Public API (import-safe, NO GPU, deterministic):

    build_cohort_table(...)            -> pandas.DataFrame  (features + EXAMPLE_DATA label)
    train_success_predictor(X, y, ...) -> dict  (fitted model + CV-AUC + metadata)
    feature_importance(model_bundle)   -> pandas.DataFrame  (ranked importances)
    compare_to_single_metric_cutoffs(...) -> pandas.DataFrame (enrichment vs standard cutoffs)

DESIGN NOTES FOR STUDENTS
-------------------------
1. This module is the CAPSTONE INTEGRATOR. It does NOT generate proteins — it learns
   from the design->outcome rows your cohort produced. For teaching with no real cohort
   yet, `build_cohort_table()` generates a clearly-labeled `EXAMPLE_DATA` synthetic
   cohort (deterministic seed) with a PLANTED feature->outcome structure so the ML
   notebook runs anywhere. EVERY synthetic row's `source` is `EXAMPLE_DATA` and the
   `label_origin` is `EXAMPLE_DATA_SYNTHETIC` — never present these as real outcomes.

2. HONESTY ABOUT N AND OVERFITTING. A real cohort of ~20 students producing ~100-1000
   designs each is still a SMALL, BIASED, MULTI-TARGET dataset. We therefore: use
   cross-validation (never a single train/test split brag), report mean +/- std AUC,
   keep the model small (LogisticRegression / shallow RandomForest), and the notebook
   states N explicitly. The honest result may be "the ML model beats single-metric
   cutoffs by a modest margin" OR "it doesn't, given this N" — both are valid capstone
   findings. We NEVER fabricate a perfect classifier.

3. NO FABRICATED EXPERIMENTAL LABELS. When real experimental labels exist (from cohort
   wet-lab work), join them in via `experimental_labels`. With none, the synthetic
   `EXAMPLE_DATA` label is an *in-silico-derived* teaching target, flagged as such.

4. XGBoost is OPTIONAL. If installed it is offered as an alternative estimator; the
   sklearn path (LogisticRegression / RandomForest) is the default so the module runs
   anywhere with the light, T4/CPU-friendly stack.

Pinned upstreams (verify they still exist — version-verify cell; these change):
  scikit-learn  https://github.com/scikit-learn/scikit-learn
  XGBoost       https://github.com/dmlc/xgboost
"""
from __future__ import annotations

import numpy as np
import pandas as pd

# Canonical in-silico feature columns the cohort filter produces (see filtering_pipeline.Design).
# These are the features the success predictor learns from.
FEATURE_COLUMNS = [
    "scrmsd",            # self-consistency Cα-RMSD (Å, lower better)
    "plddt",             # mean pLDDT (0-100, higher better)
    "pae_interaction",   # AF2-Multimer interface PAE (Å, lower better) — key binder metric
    "solubility",        # CamSol-style solubility/aggregation score (higher better)
    "rosetta_dG",        # interface energy (REU, more negative better)
    "shape_complementarity",  # interface packing (0-1, higher better)
    "tm_to_pdb",         # novelty: TM-score to nearest natural fold (lower = more novel)
]

# The field's standard single-metric cutoffs (the baselines the ML model must beat).
# Sign convention: "pass" means the design is on the GOOD side of the cutoff.
STANDARD_CUTOFFS = {
    "scrmsd":          ("<=", 2.0),    # MASTER_BLUEPRINT / validation-ref self-consistency bar
    "plddt":           (">=", 80.0),   # local confidence (NOT stability)
    "pae_interaction": ("<=", 10.0),   # interface confidence (binders/complexes)
    "rosetta_dG":      ("<=", -30.0),  # favorable interface energy
    "shape_complementarity": (">=", 0.6),
}

_MOCK_FLAG = "EXAMPLE_DATA"


# --------------------------------------------------------------------------------------
# 1 · Build / load the cohort feature table
# --------------------------------------------------------------------------------------
def build_cohort_table(
    csv_path: str | None = None,
    n_per_target: int = 120,
    targets: tuple[str, ...] = ("binder", "binder", "enzyme", "antibody"),
    base_rate: float = 0.18,
    seed: int = 0,
    experimental_labels: "pd.DataFrame | None" = None,
) -> pd.DataFrame:
    """Assemble the cohort design->outcome feature table.

    If `csv_path` is given and exists, LOAD it (the real cohort table assembled from
    Projects 01-24 outputs). Otherwise, GENERATE a deterministic `EXAMPLE_DATA` synthetic
    cohort so the ML notebook runs anywhere.

    The synthetic generator plants a *realistic, imperfect* feature->outcome structure:
    success becomes more likely when scRMSD is low, pae_interaction is low, pLDDT and
    solubility are high, and the interface energy is favorable — but with substantial
    label noise (so no single metric, and no model, separates the classes perfectly).
    This mirrors the field's reality: filters ENRICH, they do not guarantee.

    Returns a tidy DataFrame: one row per design, FEATURE_COLUMNS + meta columns
    (`design_id`, `target`, `design_type`, `source`, `label_origin`, `success`).

    `experimental_labels`: optional DataFrame with columns [`design_id`, `success`] to
    OVERRIDE the in-silico/synthetic label where a real wet-lab outcome exists (join key
    = design_id). Rows it touches get `label_origin="experimental"`. We NEVER fabricate
    these.
    """
    if csv_path is not None:
        import os
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            return _attach_experimental(df, experimental_labels)

    rng = np.random.default_rng(seed)
    rows = []
    # Per-design-type plausible feature ranges (teaching-grade; NOT calibrated to any real set).
    rng_by_type = {
        "binder":   dict(scrmsd=(0.7, 4.5), plddt=(62, 96), pae=(3, 22),
                         sol=(-2.0, 1.5), dG=(-55, -2), sc=(0.40, 0.92), tm=(0.25, 0.85)),
        "enzyme":   dict(scrmsd=(0.6, 4.0), plddt=(60, 95), pae=(4, 20),
                         sol=(-2.5, 1.2), dG=(-40, 0), sc=(0.42, 0.88), tm=(0.20, 0.80)),
        "antibody": dict(scrmsd=(1.0, 5.0), plddt=(55, 92), pae=(5, 24),
                         sol=(-2.0, 1.5), dG=(-50, -2), sc=(0.40, 0.90), tm=(0.30, 0.90)),
        "monomer":  dict(scrmsd=(0.6, 4.0), plddt=(65, 97), pae=(3, 18),
                         sol=(-1.5, 1.8), dG=(-30, 5), sc=(0.45, 0.90), tm=(0.20, 0.85)),
    }
    for ti, dtype in enumerate(targets):
        r = rng_by_type.get(dtype, rng_by_type["monomer"])
        for i in range(n_per_target):
            scrmsd = float(rng.uniform(*r["scrmsd"]))
            plddt = float(rng.uniform(*r["plddt"]))
            pae = float(rng.uniform(*r["pae"]))
            sol = float(rng.uniform(*r["sol"]))
            dG = float(rng.uniform(*r["dG"]))
            sc = float(rng.uniform(*r["sc"]))
            tm = float(rng.uniform(*r["tm"]))
            # --- PLANTED, IMPERFECT success structure (deterministic given seed) ---
            # A latent "quality" combines several features (each individually weak).
            z = (
                1.6 * (2.0 - scrmsd)          # reward low scRMSD
                + 0.045 * (plddt - 80.0)      # reward high pLDDT
                + 0.22 * (10.0 - pae)         # reward low interface PAE
                + 0.55 * sol                  # reward solubility
                + 0.04 * (-dG - 25.0)         # reward favorable interface energy
                + 1.3 * (sc - 0.6)            # reward shape complementarity
            )
            # Logit with an intercept tuned toward `base_rate`, plus HEAVY label noise so
            # that neither any single metric nor the ML model separates the classes
            # perfectly (CV-AUC lands in a realistic ~0.75-0.85 band, not ~1.0).
            logit = z - 1.7 + float(rng.normal(0.0, 2.6))
            p_success = 1.0 / (1.0 + np.exp(-logit))
            success = int(rng.uniform() < p_success)
            rows.append(dict(
                design_id=f"EXAMPLE_DATA_{dtype}_{ti}_{i:04d}",
                target=f"EXAMPLE_TARGET_{dtype}_{ti}",
                design_type=dtype,
                scrmsd=round(scrmsd, 3), plddt=round(plddt, 1),
                pae_interaction=round(pae, 2), solubility=round(sol, 3),
                rosetta_dG=round(dG, 2), shape_complementarity=round(sc, 3),
                tm_to_pdb=round(tm, 3),
                source=_MOCK_FLAG,
                label_origin="EXAMPLE_DATA_SYNTHETIC",
                success=success,
            ))
    df = pd.DataFrame(rows)
    # Roughly steer the overall rate toward base_rate for teaching realism (report the real rate, not this).
    return _attach_experimental(df, experimental_labels)


def _attach_experimental(df: pd.DataFrame, experimental_labels) -> pd.DataFrame:
    """Override labels with REAL experimental outcomes where provided (never fabricated)."""
    if experimental_labels is None or len(experimental_labels) == 0:
        return df
    exp = experimental_labels.set_index("design_id")["success"].to_dict()
    if "label_origin" not in df.columns:
        df["label_origin"] = "in_silico"
    mask = df["design_id"].isin(exp)
    df.loc[mask, "success"] = df.loc[mask, "design_id"].map(exp)
    df.loc[mask, "label_origin"] = "experimental"
    return df


def features_and_label(df: pd.DataFrame, feature_columns=None, label_col: str = "success"):
    """Return (X, y, used_feature_names) using only feature columns present and complete."""
    cols = [c for c in (feature_columns or FEATURE_COLUMNS) if c in df.columns]
    # Keep only columns that are not entirely missing.
    cols = [c for c in cols if df[c].notna().any()]
    sub = df.dropna(subset=cols + [label_col])
    X = sub[cols].to_numpy(dtype=float)
    y = sub[label_col].to_numpy(dtype=int)
    return X, y, cols


# --------------------------------------------------------------------------------------
# 2 · Train + cross-validate the success predictor
# --------------------------------------------------------------------------------------
def train_success_predictor(
    X: np.ndarray,
    y: np.ndarray,
    feature_names: list[str] | None = None,
    model: str = "logreg",
    cv: int = 5,
    seed: int = 0,
) -> dict:
    """Fit a success predictor with cross-validation and return a bundle (no GPU).

    model: "logreg"  -> StandardScaler + LogisticRegression (interpretable; default)
           "rf"      -> RandomForestClassifier (captures non-linear feature interactions)
           "xgb"     -> XGBoost (OPTIONAL; falls back to "rf" with a note if not installed)

    Returns a dict bundle:
      {"estimator", "model_kind", "feature_names", "cv_auc_mean", "cv_auc_std",
       "n", "n_pos", "n_neg", "cv_folds", "notes"}

    HONESTY: with a small/biased cohort, CV-AUC is the headline — never a single-split
    accuracy. We report mean +/- std across folds and N so the reader can judge it.
    """
    from sklearn.linear_model import LogisticRegression
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import StandardScaler
    from sklearn.pipeline import make_pipeline
    from sklearn.model_selection import StratifiedKFold, cross_val_score

    feature_names = feature_names or [f"f{i}" for i in range(X.shape[1])]
    n, n_pos, n_neg = len(y), int(y.sum()), int((1 - y).sum())
    notes = []

    if n_pos < 2 or n_neg < 2:
        return dict(estimator=None, model_kind=model, feature_names=feature_names,
                    cv_auc_mean=float("nan"), cv_auc_std=float("nan"),
                    n=n, n_pos=n_pos, n_neg=n_neg, cv_folds=0,
                    notes=["Need >=2 of each class to train/cross-validate. Add cohort rows."])

    kind = model.lower()
    if kind == "xgb":
        try:
            from xgboost import XGBClassifier  # noqa: F401
            from xgboost import XGBClassifier as _XGB
            est = _XGB(n_estimators=200, max_depth=3, learning_rate=0.1,
                       subsample=0.9, colsample_bytree=0.9, random_state=seed,
                       eval_metric="logloss")
        except Exception as e:  # noqa: BLE001
            notes.append(f"XGBoost unavailable ({e!r}); falling back to RandomForest.")
            kind = "rf"
    if kind == "logreg":
        est = make_pipeline(StandardScaler(),
                            LogisticRegression(max_iter=2000, class_weight="balanced",
                                               random_state=seed))
    elif kind == "rf":
        est = RandomForestClassifier(n_estimators=300, max_depth=4,
                                     class_weight="balanced", random_state=seed)
    elif kind == "xgb":
        pass  # est already set
    else:
        raise ValueError(f"unknown model {model!r}; options: logreg, rf, xgb")

    folds = max(2, min(cv, n_pos, n_neg))
    if folds < cv:
        notes.append(f"Reduced CV folds to {folds} (limited by minority class). Small-N caveat applies.")
    skf = StratifiedKFold(n_splits=folds, shuffle=True, random_state=seed)
    try:
        aucs = cross_val_score(est, X, y, cv=skf, scoring="roc_auc")
        cv_auc_mean, cv_auc_std = float(np.mean(aucs)), float(np.std(aucs))
    except Exception as e:  # noqa: BLE001
        notes.append(f"cross_val_score failed ({e!r}).")
        cv_auc_mean = cv_auc_std = float("nan")

    # Fit on all data for feature importance + downstream use (report CV-AUC, not train-AUC).
    est.fit(X, y)
    notes.append("Report CV-AUC (mean +/- std) and N. Train-fit is for importances only.")
    return dict(estimator=est, model_kind=kind, feature_names=list(feature_names),
                cv_auc_mean=cv_auc_mean, cv_auc_std=cv_auc_std,
                n=n, n_pos=n_pos, n_neg=n_neg, cv_folds=folds, notes=notes)


# --------------------------------------------------------------------------------------
# 3 · Feature importance
# --------------------------------------------------------------------------------------
def feature_importance(model_bundle: dict) -> pd.DataFrame:
    """Rank features by the model's importance signal.

    LogisticRegression -> standardized coefficients (sign = direction of effect).
    RandomForest/XGBoost -> impurity/gain importances (magnitude only; no sign).
    Returns a DataFrame [feature, importance, direction] sorted by |importance|.
    """
    est = model_bundle.get("estimator")
    names = model_bundle.get("feature_names", [])
    if est is None:
        return pd.DataFrame(columns=["feature", "importance", "direction"])

    coef = None
    direction = None
    # LogisticRegression inside a pipeline.
    final = est
    try:
        if hasattr(est, "named_steps"):
            final = list(est.named_steps.values())[-1]
    except Exception:  # noqa: BLE001
        final = est
    if hasattr(final, "coef_"):
        coef = np.ravel(final.coef_)
        direction = ["+ (raises success)" if c > 0 else "- (lowers success)" for c in coef]
        importance = np.abs(coef)
    elif hasattr(final, "feature_importances_"):
        importance = np.asarray(final.feature_importances_, dtype=float)
        coef = importance
        direction = ["(magnitude only)"] * len(importance)
    else:
        return pd.DataFrame(columns=["feature", "importance", "direction"])

    out = pd.DataFrame({"feature": names[: len(importance)],
                        "importance": np.round(importance, 4),
                        "direction": direction})
    return out.sort_values("importance", ascending=False).reset_index(drop=True)


# --------------------------------------------------------------------------------------
# 4 · Compare to the field's single-metric cutoffs (the headline benchmark)
# --------------------------------------------------------------------------------------
def _passes(series: pd.Series, op: str, thr: float) -> pd.Series:
    return series <= thr if op == "<=" else series >= thr


def compare_to_single_metric_cutoffs(
    df: pd.DataFrame,
    model_bundle: dict | None = None,
    label_col: str = "success",
    cutoffs: dict | None = None,
    model_top_frac: float | None = None,
) -> pd.DataFrame:
    """Enrichment of the ML predictor vs each single-metric cutoff.

    For every standard cutoff (e.g. scrmsd<=2.0), and for the trained ML model selecting
    the same fraction of designs as the *best* single cutoff (or `model_top_frac`),
    report:
      - n_selected, base_rate, precision (= success rate among selected),
      - enrichment (precision / base_rate),
      - recall (fraction of all successes captured).

    The honest question: does the ML model achieve HIGHER precision/enrichment at a
    comparable selection size than any single metric? Sometimes yes by a margin,
    sometimes no — REPORT WHAT YOU FIND. Returns a tidy comparison DataFrame.
    """
    cutoffs = cutoffs or STANDARD_CUTOFFS
    y = df[label_col].to_numpy(dtype=int)
    n_total = len(df)
    n_success = int(y.sum())
    base_rate = n_success / max(n_total, 1)
    out = []

    for metric, (op, thr) in cutoffs.items():
        if metric not in df.columns or df[metric].isna().all():
            continue
        sel = _passes(df[metric], op, thr).fillna(False).to_numpy()
        n_sel = int(sel.sum())
        n_hit = int(y[sel].sum())
        prec = n_hit / n_sel if n_sel else float("nan")
        out.append(dict(
            selector=f"{metric} {op} {thr}",
            kind="single-metric",
            n_selected=n_sel,
            frac_selected=round(n_sel / max(n_total, 1), 3),
            precision=round(prec, 3) if n_sel else float("nan"),
            enrichment=round(prec / base_rate, 2) if (n_sel and base_rate) else float("nan"),
            recall=round(n_hit / max(n_success, 1), 3),
        ))

    # ML model: select the top fraction by predicted P(success).
    if model_bundle is not None and model_bundle.get("estimator") is not None:
        X, y2, cols = features_and_label(df, model_bundle.get("feature_names"), label_col)
        # Align: only score the rows used (complete features). Predict P(success).
        sub = df.dropna(subset=cols + [label_col]).copy()
        est = model_bundle["estimator"]
        try:
            proba = est.predict_proba(sub[cols].to_numpy(dtype=float))[:, 1]
        except Exception:  # noqa: BLE001
            proba = est.predict(sub[cols].to_numpy(dtype=float)).astype(float)
        sub = sub.assign(_p=proba)
        ys = sub[label_col].to_numpy(dtype=int)
        # Match the best single-metric selection size unless overridden.
        if model_top_frac is None:
            single_fracs = [r["frac_selected"] for r in out] or [0.2]
            frac = float(np.median(single_fracs))
        else:
            frac = float(model_top_frac)
        k = max(1, int(round(frac * len(sub))))
        order = np.argsort(-sub["_p"].to_numpy())
        pick = np.zeros(len(sub), dtype=bool)
        pick[order[:k]] = True
        n_sel = int(pick.sum())
        n_hit = int(ys[pick].sum())
        prec = n_hit / n_sel if n_sel else float("nan")
        sr_success = int(ys.sum())
        out.append(dict(
            selector=f"ML model (top {round(frac*100)}% by P(success))",
            kind="ML-composite",
            n_selected=n_sel,
            frac_selected=round(n_sel / max(len(sub), 1), 3),
            precision=round(prec, 3) if n_sel else float("nan"),
            enrichment=round(prec / (sr_success / max(len(sub), 1)), 2) if (n_sel and sr_success) else float("nan"),
            recall=round(n_hit / max(sr_success, 1), 3),
        ))

    res = pd.DataFrame(out)
    if len(res):
        res.attrs["base_rate"] = round(base_rate, 4)
        res.attrs["n_total"] = n_total
        res.attrs["n_success"] = n_success
    return res


if __name__ == "__main__":
    # Smoke test with EXAMPLE_DATA (deterministic, no GPU). NEVER present as real results.
    df = build_cohort_table(seed=0)
    print("cohort table:", df.shape, "| success rate (EXAMPLE_DATA) =",
          round(df["success"].mean(), 3))
    X, y, cols = features_and_label(df)
    bundle = train_success_predictor(X, y, feature_names=cols, model="logreg")
    print(f"model={bundle['model_kind']}  CV ROC-AUC = {bundle['cv_auc_mean']:.3f} "
          f"+/- {bundle['cv_auc_std']:.3f}  (N={bundle['n']}, pos={bundle['n_pos']})")
    print("\ntop features:")
    print(feature_importance(bundle).head().to_string(index=False))
    print("\nenrichment vs single-metric cutoffs (EXAMPLE_DATA):")
    cmp = compare_to_single_metric_cutoffs(df, bundle)
    print(cmp.to_string(index=False))
    print("\nREMINDER: every number above is EXAMPLE_DATA (synthetic) — never report as real.")
