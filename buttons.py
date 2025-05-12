import tkinter as tk
import customtkinter

buttonIndietro = None
buttonStart = None
buttonAnnulla = None
buttonStop = None
buttonReplay = None
buttonRegistraDiNuovo = None
buttonUploadOnline = None

greenScreenView = None

def handleButton():
    global buttonIndietro, buttonStart, buttonAnnulla, buttonStop, buttonReplay, buttonRegistraDiNuovo, buttonUploadOnline
    from background import restart_app, start_registration, registraDiNuovo, wrappper_stop_registration, wrapper_annulla_registration
    from background import wrapperButtons
    # first view buttons
    # customtkinter.CTkButton(wrapperButtons, text="Inizia", anchor="center", font=("arial", 24, "bold"), corner_radius=50, height=60 , width=160, fg_color="#155F82", text_color="white")


    buttonIndietro =   customtkinter.CTkButton(wrapperButtons, text="Indietro", command=restart_app, anchor="center", font=("arial", 24, "bold"),
                                corner_radius=50, height=60 , width=160, fg_color="#FABC37", text_color="white")
    
    buttonStart = customtkinter.CTkButton(wrapperButtons, text="Inzia video", anchor="center", command=start_registration, font=("arial", 24, "bold"), 
                                corner_radius=50, height=60 , width=160, fg_color="#155F82", text_color="white")
    
    # second view buttons
    buttonAnnulla = customtkinter.CTkButton(wrapperButtons, text="Annulla", command=wrapper_annulla_registration, anchor="center", font=("arial", 24, "bold"),
                                            corner_radius=50, height=60 , width=160, fg_color="#FABC37", text_color="white")
    
    buttonStop = customtkinter.CTkButton(wrapperButtons, text="STOP", anchor="center", command=wrappper_stop_registration, font=("arial", 24, "bold"),
                                         corner_radius=50, height=60 , width=160, fg_color="#D05C5C", text_color="white")
    # third view buttons
    buttonRegistraDiNuovo = tk.Button(wrapperButtons, text="Registra di nuovo", command=registraDiNuovo, anchor="center", font=("arial", 18, "bold"),
                                fg="white", 
                                bg="#155F82", 
                                highlightbackground="#155F82", 
                                highlightcolor="#155F82",
                                bd=0,
                                padx=20,
                                pady=10
                            )
    # fourth view button
    buttonUploadOnline = tk.Button(wrapperButtons, text="Upload video", anchor="center", font=("arial", 18, "bold"),
                                    fg="white", 
                                    bg="#155F82", 
                                    highlightbackground="#155F82", 
                                    highlightcolor="#155F82",
                                    bd=0,
                                    padx=20,
                                    pady=10
                                )

def firstButtons(greenScreenViewVar):
    print("mostro indietro e inizia video")
    greenScreenViewVar.set('first_view')
    updateButtons(greenScreenViewVar)

def secondButtons(greenScreenViewVar):
    print("mostro annulla e stop")
    greenScreenViewVar.set('second_view')
    updateButtons(greenScreenViewVar)

# def thirdButtons(greenScreenViewVar):
#     print("mostro Rivedi e upload")
#     greenScreenViewVar.set('third_view')
#     updateButtons(greenScreenViewVar)

def fourthButton(greenScreenViewVar):
    print("mostro Upload video")
    greenScreenViewVar.set('fourth_view')
    updateButtons(greenScreenViewVar)

def fifthButtons(greenScreenViewVar):
    print("rimuovo button")
    greenScreenViewVar.set('fifth_view')
    updateButtons(greenScreenViewVar)

def updateButtons(greenScreenViewVar):
    buttonIndietro.place_forget()
    buttonStart.place_forget()
    buttonAnnulla.place_forget()
    buttonStop.place_forget()
    buttonRegistraDiNuovo.place_forget()
    buttonUploadOnline.place_forget()

    print(greenScreenViewVar.get())
    if greenScreenViewVar.get() == "first_view":
        print("ciao")
        # show
        buttonIndietro.place(relx=0.375, rely=0.923)
        buttonStart.place(relx=0.52, rely=0.923)
        
        # hide
        # buttonAnnulla.place_forget()
        # buttonStop.place_forget()
        # buttonRegistraDiNuovo.place_forget()
        # buttonUploadOnline.place_forget()
        
    elif greenScreenViewVar.get() == "second_view":
        # show
        buttonAnnulla.place(relx=0.375, rely=0.923)
        buttonStop.place(relx=0.52, rely=0.923)
        # hide
        # buttonIndietro.place_forget()
        # buttonStart.place_forget()
        # buttonRegistraDiNuovo.place_forget()
        # buttonUploadOnline.place_forget()
    
    # elif greenScreenViewVar.get() == "third_view":
        # show
        # buttonRegistraDiNuovo.place(relx=0.55, rely=0.55)
        # hide
        # buttonIndietro.place_forget()
        # buttonStart.place_forget()
        # buttonAnnulla.place_forget()
        # buttonStop.place_forget()
        # buttonUploadOnline.place_forget()

    # elif greenScreenViewVar.get() == "fourth_view":
        # show
        # buttonRegistraDiNuovo.place(relx=0.56, rely=0.55)
        # buttonUploadOnline.place(relx=0.45, rely=0.925)
        # hide
        # buttonIndietro.place_forget()
        # buttonStart.place_forget()
        # buttonAnnulla.place_forget()
        # buttonStop.place_forget()
        # buttonRegistraDiNuovo.place_forget()