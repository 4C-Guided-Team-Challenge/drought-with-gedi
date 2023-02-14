import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

sns.set()  # Setting seaborn as default style even if use only matplotlib
palette = sns.color_palette("hls", 8)


def layered_plot_per_polygon(data: pd.DataFrame, x, bar_y, line_y, title):
    fig, ax = plt.subplots(4, 2, figsize=(30, 24), sharey=False, sharex=True)
    fig.suptitle(title, fontsize=30)
    fig.tight_layout(pad=3.0, h_pad=4.0, w_pad=8.0)

    for i in range(8):
        subplot = ax[i // 2, i % 2]

        # Select polygon from the data. Polygon IDs go from 1 to 8.
        polygon_id = i + 1
        polygon_data = data[data['polygon_id'] == polygon_id]

        # Bar plot.
        sns.barplot(polygon_data, x=x, y=bar_y, color='#6BC5ED', ax=subplot)
        subplot.set_title(f"Polygon {polygon_id}", fontsize=20)

        # Line plot on top.
        pai_subplot = subplot.twinx()
        sns.pointplot(polygon_data, x=x, y=line_y, color='#FA5705',
                      ax=pai_subplot)

    return fig, ax


def barplot_per_polygon(data: pd.DataFrame, x, y, ylabel, title,
                        color='#6BC5ED', sharey=False) -> plt.figure:
    fig, ax = plt.subplots(4, 2, figsize=(30, 24), sharey=sharey)
    fig.suptitle(title, fontsize=30)
    fig.tight_layout(pad=3.0, h_pad=4.0, w_pad=8.0)

    for i in range(8):
        subplot = ax[i // 2, i % 2]

        # Select polygon from the data. Polygon IDs go from 1 to 8.
        polygon_id = i + 1
        polygon_data = data[data['polygon_id'] == polygon_id]

        # Plot.
        sns.barplot(polygon_data, x=x, y=y, color=color, ax=subplot)
        subplot.set_title(f"Polygon {polygon_id}", fontsize=20)
        subplot.set_ylabel(ylabel)

    return fig


def catplot_per_polygon(data: pd.DataFrame, x, y, hue, kind, bands, title,
                        sharey=False) -> plt.figure:
    for i in range(8):
        # Select polygon from the data. Polygon IDs go from 1 to 8.
        polygon_id = i + 1
        polygon_data = data[data['polygon_id'] == polygon_id]
        melt = pd.melt(polygon_data[[x, *bands]], id_vars=x,
                       var_name=hue, value_name=y)

        # Plot.
        cat = sns.catplot(x=x, y=y, hue=hue, data=melt, kind=kind, aspect=3)
        cat.fig.suptitle(f"Polygon {polygon_id}", fontsize=15)
