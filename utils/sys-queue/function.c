#include <sys/queue.h>
#include <stdlib.h>

#include "head.h"

void function(struct fooq * a){
	struct foo data;
	data.datum = 4;
	TAILQ_INSERT_HEAD(a, &data, tailq);
}
