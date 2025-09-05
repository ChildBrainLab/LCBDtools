import numpy as np
import matplotlib.pyplot as plt
from hmmlearn.hmm import GaussianHMM, GMMHMM
from sklearn.preprocessing import StandardScaler

folder = "/storage1/fs1/perlmansusan/Active/moochie/analysis/CARE/"

files = [
    'AHKJ_rating_avg_movieA.txt',
    'AHKJ_rating_avg_movieB.txt',
    'AHKJ_rating_avg_movieC.txt',
    "AHKJ_rating_avg_volatility_movieA.txt",
    "AHKJ_rating_avg_volatility_movieB.txt",
    "AHKJ_rating_avg_volatility_movieC.txt"
]

def num_params_gaussian_full(K, D):
    start = (K - 1)
    trans = K * (K - 1)
    means = K * D
    covars = K * (D * (D + 1) // 2)
    return start + trans + means + covars

def fit_hmm_and_bic(X, K, lengths=None, random_state=0):
    m = GaussianHMM(n_components=K, covariance_type="full", n_iter=500, tol=1e-3, random_state=random_state)
    
    m.fit(X, lengths=lengths)
    
    logL = m.score(X, lengths=lengths)
    
    N = (X.shape[0] if lengths is None else sum(lengths))
    D = X.shape[1]
    p = num_params_gaussian_full(K, D)
    bic = -2 * logL + p * np.log(N)
    return m, bic, logL

for filename in files:
    # Load contents
    with open(f"{folder}{filename}", 'r') as f:
        X_raw = np.array([float(line.strip()) for line in f])

    X_raw = X_raw.reshape(-1, 1)

    scaler = StandardScaler()
    X = scaler.fit_transform(X_raw)

    # Fit models
    fits = []
    for K in range(2, 6):
        m = GaussianHMM(n_components=K, covariance_type="full", n_iter=500, tol=1e-3, random_state=0)
        m.fit(X)
        logL = m.score(X)
        p = num_params_gaussian_full(K, X.shape[1])
        bic = -2 * logL + p * np.log(len(X))
        fits.append((K, m, bic, logL))

    best_K, best_model, best_bic, _ = min(fits, key=lambda t: t[2])
    print("Best K by BIC:", best_K)

    states = best_model.predict(X)
    change_idx = np.where(np.diff(states) != 0)[0] + 1  # indices where a new segment starts
    segments = []
    start = 0
    for idx in np.r_[change_idx, len(states)]:
        segments.append((start, idx, states[start]))  # (start_idx, end_idx, state_id)
        start = idx

    # If you have timestamps t (shape T,) or sampling rate fs:
    # segment times = (t[start_idx], t[end_idx]) or (start_idx/fs, end_idx/fs)

    T = X.shape[0]
    t = np.arange(T)  # or your real timestamps

    plt.figure(figsize=(10, 4))
    plt.plot(t, X[:, 0])  # show first feature for intuition
    for (s, e, z) in segments:
        plt.axvspan(s, e, alpha=0.15)  # light shading per segment
    plt.title("Time series with HMM segmentation")
    plt.xlabel("time")
    plt.ylabel("feature 1 (scaled)")
    plt.show()

    A = best_model.transmat_
    expected_durations = 1.0 / (1.0 - np.clip(np.diag(A), 1e-9, 1-1e-9))
    print("State means:\n", best_model.means_)
    print("Expected durations (steps):", expected_durations)