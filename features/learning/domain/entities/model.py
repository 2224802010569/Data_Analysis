import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, Input
from tensorflow.keras.optimizers import Adam
import os

class CryptoLSTMModel:
    def __init__(self, input_shape=(30, 22), num_classes=3, learning_rate=0.001):
        """
        Khởi tạo kiến trúc mô hình LSTM.
        :param input_shape: Tuple (time_steps, features) -> mặc định (30, 22)
        :param num_classes: Số lượng nhãn dự đoán (Ví dụ: 3 cho Buy, Sell, Hold)
        :param learning_rate: Tốc độ học
        """
        self.input_shape = input_shape
        self.num_classes = num_classes
        self.learning_rate = learning_rate
        self.model = self._build_model()

    def _build_model(self):
        model = Sequential()

        # --- Lớp Input ---
        # Định nghĩa hình dạng dữ liệu đầu vào
        model.add(Input(shape=self.input_shape))

        # --- Lớp LSTM 1 ---
        # return_sequences=True để chuyển tiếp chuỗi dữ liệu sang lớp LSTM tiếp theo
        model.add(LSTM(units=64, return_sequences=True))
        model.add(Dropout(0.2)) # Tắt ngẫu nhiên 20% nơ-ron để chống học vẹt (Overfitting)

        # --- Lớp LSTM 2 ---
        # return_sequences=False vì đây là lớp cuối cùng xử lý chuỗi, chỉ cần trả về kết quả tổng hợp
        model.add(LSTM(units=32, return_sequences=False))
        model.add(Dropout(0.2))

        # --- Lớp Output (Dense) ---
        # Activation='softmax' giúp trả về xác suất % cho từng hành động (VD: Buy 80%, Sell 10%, Hold 10%)
        model.add(Dense(units=self.num_classes, activation='softmax'))

        # --- Compile Model ---
        optimizer = Adam(learning_rate=self.learning_rate)
        
        # Sử dụng loss='sparse_categorical_crossentropy' nếu nhãn dạng số nguyên (0, 1, 2)
        # Sử dụng loss='categorical_crossentropy' nếu nhãn dạng one-hot vector ([0,1,0])
        model.compile(optimizer=optimizer, 
                      loss='sparse_categorical_crossentropy', 
                      metrics=['accuracy'])
        
        return model

    def summary(self):
        """In ra cấu trúc mạng"""
        self.model.summary()

    def train(self, X_train, y_train, X_val=None, y_val=None, epochs=50, batch_size=32):
        """Huấn luyện mô hình"""
        validation_data = (X_val, y_val) if X_val is not None else None
        
        history = self.model.fit(
            X_train, y_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_data=validation_data,
            verbose=1
        )
        return history

    def save(self, filepath):
        """Lưu mô hình đã train"""
        # Tạo thư mục nếu chưa tồn tại
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        self.model.save(filepath)
        print(f"✅ Đã lưu model tại: {filepath}")

    def load(self, filepath):
        """Load mô hình từ file"""
        if os.path.exists(filepath):
            self.model = tf.keras.models.load_model(filepath)
            print(f"✅ Đã load model từ: {filepath}")
        else:
            print(f"❌ Không tìm thấy file model: {filepath}")

    def predict(self, data):
        """Dự đoán hành động"""
        return self.model.predict(data)