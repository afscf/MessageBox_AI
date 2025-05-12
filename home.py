import tkinter as tk
import customtkinter
from PIL import Image, ImageTk
from image_selector import create_selection_window  # Import the function

rootView = None
message = None
middleLabel = None
invitato = None
iniziaFlusso = None

def home (root):
    global message, middleLabel, iniziaFlusso, invitato, rootView
    rootView = root
    for widget in root.winfo_children():
        widget.destroy()
    
    logoMessageBox = customtkinter.CTkImage(light_image=Image.open("message-box.jpg"),
                                  size=(350,197))

    image_label = customtkinter.CTkLabel(root, image=logoMessageBox, text="")
    image_label.place(relx=0.8, rely=0.05)

    message = tk.Label(root, text="Lascia un videomessaggio di auguri", font=("Arial", 38, "bold"), bg="white", padx=10, pady=5)
    message.pack(expand=True)
    middleLabel = tk.Label(root, text="per", font=("Arial", 30, "bold"), bg="white", padx=10, pady=5)
    middleLabel.place(relx=0.48, rely=0.4925)
    invitato = tk.Label(root, text="Marco", font=("Arial", 48, "bold"), bg="white", padx=10, pady=5)
    invitato.place(relx=0.448, rely=0.558)


    wrapper = tk.Frame(root, bg="#ffffff", height=100)
    wrapper.pack(fill='x', pady=(0, 40))
    iniziaFlusso = customtkinter.CTkButton(wrapper, text="Inizia", anchor="center", font=("arial", 24, "bold"), command=startFlow, corner_radius=50, height=60 , width=160, fg_color="#155F82", text_color="white")
    iniziaFlusso.pack()
    
    logoSCF = customtkinter.CTkImage(light_image=Image.open("scf-logo.jpg"),
                                size=(420,60))

    image_label_scf = customtkinter.CTkLabel(wrapper, image=logoSCF, text="")
    image_label_scf.place(relx=0.02, rely=0)

def startFlow():
    global rootView, middleLabel, message, iniziaFlusso, invitato
    
    message.destroy()
    middleLabel.destroy()
    invitato.destroy()
    iniziaFlusso.destroy()

    create_selection_window(rootView)