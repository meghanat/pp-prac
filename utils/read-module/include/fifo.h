#ifndef __FIFO_H
#define __FIFO_H

#include "algo.h"

void fifo_replace_frame(algorithm* algo, struct  page_stream_entry* entry);
void fifo_update_frame_in_memory(algorithm* algo, int frame_no);

#endif