import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
    
class Luna: 
    
    def __init__(self, master):
            self.master = master
            self.master.title("Luna")
            self.plotted_data = []
            self.fig, self.ax = plt.subplots()
            self.ax.clear()
            self.canvas = FigureCanvasTkAgg(self.fig, self.master)
            self.canvas.draw()
            self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)


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

                self.plotted_data.append((df[x_col], df[y_col]))

                self.ax.clear()
                for i, data in enumerate(self.plotted_data):
                    x, y = data
                    self.ax.plot(x, y, label=f"Data set {i + 1}")

                self.ax.set_xlabel(x_col)
                self.ax.set_ylabel(y_col)
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

                
    def reset_plot(self):
        self.plotted_data = []
        self.ax.clear()
        self.canvas.draw()
    
    def browse_file(self):
            file_path = filedialog.askopenfilename(title="Select file", filetypes=[("All Files", "*")])
            file_entry.delete(0, tk.END)
            file_entry.insert(0, file_path)

root = tk.Tk()
root.title("Luna")

luna = Luna(root)

file_frame = tk.Frame(root)
file_frame.pack()

file_label = tk.Label(file_frame, text="File:")
file_label.pack(side="left")

file_entry = tk.Entry(file_frame)
file_entry.pack(side="left")

file_button = tk.Button(file_frame, text="Browse", command=luna.browse_file)
file_button.pack(side="left")

x_col_label = tk.Label(root, text="X Column:")
x_col_label.pack()

x_col_entry = tk.Entry(root)
x_col_entry.pack()

y_col_label = tk.Label(root, text="Y Column:")
y_col_label.pack()

y_col_entry = tk.Entry(root)
y_col_entry.pack()

plot_button = tk.Button(root, text="Plot", command=lambda: luna.plot_data(file_entry.get(), x_col_entry.get(), y_col_entry.get()))
plot_button.pack()

root.bind('<Return>', lambda event: luna.plot_data(file_entry.get(), x_col_entry.get(), y_col_entry.get()))

reset_button = tk.Button(root, text="Reset graph", command=lambda: luna.reset_plot())
reset_button.pack(side="right", padx=10)

root.mainloop()
