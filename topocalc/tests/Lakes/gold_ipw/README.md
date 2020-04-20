# Gold files

## DEM creation

Create an IPW image from the `topo.nc` file.

```python3 ./tests/Lakes/gold_ipw/make_gold_dem.py```

This will output an IPW topo image in the same directory.

## Skew gold files

The skew gold files are to test the skew function and ensure that the python version is exactly the same as the IPW version. A bash script creates skew IPW images from -45 to 45 degrees in 5 degree increments.

```./tests/Lakes/gold_ipw/skew/make_gold_skew```

## Horizon gold files

The horizon gold files are to test the horizon function and ensure that the python version is exactly the same as the IPW version. A bash script creates horizon IPW images from 0 to 360 degrees in 5 degree increments. However, the horizon function called here is custom in that the original only outputs 8 bit images and this one outputs 16 bit images. If recreating the gold files, ensure that the [hor1d](https://github.com/USDA-ARS-NWRC/ipw/blob/2e802fc01000e0426c77a0c9b9959cfc807b2d65/src/bin/topocalc/horizon/horizon.sh#L118) calls have `-n 16` for each of the two calls.

```./tests/Lakes/gold_ipw/horizon/make_gold_horizon```
