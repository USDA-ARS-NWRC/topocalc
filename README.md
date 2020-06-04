# topocalc

[![Pypi version](https://img.shields.io/pypi/v/topocalc.svg)](https://pypi.python.org/pypi/topocalc)
[![Build Status](https://travis-ci.com/USDA-ARS-NWRC/topocalc.svg?branch=master)](https://travis-ci.com/USDA-ARS-NWRC/topocalc)
[![Coverage Status](https://coveralls.io/repos/github/USDA-ARS-NWRC/topocalc/badge.svg?branch=master)](https://coveralls.io/github/USDA-ARS-NWRC/topocalc?branch=master)
[![Maintainability](https://api.codeclimate.com/v1/badges/20930fef2e7b7fe91dd3/maintainability)](https://codeclimate.com/github/USDA-ARS-NWRC/topocalc/maintainability)

The `topocalc` package is a collection of functions to calculate various metrics on a digital elevation model (DEM). The calculations follow the equations laid out in [Dozier and Frew, 1990](https://doi.org/10.1109/36.58986) for the gradient, horizon and sky view factor. Currently the supported calculations are:

1. Gradient for slope and aspect
2. Horizon angles for an azimuth
3. Sky view factor for percent of the sky that is visible from a point on the DEM

- [topocalc](#topocalc)
- [Backgourd](#backgourd)
  - [Azimuth convention](#azimuth-convention)
  - [Gradient for slope and aspect](#gradient-for-slope-and-aspect)
  - [Horizon angles](#horizon-angles)
  - [Sky view factor](#sky-view-factor)
- [Usage](#usage)
  - [Installation](#installation)
  - [Gradient usage](#gradient-usage)
  - [Sky view factor usage](#sky-view-factor-usage)
  - [Command Line Interface](#command-line-interface)

# Background

## Azimuth convention

For the azimuth's and aspects, the convention is that South is 0 degrees (0 radians) with positive values to the East (+90 degrees or pi/4 radians) and negative values to the West (-90 degrees or -pi/4 radians). North is -180 degrees or -pi/2.

## Gradient for slope and aspect

The gradient method calculates the slope and aspect of the input DEM. There are two methods in `topocalc.gradient` the `gradient_d4` and `gradient_d8`.

`gradient_d4` mimics the slope and aspect calculations of the [IPW `gradient`](https://github.com/USDA-ARS-NWRC/ipw/tree/master/src/bin/topocalc/gradient) function. This calculates the slope for a finite difference in just the x/y direction.

`gradient_d8` (the default) uses a second order finite difference for a 3x3 square around a given point on the DEM.

The gradient is used to calculate the aspect from North (0 degrees). A conversion function will take the aspect in degrees and convert to radians with South being 0.

## Horizon angles

The horizon angle for a point on the DEM is the angle from zenith to the horizon for a given azimuth. Following the methods laid out in [Dozier and Frew, 1990](https://doi.org/10.1109/36.58986) and in [IPW `horizon`](https://github.com/USDA-ARS-NWRC/ipw/tree/master/src/bin/topocalc/horizon) the grid is rotated in the direction of the azimuth to make it a one dimensional problem.

For two points `i` and `j`, we compare the slope from `i` and `j` with the slope of `j`'s horizon. If the slope is greater, then all points past `j` are not visible. If the slope is less, then all points between `i` and `j` don't need to be checked and the search can continue past point `j`. This search is performed in C to significantly speed up the computation.

The values reported from `horizon` are cosine of the horizon angle.

## Sky view factor

The sky view factor (`svf`) is the amount of the sky that is visible to a particular point. The `svf` is between 0 and 1 with 1 indicating no obstructions from surrounding terrain and 0 indicating full obstruction. The `svf` uses the slope, aspect and horizon angles for 72 directions to estimate the sky view factor for the DEM.

# Usage

## Installation

> **NOTE**: `topocalc` has only been tested for Python 3.5 to 3.8 on Linux and MacOSX environments.

To install:

`pip install topocalc`

## Gradient usage

```python
from topocalc.gradient import gradient_d8

# Load the DEM into a numpy array
dem = load_dem(path_to_dem)

# grid cell spacing for the DEM
dem_dx = 30
dem_dy = 30

slope, aspect = gradient_d8(dem, dem_dx, dem_dy)
```

## Sky view factor usage

```python
from topocalc.viewf import viewf

# Load the DEM into a numpy array
dem = load_dem(path_to_dem)

# grid cell spacing for the DEM
dem_spacing = 30

svf, tvf = viewf(dem, spacing=dem_spacing)
```

## Command Line Interface

Comming soon!
