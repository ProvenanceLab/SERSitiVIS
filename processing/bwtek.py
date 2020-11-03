from . import utils

RS = "Raman Shift"
DS = "Dark Subtracted #1"

spectra_params = {'sep': ';', 'skiprows': lambda x: x < 79 or x > 1500, 'decimal': ',',
                  'usecols': ['Pixel', RS, DS],
                  'skipinitialspace': True, 'encoding': "utf-8"}

meta_params = {'sep': ';', 'skiprows': lambda x: x > 78, 'decimal': ',', 'index_col': 0,
               'skipinitialspace': True, 'encoding': "utf-8", 'header': None}


def read_bwtek(uploaded_files):
    temp_data_df = {}
    temp_meta_df = {}

    for uploaded_file in uploaded_files:
        data, metadata = utils.read_spec(uploaded_file, spectra_params, meta_params)

        data = data[data.loc[:, 'Pixel'] > 310]
        data.set_index('Pixel', inplace=True)

        data.dropna(inplace=True, how='any', axis=0)

        data.rename(columns={DS: uploaded_file.name[:-4]}, inplace=True)
        data.set_index('Raman Shift', inplace=True)

        temp_data_df[uploaded_file.name] = data
        temp_meta_df[uploaded_file.name] = metadata

    return temp_data_df, temp_meta_df
