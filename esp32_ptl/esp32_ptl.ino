/**
 * esp32_ptl.ino — Firmware Pick-to-Light
 * GE Healthcare Buc | Ligne Pristina
 *
 * Matériel par étagère (8 bacs) :
 *  - 1 ESP32 DevKit
 *  - 8 × TM1637 (afficheur 4 digits)
 *  - 8 × LED RGB WS2812B (ruban ou individuelles)
 *  - 8 × Bouton poussoir
 *
 * MQTT topics :
 *  Subscribe : rfid/ptl/{ETAGERE_ID}        ← commandes serveur
 *  Publish   : rfid/ptl/{ETAGERE_ID}/confirm ← bouton OK pressé
 */

#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <TM1637Display.h>
#include <FastLED.h>

// ── Configuration ─────────────────────────────────────────────
const char* WIFI_SSID  = "GE_FACTORY_WIFI";      // WiFi usine
const char* WIFI_PASS  = "motdepasse_wifi";
const char* MQTT_HOST  = "10.215.86.166";         // IP du Pi (eth0 GE)
const int   MQTT_PORT  = 1883;
const char* ETAGERE_ID = "ETAGERE_1";             // ← changer par étagère

// ── Broches GPIO ──────────────────────────────────────────────
#define NUM_BACS   8
#define LED_PIN    33
#define NUM_LEDS   8

// TM1637 : CLK + DIO par afficheur
const int CLK_PINS[8] = {4,  12, 14, 16, 18, 21, 25, 27};
const int DIO_PINS[8] = {5,  13, 15, 17, 19, 22, 26, 32};

// Boutons OK
const int BTN_PINS[8] = {34, 35, 36, 39, 23, 2,  0,  10};

// IDs bacs (correspondance position → bac_id)
const char* BAC_IDS[8] = {
    "BAC_E1_0", "BAC_E1_1", "BAC_E1_2", "BAC_E1_3",
    "BAC_E1_4", "BAC_E1_5", "BAC_E1_6", "BAC_E1_7"
};

// ── Variables globales ────────────────────────────────────────
TM1637Display afficheurs[8] = {
    TM1637Display(CLK_PINS[0], DIO_PINS[0]),
    TM1637Display(CLK_PINS[1], DIO_PINS[1]),
    TM1637Display(CLK_PINS[2], DIO_PINS[2]),
    TM1637Display(CLK_PINS[3], DIO_PINS[3]),
    TM1637Display(CLK_PINS[4], DIO_PINS[4]),
    TM1637Display(CLK_PINS[5], DIO_PINS[5]),
    TM1637Display(CLK_PINS[6], DIO_PINS[6]),
    TM1637Display(CLK_PINS[7], DIO_PINS[7])
};

CRGB leds[NUM_LEDS];
WiFiClient   espClient;
PubSubClient mqtt(espClient);

bool   bac_actif[8]   = {false};
int    bac_qte[8]     = {0};
bool   btn_prev[8]    = {false};

String topic_in;
String topic_confirm;

// ── Setup WiFi ────────────────────────────────────────────────
void setup_wifi() {
    Serial.print("WiFi connexion...");
    WiFi.begin(WIFI_SSID, WIFI_PASS);
    int tries = 0;
    while (WiFi.status() != WL_CONNECTED && tries < 30) {
        delay(500); Serial.print("."); tries++;
    }
    if (WiFi.status() == WL_CONNECTED) {
        Serial.println(" OK — IP: " + WiFi.localIP().toString());
    } else {
        Serial.println(" ÉCHEC WiFi");
    }
}

// ── Callback MQTT — commandes serveur ─────────────────────────
void on_mqtt_message(char* topic, byte* payload, unsigned int len) {
    StaticJsonDocument<256> doc;
    DeserializationError err = deserializeJson(doc, payload, len);
    if (err) return;

    String action = doc["action"] | "";
    int    pos    = doc["position"] | -1;

    if (action == "allumer" && pos >= 0 && pos < NUM_BACS) {
        int qte = doc["quantite"] | 1;
        allumer_bac(pos, qte);

    } else if (action == "eteindre" && pos >= 0) {
        eteindre_bac(pos);

    } else if (action == "eteindre_tout") {
        for (int i = 0; i < NUM_BACS; i++) eteindre_bac(i);
    }
}

// ── Allumer un bac ────────────────────────────────────────────
void allumer_bac(int pos, int qte) {
    bac_actif[pos] = true;
    bac_qte[pos]   = qte;

    // LED verte
    leds[pos] = CRGB::Green;
    FastLED.show();

    // Afficheur : quantité en grand
    afficheurs[pos].setBrightness(7);
    afficheurs[pos].showNumberDec(qte, false, 4, 0);

    Serial.printf("[PTL] Bac %d allumé — Qté: %d\n", pos, qte);
}

// ── Éteindre un bac ──────────────────────────────────────────
void eteindre_bac(int pos) {
    bac_actif[pos] = false;
    bac_qte[pos]   = 0;

    // LED éteinte
    leds[pos] = CRGB::Black;
    FastLED.show();

    // Afficheur : tirets
    afficheurs[pos].setBrightness(2);
    afficheurs[pos].showNumberDecEx(0, 0b01000000, true); // " -- "

    Serial.printf("[PTL] Bac %d éteint\n", pos);
}

// ── Vérifier boutons ─────────────────────────────────────────
void check_boutons() {
    for (int i = 0; i < NUM_BACS; i++) {
        bool pressed = (digitalRead(BTN_PINS[i]) == LOW);

        if (pressed && !btn_prev[i] && bac_actif[i]) {
            // Bouton vient d'être pressé + bac actif
            Serial.printf("[PTL] Bouton bac %d pressé\n", i);

            // Flash blanc → confirmation visuelle
            leds[i] = CRGB::White;
            FastLED.show();
            delay(200);
            leds[i] = CRGB::Black;
            FastLED.show();

            // Afficheur → "OK"
            uint8_t ok_seg[] = {
                SEG_A | SEG_B | SEG_C | SEG_D | SEG_E | SEG_F,  // O
                SEG_A | SEG_F | SEG_G | SEG_E | SEG_D,           // K (approx)
                0, 0
            };
            afficheurs[i].setSegments(ok_seg);

            bac_actif[i] = false;

            // Envoyer confirmation MQTT
            StaticJsonDocument<128> doc;
            doc["bac_id"]    = BAC_IDS[i];
            doc["position"]  = i;
            doc["etagere"]   = ETAGERE_ID;
            char buf[128];
            serializeJson(doc, buf);
            mqtt.publish(topic_confirm.c_str(), buf);

            delay(2000);
            eteindre_bac(i);
        }
        btn_prev[i] = pressed;
    }
}

// ── Reconnexion MQTT ─────────────────────────────────────────
void reconnect_mqtt() {
    int tries = 0;
    while (!mqtt.connected() && tries < 5) {
        Serial.print("[MQTT] Connexion...");
        if (mqtt.connect(ETAGERE_ID)) {
            Serial.println(" OK");
            mqtt.subscribe(topic_in.c_str());
        } else {
            Serial.printf(" ÉCHEC (état=%d)\n", mqtt.state());
            delay(2000);
        }
        tries++;
    }
}

// ── Setup ─────────────────────────────────────────────────────
void setup() {
    Serial.begin(115200);
    Serial.println("\n[PTL] GE Healthcare Buc — " + String(ETAGERE_ID));

    // Topics MQTT
    topic_in      = "rfid/ptl/" + String(ETAGERE_ID);
    topic_confirm = "rfid/ptl/" + String(ETAGERE_ID) + "/confirm";

    // LEDs
    FastLED.addLeds<WS2812B, LED_PIN, GRB>(leds, NUM_LEDS);
    FastLED.setBrightness(100);
    FastLED.clear(); FastLED.show();

    // Boutons
    for (int i = 0; i < NUM_BACS; i++) {
        pinMode(BTN_PINS[i], INPUT_PULLUP);
    }

    // Afficheurs — initialisation
    for (int i = 0; i < NUM_BACS; i++) {
        afficheurs[i].setBrightness(2);
        afficheurs[i].showNumberDecEx(0, 0b01000000, true); // " --"
    }

    // Test LEDs au démarrage
    for (int i = 0; i < NUM_LEDS; i++) {
        leds[i] = CRGB::Blue; FastLED.show(); delay(80);
        leds[i] = CRGB::Black;
    }
    FastLED.show();

    // WiFi + MQTT
    setup_wifi();
    mqtt.setServer(MQTT_HOST, MQTT_PORT);
    mqtt.setCallback(on_mqtt_message);
}

// ── Loop ──────────────────────────────────────────────────────
void loop() {
    if (!mqtt.connected()) reconnect_mqtt();
    mqtt.loop();
    check_boutons();
}
