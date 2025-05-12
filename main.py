import tkinter as tk
import customtkinter
from tkinter import font
import logging
import sys
import os
import cv2
import numpy as np
from home import home

def main():
    print("Starting app...")
    root = tk.Tk()
    
    # # Apply the custom font globally
    root.option_add("*Font", "arial")
    root.configure(bg='white')
    root.title("Image Selector")
    root.attributes('-fullscreen', True)  # Fullscreen mode

    home(root)
    #create_selection_window(root)  # Call the function


    # Allow exiting fullscreen with Esc key
    root.bind("<Escape>", lambda event: root.attributes("-fullscreen", False))

    root.mainloop()
    
# [], {}


if __name__ == "__main__":    
    main()
