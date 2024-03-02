import tkinter as tk
from tkinter import ttk
from brew import fetch_casks_from_brew

class SetupApp:
    def __init__(self, root):
        self.root = root
        self.root.title("install.sh")
        self.root.geometry("600x400")

        self.search_var = tk.StringVar()  # Variable to track search entry text
        self.debounce_job = None  # To store the debounce job reference

        self.show_welcome_screen()

    def show_welcome_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root, text="Welcome to the macOS Setup GUI", font=("Arial", 14)).pack(pady=20)
        tk.Button(self.root, text="Continue", command=self.build_cask_search_interface).pack()

    def build_cask_search_interface(self):
        self.clear_widgets()

        search_entry = tk.Entry(self.root, textvariable=self.search_var)
        search_entry.pack(pady=(5, 10))
        self.search_var.trace_add("write", lambda name, index, mode: self.debounce_search())

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill="both")

        self.all_casks_frame = ttk.Frame(self.notebook)
        self.selected_casks_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.all_casks_frame, text='All')
        self.notebook.add(self.selected_casks_frame, text='Selected')

        self.all_casks_listbox = tk.Listbox(self.all_casks_frame, selectmode=tk.MULTIPLE)
        self.all_casks_listbox.pack(expand=True, fill="both")

        self.notebook.bind("<<NotebookTabChanged>>", self.tab_changed)

        self.dynamic_brew_search()  # Initial display

    def clear_widgets(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def debounce_search(self):
        if self.debounce_job is not None:
            self.root.after_cancel(self.debounce_job)
        self.debounce_job = self.root.after(300, self.dynamic_brew_search)

    def dynamic_brew_search(self):
        typed = self.search_var.get().strip()
        if typed:
            self.root.config(cursor="wait")
            casks = fetch_casks_from_brew(typed)
            self.root.config(cursor="")
        else:
            casks = []
        self.populate_listbox(self.all_casks_listbox, casks)

    def populate_listbox(self, listbox, casks):
        listbox.delete(0, tk.END)
        for cask in casks:
            listbox.insert(tk.END, cask)

    def tab_changed(self, event=None):
        selected_tab = event.widget.select()
        tab_text = event.widget.tab(selected_tab, "text")
        if tab_text == "Selected":
            self.update_selected_tab()

    def update_selected_tab(self):
        # Clear the "Selected" frame
        for widget in self.selected_casks_frame.winfo_children():
            widget.destroy()

        # Get selected items from the "All" listbox
        selected_indices = self.all_casks_listbox.curselection()
        selected_casks = [self.all_casks_listbox.get(i) for i in selected_indices]

        # Display selected items in the "Selected" frame
        for cask in selected_casks:
            tk.Label(self.selected_casks_frame, text=cask).pack()



if __name__ == "__main__":
    root = tk.Tk()
    app = SetupApp(root)
    root.mainloop()
