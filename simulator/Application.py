import controller
import tkFileDialog
import tkFont
import Tkinter as tk
import ttk
import threading
import time


class Simulator(tk.Tk):
    def __init__(self, parent):
        tk.Tk.__init__(self, parent)
        self.parent = parent
        self.controller = None

    def initialize(self):
        self.padx = 10
        self.pady = 5
        self.label_options = {"padx": self.padx, "pady": self.pady,
                              "width": 15, "bg": "gainsboro"}
        self.frame_options = {"width": 500, "height": 500,
                              "padx": 10, "pady": 10}
        self.spinbox_options = {"width": 10}
        self.spinBoxes = {}
        self.spinbox_names = ["vas", "frames", "num_processes", "window"]
        self.label_texts = ["VAS(GB)", "Number of frames", "Number of procesess", "Simulation Window"]
        self.algo_texts = ["LRU", "LFU", "OPTIMAL", "FIFO"]
        self.algo_values = {"LRU": {}, "LFU": {}, "OPTIMAL": {}, "FIFO": {}}
        for text in self.algo_texts:
            self.algo_values[text]["label"] = None
            self.algo_values[text]["string_var"] = tk.StringVar()

        self.ranges = [(2, 4), (1, 4), (4, 8), (1, 1000), (1, 1000)]

        self.leftFrame = tk.Frame(self, bg="gainsboro", relief=tk.GROOVE, bd=5)
        self.leftFrame.grid(column=0, row=0, sticky="EWNS", padx=10, pady=10)
        self.rightFrame = tk.Frame(self)
        self.rightFrame.grid(column=1, sticky="", row=0, padx=10, pady=10)
        self.rightTopFrame = tk.Frame(self.rightFrame, self.frame_options)
        self.rightTopFrame.grid(row=0, column=0)
        self.rightBottomFrame = tk.Frame(self.rightFrame, self.frame_options)
        self.rightBottomFrame.grid(row=1, column=0)

        self.label_param = tk.Label(self.leftFrame, self.label_options,
                                    font=("Helvetica", 16), text="Parameter")
        self.label_param.grid(column=0, row=0, pady=20)
        self.label_value = tk.Label(self.leftFrame, self.label_options,
                                    font=("Helvetica", 16), text="Value")
        self.label_value.grid(column=1, row=0, pady=20)

        self.leftFrame.columnconfigure(1, pad=10)
        self.leftFrame.columnconfigure(0, pad=10)
        self.simulate_button = tk.Button(self.leftFrame, text="Simulate", command=self.start_simulation)
        self.simulate_button.grid(column=0, row=5, columnspan=2, padx=10, pady=10)

        f = tkFont.Font(self.label_param, self.label_param.cget("font"))
        f.configure(underline=True)
        self.label_param.configure(font=f)
        self.label_value.configure(font=f)

        self.create_input_labels()
        self.create_page_count_labels()
        self.create_log_frames()
        self.create_menu_bar()
        self.enable_uniform_resize()

    def create_input_labels(self):
        for i, text in enumerate(self.label_texts):
            label = tk.Label(self.leftFrame, self.label_options, text=text)
            label.grid(column=0, row=i+1)
            self.spinBoxes[self.spinbox_names[i]] = tk.Spinbox(self.leftFrame,
                           self.spinbox_options, from_=self.ranges[i][0], to=self.ranges[i][1])
            self.spinBoxes[self.spinbox_names[i]].grid(column=1, row=i+1)

    def create_log_frames(self):
        self.tabs = ttk.Notebook(self.rightBottomFrame)
        for algo in self.algo_texts:
            frame = ttk.Frame(self.tabs)
            scrollbar = tk.Scrollbar(frame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            textArea = tk.Text(frame, yscrollcommand=scrollbar.set)
            textArea.configure(state=tk.DISABLED)
            textArea.pack(side=tk.LEFT, fill=tk.BOTH)
            scrollbar.config(command=textArea.yview)
            self.algo_values[algo]["log"] = textArea
            self.tabs.add(frame, text=algo)
            self.tabs.grid(row=1, column=0)

    def create_menu_bar(self):
        menubar = tk.Menu(self)
        filemenu = tk.Menu(self, tearoff=0)
        filemenu.add_command(label="Load Access Stream From")
        filemenu.add_command(label="Save Logs As", command=self.save_logs)
        filemenu.add_command(label="Save Access Stream As")
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label="File", menu=filemenu)

        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About")
        menubar.add_cascade(label="Help", menu=helpmenu)

        self.config(menu=menubar)

    def create_page_count_labels(self):
        for i, text in enumerate(self.algo_texts):
            label = tk.Label(self.rightTopFrame, self.label_options, text=text)
            label.grid(column=0, row=i)
            self.algo_values[text]["label"] = tk.Label(self.rightTopFrame,
                                                       self.label_options,
                                                       bg="white",
                                                       textvariable=self.algo_values[text]["string_var"])
            self.algo_values[text]["label"].grid(column=1, row=i)

    def enable_uniform_resize(self):
        self.grid_columnconfigure(0,weight=1)
        self.grid_columnconfigure(1,weight=1)
        self.grid_rowconfigure(0,weight=1)
        self.leftFrame.columnconfigure(0,weight=1)
        self.leftFrame.columnconfigure(1,weight=1)
        self.leftFrame.rowconfigure(0,weight=1)
        self.leftFrame.rowconfigure(1,weight=1)
        self.leftFrame.rowconfigure(2,weight=1)
        self.leftFrame.rowconfigure(3,weight=1)
        self.leftFrame.rowconfigure(4,weight=1)
        self.leftFrame.rowconfigure(5,weight=1)
        self.rightFrame.rowconfigure(0, weight=1)
        self.rightFrame.rowconfigure(1, weight=1)
        self.rightFrame.columnconfigure(0, weight=1)

    def save_logs(self):
        file_name = tkFileDialog.asksaveasfilename()        
        file_handle = open(file_name, "w")
        for algo in self.algo_texts:
            file_handle.write("-" * 100)
            file_handle.write("\n")
            file_handle.write(algo + "\n")
            file_handle.write("-" * 100)
            file_handle.write("\n")
            file_handle.write(self.algo_values[algo]["log"].get("1.0", tk.END))
        file_handle.close()


    def start_simulation(self):
        simulation_values = {}
        for parameter in self.spinbox_names:
            simulation_values[parameter] = int(self.spinBoxes[parameter].get())
        self.controller = controller.Controller(simulation_values)
        self.update_algo_values()
        self.controller_thread = threading.Thread(target=self.controller.start_simulation)
        self.controller_thread.start()
        self.update_thread = threading.Thread(target=self.update_labels)
        self.update_thread.start()
        self.update_log_thread = threading.Thread(target=self.update_logs)
        self.update_log_thread.start()

    def update_algo_values(self):
        self.algo_values["LRU"]["algo"] = self.controller.lru
        self.algo_values["LFU"]["algo"] = self.controller.lfu
        self.algo_values["OPTIMAL"]["algo"] = self.controller.optimal
        self.algo_values["FIFO"]["algo"] = self.controller.fifo
    
    def update_labels(self):
        while True:
            self.algo_values["LRU"]["string_var"].set(str(self.controller.lru.get_page_fault_count()))
            self.algo_values["LFU"]["string_var"].set(str(self.controller.lfu.get_page_fault_count()))
            self.algo_values["OPTIMAL"]["string_var"].set(str(self.controller.optimal.get_page_fault_count()))
            self.algo_values["FIFO"]["string_var"].set(str(self.controller.fifo.get_page_fault_count()))
            for algo in self.algo_values:
                self.algo_values[algo]["label"].config(bg="white")
            self.algo_values[self.controller.switcher.current_algorithm.name]["label"].config(bg="green")
            time.sleep(1)
            self.update_idletasks()

    def update_logs(self):
        while True:
            for algo in self.algo_texts:
                self.algo_values[algo]["log"].configure(state=tk.NORMAL)
                self.algo_values[algo]["log"].insert(tk.END, str(self.algo_values[algo]["algo"].get_next_log()))
                self.algo_values[algo]["log"].configure(state=tk.DISABLED)
            self.update_idletasks()

if __name__ == "__main__":
    sim = Simulator(None)
    sim.title("Simulation of Page Replacement")
    sim.initialize()
    sim.mainloop()
