import cpu
import threading
import thread

page_num_stream = []
event_page_stream = threading.Event()

print "THREAD: ", thread.get_ident()
cpu.start_CPU(page_num_stream, event_page_stream)

