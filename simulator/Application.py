import Tkinter as tk
import controller


class Simulator(tk.Tk):
    def __init__(self, parent):
        tk.Tk.__init__(self, parent)
        self.parent = parent

    def initialize(self):
        self.padx = 10
        self.pady = 5
        self.label_options = {"padx": self.padx, "pady": self.pady
                              , "relief": tk.SUNKEN, "width": 20}
        self.spinbox_options = {"width": 20}
        self.spinBoxes = {}
        self.spinbox_names = ["vas", "memory", "page_size", "num_processes", "window"]
        self.label_texts = ["VAS(GB)", "Physical Memory(GB)", "Page Size(KB)"
                           , "Number of procesess", "Simulation Window"]
        ranges = [(1,4), (1,4), (4, 8), (1, 1000), (1, 1000)]

        self.leftFrame = tk.Frame(self)
        self.leftFrame.grid(column=0, row=0, sticky="NS")
        self.rightFrame = tk.Frame(self, width=500, height=500, bg="white")
        self.rightFrame.grid(column=1, row=0)

        self.label_param = tk.Label(self.leftFrame,self.label_options, text="Parameter", bg="gray")
        self.label_param.grid(column=0, row=0)
        self.label_value = tk.Label(self.leftFrame, self.label_options, text="Value", bg="gray")
        self.label_value.grid(column=1, row=0)

        for i,text in enumerate(self.label_texts):
            label = tk.Label(self.leftFrame,self.label_options, text=text)
            label.grid(column=0, row=i+1)
            self.spinBoxes[self.spinbox_names[i]] = tk.Spinbox(self.leftFrame
                        , self.spinbox_options, from_=ranges[i][0], to=ranges[i][1])
            self.spinBoxes[self.spinbox_names[i]].grid(column=1, row=i+1)

        self.simulate_button = tk.Button(self.leftFrame, text="Simulate", command=self.start_simulation)
        self.simulate_button.grid(column=0, row=6, columnspan=2, padx=10, pady=10 )
        self.resizable(False, False)

    def start_simulation(self):
        simulation_values = {}
        for parameter in self.spinbox_names:
            simulation_values[parameter] = int(self.spinBoxes[parameter].get())
        controller.start_simulation(simulation_values)

if __name__ == "__main__":
    sim = Simulator(None)
    sim.title("Simulation of Page Replacement")
    sim.initialize()
    sim.mainloop()
# TODO: controller.start_simulation needs to be run on a seperate thread to avoid blocking the UI
# TODO: add a stop_simulation
# TODO: add widgets for showing page fault counts
# TODO: add a dynamically changing graph for page access? :D : http://www.physics.utoronto.ca/~phy326/python/Live_Plot_Simple.py
