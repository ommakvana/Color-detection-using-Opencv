import cv2
import numpy as np
import argparse
import tkinter as tk
from tkinter import filedialog, Scale, IntVar, StringVar
from PIL import Image, ImageTk
import colorsys

class ColorExtractorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Color Extractor and Highlighter")
        self.root.geometry("1200x800")
        
        # Variables
        self.original_image = None
        self.displayed_image = None
        self.processed_image = None
        self.current_image = None
        self.filename = None
        self.color_mode = StringVar(value="RGB")
        self.tolerance = IntVar(value=20)
        self.highlight_mode = StringVar(value="highlight")
        
        # RGB/HSV values
        self.r_value = IntVar(value=0)
        self.g_value = IntVar(value=0)
        self.b_value = IntVar(value=0)
        self.h_value = IntVar(value=0)
        self.s_value = IntVar(value=0)
        self.v_value = IntVar(value=0)
        
        # Create frames
        self.create_frames()
        self.create_menu()
        self.create_controls()
        self.create_image_display()
        
        # Status bar
        self.status_var = StringVar(value="Ready")
        self.status_bar = tk.Label(self.root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def create_frames(self):
        # Control frame (left side)
        self.control_frame = tk.Frame(self.root, width=300)
        self.control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        
        # Image frame (right side)
        self.image_frame = tk.Frame(self.root)
        self.image_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def create_menu(self):
        # Menu bar
        menubar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open", command=self.open_image)
        file_menu.add_command(label="Save Result", command=self.save_result)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Instructions", command=self.show_instructions)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menubar)
    
    def create_controls(self):
        # Color mode selection
        mode_frame = tk.LabelFrame(self.control_frame, text="Color Mode", padx=10, pady=10)
        mode_frame.pack(fill=tk.X, pady=5)
        
        tk.Radiobutton(mode_frame, text="RGB", variable=self.color_mode, 
                       value="RGB", command=self.update_color_mode).pack(anchor=tk.W)
        tk.Radiobutton(mode_frame, text="HSV", variable=self.color_mode, 
                       value="HSV", command=self.update_color_mode).pack(anchor=tk.W)
        
        # RGB controls
        self.rgb_frame = tk.LabelFrame(self.control_frame, text="RGB Values", padx=10, pady=10)
        self.rgb_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(self.rgb_frame, text="R:").grid(row=0, column=0, sticky=tk.W)
        tk.Scale(self.rgb_frame, from_=0, to=255, orient=tk.HORIZONTAL, 
                 variable=self.r_value, command=self.update_color_preview).grid(row=0, column=1, sticky=tk.W+tk.E)
        
        tk.Label(self.rgb_frame, text="G:").grid(row=1, column=0, sticky=tk.W)
        tk.Scale(self.rgb_frame, from_=0, to=255, orient=tk.HORIZONTAL, 
                 variable=self.g_value, command=self.update_color_preview).grid(row=1, column=1, sticky=tk.W+tk.E)
        
        tk.Label(self.rgb_frame, text="B:").grid(row=2, column=0, sticky=tk.W)
        tk.Scale(self.rgb_frame, from_=0, to=255, orient=tk.HORIZONTAL, 
                 variable=self.b_value, command=self.update_color_preview).grid(row=2, column=1, sticky=tk.W+tk.E)
        
        # HSV controls
        self.hsv_frame = tk.LabelFrame(self.control_frame, text="HSV Values", padx=10, pady=10)
        
        tk.Label(self.hsv_frame, text="H:").grid(row=0, column=0, sticky=tk.W)
        tk.Scale(self.hsv_frame, from_=0, to=179, orient=tk.HORIZONTAL, 
                 variable=self.h_value, command=self.update_color_preview).grid(row=0, column=1, sticky=tk.W+tk.E)
        
        tk.Label(self.hsv_frame, text="S:").grid(row=1, column=0, sticky=tk.W)
        tk.Scale(self.hsv_frame, from_=0, to=255, orient=tk.HORIZONTAL, 
                 variable=self.s_value, command=self.update_color_preview).grid(row=1, column=1, sticky=tk.W+tk.E)
        
        tk.Label(self.hsv_frame, text="V:").grid(row=2, column=0, sticky=tk.W)
        tk.Scale(self.hsv_frame, from_=0, to=255, orient=tk.HORIZONTAL, 
                 variable=self.v_value, command=self.update_color_preview).grid(row=2, column=1, sticky=tk.W+tk.E)
        
        # Color preview
        preview_frame = tk.LabelFrame(self.control_frame, text="Color Preview", padx=10, pady=10)
        preview_frame.pack(fill=tk.X, pady=5)
        
        self.color_preview = tk.Canvas(preview_frame, width=50, height=50, bg="black")
        self.color_preview.pack()
        
        # Tolerance control
        tolerance_frame = tk.LabelFrame(self.control_frame, text="Color Tolerance", padx=10, pady=10)
        tolerance_frame.pack(fill=tk.X, pady=5)
        
        tk.Scale(tolerance_frame, from_=0, to=100, orient=tk.HORIZONTAL, 
                 variable=self.tolerance, label="Tolerance").pack(fill=tk.X)
        
        # Output mode
        output_frame = tk.LabelFrame(self.control_frame, text="Output Mode", padx=10, pady=10)
        output_frame.pack(fill=tk.X, pady=5)
        
        tk.Radiobutton(output_frame, text="Highlight Color", variable=self.highlight_mode, 
                      value="highlight").pack(anchor=tk.W)
        tk.Radiobutton(output_frame, text="Extract Color (White Background)", variable=self.highlight_mode, 
                      value="extract_white").pack(anchor=tk.W)
        tk.Radiobutton(output_frame, text="Extract Color (Transparent Background)", variable=self.highlight_mode, 
                      value="extract_transparent").pack(anchor=tk.W)
        tk.Radiobutton(output_frame, text="Mask Only", variable=self.highlight_mode, 
                      value="mask").pack(anchor=tk.W)
        
        # Action buttons
        button_frame = tk.Frame(self.control_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        tk.Button(button_frame, text="Process", command=self.process_image).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Reset", command=self.reset_image).pack(side=tk.LEFT, padx=5)
        
        # Update color mode to show the right controls initially
        self.update_color_mode()
    
    def create_image_display(self):
        # Canvas for image display
        self.canvas = tk.Canvas(self.image_frame, bg="gray")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Bind click event for color picking
        self.canvas.bind("<Button-1>", self.pick_color)
        
        # ScrollTk.Bars for large images
        h_scrollbar = tk.Scrollbar(self.image_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        v_scrollbar = tk.Scrollbar(self.image_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.canvas.configure(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)
    
    def open_image(self):
        self.filename = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.tif *.tiff")]
        )
        
        if self.filename:
            # Read image
            self.original_image = cv2.imread(self.filename)
            if self.original_image is None:
                self.status_var.set(f"Error: Could not open {self.filename}")
                return
            
            # Convert from BGR to RGB for display
            self.displayed_image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
            self.current_image = self.displayed_image.copy()
            
            # Display image
            self.display_image(self.current_image)
            self.status_var.set(f"Loaded: {self.filename}")
    
    def display_image(self, image):
        if image is None:
            return
        
        # Calculate new size to fit canvas while maintaining aspect ratio
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:  # Canvas not yet realized
            canvas_width = 800
            canvas_height = 600
        
        img_height, img_width = image.shape[:2]
        scale = min(canvas_width / img_width, canvas_height / img_height)
        
        if scale < 1:
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            resized_image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
        else:
            resized_image = image.copy()
        
        # Convert to PhotoImage
        self.photo_image = ImageTk.PhotoImage(image=Image.fromarray(resized_image))
        
        # Update canvas
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo_image)
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))
    
    def update_color_mode(self):
        mode = self.color_mode.get()
        if mode == "RGB":
            self.rgb_frame.pack(fill=tk.X, pady=5)
            self.hsv_frame.pack_forget()
            self.update_color_preview()
        else:  # HSV
            self.rgb_frame.pack_forget()
            self.hsv_frame.pack(fill=tk.X, pady=5)
            self.update_color_preview()
    
    def update_color_preview(self, event=None):
        mode = self.color_mode.get()
        if mode == "RGB":
            r, g, b = self.r_value.get(), self.g_value.get(), self.b_value.get()
            h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
            self.h_value.set(int(h * 179))
            self.s_value.set(int(s * 255))
            self.v_value.set(int(v * 255))
            color = f'#{r:02x}{g:02x}{b:02x}'
        else:  # HSV
            h, s, v = self.h_value.get()/179, self.s_value.get()/255, self.v_value.get()/255
            r, g, b = colorsys.hsv_to_rgb(h, s, v)
            self.r_value.set(int(r * 255))
            self.g_value.set(int(g * 255))
            self.b_value.set(int(b * 255))
            color = f'#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}'
        
        self.color_preview.config(bg=color)
    
    def pick_color(self, event):
        if self.displayed_image is None:
            return
        
        # Get canvas coordinates
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        
        # Convert to image coordinates
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        img_height, img_width = self.displayed_image.shape[:2]
        
        scale = min(canvas_width / img_width, canvas_height / img_height)
        if scale < 1:
            img_x = int(x / scale)
            img_y = int(y / scale)
        else:
            img_x, img_y = int(x), int(y)
        
        # Check bounds
        if 0 <= img_x < img_width and 0 <= img_y < img_height:
            # Get color at that point
            color = self.displayed_image[img_y, img_x]
            r, g, b = color
            
            mode = self.color_mode.get()
            if mode == "RGB":
                self.r_value.set(r)
                self.g_value.set(g)
                self.b_value.set(b)
            else:  # HSV
                # Convert RGB to HSV
                hsv = cv2.cvtColor(np.uint8([[color]]), cv2.COLOR_RGB2HSV)[0][0]
                h, s, v = hsv
                self.h_value.set(h)
                self.s_value.set(s)
                self.v_value.set(v)
            
            self.update_color_preview()
            self.status_var.set(f"Picked color at ({img_x}, {img_y}): RGB({r}, {g}, {b})")
    
    def process_image(self):
        if self.original_image is None:
            self.status_var.set("Error: No image loaded")
            return
        
        # Get color values based on mode
        mode = self.color_mode.get()
        tolerance = self.tolerance.get()
        
        if mode == "RGB":
            # Create mask for the selected color
            lower_bound = np.array([
                max(0, self.b_value.get() - tolerance),
                max(0, self.g_value.get() - tolerance),
                max(0, self.r_value.get() - tolerance)
            ])
            upper_bound = np.array([
                min(255, self.b_value.get() + tolerance),
                min(255, self.g_value.get() + tolerance),
                min(255, self.r_value.get() + tolerance)
            ])
            mask = cv2.inRange(self.original_image, lower_bound, upper_bound)
        else:  # HSV
            # Convert image to HSV
            hsv_image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2HSV)
            
            # Create mask for the selected color
            h_tolerance = min(90, tolerance * 179/255)  # Scale tolerance for hue
            lower_bound = np.array([
                max(0, self.h_value.get() - h_tolerance),
                max(0, self.s_value.get() - tolerance),
                max(0, self.v_value.get() - tolerance)
            ])
            upper_bound = np.array([
                min(179, self.h_value.get() + h_tolerance),
                min(255, self.s_value.get() + tolerance),
                min(255, self.v_value.get() + tolerance)
            ])
            mask = cv2.inRange(hsv_image, lower_bound, upper_bound)
        
        # Process based on output mode
        highlight_mode = self.highlight_mode.get()
        
        if highlight_mode == "highlight":
            # Create a colored mask to overlay
            overlay = np.zeros_like(self.original_image)
            
            # Color the mask in bright magenta for visibility
            overlay[mask > 0] = [255, 0, 255]  # BGR magenta
            
            # Apply the overlay with transparency
            alpha = 0.5
            self.processed_image = cv2.addWeighted(self.original_image, 1, overlay, alpha, 0)
        
        elif highlight_mode == "extract_white":
            # Create white background
            self.processed_image = np.ones_like(self.original_image) * 255
            
            # Copy only the masked pixels from the original
            self.processed_image[mask > 0] = self.original_image[mask > 0]
        
        elif highlight_mode == "extract_transparent":
            # For display purposes, we'll show white background but save with transparency
            self.processed_image = np.ones_like(self.original_image) * 255
            self.processed_image[mask > 0] = self.original_image[mask > 0]
            
            # Store the mask for saving
            self.transparency_mask = mask
        
        elif highlight_mode == "mask":
            # Just display the mask
            self.processed_image = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
        
        # Display processed image
        self.current_image = cv2.cvtColor(self.processed_image, cv2.COLOR_BGR2RGB)
        self.display_image(self.current_image)
        self.status_var.set("Image processed")
    
    def reset_image(self):
        if self.displayed_image is not None:
            self.current_image = self.displayed_image.copy()
            self.display_image(self.current_image)
            self.status_var.set("Image reset")
    
    def save_result(self):
        if self.processed_image is None:
            self.status_var.set("Error: No processed image to save")
            return
        
        save_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
        )
        
        if save_path:
            highlight_mode = self.highlight_mode.get()
            
            if highlight_mode == "extract_transparent" and save_path.lower().endswith('.png'):
                # Create RGBA image with transparency
                bgr = self.processed_image
                alpha = self.transparency_mask
                
                # Convert BGR to RGB
                rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
                
                # Create transparent image
                rgba = np.dstack((rgb, alpha))
                
                # Save using PIL to preserve transparency
                Image.fromarray(rgba).save(save_path)
            else:
                cv2.imwrite(save_path, self.processed_image)
            
            self.status_var.set(f"Saved to {save_path}")
    
    def show_instructions(self):
        instructions = tk.Toplevel(self.root)
        instructions.title("Instructions")
        instructions.geometry("500x400")
        
        text = """
        Color Extractor and Highlighter Instructions:
        
        1. Open an image using File > Open.
        2. Select color mode (RGB or HSV).
        3. Choose a color either by:
           - Adjusting the sliders
           - Clicking directly on the image
        4. Adjust the tolerance to control how strict the color matching is.
        5. Select an output mode:
           - Highlight Color: Shows original image with matching colors highlighted
           - Extract Color (White Background): Shows only matching colors on white
           - Extract Color (Transparent Background): Shows matching colors with transparency (PNG only)
           - Mask Only: Shows binary mask of matching colors
        6. Click Process to apply the changes.
        7. Save the result using File > Save Result.
        
        Tips:
        - Use HSV mode for more intuitive color selection
        - Higher tolerance values will match more similar colors
        - Click Reset to revert to the original image
        """
        
        tk.Label(instructions, text=text, justify=tk.LEFT, padx=10, pady=10).pack(fill=tk.BOTH, expand=True)
    
    def show_about(self):
        about = tk.Toplevel(self.root)
        about.title("About")
        about.geometry("300x200")
        
        text = """
        Color Extractor and Highlighter
        
        A tool for identifying, highlighting, and extracting 
        specific colors from images.
        
        Built with Python, OpenCV, and Tkinter.
        """
        
        tk.Label(about, text=text, justify=tk.CENTER, padx=10, pady=10).pack(fill=tk.BOTH, expand=True)

def main():
    root = tk.Tk()
    app = ColorExtractorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
