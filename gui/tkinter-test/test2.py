import tkinter as tk
import customtkinter as ctk
import sys
from PIL import Image
import paho.mqtt.client as mqtt
import threading
import os

# Configuration and Image List (Adjust paths as needed for testing)
# Using absolute paths for robustness in this example
current_dir = os.path.dirname(os.path.abspath(__file__))
image_dir = os.path.join(current_dir, "../../images")

image_list = [
    os.path.join(image_dir, "1775206919136.png"), # car right
    os.path.join(image_dir, "1775206081435.png"), # car middle
    os.path.join(image_dir, "1775205902337.png")  # PiHU logo
]

# MQTT Configuration
mqtt_broker = "localhost"
mqtt_port = 1883
mqtt_topic_speed = "car/speed"
mqtt_topic_bg = "car/HU/bg_image"

# Parse command line arguments
fullscreen_mode = "--fullscreen" in sys.argv

# Initialize CustomTkinter
ctk.set_appearance_mode("dark")
root = ctk.CTk()

if fullscreen_mode:
    root.attributes("-fullscreen", True)
    root.bind("<Escape>", lambda event: root.attributes("-fullscreen", False))
    root.update()
    window_width = root.winfo_screenwidth()
    window_height = root.winfo_screenheight()
else:
    window_width, window_height = 1024, 800
    root.geometry(f"{window_width}x{window_height}")

root.title("PiHU - Dynamic Corners")

# Main Container
main_frame = ctk.CTkFrame(root, fg_color="black")
main_frame.pack(fill=tk.BOTH, expand=True)

# Background Image Label
bg_image_display = ctk.CTkLabel(main_frame, text="")
bg_image_display.place(x=0, y=0, relwidth=1, relheight=1)

# --- Helper Function for Color Conversion ---
def rgb_to_hex(rgb):
    """Converts an (R, G, B) tuple to a #RRGGBB string."""
    return '#%02x%02x%02x' % rgb

# --- Modified Load Function ---
def load_background_image(image_path):
    try:
        # 1. Open the image with PIL
        pil_image = Image.open(image_path)
        
        # Ensure image is in RGB mode before getting pixel
        rgb_pil_image = pil_image.convert('RGB')
        
        # 2. Extract top-left corner color (0, 0)
        corner_pixel = rgb_pil_image.getpixel((0, 0))
        
        # 3. Convert RGB tuple to Hex string
        corner_hex_color = rgb_to_hex(corner_pixel)
        
        # print(f"Loaded: {image_path}, Corner color: {corner_hex_color}")

        # 4. Update the CTkImage for display
        ctk_img = ctk.CTkImage(
            light_image=pil_image, 
            dark_image=pil_image, 
            size=(window_width, window_height)
        )
        bg_image_display.configure(image=ctk_img)
        bg_image_display._image = ctk_img  # Keep reference

        # 5. DYNAMIC UPDATE: Change the frame's background color
        # This fills the "empty" spaces created by rounded corners
        overlay_frame.configure(bg_color=corner_hex_color)

    except Exception as e:
        print(f"Error loading image: {e}")

# Rounded UI Panel
panel_width = 300
panel_height = int(window_height * 0.8)
panel_x = 50
panel_y = int((window_height - panel_height) / 2)

overlay_frame = ctk.CTkFrame(
    root,
    width=panel_width,
    height=panel_height,
    fg_color="#444444",      # Dark grey panel content area
    # bg_color will be set dynamically in load_background_image
    corner_radius=40         # Smooth rounded corners
)
overlay_frame.place(x=panel_x, y=panel_y)

# Speed Text
speed_label = ctk.CTkLabel(
    overlay_frame,
    text="???",
    font=("Nunito", 72, "bold"),
    text_color="white",
    fg_color="transparent"
)
speed_label.place(relx=0.5, rely=0.5, anchor="center")

# Initial Load (now triggers dynamic corner update)
load_background_image(image_list[0])

# Keyboard and MQTT Logic
def on_key_image(event, index):
    load_background_image(image_list[index])
    # Publish index as string to MQTT
    try:
        mqtt_client.publish(mqtt_topic_bg, str(index))
    except Exception as e:
        print(f"MQTT Publish error: {e}")

root.bind('1', lambda e: on_key_image(e, 0))
root.bind('2', lambda e: on_key_image(e, 1))
root.bind('3', lambda e: on_key_image(e, 2))

# MQTT Callbacks
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("MQTT Connected")
        client.subscribe([(mqtt_topic_speed, 0), (mqtt_topic_bg, 0)])
    else:
        print(f"Connection failed: {rc}")

def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode().strip()
        # print(f"Topic: {msg.topic}, Payload: {payload}")
        
        if msg.topic == mqtt_topic_speed:
            # Safely update GUI from MQTT thread
            root.after(0, lambda: speed_label.configure(text=f"{payload} km/h"))
            
        elif msg.topic == mqtt_topic_bg:
            try:
                # Try to interpret payload as list index (integer)
                index = int(payload)
                if 0 <= index < len(image_list):
                    root.after(0, lambda idx=index: load_background_image(image_list[idx]))
                else:
                    print(f"MQTT BG Index out of range: {index}")
            except ValueError:
                # If not an integer, treat payload directly as a file path
                # (Handle with caution regarding OS paths)
                if os.path.exists(payload):
                    root.after(0, lambda path=payload: load_background_image(path))
                else:
                    print(f"MQTT BG Invalid path/index: {payload}")
                    
    except Exception as e:
        print(f"MQTT Msg Error: {e}")

# Initialize and Start MQTT
# Update to modern Client initialization if necessary (depending on paho version)
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

def mqtt_worker():
    try:
        # Connect with a reasonable keepalive
        mqtt_client.connect(mqtt_broker, mqtt_port, 60)
        mqtt_client.loop_forever()
    except Exception as e:
        print(f"MQTT Thread Error (check broker): {e}")

# Use daemon thread so it exits when main app closes
threading.Thread(target=mqtt_worker, daemon=True).start()

root.mainloop()