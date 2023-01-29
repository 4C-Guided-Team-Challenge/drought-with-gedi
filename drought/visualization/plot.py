import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

sns.set()  # Setting seaborn as default style even if use only matplotlib
palette = sns.color_palette("hls", 8)


def barplot_per_polygon(data: pd.DataFrame, x, y, ylabel, title,
                        color='#6BC5ED', sharey=False) -> plt.figure:
    fig, ax = plt.subplots(4, 2, figsize=(30, 24), sharey=sharey)
    fig.suptitle(title, fontsize=30)
    fig.tight_layout(pad=3.0, h_pad=4.0, w_pad=8.0)

    for i in range(8):
        subplot = ax[i // 2, i % 2]
        subplot.set_facecolor('white')

        # Select polygon from the data. Polygon IDs go from 1 to 8, so we need
        # i + 1.
        polygon_id = i + 1
        polygon_data = data[data['polygon_id'] == polygon_id]

        # Plot.
        sns.barplot(polygon_data, x=x, y=y, color=color, ax=subplot)
        subplot.set_title(f"Polygon {polygon_id}", fontsize=20)
        subplot.set_ylabel(ylabel)

    return fig
