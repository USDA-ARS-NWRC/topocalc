from spatialnc import ipw
from spatialnc.topo import get_topo_stats
import netCDF4 as nc

# convert the netcdf DEM to IPW file

# Load the netcdf dem and get all the geo coords for IPW
topo_path = './tests/Lakes/topo.nc'

d = nc.Dataset(topo_path)
dem = d.variables['dem'][:]
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
    './tests/Lakes/gold/gold_dem.ipw',
    nbits=nbits
)
