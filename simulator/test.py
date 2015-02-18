import OptimalAlgorithm as opt
import threading

# Test the page fault count logic
def test_lru_page_fault_count():
    number_frames = 3
    number_pr_threads = 1
    event_page_stream = threading.Event()
    event_page_stream.set()
    read_lock = threading.Lock()
    expected_faults = 7
    thread_set = set()

    page_num_stream = [[1, 2, set()], [1, 3, set()], [1, 2, set()], [1, 1, set()], [1, 5, set()], [1, 2, set()], [1, 4, set()], [1, 5, set()], [1, 3, set()], [1, 2, set()], [1, 5, set()], [1, 2, set()]]
    lruob = lru.LRU(100, number_frames, number_pr_threads, 
                       page_num_stream, event_page_stream, read_lock, thread_set)
    thread_lru = threading.Thread(target=lruob, args=())
    thread_lru.start()
    while len(page_num_stream) > 0:
        pass
    thread_lru._Thread__stop()
    assert expected_faults == lruob.get_page_fault_count()

def test_optimal_page_fault_count():
    number_frames = 3
    number_pr_threads = 1
    event_page_stream = threading.Event()
    event_page_stream.set()
    read_lock = threading.Lock()
    expected_faults = 5
    thread_set = set()

    page_num_stream = [[1, 2], [1, 3], [1, 2], [1, 1], [1, 5], [1, 2], [1, 4], [1, 5], [1, 3]]
    lruob = opt.Optimal(100, number_frames, number_pr_threads, 
                       page_num_stream, event_page_stream, read_lock, thread_set)
    thread_lru = threading.Thread(target=lruob, args=(None,))
    thread_lru.start()
    while len(page_num_stream) > 0:
        event_page_stream.set()
        pass
    thread_lru._Thread__stop()
    print lruob.get_page_fault_count()
    assert expected_faults == lruob.get_page_fault_count()

test_optimal_page_fault_count()

