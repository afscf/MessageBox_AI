import cv2
import sys
import os
import numpy as np
import sounddevice as sd
import tkinter as tk
from tkinter import NW, Tk, Canvas, PhotoImage
from PIL import Image, ImageTk, ImageDraw, ImageFilter
import wave
import threading
import time
from datetime import datetime
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips
from upload_online import upload_form
from pynput.keyboard import Key, Controller


# Get the directory where the app is running (for PyInstaller)
if hasattr(sys, '_MEIPASS'):
    base_path = sys._MEIPASS
else:
    base_path = os.path.abspath(".")

fps = 60
# Get current timestamp formatted as day_month_year_hour_minute_second
timestamp = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")

video_filename = "output_video.mp4"
audio_filename = "output_audio.wav"
final_output = f"final_output_{timestamp}.mp4"
print(final_output)

# Video writer
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = None  # Initialize later when recording starts

# Global variables
device_info = sd.query_devices(kind='input')
recording = False
samplerate = samplerate = 44100  # CD quality 29400
channels = 1  # Stereo
audio_data = []
audio_thread = None
start_time = 0
timer_duration = 5
show_gui = True
restart = 0
captured_background = None

cap = cv2.VideoCapture(0)
width = 1280  # Set the width of the video
height = 720  # Set the height of the video

# Apply the resolution settings
cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
frame_width = int(cap.get(3))
frame_height = int(cap.get(4))

showingButton = False

mouse_x, mouse_y = -1, -1
mouse_clicked = False

def background_replace(root, selected_image):
    root.option_add("*Font", "Helvetica 12")

    # Construct the path to the image
    image_path = os.path.join(base_path, '', selected_image)
    
    # Load the background image (replace "background.jpg" with your image file)
    background = cv2.imread(image_path)
    
    # Resize background to match video frame size
    
    background = cv2.resize(background, (frame_width, frame_height))

    # Audio recording function
    def record_audio():
        print("start recording audio")
        global audio_data
        audio_data = []
        
        def callback(indata, frames, time, status):
            if status:
                print(status)
            audio_data.append(indata.copy())

        with sd.InputStream(samplerate=samplerate, channels=channels, callback=callback):
            while recording:
                sd.sleep(100)
    
    # Function to replace green screen with the background image
    def apply_green_screen(frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # # Define range for green color in HSV
        lower_green = np.array([35, 40, 40])   # Lower bound of green
        upper_green = np.array([85, 255, 255]) # Upper bound of green

        # Create a mask for the green background
        mask = cv2.inRange(hsv, lower_green, upper_green)

        # Invert mask (to keep the subject)
        mask_inv = cv2.bitwise_not(mask)

        # Extract the subject (person) from the original frame
        person = cv2.bitwise_and(frame, frame, mask=mask_inv)

        # Extract the background image where the mask is green
        new_bg = cv2.bitwise_and(background, background, mask=mask)

        # Merge person with new background
        final_frame = cv2.add(person, new_bg)

        return final_frame
        
    # Function to handle mouse clicks on buttons
    def mouse_callback(event, x, y, flags, param):
        global recording, out, audio_thread, start_time, mouse_x, mouse_y, mouse_clicked, restart, frame

        lastFrame = None

        # Calculate button positions at the top
        button_y_start_top = 20
        button_y_end_top = 70

        # Calculate button positions at the bottom
        button_y_start = frame_height - 70
        button_y_end = frame_height - 20

        # Calculate button positions centered at bottom
        center_x = frame_width // 2
        start_x_start = center_x - 50
        start_x_end = center_x + 50
        stop_x_start = center_x - 50
        stop_x_end = center_x + 50

        #start button center right
        start_x_button_start = (frame_width // 2) + 70
        start_x_button_end = (frame_width // 2) + 190 

        # indietro button center left
        indietro_x_button_start = (frame_width // 2) - 190
        indietro_x_button_end = (frame_width // 2) - 70

        if event == cv2.EVENT_LBUTTONDOWN:
            mouse_x, mouse_y = x, y
            mouse_clicked = True

        if event == cv2.EVENT_LBUTTONDOWN:
            if not recording and indietro_x_button_start <= x <= indietro_x_button_end and button_y_start <= y <= button_y_end:
                # ✅ Restart script using os.system()
                restart = 1
                # os.system(f"{sys.executable} {' '.join(sys.argv)}")
                # sys.exit()  # Exit current process

            elif recording and start_x_button_start <= x <= start_x_button_end and button_y_start_top <= y <= button_y_end_top:
                # cancel registration event
                mouse_x, mouse_y = x, y
                mouse_clicked = True

            # Start button area
            if not recording and start_x_button_start <= x <= start_x_button_end and button_y_start <= y <= button_y_end:
                # Countdown before recording
                for i in range(3, 0, -1):
                    ret, frame = cap.read()  # Capture live frame
                    if not ret:
                        break

                    # Overlay countdown on live camera feed
                    frame[:] = (0, 0, 0)  # Clear screen (black background)

                    text_countdown = "La registrazione del video iniziera' tra"
                    text_size = cv2.getTextSize(text_countdown, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
                    text_x = (frame_width - text_size[0]) // 2
                    text_y = (frame_height + text_size[1]) // 2 - 100
                    cv2.putText(frame, text_countdown, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

                    text = f"{i}"
                    text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 4, 5)[0]
                    text_x = (frame_width - text_size[0]) // 2
                    text_y = (frame_height + text_size[1]) // 2
                    cv2.putText(frame, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 4, (255, 255, 255), 8)

                    cv2.imshow("Video Recorder", frame)
                    cv2.imshow("Video Recorder", frame)
                       #cv2.waitKey(1000)  # Wait for 1 second
                    if  i >= 1:
                        cv2.waitKey(1000)  # Wait for 1 second

                keyboard = Controller()
                keyboard.press('a')
                keyboard.release('a')
                    
                print("Recording started...")
                recording = True
                start_time = time.time()  # Start timer when recording starts
                out = cv2.VideoWriter(video_filename, fourcc, fps, (frame_width, frame_height))

                # Start audio recording
                audio_thread = threading.Thread(target=record_audio)
                audio_thread.start()

            # Stop button area
            elif recording and start_x_button_start <= x <= start_x_button_end and button_y_start <= y <= button_y_end:
                print("Recording stopped.")
                # Function to stop recording
                stop_recording(0)
    
    def stop_recording(jumpSave):
        global recording, out, audio_thread
        recording = False
        recordingVar.set('first_screen')
        if out:
            out.release()
        
        print("stop recording")

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

            # 🚀 Show buttons for "Play Video" and "Upload Online"
            display_buttons()

    def display_buttons():
        """Displays stylish buttons for 'Play Video' and 'Upload Online'."""        
        
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
        ret, frame = cap.read()
        cap.release()

        if not ret:
            print("Error: Could not read frame from video.")
            return
        
        # Button positions
        # play_button = ((50, 70), (250, 140))
        # upload_button = ((300, 70), (500, 140))

        # Define button area replay, upload
        button_y = frame_height - 50  # Adjust position

        replay_x = (frame_width // 2) - 100  # Left side
        upload_x = (frame_width // 2) + 100  # Right side

        button_width = 180
        button_height = 50

        # Draw buttons
        # draw_stylish_button(frame, play_button[0], play_button[1], (0, 180, 0), "Rivedi video")
        # draw_stylish_button(frame, upload_button[0], upload_button[1], (0, 120, 255), "Upload Online")
        draw_rounded_button(frame, "Rivedi video", replay_x, button_y, button_width, button_height, (92, 208, 108), (255, 255, 255))
        draw_rounded_button(frame, "Upload Online", upload_x, button_y, button_width, button_height, (177, 156, 50), (255, 255, 255))

        # Set mouse callback to detect button clicks
        cv2.namedWindow("Video Recorder", flags=cv2.WINDOW_GUI_NORMAL + cv2.WINDOW_NORMAL + cv2.WINDOW_AUTOSIZE)
        cv2.setWindowProperty("Video Recorder", prop_id=cv2.WND_PROP_FULLSCREEN, prop_value=cv2.WINDOW_FULLSCREEN)
        cv2.setMouseCallback("Video Recorder", button_click_callback)

        while True:
            cv2.imshow("Video Recorder", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):  # Exit with 'q'
                break
            
    def button_click_callback(event, x, y, flags, param):
        """Handles button clicks in OpenCV."""
        global frame
        button_width = 180
        button_height = 50

        # define button click area of replay
        replay_x_start_button = (frame_width // 2) - button_width
        replay_x_end_button = (frame_width // 2) - 50

        # define button click area of upload online
        upload_x_start_button = (frame_width // 2)
        upload_x_end_button = (frame_width // 2) + button_width

        button_y_start_button = (frame_height - 50) - button_height  # Adjust position
        button_y_end_button = frame_height  # Adjust position

        upload_x = (frame_width // 2) + 100  # Right side
        

        if event == cv2.EVENT_LBUTTONDOWN:
            print("x: ", x, "y: ", y)
            print(upload_x_start_button, upload_x_end_button)
            if replay_x_start_button <= x <= replay_x_end_button and button_y_start_button <= y <= button_y_end_button:
                print("Play Video button clicked!")
                play_video()
            elif upload_x_start_button <= x <= upload_x_end_button and button_y_start_button <= y <= button_y_end_button:
                print("Upload Online button clicked!")
                upload_online()

    def play_video():
        """Plays the final video inside the same OpenCV window."""
        cap = cv2.VideoCapture(final_output)

        if not cap.isOpened():
            print("Error opening video file!")
            return

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            cv2.imshow("Video Recorder", frame)

            # Exit preview with 'q'
            if cv2.waitKey(25) & 0xFF == ord('q'):
                break

        cap.release()
        display_buttons()  # Show buttons again after preview

    def upload_online():
        """Dummy function for uploading the video online."""
        upload_form(root, final_output, frame)

    def draw_rounded_button(frame, text, center_x, center_y, width, height, color, text_color, border_radius=20):
        """Draws a rounded button with centered text on the frame."""
        button_color = tuple(int(c) for c in color)  # Convert color to tuple
    
        # Define corners
        top_left = (center_x - width // 2, center_y - height // 2)
        bottom_right = (center_x + width // 2, center_y + height // 2)

        # Create a filled rectangle (center part of button)
        cv2.rectangle(frame, 
                    (top_left[0] + border_radius, top_left[1]), 
                    (bottom_right[0] - border_radius, bottom_right[1]), 
                    button_color, -1, cv2.LINE_AA)

        cv2.rectangle(frame, 
                    (top_left[0], top_left[1] + border_radius), 
                    (bottom_right[0], bottom_right[1] - border_radius), 
                    button_color, -1, cv2.LINE_AA)

        # Draw 4 filled circles for the rounded corners
        cv2.circle(frame, (top_left[0] + border_radius, top_left[1] + border_radius), border_radius, button_color, -1, cv2.LINE_AA)
        cv2.circle(frame, (bottom_right[0] - border_radius, top_left[1] + border_radius), border_radius, button_color, -1, cv2.LINE_AA)
        cv2.circle(frame, (top_left[0] + border_radius, bottom_right[1] - border_radius), border_radius, button_color, -1, cv2.LINE_AA)
        cv2.circle(frame, (bottom_right[0] - border_radius, bottom_right[1] - border_radius), border_radius, button_color, -1, cv2.LINE_AA)

        # Add text to button
        font = cv2.FONT_HERSHEY_SIMPLEX
        text_size = cv2.getTextSize(text, font, 0.7, 1)[0]
        text_x = center_x - text_size[0] // 2
        text_y = center_y + text_size[1] // 2

        cv2.putText(frame, text, (text_x, text_y), font, 0.7, text_color, 1, cv2.LINE_AA)

    def is_button_clicked(x, y, width, height):
        """Checks if the button is clicked based on the last mouse click position."""
        global mouse_x, mouse_y, mouse_clicked
        if mouse_clicked:
            if x - width//2 <= mouse_x <= x + width//2 and y - height//2 <= mouse_y <= y + height//2:
                mouse_clicked = False  # Reset click state
                return True
        return False
    
    # def photo_image(img):
    #     h, w = img.shape[:2]
    #     data = f'P6 {w} {h} 255 '.encode() + img[..., ::-1].tobytes()
    #     return PhotoImage(width=w, height=h, data=data, format='PPM')

    # def update(preview_frame):
    #     ret, frame = cap.read()
    #     if ret:
    #         photo = photo_image(preview_frame)
    #         canvas.create_image(0, 0, image=photo, anchor=NW)
    #         canvas.image = photo
    #     root.after(15, update)

    # Set mouse callback function
    # cv2.namedWindow("Video Recorder", flags=cv2.WINDOW_GUI_NORMAL + cv2.WINDOW_NORMAL)
    # cv2.setWindowProperty("Video Recorder", prop_id=cv2.WND_PROP_FULLSCREEN, prop_value=cv2.WINDOW_FULLSCREEN)
    # cv2.setMouseCallback("Video Recorder", mouse_callback)

    # Create a canvas to display the video feed
    canvas = tk.Canvas(root, width=1920, height=1080)
    canvas.pack()
    # Function to convert OpenCV frame to PhotoImage for Tkinter
    def cv_to_tk(frame):
        # Convert the color format from BGR (OpenCV) to RGB (Tkinter)

        frame = apply_green_screen(frame)
        
        preview_frame = frame.copy()
        resized_preview_frame = cv2.resize(preview_frame, (1920, 1080))
        
        # return back button
        center_x = frame_width // 2
        button_y_back = frame_height - 50  # Adjust position
        
        # Define button area
        button_y = frame_height - 50  # Adjust position
        button_width = 150
        button_height = 50
        center_x = frame_width // 2

        indietro_x = (frame_width // 2) - 80  # Left side
        start_x = (frame_width // 2) + 80  # Right side
    
        # Calculate and display timer **ONLY when recording**
        if recording:
            elapsed = time.time() - start_time  # Timer starts when recording begins
            remaining = max(timer_duration - int(elapsed), 0)
            timer_text = f"Restano: {remaining}s"
            cv2.putText(resized_preview_frame, timer_text, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)

            # Auto-stop when timer reaches 0
            if remaining == 0:
                print("Time's up! Stopping recording automatically.")
                stop_recording(0)


        cv_rgb = cv2.cvtColor(resized_preview_frame, cv2.COLOR_BGR2RGB)

        # Convert to Image for Tkinter
        pil_image = Image.fromarray(cv_rgb)
        return ImageTk.PhotoImage(pil_image)
    
    def start_recording():
        global recording, start_time, out, audio_thread
        recordingText = tk.Label(root, text="La registrazione sta per iniziare", font=("Arial", 15), anchor="center")
        recordingText.place(relx=0.5, rely=0.5)
        recordingCountDown = tk.Label(root, text="3", font=("Arial", 15), anchor="center")
        recordingCountDown.place(relx=0.5, rely=0.55)

        def countdown(n):
            global recording, start_time, out, audio_thread
            if n > 0:
                recordingCountDown.config(text=str(n))
                root.after(1000, countdown, n - 1)
            else:
                recordingCountDown.destroy()
                recordingText.destroy()
                secondButtons()
                updateButtons()
                print("Recording started...")
                recording = True
                
                start_time = time.time()  # Start timer when recording starts
                out = cv2.VideoWriter(video_filename, fourcc, fps, (frame_width, frame_height))

                # Start audio recording
                audio_thread = threading.Thread(target=record_audio)
                audio_thread.start()

        countdown(3)
    
    # first buttons
    buttonIndietro = tk.Button(root, text="Indietro", anchor="center", font=("arial", 15))
    buttonStart = tk.Button(root, text="Inzia video", anchor="center", command=start_recording, font=("arial", 15))
    # second button
    buttonAnnulla = tk.Button(root, text="Annulla", anchor="center", font=("arial", 15))
    buttonAnnulla.place(relx=0.45, rely=0.95)
    buttonStop = tk.Button(root, text="STOP", anchor="center", command=start_recording, font=("arial", 15))
    buttonStop.place(relx=0.55, rely=0.95)
    
    recordingVar = tk.StringVar(value="first_screen")


        
    def firstButtons():
        print("mostro indietro e inizia video")
        recordingVar.set('first_screen')
        updateButtons()


    def secondButtons():
        print("mostro annulla e stop")
        recordingVar.set('second_screen')
        updateButtons()

    def updateButtons():
        if recordingVar.get() == 'first_screen':
            # show
            buttonIndietro.place(relx=0.45, rely=0.95)
            buttonStart.place(relx=0.55, rely=0.95)
            # hide
            buttonAnnulla.place_forget()
            buttonStop.place_forget()

        elif recordingVar.get() == 'second_screen':
            # show
            buttonAnnulla.place(relx=0.45, rely=0.95)
            buttonStop.place(relx=0.55, rely=0.95)
            # hide
            buttonIndietro.place_forget()
            buttonStart.place_forget()
        
            

    # Function to update the video feed in the Tkinter window
    def update_video():
        ret, frame = cap.read()
        if ret:
            # If a frame is successfully read, convert and display it on the canvas
            photo = cv_to_tk(frame)
            canvas.create_image(0, 0, image=photo, anchor=NW)

            canvas.image = photo  # Keep reference to avoid garbage collection

        # Schedule the next update (approx. 15ms for 60fps)
        root.after(15, update_video)
    

   
    update_video()
    updateButtons()
    root.mainloop()
    cap.release()

    
    
        
    # # pulsanti prima schermata indietro e avanti
    # buttonIndietro = tk.Button(root, text="Annulla", anchor="center", font=("arial", 15))
    # buttonIndietro.place(relx=0.45, rely=0.95)

    # buttonStart = tk.Button(root, text="Stop", anchor="center", command=start_recording, font=("arial", 15))
    # buttonStart.place(relx=0.55, rely=0.95)



    


    # Start Tkinter main loop
    
   
    # # Start video loop
    # while True:
    #     ret, frame = cap.read()
    #     if not ret:
    #         break

    #     if restart:
    #         # ✅ Restart script using os.system()
    #         root.attributes('-fullscreen', False)  # Fullscreen mode
    #         root.destroy()
    #         cv2.destroyAllWindows()
    #         print("🔄 Restarting script...")
    #         os.system(f"{sys.executable} {' '.join(sys.argv)}")
    #         sys.exit()  # Exit current process
    #         break
        
    #     # Apply green screen effect
    #     frame = apply_green_screen(frame)
    #     preview_frame = frame.copy()

    #     # return back button
    #     center_x = frame_width // 2
    #     button_y_back = frame_height - 50  # Adjust position
        
    #     # Define button area
    #     button_y = frame_height - 50  # Adjust position
    #     button_width = 150
    #     button_height = 50
    #     center_x = frame_width // 2

    #     indietro_x = (frame_width // 2) - 80  # Left side
    #     start_x = (frame_width // 2) + 80  # Right side
    
    #     # Calculate and display timer **ONLY when recording**
    #     if recording:
    #         elapsed = time.time() - start_time  # Timer starts when recording begins
    #         remaining = max(timer_duration - int(elapsed), 0)
    #         timer_text = f"Restano: {remaining}s"
    #         cv2.putText(preview_frame, timer_text, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)

    #         # Auto-stop when timer reaches 0
    #         if remaining == 0:
    #             print("Time's up! Stopping recording automatically.")
    #             stop_recording(0)
            
    #         # Show "Annulla" button during recording
    #         draw_rounded_button(preview_frame, "Annulla", indietro_x, button_y_back, button_width, button_height, (190, 190, 190), (255, 255, 255))

    #     if not recording:
    #         # return back button
    #         draw_rounded_button(preview_frame, "", indietro_x, button_y_back + 5, button_width, button_height, (190, 190, 190), (255, 255, 255))
    #         draw_rounded_button(preview_frame, "Indietro", indietro_x, button_y_back, button_width, button_height, (190, 190, 190), (255, 255, 255))
    #         # start button
    #         draw_rounded_button(preview_frame, "", start_x, button_y + 5, button_width, button_height, (103, 88, 16), (255, 255, 255))
    #         draw_rounded_button(preview_frame, "Inizia video", start_x, button_y, button_width, button_height, (177, 156, 50), (255, 255, 255))
    #     else:
    #         # stop button
    #         draw_rounded_button(preview_frame, "STOP", start_x, button_y, button_width, button_height, (0, 0, 200), (255, 255, 255))

        
    #     # canvas = Canvas(root, width=1920, height=1080)
    #     # canvas.pack()
    #     # update(preview_frame)
    #     # root.mainloop()
        
    #     # Show video frame
    #     cv2.imshow("Video Recorder", preview_frame)

    #     if recording and out:
    #         out.write(frame)

    #     if cv2.waitKey(1) & 0xFF == ord('q'):  # Quit with 'q'
    #         break
        
    #     # Check if "Annulla" button is clicked
    #     if recording and is_button_clicked(indietro_x, button_y_back, button_width, button_height):
    #         print("Annulla pressed, restarting...")
    #         stop_recording(1)  # Stop recording if needed
    #         background_replace(root, selected_image)  # Restart function
    #         break


    cap.release()
    cv2.destroyAllWindows()



    
