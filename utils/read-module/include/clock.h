#ifndef __CLOCK_H
#define __CLOCK_H

#include "algo.h"

void clock_replace_frame(algorithm* algo, struct  page_stream_entry* entry);
void clock_update_frame_in_memory(algorithm* algo, int frame_no);

#endif