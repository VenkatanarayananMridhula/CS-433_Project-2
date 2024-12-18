import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage import gaussian_filter1d

def wrap_dihedral_angles(dihedral_angles):
    """
    Wrap angles close to 180 degrees back into the range [-90, 90].
    """
    wrapped_angles = dihedral_angles.copy()
    wrapped_angles[wrapped_angles > 90] -= 180
    wrapped_angles[wrapped_angles < -90] += 180
    return wrapped_angles

def process_combined_distributions(base_directory="."):
    """
    Process and overlay QM, unbiased+biased, and unbiased dihedral distributions for comparison.
    
    Parameters:
        base_directory (str): Base directory containing QM and simulation data directories.
    """
    # Define relative paths
    qm_directory = os.path.join(base_directory, "QM")
    simulation_dirs = {"Unbiased": "unbiased", "Unbiased+Biased": "unbiased_biased"}
    temperatures = {"150 K": "150_NVE", "300 K": "300_NVE", "1200 K": "1200_NVE"}

    # Initialize the combined overlay plot
    fig, axes = plt.subplots(1, 3, figsize=(18, 6), sharey=True)
    fig.suptitle("Comparison of QM, Unbiased, and Unbiased+Biased Distributions", fontsize=20, fontweight='bold')

    for idx, (temp_label, temp_dir) in enumerate(temperatures.items()):
        ax = axes[idx]
        ax.set_title(temp_label, fontsize=16, fontweight='bold')

        # Process and overlay QM data
        qm_file = os.path.join(qm_directory, f"dihedral_angles_{temp_label.split()[0]}.out")
        if os.path.exists(qm_file):
            qm_data = pd.read_csv(qm_file, delim_whitespace=True, comment="#", names=["Frame", "Dihedral_Angle(deg)"])
            qm_angles = wrap_dihedral_angles(qm_data["Dihedral_Angle(deg)"])
            hist_qm, bins = np.histogram(qm_angles, bins=np.linspace(-90, 90, 100), density=True)
            smoothed_qm = gaussian_filter1d(hist_qm, sigma=2)
            ax.plot((bins[:-1] + bins[1:]) / 2, smoothed_qm, label="QM", linestyle='-', linewidth=3)

        # Process and overlay Simulation data
        for sim_label, sim_dir in simulation_dirs.items():
            sim_path = os.path.join(base_directory, sim_dir, "attempt_0_0", temp_dir)
            all_distributions = []
            if os.path.exists(sim_path):
                for file_name in os.listdir(sim_path):
                    if file_name.endswith(".out"):
                        file_path = os.path.join(sim_path, file_name)
                        try:
                            sim_data = pd.read_csv(file_path, delim_whitespace=True, comment="#", names=["Frame", "Dihedral_Angle(deg)"])
                            sim_angles = wrap_dihedral_angles(sim_data["Dihedral_Angle(deg)"])
                            hist, _ = np.histogram(sim_angles, bins=np.linspace(-90, 90, 100), density=True)
                            all_distributions.append(hist)
                        except Exception as e:
                            print(f"Error processing file {file_path}: {e}")
                if all_distributions:
                    averaged_hist = np.mean(all_distributions, axis=0)
                    smoothed_hist = gaussian_filter1d(averaged_hist, sigma=2)
                    ax.plot((bins[:-1] + bins[1:]) / 2, smoothed_hist, label=sim_label, linestyle='--' if sim_label == "Unbiased" else '-.', linewidth=3)

        # Customize the plot
        ax.set_xlabel("Dihedral Angle (degrees)", fontsize=14, fontweight='bold')
        ax.set_xlim(-30, 30)
        ax.grid(True, linestyle="--", alpha=0.7)
        if idx == 0:
            ax.set_ylabel("Frequency (Smoothed)", fontsize=14, fontweight='bold')
        ax.legend(fontsize=12)

    # Save and show the combined overlay plot
    output_path = os.path.join(base_directory, "comparison_dihedral_distribution.png")
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig(output_path)
    plt.close()
    print(f"Saved comparison dihedral distribution plot: {output_path}")

# Example usage
if __name__ == "__main__":
    # Base directory (relative to the script location)
    base_directory = os.path.join(os.getcwd(), "dihedral")
    process_combined_distributions(base_directory)
