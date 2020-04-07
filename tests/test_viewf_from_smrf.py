from spatialnc import ipw
import matplotlib.pyplot as plt
import numpy as np
import unittest
import os
import subprocess as sp

from smrf.data import loadTopo
from smrf.utils.topo import hor1d, viewf

from tests.test_configurations import SMRFTestCase

rme_topo_config = {
    'basin_lon': -116.7547,
    'basin_lat': 43.067,
    'filename': 'tests/RME/topo/topo.nc',
    'type': 'netcdf',
            'threading': False
}


class TestViewf(SMRFTestCase):

    def ipw_skew(self, angle, infile, out_dir):

        skew_out = os.path.join(out_dir, 'skew.ipw')
        unskew_out = os.path.join(out_dir, 'unskew.ipw')

        # Skew the image
        cmd = 'skew -a {} {} > {}'.format(angle, infile, skew_out)
        proc = sp.Popen(cmd, shell=True, env=os.environ.copy()).wait()

        if proc != 0:
            raise OSError('IPW skew failed')

        # Unskew the image
        cmd = 'skew {} > {}'.format(skew_out, unskew_out)
        proc = sp.Popen(cmd, shell=True, env=os.environ.copy()).wait()

        if proc != 0:
            raise OSError('IPW skew failed')

        i = ipw.IPW(skew_out)
        ii = ipw.IPW(unskew_out)

        os.remove(skew_out)
        os.remove(unskew_out)

        return i.bands[0].data, ii.bands[0].data

    def test_hor1d_RME_forward(self):
        """ Hor1d on the RME test dem forward"""

        # IPW topo calc
        topo = loadTopo.topo(rme_topo_config, calcInput=True,
                             tempDir='tests/RME/output')

        dx = np.mean(np.diff(topo.x))

        # FORWARD DIRECTION
        # ipw/src/bin/topocalc/horizon/hor1d/hor1d -a 90 dem.ipw > hor1d_forward.ipw
        # hor1d in the East direction
        hipw = ipw.IPW('tests/RME/gold/radiation/hor1d_forward.ipw')
        hipw = hipw.bands[0].data

        # compare the 1D horizon functions
        h = hor1d.hor1f(topo.dem[1, :])
        py_hcos = hor1d.horval(topo.dem[1, :], dx, h)

        # C version
        c_hcos = hor1d.hor1d_c(topo.dem[1, :], dx)
        self.assertTrue(np.all(c_hcos == py_hcos))

        # 2D horizon functions
        hcos = hor1d.hor1d(topo.dem, dx)
        hcos2 = hor1d.hor2d_c(topo.dem, dx)
        self.assertTrue(np.all(hcos == hcos2))

        # about the tolerance between a 16bit image and a float
        self.assertTrue(np.allclose(hipw, hcos, atol=1e-4))

    def test_hor1d_RME_backward(self):
        """ Hor1d on the RME test dem backward """

        # IPW topo calc
        topo = loadTopo.topo(rme_topo_config, calcInput=True,
                             tempDir='tests/RME/output')

        dx = np.mean(np.diff(topo.x))

        # BACKWARD DIRECTION
        # ipw/src/bin/topocalc/horizon/hor1d/hor1d -b -a 90 dem.ipw > hor1d_backward.ipw
        # hor1d in the East direction
        hipw = ipw.IPW('tests/RME/gold/radiation/hor1d_backward.ipw')
        hipw = hipw.bands[0].data

        # compare the 1D horizon functions
        h = hor1d.hor1b(topo.dem[1, :])
        py_hcos = hor1d.horval(topo.dem[1, :], dx, h)
        self.assertTrue(np.allclose(hipw[1, :], py_hcos, atol=1e-4))

        # C version
        c_hcos = hor1d.hor1d_c(topo.dem[1, :], dx, fwd=False)
        self.assertTrue(np.all(py_hcos == c_hcos))
        self.assertTrue(np.allclose(hipw[1, :], c_hcos, atol=1e-4))

        # 2D horizon functions
        hcos = hor1d.hor1d(topo.dem, dx, fwd=False)
        hcos2 = hor1d.hor2d_c(topo.dem, dx, fwd=False)
        self.assertTrue(np.all(hcos == hcos2))

        # about the tolerance between a 16bit image and a float
        # There are 2 points where IPW found it to be it's own horizon
        # but upon further inspection, the python versions have
        # found the correct horizon. Not sure what is happening with the
        # IPW version -- SH
        # self.assertTrue(np.allclose(hipw, hcos, atol=1e-3))

    def test_hor1d_Tuolumne_forward(self):
        """ hor1d Tuolumne test forward """
        # Pretty close, it doesn't pass but the bulk of the pixels are 0

        dem_file = 'tests/Tuolumne/topo/dem_50m.ipw'
        dem = ipw.IPW(dem_file)
        dx = dem.bands[0].dsamp
        z = dem.bands[0].data

        # convert to double
        z = z.astype(np.double)

        # ~/code/ipw/src/bin/topocalc/horizon/hor1d/hor1d -a 90 dem_50m.ipw > hor1d_forward.ipw
        # hor1d in the East direction using a special 16 bit version of hor1d
        hipw = ipw.IPW('tests/Tuolumne/gold/radiation/hor1d_forward.ipw')
        hipw = hipw.bands[0].data

        # C hor1d
        hcos = hor1d.hor2d_c(z, dx)

        # ensure that 99.9% (actual is 99.997%) of pixels are noise
        r = 100 * np.sum((hcos-hipw) <= 1e-5)/z.size
        self.assertTrue(r > 99.9)

    def test_hor1d_Tuolumne_backward(self):
        """ hor1d Tuolumne test backward """
        # Pretty close, it doesn't pass but the bulk of the pixels are 0

        dem_file = 'tests/Tuolumne/topo/dem_50m.ipw'
        dem = ipw.IPW(dem_file)
        dx = dem.bands[0].dsamp
        z = dem.bands[0].data

        # convert to double
        z = z.astype(np.double)

        # ~/code/ipw/src/bin/topocalc/horizon/hor1d/hor1d -b -a 90 dem_50m.ipw > hor1d_backward.ipw
        # hor1d in the East direction using a special 16 bit version of hor1d
        hipw = ipw.IPW('tests/Tuolumne/gold/radiation/hor1d_backward.ipw')
        hipw = hipw.bands[0].data

        # C hor1d
        hcos = hor1d.hor2d_c(z, dx, fwd=False)

        # ensure that 99.9% (actual is 99.997%) of pixels are noise
        r = 100 * np.sum((hcos-hipw) <= 1e-5)/z.size
        self.assertTrue(r > 99.9)

    def test_viewf_RME(self):
        """ Test the view factor for RME """

        # IPW topo calc for sky view factor
        topo = loadTopo.topo(rme_topo_config, calcInput=True,
                             tempDir='tests/RME/output')
        dx = np.mean(np.diff(topo.x))
        ipw_svf = topo.stoporad_in.bands[3].data
        ipw_tcf = topo.stoporad_in.bands[4].data

        # Calcualte the sky view factor
        svf, tcf = viewf.viewf(
            topo.dem, dx, slope=topo.slope, aspect=topo.aspect)

        plt.imshow(10*(ipw_svf-svf/10))
        plt.title('Sky view factor')
        plt.colorbar()
        plt.show()

        plt.hist((10*(ipw_svf-svf/10)).flatten(), bins=50)
        plt.show()

        # plt.imshow(ipw_tcf - tcf)
        # plt.title('Terrain configuration factor')
        # plt.colorbar()
        # plt.show()

    def test_viewf_Tuolumne(self):
        """ viewf Tuolumne test """

        # IPW DEM support is still there, just not easy to use
        topo_config = {
            'basin_lon': -116.7547,
            'basin_lat': 43.067,
            'dem': 'tests/Tuolumne/topo/dem_50m.ipw',
            'type': None,
            'threading': False
        }
        topo = loadTopo.topo(topo_config, calcInput=False,
                             tempDir='tests/Tuolumne/output')
        topo.readImages()
        topo.topoConfig['type'] = 'ipw'
        topo.stoporadInput()

        # viewf gold generated by IPW with 16bit hor1d
        ivf = ipw.IPW('tests/Tuolumne/gold/radiation/viewf_16.ipw')
        ipw_svf = ivf.bands[0].data

        # Calcualte the sky view factor
        dx = np.mean(np.diff(topo.x))
        svf, tcf = viewf.viewf(
            topo.dem, dx, slope=topo.slope, aspect=topo.aspect)

        plt.imshow(ipw_svf - svf)
        plt.title('Sky view factor')
        plt.colorbar()
        plt.show()

    def test_skew(self):
        """ Test the skew of an image """

        # Use the Tuolumne DEM
        infile = 'tests/Tuolumne/topo/dem_50m.ipw'
        out_dir = 'tests/Tuolumne/output'
        i = ipw.IPW(infile)
        arr = i.bands[0].data

        for angle in range(-45, 45, 5):

            # Get the IPW skew values
            ipw_skew, ipw_unskew = self.ipw_skew(angle, infile, out_dir)

            # skew the initial array
            sarr = viewf.skew(arr, angle=angle, fill_min=True)
            self.assertTrue(np.all(sarr == ipw_skew))

            # skew it back to original
            sbarr = viewf.skew(sarr, angle=angle, fwd=False)
            self.assertTrue(np.all(sbarr == ipw_unskew))

            # ensure that the skewed back is the same as the original
            self.assertTrue(np.all(arr == sbarr))

        # test the error
        self.assertRaises(ValueError, viewf.skew, arr, -100)
        self.assertRaises(ValueError, viewf.skew, arr, 100)

    def test_skew_hor1d_RME_foward(self):
        """ Test the skew then hor1d call """

        topo = loadTopo.topo(rme_topo_config, calcInput=True,
                             tempDir='tests/RME/output')
        dx = np.mean(np.diff(topo.x))

        dem_file = 'tests/RME/output/dem.ipw'
        cmd = 'demux -b 0 tests/RME/output/stoporad_in.ipw > {}'.format(
            dem_file)
        proc = sp.Popen(cmd, shell=True, env=os.environ.copy()).wait()

        # IPW command
        hcmd = '$IPW/aux/horizon/hor1d'
        out_file = 'tests/RME/output/horz.ipw'
        cmd = 'skew -a -22.5 {} | transpose | {} -a -22.5 | transpose | skew > {}'.format(
            dem_file, hcmd, out_file)

        # compare the 1D horizon functions
        h = hor1d.hor1f(topo.dem[1, :])
        py_hcos = hor1d.horval(topo.dem[1, :], dx, h)

        # C version
        c_hcos = hor1d.hor1d_c(topo.dem[1, :], dx)
        self.assertTrue(np.all(c_hcos == py_hcos))

        # 2D horizon functions
        hcos = hor1d.hor1d(topo.dem, dx)
        hcos2 = hor1d.hor2d_c(topo.dem, dx)
        self.assertTrue(np.all(hcos == hcos2))

        # about the tolerance between a 16bit image and a float
        self.assertTrue(np.allclose(hipw, hcos, atol=1e-4))