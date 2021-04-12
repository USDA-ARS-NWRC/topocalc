#!/usr/bin/env python

import unittest
# from sys import platform

import numpy as np

from topocalc.viewf import viewf


class TestViewf(unittest.TestCase):
    """Tests for `viewf` package."""

    def test_theory_edge(self):
        """Test with infinite edge dem"""

        dem = np.ones((50, 50))
        dem[:, :25] = 100000

        svf, tvf = viewf(dem, spacing=10, nangles=360)

        # The top should all be ones with 100% sky view
        # OSX seems to have some difficulty with the edge
        # where linux does not. It is close to 1 but not quite
        # if platform == 'darwin':
        #     np.testing.assert_allclose(
        #         svf[:, :24],
        #         np.ones_like(svf[:, :24]),
        #         atol=1e-2
        #     )

        #     # The edge should be 50% or 0.5 svf
        #     np.testing.assert_allclose(
        #         svf[:, 25],
        #         0.5 * np.ones_like(svf[:, 25]),
        #         atol=1e-2
        #     )

        # else:
        np.testing.assert_array_equal(
            svf[:, :24],
            np.ones_like(svf[:, :24])
        )

        # The edge should be 50% or 0.5 svf
        np.testing.assert_allclose(
            svf[:, 25],
            0.5 * np.ones_like(svf[:, 25]),
            atol=1e-3
        )

    def test_viewf_errors_dem(self):
        """Test viewf dem errors"""

        self.assertRaises(ValueError, viewf, np.ones(10), 10)

    def test_viewf_errors_angles(self):
        """Test viewf nangles errors"""

        self.assertRaises(ValueError, viewf, np.ones(
            (10, 1)), 10, nangles=10)

    def test_viewf_errors_sin_slope(self):
        """Test viewf sin_slope errors"""

        self.assertRaises(ValueError, viewf, np.ones(
            (10, 1)), 10, sin_slope=10*np.ones((10, 1)))
