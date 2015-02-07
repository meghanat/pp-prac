import cpu
import threading
import thread
from LRUAlgorithm import LRU

def start_simulation(simulation_values):
    page_num_stream = []  # Each List Entry
                          # [pid, virtual_page_number, set of threads that have
                          #  read from this entry]
    event_page_stream = threading.Event()  # Used to wait for an address to be 
                                           # available on page_num_stream
    number_processes = simulation_values["num_processes"] # 3
    main_memory_size = simulation_values["memory"] * (2 ** 30)  # 1GB
    page_size = simulation_values["page_size"] * (2 ** 10)  # 4KB
    number_frames = main_memory_size / page_size
    process_size = simulation_values["vas"] * (2 ** 30)  # 4GB Virtual Address space
    number_virtual_pages = process_size / page_size

    number_pr_threads = 1  # No of page replacement algorithms
    threads = []  # Array of PR started. Used to wait on them

    #print "THREAD: ", thread.get_ident()
    try:
        thread = threading.Thread(target=lambda : cpu.start_CPU(number_processes, 
                                    page_num_stream, event_page_stream), args=())
        threads.append(thread)
        thread.start()

        lru = LRU(number_virtual_pages, number_frames, number_pr_threads, page_num_stream, event_page_stream)
        thread = threading.Thread(target=lru, args=())
        threads.append(thread)
        thread.start()
    except Exception as e:
        print "Failed to start thread:", e


    for thread in threads:
        thread.join()
