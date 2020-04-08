import unittest
from spatialnc import ipw
import numpy as np

from viewf.skew import skew


class TestSkew(unittest.TestCase):

    def test_skew(self):
        """ Test the skew of an image """

        # read in the dem from the gold file as we're
        # comparing the arrays at the end and it will
        # ensure that the bit resolution is kept

        infile = 'tests/Lakes/gold/gold_dem.ipw'
        d = ipw.IPW(infile)
        gold_dem = d.bands[0].data

        for angle in range(-45, 45, 5):

            # Get the IPW gold skew values
            gold = ipw.IPW('./tests/Lakes/gold/skew/skew_{}.ipw'.format(angle))
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
