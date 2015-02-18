import Tkinter as tk
import controller
import time
import tkFont
import ttk
import threading

class Simulator(tk.Tk):
    def __init__(self, parent):
        tk.Tk.__init__(self, parent)
        self.parent = parent
        self.controller = None

    def initialize(self):
        self.padx = 10
        self.pady = 5
        self.label_options = {"padx": self.padx, "pady": self.pady
                              ,"width": 15,"bg":"gainsboro"}
        self.spinbox_options = {"width": 10}
        self.spinBoxes = {}
        self.spinbox_names = ["vas", "memory", "page_size", "num_processes", "window"]
        self.label_texts = ["VAS(GB)", "Physical Memory(GB)", "Page Size(KB)"
                           , "Number of procesess", "Simulation Window"]
        self.algo_texts = ["LRU", "LFU", "OPTIMAL", "FIFO"]
        self.algo_values = {"LRU" : {}, "LFU": {}, "FIFO": {}, "OPTIMAL": {}}
        for text in self.algo_texts:
            self.algo_values[text]["label"] = None
            self.algo_values[text]["string_var"] = tk.StringVar()

        ranges = [(2,4), (1,4), (4, 8), (1, 1000), (1, 1000)]

        self.leftFrame = tk.Frame(self, bg="gainsboro", relief=tk.GROOVE, bd=5)
        self.leftFrame.grid(column=0, row=0, sticky="NS",padx=10, pady=10)
        self.rightFrame = tk.Frame(self)
        self.rightFrame.grid(column=1, sticky="NS", row=0, padx=10, pady=10)
        self.rightTopFrame = tk.Frame(self.rightFrame, width=500, height=500)
        self.rightTopFrame.grid(row=0, column=0, sticky="NS")
        self.rightBottomFrame = tk.Frame(self.rightFrame, width=500, height=500)
        self.rightBottomFrame.grid(row=1, column=0, sticky="NS")


        self.label_param = tk.Label(self.leftFrame, self.label_options, font=("Helvetica", 16), text="Parameter")
        self.label_param.grid(column=0, row=0, pady=20)
        self.label_value = tk.Label(self.leftFrame, self.label_options, font=("Helvetica", 16), text="Value")
        self.label_value.grid(column=1, row=0,pady=20)

        self.leftFrame.columnconfigure(1, pad=10)
        self.leftFrame.columnconfigure(0, pad=10)
        self.simulate_button = tk.Button(self.leftFrame, text="Simulate", command=self.start_simulation)
        self.simulate_button.grid(column=0, row=6, columnspan=2, padx=10, pady=10)

        f = tkFont.Font(self.label_param, self.label_param.cget("font"))
        f.configure(underline = True)
        self.label_param.configure(font=f)
        self.label_value.configure(font=f)

        for i,text in enumerate(self.label_texts):
            label = tk.Label(self.leftFrame, self.label_options, text=text)
            label.grid(column=0, row=i+1)
            self.spinBoxes[self.spinbox_names[i]] = tk.Spinbox(self.leftFrame,
                          self.spinbox_options, from_=ranges[i][0], to=ranges[i][1])
            self.spinBoxes[self.spinbox_names[i]].grid(column=1, row=i+1)

        for i,text in enumerate(self.algo_texts):
            label = tk.Label(self.rightTopFrame, self.label_options, text=text)
            label.grid(column=0, row=i)
            self.algo_values[text]["label"] = tk.Label(self.rightTopFrame, self.label_options,
                                              bg="white", textvariable=self.algo_values[text]["string_var"])
            self.algo_values[text]["label"].grid(column=1, row=i)

        self.tabs = ttk.Notebook(self.rightBottomFrame)
        for algo in self.algo_texts:
            frame = ttk.Frame(self.tabs)
            label = tk.Label(frame, text=algo)
            label.grid(row=0, column=0)
            self.tabs.add(frame, text=algo)
        self.tabs.grid(row=1, column=0)
        
        self.resizable(False, False)



    def start_simulation(self):
        simulation_values = {}
        for parameter in self.spinbox_names:
            simulation_values[parameter] = int(self.spinBoxes[parameter].get())
        self.controller = controller.Controller(simulation_values)
        self.controller_thread = threading.Thread(target=self.controller.start_simulation)
        self.controller_thread.start()
        self.update_thread = threading.Thread(target=self.update_labels)
        self.update_thread.start()

    def update_labels(self):
        while True:
            #print "LRU", self.controller.lru.get_page_fault_count()
            #print "LFU", self.controller.lfu.get_page_fault_count()
            #print "OPTIMAL", self.controller.optimal.get_page_fault_count()
            self.algo_values["LRU"]["string_var"].set(str(self.controller.lru.get_page_fault_count()))
            self.algo_values["LFU"]["string_var"].set(str(self.controller.lfu.get_page_fault_count()))
            self.algo_values["OPTIMAL"]["string_var"].set(str(self.controller.optimal.get_page_fault_count()))
            for algo in self.algo_values:
                self.algo_values[algo]["label"].config(bg="white")
            self.algo_values[self.controller.switcher.current_algorithm.name]["label"].config(bg="green")
            


            #self.algo_values["OPTIMAL"]["string_var"].set(str(self.controller.optimal.get_page_fault_count()))
            #self.algo_values["FIFO"]["string_var"].set(str(self.controller.lru.get_page_fault_count()))
            time.sleep(1)
            self.update_idletasks()

if __name__ == "__main__":
    sim = Simulator(None)
    sim.title("Simulation of Page Replacement")
    sim.initialize()
    sim.mainloop()

