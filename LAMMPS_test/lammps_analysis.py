import pandas as pd
import matplotlib.pyplot as plt

def read_thermo_data(file_name, columns, skiprows=1):
    return pd.read_csv(file_name, sep=r'\s+', skiprows=skiprows, names=columns)

def compute_running_stats(data, column, window_size):
    data[f"{column}_RunningAvg"] = data[column].rolling(window=window_size).mean()
    data[f"{column}_StdDev"] = data[column].rolling(window=window_size).std()
    return data

def annotate_plot(ax, x_data, y_data, interval, label_prefix="", fontsize=10, color="black"):
    for i in range(0, len(x_data), interval):
        if not pd.isna(y_data.iloc[i]):
            ax.annotate(f"{label_prefix}{y_data.iloc[i]:.2f}",
                        (x_data.iloc[i], y_data.iloc[i]),
                        textcoords="offset points", xytext=(0, 10), ha='center',
                        fontsize=fontsize, color=color, fontweight="bold")

def plot_thermo_data(data, columns, window_size, annotation_interval, colors, title, save_dir):
    fig, axs = plt.subplots(len(columns), 3, figsize=(18, 6 * len(columns)))
    for idx, column in enumerate(columns):
        row_axs = axs[idx] if len(columns) > 1 else axs

        # Plot 1: Property vs Step
        row_axs[0].plot(data["Step"], data[column], label=column, color=colors['property'])
        row_axs[0].plot(data["Step"], data[f"{column}_RunningAvg"], label=f"{column} Running Avg", linestyle="--", color=colors['running_avg'])
        row_axs[0].set_title(f"{title}: {column} vs Step")
        row_axs[0].set_xlabel("Step")
        row_axs[0].set_ylabel(column)
        row_axs[0].legend()
        row_axs[0].text(0.9, 0.1, f"Mean: {data[column].mean():.2f}", transform=row_axs[0].transAxes, fontsize=12, color="red", fontweight="bold")
        annotate_plot(row_axs[0], data["Step"], data[f"{column}_RunningAvg"], annotation_interval, fontsize=10, color="black")

        # Plot 2: Running Average vs Step
        row_axs[1].plot(data["Step"], data[f"{column}_RunningAvg"], label=f"{column} Running Avg", linestyle="--", color=colors['running_avg'])
        row_axs[1].set_title(f"{column} Running Avg vs Step")
        row_axs[1].set_xlabel("Step")
        row_axs[1].set_ylabel(f"{column} Running Avg")
        row_axs[1].legend()
        row_axs[1].text(0.9, 0.1, f"Mean Avg: {data[f'{column}_RunningAvg'].mean():.2f}", transform=row_axs[1].transAxes, fontsize=12, color="red", fontweight="bold")
        annotate_plot(row_axs[1], data["Step"], data[f"{column}_RunningAvg"], annotation_interval, label_prefix="Avg: ", fontsize=10, color="black")

        # Plot 3: Std Dev vs Step
        row_axs[2].plot(data["Step"], data[f"{column}_StdDev"], label=f"{column} Std Dev", linestyle="dotted", color=colors['std_dev'])
        row_axs[2].set_title(f"{column} Std Dev vs Step")
        row_axs[2].set_xlabel("Step")
        row_axs[2].set_ylabel(f"{column} Std Dev")
        row_axs[2].legend()
        row_axs[2].text(0.9, 0.1, f"Mean Std: {data[f'{column}_StdDev'].mean():.2f}", transform=row_axs[2].transAxes, fontsize=12, color="red", fontweight="bold")
        annotate_plot(row_axs[2], data["Step"], data[f"{column}_StdDev"], annotation_interval, label_prefix="Std: ", fontsize=10, color="black")

#         # Save individual subplots
#         column_save_path = f"{save_dir}/{column}_plots.png"
#         plt.savefig(column_save_path)

    plt.tight_layout()
    plt.savefig(f"{save_dir}/all_properties_plots.png")
    plt.show()
