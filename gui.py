import customtkinter as customtkinter
import turtle
import time
import random
import colorsys
import os
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
from detectTumor import *
from highlightTumor import *
import io

# Set the script directory
script_directory = os.path.dirname(os.path.abspath(__file__))

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

class App(customtkinter.CTk):
    DT = object()

    def __init__(self):
        global mriImage
        super().__init__()
        self.attributes('-alpha', True)
        self.fileName = tk.StringVar()
        self.uploaded_image_data = None  # Important Variables
        self.uploaded_image = None
        self.DT = HighlightTumor()
        self.isTumor = False
        self.isHighlight = False
        self.curImg = 0
        self.Img = 0
        self.currentImg = None

        self.title("BrainScan")
        self.geometry(f"{1100}x{580}")

        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        # create sidebar frame with widgets
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="Brain Tumor Detection",
                                                 font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame,
                                                                       values=["System", "Dark", "Light"],
                                                                       command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 10))
        self.scaling_label = customtkinter.CTkLabel(self.sidebar_frame, text="UI Scaling:", anchor="w")
        self.scaling_label.grid(row=7, column=0, padx=20, pady=(10, 0))
        self.scaling_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame,
                                                               values=["Default", "80%", "90%", "100%", "110%", "120%"],
                                                               command=self.change_scaling_event)
        self.scaling_optionemenu.grid(row=8, column=0, padx=20, pady=(10, 20))

        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="Brain Tumor Detection",
                                                 font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Create a white line (separator) below the title
        line_canvas = customtkinter.CTkCanvas(self.sidebar_frame, bg="white", height=1)
        line_canvas.grid(row=1, column=0, padx=20, pady=0, sticky="ew")
        line_canvas.create_line(0, 0, line_canvas.winfo_width(), 0, fill="white")

        # Create a label for the description on a new line with a bigger font size
        description_text = "Detects and highlights brain tumors\ngiven magnetic resonance imaging (MRI) scans"
        self.description_label = customtkinter.CTkLabel(self.sidebar_frame, text=description_text,
                                                        font=customtkinter.CTkFont(size=14, weight="bold"))
        self.description_label.grid(row=2, column=0, padx=20, pady=(10, 10))

        # Create a canvas for displaying the image
        self.image_canvas = customtkinter.CTkCanvas(self, bg="grey17", width=250, height=250)
        self.image_canvas.grid(row=0, column=1, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.bind("<Configure>", self.handle_window_configure)

        # Create a Text widget for displaying text
        self.textbox = customtkinter.CTkTextbox(self, width=250)
        self.textbox.grid(row=1, column=1, padx=(20, 0), pady=(20, 0), sticky="nsew")

        # Set the font size for the entire text widget
        self.textbox.configure(font=customtkinter.CTkFont(size=16))

        # create tabview
        self.tabview = customtkinter.CTkTabview(self, width=250)
        self.tabview.grid(row=0, column=2, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.tabview.add("Functions")  # Change the name of the tab to "Functions"

        self.upload_image_button = customtkinter.CTkButton(self.tabview.tab("Functions"), text="Upload",
                                                           command=self.upload_image_event)
        self.upload_image_button.grid(row=0, column=0, padx=20, pady=10)

        # Add "Check Image" button
        self.check_image_button = customtkinter.CTkButton(self.tabview.tab("Functions"), text="Check Image",
                                                          command=self.check_event)
        self.check_image_button.grid(row=1, column=0, padx=20, pady=10)

        # Add "Show Highlights" button
        self.show_highlights_button = customtkinter.CTkButton(self.tabview.tab("Functions"),
                                                              text="Show/Hide Highlights", command=self.highlight_event)
        self.show_highlights_button.grid(row=2, column=0, padx=20, pady=10)
        # Screenshot button
        self.screenshot_button = customtkinter.CTkButton(self.tabview.tab("Functions"), text="Take Screenshot",
                                                         command=self.take_screenshot)
        self.screenshot_button.grid(row=3, column=0, padx=20, pady=10)

        # Create a progress bar
        self.progressbar = customtkinter.CTkProgressBar(self.tabview.tab("Functions"), mode="determinate")
        self.progressbar.grid(row=4, column=0, padx=20, pady=10)
        self.progressbar.set(-100)  # Set progress to 0 initially

        # Create a Reset button
        self.reset_button = customtkinter.CTkButton(self.tabview.tab("Functions"), text="Reset",
                                                    command=self.reset_image)
        self.reset_button.grid(row=5, column=0, padx=20, pady=10)

    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def change_scaling_event(self, new_scaling: str):
        if new_scaling == "Default":
            new_scaling_float = 1.0  # 100% scaling
        else:
            new_scaling_float = int(new_scaling.replace("%", "")) / 100

        customtkinter.set_widget_scaling(new_scaling_float)

    def sidebar_button_event(self):
        print("sidebar_button click")

    def upload_image_event(self):
        if self.uploaded_image is not None:
            self.textbox.insert("end", "Please reset image to upload another one.\n")
        else:
            # Open a file dialog to select an image file
            FILEOPENOPTIONS = dict(defaultextension='*.*',
                                   filetypes=[('jpg', '*.jpg'), ('png', '*.png'), ('jpeg', '*.jpeg'),
                                              ('All Files', '*.*')])
            self.fileName = filedialog.askopenfilename(**FILEOPENOPTIONS)
            if self.fileName:
                self.uploaded_image = self.fileName
                self.uploaded_image_data = Image.open(self.fileName)
                image = Image.open(self.fileName)
                imageName = str(self.fileName)
                mriImage = cv.imread(imageName, 1)
                self.DT.readImage(mriImage)
                self.currentImg = Image.open(self.fileName)
                self.progressbar.set(100)  # Set progress to 100% when the image is uploaded
                # Append "Image Uploaded." to the Text widget
                self.textbox.insert("end", "Image Uploaded: " + self.fileName + "\n")
                # Optionally, you can also scroll the Text widget to the end
                self.textbox.see("end")

                # Display the uploaded image on the canvas
                if self.uploaded_image_data:
                    canvas_width = self.image_canvas.winfo_width()
                    canvas_height = self.image_canvas.winfo_height()
                    # Resize the image to match the canvas size
                    image = self.uploaded_image_data.resize((canvas_width, canvas_height))
                    self.image_canvas.image = ImageTk.PhotoImage(image=image)
                    # Clear the canvas before drawing the image
                    self.image_canvas.delete("all")
                    # Draw the image to fill the canvas
                    self.image_canvas.create_image(0, 0, anchor="nw", image=self.image_canvas.image)

    def check_event(self):
        if self.uploaded_image is not None:
            res = detectTumor(self.DT.getImage())  # Use the global image variable

            if res > 0.5:
                # Tumor Detected
                self.textbox.insert("end", "Tumor Detected.\n")
                self.isTumor = True
            else:
                # No Tumor
                self.textbox.insert("end", "No Tumor Detected.\n")
        else:
            self.textbox.insert("end", "Please Upload a Image.\n")
        # Optionally, scroll the Text widget to the end
        self.textbox.see("end")

    def reset_image(self):
        self.uploaded_image = None
        self.progressbar.set(0)
        self.textbox.insert(tk.END, "Select New Image.\n")

        # Clear the canvas
        canvas_width = 250
        canvas_height = 250
        self.image_canvas.config(width=canvas_width, height=canvas_height)
        self.image_canvas.delete("all")
        self.isTumor = False
        self.isHighlight = False
        self.currentImg = None

    def handle_window_configure(self, event):
        canvas_width = self.image_canvas.winfo_width()
        canvas_height = self.image_canvas.winfo_height()

        # Check if there is an image uploaded
        if self.currentImg is not None:
            # Resize and redraw the image to fit the canvas size
            image = self.currentImg
            image = image.resize((canvas_width, canvas_height))
            self.image_canvas.image = ImageTk.PhotoImage(image=image)
            self.image_canvas.delete("all")
            self.image_canvas.create_image(0, 0, anchor="nw", image=self.image_canvas.image)

    def highlight_event(self):
        if self.isTumor:
            if self.isHighlight:
                canvas_width = self.image_canvas.winfo_width()
                canvas_height = self.image_canvas.winfo_height()
                # Resize the image to match the canvas size
                image = self.uploaded_image_data.resize((canvas_width, canvas_height))
                self.image_canvas.image = ImageTk.PhotoImage(image=image)
                # Clear the canvas before drawing the image
                self.image_canvas.delete("all")
                # Draw the image to fill the canvas
                self.image_canvas.create_image(0, 0, anchor="nw", image=self.image_canvas.image)
                self.currentImg = self.uploaded_image_data
                self.isHighlight = False  # Update Flag to noting image is not highlighted


            else:
                mriImage = cv.imread(self.uploaded_image, 1)
                self.Img = np.array(mriImage)
                self.curImg = np.array(mriImage)
                gray = cv.cvtColor(np.array(self.Img), cv.COLOR_BGR2GRAY)
                self.ret, self.thresh = cv.threshold(gray, 0, 255, cv.THRESH_BINARY_INV + cv.THRESH_OTSU)
                self.kernel = np.ones((3, 3), np.uint8)
                opening = cv.morphologyEx(self.thresh, cv.MORPH_OPEN, self.kernel, iterations=2)
                self.curImg = opening
                sure_bg = cv.dilate(self.curImg, self.kernel, iterations=3)
                dist_transform = cv.distanceTransform(self.curImg, cv.DIST_L2, 5)
                ret, sure_fg = cv.threshold(dist_transform, 0.7 * dist_transform.max(), 255, 0)
                sure_fg = np.uint8(sure_fg)
                unknown = cv.subtract(sure_bg, sure_fg)
                ret, markers = cv.connectedComponents(sure_fg)
                markers = markers + 1
                markers[unknown == 255] = 0
                markers = cv.watershed(self.Img, markers)
                self.Img[markers == -1] = [255, 0, 0]
                tumorImage = cv.cvtColor(self.Img, cv.COLOR_HSV2BGR)
                self.curImg = tumorImage
                # Update the canvas with the highlighted image
                canvas_width = self.image_canvas.winfo_width()
                canvas_height = self.image_canvas.winfo_height()

                # Convert the highlighted image (self.curImg) to a format that can be displayed on the canvas
                highlighted_image = Image.fromarray(self.curImg)

                # Resize the highlighted image to match the canvas size
                highlighted_image = highlighted_image.resize((canvas_width, canvas_height))

                # Create a PhotoImage object from the resized image
                self.image_canvas.image = ImageTk.PhotoImage(image=highlighted_image)

                # Clear the canvas before drawing the image
                self.image_canvas.delete("all")

                # Draw the highlighted image to fill the canvas
                self.image_canvas.create_image(0, 0, anchor="nw", image=self.image_canvas.image)

                # Update the flag to indicate that the image is highlighted
                self.currentImg = highlighted_image
                self.isHighlight = True


        else:
            self.textbox.insert(tk.END, "The image does not have tumors / Check Image First\n")

    def take_screenshot(self):
        if self.currentImg is not None:
            try:
                # Prompt the user to choose a location to save the screenshot
                screenshot_filename = filedialog.asksaveasfilename(
                    defaultextension=".png", filetypes=[("PNG files", "*.png")]
                )

                if screenshot_filename:
                    # Create an in-memory bytes buffer
                    screenshot_buffer = io.BytesIO()

                    # Save the screenshot as a PNG image to the buffer
                    highlighted_image = self.currentImg
                    highlighted_image.save(screenshot_buffer, format="PNG")

                    # Write the contents of the buffer to the file
                    with open(screenshot_filename, 'wb') as file:
                        file.write(screenshot_buffer.getvalue())

                    # Provide feedback to the user
                    self.textbox.insert("end", f"Screenshot saved as {screenshot_filename}\n")
            except Exception as e:
                self.textbox.insert("end", f"Error taking screenshot: {str(e)}\n")
        else:
            self.textbox.insert(tk.END, "Please upload an image.\n")
        # Optionally, scroll the Text widget to the end
        self.textbox.see("end")



def draw_loading_animation():
    # Create a Turtle screen
    screen = turtle.Screen()
    screen.title("BrainScan")
    screen.bgcolor("grey17")  # Set a dark grey background color
    screen_width = screen.window_width()
    screen_height = screen.window_height()
    screen.setup(width=screen_width, height=screen_height)

    # Create a Turtle object
    t = turtle.Turtle()
    t.speed(0)
    t.width(20)  # Initial width of the loading circle
    t.hideturtle()

    # Set the number of steps for the RGB circle animation
    num_steps = 150
    c = 0.0006

    for _ in range(random.randint(1, 3)):  # Generate a random number for loop (1-3 times)
        h = 0.6  # Initialize hue value to start at blue
        t.up()
        t.setposition(0, -100)  # Set the position at the center
        t.down()

        for step in range(num_steps):
            r, g, b = colorsys.hsv_to_rgb(h, 1, 1)  # Full saturation and value for vivid colors
            t.color(r, g, b)
            t.width(30)  # Set the circle width
            t.circle(200, 360 / num_steps)
            screen.update()
            h += c
            time.sleep(0.01)  # Add a delay to slow down the animation
        c += .001  # Change rate of change of gradient in 2nd and 3rd loop

        # Add the "SoleScan" text below the circle with a smooth animation
    t.up()
    text_x = -100  # Adjust this value to shift the text to the left
    t.goto(text_x, -170)  # Position the text below the circle
    t.down()
    t.color("azure")  # Set the text color to blue
    font = ("bold italic", 30, "bold")

    # Smoothly reveal each letter
    letter_spacing = 20  # Adjust this value to control the spacing between letters
    i = 0

    '''Make the letters print out neat'''
    for letter in "Brain":
        t.up()
        if letter == "B":
            t.forward(25)
        else:
            t.forward(15 if letter in "ain" else letter_spacing)
        # Use special_spacing for 'r', 'a', 'i', 'n'
        t.down()
        t.write(letter, align="center", font=font)
        screen.update()
        time.sleep(.15)  # Add a small delay between letters
    for letter in "Scan":
        t.up()
        t.forward(20)
        t.down()
        t.write(letter, align="center", font=font)
        screen.update()
        time.sleep(.15)  # Add a small delay between letters