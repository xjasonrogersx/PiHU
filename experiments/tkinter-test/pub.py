import paho.mqtt.client as mqtt
import time
import random

# MQTT Configuration
mqtt_broker = "localhost"
mqtt_port = 1883
mqtt_topic = "car/speed"

# Initialize MQTT client
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"Connected to MQTT broker at {mqtt_broker}:{mqtt_port}")
    else:
        print(f"Failed to connect, return code {rc}")

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print(f"Unexpected disconnection, return code {rc}")

client.on_connect = on_connect
client.on_disconnect = on_disconnect

try:
    client.connect(mqtt_broker, mqtt_port, keepalive=60)
    client.loop_start()
    
    speed = 0
    direction = 1  # 1 for increasing, -1 for decreasing
    
    print(f"Publishing changing speed to topic '{mqtt_topic}' every 1 second...")
    print("Press Ctrl+C to stop\n")
    
    while True:
        # Update speed
        speed += direction * random.randint(5, 15)
        
        # Reverse direction if we hit bounds
        if speed >= 120:
            direction = -1
            speed = 120
        elif speed <= 0:
            direction = 1
            speed = 0
        
        # Publish the speed
        message = f"{speed}"
        result = client.publish(mqtt_topic, message)
        print(f"Published: {message}")
        
        time.sleep(1)
        
except KeyboardInterrupt:
    print("\nStopping publisher...")
except Exception as e:
    print(f"Error: {e}")
finally:
    client.disconnect()
    client.loop_stop()
