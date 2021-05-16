import streamlit as st

from visualisation import draw


def show_charts(cols_left, figs, plots_color, template):
    """
    Neat function for plotting charts on left side.

    Elements of fig type are simply drawn.
    For elements of type list or tuple creates inner loop - first element is
    drawn and the rest is hidden in beta_expander

    Args:
        cols_left (list): columns to draw on
        figs (list): list of figures to plot (might be nested)
        plots_color: color scale for plotly
        template: plotly template

    """
    for col_left, fig in zip(cols_left, figs):
        with col_left:
            if isinstance(fig, (list, tuple)):
                f = fig[0]
                draw.fig_layout(template, f, plots_colorscale=plots_color)
                f.update_traces(line=dict(width=3.5))
                st.plotly_chart(f, use_container_width=True)
                
                with st.beta_expander('Detailed view'):
                    for f in fig[1:]:
                        draw.fig_layout(template, f, plots_colorscale=plots_color)
                        f.update_traces(line=dict(width=3.5))
                        st.plotly_chart(f, use_container_width=True)
            else:
                draw.fig_layout(template, fig, plots_colorscale=plots_color)
                fig.update_traces(line=dict(width=3.5))
                st.plotly_chart(fig, use_container_width=True)
