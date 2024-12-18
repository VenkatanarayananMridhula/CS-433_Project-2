import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

def plot_bond_lengths(base_path="./bondlength/unbiased_biased", temperatures=["300", "1200"], bond_types=["C-C", "C-H"], exp_bond_lengths=None):
    """
    Plot bond lengths dynamically for given temperatures and bond types, with experimental reference values.

    Parameters:
        base_path (str): Base directory containing bond length data.
        temperatures (list): List of temperatures to analyze.
        bond_types (list): List of bond types to analyze.
        exp_bond_lengths (dict): Experimental bond lengths for reference.
    """
    if exp_bond_lengths is None:
        exp_bond_lengths = {"C-C": 1.339, "C-H": 1.086}

    # File template
    file_template = "{base_path}/{temp}_NVE/{bond_type}_bond_lengths_{temp}_0.out"

    # Read data for all temperatures and bond types
    data = {}
    means = {}
    for temp in temperatures:
        for bond_type in bond_types:
            key = f"{bond_type}_{temp}K"
            file_path = file_template.format(base_path=base_path, temp=temp, bond_type=bond_type.lower().replace("-", ""))
            if os.path.exists(file_path):
                # Read bond length data
                data[key] = pd.read_csv(file_path, delim_whitespace=True, comment='#', names=["Frame", "Bond_Length(Å)"])
                # Calculate mean bond length
                means[key] = data[key]["Bond_Length(Å)"].mean()
            else:
                print(f"File not found: {file_path}")
                data[key] = None

    # Create plots dynamically
    fig, axes = plt.subplots(1, len(temperatures), figsize=(15, 6), sharey=True)

    for i, temp in enumerate(temperatures):
        ax = axes[i]
        for bond_type in bond_types:
            key = f"{bond_type}_{temp}K"
            if data[key] is not None:
                ax.plot(data[key]["Frame"], data[key]["Bond_Length(Å)"], marker='o', linestyle='-', label=f"{bond_type} ({temp} K)", linewidth=1, markersize=3)
                ax.axhline(y=means[key], linestyle='--', linewidth=2, label=f"Mean {bond_type} = {means[key]:.3f} Å")

        # Add experimental reference lines
        for bond_type, exp_value in exp_bond_lengths.items():
            ax.axhline(y=exp_value, color='black', linestyle=':', linewidth=2, label=f"Exp {bond_type} = {exp_value:.3f} Å")

        ax.set_title(f"Bond Lengths at {temp} K")
        ax.set_xlabel("Frame")
        if i == 0:
            ax.set_ylabel("Bond Length (Å)")
        ax.legend()
        ax.grid(True)

    # Adjust layout and save plots
    plt.tight_layout()
    output_path = os.path.join(base_path, "bond_lengths_with_experiment.png")
    plt.savefig(output_path, dpi=300)
    plt.show()

    print(f"Plot saved to {output_path}")

# Example usage
if __name__ == "__main__":
    # Base directory (relative to the script location)
    base_path = os.path.join(os.getcwd(), "bondlength/unbiased_biased")
    temperatures = ["300", "1200"]
    bond_types = ["C-C", "C-H"]
    exp_bond_lengths = {"C-C": 1.339, "C-H": 1.086}

    plot_bond_lengths(base_path=base_path, temperatures=temperatures, bond_types=bond_types, exp_bond_lengths=exp_bond_lengths)
