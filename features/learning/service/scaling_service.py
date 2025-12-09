import numpy as np
from sklearn.preprocessing import StandardScaler

class ScalingService:

    def scale_features(self, X):
        n_samples, window, n_features = X.shape
        scaler = StandardScaler()
        X_2d = X.reshape(n_samples, window * n_features)
        X_scaled_2d = scaler.fit_transform(X_2d)
        X_scaled = X_scaled_2d.reshape(n_samples, window, n_features)
        return scaler, X_scaled
