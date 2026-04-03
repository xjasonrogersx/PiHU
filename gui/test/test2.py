import tkinter as tk
import customtkinter as ctk
import sys
from PIL import Image, ImageTk

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

# Load and display the background image
try:
    bg_image = Image.open("/workspace/PiHU/images/1775206919136.png")
    # Resize image to fit window
    bg_image = bg_image.resize((window_width, window_height), Image.Resampling.LANCZOS)
    bg_photo = ImageTk.PhotoImage(bg_image)
    canvas.create_image(0, 0, image=bg_photo, anchor="nw")
    canvas.image = bg_photo  # Keep a reference
except Exception as e:
    print(f"Error loading image: {e}")

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
    text="60Kph",
    font=("Nunito Black", 72, "bold"),
    text_color="white"
)
speed_label.pack(expand=True)

root.mainloop()


