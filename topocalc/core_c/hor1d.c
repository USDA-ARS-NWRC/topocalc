/*
 * horizon in forward direction for equi-spaced elevation vector
 */

#include <math.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdio.h>
#include "topo_core.h"

#define SLOPEF(i, j, zi, zj) \
    (((zj) <= (zi)) ? 0 : ((zj) - (zi)) / ((float)((j) - (i))))

#define SLOPEB(i, j, zi, zj) \
    (((zj) <= (zi)) ? 0 : ((zj) - (zi)) / ((float)((i) - (j))))

void hor2d(
    int nrows,    /* rows of elevations array */
    int ncols,    /* columns of elevations array */
    double *z,    /* elevations */
    double delta, /* spacing */
    bool forward, /* forward function */
    int *h,       /* horizon function */
    double *hcos) /* cosines of angles to horizon */
{
    int i, j; /* loop index */

    /*
    * Allocate an array for the line buffers to populate
    */
    int *hbuf;
    hbuf = (int *)calloc(ncols, sizeof(int));

    double *obuf;
    obuf = (double *)calloc(ncols, sizeof(double));

    double *zbuf;
    zbuf = (double *)calloc(ncols, sizeof(double));

    /*
     * main loop, read in full line at a time
     */
    for (i = 0; i < nrows; i++)
    {
        // Fill the zbuf with the rows elevation
        for (j = 0; j < ncols; j++)
        {
            zbuf[j] = z[j + ncols * i];
        }

        /*
    	 * find points that form horizons
    	 */
        if (forward)
        {
            hor1f(ncols, zbuf, hbuf);
        }
        else
        {
            hor1b(ncols, zbuf, hbuf);
        }

        /*
    	 * if not mask output, compute and write horizons along each row
    	 */
        horval(ncols, zbuf, delta, hbuf, obuf);

        for (j = 0; j < ncols; j++)
        {
            hcos[i * ncols + j] = obuf[j];
        }
    }
}

/*
* hor1f from hor1f.c in IPW
* https://github.com/USDA-ARS-NWRC/ipw/blob/main/src/bin/topocalc/horizon/hor1d/hor1f.c
*/
int hor1f(
    int n,     /* length of vectors b and h */
    double *z, /* elevation function */
    int *h)    /* horizon function (return) */
{
    double sihj; /* slope i to h[j] */
    double sij;  /* slope i to j */
    double zi;   /* z[i] */
    int i;       /* point index */
    int j;       /* point index */
    int k;       /* h[j] */

    /*
    * end point is its own horizon in forward direction; first point is
    * its own horizon in backward direction
    */
    h[n - 1] = n - 1;

    /*
    * For forward direction, loop runs from next-to-end backward to
    * beginning.  For backward direction, loop runs from
    * next-to-beginning forward to end.
    */
    for (i = n - 2; i >= 0; --i)
    {
        zi = z[i];

        /*
        * Start with next-to-adjacent point in either forward or backward
        * direction, depending on which way loop is running. Note that we
        * don't consider the adjacent point; this seems to help reduce noise.
        */
        if ((k = i + 2) >= n)
            --k;
        /*
        * loop until horizon found
        */

        do
        {
            /*
            * slopes from i to j and from j to its horizon
            */

            j = k;
            k = h[j];
            sij = SLOPEF(i, j, zi, z[j]);
            sihj = SLOPEF(i, k, zi, z[k]);

            /*
            * if slope(i,j) >= slope(i,h[j]), horizon has been found; otherwise
            * set j to k (=h[j]) and loop again
            */

        } while (sij < sihj);

        /*
        * if slope(i,j) > slope(j,h[j]), j is i's horizon; else if slope(i,j)
        * is zero, i is its own horizon; otherwise slope(i,j) = slope(i,h[j])
        * so h[j] is i's horizon
        */

        if (sij > sihj)
        {
            h[i] = j;
        }
        else if (sij == 0)
        {
            h[i] = i;
        }
        else
        {
            h[i] = k;
        }
    }
    return (0);
}

/*
* hor1b from hor1b.c in IPW
* https://github.com/USDA-ARS-NWRC/ipw/blob/main/src/bin/topocalc/horizon/hor1d/hor1b.c
*/
int hor1b(
    int n,     /* length of vectors b and h */
    double *z, /* elevation function */
    int *h)    /* horizon function (return) */
{
    double sihj; /* slope i to h[j] */
    double sij;  /* slope i to j */
    double zi;   /* z[i] */
    int i;       /* point index */
    int j;       /* point index */
    int k;       /* h[j] */

    /*
    * end point is its own horizon in forward direction; first point is
    * its own horizon in backward direction
    */
    h[0] = 0;

    /*
    * For forward direction, loop runs from next-to-end backward to
    * beginning.  For backward direction, loop runs from
    * next-to-beginning forward to end.
    */
    for (i = 1; i < n; ++i)
    {
        zi = z[i];

        /*
        * Start with next-to-adjacent point in either forward or backward
        * direction, depending on which way loop is running. Note that we
        * don't consider the adjacent point; this seems to help reduce noise.
        */
        if ((k = i - 2) < 0)
            ++k;
        /*
        * loop until horizon found
        */

        do
        {
            /*
            * slopes from i to j and from j to its horizon
            */

            j = k;
            k = h[j];
            sij = SLOPEB(i, j, zi, z[j]);
            sihj = SLOPEB(i, k, zi, z[k]);

            /*
            * if slope(i,j) >= slope(i,h[j]), horizon has been found; otherwise
            * set j to k (=h[j]) and loop again
            */

        } while (sij < sihj);

        /*
        * if slope(i,j) > slope(j,h[j]), j is i's horizon; else if slope(i,j)
        * is zero, i is its own horizon; otherwise slope(i,j) = slope(i,h[j])
        * so h[j] is i's horizon
        */

        if (sij > sihj)
        {
            h[i] = j;
        }
        else if (sij == 0)
        {
            h[i] = i;
        }
        else
        {
            h[i] = k;
        }
    }
    return (0);
}

/*
**	Calculate values of cosines of angles to horizons, measured
**	from zenith, from elevation difference and distance.  Let
**	G be the horizon angle from horizontal and note that:
**
**		sin G = z / sqrt( z^2 + dis^2);
**
**	This result is the same as cos H, where H measured from zenith.
**  https://github.com/USDA-ARS-NWRC/ipw/blob/main/src/bin/topocalc/horizon/hor1d/horval.c
*/

void horval(
    int n,        /* length of horizon vector */
    double *z,    /* elevations */
    double delta, /* spacing */
    int *h,       /* horizon function */
    double *hcos) /* cosines of angles to horizon */
{
    int d;       /* difference in indices */
    int i;       /* index of point */
    int j;       /* index of horizon point */
    double diff; /* elevation difference */

    for (i = 0; i < n; ++i)
    {

        /* # grid points to horizon */
        j = h[i];
        d = j - i;

        /* point is its own horizon */
        if (d == 0)
        {
            *hcos++ = 0;
        }

        /* else need to calculate sine */
        else
        {
            if (d < 0)
                d = -d;
            diff = z[j] - z[i];
            *hcos++ = diff / (double)hypot(diff, d * delta);
        }
    }
}