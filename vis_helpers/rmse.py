import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from scipy.signal import find_peaks
from sklearn.preprocessing import MinMaxScaler

import processing
from constants import LABELS
from . import rmse_utils, sidebar, vis_utils
from visualisation.draw import fig_layout

SLIDERS_PARAMS_RAW = {'rel_height': dict(min_value=1, max_value=100, value=20, step=1),
                      'height': dict(min_value=1000, max_value=100000, value=10000, step=1000),
                      }
SLIDERS_PARAMS_NORMALIZED = {'rel_height': dict(min_value=0.01, max_value=1., value=0.5, step=0.01),
                             'height': dict(min_value=0.001, max_value=1., value=0.1, step=0.001),
                             }

# TODO sprawdzić jak liczą w publikacjach RMSE, czy to chodzi o różnice intensywnosci miedzy widmami,
#  czy o stosunek pików, który w sumie powinien być stały... więc trochę bez sensu

def main():
    spectra_types = ['EMPTY', 'BWTEK', 'RENI', 'WITEC', 'WASATCH', 'TELEDYNE', 'JOBIN']
    rmse_types = ['OneP', 'P2P']
    st.header('Relative Standard Deviation (RSD)')

    spectrometer = st.sidebar.selectbox("Choose spectra type",
                                        spectra_types,
                                        format_func=LABELS.get,
                                        index=0
                                        )
    sidebar.print_widgets_separator()

    files = st.sidebar.file_uploader(label='Upload your data or try with ours',
                                     accept_multiple_files=True,
                                     type=['txt', 'csv'])

    if not files:
        return st.warning("Upload data for calculatios")

    main_expander = st.beta_expander("Customize your chart")
    # Choose plot colors and templates
    with main_expander:
        plot_palette, plot_template = vis_utils.get_chart_vis_properties()

    rmse_type = st.radio("RSD type:",
                         rmse_types,
                         format_func=LABELS.get,
                         index=0)

    df = processing.save_read.files_to_df(files, spectrometer)
    df = df.interpolate().bfill().ffill()

    plot_x_min = int(df.index.min())
    plot_x_max = int(df.index.max())

    rescale = st.sidebar.checkbox("Normalize")
    if rescale:
        scaler = MinMaxScaler()
        rescaled_data = scaler.fit_transform(df)
        df = pd.DataFrame(rescaled_data, columns=df.columns, index=df.index)
        sliders_params = SLIDERS_PARAMS_NORMALIZED
    else:
        sliders_params = SLIDERS_PARAMS_RAW

    bg_colors = {'Peak 1': 'yellow', 'Peak 2': 'orange'}

    cols = st.beta_columns((4, 1, 4))
    # with cols[0]:
    peak1_range = st.slider(f'Peak 1 range ({bg_colors["Peak 1"]})',
                            min_value=plot_x_min,
                            max_value=plot_x_max,
                            value=[plot_x_min, plot_x_max])
    peak1_range = [int(i) for i in peak1_range.split('__')]

    with cols[0]:
        if rmse_type == 'P2P':
            peak2_range = st.slider(f'Peak 2 range ({bg_colors["Peak 2"]})',
                                    min_value=plot_x_min,
                                    max_value=plot_x_max,
                                    value=[plot_x_min, plot_x_max])
        
            peak2_range = [int(i) for i in peak2_range.split('__')]

    fig = px.line(df)
    fig_layout(plot_template, fig, plot_palette)
    fig.update_xaxes(range=[plot_x_min, plot_x_max])

    peaks = zip([peak1_range], ['Peak 1'])

    if rmse_type == 'P2P':
        peaks = zip([peak1_range, peak2_range], ['Peak 1', 'Peak 2'])

    for ran, text in peaks:
        if ran == [plot_x_min, plot_x_max]: continue
    
        fig.add_vline(x=ran[0], line_dash="dash", annotation_text=text)
        fig.add_vline(x=ran[1], line_dash="dash")

    cols = st.beta_columns((7, 3))

    with cols[0]:
        st.plotly_chart(fig, use_container_width=True)

    mask = (peak1_range[0] <= df.index) & (df.index <= peak1_range[1])
    peak1 = df[mask]

    if rmse_type == 'P2P':
        mask = (peak2_range[0] <= df.index) & (df.index <= peak2_range[1])
        peak2 = df[mask]

    with cols[1]:
        st.header('RSD scores')
        st.write(' ')
        if rmse_type == 'OneP':
            st.table(rmse_utils.rsd_one_peak(peak1))
        elif rmse_type == 'P2P':
            st.table(rmse_utils.rsd_peak_to_peak_ratio(peak1, peak2))

    # TODO to bym przerzucił do wizualizacji i jakoś zaaplikował możliwość dodania peaków do widma
    cols = st.beta_columns(4)
    peak_width = cols[0].slider('Min width', min_value=5, max_value=100, value=15, step=5, )
    peak_distance = cols[1].slider('Min distance', min_value=1, max_value=100, value=5, step=1, )
    peak_rel_height = cols[2].slider('Min relative height', **sliders_params['rel_height'])
    peak_height = cols[3].slider('Min absolute height', **sliders_params['height'])

    peak_width = int(peak_width)
    peak_distance = int(peak_distance)
    peak_rel_height = float(peak_rel_height) if rescale else int(peak_rel_height)
    peak_height = float(peak_height) if rescale else int(peak_height)

    peak_df = pd.DataFrame()
    for col in df.columns:
        # TODO dodać opcję wyświetlania peaków na wykresach z podpisami od pasm dla maximow lokalnych
        #  oczywiście gdzieś w wersji wizualizacyjnej
        peaks = np.array(find_peaks(df[col], width=peak_width, distance=peak_distance,
                                    rel_height=peak_rel_height, height=peak_height)
                         )[0]
        peak_df = pd.concat([peak_df, df[col].reset_index().iloc[pd.Series(peaks), :].set_index('Raman Shift')],
                            axis=1)

    # FIX
    #  poniżej moje wypociny mające na celu splaszczenie ramanshifta i przypisanie splaszczonym
    #  ramanshiftom srednich wartości, ale coś poszło nie do końca tak jak chciałem ; /

    fig = px.scatter(peak_df, x=peak_df.index, y=peak_df.columns, title='Peak positions')
    fig.update_xaxes(range=[plot_x_min, plot_x_max])
    st.plotly_chart(fig, use_container_width=True)
