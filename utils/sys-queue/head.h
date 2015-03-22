struct foo {
    TAILQ_ENTRY(foo) tailq;
    int datum;
    /* ... */
};

TAILQ_HEAD(fooq, foo);

