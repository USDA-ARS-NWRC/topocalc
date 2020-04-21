import os
import unittest

import numpy as np
from spatialnc import ipw

from topocalc.skew import adjust_spacing, skew


class TestSkew(unittest.TestCase):

    def test_skew(self):
        """ Test the skew of an image """

        test_dir = os.path.dirname(os.path.abspath(__file__))

        # read in the dem from the gold file as we're
        # comparing the arrays at the end and it will
        # ensure that the bit resolution is kept

        infile = os.path.join(
            test_dir, 'Lakes/gold_ipw/gold_dem.ipw')
        d = ipw.IPW(infile)
        gold_dem = d.bands[0].data

        for angle in range(-45, 45, 5):

            # Get the IPW gold skew values
            gold = ipw.IPW(
                os.path.join(
                    test_dir,
                    'Lakes/gold_ipw/skew/skew_{}.ipw'.format(angle)
                )
            )
            gold_data = gold.bands[0].data

            # skew the initial array
            sarr = skew(gold_dem, angle=angle, fill_min=True)
            self.assertTrue(np.array_equal(sarr, gold_data))

            # skew it back to original
            sbarr = skew(sarr, angle=angle, fwd=False)
            self.assertTrue(np.array_equal(sbarr, gold_dem))

    def test_skew_error(self):
        """Test error with angle"""
        self.assertRaises(ValueError, skew, np.ones(10), -100)
        self.assertRaises(ValueError, skew, np.ones(10), 100)

    def test_skew_spacing_angle(self):
        """Test the output of the skew spacing angle"""

        # outputs created on Ubuntu 18.04
        s = [
            50.0, 50.19099187716737, 50.77133059428725,
            51.76380902050415, 53.2088886237956,
            55.168895948124586, 57.735026918962575,
            61.0387294380728, 65.27036446661393]

        for i, a in enumerate(range(0, 45, 5)):
            t = adjust_spacing(50, a)
            self.assertAlmostEqual(t, s[i])

    def test_adjust_spacing(self):
        """Test error with angle"""
        self.assertRaises(ValueError, adjust_spacing, 10, -100)
        self.assertRaises(ValueError, skew, 10, 100)
