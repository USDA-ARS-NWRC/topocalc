#!/usr/bin/env python

import unittest
import collections

import numpy as np
from spatialnc import ipw

from viewf.viewf import viewf, viewcalc, d2r
from viewf.horizon import horizon


class TestViewfIPW(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        # input DEM
        infile = 'tests/Lakes/gold_ipw/gold_dem.ipw'
        d = ipw.IPW(infile)
        cls.gold_dem = np.double(d.bands[0].data)
        cls.spacing = d.bands[0].dline

        # 8 bit gradient
        infile = 'tests/Lakes/gold_ipw/gold_gradient8.ipw'
        d = ipw.IPW(infile)
        cls.gold_slope = d.bands[0].data    # sin(slope)
        cls.gold_aspect = d.bands[1].data   # radians

        # Viewf gold files
        cls.gold_file = 'tests/Lakes/gold_ipw/viewf/viewf_8bit_16ang.ipw'
        d = ipw.IPW(cls.gold_file)
        cls.gold_svf_data = d.bands[0].data
        cls.gold_tcf_data = d.bands[1].data

        # to make a fair comparison, first convert the viewf to
        # integers then back using the 8 bit LQ
        # with viewf the float min/max are constant from 0-1
        cls.float_min_svf = 1.0
        cls.float_max_svf = 0.0
        cls.float_min_tcf = 0.0
        cls.float_max_tcf = 1.0
        cls.int_min = 0
        cls.int_max = 2**8-1

    def convert_horizon_to_ipw_and_back(self, horizon):
        """Convert the horizon image to 8 bit image and then back
        to mimic what hor1d is doing in viewf.sh

        Arguments:
            horizon {np.array} -- numpy array of horizon values
        """
        svf_int = ipw.map_fn(horizon, self.float_min_svf,
                             self.float_max_svf, self.int_min, self.int_max)
        svf_float = (self.float_max_svf - self.float_min_svf) * \
            (svf_int / self.int_max) + self.float_min_svf

        return svf_float

    def test_viewf_ipw(self):
        """test viewf compared with IPW images"""

        # This gets really wonky as viewf in IPW is a shell
        # script that is calling hor1d. So each hor1d call
        # will create a temporary 8 bit image

        svf, tcf = viewf(
            self.gold_dem,
            self.spacing,
            nangles=16,
            sin_slope=self.gold_slope,
            aspect=self.gold_aspect
        )

        Horizon = collections.namedtuple('Horizon', ['azimuth', 'hcos'])

        angles = np.linspace(-180, 180, num=16, endpoint=False)

        hcos = {}
        for angle in angles:
            h = horizon(angle, self.gold_dem, self.spacing)  # has been tested
            hcos[angle] = Horizon(
                d2r(angle),
                self.convert_horizon_to_ipw_and_back(h)
            )

        svf, tcf = viewcalc(self.gold_slope, self.gold_aspect, hcos)

        svf
