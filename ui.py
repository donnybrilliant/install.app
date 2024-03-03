import tkinter as tk
from tkinter import ttk
from fetch import fetch_homebrew_data
from search import search_packages


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

        tk.Label(self.root, text="Welcome to the macOS Setup GUI", font=("Arial", 14)).pack(pady=20)
        tk.Button(self.root, text="Continue", command=self.setup_search).pack()



    def setup_search(self):
        self.clear_widgets()
   
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)
        self.setup_all_tab()
        self.setup_selected_tab()
        

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
        self.result_canvas.create_window((0, 0), window=self.scrollable_result_frame, anchor="nw")

        self.result_canvas.pack(side="left", fill="both", expand=True)
        self.result_scrollbar.pack(side="right", fill="y")

        self.result_frame.bind("<Configure>", lambda e: self.result_canvas.configure(scrollregion=self.result_canvas.bbox("all")))

        # Right side for info display, taking up the remaining space
        self.info_text = tk.Text(self.all_tab, state="disabled", wrap="word")
        self.info_text.pack(side="left", fill="both", expand=True)

        # Adjust the packing of the result frame and info text to control their widths
        self.result_frame.pack_configure(fill="y", expand=False)
        self.info_text.pack_configure(fill="both", expand=True)


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

            var = tk.BooleanVar()
            chk = tk.Checkbutton(result_frame, variable=var, cursor="cross", command=lambda p=pkg, v=var: self.toggle_package_selection(p['name'], v))
            chk.pack(side="left")

            label = tk.Label(result_frame, text=pkg['name'])
            label.pack(side="left")  # Make the label fill the rest of the line
            label.bind("<Button-1>", lambda e, p=pkg['name']: self.display_package_info(p))

            # Make the whole frame clickable
            result_frame.bind("<Button-1>", lambda e, p=pkg['name']: self.display_package_info(p))



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

