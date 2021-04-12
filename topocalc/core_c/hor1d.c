/*
 * horizon in forward direction for equi-spaced elevation vector
 */

#include <math.h>
#include <stdlib.h>
#include <stdbool.h>
#include "topo_core.h"

void hor2d(
    int nrows,    /* rows of elevations array */
    int ncols,    /* columns of elevations array */
    double *z,    /* elevations */
    double delta, /* spacing */
    bool forward, /* forward function */
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
    double slope_ik;  /* slope i to k */
    double max_slope; /* max slope value */
    int max_point;    /* point with max horizon */
    double zi;        /* z[i] */
    int i;            /* current point index */
    int k;            /* search point index */
    double dist;      /* difference between i and k */

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
    for (i = n - 1; i >= 0; --i)
    {
        zi = z[i];

        /* assume the point is it's own horizon at first*/
        max_slope = 0;
        max_point = i;

        /*
        * Start with adjacent point in either forward or backward
        * direction, depending on which way loop is running. Note,
        * this differs from the original in that the original started
        * with the next to adjacent point
        */
        for (k = i + 1; k <= n; k++)
        {
            /*
            * Slope from the current point to the kth point
            */
            slope_ik = 0;
            if (z[k] > zi)
            {
                dist = (double)(k - i);
                slope_ik = (z[k] - zi) / dist;
            }

            /*
            * Compare each kth point against the maximum slope
            * already found. If it's slope is greater than the previous
            * horizon, then it's found a new horizon
            */
            if (slope_ik > max_slope)
            {
                max_slope = slope_ik;
                max_point = k;
            }
        }

        h[i] = max_point;
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
    double slope_ik;  /* slope i to k */
    double max_slope; /* max slope value */
    int max_point;    /* point with max horizon */
    double zi;        /* z[i] */
    int i;            /* current point index */
    int k;            /* search point index */
    double dist;      /* difference between i and k */

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

        /* assume the point is it's own horizon at first*/
        max_slope = 0;
        max_point = i;

        /*
        * Start with adjacent point in either forward or backward
        * direction, depending on which way loop is running. Note,
        * this differs from the original in that the original started
        * with the next to adjacent point
        */
        for (k = i - 1; k >= 0; k--)
        {

            /*
            * Slope from the current point to the kth point
            */
            slope_ik = 0;
            if (z[k] > zi)
            {
                dist = (double)(i - k);
                slope_ik = (z[k] - zi) / dist;
            }

            /*
            * Compare each kth point against the maximum slope
            * already found. If it's slope is greater than the previous
            * horizon, then it's found a new horizon
            */
            if (slope_ik > max_slope)
            {
                max_slope = slope_ik;
                max_point = k;
            }
        }

        h[i] = max_point;
    }
    return (0);
}

/*
**	Calculate values of cosines of angles to horizons, measured
**	from zenith, from elevation difference and distance.  Let
**	H be the angle from zenith and note that:
**
**		cos H = z / sqrt( z^2 + dis^2);
*/

void horval(
    int n,        /* length of horizon vector */
    double *z,    /* elevations */
    double delta, /* spacing */
    int *h,       /* horizon function */
    double *hcos) /* cosines of angles to horizon */
{
    double d;    /* difference in indices */
    int i;       /* index of point */
    int j;       /* index of horizon point */
    double diff; /* elevation difference */

    for (i = 0; i < n; ++i)
    {

        /* # grid points to horizon */
        j = h[i];
        d = (double)(j - i);

        /* point is its own horizon */
        if (d == 0)
        {
            hcos[i] = 0;
        }

        /* else need to calculate sine */
        else
        {
            if (d < 0)
                d = -d;
            diff = z[j] - z[i];
            // hcos[i] = diff / (double)hypot(diff, d * delta);
            hcos[i] = diff / sqrt(diff * diff + d * d * delta * delta);
        }
    }
}