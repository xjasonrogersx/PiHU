import tkinter as tk
import customtkinter as ctk
import sys
from PIL import Image, ImageTk
import paho.mqtt.client as mqtt
import threading


image_list = [
    "/workspace/PiHU/images/1775206919136.png", # car right
    "/workspace/PiHU/images/1775206081435.png", # car middle
    "/workspace/PiHU/images/1775205902337.png" ## PiHU logo
]

# Global variable to store background photo reference
bg_photo = None


# Parse command line arguments
fullscreen_mode = "--fullscreen" in sys.argv

# Create the main window
root = ctk.CTk()

# Set window size or fullscreen
if fullscreen_mode:
    root.attributes("-fullscreen", True)
    # Bind Escape key to exit fullscreen
    root.bind("<Escape>", lambda event: root.attributes("-fullscreen", False))
    # Get screen dimensions
    root.update()
    window_width = root.winfo_screenwidth()
    window_height = root.winfo_screenheight()
else:
    root.geometry("1024x800")
    window_width = 1024
    window_height = 800

root.title("PiHU")

# Create main frame for layering
main_frame = ctk.CTkFrame(root, fg_color="transparent")
main_frame.pack(fill=tk.BOTH, expand=True)

# Create a canvas for the background image
canvas = tk.Canvas(main_frame, highlightthickness=0)
canvas.pack(fill=tk.BOTH, expand=True)

# Function to load and display background image
def load_background_image(image_path):
    global bg_photo
    try:
        bg_image = Image.open(image_path)
        # Resize image to fit window
        bg_image = bg_image.resize((window_width, window_height), Image.Resampling.LANCZOS)
        bg_photo = ImageTk.PhotoImage(bg_image)
        canvas.delete("bg")
        canvas.create_image(0, 0, image=bg_photo, anchor="nw", tags="bg")
        print(f"Loaded background image: {image_path}")
    except Exception as e:
        print(f"Error loading image: {e}")

# Load initial background image
load_background_image(image_list[0])

# Keyboard event handlers for switching images
def on_key_1(event):
    load_background_image(image_list[0])

def on_key_2(event):
    load_background_image(image_list[1])

def on_key_3(event):
    load_background_image(image_list[2])

# Bind keyboard events
root.bind('1', on_key_1)
root.bind('2', on_key_2)
root.bind('3', on_key_3)

# Create panel with 80% of full height
panel_width = 300
panel_height = int(window_height * 0.8)
panel_x = 50
panel_y = int((window_height - panel_height) / 2)  # Center vertically

# Create rounded gray panel with speed text
overlay_frame = ctk.CTkFrame(
    root,
    width=panel_width,
    height=panel_height,
    fg_color="#808080",
    corner_radius=30,
    border_width=0
)
overlay_frame.place(x=panel_x, y=panel_y)

# Add the speed text in Nunito Black font
speed_label = ctk.CTkLabel(
    overlay_frame,
    text="???",
    font=("Nunito", 72, "bold"),
    text_color="white"
)
speed_label.pack(expand=True)

# MQTT Configuration
mqtt_broker = "localhost"
mqtt_port = 1883
mqtt_topic = "car/speed"

# MQTT Callbacks
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker")
        client.subscribe(mqtt_topic)
        print(f"Subscribed to topic: {mqtt_topic}")
    else:
        print(f"Failed to connect, return code {rc}")

def on_message(client, userdata, msg):
    try:
        speed_value = msg.payload.decode().strip()
        # Update the label in a thread-safe manner
        root.after(0, lambda: speed_label.configure(text=f"{speed_value} km/h"))
    except Exception as e:
        print(f"Error processing message: {e}")

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print(f"Unexpected disconnection, return code {rc}")

# Initialize MQTT client
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.on_disconnect = on_disconnect

# Connect to MQTT broker in a separate thread
def mqtt_connect():
    try:
        mqtt_client.connect(mqtt_broker, mqtt_port, keepalive=60)
        mqtt_client.loop_forever()
    except Exception as e:
        print(f"MQTT Connection Error: {e}")

mqtt_thread = threading.Thread(target=mqtt_connect, daemon=True)
mqtt_thread.start()

root.mainloop()


