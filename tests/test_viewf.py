#!/usr/bin/env python

"""Tests for `viewf` package."""


import unittest

import numpy as np

from viewf.viewf import viewf


class TestViewf(unittest.TestCase):
    """Tests for `viewf` package."""

    def test_theory_edge(self):
        """Test with theortical edge dem"""

        dem = np.ones((50, 50))
        dem[:, :25] = 10000

        svf, tvf = viewf(dem, spacing=10)
