# sfcm_dash/algorithms/sfcm.py

import numpy as np
from sklearn.metrics import davies_bouldin_score, silhouette_score

def subtractive_clustering(X, ra=0.5, rb_ratio=1.5, accept_ratio=0.5, reject_ratio=0.15):
    rb = ra * rb_ratio
    n  = X.shape[0]

    potentials = np.array([
        np.sum(np.exp(-np.sum((X - X[i])**2, axis=1) / (ra / 2)**2))
        for i in range(n)
    ])

    centers, pots = [], []
    first_max = potentials.max()

    while True:
        idx = potentials.argmax()
        pot = potentials[idx]

        if not centers:
            centers.append(X[idx].copy())
            pots.append(pot)
        else:
            ratio = pot / first_max
            if ratio >= accept_ratio:
                centers.append(X[idx].copy())
                pots.append(pot)
            elif ratio <= reject_ratio:
                break
            else:
                d_min = min(np.linalg.norm(X[idx] - c) for c in centers)
                if (d_min / ra) + ratio >= 1:
                    centers.append(X[idx].copy())
                    pots.append(pot)
                else:
                    potentials[idx] = 0
                    continue

        if len(centers) >= 15:
            break

        diff_sq    = np.sum((X - centers[-1])**2, axis=1)
        potentials -= pot * np.exp(-diff_sq / (rb / 2)**2)
        potentials  = np.maximum(potentials, 0)

        if potentials.max() < reject_ratio * first_max:
            break

    return np.array(centers), pots

def fuzzy_cmeans(X, init_centers, m=2.0, max_iter=100, eps=1e-6):
    n, _ = X.shape
    c = len(init_centers)
    centers = init_centers.copy()
    obj_history = []

    for _ in range(max_iter):
        U = np.zeros((c, n))
        for i in range(c):
            for k in range(n):
                d_ik = np.linalg.norm(X[k] - centers[i])
                if d_ik == 0:
                    U[i, k] = 1.0
                    continue
                total = sum(
                    (d_ik / max(np.linalg.norm(X[k] - centers[j]), 1e-10)) ** (2 / (m - 1))
                    for j in range(c)
                )
                U[i, k] = 1.0 / total

        centers_new = np.array([
            np.sum((U[i] ** m)[:, None] * X, axis=0) / np.sum(U[i] ** m)
            for i in range(c)
        ])

        obj = sum(
            (U[i, k] ** m) * np.linalg.norm(X[k] - centers_new[i]) ** 2
            for i in range(c) for k in range(n)
        )
        obj_history.append(obj)

        if np.max(np.abs(centers_new - centers)) < eps:
            break
        centers = centers_new.copy()

    return centers, U, obj_history

def evaluate_clustering(X, labels):
    try:
        dbi = davies_bouldin_score(X, labels)
        sil = silhouette_score(X, labels)
    except Exception:
        dbi, sil = float("nan"), float("nan")
    return dbi, sil

def build_label_map(centers_orig, n_cl):
    p0_vals    = centers_orig[:, 0]
    sorted_idx = np.argsort(p0_vals)

    if n_cl == 2:
        cat_names = ["Kemiskinan Rendah", "Kemiskinan Tinggi"]
    elif n_cl == 3:
        cat_names = ["Kemiskinan Rendah", "Kemiskinan Sedang", "Kemiskinan Tinggi"]
    elif n_cl == 4:
        cat_names = ["Sangat Rendah", "Rendah", "Sedang", "Tinggi"]
    else:
        cat_names = [f"Kelompok {i+1}" for i in range(n_cl)]

    return {int(ci): cat_names[rank] for rank, ci in enumerate(sorted_idx)}