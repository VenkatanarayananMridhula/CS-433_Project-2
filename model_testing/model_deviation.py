import os
import pandas as pd
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d

def plot_model_deviation_comparison(unbiased_file, biased_file, output_dir):
    """
    Combines and compares model deviations (forces and energy) for Unbiased and Unbiased+Biased.

    Args:
        unbiased_file (str): Path to the unbiased model deviation file.
        biased_file (str): Path to the unbiased+biased model deviation file.
        output_dir (str): Directory to save the resulting comparison plots.

    Returns:
        None
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Read and clean the data
    columns = ["step", "max_devi_v", "min_devi_v", "avg_devi_v", 
               "max_devi_f", "min_devi_f", "avg_devi_f", "devi_e"]
    data_unbiased = pd.read_csv(unbiased_file, delim_whitespace=True, comment='#', header=None, names=columns)
    data_biased = pd.read_csv(biased_file, delim_whitespace=True, comment='#', header=None, names=columns)

    # Smooth the data to reduce noise
    sigma = 2  # Degree of smoothing
    unbiased_avg_f_smooth = gaussian_filter1d(data_unbiased["avg_devi_f"], sigma)
    biased_avg_f_smooth = gaussian_filter1d(data_biased["avg_devi_f"], sigma)
    unbiased_max_f_smooth = gaussian_filter1d(data_unbiased["max_devi_f"], sigma)
    biased_max_f_smooth = gaussian_filter1d(data_biased["max_devi_f"], sigma)
    unbiased_e_smooth = gaussian_filter1d(data_unbiased["devi_e"], sigma)
    biased_e_smooth = gaussian_filter1d(data_biased["devi_e"], sigma)

    # Create subplots for comparison
    fig, axes = plt.subplots(1, 2, figsize=(14, 6), sharey=False)
    plt.suptitle("Model Deviation Comparison:Unbiased+Biased vs Unbiased", fontsize=16, fontweight='bold')

    # Plot Force Deviation
    axes[0].plot(data_unbiased["step"], unbiased_avg_f_smooth, label="Unbiased Avg Force", color='blue')
    axes[0].plot(data_biased["step"], biased_avg_f_smooth, label="Unbiased+Biased Avg Force", color='orange')
    axes[0].plot(data_unbiased["step"], unbiased_max_f_smooth, label="Unbiased Max Force", color='blue', linestyle='--')
    axes[0].plot(data_biased["step"], biased_max_f_smooth, label="Unbiased+Biased Max Force", color='orange', linestyle='--')
    axes[0].set_title("Force Deviation (Smoothed)", fontsize=14, fontweight='bold')
    axes[0].set_xlabel("Frame", fontsize=12)
    axes[0].set_ylabel("Deviation (eV/\u00c5)", fontsize=12)
    axes[0].grid(True)
    axes[0].legend(fontsize=10)

    # Plot Energy Deviation
    axes[1].plot(data_unbiased["step"], unbiased_e_smooth, label="Unbiased Energy Deviation", color='blue')
    axes[1].plot(data_biased["step"], biased_e_smooth, label="Unbiased+Biased Energy Deviation", color='orange')
    axes[1].set_title("Energy Deviation (Smoothed)", fontsize=14, fontweight='bold')
    axes[1].set_xlabel("Frame", fontsize=12)
    axes[1].set_ylabel("Deviation (eV)", fontsize=12)
    axes[1].grid(True)
    axes[1].legend(fontsize=10)

    # Adjust layout and save
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    output_file = os.path.join(output_dir, "model_deviation_comparison.png")
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.show()
    print(f"Plots saved at: {output_file}")

# File paths and output directory
unbiased_file = './model_deviation/unbiased/absolute/model_devi_absolute.out'
biased_file = './model_deviation/unbiased_biased/absolute/model_devi_absolute.out'
output_dir = './model_deviation/'


# Call the function
plot_model_deviation_comparison(unbiased_file, biased_file, output_dir)
