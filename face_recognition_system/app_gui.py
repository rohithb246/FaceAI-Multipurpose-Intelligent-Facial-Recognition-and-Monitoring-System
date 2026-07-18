import tkinter as tk
from tkinter import messagebox
import threading
import os
from capture_face import capture_and_register
from main import recognize_faces
from db_manager import init_db, get_all_people

init_db()

# --- GUI Functions ---
def register_person():
    # Check if camera is available
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            messagebox.showerror("Error", "Camera not available. Please check your camera connection.")
            return
        cap.release()
    except Exception as e:
        messagebox.showerror("Error", f"Camera error: {str(e)}")
        return
    
    # Update button state
    btn_register.config(state='disabled', text="Registering...")
    window.update()
    
    def register_thread():
        try:
            capture_and_register()
            # Update button back to normal
            btn_register.config(state='normal', text="Register New Person")
            # Show success message
            messagebox.showinfo("Success", "Person registered successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Registration failed: {str(e)}")
            btn_register.config(state='normal', text="Register New Person")
    
    threading.Thread(target=register_thread, daemon=True).start()

def start_recognition():
    # Check if there are registered people
    people = get_all_people()
    if not people:
        messagebox.showwarning("Warning", "No registered people found. Please register some people first.")
        return
    
    # Check if camera is available
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            messagebox.showerror("Error", "Camera not available. Please check your camera connection.")
            return
        cap.release()
    except Exception as e:
        messagebox.showerror("Error", f"Camera error: {str(e)}")
        return
    
    # Update button state
    btn_recognize.config(state='disabled', text="Starting...")
    window.update()
    
    def recognition_thread():
        try:
            recognize_faces()
            # Update button back to normal
            btn_recognize.config(state='normal', text="Start Recognition")
        except Exception as e:
            messagebox.showerror("Error", f"Recognition failed: {str(e)}")
            btn_recognize.config(state='normal', text="Start Recognition")
    
    threading.Thread(target=recognition_thread, daemon=True).start()

def show_registered_people():
    people = get_all_people()
    if not people:
        messagebox.showinfo("Info", "No registered people found.")
        return
    
    people_text = "Registered People:\n\n"
    for person in people:
        id, name, age, phone, image_path = person
        people_text += f"Name: {name}\n"
        people_text += f"Age: {age}\n"
        people_text += f"Phone: {phone}\n"
        people_text += f"Image: {image_path}\n"
        people_text += "-" * 30 + "\n"
    
    # Create a new window to show the list
    people_window = tk.Toplevel(window)
    people_window.title("Registered People")
    people_window.geometry("400x500")
    
    text_widget = tk.Text(people_window, wrap=tk.WORD, padx=10, pady=10)
    text_widget.pack(fill=tk.BOTH, expand=True)
    text_widget.insert(tk.END, people_text)
    text_widget.config(state=tk.DISABLED)

def exit_app():
    if messagebox.askokcancel("Exit", "Are you sure you want to exit?"):
        window.destroy()

# --- GUI Layout ---
window = tk.Tk()
window.title("Face Recognition System")
window.geometry("500x400")
window.configure(bg="#f0f0f0")

# Center the window
window.eval('tk::PlaceWindow . center')

lbl_title = tk.Label(window, text="Face Recognition System", font=("Arial", 20, "bold"), bg="#f0f0f0", fg="#2c3e50")
lbl_title.pack(pady=20)

# Create a frame for buttons
button_frame = tk.Frame(window, bg="#f0f0f0")
button_frame.pack(pady=20)

btn_register = tk.Button(button_frame, text="Register New Person", font=("Arial", 14), 
                        width=25, command=register_person, bg="#3498db", fg="white", 
                        relief=tk.RAISED, bd=3)
btn_register.pack(pady=10)

btn_recognize = tk.Button(button_frame, text="Start Recognition", font=("Arial", 14), 
                         width=25, command=start_recognition, bg="#27ae60", fg="white", 
                         relief=tk.RAISED, bd=3)
btn_recognize.pack(pady=10)

btn_view_people = tk.Button(button_frame, text="View Registered People", font=("Arial", 14), 
                           width=25, command=show_registered_people, bg="#f39c12", fg="white", 
                           relief=tk.RAISED, bd=3)
btn_view_people.pack(pady=10)

btn_exit = tk.Button(button_frame, text="Exit", font=("Arial", 14), 
                    width=25, command=exit_app, bg="#e74c3c", fg="white", 
                    relief=tk.RAISED, bd=3)
btn_exit.pack(pady=10)

# Status label
status_label = tk.Label(window, text="Ready", font=("Arial", 10), bg="#f0f0f0", fg="#7f8c8d")
status_label.pack(side=tk.BOTTOM, pady=10)

window.mainloop()
