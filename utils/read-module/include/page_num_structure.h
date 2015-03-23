struct page_stream_entry{
    TAILQ_ENTRY(page_stream_entry) tailq;
    long pid;
    long virt_page_no;
    
};

TAILQ_HEAD(page_stream_entry_q, page_stream_entry);

