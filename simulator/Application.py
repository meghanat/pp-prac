import Tkinter as tk
import controller
import tkFont
import ttk

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
        ranges = [(1,4), (1,4), (4, 8), (1, 1000), (1, 1000)]

        #self.settings_label=th.Label(self,{})
        self.leftFrame = tk.Frame(self,bg="gainsboro", relief=tk.GROOVE,bd=5)
        self.leftFrame.grid(column=0, row=0, sticky="NS",padx=10,pady=10)
        self.rightFrame = tk.Frame(self, width=500, height=500, bg="white")
        self.rightFrame.grid(column=1, row=0)



        self.label_param = tk.Label(self.leftFrame,padx=self.padx,pady=self.pady,width=15,font=("Helvetica", 16), text="Parameter", bg="gainsboro")
        self.label_param.grid(column=0, row=0, pady=20)
        self.label_value = tk.Label(self.leftFrame,padx=self.padx,pady=self.pady,width=15,font=("Helvetica", 16), text="Value", bg="gainsboro")
        self.label_value.grid(column=1, row=0,pady=20)

        f = tkFont.Font(self.label_param, self.label_param.cget("font"))
        f.configure(underline = True)
        self.label_param.configure(font=f)
        self.label_value.configure(font=f)

        for i,text in enumerate(self.label_texts):
            label = tk.Label(self.leftFrame,self.label_options, text=text)
            label.grid(column=0, row=i+1)
            self.spinBoxes[self.spinbox_names[i]] = tk.Spinbox(self.leftFrame
                        , self.spinbox_options, from_=ranges[i][0], to=ranges[i][1])
            self.spinBoxes[self.spinbox_names[i]].grid(column=1, row=i+1)

        self.leftFrame.columnconfigure(1,pad=10)
        self.leftFrame.columnconfigure(0,pad=10)
        self.simulate_button = tk.Button(self.leftFrame, text="Simulate", command=self.start_simulation)
        self.simulate_button.grid(column=0, row=6, columnspan=2, padx=10, pady=10 )
        self.resizable(False, False)


    def start_simulation(self):
        simulation_values = {}
        for parameter in self.spinbox_names:
            simulation_values[parameter] = int(self.spinBoxes[parameter].get())
        self.controller = controller.Controller(simulation_values)
        self.controller.start_simulation()

    ## Plan : To add a method which periodically updates some label(To be added) with the value of self.controller.lru.get_page_fault_count()
    ## Add labels for each of the algorithms, with the thread updating all the values from the corresponding objects periodically


if __name__ == "__main__":
    sim = Simulator(None)
    sim.title("Simulation of Page Replacement")
    sim.initialize()
    sim.mainloop()
# TODO: controller.start_simulation needs to be run on a seperate thread to avoid blocking the UI
# TODO: add a stop_simulation
# TODO: add widgets for showing page fault counts
# TODO: add a dynamically changing graph for page access? :D : http://www.physics.utoronto.ca/~phy326/python/Live_Plot_Simple.py
