#include <sys/queue.h>
#include <stdio.h>
#include <stdlib.h>

#include "head.h"

int main(){
	struct fooq q;
	struct foo *p;
	TAILQ_INIT(&q);
	struct foo data;

	data.datum = 3;
	TAILQ_INSERT_HEAD(&q, &data, tailq);

	function(&q);
	
	p = TAILQ_FIRST(&q);
	printf("%d\n", p->datum);	
}
