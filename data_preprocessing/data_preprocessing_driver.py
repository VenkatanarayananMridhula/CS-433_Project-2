import os
import shutil
import sys
import dpdata
import numpy as np
import random
script_dir = "./data_preprocessing.py"
sys.path.append(script_dir)
import data_preprocessing
from data_preprocessing import *



def main():
    # Specify the path to the all_simulations directory
#     all_simulations_dir = "./all_simulations"

#     # Specify the file paths to transfer (relative to each subfolder)
#     files_to_transfer = [
#         "TRAJEC.xyz",
#         "client_cp2k/ETH-forces-1.xyz",
#         "client.out",
#     ]

#     # Step 1: Transfer files to raw_data
#     print("Transferring files to raw_data...")
#     raw_data_dir, refined_data_dir = transfer_training_files(all_simulations_dir, files_to_transfer)
#     raw_data_dir = "./training_data/raw_data"
    refined_data_dir = "./training_data/refined_data"

    # Step 2: Refine energy data and save to refined_data
#     print("Refining energy data...")
    N = 20000  # Total number of snapshots
    output_interval = 20  # Interval at which trajectory outputs are generated
#     refine_cp2k_energy(raw_data_dir, N, output_interval)

    # Step 3: Clean ETH-forces-1.xyz and save to refined_data
#     print("Cleaning ETH-forces-1.xyz...")
    atom_count = 6  # Number of atoms in the system (user-defined)
#     clean_and_transfer_forces(raw_data_dir, refined_data_dir, N, atom_count, output_interval)
    
    # Step 4: Clean TRAJEC.xyz and save to refined_data
#     print("Cleaning TRAJEC.xyz...")
#     clean_and_transfer_trajectory(raw_data_dir, refined_data_dir, output_interval)
    
    # Step 5: Check frame consistency
    print("Checking frame consistency...")
    check_frame_consistency(refined_data_dir)
    
    # Step 6: Generate .xyz files for each subfolder
    print("Generating .xyz files...")
    lattice_params = [12.718, 12.718, 12.718, 90.0, 90.0, 90.0]  # Cubic box dimensions
    atomic_numbers = {"C": 6, "H": 1}  # Atomic number mapping
    xyz_files_dir = generate_xyz_files(refined_data_dir, atom_count, lattice_params, atomic_numbers)

    # Step 7: Split xyz files into train, validation, and test datasets
    split_xyz_files(xyz_files_dir)
    
    #Step 8: Merge all the test files together
    merged_file_path = merge_test_files(xyz_files_dir)
    
    # Step 9: Check for overlaps in the xyz files
    check_frame_overlap(xyz_files_dir)

    # Step 10: Convert .xyz files to DeepMD-ready data
    print("Converting .xyz files to DeepMD-ready data...")
    generate_deepmd_ready_data(refined_data_dir)



    print("Workflow complete.")

if __name__ == "__main__":
    main()