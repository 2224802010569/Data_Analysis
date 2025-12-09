import tensorflow as tf

class ModelService:

    def build_model(self, window_size, num_features, num_classes):
        model = tf.keras.Sequential([
            tf.keras.layers.Input(shape=(window_size, num_features)),
            tf.keras.layers.LSTM(32),
            tf.keras.layers.Dense(num_classes, activation="softmax")
        ])
        model.compile(
            optimizer="adam",
            loss="categorical_crossentropy",
            metrics=["accuracy"]
        )
        return model

    def train(self, model, X_scaled, y):
        history = model.fit(
            X_scaled,
            y,
            epochs=10,
            batch_size=32,
            verbose=0
        )
        return history
