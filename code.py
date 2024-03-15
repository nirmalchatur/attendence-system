import cv2
from PIL import Image, ImageTk
import face_recognition
import os
import tkinter as tk
from tkinter import simpledialog, messagebox
from datetime import datetime
import pandas as pd
from openpyxl import load_workbook

class LoginWindow:
    def __init__(self, parent):
        self.parent = parent
        self.parent.title("Login")

        # Load the background image
        background_image = Image.open("D:/pexels-shubhankar-roy-20323309.jpg")
        background_photo = ImageTk.PhotoImage(background_image)

        # Create a label to display the background image
        self.background_label = tk.Label(parent, image=background_photo)
        self.background_label.image = background_photo  # Keep a reference to avoid garbage collection
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Add a frame for login elements
        self.login_frame = tk.Frame(parent, bg="", bd=0)  # Set background to transparent
        self.login_frame.place(relx=0.5, rely=0.5, relwidth=0.3, relheight=0.5, anchor="center")

        # Add a label for the title
        self.label_title = tk.Label(self.login_frame, text="Login", font=("Helvetica", 24))
        self.label_title.pack(pady=20)

        # Username label and entry
        self.label_username = tk.Label(self.login_frame, text="Username:", font=("Helvetica", 12))
        self.label_username.pack()
        self.entry_username = tk.Entry(self.login_frame, font=("Helvetica", 12))
        self.entry_username.pack()

        # Password label and entry
        self.label_password = tk.Label(self.login_frame, text="Password:", font=("Helvetica", 12))
        self.label_password.pack()
        self.entry_password = tk.Entry(self.login_frame, show="*", font=("Helvetica", 12))
        self.entry_password.pack()

        # Login button with some styling
        self.btn_login = tk.Button(self.login_frame, text="Login", font=("Helvetica", 12), command=self.login)
        self.btn_login.pack(pady=20)

        # Capture Face button
        self.btn_capture_face = tk.Button(self.login_frame, text="Capture Face", font=("Helvetica", 12), command=self.capture_face)
        self.btn_capture_face.pack(pady=10)

        # Label to display real-time date and time
        self.label_datetime = tk.Label(self.login_frame, text="", font=("Helvetica", 12))
        self.label_datetime.pack(pady=5)

        # Update the date and time label
        self.update_datetime()


    def login(self):
        self.username = self.entry_username.get()
        self.password = self.entry_password.get()

        # Check username and password
        if self.username == "admin" and self.password == "password":
            self.parent.destroy()  # Close login window
            root = tk.Tk()  # Create main application window
            app = CameraApp(root, "Camera App")  # Start the CameraApp
            root.mainloop()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

    def capture_face(self):
        root = tk.Tk()  # Create a new window for face capture
        root.title("Capture Face")

        # Create a label for instructions
        lbl_instruction = tk.Label(root, text="Press 'A' to capture", font=("Helvetica", 12))
        lbl_instruction.pack(pady=10)

        # Function to capture face on pressing 'A'
        def on_key_press(event):
            if event.char.lower() == 'a':
                # Capture the face
                face_capture()

        root.bind("<Key>", on_key_press)

        # Function to capture the face
        def face_capture():
            # Open webcam
            cap = cv2.VideoCapture(0)

            def capture():
                ret, frame = cap.read()
                if ret:
                    # Save the captured image
                    filename = f"admin_face.jpg"
                    cv2.imwrite(filename, frame)
                    messagebox.showinfo("Face Captured", "Face captured successfully!")
                    cap.release()
                    root.destroy()

            capture()

        root.mainloop()

    def update_datetime(self):
        # Update the date and time label every second
        now = datetime.now()
        current_datetime = now.strftime("%d-%m-%Y %H:%M:%S")
        self.label_datetime.config(text="Date & Time: " + current_datetime)
        self.parent.after(1000, self.update_datetime)


class CameraApp:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)

        self.video_source = 0  # Use default camera (change if you have multiple cameras)
        self.frame_width = 640  # Width of the processed frame
        self.frame_height = 380  # Height of the processed frame

        self.vid = cv2.VideoCapture(self.video_source)

        self.canvas = tk.Canvas(window, width=self.frame_width, height=self.frame_height)
        self.canvas.pack()
        self.btn_insert_manually = tk.Button(window, text="Insert manually", width=20, command=self.insert_manually,
                                             font=("Helvetica", 12, "bold"), bg="#ffc107", fg="black",
                                             activebackground="#ffca28", activeforeground="black")
        self.btn_view_photo = tk.Button(window, text="View photo", width=20, command=self.view_photo,
                                        font=("Helvetica", 12, "bold"), bg="#2196f3", fg="white",
                                        activebackground="#1976d2", activeforeground="white")
        self.btn_view_photo.pack(pady=10)
        self.btn_insert_manually = tk.Button(window, text="Insert manually", width=20, command=self.insert_manually,
                                             font=("Helvetica", 12, "bold"), bg="#ffc107", fg="black",
                                             activebackground="#ffca28", activeforeground="black")
        self.btn_insert_manually.pack(pady=10)
        self.btn_open_camera = tk.Button(window, text="Open Camera", width=20, command=self.open_camera,
                                         font=("Helvetica", 12, "bold"), bg="#4CAF50", fg="white",
                                         activebackground="#45a049", activeforeground="white")
        self.btn_open_camera.pack(pady=10)

        self.btn_close = tk.Button(window, text="Close", width=20, command=self.close_camera,
                                   font=("Helvetica", 12, "bold"), bg="#f44336", fg="white",
                                   activebackground="#d32f2f", activeforeground="white")
        self.btn_close.pack(pady=10)

        self.is_camera_open = False
        self.unknown_name = None
        self.adhar_id = None
        self.pan_id = None

        # Load known face images and encodings
        self.known_faces_directory = "C:/Users/Nirmal chaturvedi/Desktop/known_faces"
        self.known_face_encodings = []
        self.known_face_names = []
        self.load_known_faces()

        # Create directory to store unknown faces
        self.unknown_faces_directory = "C:/Users/Nirmal chaturvedi/Desktop/now"
        self.create_directory(self.unknown_faces_directory)

        # Create Excel file to store Aadhar number, PAN card number, and name
        self.excel_file = "C:/Users/Nirmal chaturvedi/Desktop/hi.xlsx"
        self.create_excel()

        # Cooldown period for face detection (in seconds)
        self.cooldown_duration = 5
        self.last_detection_time = datetime.now()

        self.update()

        # Add entry field for searching
        self.search_entry = tk.Entry(window)
        self.search_entry.pack(pady=10)

        # Add search button
        self.btn_search = tk.Button(window, text="Search", command=self.search_person,
                                    font=("Arial", 12), bg="#007bff", fg="white",
                                    activebackground="#0056b3", activeforeground="white")

        # Adjust the search button to be rectangular
        self.btn_search.config(width=10, height=2, bd=0, relief=tk.RIDGE, padx=0, pady=0, font=("Arial", 12, "bold"))
        # Place the search button at the right top of the window
        self.btn_search.place(relx=1.0, rely=0.0, anchor=tk.NE, x=-10, y=10)

        # Add scrollbar and text widget for search result
        self.scrollbar = tk.Scrollbar(window)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.search_result_text = tk.Text(window, height=10, width=50, yscrollcommand=self.scrollbar.set)
        self.search_result_text.pack(pady=5)
        self.scrollbar.config(command=self.search_result_text.yview)

    def open_camera(self):
        if not self.is_camera_open:
            self.is_camera_open = True
            self.btn_open_camera.config(text="Close Camera")
            self.vid = cv2.VideoCapture(self.video_source)

    def load_known_faces(self):
        if not os.path.exists(self.known_faces_directory):
            print(f"Directory '{self.known_faces_directory}' does not exist.")
            return

        print("Loading known faces...")

        for filename in os.listdir(self.known_faces_directory):
            name, ext = os.path.splitext(filename)
            if ext.lower() in (".jpg", ".jpeg", ".png"):
                print(f"Loading face: {name}")
                image_path = os.path.join(self.known_faces_directory, filename)
                image = face_recognition.load_image_file(image_path)
                encoding = face_recognition.face_encodings(image)[0]
                self.known_face_encodings.append(encoding)
                self.known_face_names.append(name)

    def create_directory(self, directory):
        if not os.path.exists(directory):
            print(f"Creating directory: {directory}")
            os.makedirs(directory)

    def create_excel(self):
        if not os.path.exists(self.excel_file):
            print(f"Creating Excel file: {self.excel_file}")
            df = pd.DataFrame(columns=["Name", "Aadhar ID", "PAN ID"])
            df.to_excel(self.excel_file, index=False)

    def update(self):
        if self.is_camera_open:
            ret, frame = self.vid.read()

            if ret:
                # Resize the frame
                frame = cv2.resize(frame, (self.frame_width, self.frame_height))

                # Convert the frame to RGB for face_recognition library
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Find all face locations in the frame
                face_locations = face_recognition.face_locations(rgb_frame)
                face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

                # Get current time
                current_time = datetime.now()

                # Match faces with stored faces
                for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                    if (current_time - self.last_detection_time).total_seconds() >= self.cooldown_duration:
                        matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
                        name = "Unknown"
                        color = (0, 0, 255)  # Default color: red (for unknown faces)
                        if True in matches:
                            index = matches.index(True)
                            name = self.known_face_names[index]
                            color = (255, 0, 0)  # Blue color for known faces

                        # Draw rectangle around the face and label it
                        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                        if name == "Unknown":
                            if self.unknown_name is None:
                                self.unknown_name = self.ask_name()  # Ask for the name of the unknown face
                                self.adhar_id = self.ask_adhar_id()  # Ask for Aadhar ID
                                self.pan_id = self.ask_pan_id()  # Ask for PAN ID

                                # Check if Aadhar and PAN already exist
                                if not self.check_duplicate(self.adhar_id, self.pan_id):
                                    # Save details to Excel
                                    self.save_to_excel(self.unknown_name, self.adhar_id, self.pan_id)

                            name = self.unknown_name  # Assign the entered name to the face

                            # Debugging output
                            print("Saving unknown face")
                            print("Name:", name)
                            print("Coordinates:", (top, right, bottom, left))

                            # Save the frame containing the detected face
                            self.save_face_frame(rgb_frame, self.adhar_id)

                            # Update last detection time
                            self.last_detection_time = current_time

                        cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, color, 2)

                # Convert the frame back to RGB for displaying in tkinter
                self.photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
                self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)

            else:
                self.close_camera()  # Stop update when video ends

        self.window.after(10, self.update)

    def ask_name(self):
        name = simpledialog.askstring("Input", "Enter the name of the unknown face:")
        return name

    def ask_adhar_id(self):
        adhar_id = simpledialog.askstring("Input", "Enter Aadhar ID:")
        return adhar_id

    def ask_pan_id(self):
        pan_id = simpledialog.askstring("Input", "Enter PAN ID:")
        return pan_id

    def close_camera(self):
        if self.is_camera_open:
            self.is_camera_open = False
            self.btn_open_camera.config(text="Open Camera")
            if self.vid.isOpened():
                self.vid.release()

    def save_face_frame(self, frame, adhar_id):
        # Convert frame to grayscale
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

        # Get current time for unique filename
        current_time = datetime.now().strftime("%Y%m%d%H%M%S")
        # Save the frame as an image file in the known_faces directory
        filename = os.path.join(self.known_faces_directory, f"{adhar_id}.jpg")
        success = cv2.imwrite(filename, gray_frame)
        if success:
            print(f"Saved face frame: {filename}")
        else:
            print(f"Failed to save face frame: {filename}")

    def save_to_excel(self, name, adhar_id, pan_id):
        data = {"Name": [name], "Aadhar ID": [adhar_id], "PAN ID": [pan_id]}
        df = pd.DataFrame(data)

        if os.path.exists(self.excel_file):
            print(f"Appending to Excel file: {self.excel_file}")
            # Load the existing Excel file
            wb = load_workbook(self.excel_file)
            ws = wb.active

            # Append data to the Excel file
            for row in df.iterrows():
                values = list(row[1])
                ws.append(values)

            # Save the modified Excel file
            wb.save(self.excel_file)
            messagebox.showinfo("Success", "Record inserted successfully!")
        else:
            print(f"Creating new Excel file: {self.excel_file}")
            df.to_excel(self.excel_file, index=False)
            messagebox.showinfo("Success", "Record inserted successfully!")

    def check_duplicate(self, adhar_id, pan_id):
        try:
            df = pd.read_excel(self.excel_file)
            adhar_id = str(adhar_id).strip()  # Strip whitespace and convert to string
            pan_id = str(pan_id).strip()  # Strip whitespace and convert to string
            if df['Aadhar ID'].astype(str).str.strip().isin([adhar_id]).any() or \
                    df['PAN ID'].astype(str).str.strip().isin([pan_id]).any():
                messagebox.showinfo("Duplicate Record", "Duplicate Aadhar ID or PAN ID found.")
                return True
            else:
                return False
        except KeyError:
            return False

    def search_person(self):
        search_query = self.search_entry.get()
        if search_query:
            result = self.search_in_excel(search_query)
            self.display_search_result(result)
        else:
            messagebox.showinfo("Error", "Please enter Aadhar number or PAN number for search.")

    def insert_manually(self):
        adhar_id = simpledialog.askstring("Input", "Enter Aadhar ID:")
        if adhar_id is None:
            return  # User canceled the input
        pan_id = simpledialog.askstring("Input", "Enter PAN ID:")
        if pan_id is None:
            return  # User canceled the input

        if not self.check_duplicate(adhar_id, pan_id):
            self.save_to_excel(adhar_id, pan_id)
            messagebox.showinfo("Success", "Record inserted successfully!")
        else:
            messagebox.showinfo("Duplicate Record", "Duplicate Aadhar ID or PAN ID found.")
    def search_in_excel(self, query):
        try:
            df = pd.read_excel(self.excel_file)
            print("Data from Excel file:")
            print(df)
            result = df[(df['Aadhar ID'] == int(query)) | (df['PAN ID'] == int(query))]
            print("Search Result:")
            print(result)
            return result
        except KeyError:
            print("Error: Aadhar ID or PAN ID column not found in Excel file.")
            return None
        except Exception as e:
            print("Error during search:", e)
            return None

    def display_search_result(self, result):
        if result is not None and not result.empty:
            # Create a new window to display search results
            search_result_window = tk.Toplevel(self.window)
            search_result_window.title("Search Result")

            # Create a label to display the search result
            result_label = tk.Label(search_result_window, text="Search Result:")
            result_label.pack()

            # Create a text widget to display the search result
            result_text = tk.Text(search_result_window, height=10, width=50)
            result_text.pack()

            # Insert the search result into the text widget
            result_str = result.to_string(index=False)
            result_text.insert(tk.END, result_str)
        else:
            messagebox.showinfo("Search Result", "No matching record found.")

    def view_photo(self):
        adhar_id = simpledialog.askstring("Input", "Enter Aadhar ID:")
        if adhar_id is None:
            return  # User canceled the input
        pan_id = simpledialog.askstring("Input", "Enter PAN ID:")
        if pan_id is None:
            return  # User canceled the input

        result = self.search_in_excel(adhar_id)  # Call search_in_excel with Aadhar ID only
        if result is not None and not result.empty:
            photo_filename = os.path.join(self.known_faces_directory,
                                          f"{adhar_id}.jpg")  # Construct filename directly with Aadhar ID
            if os.path.exists(photo_filename):
                image = Image.open(photo_filename)
                image.show()
            else:
                messagebox.showinfo("Error", "Photo not found.")
        else:
            messagebox.showinfo("Error", "Record not found.")



# Create a login window
login_root = tk.Tk()
login_window = LoginWindow(login_root)
login_root.mainloop()
