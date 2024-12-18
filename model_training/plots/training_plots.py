import numpy as np
import matplotlib.pyplot as plt
import os

def load_data(filepath):
    """Load the lcurve.out file data."""
    return np.genfromtxt(filepath, names=True)

def plot_training_curves(data, title, output_dir):
    """
    Plot RMSE subplots for forces, energy, and combined loss.
    
    Args:
        data (ndarray): Data loaded from lcurve.out.
        title (str): Title of the entire figure.
        output_dir (str): Directory where the plot will be saved.
    """
    # Define column groupings
    column_groups = [
        (['step', 'rmse_f_val', 'rmse_f_trn'], "RMSE: Forces"),
        (['step', 'rmse_e_val', 'rmse_e_trn'], "RMSE: Energy"),
        (['step', 'rmse_val', 'rmse_trn'], "RMSE: Combined")
    ]

    # Plot configuration
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))  # 1 row, 3 columns
    fig.suptitle(title, fontsize=14)

    for ax, (columns, subplot_title) in zip(axes, column_groups):
        step, val_metric, trn_metric = columns
        ax.plot(data[step], data[val_metric], label=f'{val_metric}')
        ax.plot(data[step], data[trn_metric], label=f'{trn_metric}')
        ax.set_title(subplot_title)
        ax.set_xlabel('Step')
        ax.set_ylabel('Loss')
        ax.set_xscale('symlog')
        ax.set_yscale('log')
        ax.grid()
        ax.legend()

    # Save the plot
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{title.replace(' ', '_')}.png")
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig(output_path)
    plt.close()
    print(f"Plot saved at: {output_path}")
    
    

def main():
    # Base directory paths
    base_dir = "../../"  # Relative to the current working directory (plots/)
    model_training_dir = os.path.join(base_dir, "model_training")

    # File paths
    files = {
        "Unbiased+Biased Training": os.path.join(model_training_dir, "unbiased_biased/attempt_0_0/lcurve.out"),
        "Only Unbiased Training": os.path.join(model_training_dir, "unbiased/attempt_0_0/lcurve.out")
    }

    # Output directories
    output_dirs = {
        "Unbiased+Biased Training": os.path.join("unbiased_biased/attempt_0_0"),
        "Only Unbiased Training": os.path.join("unbiased/attempt_0_0")
    }

    # Process each file
    for title, filepath in files.items():
        if os.path.exists(filepath):
            data = load_data(filepath)  
            output_dir = os.path.join(os.getcwd(), output_dirs[title])
            os.makedirs(output_dir, exist_ok=True)  # Create output directories if they don't exist
            plot_training_curves(data, title, output_dir)  
        else:
            print(f"File not found: {filepath}")

if __name__ == "__main__":
    main()
