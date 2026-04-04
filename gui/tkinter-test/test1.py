import tkinter 
import customtkinter

from PIL import Image, ImageTk


app = customtkinter.CTk()
app.geometry("600x600")
app.title("CustomTkinter Example")

customtkinter.set_appearance_mode("dark")  # Modes: "system" (default), "dark", "light"

app.resizable(width=True, height=True)


left_frame = customtkinter.CTkFrame(master=app , fg_color="light gray")
left_frame.pack( side="left" , expand=True , fill="both" )

sub1 = customtkinter.CTkFrame(master=left_frame , corner_radius=20 , border_width=10 , fg_color="red")
sub1.pack( side="top" , expand=True , fill="both" )

text = customtkinter.CTkTextbox(master=left_frame, width=200, height=100, corner_radius=10)
text.pack(side="bottom" , expand=True , fill="both" )
text.insert( "1.0", "This is a CustomTkinter Textbox.\nYou can type here.")


# Create a CTkImage not a widget, its a utility 
ctk_image = customtkinter.CTkImage(light_image=Image.open("/workspace/PiHU/images/1775206081435.png"), size=(300, 300))

label= customtkinter.CTkLabel(master=app,  image=ctk_image , text="")
label.pack(side="right" , expand=True , fill="both") 

app.mainloop()