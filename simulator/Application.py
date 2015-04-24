#!/usr/bin/python
# -*- coding: utf-8 -*-
import controller
import tkFileDialog
import tkFont
import tkMessageBox
import Tkinter as tk
import ttk
import threading
import time



class Simulator(tk.Tk):

    def __init__(self, parent):
        
        tk.Tk.__init__(self, parent)
        self.parent = parent
        self.controller = None
        self.read_from_file = False
        self.page_accesses = None

    def initialize(self):
        
        self.padx=10
        self.pady=10
        self.param_options = {
            'bg': 'gainsboro',
            "padx": 5

            }
        self.value_options = {
            'width' : 7,

            }
        self.heading_options={
            'bg': 'gainsboro'
        }
        self.leftFrame_options={

            "padx" :10,
            "pady":10
        }
        self.label_options={
            "bg" :"gainsboro",
            "width" :20,
            "padx" :5,
            "pady" : 7,

        }
        self.count_options={
            "width" : 30,
            "bg":"gainsboro",
            "pady" : 7
        }
        self.spinBoxes = {}
        self.spinbox_names = [
                            'vas',
                            'number_frames',
                            'number_processes'
                              ]
        self.label_texts = [
                            'Virtual Address Space\n(in GB)',
                            'Number of frames',
                            'Number of procesess'
                            ]
        self.algo_texts = [
            'LRU',
            'LFU',
            'OPTIMAL',
            'FIFO',
            'RANDOM',
            'CLOCK',
            ]
        self.algo_values = {
            'LRU': {},
            'LFU': {},
            'OPTIMAL': {},
            'FIFO': {},
            'RANDOM': {},
            'CLOCK': {},
            }
        for text in self.algo_texts:
            self.algo_values[text]['label'] = None
            self.algo_values[text]['string_var'] = tk.StringVar()

        self.ranges = [(2, 4), (1, 4), (4, 8), (1, 1000), (1, 1000)]

        self.leftFrame = tk.Frame(self,self.leftFrame_options, bg='gainsboro',
                                  relief=tk.GROOVE, bd=5,padx=15)
        self.leftFrame.grid(column=0, row=0, sticky='NSWE')

        self.rightFrame = tk.Frame(self)
        self.rightFrame.grid(column=1, sticky='NSWE', row=0)
        self.rightFrame.columnconfigure(1,pad=10)
        self.rightFrame.columnconfigure(0,pad=10)

        
        self.rightTopFrame=tk.Frame(self.rightFrame,relief=tk.FLAT,bd=5)
        self.rightTopFrame.grid(row=0, column=0,sticky='EW')
        self.rightTopLeftFrame = tk.Frame(self.rightTopFrame,relief=tk.RIDGE,bd=5)
        self.rightTopLeftFrame.grid(row=0, column=0,sticky='NSEW')
        self.rightTopFrame.grid_columnconfigure(1, weight=1,pad=20)
        self.rightTopRightFrame = tk.Frame(self.rightTopFrame,relief=tk.RIDGE,bd=5)
        self.rightTopRightFrame.grid(row=0, column=1,sticky='NSEW')

        self.canvas = tk.Canvas(self.rightTopRightFrame, width=400,height=220)
        self.canvas.grid(row=0,column=0,sticky="NSEW",padx=75)
        

        self.rightBottomFrame = tk.Frame(self.rightFrame)
        self.rightBottomFrame.grid(row=1, column=0)

        self.label_param = tk.Label(self.leftFrame, self.heading_options,
                                    font=('Helvetica', 20),
                                    text='Parameter')
        self.label_param.grid(column=0, row=0)

        self.label_value = tk.Label(self.leftFrame, self.heading_options,
                                    font=('Helvetica', 20), text='Value'
                                    )
        self.label_value.grid(column=1, row=0)

        self.leftFrame.columnconfigure(1)
        self.leftFrame.columnconfigure(0)

        self.simulate_button = tk.Button(self.leftFrame, text='Simulate'
                , command=self.verifyParams)
        self.simulate_button.grid(column=0, row=5, columnspan=2)

        self.stop_button = tk.Button(self.leftFrame, text=' Stop',
                command=self.stop_simulation, state=tk.DISABLED)
        self.stop_button.grid(column=0, row=7, columnspan=2)

        self.progress_bar = ttk.Progressbar(self.leftFrame,
                orient='horizontal', length=60, mode='determinate')


        f = tkFont.Font(self.label_param, self.label_param.cget('font'))
        f.configure(underline=True)

        self.label_param.configure(font=f)
        self.label_value.configure(font=f)

        self.create_input_labels()
        self.create_page_count_labels()
        self.create_log_frames()
        self.create_menu_bar()

        self.graph_data={}

        self.enable_uniform_resize()

    def create_input_labels(self):
        
        for (i, text) in enumerate(self.label_texts):
            label = tk.Label(self.leftFrame, self.param_options,font=('Helvetica', 16),
                             text=text)
            label.grid(column=0, row=i + 1)

            self.spinBoxes[self.spinbox_names[i]] = \
                tk.Spinbox(self.leftFrame,self.value_options,
                           from_=self.ranges[i][0],
                           to=self.ranges[i][1])
            self.spinBoxes[self.spinbox_names[i]].grid(column=1, row=i
                    + 1)

        self.switcher_label = tk.Label(self.leftFrame,
                self.param_options,font=('Helvetica', 16), text='Switching Window')
        self.switcher_label.grid(column=0, row=len(self.label_texts)
                                 + 1)

        self.switcher_slider = tk.Scale(self.leftFrame, from_=0,
                to=10000, orient=tk.HORIZONTAL)
        self.switcher_slider.set(1000)
        self.switcher_slider.grid(column=1, row=len(self.label_texts)
                                  + 1,)

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
            self.algo_values[algo]['log'] = textArea
            self.tabs.add(frame, text=algo)
            self.tabs.grid(row=1, column=0)

    def create_menu_bar(self):
        
        menubar = tk.Menu(self)
        filemenu = tk.Menu(self, tearoff=0)
        filemenu.add_command(label='Load Access Stream From',
                             command=self.load_accesses)
        filemenu.add_command(label='Save Logs As',
                             command=self.save_logs)
        filemenu.add_command(label='Save Access Stream As',
                             command=self.save_accesses)
        filemenu.add_separator()
        filemenu.add_command(label='Exit', command=self.quit)
        menubar.add_cascade(label='File', menu=filemenu)

        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label='About')
        menubar.add_cascade(label='Help', menu=helpmenu)
        self.config(menu=menubar)

    def create_page_count_labels(self):
        
        self.total_count = tk.StringVar()
        self.total_count_label = tk.Label(self.rightTopLeftFrame,
                self.label_options, text='TOTAL')
        self.total_count_label.grid(column=0, row=0)

        self.total_count_box = tk.Label(self.rightTopLeftFrame,
                self.count_options, bg='white',
                textvariable=self.total_count)
        self.total_count_box.grid(column=1, row=0)

        for (i, text) in enumerate(self.algo_texts):
            label = tk.Label(self.rightTopLeftFrame, self.label_options,
                             text=text)
            label.grid(column=0, row=i + 1)
            self.algo_values[text]['label'] = \
                tk.Label(self.rightTopLeftFrame, self.count_options,
                         bg='white',
                         textvariable=self.algo_values[text]['string_var'
                         ])
            self.algo_values[text]['label'].grid(column=1, row=i + 1)

    def enable_uniform_resize(self):
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.leftFrame.columnconfigure(0, weight=1)
        self.leftFrame.columnconfigure(1, weight=1)
        self.leftFrame.rowconfigure(0, weight=1)
        self.leftFrame.rowconfigure(1, weight=1)
        self.leftFrame.rowconfigure(2, weight=1)
        self.leftFrame.rowconfigure(3, weight=1)
        self.leftFrame.rowconfigure(4, weight=1)
        self.leftFrame.rowconfigure(5, weight=1)
        self.rightFrame.rowconfigure(0, weight=1)
        self.rightFrame.rowconfigure(1, weight=1)
        self.rightFrame.columnconfigure(0, weight=1)
        self.rightFrame.columnconfigure(1, weight=1)

    def graph_points(self,width=500,height=200):

        data=list(self.graph_data.values())
        keys=list(self.graph_data.keys())
        max_val=max(data)
        for i in range(len(data)):
            data[i]=data[i]*1.0/(max_val*1.0 +1.0)  * 180.0        
        
        self.canvas.delete("all")
        x_stretch = 10
        x_width = 25
        x_gap = 20
        for x, y in enumerate(data):
            x0 = x * x_stretch +  x*x_width +x*x_gap + 30
            y0 = height - (y)
            x1 = x0 + x_width
            y1 = height
            #print ("xo :",x0,"y0 :",y0,"y :",y)   
            self.canvas.create_rectangle(x0, y0, x1, y1, fill="indian red")
            self.canvas.create_text(x0+12, y0, anchor=tk.S, text=str(keys[x]))

        self.canvas.create_line(5,height,width,height+2,width=4);
        self.canvas.create_line(5,height-180,5,height+2,width=4)

            

    def save_logs(self):
        
        file_name = tkFileDialog.asksaveasfilename()
        file_handle = open(file_name, 'w')
        for algo in self.algo_texts:
            file_handle.write('-' * 100)
            file_handle.write('\n')
            file_handle.write(algo + '\n')
            file_handle.write('-' * 100)
            file_handle.write('\n')
            file_handle.write(self.algo_values[algo]['log'].get('1.0',
                              tk.END))
        file_handle.close()

    def load_accesses(self):
        
        try:
            #print 'in load_accesses'
            file_handle = tkFileDialog.askopenfile()
            self.read_from_file = True

            logs = file_handle.read().strip()
            logs = logs.split('=')[0].strip()  # get only accesses, trim whitespaces

            logs = logs.split('\n')
            self.page_accesses = list()

            for i in logs:
                i = i.strip().split(',')
                self.page_accesses.append([i[1], int(i[0], 16) >> 12])

            self.spinBoxes['number_processes'].config(state=tk.DISABLED)

        except:
            #print 'Fail'
            self.read_from_file = False
            self.spinBoxes['number_processes'].config(state=tk.NORMAL)

    def save_accesses(self):

        pass

    def verifyParams(self):

        # check VAS
        try:
            vas = float(self.spinBoxes['vas'].get())
            if vas < 1:
                tkMessageBox.showerror('Error',
                        'Virtual Address Space must be greater than 1 GB!'
                        )
                return
        except ValueError:
            tkMessageBox.showerror('Error',
                                   'Virtual Address Space must be a number!'
                                   )
            return

        # check Number of frames
        try:
            number_frames = int(self.spinBoxes['number_frames'].get())
            if number_frames < 1:
                tkMessageBox.showerror('Error',
                        'Number of frames must be greater than 0')
                return
        except ValueError:
            tkMessageBox.showerror('Error',
                                   "Input 'Number of frames' must be a positive integer!"
                                   )
            return

        # check NUmber of processes
        try:
            number_processes = int(self.spinBoxes['number_processes'
                                   ].get())
            if number_processes < 1:
                tkMessageBox.showerror('Error',
                        'Number of processes must be greater than 0')
                return
        except ValueError:
            tkMessageBox.showerror('Error',
                                   "Input 'Number of processes' must be a positive integer!"
                                   )
            return
        self.start_simulation()

    def start_simulation(self):

        # clear logs
        for algo in self.algo_texts:
            self.algo_values[algo]['log'].configure(state=tk.NORMAL)
            self.algo_values[algo]['log'].delete(1.0, tk.END)
            self.algo_values[algo]['log'].configure(state=tk.DISABLED)

        self.simulation_values = {}

        self.stop_button.configure(state=tk.NORMAL)
        for parameter in self.spinbox_names:
            try:
                self.simulation_values[parameter] = \
                    int(self.spinBoxes[parameter].get())
            except:
                tkMessageBox.showerror('Error', 'Invalid Input : '
                        + parameter)
                return
        self.simulation_values['window'] = \
            int(self.switcher_slider.get())
        self.simulation_values['read_from_file'] = self.read_from_file
        self.simulation_values['page_accesses'] = self.page_accesses
        self.simulation_values['simulating'] = True
        self.simulation_values['progress_bar'] = self.progress_bar
        
        self.controller = controller.Controller(self.simulation_values)
        
        self.update_algo_values()
        
        self.start_time=time.time()
        self.controller_thread = \
            threading.Thread(target=self.controller.start_simulation)
        self.controller_thread.start()
        self.update_thread = threading.Thread(target=self.update_labels)
        self.update_thread.start()
        self.update_log_thread = \
            threading.Thread(target=self.update_logs)
        self.update_log_thread.start()

    def stop_simulation(self):

        self.simulation_values['simulating'] = False

        self.stop_time=time.time()
        self.report = tk.Toplevel()
        self.report.geometry("%dx%d%+d%+d" % (555, 400, 350, 70))
        self.report.title("Simulation Summary")

        self.reportFrame = tk.Frame(self.report, bg='gainsboro',
                                  relief=tk.GROOVE, bd=5)
        self.reportFrame.grid(column=0, row=0, sticky='NS', padx=25,
                            pady=70)

        self.reportFrame.columnconfigure(1, pad=5)
        self.reportFrame.columnconfigure(0, pad=5)

        self.report_label_options = {
            'padx': 0,
            'pady': 10,
            'width': 30,
            'bg': 'gainsboro',

            }

        self.heading=tk.Label(self.reportFrame,self.heading_options,font=('Helvetica', 20),text="Summary")
        self.heading.grid(row=0,column=0,columnspan=2)
        #Total number of page faults
        self.report_faults_label = tk.Label(self.reportFrame,self.report_label_options,
                                    text='Total Number of Page Faults:')
        self.report_faults_label.grid(row=1, column=0)
        self.report_faults_value=tk.Label(self.reportFrame,self.report_label_options,
                                    text=self.controller.switcher.get_total_count())
        self.report_faults_value.grid(row=1, column=1)

        #Simulation duration
        self.report_time_label = tk.Label(self.reportFrame,self.report_label_options,
                                    text='Simulation Duration:')
        self.report_time_label.grid(row=2, column=0)
        self.report_time_value=tk.Label(self.reportFrame,self.report_label_options,
                                    text=self.stop_time - self.start_time)
        self.report_time_value.grid(row=2, column=1)

        #Switching window size
        self.report_size_windows_label = tk.Label(self.reportFrame,self.report_label_options,
                                    text='Size of Switching Window:')
        self.report_size_windows_label.grid(row=3, column=0)
        self.report_size_windows_value = tk.Label(self.reportFrame,self.report_label_options,
                                    text=self.simulation_values["window"])
        self.report_size_windows_value.grid(row=3, column=1)

        #Number of Switching windows
        self.report_num_windows_label = tk.Label(self.reportFrame,self.report_label_options,
                                    text='Number of Switching Windows:')
        self.report_num_windows_label.grid(row=4, column=0)
        self.report_size_windows_value = tk.Label(self.reportFrame,self.report_label_options,
                                    text=self.controller.switcher.get_total_windows())
        self.report_size_windows_value.grid(row=4, column=1)

        #Number of page accesses performed
        self.report_accesses_label = tk.Label(self.reportFrame,self.report_label_options,
                                    text='Number of Page Accesses:')
        self.report_accesses_label.grid(row=5,column=0)
        self.report_accesses_values = tk.Label(self.reportFrame,self.report_label_options,
                                    text=self.controller.optimal.pages_accessed )
        self.report_accesses_values.grid(row=5,column=1)


        #Best Performing algorithm
        self.report_best_label = tk.Label(self.reportFrame,self.report_label_options,
                                    text='Best Performing Algorithm:')
        self.report_best_label.grid(row=6,column=0)
        self.report_best_label = tk.Label(self.reportFrame,self.report_label_options,
                                    text=self.controller.switcher.get_best_performing_algorithm())
        self.report_best_label.grid(row=6,column=1)

        

    def update_algo_values(self):

        self.algo_values['LRU']['algo'] = self.controller.lru
        self.algo_values['LFU']['algo'] = self.controller.lfu
        self.algo_values['OPTIMAL']['algo'] = self.controller.optimal
        self.algo_values['FIFO']['algo'] = self.controller.fifo
        self.algo_values['RANDOM']['algo'] = self.controller.random
        self.algo_values['CLOCK']['algo'] = self.controller.clock

    def update_labels(self):

        self.graph_data={}

        while self.simulation_values['simulating']:
            self.total_count.set(self.controller.switcher.get_total_count())

            for algo in self.algo_values:
                count=self.algo_values[algo]['algo'].get_page_fault_count()
                self.graph_data[self.algo_values[algo]['algo'].name]=count
                self.algo_values[algo]['string_var'
                        ].set(str(count))
            #print(self.graph_data)
            for algo in self.algo_values:
                self.algo_values[algo]['label'].config(bg='white')

            self.algo_values[self.controller.switcher.current_algorithm.name]['label'
                    ].config(bg='green')

            self.graph_points()
            time.sleep(1)
            self.update_idletasks()

    def update_logs(self):

        while self.simulation_values['simulating']:
            for algo in self.algo_texts:
                self.algo_values[algo]['log'].configure(state=tk.NORMAL)
                self.algo_values[algo]['log'].insert(tk.END,
                        str(self.algo_values[algo]['algo'
                        ].get_next_log()))

                self.algo_values[algo]['log'
                        ].configure(state=tk.DISABLED)
            self.update_idletasks()


if __name__ == '__main__':

    sim = Simulator(None)
    sim.title('Simulation of Page Replacement')
    sim.attributes('-fullscreen', True)
    sim.initialize()
    sim.mainloop()