import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

class ValidationInterface:
    def __init__(self, master, extracted_info, text, image_paths):
        self.master = master
        self.extracted_info = extracted_info
        self.text = text
        self.image_paths = image_paths
        
        self.master.title("Extraction Validation Interface")
        self.create_widgets()

    def create_widgets(self):
        # Create a frame for the extracted information
        info_frame = ttk.Frame(self.master, padding="10")
        info_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Create a frame for the source content
        source_frame = ttk.Frame(self.master, padding="10")
        source_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Populate the info frame
        for i, (question, answer) in enumerate(self.extracted_info.items()):
            ttk.Label(info_frame, text=question, wraplength=300).grid(row=i*2, column=0, sticky=tk.W)
            text_widget = tk.Text(info_frame, height=3, width=40)
            text_widget.insert(tk.END, answer)
            text_widget.grid(row=i*2+1, column=0, sticky=(tk.W, tk.E))
            ttk.Button(info_frame, text="Validate", command=lambda q=question: self.validate(q)).grid(row=i*2+1, column=1)

        # Populate the source frame
        text_widget = tk.Text(source_frame, height=20, width=50)
        text_widget.insert(tk.END, self.text)
        text_widget.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Add a canvas for displaying images
        self.canvas = tk.Canvas(source_frame, width=400, height=400)
        self.canvas.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Add buttons to navigate through images
        ttk.Button(source_frame, text="Previous Image", command=self.prev_image).grid(row=2, column=0, sticky=tk.W)
        ttk.Button(source_frame, text="Next Image", command=self.next_image).grid(row=2, column=0, sticky=tk.E)

        self.current_image = 0
        self.display_image()

    def validate(self, question):
        # This method would be called when a validation button is clicked
        # You can implement the logic for updating the extracted information here
        print(f"Validating answer for: {question}")

    def display_image(self):
        if self.image_paths:
            image = Image.open(self.image_paths[self.current_image][1])
            image = image.resize((400, 400), Image.ANTIALIAS)
            photo = ImageTk.PhotoImage(image)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=photo)
            self.canvas.image = photo

    def next_image(self):
        if self.current_image < len(self.image_paths) - 1:
            self.current_image += 1
            self.display_image()

    def prev_image(self):
        if self.current_image > 0:
            self.current_image -= 1
            self.display_image()

# # Usage
# root = tk.Tk()
# app = ValidationInterface(root, extracted_info, text, image_paths)
# root.mainloop()