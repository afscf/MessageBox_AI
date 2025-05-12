import cv2
import os
import sys
import numpy as np
from PIL import Image
from datetime import datetime
from PIL import Image, ImageTk, ImageDraw, ImageFilter
import platform
import requests  # Add this for API calls
import tkinter as tk
import customtkinter

video_name = ""
root = None



# def restart_mouse_callback(event, x, y, flags, param):
#     """Handles restart button click."""
#     if event == cv2.EVENT_LBUTTONDOWN:
#         if restart_button_top_left[0] <= x <= restart_button_bottom_right[0] and \
#            restart_button_top_left[1] <= y <= restart_button_bottom_right[1]:
#             print("Restarting script...")
#             cv2.destroyAllWindows()
#             os.system(f"{sys.executable} {' '.join(sys.argv)}")
#             sys.exit()

def restart_app():
    os.system(f"{sys.executable} {' '.join(sys.argv)}")
    sys.exit()

def complete_upload(final_output, cap):
    from background import getMiddleFrame
    global root
    for widget in root.winfo_children():
        widget.pack_forget()

   

    middleFrame = getMiddleFrame(final_output=final_output, cap=cap)

    # Convert to Image for Tkinter
    cv_rgb = cv2.cvtColor(middleFrame, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(cv_rgb)
    resizeImage = (900, 506)
    pil_image_resized = pil_image.resize(resizeImage)
    photo = ImageTk.PhotoImage(image=pil_image_resized)
    
    header = tk.Frame(root, bg="#155F82", height=50)
    header.pack(fill='x', pady=(0, 10))
    title = tk.Label(header, text="Fine", font=("Arial", 24, "bold"), bg="#155F82", fg="#ffffff")
    title.pack(pady=10)

    imageFrame = tk.Label(root)
    imageFrame.pack(pady=(100, 10))

    imageFrame.config(image=photo)
    imageFrame.image = photo

    label = tk.Label(root, text="Video salvato con successo", font=("arial", 18), bg="white")
    label.pack(pady=20)

    label = tk.Label(root, text="Grazie aver lasciato gli auguri a Marco", font=("arial", 28, "bold"), bg="white")
    label.pack(pady=20)

    root.after(5000, restart_app)

    

def upload_form(rootParam, file_path, name, cap):
    global root
    """Displays an upload form with a rounded input box and button."""
    root = rootParam

    # Generate timestamp
    timestamp = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
    
    # Construct new file name based on the provided name
    directory, original_filename = os.path.split(file_path)
    file_extension = os.path.splitext(original_filename)[1]  # Extract file extension
    clean_name = name.replace(" ", "_")
    new_file_name = f"{clean_name}_{timestamp}{file_extension}"
    new_file_path = os.path.join(directory, new_file_name)

    # Rename file before uploading
    os.rename(file_path, new_file_path)
    complete_upload(new_file_path, cap)

    print(new_file_path)

    url = "https://messagebox.scfgroup.it/api/upload"  # Replace with actual API
    files = {'file': open(new_file_path, 'rb')}
    data = {'name': name}
    header = {'x-auth-app-message-box': "MemoryBox2025@!"}

    try:
        response = requests.post(url, files=files, data=data, headers=header)
        if response.status_code == 200:
            print("✅ Upload successful!")
        else:
            print(f"❌ Upload failed: {response.status_code}")
    except Exception as e:
        print(f"⚠ Error uploading: {e}")
