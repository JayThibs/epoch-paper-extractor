import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

class ResultsViewer:
    def __init__(self, master, extracted_info, pdf_path):
        self.master = master
        self.extracted_info = extracted_info
        self.pdf_path = pdf_path
        
        self.master.title("Results Viewer")
        self.create_widgets()

    def create_widgets(self):
        # Create a frame for the table of extracted information
        table_frame = ttk.Frame(self.master, padding="10")
        table_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Create a frame for displaying the PDF
        pdf_frame = ttk.Frame(self.master, padding="10")
        pdf_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Create the table
        self.tree = ttk.Treeview(table_frame, columns=('Question', 'Answer'), show='headings')
        self.tree.heading('Question', text='Question')
        self.tree.heading('Answer', text='Answer')
        self.tree.column('Question', width=200)
        self.tree.column('Answer', width=300)

        for question, answer in self.extracted_info.items():
            self.tree.insert('', 'end', values=(question, answer))

        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.tree.bind('<<TreeviewSelect>>', self.on_select)

        # Add a canvas for displaying PDF pages
        self.canvas = tk.Canvas(pdf_frame, width=600, height=800)
        self.canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Add buttons to navigate through PDF pages
        ttk.Button(pdf_frame, text="Previous Page", command=self.prev_page).grid(row=1, column=0, sticky=tk.W)
        ttk.Button(pdf_frame, text="Next Page", command=self.next_page).grid(row=1, column=0, sticky=tk.E)

        self.current_page = 0
        self.display_pdf_page()

    def on_select(self, event):
        selected_item = self.tree.selection()[0]