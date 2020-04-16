#include <stdbool.h>

/* From hor1d.c */
int hor1f(int n, double *z, int *h);
int hor1b(int n, double *z, int *h);
void horval(int n, double *z, double delta, int *h, double *hcos);
void hor2d(int n, int m, double *z, double delta, bool forward, int *h, double *hcos);