import numpy as np
import pandas as pd
import streamlit as st

import plotly.express as px
from sklearn.preprocessing import MinMaxScaler

import processing
from constants import LABELS
from . import rmse_utils, sidebar, vis_utils
from visualisation.draw import fig_layout
from . import ef_utils


def main():
    st.title('Enhancement Factor calculator')
    
    # # # #
    # # #
    # # First step of calculations and the user input required to calculate it
    #
    st.markdown('## First step of calculations')
    st.markdown('### Calculating the number of molecules ($N$) in the solution')
    step = st.beta_expander('Show description')
    with step:
        st.markdown(r'### <p style="text-align: center;">$$N=N_A \times C \times V$$</p>', unsafe_allow_html=True)
        st.markdown(r'$N$ - Number of particles')
        st.markdown(r'$N_A$ - Avogadro constant $[mol^{-1}]$')
        st.markdown(r'$C$ - Molar concentration $[\frac{mol}{dm^3}]$')
        st.markdown(r'$V$ - Volume $[{dm^3}]$')

    # #  Concentration of analyte in solution (in mol/dm^3
    concentration = ef_utils.get_concentration()
    
    # # Volume of solution (ml)
    volume = ef_utils.get_volume()
    
    # # Calculating the number of molecules
    num_molecules = ef_utils.num_of_molecules(concentration, volume)

    st.markdown(r'$N =$' + f' {"{:.1e}".format(num_molecules)} $[m^2]$')

    # # # #
    # # #
    # # Second step of calculations and the user input required to calculate it
    #
    st.markdown('---')
    st.markdown('## Second step of calculations')
    st.markdown('### Calculating the laser spot ($S_{Laser}$), '
                'which is the function of wave length and aperture of the lens:')
    step = st.beta_expander('Show description')

    with step:
        st.markdown(
            r'### <p style="text-align: center;font-size:1.15em">$$S_{Laser}=\frac{1.22 \times \lambda}{NA}$$</p>',
            unsafe_allow_html=True)
        st.markdown(r'$S_{Laser}$ - diameter of the laser spot $[m]$')
        st.markdown(r'$\lambda$ - Laser wavelength $[m]$')
        st.markdown(r'$NA$ - value of numerical aperture, lens dependent')

    cols = st.beta_columns(2)
    with cols[0]:
        # # Laser wavelength in nm
        laser_wave_length = ef_utils.get_Laser_wave_length()
    with cols[1]:
        # # Lens parameter - Numerical aperture
        lens_params = ef_utils.get_lens_params()

    # # Calculating the Laser spot
    s_laser = ef_utils.cal_size_of_laser_spot(laser_wave_length, lens_params)
    st.markdown(r'$S_{Laser} =$' + f' {"{:.1e}".format(s_laser)} $[m^2]$')

    # # # #
    # # #
    # # Third step of calculations and the user input required to calculate it
    #
    st.markdown('---')
    st.markdown('## Third step of calculations')
    st.markdown('### Calculating the surface area irradiated with the laser ($S_{0}$)')
    step = st.beta_expander('Show description')

    with step:
        st.markdown(
            r'### <p style="text-align: center;font-size:1.15em">$$S_{0}=\pi \times (\frac{S_{Laser}}{2})^2$$</p>',
            unsafe_allow_html=True)
        st.markdown(r'$S_{0}$ - Surface area of the laser spot $[m^2]$')
        st.markdown(r'$\pi$ - mathematical constant, approximately equal to 3.14159')
        st.markdown(r'$S_{Laser}$ - Laser spot diameter calculated in the previous step $[m^2]$')

    s0_spot_area = np.pi * (s_laser / 2) ** 2
    st.markdown(r'$S_{0} =$' + f' {"{:.1e}".format(s0_spot_area)} $[m^2]$')

    # # # #
    # # #
    # # Fourth step of calculations and the user input required to calculate it
    #
    st.markdown('---')
    st.markdown('## Fourth step of calculations')
    st.markdown('### Determination of the number of molecules per laser irradiated surface ($N_{SERS}$)')
    step = st.beta_expander('Show description')

    with step:
        # # Basic formula for N_SERS
        st.markdown(
            r'### <p style="text-align: center;font-size:1.15em">$$N_{SERS} = N_{Laser} \times coverage$$</p>',
            unsafe_allow_html=True)
        # # Arrow
        st.markdown(
            r'### <p style="text-align: center;font-size:1.15em; margin-top:-35px; margin-bottom:-55px;">&darr;</p>',
            unsafe_allow_html=True)
        # # Formula for N_LASER
        st.markdown(
            r'### <p style="text-align: center;font-size:1.15em; margin-top:-35px">$$N_{Laser} = '
            r'\frac {N \times S_{Laser}}{S_{Platform}}$$</p>',
            unsafe_allow_html=True)
        # # Arrow
        st.markdown(
            r'### <p style="text-align: center;font-size:1.15em; margin-top:-35px; margin-bottom:-55px;">&darr;</p>',
            unsafe_allow_html=True)
        # # Final formula for N_SERS
        st.markdown(
            r'### <p style="text-align: center;font-size:1.15em; margin-top:-35px">$$N_{SERS} = '
            r'\frac {N \times S_{Laser} \times coverage}{S_{Platform}}$$</p>',
            unsafe_allow_html=True)
    
        st.markdown(r'$N_{SERS}$ - The number of molecules per laser irradiated surface')
        st.markdown(r'$N_{Laser}$ - $$\frac {N \times S_{Laser}}{S_{Platform}}$$')
        st.markdown(r'$coverage$ - Surface coverage with the particles (e.g. for p-MBA $10^{-6} M$ ~= 10%')
        st.markdown(r'$N$ - Number of particles')
        st.markdown(r'$S_{Laser}$ - Laser spot diameter calculated in the previous step $[m]$')
        st.markdown(r'$S_{Platform}$ - Surface of the SERS platform '
                    r'$\times$ surface area development coefficient (rough surface ~= 2) $[m^2]$')

    # # The area of active surface of the SERS substrate
    s_platform = ef_utils.get_active_surface_area()
    # # The coverage of the analyte on the surface between 10^-6 and 6*10^-6 ~=10%
    surface_coverage = ef_utils.get_surface_coverage()

    # n_sers = (num_molecules * s_laser * surface_coverage) / s_platform  # formula version
    n_sers = (num_molecules * s0_spot_area * surface_coverage) / s_platform  # Szymborski use

    # TODO delete after checking the results
    # st.markdown(f'num_molecules: {"{:.1e}".format(num_molecules)}')
    # st.markdown(f's_laser: {"{:.1e}".format(s_laser)}')
    # st.markdown(f'surface_coverage: {"{:.1e}".format(surface_coverage)}')
    # st.markdown(f's_platform: {"{:.1e}".format(s_platform)}')

    st.markdown(r'$N_{SERS} =$' + f' {"{:.1e}".format(n_sers)}')
    st.markdown('---')

    # # # #
    # # #
    # # Fifth step of calculations and the user input required to calculate it
    #
    st.markdown('## Fifth step of calculations')
    st.markdown('### Calculation of the volume from which the Raman signal for your compound in solids is recorded')
    step = st.beta_expander('Show description')
    with step:
        st.markdown(r'### <p style="text-align: center;">$$V_{compound}=S_0 \times h$$</p>', unsafe_allow_html=True)
        st.markdown(r'$V_{compound}$ - The volume of your chemical compound crystal subjected to laser illumination')
        st.markdown(r'$S_0$ - Surface area of the laser spot $[m^2]$')
        st.markdown(r'$h$ - Depth into which the laser penetrates the chemical compound in crystalline '
                    r'form (in the case of p-MBA we assume 2 mm)')

    penetration_depth = ef_utils.get_penetration_depth()
    v_compound = s0_spot_area * penetration_depth

    st.markdown(r'$V_{compound} =$' + f' {"{:.1e}".format(v_compound)} $[m^3]$')

    st.markdown('---')

    # # # #
    # # #
    # # Sixth step of calculations and the user input required to calculate it
    #
    st.markdown('## Sixth step of calculations')
    st.markdown(r'### Determining the number of p-MBA molecules from which the Raman signal ($N_{Raman}$) comes')
    step = st.beta_expander('Show description')
    with step:
        st.markdown('---')
    
        st.markdown(r'Firstly, the mass of the irradiated crystal is determined from the compound density:')
        st.markdown(r'### <p style="text-align: center;">$$m_{compound}=d_{compound} \times V_{compound}$$</p>',
                    unsafe_allow_html=True)
        st.markdown(r'$m_{compound}$ - Mass of the irradiated crystal $[g]$')
        st.markdown(r'$d_{compound}$ - density of the chemical compound$[\frac{g}{cm^3}]$')
        st.markdown(
            r'$V_{compound}$ - The volume of your chemical compound crystal subjected to laser illumination $[m^3]$')
    
        st.markdown('---')
    
        st.markdown(r'Secondly, from the molar mass, the number of moles is calculated:')
        st.markdown(r'### <p style="text-align: center;">$$n_{compound}= \frac{m_{compound}}{M_{compound}}$$</p>',
                    unsafe_allow_html=True)
        st.markdown(r'$n_{compound}$ - Number of moles of the irradiated crystal $[mol]$')
        st.markdown(r'$m_{compound}$ - Mass of the irradiated crystal $[g]$')
        st.markdown(r'$M_{compound}$ - Molecular weight of the chemical compound $[\frac{g}{mol}]$')
    
        st.markdown('---')
    
        st.markdown(
            r'Lastly, The number of molecules irradiated during the recording of the Raman spectrum (&N_{Raman}&) is obtained by multiplying the number of moles by the Avogadro constant:')
        st.markdown(r'### <p style="text-align: center;">$$N_{Raman}= n_{compound}\times N_A$$</p>',
                    unsafe_allow_html=True)
        st.markdown(r'$N_{Raman}$ - The number of molecules irradiated during the recording of the Raman spectrum')
        st.markdown(r'$n_{compound}$ - Mass of the irradiated crystal $[mol]$')
        st.markdown(r'$N_A$ - Avogadro constant $[mol^{-1}]$')

    # # Molecular weight
    compound_density = ef_utils.get_compound_density()
    compound_molecular_weight = ef_utils.get_molecular_weight()

    n_raman = ef_utils.cal_n_raman(v_compound, compound_density, compound_molecular_weight)

    st.markdown(r'$N_{Raman} =$' + f' {"{:.1e}".format(n_raman)}')

    st.markdown('---')

    # # # #
    # # #
    # # Final, seventh, step of calculations and the user input required to calculate it
    #
    st.markdown('## Seventh step of calculations')
    st.markdown('### Calculating the Enhancement Factor')
    step = st.beta_expander('Show description')
    with step:
        st.markdown(
            r'### <p style="text-align: center;">$$EF=\frac{I_{SERS}}{N_{SERS}} \times \frac{N_{Raman}}{I_{Raman}}$$</p>',
            unsafe_allow_html=True)
        st.markdown(
            r'$I_{SERS}$ - SERS signal (particular peak) of your compound adsorbed on the surface of the SERS platform')
        st.markdown(r'$N_{SERS}$ - The number of molecules irradiated during the recording of the SERS spectrum')
        st.markdown(r'$I_{Raman}$ - Raman signal (particular peak) of you compound')
        st.markdown(r'$N_{Raman}$ - The number of molecules irradiated during the recording of the Raman spectrum')
    
    # # SERS intensity and Raman Intensity
    # TODO wykorzystać Charza pomysł na wybieranie maksa z zakresu, gdyby ktoś chciał, żeby mu automatycznie policzyło
    i_sers, i_raman = ef_utils.get_laser_intensities()
    
    SLIDERS_PARAMS_RAW = {'rel_height': dict(min_value=1, max_value=100, value=20, step=1),
                          'height': dict(min_value=1000, max_value=100000, value=10000, step=1000),
                          }
    SLIDERS_PARAMS_NORMALIZED = {'rel_height': dict(min_value=0.01, max_value=1., value=0.5, step=0.01),
                                 'height': dict(min_value=0.001, max_value=1., value=0.1, step=0.001),
                                 }
    files = st.sidebar.file_uploader(label='Upload your data or try with ours',
                                     accept_multiple_files=True,
                                     type=['txt', 'csv'])
    
    if not files:
        return st.warning("Upload data for calculatios")
    
    main_expander = st.beta_expander("Customize your chart")
    # Choose plot colors and templates
    with main_expander:
        plot_palette, plot_template = vis_utils.get_chart_vis_properties()


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

    bg_colors = {'Peak 1': 'yellow', 'Peak 2': 'green'}

    peak1_range = st.slider(f'Peak 1 range ({bg_colors["Peak 1"]})',
                            min_value=plot_x_min,
                            max_value=plot_x_max,
                            value=[plot_x_min, plot_x_max])

    peak1_range = [int(i) for i in peak1_range.split('__')]

    fig = px.line(df)
    fig_layout(plot_template, fig, plot_palette)
    fig.update_xaxes(range=[plot_x_min, plot_x_max])

    peaks = zip([peak1_range], ['Peak 1'])

    for ran, text in peaks:
        if ran == [plot_x_min, plot_x_max]: continue
    
        fig.add_vline(x=ran[0], line_dash="dash", annotation_text=text)
        fig.add_vline(x=ran[1], line_dash="dash")
        fig.add_vrect(x0=ran[0], x1=ran[1], line_width=0, fillcolor=bg_colors[text], opacity=0.15)

    cols = st.beta_columns((7, 3))

    with cols[0]:
        st.plotly_chart(fig, use_container_width=True)

    mask = (peak1_range[0] <= df.index) & (df.index <= peak1_range[1])
    peak1 = df[mask]

    enhancement_factor = (i_sers / n_sers) * (n_raman / i_raman)

    st.markdown(r'$EF =$' + f' {"{:.1e}".format(enhancement_factor)}')

    st.markdown('---')

    # TODO, to zapobiega pojawianiu się błędu, ale trzeba to poprawić
    st.stop()
