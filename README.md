# **README: ML Forcefield Development using Classical Dihedral Biases**

## Note for TAs

Due to technical issues with the GitHub Classroom setup, I have placed my codes in my own GitHub repository instead. All relevant files and documentation can be accessed here. If you need any clarification, please feel free to reach out.


## **Introduction**

This project presents a comprehensive **machine learning pipeline** for training, evaluating, and validating forcefields using the **DeepMD-kit** framework. The workflow is designed to process simulation data, train machine-learned forcefields, and rigorously evaluate their performance through testing and auxiliary analysis.

The pipeline is organized into several key components:

- **Data Preprocessing**: Converts raw simulation outputs into DeePMD-compatible data formats.
- **Model Training**: Trains forcefields using DeePMD-kit on unbiased and combined (unbiased + biased) datasets.
- **Model Testing**: Evaluates the trained models through predictions, parity plots, and model deviation analysis.
- **LAMMPS Analysis**: Performs auxiliary tests (thermodynamic properties, bond lengths, and dihedral angles) using the ML-trained forcefields as input for **LAMMPS simulations**.






### Install Project Dependencies

To install all required Python libraries, run:

```bash
pip install -r requirements.txt
```


# **Data Preprocessing Pipeline**

## **Overview**  
The `data_preprocessing` pipeline processes simulation outputs starting from the **`refined_data/`** directory and prepares them into DeePMD-compatible format. The script is designed to be flexible and generalized, capable of handling raw output files from the **MiMiC** framework. However, due to memory constraints on GitHub, we have started the data preprocessing from an intermediate step where only the relevant data, already extracted and cleaned, resides in the **`refined_data/`** directory.

For users who wish to process the raw MiMiC output files from scratch, the pipeline can be adapted by commenting out **Step 1** and **Step 2** in the provided scripts. This allows for the full data processing pipeline, starting from raw simulation outputs, to be used.

---

## **Running the Pipeline**  
To execute the preprocessing pipeline, ensure that the **`refined_data/`** folder (located within the **`training_data/`** directory) is in place, containing the post-processed data for the six systems under study. Run the pipeline using the following command:

```bash
python data_preprocessing_driver.py
```
This command will automatically process the refined data and create three key output directories under **`training_data/`**:

---

### **refined_data/**  
This folder contains system-specific subdirectories, where the post-processed data resides:

- `biased_300K_-0.5FF`
- `biased_300K_-1FF`
- `unbiased_1200K`
- `unbiased_150K`
- `unbiased_300K`
- `unbiased_600K`

Each subdirectory holds the following refined data files:

- **CP2K_ENERGY_cleaned**: Extracted energies (converted to eV).
- **TRAJEC_cleaned.xyz**: Cleaned trajectory file.
- **forces_cleaned.xyz**: Forces converted to eV/Å.

These files are the result of preprocessing steps applied to the raw simulation data. The preprocessing steps can be fully automated through the provided scripts.

---
### **xyz_files/**  
This folder organizes the cleaned data into **QUIP/GAP/XYZ** format. It contains system-specific subdirectories:
- `biased_300K_-0.5FF`
- `biased_300K_-1FF`
- `unbiased_1200K`
- `unbiased_150K`
- `unbiased_300K`
- `unbiased_600K`

Each subdirectory includes:
- **Full dataset**: `*_system.xyz` containing forces, energies, atomic positions, and lattice parameters with metadata.
- **Training dataset**: `*_train.xyz` (70% of data).
- **Validation dataset**: `*_val.xyz` (20% of data).
- **Testing dataset**: `*_test.xyz` (10% of data).

Additionally, a **`merged_test.xyz`** file combines the test datasets from all systems into a single file for evaluation.

---

### **deePMD_ready/**  
This is the final output folder, containing data formatted for DeePMD training and testing. It is divided into three subdirectories:
- **train/**
- **val/**
- **test/**

Each directory contains system-specific subdirectories:
- `biased_300K_-0.5FF`
- `biased_300K_-1FF`
- `unbiased_1200K`
- `unbiased_150K`
- `unbiased_300K`
- `unbiased_600K`

Within each system-specific folder, the **`set.000/`** directory includes the final DeePMD-compatible files:
- **box.npy**: Box dimensions.
- **coord.npy**: Atomic positions.
- **energy.npy**: Energies.
- **force.npy**: Forces.
- **type.raw**: Atomic type information.
- **type_map.raw**: Integer mapping to atomic types.

The **test/** directory also includes a special **`merged_test/`** folder, which aggregates test datasets from all systems into a single dataset for evaluation.

---

# **Model Training**

## **Overview**  
Once the DeePMD-compatible data is prepared in the **data_preprocessing** pipeline, the training process begins. Model training is performed using **DeepMD-kit**, with all configurations, outputs, and results organized within the **model_training/** directory.

---

## **Directory Structure**  
The **model_training/** directory contains the following subdirectories:

### **1. unbiased_biased/**  
This directory is used to train models on a combined dataset of **biased** and **unbiased** simulations. It includes three subdirectories, each representing training runs with different random seeds:
- `attempt_0_0`
- `attempt_0_1`
- `attempt_0_2`

Each subdirectory contains:
- **input.json**: Configuration file for training.
- **input_v2_compat.json**: Compatibility version of the input file (generated during training).
- **lcurve.out**: Records training and validation loss values (primary file for monitoring performance, generated during training).
- **out.json**: Summary of the model's progress (generated during training).
- **checkpoints/**: Directory storing the final model checkpoints (generated by training).

---

### **2. unbiased/**  
This directory is dedicated to models trained **exclusively** on the unbiased dataset. It mirrors the structure of `unbiased_biased/`, containing:
- Subdirectories: `attempt_0_0`, `attempt_0_1`, and `attempt_0_2`.
- Files: 
  - **input.json**
  - **input_v2_compat.json**
  - **lcurve.out**
  - **out.json**
  - **checkpoints/**

---

### **3. plots/**  
This directory automates the visualization of training and validation losses using the **lcurve.out** file. It contains:
- **training_plots.py**: Script to generate loss curve plots.
- Two subdirectories are created upon running the script:
  - **unbiased_biased/**: Contains loss plots for combined datasets.
  - **unbiased/**: Contains loss plots for unbiased datasets.

Each subdirectory includes a folder corresponding to the processed training attempt (default: `attempt_0_0`). The generated plots are:
- **Unbiased+Biased_Training.png**: Loss curves for the combined dataset.
- **Only_Unbiased_Training.png**: Loss curves for the unbiased dataset.

> **Note**: To plot results for other training attempts (e.g., `attempt_0_1`), update the paths in the `main()` function of **training_plots.py**.

---

## **Training the Model**  
To start model training, navigate to the directory containing **input.json** (e.g., `attempt_0_0/`) and run:

```bash
dp train input.json
```

> **Important**: Activate the environment where **DeepMD-kit** is installed before running the command.

---

## **Monitoring the Training Process**

The **lcurve.out** file records the training and validation losses at each epoch, serving as the primary metric for performance monitoring. Note that the version used here, DeePMD-kit v2.2.11, has an unresolved bug that occasionally results in NaN values during training. This issue can be resolved by restarting from the last saved checkpoint. For more details, refer to the [GitHub forum discussion](https://github.com/deepmodeling/deepmd-kit/discussions/4461#discussioncomment-11512503).

### Restarting from the Last Saved Checkpoint

To restart training from the last saved checkpoint, use the following command:

```bash
dp train --restart /path/to/last/checkpoint input.json
```
### **Visualizing Loss Curves**  
To plot the training and validation losses, navigate to the directory and run the **training_plots.py** script:

```bash
python training_plots.py
```

The plots are saved under:
- **unbiased_biased/attempt_0_0/**
- **unbiased/attempt_0_0/**  
By default, the script processes `attempt_0_0`. Update the paths in the script to visualize other training attempts.

---

# **Model Testing**

## **Overview**  
The **model_testing/** directory is used to evaluate the performance of the trained models on unseen test datasets. It includes tools for generating predictions, creating parity plots, and analyzing model deviations.

---

## **Directory Structure**  
The **model_testing/** directory contains the following components:

### **1. unbiased_biased/** and **unbiased/**  
These directories evaluate models trained on **biased+unbiased** and **unbiased-only** datasets, respectively. 

- Each directory contains three subdirectories:
  - `attempt_0_0`
  - `attempt_0_1`
  - `attempt_0_2`
- Files within each subdirectory:
  - **graph.pb**: Frozen model file created from the final training checkpoints.
  - **test_all/**: Subdirectory containing prediction output files:
    - `test_results.e.out`: Energy predictions.
    - `test_results.f.out`: Force predictions.
    - `test_results.e_peratom.out`: Per-atom energy predictions.
    - `test_results.v.out`: Virial predictions (not used if virials were excluded during training).
    - `test_results.v_peratom.out`: Per-atom virial predictions.

---

### **2. test_plots/**  
This directory stores **parity plots** comparing AIMD results with predicted results.

- Plots are saved as **parity_plots_side_by_side.png**.
- Generated using the **test_plots.py** script.

---

### **3. model_deviation/**  
This directory contains output files and comparison plots for **model deviation analysis**.

- Subdirectories:
  - **unbiased_biased/absolute/**: Stores `model_devi_absolute.out` for the unbiased+biased models.
  - **unbiased/absolute/**: Stores `model_devi_absolute.out` for the unbiased models.
- Comparison Plot:
  - Generated using the **model_deviation.py** script.
  - Saved as **model_deviation_comparison.png**.

---

## **Freezing the Model**  
To generate predictions, freeze the last set of weights from the training checkpoints to create a **graph.pb** file. Example:
- The command is to be executed from the **`model_testing/unbiased_biased/attempt_0_0`** directory or the corresponding `attempt_0_X` directory where the **graph.pb** file will be stored.

```bash
dp freeze -c ../../../model_training/unbiased_biased/attempt_0_0/checkpoints/checkpoints-1000000 -o graph.pb
```

---

## **Making Predictions**  
To generate predictions for the test dataset, run the following command from the directory containing **graph.pb**:

```bash
dp test -m graph.pb -s ../../../data_preprocessing/training_data/deePMD_ready/test/merged_test -n 600 --shuffle-test -d test_results
```

This creates prediction output files (`test_results.e.out`, `test_results.f.out`, etc.) in the **test_all/** subdirectory.

---

## **Generating Parity Plots**  
Once predictions are generated, create parity plots by running the **test_plots.py** script:

```bash
python test_plots.py
```

- Default Output Path: **test_plots/attempt_0_0/parity_plots_side_by_side.png**
- Update paths in the script to process other attempts (e.g., `attempt_0_1`).

---

## **Model Deviation Analysis**  
Model deviation analysis compares predictions across multiple frozen models (`graph.pb`) for unbiased+biased and unbiased datasets.

### **1. Unbiased+Biased Models**  
Run the following command from the **model_testing/** directory:

```bash
dp model-devi -m ./unbiased_biased/attempt_0_0/graph.pb \
              ./unbiased_biased/attempt_0_1/graph.pb \
              ./unbiased_biased/attempt_0_2/graph.pb \
              -s ../data_preprocessing/training_data/deePMD_ready/test/merged_test -f 1 \
              -o model_deviation/unbiased_biased/absolute/model_devi_absolute.out
```

### **2. Unbiased Models**  
Run the following command:

```bash
dp model-devi -m ./unbiased/attempt_0_0/graph.pb \
              ./unbiased/attempt_0_1/graph.pb \
              ./unbiased/attempt_0_2/graph.pb \
              -s ../data_preprocessing/training_data/deePMD_ready/test/merged_test -f 1 \
              -o model_deviation/unbiased/absolute/model_devi_absolute.out
```

---

## **Comparison of Model Deviation**  
To compare deviations for **unbiased+biased** and **unbiased** models, run the **model_deviation.py** script:

```bash
python model_deviation.py
```

The comparison plot is saved as **model_deviation_comparison.png** in the **model_deviation/** directory.

---

# LAMMPS Analysis

## Overview
The `LAMMPS_test/` directory contains auxiliary tests performed using ML-trained forcefields. While LAMMPS implementation details are beyond the scope of this project, this section provides an overview of the directory structure, the scripts involved, and the outputs generated.

## Directory Structure
The `LAMMPS_test/` directory contains the following components:

### Scripts:

- **`LAMMPS_analysis_driver.py`**: Main driver script to analyze NVT equilibration simulations and generate thermodynamic property plots.
- **`bondlength_analysis.py`**: Script to analyze bond lengths.
- **`dihedral_analysis.py`**: Script to analyze dihedral angles.
- **`lammps_analysis.py`**: Contains helper functions called by `LAMMPS_analysis_driver.py`.

### Directories:

#### `unbiased_biased/` and `unbiased/`:

These directories contain subdirectories `attempt_0_0/`, where tests are performed at different temperatures: `1200/`, `300/`, and `150/`.

- **`graph.pb`**: The frozen model file (forcefield) generated from the model training of `attempt_0_0`. This file is used to run the LAMMPS simulations.

Each temperature folder has two subdirectories:

- **`equilibration_NVT/`**:

  Runs the NVT equilibration step and includes the following files:

  - `ethylene_NVT<TEMP>.dump`: Trajectory files used to compute dihedral angles and bond lengths.
  - `in.lammps`: LAMMPS input file.
  - `log.lammps`, `out.lmp`: LAMMPS output files.
  - `thermo_data_NVT<TEMP>.out`: Thermodynamic data file.
  - `LAMMPS_analysis/`: Contains thermodynamic property plots generated using `LAMMPS_analysis_driver.py`.

- **`production_NVE/`**:

  Runs 5 independent NVE simulations (`NVE_0` to `NVE_4`) at each temperature. Each subdirectory contains:

  - Trajectory files (`.dump`) and outputs (thermo, log, and out files).

#### `dihedral/`:

##### Scripts and Outputs:

- **`calculate_dihedral.tcl`**: VMD script used to calculate dihedral angles.
- **`unbiased_biased/` and `unbiased/`**:

  Subdirectories for temperatures (`1200_NVE`, `300_NVE`, `150_NVE`) store dihedral angle `.out` files for the 5 NVE runs.

- **`QM/`**: Contains dihedral angle outputs for the QM trajectories at `150 K`, `300 K`, and `1200 K`.
- **`comparison_dihedral_distribution.png`**: Plot generated using `dihedral_analysis.py` to compare dihedral distributions.

#### `bondlength/`:

##### Scripts and Outputs:

- **`calculate_BL.tcl`**: VMD script used to calculate C-C and C-H bond lengths.
- **`unbiased_biased/`**:

  Subdirectories (`1200_NVE`, `300_NVE`) store bond length `.out` files.

- **`bond_lengths_with_experiment.png`**: Plot generated by running `bondlength_analysis.py`.

# References

1. Han Wang, Linfeng Zhang, Jiequn Han, and Weinan E. "DeePMD-kit: A deep learning package for many-body potential energy representation and molecular dynamics." *Comput. Phys. Comm.*, 228:178–184, July 2018. [doi:10.1016/j.cpc.2018.03.016](https://doi.org/10.1016/j.cpc.2018.03.016).

2. Denghui Lu, Han Wang, Mohan Chen, Lin Lin, Roberto Car, Weinan E, Weile Jia, and Linfeng Zhang. "86 PFLOPS Deep Potential Molecular Dynamics simulation of 100 million atoms with ab initio accuracy." *Comput. Phys. Comm.*, 259:107624, 2021. [doi:10.1016/j.cpc.2020.107624](https://doi.org/10.1016/j.cpc.2020.107624).
3. A. P. Thompson, H. M. Aktulga, R. Berger, D. S. Bolintineanu, W. M. Brown, P. S. Crozier, P. J. in 't Veld, A. Kohlmeyer, S. G. Moore, T. D. Nguyen, R. Shan, M. J. Stevens, J. Tranchida, C. Trott, S. J. Plimpton. "LAMMPS - a flexible simulation tool for particle-based materials modeling at the atomic, meso, and continuum scales." *Comp. Phys. Comm.*, 271:10817, 2022. [doi:10.1016/j.cpc.2022.10817](https://doi.org/10.1016/j.cpc.2022.10817).
4. Humphrey, W., Dalke, A. and Schulten, K., "VMD - Visual Molecular Dynamics", *J. Molec. Graphics*, 1996, vol. 14, pp. 33-38.
5. A. Antalík, A. Levy, S. Kvedaraviciūtė, S. K. Johnson, D. Carrasco-Busturia, B. Raghavan, F. Mouvet, A. Acocella, S. Das, V. Gavini, D. Mandelli, E. Ippoliti, S. Meloni, P. Carloni, U. Rothlisberger, and J. M. H. Olsen, “MiMiC: A high-performance framework for multiscale molecular dynamics simulations,” *The Journal of Chemical Physics*, vol. 161, no. 2, p. 022501, 2024.
