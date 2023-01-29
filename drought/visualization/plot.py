import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

sns.set()  # Setting seaborn as default style even if use only matplotlib
palette = sns.color_palette("hls", 8)


def barplot_per_region(data: pd.DataFrame, region_ids, region_col,
                       x, y, ylabel, title, color='#6BC5ED', sharey=False
                       ) -> plt.figure:
    num_of_regions = len(region_ids)
    fig, ax = plt.subplots(num_of_regions // 2, 2, figsize=(30, 24),
                           sharey=sharey)
    fig.suptitle(title, fontsize=30)
    fig.tight_layout(pad=3.0, h_pad=4.0, w_pad=8.0)

    for i in range(num_of_regions):
        subplot = ax[i // 2, i % 2]
        subplot.set_facecolor('white')

        # Select region / polygon from the data.
        selected_region = data[data[region_col] == region_ids[i]]

        # Plot.
        sns.barplot(selected_region, x=x, y=y, color=color, ax=subplot)
        subplot.set_title(f"Region {i+1}", fontsize=20)
        subplot.set_ylabel(ylabel)

    return fig
