import subprocess

import netCDF4 as nc
import numpy as np
from spatialnc import ipw
from spatialnc.topo import get_topo_stats

# convert the netcdf DEM to IPW file
# Convert the dem to integers to limit the problem of
# double percision error for the input

# Load the netcdf dem and get all the geo coords for IPW
topo_path = './tests/Lakes/topo.nc'

d = nc.Dataset(topo_path)
dem = np.round(d.variables['dem'][:])
d.close()

ts = get_topo_stats(topo_path)

csys = 'UTM'
nbits = 16

# Create the IPW image
i = ipw.IPW()
i.new_band(dem)
i.add_geo_hdr(
    coordinates=[ts['u'], ts['v']],
    d=[ts['dv'], ts['du']],
    units=ts['units'],
    csys=csys
)

i.write(
    './tests/Lakes/gold_ipw/gold_dem.ipw',
    nbits=nbits
)

# Create a gradient ipw image (slope and aspect)
# in both 8 and 16 bit resolution
cmd = "gradient -i {0} ./tests/Lakes/gold_ipw/gold_dem.ipw >" \
    "./tests/Lakes/gold_ipw/gold_gradient{0}.ipw"

for nbit in [8, 16]:
    with subprocess.Popen(
        cmd.format(nbit),
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True
    ) as s:

        # stream the output of WindNinja to the logger
        return_code = s.wait()
        if return_code == 0:
            print('Succces for: {}'.format(cmd.format(nbit)))
        else:
            raise Exception('Error creating gradient')
