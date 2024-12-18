import os
import pandas as pd
import matplotlib.pyplot as plt



def plot_energy_force_parity(
        directories, labels, metrics, output_dir,
        energy_file="test_results.e.out",
        force_file="test_results.f.out",
        fig_size=(10, 5)
):
    """
    Generates side-by-side energy and force parity plots and saves them.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Create a figure for the subplots
    fig, axes = plt.subplots(1, 2 * len(directories), figsize=(fig_size[0] * len(directories), fig_size[1]))

    for i, (directory, label) in enumerate(zip(directories, labels)):
        # Define file paths
        energy_path = os.path.join(directory, energy_file)
        force_path = os.path.join(directory, force_file)

        # Check if files exist
        if not os.path.exists(energy_path) or not os.path.exists(force_path):
            print(f"Missing files in {directory}. Skipping.")
            continue

        # Load energy and force data
        energy_data = pd.read_csv(energy_path, delim_whitespace=True, comment='#', names=["data_e", "pred_e"])
        force_data = pd.read_csv(force_path, delim_whitespace=True, comment='#',
                                 names=["data_fx", "data_fy", "data_fz", "pred_fx", "pred_fy", "pred_fz"])

        # Energy Parity Plot
        ax_energy = axes[2 * i]
        ax_energy.scatter(energy_data["data_e"], energy_data["pred_e"], alpha=0.6, label=label, color='blue')
        ax_energy.plot([
            energy_data["data_e"].min(), energy_data["data_e"].max()],
            [energy_data["data_e"].min(), energy_data["data_e"].max()],
            'r--', label="Ideal (y = x)")
        ax_energy.set_title(f"Energy Parity Plot\n{label}", fontsize=14, fontweight='bold')
        ax_energy.set_xlabel("AIMD Energy (eV)", fontsize=12, fontweight='bold')
        ax_energy.set_ylabel("Predicted Energy (eV)", fontsize=12, fontweight='bold')
        ax_energy.tick_params(axis='both', which='major', labelsize=10)
        ax_energy.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), fontsize=10)  # Legend outside
        ax_energy.grid(True)
        ax_energy.text(0.05, 0.75,
                       f"RMSE: {metrics[i]['Energy_RMSE']} eV\nMAE: {metrics[i]['Energy_MAE']} eV",
                       transform=ax_energy.transAxes, fontsize=10, fontweight='bold',
                       bbox=dict(facecolor='white', alpha=0.8))

        # Force Parity Plot
        ax_force = axes[2 * i + 1]
        ax_force.scatter(force_data["data_fx"], force_data["pred_fx"], alpha=0.6, label="Fx", marker='o', color='green')
        ax_force.scatter(force_data["data_fy"], force_data["pred_fy"], alpha=0.6, label="Fy", marker='x', color='orange')
        ax_force.scatter(force_data["data_fz"], force_data["pred_fz"], alpha=0.6, label="Fz", marker='^', color='purple')
        ax_force.plot([
            force_data[["data_fx", "data_fy", "data_fz"]].values.min(),
            force_data[["data_fx", "data_fy", "data_fz"]].values.max()],
            [force_data[["data_fx", "data_fy", "data_fz"]].values.min(),
             force_data[["data_fx", "data_fy", "data_fz"]].values.max()],
            'r--', label="Ideal (y = x)")
        ax_force.set_title(f"Force Parity Plot\n{label}", fontsize=14, fontweight='bold')
        ax_force.set_xlabel("AIMD Force Components (eV/\u00c5)", fontsize=12, fontweight='bold')
        ax_force.set_ylabel("Predicted Force Components (eV/\u00c5)", fontsize=12, fontweight='bold')
        ax_force.tick_params(axis='both', which='major', labelsize=10)
        ax_force.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), fontsize=10)  # Legend outside
        ax_force.grid(True)
        ax_force.text(0.05, 0.75,
                      f"RMSE: {metrics[i]['Force_RMSE']} eV/\u00c5\nMAE: {metrics[i]['Force_MAE']} eV/\u00c5",
                      transform=ax_force.transAxes, fontsize=10, fontweight='bold',
                      bbox=dict(facecolor='white', alpha=0.8))

    # Adjust layout and save
    plt.tight_layout()
    output_file = os.path.join(output_dir, "parity_plots_side_by_side.png")
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.show()
    print(f"Plots saved at: {output_file}")

# Example usage
directories = [
    './unbiased_biased/attempt_0_0/test_all/',
    './unbiased/attempt_0_0/test_all/'
]
labels = ['Unbiased+Biased', 'Only Unbiased']
metrics = [
    {"Energy_RMSE": "4.71e-04", "Energy_MAE": "2.91e-04", "Force_RMSE": "5.83e-03", "Force_MAE": "3.03e-03"},
    {"Energy_RMSE": "3.84e-02", "Energy_MAE": "1.51e-02", "Force_RMSE": "8.50e-02", "Force_MAE": "2.76e-02"}
]
output_dir = "./test_plots/attempt_0_0"

# Call the function
plot_energy_force_parity(directories, labels, metrics, output_dir)
