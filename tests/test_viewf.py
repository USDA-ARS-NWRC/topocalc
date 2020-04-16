#!/usr/bin/env python

"""Tests for `viewf` package."""


import unittest

import numpy as np

from viewf.viewf import viewf


class TestViewf(unittest.TestCase):
    """Tests for `viewf` package."""

    def test_theory_edge(self):
        """Test with infinite edge dem"""

        dem = np.ones((50, 50))
        dem[:, :25] = 100000

        svf, tvf = viewf(dem, spacing=10)

        # The top should all be ones with 100% sky view
        self.assertTrue(
            np.array_equal(svf[:, :24],
                           np.ones_like(svf[:, :24]))
        )

        # The edge should be 50% or 0.5 svf
        np.testing.assert_allclose(
            svf[:, 25],
            0.5 * np.ones_like(svf[:, 25]),
            atol=1e-3
        )
