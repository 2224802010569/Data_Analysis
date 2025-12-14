import tensorflow as tf
from app.config import config as con
from keras.saving import register_keras_serializable

@register_keras_serializable(package="CustomLoss")
def asymmetric_mae_loss(y_true, y_pred):
    diff = y_true - y_pred
    weight = tf.where(diff > 0, 1.5, 1.0)
    return tf.reduce_mean(weight * tf.abs(diff))

class ModelService:

    def _build_encoder_with_gru(self, window_size, num_features):
        inputs = tf.keras.layers.Input(
            shape=(window_size, num_features),
            name="input_window"
        )
        x = tf.keras.layers.GRU(
            64,
            return_sequences=True,
            name="gru_64"
        )(inputs)
        x = tf.keras.layers.Dropout(0.1, name="dropout_gru_64")(x)
        x = tf.keras.layers.LSTM(
            32,
            return_sequences=True,
            name="lstm_32"
        )(x)
        x = tf.keras.layers.Dropout(0.1, name="dropout_32")(x)
        return inputs, x

    def _apply_multihead_attention(self, x, num_heads=4):
        attn_output = tf.keras.layers.MultiHeadAttention(
            num_heads=num_heads,
            key_dim=x.shape[-1],
            dropout=0.05,
            name="multihead_attention"
        )(x, x)
        x = tf.keras.layers.Add(name="attn_residual")([x, attn_output])
        x = tf.keras.layers.LayerNormalization(
            epsilon=1e-6,
            name="attn_norm"
        )(x)
        return x

    def _build_regression_head(self, x):
        x = tf.keras.layers.Flatten(name="flatten")(x)
        x = tf.keras.layers.Dense(
            32,
            activation="relu",
            name="dense_32"
        )(x)
        outputs = tf.keras.layers.Dense(
            5,
            activation="linear",
            name="ohlcv_output"
        )(x)
        return outputs
    def asymmetric_mae_loss(self, y_true, y_pred):
        diff = y_true - y_pred
        weight = tf.where(diff > 0, 1.5, 1.0)
        return tf.reduce_mean(weight * tf.abs(diff))

    def build_model(self, window_size, num_features):
        inputs, x = self._build_encoder_with_gru(window_size, num_features)
        x = self._apply_multihead_attention(x, num_heads=4)
        outputs = self._build_regression_head(x)
        model = tf.keras.Model(
            inputs=inputs,
            outputs=outputs,
            name="GRU_LSTM_Attention_Regression"
        )
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
            loss=asymmetric_mae_loss,
            metrics=[tf.keras.metrics.MeanAbsoluteError()],
        )

        return model

    def train(self, model, X_scaled, y):
        history = model.fit(
            X_scaled,
            y,
            epochs=con.EPOCHS,
            batch_size=con.BATCH_SIZE,
            verbose=1
        )
        return history
