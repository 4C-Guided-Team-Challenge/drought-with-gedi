import h5py
import os
import numpy as np
import pandas as pd

data_path = "/maps/forecol/data/GEDI/level2B"
files = [f for f in os.listdir(data_path) if f.endswith(".h5")]

# TODO read the time from the h5 file name, granule['METADATA']['DatasetIdentification'] is empty
# data = {
#     "pai": np.array([]),
#     "l2b_quality_flag": np.array([]),
#     "shot_number": np.array([]),
#     "lon": np.array([]),
#     "lat": np.array([]),
# }

data = dict({})
for f in files:
    fname = os.path.join(data_path, f)
    granule = h5py.File(fname, "r")
    filter = np.array(granule['BEAM0000']['l2b_quality_flag'])==1
    data["pai"] = np.array(granule['BEAM0000']['pai'])[filter]
    data["l2b_quality_flag"] = np.array(granule['BEAM0000']['l2b_quality_flag'])[filter]
    data["shot_number"] = np.array(granule['BEAM0000']['geolocation']['shot_number'])[filter]
    data["lon"] = np.array(granule['BEAM0000']['geolocation']['lon_lowestmode'])[filter]
    data["lat"] = np.array(granule['BEAM0000']['geolocation']['lat_lowestmode'])[filter]
    # NOTE the following line can be used to save the data as a csv file
    df = pd.DataFrame(data)
