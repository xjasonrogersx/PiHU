import tkinter as tk
import customtkinter as ctk
import sys
from PIL import Image, ImageTk, ImageDraw, ImageFont
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

# Create a single canvas for background and overlays
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

# Keyboard event handler for switching images
def on_key_image(event, index):
    load_background_image(image_list[index])
    mqtt_client.publish(mqtt_topic_bg, str(index))

# Bind keyboard events
root.bind('1', lambda e: on_key_image(e, 0))
root.bind('2', lambda e: on_key_image(e, 1))
root.bind('3', lambda e: on_key_image(e, 2))

# Store global references for overlays
panel_photo_ref = None
speed_photo_ref = None

# Create panel with 80% of full height
panel_width = 300
panel_height = int(window_height * 0.8)
panel_x = 50
panel_y = int((window_height - panel_height) / 2)  # Center vertically

def draw_panel_with_speed(speed_text):
    global panel_photo_ref
    
    # Create RGBA image for the panel with transparency
    panel_img = Image.new('RGBA', (panel_width, panel_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(panel_img)
    
    # Draw rounded rectangle (semi-transparent gray)
    # Draw the rectangle with rounded corners
    corner_radius = 30
    draw.rounded_rectangle(
        [(0, 0), (panel_width - 1, panel_height - 1)],
        radius=corner_radius,
        fill=(128, 128, 128, 180)  # RGB + Alpha for 70% opacity
    )
    
    # Create fonts - main speed font and smaller km/h font
    speed_font = None
    kmh_font = None
    font_paths = [
        "/workspace/PiHU/gui/test/nunito.black.ttf",
        "/workspace/PiHU/gui/test/nunito.black.ttf"
    ]
    
    for font_path in font_paths:
        try:
            speed_font = ImageFont.truetype(font_path, 100)
            kmh_font = ImageFont.truetype(font_path, 50)
            break
        except:
            continue
    
    if speed_font is None:
        speed_font = ImageFont.load_default()
        kmh_font = ImageFont.load_default()
    
    # Draw black outline for speed text with bigger outline
    text_x = panel_width // 2
    text_y = panel_height // 2
    outline_width = 6  # Bigger outline
    
    for adj_x in range(-outline_width, outline_width + 1):
        for adj_y in range(-outline_width, outline_width + 1):
            if adj_x != 0 or adj_y != 0:
                draw.text(
                    (text_x + adj_x, text_y + adj_y),
                    speed_text,
                    font=speed_font,
                    fill=(0, 0, 0, 255),
                    anchor="mm"
                )
    
    # Draw yellow speed text on top
    draw.text(
        (text_x, text_y),
        speed_text,
        font=speed_font,
        fill=(255, 255, 0, 255),
        anchor="mm"
    )
    
    # Draw "km/h" text below the speed, at half size
    kmh_x = text_x
    kmh_y = text_y + 80
    
    # Draw black outline for km/h text
    for adj_x in range(-3, 4):
        for adj_y in range(-3, 4):
            if adj_x != 0 or adj_y != 0:
                draw.text(
                    (kmh_x + adj_x, kmh_y + adj_y),
                    "km/h",
                    font=kmh_font,
                    fill=(0, 0, 0, 255),
                    anchor="mm"
                )
    
    # Draw yellow km/h text on top
    draw.text(
        (kmh_x, kmh_y),
        "km/h",
        font=kmh_font,
        fill=(255, 255, 0, 255),
        anchor="mm"
    )
    
    # Convert to PhotoImage
    panel_photo_ref = ImageTk.PhotoImage(panel_img)
    
    # Draw on canvas
    canvas.delete("panel")
    canvas.create_image(panel_x, panel_y, image=panel_photo_ref, anchor="nw", tags="panel")

# Draw initial panel
draw_panel_with_speed("???")

# MQTT Configuration
mqtt_broker = "localhost"
mqtt_port = 1883
mqtt_topic_speed = "car/speed"
mqtt_topic_bg = "car/HU/bg_image"

# MQTT Callbacks
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker")
        client.subscribe(mqtt_topic_speed)
        client.subscribe(mqtt_topic_bg)
        print(f"Subscribed to topics: {mqtt_topic_speed}, {mqtt_topic_bg}")
    else:
        print(f"Failed to connect, return code {rc}")

def on_message(client, userdata, msg):
    try:
        if msg.topic == mqtt_topic_speed:
            speed_value = msg.payload.decode().strip()
            # Update the panel display in a thread-safe manner
            root.after(0, lambda: draw_panel_with_speed(speed_value))
        elif msg.topic == mqtt_topic_bg:
            bg_index = msg.payload.decode().strip()
            try:
                # Try to parse as integer index
                index = int(bg_index)
                if 0 <= index < len(image_list):
                    root.after(0, lambda: load_background_image(image_list[index]))
                else:
                    print(f"Invalid image index: {index}. Must be 0-{len(image_list)-1}")
            except ValueError:
                # If it's not a number, treat it as a file path
                root.after(0, lambda: load_background_image(bg_index))
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


