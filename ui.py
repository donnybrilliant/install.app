import tkinter as tk
from tkinter import ttk
from fetch import fetch_homebrew_data
from search import search_packages
import subprocess
import threading
import sys


class SetupApp:
    def __init__(self, root):
        self.root = root
        self.root.title("install.sh")
        self.root.geometry("600x400")

        self.selected_packages = set()  # Track selected packages
        # Fetch and store the package data from Homebrew
        self.packages_data = fetch_homebrew_data()
        self.show_welcome_screen()

    def show_welcome_screen(self):
        self.clear_widgets()

        label = tk.Label(self.root, text="Welcome to the macOS Setup GUI", font=("Arial", 14))
        label.place(relx=0.5, rely=0.4, anchor='center')  # Adjusted rely

        button = tk.Button(self.root, text="Continue", command=self.setup_search)
        button.place(relx=0.5, rely=0.6, anchor='center')  # Adjusted rely

    def setup_search(self):
        self.clear_widgets()

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=0, column=0, sticky="nsew")
        self.setup_all_tab()
        self.setup_selected_tab()

        # Create a frame for the continue button
        button_frame = ttk.Frame(self.root)
        button_frame.grid(row=1, column=0, sticky="e")

        # Add a continue button to the frame
        continue_button = ttk.Button(button_frame, text="Continue", command=self.install_packages)
        continue_button.pack(side="right", padx=10, pady=10)


    def install_packages(self):
        self.clear_widgets()
  
        # Create a temporary Frame to get the default background color
        temp_frame = tk.Frame(self.root)
        default_bg_color = temp_frame.cget("bg")
        temp_frame.destroy()

        # Setup a Text widget to display the installation process output
        self.info_process = tk.Text(self.root, state='normal', height=15, width=50,
                                    bd=0, bg=default_bg_color, wrap="word")  # Set background color

        # Make the Text widget read-only
        self.make_text_read_only(self.info_process)
        # Pack the Text widget to fill the entire window
        self.info_process.pack(pady=10, padx=10, expand=True, fill="both")
        self.info_process.insert(tk.END, "Please enter your root password to continue.")
        # Create a frame for the continue button
        self.button_frame = ttk.Frame(self.root)
        self.button_frame.pack(side="bottom", fill="x", padx=10, pady=10)

       

        # Run the entire installation process in a new thread
        threading.Thread(target=self.run_installation_commands).start()


    def make_text_read_only(self, text_widget):
        def on_key_press(event):
            """Prevent text modification by intercepting key presses."""
            if event.keysym not in ("Up", "Down", "Left", "Right", "Copy", "Cut", "Paste"):
                return "break"  # Prevents the event from being processed further

        text_widget.bind("<Key>", on_key_press)
        text_widget.bind("<Button-1>", lambda event: "break")  # Prevent text selection with mouse


    def request_sudo_permission(self):
        try:
            # Request sudo permission via GUI
            subprocess.run(["osascript", "-e", 'do shell script "sudo -v" with administrator privileges'], check=True)
            return True
        except subprocess.CalledProcessError:
            print("Failed to obtain sudo permissions.")
            return False

    def run_helper_script(self, script_path):
        # Clear the GUI text area first
        self.info_process.config(state='normal')
        self.info_process.delete('1.0', tk.END)

        process = subprocess.Popen(["/bin/bash", script_path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, bufsize=1)

        # Poll process for new output until finished
        while True:
            nextline = process.stdout.readline()
            if nextline == '' and process.poll() is not None:
                break
            sys.stdout.write(nextline)
            sys.stdout.flush()

            # Update GUI with the output
            self.info_process.insert(tk.END, nextline)
            self.info_process.see(tk.END)
            self.info_process.update_idletasks()  # Update the text area


        exitCode = process.returncode
        if (exitCode == 0):
                         # Add a continue button to the frame

            self.info_process.insert(tk.END, "\nProcess finished successfully.")
        else:
            self.info_process.insert(tk.END, "\nProcess finished with errors.")



    def run_installation_commands(self):
        if self.request_sudo_permission():
            script_path = "./install.sh"  # Update this path
            self.run_helper_script(script_path)
            continue_button = ttk.Button(self.button_frame, text="Reboot")
            continue_button.pack(side="right")

        else:
            print("Sudo permission was not granted.")
            self.info_process.insert(tk.END, "\nSudo permission was not granted.")
            continue_button = ttk.Button(self.button_frame, text="Try Again", command=self.install_packages)
            continue_button.pack(side="right")

    def setup_all_tab(self):
        self.all_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.all_tab, text="All")

        # Search bar at the top
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(self.all_tab, textvariable=self.search_var)
        self.search_entry.pack(fill="x")
        self.search_entry.bind("<KeyRelease>", self.debounce_search)

        # Left side for the scrollable result list, taking up 30% of the width
        self.result_frame = ttk.Frame(self.all_tab)
        self.result_frame.pack(side="left", fill="y", expand=False)
        

        self.result_canvas = tk.Canvas(self.result_frame, width=180)  # Set an approximate width
        self.result_scrollbar = ttk.Scrollbar(self.result_frame, orient="vertical", command=self.result_canvas.yview)
        self.result_canvas.configure(yscrollcommand=self.result_scrollbar.set)

        self.scrollable_result_frame = ttk.Frame(self.result_canvas)
        self.result_canvas.create_window((0, 0), window=self.scrollable_result_frame, anchor="nw", width=self.result_canvas.winfo_reqwidth())

        self.result_canvas.pack(side="left", fill="both", expand=True)
        self.result_scrollbar.pack(side="right", fill="y")

        self.result_frame.bind("<Configure>", lambda e: self.result_canvas.configure(scrollregion=self.result_canvas.bbox("all")))
        self.result_canvas.bind("<Configure>", self.on_canvas_configure)



        # Right side for info display, taking up the remaining space
        self.info_text = tk.Text(self.all_tab, state="disabled", wrap="word")
        self.info_text.pack(side="left", fill="both", expand=True)

        # Insert the initial text
        self.info_text.config(state='normal')
        self.info_text.insert('end', "Search Homebrew casks and formulae.\nSelect packages to install.")
        self.info_text.config(state='disabled')



        # Adjust the packing of the result frame and info text to control their widths
        self.result_frame.pack_configure(fill="y", expand=False)
        self.info_text.pack_configure(fill="both", expand=True)


    def on_canvas_configure(self, event):
        # Set the scrollregion and the width of the scrollable_result_frame to fill the canvas
        self.result_canvas.itemconfig("all", width=event.width)
        self.result_canvas.configure(scrollregion=self.result_canvas.bbox("all"))

    def setup_selected_tab(self):
        self.selected_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.selected_tab, text="Selected")

        # List of selected packages
        self.selected_listbox = tk.Listbox(self.selected_tab)
        self.selected_listbox.pack(fill="both", expand=True)

    def debounce_search(self, event=None):
        if hasattr(self, 'debounce_job'):
            self.root.after_cancel(self.debounce_job)
        self.debounce_job = self.root.after(500, self.perform_search)

    def clear_widgets(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def perform_search(self):
        query = self.search_var.get().strip().lower()

        # If the query is less than 2 characters, display a message
        if len(query) < 2:
            self.info_text.config(state='normal')
            self.info_text.delete('1.0', 'end')
            self.info_text.insert('end', "Search Homebrew casks and formulae.\nSelect packages to install.")
            self.info_text.config(state='disabled')
            return

        results = search_packages(self.packages_data, query)
        self.display_search_results(results)

    def fetch_package_info(self, package_name):
        # Search for the package dictionary by name
        for package in self.packages_data:
            if package['name'].lower() == package_name.lower():
                # Construct a detailed info string (customize as needed)
                info = f"Name: {package['name']}\n"
                info += f"Description: {package.get('desc')}\n"
                info += f"Homepage: {package.get('homepage')}\n"
                info += f"License: {package.get('license')}\n"
                info += f"Type: {package['type']}\n"
                info += f"Version: {package.get('stable_version')}\n"
                return info
        return "Package information not found."

    def display_search_results(self, results):
    # Clear current results
        for widget in self.scrollable_result_frame.winfo_children():
            widget.destroy()


        for pkg in results:
            result_frame = ttk.Frame(self.scrollable_result_frame, cursor="hand2")
            result_frame.pack(fill="x", expand=True)
            result_frame.bind("<Button-1>", lambda e, p=pkg['name']: self.display_package_info(p))

            var = tk.BooleanVar()
            chk = tk.Checkbutton(result_frame, variable=var, cursor="cross", command=lambda p=pkg, v=var: self.toggle_package_selection(p['name'], v))
            chk.pack(side="left", anchor="w", padx=2)

            label = tk.Label(result_frame, text=pkg['name'], anchor="w")
            label.pack(side="left", fill="x", expand=True, padx=2)
            # Bind the label to the same function for consistency
            label.bind("<Button-1>", lambda e, p=pkg['name']: self.display_package_info(p))

            # Add a badge for the package type
            badge = tk.Label(result_frame, text=pkg['type'], font=("Arial", 8), anchor="e")
            badge.pack(side="right", padx=2)
            badge.bind("<Button-1>", lambda e, p=pkg['name']: self.display_package_info(p))

    def display_package_info(self, package_name):

        package_info = self.fetch_package_info(package_name)
        self.info_text.config(state="normal")  # Enable text widget to modify its content
        self.info_text.delete("1.0", tk.END)  # Clear current content
        self.info_text.insert(tk.END, package_info)  # Insert new package info
        self.info_text.config(state="disabled")  # Disable text widget to prevent user editing

    def toggle_package_selection(self, package, var):
        if var.get():
            self.selected_packages.add(package)
        else:
            self.selected_packages.remove(package)
        self.update_selected_tab()

    def update_selected_tab(self):
        self.selected_listbox.delete(0, tk.END)
        for package in sorted(self.selected_packages):
            self.selected_listbox.insert(tk.END, package)

