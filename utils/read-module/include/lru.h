#ifndef __LRU_H
#define __LRU_H

#include "algo.h"

void lru_replace_frame(algorithm* algo, struct  page_stream_entry* entry);
void lru_update_frame_in_memory(algorithm* algo, int frame_no);

#endif