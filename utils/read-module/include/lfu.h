#ifndef __LFU_H
#define __LFU_H

#include "algo.h"

void lfu_replace_frame(algorithm* algo, struct  page_stream_entry* entry);
void lfu_update_frame_in_memory(algorithm* algo, int frame_no);

#endif