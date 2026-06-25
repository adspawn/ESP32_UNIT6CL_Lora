// ============================================
// フラッグ確保ボタン → ブザー + C6L(Meshtastic)通知
// ============================================

// ===== ピン定義 =====
const int BUTTON_PIN = 23;   // D23: 短絡検出(入力、内部プルアップ)
const int MOSFET_PIN = 32;   // D32: MOSFET信号出力(ブザー)
const int C6L_PIN    = 22;   // D22: C6LのGrove G4(GPIO4)へ通知

// ===== 設定 =====
const unsigned long HOLD_TIME = 3000;  // 長押し判定時間(3秒)
const unsigned long C6L_PULSE = 1000;  // C6Lへの通知HIGH保持時間

// ===== 状態管理 =====
unsigned long pressStart = 0;
bool isPressing = false;
bool triggered = false;

void setup() {
  Serial.begin(115200);
  delay(2000);  // USB-CDC安定化

  pinMode(BUTTON_PIN, INPUT_PULLUP);  // 短絡でLOW
  pinMode(MOSFET_PIN, OUTPUT);
  pinMode(C6L_PIN, OUTPUT);

  digitalWrite(MOSFET_PIN, LOW);  // ブザーOFF
  digitalWrite(C6L_PIN, LOW);     // C6L通知LOW(重要:通常時はLOWで誤送信防止)

  Serial.println("Ready. D23を3秒短絡で発火");
}

void loop() {
  bool pressed = (digitalRead(BUTTON_PIN) == LOW);  // 短絡=LOW

  if (pressed) {
    if (!isPressing) {
      isPressing = true;
      pressStart = millis();
      triggered = false;
      Serial.println("短絡開始...");
    }
    if (!triggered && (millis() - pressStart >= HOLD_TIME)) {
      triggered = true;
      fire();
    }
  } else {
    if (isPressing) {
      isPressing = false;
      Serial.println("短絡解除");
    }
  }

  delay(10);  // 簡易デバウンス
}

// ===== 発火処理 =====
void fire() {
  Serial.println("3秒到達! → ブザー + C6L通知");

  // C6Lへ通知開始(G4をHIGH → Detection SensorがLOGIC_HIGH検知)
  digitalWrite(C6L_PIN, HIGH);

  // ブザー:ピッピッピッ(3回)
  for (int i = 0; i < 3; i++) {
    digitalWrite(MOSFET_PIN, HIGH);
    delay(150);
    digitalWrite(MOSFET_PIN, LOW);
    delay(150);
  }
  // ブザーで約900ms経過。C6L_PULSEまで残りを保持
  delay(C6L_PULSE - 900);

  // C6L通知終了(G4をLOWに戻す)
  digitalWrite(C6L_PIN, LOW);

  Serial.println("発火完了");
}