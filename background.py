import cv2
import sys
import os
import numpy as np
import sounddevice as sd
import platform
import subprocess
import tkinter as tk
import customtkinter
from ffpyplayer.player import MediaPlayer
from tkinter import NW, Tk, Canvas, PhotoImage
from PIL import Image, ImageTk, ImageDraw, ImageFilter
import wave
import threading
import time
from datetime import datetime
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips
from upload_online import upload_form
from pynput.keyboard import Key, Controller
import buttons


# Get the directory where the app is running (for PyInstaller)
if hasattr(sys, '_MEIPASS'):
    base_path = sys._MEIPASS
else:
    base_path = os.path.abspath(".")

color_bgr = None
configuration = False
root = None
wrapperButtons = None
image_selected = None

# Get current timestamp formatted as day_month_year_hour_minute_second
timestamp = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
video_filename = "output_video.mp4"
audio_filename = "output_audio.wav"
final_output = f"final_output_{timestamp}.mp4"

# Video writer
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
cap = cv2.VideoCapture(0)
width = 1280  # Set the width of the video
height = 720  # Set the height of the video

# Apply the resolution settings
print(cap.get(cv2.CAP_PROP_FPS), "...............")
cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

# video
recording = False
fps = 10
fpsFromCamera = cap.get(cv2.CAP_PROP_FPS)
print(fpsFromCamera, "------------------fps--------------------")
samplerate = 44100  # CD quality 29400
channels = 1  # Stereo
start_time = 0

# audio
audio_data = []
audio_thread = None
player = None


# timer
timer_duration = 180
timer_remaining = None
timer = None
pulsar_light = None
colorTimer = "white"



# view
greenScreenView = None

def apply_chroma_key(frame, background):
    """Apply chroma key effect to the frame."""
    # If processing is disabled, return the original frame
    
    lower_green = np.array([37, 50, 50]) # Lower bound of green
    upper_green = np.array([85, 255, 255])
    

    # Traditional chroma key method (color-based)
    # Convert to HSV for better color segmentation
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Create a mask based on the green color range
    mask = cv2.inRange(hsv, lower_green, upper_green)
    
    # Invert mask to get the foreground
    mask_inv = cv2.bitwise_not(mask)

    
    # Extract foreground from original frame
    fg = cv2.bitwise_and(frame, frame, mask=mask_inv)
    
    # Extract background from background image/video
    bg = cv2.bitwise_and(background, background, mask=mask)
    
    # Combine foreground and background
    result = cv2.add(fg, bg)
    
    return result

# Function to replace green screen with the background image
def apply_green_screen(frame, background):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # # Define range for green color in HSV
    lower_green = np.array([37, 50, 50]) # Lower bound of green
    upper_green = np.array([85, 255, 255]) # Upper bound of green
    # lower_green = np.array([35, 40, 40]) # Lower bound of green
    # upper_green = np.array([100, 255, 255]) # Upper bound of green
    # lower_green = np.array([40, 50, 50])   # Lower bound of green (increased saturation to avoid blues)
    # upper_green = np.array([80, 255, 255])

    # Create a mask for the green background
    mask = cv2.inRange(hsv, lower_green, upper_green)
    # Miglioramento della maschera
    mask = cv2.GaussianBlur(mask, (1, 1), 0)  # Sfocatura per bordi più morbidi
    mask = cv2.erode(mask, np.ones((10, 10), np.uint8), iterations=1)  # Erosione per rimuovere rumore
    mask = cv2.dilate(mask, np.ones((10, 10), np.uint8), iterations=1)  # Dilatazione per ripristinare i bordi

    # Invert mask (to keep the subject)
    mask_inv = cv2.bitwise_not(mask)

    # Extract the subject (person) from the original frame
    person = cv2.bitwise_and(frame, frame, mask=mask_inv)

    # Extract the background image where the mask is green
    new_bg = cv2.bitwise_and(background, background, mask=mask)
    # Fusione con alpha blending
    mask_f = mask_inv.astype(float) / 255.0
    person = person.astype(float)
    new_bg = new_bg.astype(float)
    result = cv2.addWeighted(person, 1, new_bg, 1, 0)
    result = result.astype(np.uint8)

    # Merge person with new background
    # final_frame = cv2.add(person, new_bg)

    return result

def getCenterPosition(text):
    return 0.5 - (text.winfo_width() / 100)

    
# Audio recording function
def record_audio():
    print("start recording audio")
    global audio_data, samplerate, channels
    audio_data = []
    
    def callback(indata, frames, time, status):
        if status:
            print(status)
        audio_data.append(indata.copy())

    with sd.InputStream(samplerate=samplerate, channels=channels, callback=callback):
        while recording:
            sd.sleep(100)

def start_registration():
    global recording, start_time, out, audio_thread, greenScreenView, fps, fourcc, root, width, height
    print("Recording started...")
    backgroundCounter = tk.Canvas(root, width=900, heigh=200, bg="white")
    backgroundCounter.place(relx=0.385, rely=0.45)
    recordingText = tk.Label(backgroundCounter, text="La registrazione sta per iniziare", font=("Arial", 22, "bold"), anchor="center", bg="white", padx=10, pady=5)
    recordingText.pack(pady=(20, 10), padx=20)
    # recordingText.place(relx=0.38, rely=0.5)
    recordingCountDown = tk.Label(backgroundCounter, text="3", font=("Arial", 30, "bold"), anchor="center", bg="white", padx=10, pady=5)
    recordingCountDown.pack(pady=(0, 10))
    # recordingCountDown.place(relx=getCenterPosition(recordingCountDown), rely=0.54)

    def countdown(n):
        global recording, start_time, out, audio_thread, fps, fourcc, width, height
        if n > 0:
            recordingCountDown.config(text=str(n))
            root.after(1000, countdown, n - 1)
        else:
            backgroundCounter.destroy()
            recordingCountDown.destroy()
            recordingText.destroy()
            print("Recording started...")
            greenScreenView.set('second_view')
            buttons.secondButtons(greenScreenView)
            start_time = time.time()  # Start timer when recording starts
            out = cv2.VideoWriter(video_filename, fourcc, fps, (width, height))
            recording = True
            # Start audio recording
            audio_thread = threading.Thread(target=record_audio)
            audio_thread.start()

    countdown(3)

def stop_registration(jumpSave):
    global recording, out, audio_thread, root, pulsar_light, timer
    recording = False

    if timer is not None:
        timer.destroy()
    if pulsar_light is not None:
        pulsar_light.destroy()

    if out:
        out.release() 

    print("stop recording")
    # greenScreenView.set('third_view')
    # buttons.thirdButtons(greenScreenView)

    if not jumpSave:
        # Wait for audio thread to finish
        if audio_thread:
            audio_thread.join()

        print(audio_thread)

        # Save audio file
        audio_data_np = np.concatenate(audio_data, axis=0)
        with wave.open(audio_filename, 'wb') as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(2)  # 16-bit audio
            wf.setframerate(samplerate)
            wf.writeframes((audio_data_np * 32767).astype(np.int16).tobytes())

        print("Merging video and audio...")
        
        video_clip = VideoFileClip("output_video.mp4")
        audio_clip = AudioFileClip("output_audio.wav")

        final_clip = video_clip.set_audio(audio_clip)
        final_clip.write_videofile(final_output)

        print(f"Final video saved as {final_output} 🎬")

def wrappper_stop_registration():
    global timer, pulsar_light
    timer.destroy()
    pulsar_light.destroy()
    pulsar_light = None
    greenScreenView.set("fourth_view")
    buttons.fourthButton(greenScreenView)
    stop_registration(0)

def wrapper_annulla_registration():
    global timer, pulsar_light
    timer.place_forget()
    timer = None
    pulsar_light.place_forget()
    pulsar_light = None
    greenScreenView.set("first_view")
    buttons.firstButtons(greenScreenView)
    stop_registration(1)

def uploadVideo():
    greenScreenView.set("fourth_view")
    buttons.fourthButton(greenScreenView)
    buttons.updateButtons(greenScreenView)
    background_replace(root, image_selected)

def getMiddleFrame(final_output, cap):
    # Load the video and extract a frame
    print("path del file video", final_output)
    cap = cv2.VideoCapture(final_output)
    if not cap.isOpened():
        print("Error: Could not open video file.")
        return
    
    # Get total frame count
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    if total_frames == 0:
        print("Error: No frames found in video.")
        cap.release()
        return None
    
    # Calculate middle frame index
    middle_frame_index = total_frames // 2  # Use integer division
    
    cap.set(cv2.CAP_PROP_POS_FRAMES, middle_frame_index)  # Move to desired frame
    ret, single_frame = cap.read()
    cap.release()

    if not ret:
        print("Error: Could not read frame from video.")
        return
    
    return single_frame

def restart_app():
    global root, cap, image_selected, timestamp, video_filename, audio_filename, final_output, recording, start_time, audio_data, audio_thread, timer_remaining, timer, greenScreenView
    
    root = None
    image_selected = None
    timestamp = None
    video_filename = None
    audio_filename = None
    final_output = None
    cap = None
    recording = False
    start_time = 0

    # audio
    audio_data = []
    audio_thread = None

    # timer
    timer_remaining = None
    timer = None
    pulsar_light = None

    # view
    greenScreenView = None
    
    os.system(f"{sys.executable} {' '.join(sys.argv)}")
    sys.exit()


def registraDiNuovo():
    global root, image_selected, greenScreenView, recording, timer, video_filename, audio_filename, final_output, player
    greenScreenView = None
    recording = False
    timer = None

    if player is not None:
        player.close_player()

    os.system(f"{sys.executable} {' '.join(sys.argv)}")
    sys.exit()

    # for widget in root.winfo_children():
    #     widget.pack_forget()
    
    # background_replace(root, image_selected)
# class VirtualKeyboard:
#     def __init__(self, root, entry):
#         self.root = root
#         self.root.title("Virtual Keyboard")
#         self.input = entry

#         # Create a frame to hold the virtual keyboard
#         self.keyboard_frame = tk.Frame(root, bg="#ffffff", bd=2)
#         self.keyboard_frame.pack(pady=(20, 20))

#         # Define the keys on the virtual keyboard
#         self.keys = [
#             ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', 'CANCELLA'],
#             ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
#             ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', '@'],
#             ['Z', 'X', 'C', 'V', 'B', 'N', 'M', '.'],
#             ['SPAZIO']
#         ]

#         # Create the buttons for each key
#         for row in self.keys:
#             row_frame = tk.Frame(self.keyboard_frame, bg="#ffffff")
#             row_frame.pack()

#             for key in row:
#                 if key == "SPAZIO":
#                     button = tk.Button(row_frame, text=key, bg="#ffffff", fg="black", width=40, height=2, font=('Arial', 16), bd=2,
#                                     command=lambda key=key: self.on_key_click(key))
#                 elif key == "CANCELLA":
#                     button = tk.Button(row_frame, text=key, bg="#ffffff", fg="black", width=10, height=2, font=('Arial', 16), bd=2,
#                                     command=lambda key=key: self.on_key_click(key))
#                 else:
#                     button = tk.Button(row_frame, text=key, bg="#ffffff", fg="black", width=5, height=2, font=('Arial', 16), bd=2,
#                                     command=lambda key=key: self.on_key_click(key))
#                 button.pack(side=tk.LEFT, padx=5, pady=5)

#     def on_key_click(self, key):
#         # Handle key click
#         current_text = self.input.get()

#         if key == "SPAZIO":
#             # Add a space when the Space key is clicked
#             self.input.delete(0, tk.END)
#             self.input.insert(tk.END, current_text + " ")
#         elif key == "CANCELLA":
#             # Clear the text when the Clear button is clicked
#             # self.input.delete(0, tk.END)
#             self.input.delete(len(current_text) - 1, tk.END)
#         else:
#             # Append the clicked key to the entry widget
#             self.input.delete(0, tk.END)
#             self.input.insert(tk.END, current_text + key)


class VirtualKeyboard:
    def __init__(self, root, entry):
        self.root = root
        self.root.title("Virtual Keyboard")
        self.input = entry

        # Create a frame to hold the virtual keyboard
        self.keyboard_frame = tk.Frame(root, bg="#ffffff")
        self.keyboard_frame.pack(pady=(20, 20))
        

        # Define the keys on the virtual keyboard
        self.keys = [
            ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', 'CANCELLA'],
            ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
            ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', '@'],
            ['Z', 'X', 'C', 'V', 'B', 'N', 'M', '.'],
            ['SPAZIO']
        ]

        # Create the buttons for each key
        for row in self.keys:
            row_frame = tk.Frame(self.keyboard_frame, bg="#ffffff")
            row_frame.pack()

            for key in row:
                if key == "SPAZIO":
                    button = customtkinter.CTkButton(row_frame, text=key, text_color="#000000", fg_color="white", width=400, height=60, font=('Arial', 16), border_width=1,
                                    command=lambda key=key: self.on_key_click(key))
                elif key == "CANCELLA":
                    button = customtkinter.CTkButton(row_frame, text=key, text_color="#000000", fg_color="white", width=120, height=60, font=('Arial', 16), border_width=1,
                                    command=lambda key=key: self.on_key_click(key))
                else:
                    button = customtkinter.CTkButton(row_frame, text=key, text_color="#000000", fg_color="white", width=60, height=60, font=('Arial', 16), border_width=1,
                                    command=lambda key=key: self.on_key_click(key))
                # if key == "SPAZIO":
                #     button = tk.Button(row_frame, text=key, bg="#ffffff", fg="black", width=40, height=2, font=('Arial', 16), bd=2,
                #                     command=lambda key=key: self.on_key_click(key))
                # elif key == "CANCELLA":
                #     button = tk.Button(row_frame, text=key, bg="#ffffff", fg="black", width=10, height=2, font=('Arial', 16), bd=2,
                #                     command=lambda key=key: self.on_key_click(key))
                # else:
                #     button = tk.Button(row_frame, text=key, bg="#ffffff", fg="black", width=5, height=2, font=('Arial', 16), bd=2,
                #                     command=lambda key=key: self.on_key_click(key))

                button.pack(side=tk.LEFT, padx=5, pady=5)

    def on_key_click(self, key):
        # Handle key click
        current_text = self.input.get()

        if key == "SPAZIO":
            # Add a space when the Space key is clicked
            self.input.delete(0, tk.END)
            self.input.insert(tk.END, current_text + " ")
        elif key == "CANCELLA":
            # Clear the text when the Clear button is clicked
            # self.input.delete(0, tk.END)
            self.input.delete(len(current_text) - 1, tk.END)
        else:
            # Append the clicked key to the entry widget
            self.input.delete(0, tk.END)
            self.input.insert(tk.END, current_text + key)



def configuration_app():
    def get_color(event, x, y, flags, param):
        global configuration, root, image_selected, color_bgr, root, image_selected
        if event == cv2.EVENT_LBUTTONDOWN:
            color_bgr = frame[y, x]
            color_rgb = color_bgr[::-1]
            print(f"Color (BGR):  {color_bgr}, Color (RGB): {color_rgb}")
            configuration = False
            # restart app
            cap.release()
            cv2.destroyAllWindows()

            background_replace(root, image_selected)

    if configuration:
        cv2.namedWindow("Video Feed")
        cv2.setMouseCallback("Video Feed", get_color)

        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            cv2.imshow("Video Feed", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

def background_replace(rootParam, selected_image):
    global greenScreenView, timer, image_selected, root, configuration, color_bgr, pulsar_light
    root = rootParam
    image_selected = selected_image

    wrapperButtons = tk.Frame(root, bg="#ffffff", height=105)
    wrapperButtons.pack(anchor="center", side="bottom", fill="x")
    
    def uploadVideoOnline():
            global greenScreenView, final_output, cap, player, entry_var
            button = None
            replayButton = None
            
            entry_var = tk.StringVar()

            def send_video():
                global final_output, cap, timer
                timer = None
                greenScreenView.set("fifth_view")
                if button is not None:
                    button.destroy()
                
                replayButton.destroy()

                from upload_online import upload_form
                input_value = entry.get()
                print(f"Input value: {input_value}")
                upload_form(root, final_output, input_value, cap)

            for widget in root.winfo_children():
                widget.pack_forget()

            header = tk.Frame(root, bg="#155F82", height=50)
            header.pack(fill='x', pady=(0, 10))
            title = tk.Label(header, text="Salva il video", font=("Arial", 24, "bold"), bg="#155F82", fg="#ffffff")
            title.pack(pady=10)

            middleFrame = getMiddleFrame(final_output=final_output, cap=cap)

            # Convert to Image for Tkinter
            cv_rgb = cv2.cvtColor(middleFrame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(cv_rgb)
            resizeImage = (1400, 788)
            pil_image_resized = pil_image.resize(resizeImage)
            photo = ImageTk.PhotoImage(image=pil_image_resized)
            
            imageFrame = tk.Label(root)
            imageFrame.pack(pady=(10, 10))
            
            # Function to update video frames continuously
            def update_video(player):
                global final_output
                ret, frame = cap.read()
                print(ret," ------------------------- RET")
                
                if ret:
                    print("il video sta girando")
                    # audio_frame, val = player.get_frame()
                    # Convert the frame to RGB and update the image
                    cv_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    pil_image = Image.fromarray(cv_rgb)
                    pil_image_resized = pil_image.resize(resizeImage)
                    photo = ImageTk.PhotoImage(image=pil_image_resized)
                    imageFrame.config(image=photo)
                    imageFrame.image = photo
                    root.after(60, lambda: update_video(player)) # Adjust time for smoother or slower updates
                else:
                    print("il replay è concluso")
                    cap.release()
                    player.close_player()
                    uploadVideoOnline()
                    
                    

            # Button to replay the video from the current position
            def replay_video():
                global final_output, player
                if player is not None:
                    player.close_player()

                player = MediaPlayer(final_output)
                print("replay video")
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0) # Reset to the saved frame position
                update_video(player) # Start video update from that position

            replayButton = None
            buttonRegistraDiNuovo = None
            buttonConfermaVideo = None

            containerButtons = tk.Frame(root, bg="#ffffff")
            containerButtons.pack(pady=(10, 0))

            def showKeyboard():
                global entry_var, entry, cap, final_output

                imageFrame.destroy()
                
                middleFrame2 = getMiddleFrame(final_output=final_output, cap=cap)

                # Convert to Image for Tkinter
                cv_rgb2 = cv2.cvtColor(middleFrame2, cv2.COLOR_BGR2RGB)
                pil_image2 = Image.fromarray(cv_rgb2)
                resizeImage2 = (500, 281)
                pil_image_resized2 = pil_image2.resize(resizeImage2)
                photo = ImageTk.PhotoImage(image=pil_image_resized2)
                
                imageFrame2 = tk.Label(root, image=photo)
                imageFrame2.pack(pady=(10, 10))
                imageFrame2.config(image=photo)
                imageFrame2.image = photo

                containerButtons.destroy()
                replayButton.destroy()
                buttonRegistraDiNuovo.destroy()
                buttonConfermaVideo.destroy()

                # # Schedule the next frame update
                labelInput = tk.Label(root, text="Dai un titolo al videomessaggio di auguri", font=("arial", 18, "bold"), bg="white")
                labelInput.pack(pady=(20, 10))

                # Called every time the entry text changes
                def on_entry_change(*args):
                    if len(entry_var.get().strip()) > 0:
                        button.configure(state="normal")
                    else:
                        button.configure(state="disabled")

                entry_var.trace_add("write", on_entry_change)

                entry = customtkinter.CTkEntry(root, width=600, height=60, font=("arial", 20), textvariable=entry_var)
                entry.focus()
                entry.pack(pady=(10, 0))
                # entry.bind("<FocusIn>", VirtualKeyboard(root=root, entry=entry))

                keyboard = VirtualKeyboard(root=root, entry=entry)
        
                containerButtonsKey = tk.Frame(root, bg="#ffffff")
                containerButtonsKey.pack(pady=(0, 15))
                newRegistraDiNuovo = customtkinter.CTkButton(containerButtonsKey, text="Registra di nuovo", command=registraDiNuovo, anchor="center", font=("arial", 24, "bold"),
                                                            corner_radius=50, height=60 , width=160, fg_color="#155F82", text_color="white")
                newRegistraDiNuovo.pack(side="left", padx=20)

                button = customtkinter.CTkButton(containerButtonsKey, text="Salva video", state="disabled", anchor="center", command=send_video, font=("arial", 24, "bold"),
                                    corner_radius=50, height=60 , width=160, fg_color="#5EC74E", text_color="white")
                button.pack(side="left")

            
             # Button to trigger video replay
            replayButton = customtkinter.CTkButton(containerButtons, text="Rivedi video", anchor="center", command=replay_video, font=("arial", 24, "bold"),
                                                   corner_radius=50, height=60 , width=160, fg_color="#FABC37", text_color="white")
            replayButton.pack(side="left", padx=10)

            buttonRegistraDiNuovo = customtkinter.CTkButton(containerButtons, text="Registra di nuovo", command=registraDiNuovo, anchor="center", font=("arial", 24, "bold"),
                                                            corner_radius=50, height=60 , width=160, fg_color="#155F82", text_color="white")
            buttonRegistraDiNuovo.pack(side="left", padx=10)

            buttonConfermaVideo = customtkinter.CTkButton(containerButtons, text="Conferma video", command=showKeyboard, anchor="center", font=("arial", 24, "bold"),
                                                            corner_radius=50, height=60 , width=160, fg_color="#5EC74E", text_color="white")
            buttonConfermaVideo.pack(side="left", padx=10)

            imageFrame.config(image=photo)
            imageFrame.image = photo

            cap = cv2.VideoCapture(final_output)
           
    if greenScreenView is not None and greenScreenView.get() == "fourth_view":
        print("vado alla quarta vista")
        # greenScreenView.set("fourth_view")
        # buttons.fourthButton(greenScreenView)
        uploadVideoOnline()
    else:
        print("non vado alla quarta vista")

    # Construct the path to the image
    image_path = os.path.join(base_path, '', selected_image)
    # Load the background image (replace "background.jpg" with your image file)
    background = cv2.imread(image_path)
    # Resize background to match video frame size
    background = cv2.resize(background, (width, height))

    canvas = tk.Canvas(root, width=1920, height=1080)
    canvas.pack()

    def pulsate_light():
        global pulsar_light, colorTimer
        if pulsar_light is not None and pulsar_light.cget("text_color") == "red":
            colorTimer = "white"
            pulsar_light.place_forget()

        elif pulsar_light is not None and pulsar_light.cget("text_color") != "red":
            colorTimer = "red"
            pulsar_light.place(relx=0.98, rely=0.5)
        
    # view for before or during registration
    def startView():
        global timer, timer_remaining, pulsar_light
        ret, frame = cap.read()
        if ret:
            if (selected_image != "assets/1.jpg"):
                frame = apply_chroma_key(frame, background)

            if recording and out:
                out.write(frame)
            
            if recording:
                elapsed = time.time() - start_time  # Timer starts when recording begins
                remaining = max(timer_duration - int(elapsed), 0)
                timer_text = f"Restano: {remaining}s"
                if timer_remaining is None or timer_remaining != remaining:
                    if timer is not None:
                        timer.place_forget()
                    timer_remaining = remaining
                    
                    timer = tk.Frame(root, bg="white", padx=40, pady=5, width=240, height=50)
                    timer.place(relx=0.05, rely=0.05)

                    timerContent = tk.Label(timer, text=timer_text, font=("Arial", 18, "bold"), bg="white", height=1)
                    timerContent.place(relx=-0.1, rely=0.1)

                    img = customtkinter.CTkImage(light_image=Image.open("record.png"), size=(40,40))
                    pulsar_light = customtkinter.CTkLabel(timer, text="", corner_radius=20, image=img, text_color=colorTimer, font=("Arial", 18, "bold"), height=1)
                    pulsar_light.place(relx=0.92, rely=0.5, anchor="w")  # Place it next to the timer
                    pulsate_light()

                # Auto-stop when timer reaches 0
                if remaining == 0:
                    timer.place_forget()
                    pulsar_light.place_forget()  # Remove the pulsating light when time is up
                    print("Time's up! Stopping recording automatically.")
                    greenScreenView.set("fourth_view")
                    buttons.fourthButton(greenScreenView)
                    thread = threading.Thread(stop_registration(0))
                    thread.start()

            preview_frame = frame.copy()
            resized_preview_frame = cv2.resize(preview_frame, (1920, 1080))
            
            cv_rgb = cv2.cvtColor(resized_preview_frame, cv2.COLOR_BGR2RGB)
            
            # Convert to Image for Tkinter
            pil_image = Image.fromarray(cv_rgb)
            photo = ImageTk.PhotoImage(pil_image)
        
            canvas.create_image(0, 0, image=photo, anchor=NW)
            canvas.image = photo
            view = greenScreenView
            if view is None or (view.get() == "first_view" or view.get() == "second_view"):
                root.after(7, startView)
            elif view is not None and view.get() == "fourth_view":
                cap.release()
                uploadVideoOnline()
        
    view = greenScreenView
    if view is None:
        startView()
        # handle buttons
        buttons.handleButton()
        greenScreenView = tk.StringVar(value="first_view")
        buttons.updateButtons(greenScreenView)