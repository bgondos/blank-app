import streamlit as st
import json
import threading
import time
import paho.mqtt.client as mqtt

# ---------------- CONFIG ----------------
MQTT_BROKER = "172.161.52.49"
MQTT_PORT = 1883
MQTT_TOPIC = "serre/data"

# ---------------- STREAMLIT SETUP ----------------
st.set_page_config(
    page_title="🌱 Serre IoT",
    layout="wide"
)

st.title("🌱 Dashboard Serre IoT (MQTT)")

# ---------------- SESSION STATE INIT ----------------
if "data" not in st.session_state:
    st.session_state.data = {
        "temp": None,
        "humi": None,
        "lum": None,
        "pression": None,
        "alarme": None,
        "fenetre": None,
        "lampe": None,
        "pompe": None
    }

# ---------------- MQTT CALLBACKS ----------------
def on_connect(client, userdata, flags, rc):
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    payload = json.loads(msg.payload.decode())
    st.session_state.data.update(payload)

# ---------------- MQTT THREAD ----------------
def mqtt_thread():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_forever()

# Démarrer MQTT UNE SEULE FOIS
if "mqtt_started" not in st.session_state:
    threading.Thread(target=mqtt_thread, daemon=True).start()
    st.session_state.mqtt_started = True

# ---------------- DASHBOARD UI ----------------
placeholder = st.empty()

while True:
    d = st.session_state.data

    with placeholder.container():
        col1, col2, col3, col4 = st.columns(4)

        col1.metric("🌡️ Température (°C)", d["temp"])
        col2.metric("💧 Humidité (%)", d["humi"])
        col3.metric("☀️ Luminosité", d["lum"])
        col4.metric("🔽 Pression", d["pression"])

        st.divider()

        col5, col6, col7, col8 = st.columns(4)

        col5.metric("🚨 Alarme", "ON" if d["alarme"] else "OFF")
        col6.metric("🪟 Fenêtre", "OUVERTE" if d["fenetre"] else "FERMÉE")
        col7.metric("💡 Lampe", "ON" if d["lampe"] else "OFF")
        col8.metric("🚿 Pompe", "ON" if d["pompe"] else "OFF")

    time.sleep(1)
