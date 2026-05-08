# sfcm_dash/utils/data_processing.py

import io
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from .constants import FEATURE_COLS

def _parse_rp(val):
    if pd.isna(val):
        return np.nan
    s = str(val).strip().replace("Rp", "").replace(" ", "")
    has_dot, has_comma = "." in s, "," in s
    if has_dot and has_comma:
        s = s.replace(".", "").replace(",", ".")
    elif has_comma and not has_dot:
        s = s.replace(",", ".")
    try:
        return float(s)
    except Exception:
        return np.nan

def load_and_preprocess(file_bytes: bytes):
    df = pd.read_csv(
        io.BytesIO(file_bytes),
        sep=";",
        skipinitialspace=True,
        decimal=",",
    )
    df.columns = [c.strip() for c in df.columns]

    pen_col = "Pengeluaran per Kapita Disesuaikan (Ribu Rupiah/Orang/Tahun)"
    if pen_col in df.columns and not pd.api.types.is_numeric_dtype(df[pen_col]):
        df[pen_col] = df[pen_col].apply(_parse_rp)

    for col in FEATURE_COLS:
        if col in df.columns and col != pen_col:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    available = [c for c in FEATURE_COLS if c in df.columns]
    if not available:
        raise ValueError(
            "Tidak ada kolom fitur yang cocok. "
            "Pastikan nama kolom di file CSV sama persis."
        )

    df_clean = df.dropna(subset=available).copy()
    scaler   = MinMaxScaler()
    X        = scaler.fit_transform(df_clean[available].values)

    return df_clean, X, scaler, available

def detect_columns(df: pd.DataFrame):
    kab_col  = next((c for c in df.columns if "kab" in c.lower()), None)
    prov_col = next((c for c in df.columns if "prov" in c.lower()), None)
    if kab_col is None and len(df.columns) > 1:
        kab_col = df.columns[1]
    return kab_col, prov_col