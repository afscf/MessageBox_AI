import tkinter as tk
import customtkinter
import sys
import os
from PIL import Image, ImageTk
from background import background_replace, configuration  # Assuming background_replace is defined elsewhere

# Get the base path (for PyInstaller compatibility)
if hasattr(sys, '_MEIPASS'):
    base_path = sys._MEIPASS
else:
    base_path = os.path.abspath(".")

# Path to assets directory
assets_dir = os.path.join(base_path, "assets")

# Get all image files from the assets directory
image_extensions = (".jpg")  # Supported formats
image_paths = [os.path.join("assets", f) for f in os.listdir(assets_dir) if f.lower().endswith(image_extensions)]

root = None

class DraggableRow:
    global root
    def __init__(self, root, img_paths):
        root = root
        self.root = root
        self.img_paths = img_paths
        self.images = []
        self.buttons = []
        self.selected_image = None  # Store selected image

        for widget in self.root.winfo_children():
            widget.pack_forget()

        # Title label
        header = tk.Frame(root, bg="#155F82", height=50)
        header.pack(fill='x', pady=(0, 250))
        title_label = tk.Label(header, text="Seleziona uno sfondo", font=("Arial", 24, "bold"), bg="#155F82", fg="#ffffff")
        title_label.pack(pady=10)

        # Create a Canvas for smooth scrolling
        self.canvas = tk.Canvas(self.root, height=320, bg="white", highlightthickness=0)
        self.frame = tk.Frame(self.canvas, bg="white", padx=95)
        
        buttonIndietro = tk.Button(self.canvas, text="⟨", bg="white", bd=0, highlightbackground="white", highlightcolor="white", font=("arial", 102, "bold"), height=2, padx=15)
        buttonIndietro.place(relx=0, rely=0.015)
        buttonIndietro.bind("<ButtonPress-1>", self.on_prev_snap)

        buttonAvanti = tk.Button(self.canvas, text="⟩", bg="white", bd=0, highlightbackground="white", highlightcolor="white", font=("arial", 102, "bold"), height=2, padx=15)
        buttonAvanti.place(relx=0.955, rely=0.015)
        buttonAvanti.bind("<ButtonPress-1>", self.on_next_snap)
        
        
        self.scroll_window = self.canvas.create_window((0, 0), window=self.frame, anchor="nw")
        self.canvas.pack(fill="both", expand=True)

        # Create the image selection buttons and the confirm button
        self.create_buttons()


        # Bind dragging events to the canvas
        # self.canvas.bind("<ButtonPress-1>", self.on_press)
        # self.canvas.bind("<B1-Motion>", self.on_drag)
        # self.canvas.bind("<ButtonRelease-1>", self.on_release)

        self.frame.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def create_buttons(self):
        """Create buttons for each image inside the frame on the canvas."""
        for img_path in self.img_paths:
            full_img_path = os.path.join(base_path, img_path)

            try:
                img = Image.open(full_img_path)
                target_width = 552
                target_height = 350
                # Calculate the aspect ratio
                aspect_ratio = img.width / img.height
                
                # Calculate new dimensions
                if img.width > img.height:  # Landscape orientation
                    new_width = target_width
                    new_height = int(target_width / aspect_ratio)
                else:  # Portrait orientation or square
                    new_height = target_height
                    new_width = int(target_height * aspect_ratio)
                
                # Resize the image to the calculated size
                img = img.resize((new_width, new_height))
                
               
                
                # Convert to PhotoImage
                img = ImageTk.PhotoImage(img)

                # Create button for each image
                btn = tk.Button(self.frame, image=img)
                btn.config(command=lambda p=img_path: self.select_image(p))
                btn.image = img  # Keep reference to prevent garbage collection
                btn.image_path = img_path
                btn.pack(side="left", padx=10, pady=10)

                self.images.append(img)
                self.buttons.append(btn)

            except Exception as e:
                print(f"Error loading image {full_img_path}: {e}")

    def select_image(self, img_path):
        """Set the selected image when a button is clicked."""    
        for button in self.buttons:
            imageButton = button.image_path # pyimage1, pyimage2 etc etc
            if img_path in imageButton:
                button.config(bd=5, relief="solid")
            else:
                button.config(bd=1)
        
        self.selected_image = img_path
        print(f"Selected image: {img_path}")  # Debugging output

        start_background_replace(self.root, self.selected_image)

    def on_button_click(self):
        """This method will be triggered when the button is clicked."""
        if self.selected_image:
            start_background_replace(self.root, self.selected_image)  # Trigger the background replace with the selected image
        else:
            print("No image selected!")  # Debugging output

    def create_rounded_rectangle(self, canvas, x1, y1, x2, y2, radius, **kwargs):
        """Create a rounded rectangle by drawing a polygon with rounded corners."""
        points = [
            (x1 + radius, y1),  # Top-left corner
            (x2 - radius, y1),  # Top-right corner
            (x2, y1 + radius),  # Right-top corner
            (x2, y2 - radius),  # Right-bottom corner
            (x2 - radius, y2),  # Bottom-right corner
            (x1 + radius, y2),  # Bottom-left corner
            (x1, y2 - radius),  # Left-bottom corner
            (x1, y1 + radius),  # Left-top corner
        ]
        canvas.create_polygon(
            points,
            smooth=True,
            fill=kwargs.get("fill", "lightblue"),
            outline=kwargs.get("outline", "lightblue"),
            width=kwargs.get("width", 1),
            tags="button"
        )

    def on_press(self, event):
        """Handle the start of dragging."""
        self.dragging = True
        self.offset_x = event.x

    def on_drag(self, event):
        """Handle dragging the image."""
        if self.dragging:
            dx = event.x - self.offset_x
            for btn in self.buttons:
                btn.place(x=btn.winfo_x() + dx, y=btn.winfo_y())

            # Update offset for next motion event
            self.offset_x = event.x
            
    def on_next_snap(self, event):
        """Handle dragging the image."""
        dx = 673.2
        for btn in self.buttons:
            btn.place(x=btn.winfo_x() - dx, y=btn.winfo_y())

    def on_prev_snap(self, event):
        """Handle dragging the image."""
        dx = 483.2
        for btn in self.buttons:
            btn.place(x=btn.winfo_x() + dx, y=btn.winfo_y())

    def on_release(self, event):
        """Stop dragging."""
        self.dragging = False

def start_background_replace(root, selected_image_path):
    """Clear the window and display only the selected image."""
    for widget in root.winfo_children():
        widget.destroy()  # Remove all widgets from window
    if configuration:
        print("configurare l'app")
    else:
        background_replace(root, selected_image_path)  # Assuming background_replace is your custom function

# Function to initiate the image selection window
def create_selection_window(root):
    """Display image selection buttons dynamically."""

    # Create a DraggableRow to display images
    draggable_row = DraggableRow(root, image_paths)