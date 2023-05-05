import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
from matplotlib.backend_bases import MouseButton
import pandas as pd
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import Entry
import os
    
class Luna: 
    
    def __init__(self, master):
            self.master = master
            self.master.title("Luna")
            self.master.minsize(width=750, height=700)
            self.master.maxsize(width=1200, height=700)
            
            self.plotted_data = []
            
            self.fig, self.ax = plt.subplots()
            self.ax.clear()
            
            self.canvas = FigureCanvasTkAgg(self.fig, self.master)
            self.canvas.draw()
            self.canvas.get_tk_widget().grid(row=1, column=0, sticky="nsew", columnspan=7)
            
            self.plotted_data_dict = {}
            
            self.y_max_entry = tk.Entry(root, width=9)
            self.y_max_entry.grid(row=7, column=5, sticky="e")
            self.y_min_entry = tk.Entry(root, width=9)
            self.y_min_entry.grid(row=7, column=5, sticky="w")
            self.x_min_entry = tk.Entry(root, width=9)
            self.x_min_entry.grid(row=4, column=5, sticky="w")
            self.x_max_entry = tk.Entry(root, width=9)
            self.x_max_entry.grid(row=4, column=5, sticky="e", columnspan =1)

            self.xanes_button = tk.Button(self.master, text="XANES", command=lambda: self.update_axis_labels("XANES", "Energy (eV)", "Absorption Intensity (Normalized)"))
            self.xanes_button.grid(row=4, column=1)

            self.exafs_button = tk.Button(self.master, text="EXAFS", command=lambda: self.update_axis_labels("EXAFS", "Wavenumber (Å\u207B\u00B9)", "k\u00B3*EXAFS"))
            self.exafs_button.grid(row=6, column=1)

            self.ft_exafs_button = tk.Button(self.master, text="FT-EXAFS", command=lambda: self.update_axis_labels("FT-EXAFS", "Apparent Distance (R', Å)", "Fourier Transform Intensity"))
            self.ft_exafs_button.grid(row=8, column=1)

            self.plotted_data = []
            
            self.x_label_var = tk.StringVar()
            self.y_label_var = tk.StringVar()
                
            self.toolbar_frame = ttk.Frame(master, width=1000, height=100)
            self.toolbar_frame.grid(row=0, column=0, columnspan=4, rowspan=1, sticky="ew")
            self.toolbar = NavigationToolbar2Tk(self.canvas, self.toolbar_frame)
            self.toolbar.pack(side=tk.BOTTOM)
            
            self.canvas.mpl_connect('button_press_event', lambda event: self.zoom(event.xdata, event.ydata))

            self.uploaded_files = {}
            self.menu = tk.Menu(self.master)
            self.master.config(menu=self.menu)
            
            #listbox
                
            self.listbox_frame = ttk.Frame(self.master, width=200)
            self.listbox_frame.grid(row=1, column=10, padx=5, pady=5, sticky='nsew')
            self.listbox_frame.grid_propagate(False)
            self.listbox_frame.columnconfigure(0, weight=1)
            self.listbox_frame.rowconfigure(1, weight=2)
            
            self.listbox_label = ttk.Label(self.listbox_frame, text="Uploaded Files")
            self.listbox_label.grid(row=0, column=0, pady=5)
            
            self.listbox = tk.Listbox(self.listbox_frame, selectmode=tk.MULTIPLE)
            self.listbox.grid(row=1, column=0, sticky='nsew')

            self.listbox_scrollbar = ttk.Scrollbar(self.listbox_frame, orient=tk.VERTICAL, command=self.listbox.yview)
            self.listbox_scrollbar.grid(row=1, column=1, sticky=tk.NS)
            self.listbox.config(yscrollcommand=self.listbox_scrollbar.set)
    

            self.sizegrip = ttk.Sizegrip(self.listbox_frame)
            self.sizegrip.grid(row=1, column=1, sticky=tk.SE)
            
            self.display_uploaded_files()

            self.sizegrip.bind("<B1-Motion>", self.on_resize)
            self.sizegrip.bind("<ButtonPress-1>", self.on_press)
            
    def on_press(self, event):
        # Prevent the event from propagating to the parent widgets
        event.widget.bind("<B1-Motion>", lambda event: self.on_resize(event))
        event.widget.bind("<ButtonRelease-1>", lambda event: event.widget.unbind("<B1-Motion>"))

    def on_resize(self, event):
        # Determine the new width of the listbox based on the mouse position
        new_width = event.x_root - self.listbox_frame.winfo_rootx() - 10
        max_width = self.master.winfo_width() - self.listbox_frame.winfo_x() - 10
        if new_width < 100:
            new_width = 100
        elif new_width > max_width:
            new_width = max_width
        self.listbox_frame.config(width=new_width)
        
    def on_listbox_select(self, event):
        selected_items = self.listbox.curselection()
        print(selected_items)
        
    def display_uploaded_files(self):
        self.listbox.delete(0, tk.END)
        for filename in self.uploaded_files:
            var = tk.BooleanVar(value=self.uploaded_files[filename])
            checkbutton = tk.Checkbutton(self.listbox, text=filename, variable=var)
            self.listbox.insert(tk.END, '')
            self.listbox.window_create(tk.END, window=checkbutton)

    def update_axis_labels(self, plot_type, x_label, y_label):
        if plot_type == "XANES":
            self.x_label_var.set("Energy (eV)")
            self.y_label_var.set("Absorption Intensity (Normalized)")
        elif plot_type == "EXAFS":
            self.x_label_var.set("Wavenumber (Å\u207B\u00B9)")
            self.y_label_var.set("k\u00B3*EXAFS")
        elif plot_type == "FT-EXAFS":
            self.x_label_var.set("Apparent Distance (R', Å)")
            self.y_label_var.set("Fourier Transform Intensity")
        self.ax.set_xlabel(self.x_label_var.get())
        self.ax.set_ylabel(self.y_label_var.get())
        self.canvas.draw()
        self.canvas.draw()

    def plot_data(self, file_path, x_col, y_col):
        delimiters = ['\s+', ',']
        for delim in delimiters:
            try:
                if file_path.endswith('.nor'):
                    df = pd.read_csv(file_path, delimiter='\s+')
                elif file_path.endswith('.xlsx'):
                    df = pd.read_excel(file_path)
                elif file_path.endswith('.txt'):
                    df = pd.read_csv(file_path, delimiter=delim)
                elif file_path.endswith('.chir'):
                    df = pd.read_csv(file_path, delimiter='\s+')
                elif file_path.endswith('.chik'):
                    df = pd.read_csv(file_path, delimiter='\s+')
                else:
                    return

                # Convert column names to lowercase
                df.columns = map(str.lower, df.columns)

                # Convert user input to lowercase
                x_col = x_col.lower()
                y_col = y_col.lower()
            
                print(df)

                filename = os.path.basename(file_path)
                self.plotted_data_dict.setdefault(filename, []).append((df[x_col], df[y_col]))

                self.ax.clear()
                for filename, data_list in self.plotted_data_dict.items():
                    for i, data in enumerate(data_list):
                        x, y = data
                        self.ax.plot(x, y, linewidth=2, label=f"{filename}")

                file_name = os.path.basename(file_path)
                self.listbox.insert(tk.END, file_name)
                self.uploaded_files[file_name] = True
                self.ax.set_xlabel(self.x_label_var.get())
                self.ax.set_ylabel(self.y_label_var.get())
                print("X Label:", self.x_label_var.get())
                print("Y Label:", self.y_label_var.get())
                self.ax.legend()
                self.canvas.draw()
            
                break
            except pd.errors.ParserError:
                pass
            except KeyError:
                messagebox.showerror("Error", "The specified column does not exist in the file.")
            except PermissionError:
                messagebox.showerror("Error", "The file is already in use.")
            except Exception as e:
                messagebox.showerror("Error", str(e))
                
    def apply_y_range(self):
        y_min = float(self.y_min_entry.get())
        y_max = float(self.y_max_entry.get())
        self.ax.set_ylim([y_min, y_max])
        self.canvas.draw()
        
    def apply_x_range(self):
        x_min = float(self.x_min_entry.get())
        x_max = float(self.x_max_entry.get())
        self.ax.set_xlim([x_min, x_max])
        self.canvas.draw()
                
    def reset_plot(self):
        self.plotted_data = []
        self.ax.clear()
        self.canvas.draw()
        self.listbox.delete(0, tk.END)
        self.plotted_data_dict = {}
    
    def browse_file(self):
            file_path = filedialog.askopenfilename(title="Select file", filetypes=[("All Files", "*")])
            file_entry.delete(0, tk.END)
            file_entry.insert(0, file_path)

    def zoom(self, x,y):
        xmin, xmax = self.ax.get_xlim()
        ymin, ymax = self.ax.get_ylim()

        x_span = xmax - xmin
        y_span = ymax - ymin

        x_middle = (xmax + xmin)/2
        y_middle = (ymax + ymin)/2

        zoom_fraction = 0.5

        self.ax.set_xlim([x_middle - zoom_fraction * x_span, x_middle + zoom_fraction * x_span])
        self.ax.set_ylim([y_middle - zoom_fraction * y_span, y_middle + zoom_fraction * y_span])
        self.canvas.draw_idle()
            
root = tk.Tk()
root.title("Luna")

luna = Luna(root)

x_min_label = tk.Label(root, text="   X min")
x_min_label.grid(row=3, column=5, sticky="w")

x_max_label = tk.Label(root, text="X max   ")
x_max_label.grid(row=3, column=5, sticky="e")

y_min_label = tk.Label(root, text="   Y min")
y_min_label.grid(row=6, column=5, sticky="w")

y_max_label = tk.Label(root, text="Y max   ")
y_max_label.grid(row=6, column=5, sticky="e")

x_apply_button = tk.Button(root, text="Apply X Range", command=luna.apply_x_range)
x_apply_button.grid(row=5, column=5)

y_apply_button = tk.Button(root, text="Apply Y Range", command=luna.apply_y_range)
y_apply_button.grid(row=8, column=5)

file_frame = tk.Frame(root)
file_frame.grid(row=3, column=3)

file_label = tk.Label(file_frame, text="File:")
file_label.grid(row=2, column=1)

file_entry = tk.Entry(file_frame)
file_entry.grid(row=2, column=3)

file_button = tk.Button(file_frame, text="Browse", command=luna.browse_file)
file_button.grid(row=2, column=4)

x_col_label = tk.Label(root, text="X axis:")
x_col_label.grid(row=4, column=3)

x_col_entry = tk.Entry(root)
x_col_entry.grid(row=5, column=3)

y_col_label = tk.Label(root, text="Y axis:")
y_col_label.grid(row=6, column=3)

y_col_entry = tk.Entry(root)
y_col_entry.grid(row=7, column=3)

empty_label = tk.Label(root)
empty_label.grid(row=11, column=0)

empty_label = tk.Label(root)
empty_label.grid(row=0, column=1)

root.rowconfigure(11, weight=1)

empty_label = tk.Label(root)
empty_label.grid(row=2, column=0)

root.rowconfigure(2, weight=1)

plot_button = tk.Button(root, text="Plot", command=lambda: luna.plot_data(file_entry.get(), x_col_entry.get(), y_col_entry.get()))
plot_button.grid(row=8, column=3)

root.bind('<Return>', lambda event: luna.plot_data(file_entry.get(), x_col_entry.get(), y_col_entry.get()))

reset_button = tk.Button(root, text="Reset graph", command=lambda: luna.reset_plot())
reset_button.grid(row=0, column=4)

root.mainloop()
