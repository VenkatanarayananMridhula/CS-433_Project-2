import os
import shutil
import dpdata
import random
import numpy as np
                    
                    
                    
def transfer_training_files(all_simulations_dir, files_to_transfer):
    """
    Transfers specific files from simulation subfolders in `all_simulations` to the `raw_data` directory under `training_data`.
    Skips subfolders if the files have already been copied.

    Args:
        all_simulations_dir (str): Path to the `all_simulations` directory containing subfolders.
        files_to_transfer (list of str): List of file paths relative to each subfolder to be transferred.

    Returns:
        str: Path to the created `raw_data` directory.
        str: Path to the created `refined_data` directory.
    """
    # Create training_data directory
    training_data_dir = os.path.join(os.path.dirname(all_simulations_dir), "training_data")
    raw_data_dir = os.path.join(training_data_dir, "raw_data")
    refined_data_dir = os.path.join(training_data_dir, "refined_data")

    # Ensure directories exist
    os.makedirs(raw_data_dir, exist_ok=True)
    os.makedirs(refined_data_dir, exist_ok=True)

    # Loop through each subfolder in the all_simulations directory
    for subfolder in os.listdir(all_simulations_dir):
        subfolder_path = os.path.join(all_simulations_dir, subfolder)

        if os.path.isdir(subfolder_path):
            # Create a corresponding subfolder in raw_data
            raw_subfolder_path = os.path.join(raw_data_dir, subfolder)
            os.makedirs(raw_subfolder_path, exist_ok=True)

            # Check if all files are already copied
            all_files_exist = all(
                os.path.exists(os.path.join(raw_subfolder_path, os.path.basename(file)))
                for file in files_to_transfer
            )
            if all_files_exist:
                print(f"All files for {subfolder} already exist in raw_data. Skipping transfer.")
                continue

            # Copy specified files
            for relative_path in files_to_transfer:
                file_path = os.path.join(subfolder_path, relative_path)
                if os.path.exists(file_path):
                    shutil.copy(file_path, raw_subfolder_path)
                    print(f"Copied {file_path} to {raw_subfolder_path}")
                else:
                    print(f"File not found: {file_path}")

    print(f"Raw data successfully transferred to {raw_data_dir}")
    return raw_data_dir, refined_data_dir



def refine_cp2k_energy(raw_data_dir, N, output_interval):
    """
    Refines the energy values from `client.out` files in the `raw_data` directory and transfers cleaned data
    to the `refined_data` directory under `training_data`. Skips subfolders if the cleaned file already exists.

    Args:
        raw_data_dir (str): Path to the raw_data directory containing subfolders.
        N (int): Total number of snapshots.
        output_interval (int): Interval at which trajectory outputs are generated.

    Returns:
        str: Path to the refined data directory.
    """
    # Conversion factor from Hartree to eV
    HARTREE_TO_EV = 27.211386245988

    # Create refined_data directory internally
    refined_data_dir = os.path.join(os.path.dirname(raw_data_dir), "refined_data")
    os.makedirs(refined_data_dir, exist_ok=True)

    for subfolder in os.listdir(raw_data_dir):
        subfolder_path = os.path.join(raw_data_dir, subfolder)

        if os.path.isdir(subfolder_path):
            # Define paths
            client_out_file = os.path.join(subfolder_path, "client.out")
            refined_subfolder_path = os.path.join(refined_data_dir, subfolder)
            os.makedirs(refined_subfolder_path, exist_ok=True)

            # Check if the cleaned file already exists
            cp2k_energy_cleaned_file = os.path.join(refined_subfolder_path, "CP2K_ENERGY_cleaned")
            if os.path.exists(cp2k_energy_cleaned_file):
                print(f"Cleaned energy file already exists for {subfolder}. Skipping refinement.")
                continue

            # Temporary file in raw_data
            cp2k_energy_file = os.path.join(subfolder_path, "CP2K_ENERGY")

            # Step 1: Extract total energies from client.out
            os.system(f"grep -i 'Total energy:' {client_out_file} > {cp2k_energy_file}")

            # Step 2: Validate energy count
            with open(cp2k_energy_file, "r") as f:
                lines = f.readlines()

            expected_energies = N + 2
            if len(lines) != expected_energies:
                raise ValueError(f"Energy count mismatch in {subfolder}: Found {len(lines)}, expected {expected_energies}.")

            # Step 3: Refine energies
            energy_values = [float(line.split(":")[1].strip()) for line in lines if "Total energy:" in line]
            
            # Convert energies to eV
            energy_values_in_ev = [value * HARTREE_TO_EV for value in energy_values]
            
            selected_values = energy_values_in_ev[2::output_interval]

            # Write cleaned energy values to the cleaned file
            with open(cp2k_energy_cleaned_file, "w") as f:
                for value in selected_values:
                    f.write(f"{value}\n")

            print(f"Cleaned energy values saved to {cp2k_energy_cleaned_file}.")

            # Step 4: Remove the temporary CP2K_ENERGY file
            os.remove(cp2k_energy_file)
            print(f"Removed temporary file {cp2k_energy_file}.")

    print(f"Refined data successfully saved in {refined_data_dir}")
    return refined_data_dir


def clean_and_transfer_forces(raw_data_dir, refined_data_dir, N, atom_count, output_interval):
    """
    Cleans the ETH-forces-1.xyz file in the raw_data directory, validates it, and saves the cleaned file 
    as forces_cleaned.xyz in the refined_data directory. Skips processing if the cleaned file already exists.
    Converts forces in columns X, Y, and Z from Hartree/Bohr to eV/Å.

    Args:
        raw_data_dir (str): Path to the raw_data directory containing subfolders.
        refined_data_dir (str): Path to the refined_data directory where cleaned files will be stored.
        N (int): Total number of snapshots.
        atom_count (int): Number of atoms in the system.
        output_interval (int): Interval for selecting frames (e.g., every 20th frame).

    Returns:
        None
    """
    # Conversion factor from Hartree/Bohr to eV/Å
    conversion_factor = 51.4221


    # Ensure refined_data directory exists
    os.makedirs(refined_data_dir, exist_ok=True)

    for subfolder in os.listdir(raw_data_dir):
        subfolder_path = os.path.join(raw_data_dir, subfolder)

        if os.path.isdir(subfolder_path):
            # Define paths
            input_file = os.path.join(subfolder_path, "ETH-forces-1.xyz")
            refined_subfolder_path = os.path.join(refined_data_dir, subfolder)
            os.makedirs(refined_subfolder_path, exist_ok=True)
            temp_output_file = os.path.join(refined_subfolder_path, "forces_temp.xyz")
            final_output_file = os.path.join(refined_subfolder_path, "forces_cleaned.xyz")

            # Skip processing if the cleaned file already exists
            if os.path.exists(final_output_file):
                print(f"Cleaned forces file already exists for {subfolder}. Skipping cleaning.")
                continue

            # Step 1: Validate ETH-forces-1.xyz
            element_count = os.popen(f"grep -c 'Element' {input_file}").read().strip()
            if int(element_count) != N + 1:
                raise ValueError(f"Validation failed for {input_file}: Found {element_count} entries, expected {N + 1}.")

            print(f"Validation passed for {input_file}: Found {element_count} entries.")

            # Step 2: Clean and process the file
            # First cleaning operation: Select every 20th frame starting from the second frame
            start_frame = 1
            frame_step = output_interval
            with open(input_file, "r") as infile, open(temp_output_file, "w") as outfile:
                lines = infile.readlines()
                current_frame = 0
                inside_frame = False
                frame_lines = []

                for line in lines:
                    if "ATOMIC FORCES in [a.u.]" in line:
                        if inside_frame:
                            if current_frame >= start_frame and (current_frame - start_frame) % frame_step == 0:
                                outfile.writelines(frame_lines)
                            current_frame += 1
                            frame_lines = []
                        inside_frame = True
                        frame_lines.append(line)
                    elif inside_frame:
                        frame_lines.append(line)

                # Write the last frame if applicable
                if inside_frame and current_frame >= start_frame and (current_frame - start_frame) % frame_step == 0:
                    outfile.writelines(frame_lines)

            print(f"Intermediate file written to {temp_output_file}.")

            # Second cleaning operation: Fix frame structure and convert forces
            frame_number = 1  # Initial frame number
            with open(temp_output_file, "r") as infile, open(final_output_file, "w") as outfile:
                lines = infile.readlines()
                frame_data = []

                for line in lines:
                    if "ATOMIC FORCES in [a.u.]" in line:
                        if frame_data:
                            outfile.write(f"{atom_count}\n# Frame {frame_number}\n")
                            outfile.writelines(frame_data)
                            frame_data = []
                            frame_number += output_interval  # Increment frame number by 20
                    elif "SUM OF ATOMIC FORCES" in line or line.strip() == "":
                        continue
                    else:
                        # Perform unit conversion for X, Y, Z columns
                        parts = line.split()
                        if len(parts) == 6:  # Check if the line contains force data
                            try:
                                x_force = float(parts[3]) * conversion_factor
                                y_force = float(parts[4]) * conversion_factor
                                z_force = float(parts[5]) * conversion_factor
#                                 Reconstruct the line with converted forces
#                                 parts[3] = f"{x_force:.8f}"
#                                 parts[4] = f"{y_force:.8f}"
#                                 parts[5] = f"{z_force:.8f}"
#                                 line = " ".join(parts) + "\n"
                                line = f"{parts[0]:>3} {parts[1]:>3} {parts[2]:>3} {x_force:>15.8f} {y_force:>15.8f} {z_force:>15.8f}\n"
                                  
                            except ValueError:
                                pass
                        frame_data.append(line)

                # Write the last frame if it exists
                if frame_data:
                    outfile.write(f"{atom_count}\n# Frame {frame_number}\n")
                    outfile.writelines(frame_data)

            # Remove temporary file
            os.remove(temp_output_file)

            print(f"Cleaned forces file saved to {final_output_file}.")





            
def clean_and_transfer_trajectory(raw_data_dir, refined_data_dir, output_interval):
    """
    Cleans the TRAJEC.xyz file in the raw_data directory and saves the cleaned file
    as TRAJEC_cleaned.xyz in the refined_data directory. Skips processing if the
    cleaned file already exists.

    Args:
        raw_data_dir (str): Path to the raw_data directory containing subfolders.
        refined_data_dir (str): Path to the refined_data directory where cleaned files will be stored.
        output_interval (int): Interval for selecting frames (e.g., every 20th frame).

    Returns:
        None
    """
    # Ensure refined_data directory exists
    os.makedirs(refined_data_dir, exist_ok=True)

    for subfolder in os.listdir(raw_data_dir):
        subfolder_path = os.path.join(raw_data_dir, subfolder)

        if os.path.isdir(subfolder_path):
            # Define paths
            input_file = os.path.join(subfolder_path, "TRAJEC.xyz")
            refined_subfolder_path = os.path.join(refined_data_dir, subfolder)
            os.makedirs(refined_subfolder_path, exist_ok=True)
            output_file = os.path.join(refined_subfolder_path, "TRAJEC_cleaned.xyz")

            # Skip processing if the cleaned file already exists
            if os.path.exists(output_file):
                print(f"Cleaned trajectory file already exists for {subfolder}. Skipping cleaning.")
                continue

            # Step 1: Clean the TRAJEC.xyz file
            try:
                with open(input_file, "r") as infile, open(output_file, "w") as outfile:
                    lines = infile.readlines()  # Read all lines from the file
                    frame_count = 0  # Counter for frames
                    step = 1  # Start the step at 1

                    for line in lines:
                        stripped_line = line.strip()

                        if stripped_line.isdigit() and int(stripped_line) == 6:  # Atom count line
                            # Write atom count to output file
                            outfile.write("6\n")
                            frame_count += 1
                            # Add step information
                            outfile.write(f"Step {step}\n")
                            step += output_interval # Increment step by 20
                        elif stripped_line.startswith("C") or stripped_line.startswith("H"):  # Atom data
                            # Write atom information
                            outfile.write(line)

                    print(f"Cleaned trajectory saved to {output_file} with {frame_count} frames.")
            except FileNotFoundError:
                print(f"TRAJEC.xyz file not found for {subfolder}. Skipping cleaning.")

def check_frame_consistency(refined_data_dir):
    """
    Checks if the number of frames in CP2K_ENERGY_cleaned, TRAJEC_cleaned.xyz, 
    and forces_cleaned.xyz are consistent across all subfolders in refined_data.

    Args:
        refined_data_dir (str): Path to the refined_data directory containing subfolders.

    Returns:
        None
    """
    for subfolder in os.listdir(refined_data_dir):
        subfolder_path = os.path.join(refined_data_dir, subfolder)

        if os.path.isdir(subfolder_path):
            # Define file paths
            energy_file = os.path.join(subfolder_path, "CP2K_ENERGY_cleaned")
            trajectory_file = os.path.join(subfolder_path, "TRAJEC_cleaned.xyz")
            forces_file = os.path.join(subfolder_path, "forces_cleaned.xyz")

            # Check if all files exist
            if not (os.path.exists(energy_file) and os.path.exists(trajectory_file) and os.path.exists(forces_file)):
                print(f"One or more required files are missing in {subfolder}. Skipping consistency check.")
                continue

            try:
                # Count lines in each file
                with open(energy_file, "r") as f:
                    energy_frames = sum(1 for _ in f)  # Number of lines in energy file

                with open(trajectory_file, "r") as f:
                    trajectory_steps = sum(1 for line in f if "Step" in line)  # Count "Step" occurrences

                with open(forces_file, "r") as f:
                    forces_elements = sum(1 for line in f if "Element" in line)  # Count "Element" occurrences

                # Compare counts
                if energy_frames == trajectory_steps == forces_elements:
                    print(f"Frame counts are consistent in {subfolder}: {energy_frames} frames.")
                else:
                    print(f"Inconsistency in {subfolder}:")
                    print(f"  CP2K_ENERGY_cleaned: {energy_frames} frames")
                    print(f"  TRAJEC_cleaned.xyz: {trajectory_steps} frames")
                    print(f"  forces_cleaned.xyz: {forces_elements} frames")
            except Exception as e:
                print(f"Error processing files in {subfolder}: {e}")
                

def generate_xyz_files(refined_data_dir, atom_count, lattice_params, atomic_numbers):
    """
    Generates .xyz files for each subfolder in refined_data and saves them in subfolders under the xyz_files directory.

    Args:
        refined_data_dir (str): Path to the refined_data directory containing subfolders.
        atom_count (int): Number of atoms in the system.
        lattice_params (list): Lattice parameters [a, b, c, alpha, beta, gamma].
        atomic_numbers (dict): Mapping of atom types to their atomic numbers.

    Returns:
        str: Path to the xyz_files directory.
    """
    # Create xyz_files directory internally
    xyz_files_dir = os.path.join(os.path.dirname(refined_data_dir), "xyz_files")
    os.makedirs(xyz_files_dir, exist_ok=True)

    for subfolder in os.listdir(refined_data_dir):
        subfolder_path = os.path.join(refined_data_dir, subfolder)

        if os.path.isdir(subfolder_path):
            # Create a subfolder in xyz_files for this system
            system_xyz_dir = os.path.join(xyz_files_dir, subfolder)
            os.makedirs(system_xyz_dir, exist_ok=True)

            # Define file paths
            trajec_file = os.path.join(subfolder_path, "TRAJEC_cleaned.xyz")
            energy_file = os.path.join(subfolder_path, "CP2K_ENERGY_cleaned")
            forces_file = os.path.join(subfolder_path, "forces_cleaned.xyz")
            output_xyz_file = os.path.join(system_xyz_dir, f"{subfolder}.xyz")

            # Check if all required files exist
            if not (os.path.exists(trajec_file) and os.path.exists(energy_file) and os.path.exists(forces_file)):
                print(f"Required files missing for {subfolder}. Skipping .xyz generation.")
                continue

            # Skip processing if the .xyz file already exists
            if os.path.exists(output_xyz_file):
                print(f"{output_xyz_file} already exists. Skipping generation.")
                continue

            try:
                # Read energies
                with open(energy_file, "r") as f:
                    energies = [float(line.strip()) for line in f.readlines()]

                # Read atomic positions from the trajectory file
                with open(trajec_file, "r") as f:
                    trajec_lines = f.readlines()

                # Read and preprocess forces
                forces = []
                with open(forces_file, "r") as f:
                    lines = f.readlines()
                    frame_forces = []
                    skip_next_lines = 0
                    for line in lines:
                        if line.strip() == str(atom_count):  # Start of a new frame
                            if frame_forces:  # Append the previous frame's forces
                                forces.append(frame_forces)
                                frame_forces = []
                            skip_next_lines = 2  # Skip the next two lines (metadata/header)
                            continue
                        if skip_next_lines > 0:  # Skip metadata lines
                            skip_next_lines -= 1
                            continue
                        # Process force lines
                        parts = line.split()
                        if len(parts) >= 6:  # Ensure valid line with enough columns
                            fx, fy, fz = map(float, parts[-3:])  # Extract last three columns
                            frame_forces.append([fx, fy, fz])  # Add forces to the current frame
                    if frame_forces:  # Add the last frame
                        forces.append(frame_forces)

                # Prepare the output .xyz file
                with open(output_xyz_file, "w") as output_file:
                    trajec_index = 0
                    frame_counter = 0

                    while trajec_index < len(trajec_lines):
                        if trajec_lines[trajec_index].startswith(str(atom_count)):
                            # Start of a new frame in trajectory
                            frame_counter += 1
                            energy = energies[frame_counter - 1]  # Energy for the current frame
                            frame_forces = forces[frame_counter - 1]  # Forces for the current frame

                            # Skip the "Step X" line
                            trajec_index += 2

                            # Extract positions for the current frame
                            positions = trajec_lines[trajec_index:trajec_index + atom_count]
                            trajec_index += atom_count

                            # Write the number of atoms
                            output_file.write(f"{atom_count}\n")

                            # Write metadata with lattice parameters, energy, and properties
                            output_file.write(
                                f'energy={energy:.6f} '
                                f'Lattice="{lattice_params[0]} 0.0 0.0 0.0 {lattice_params[1]} 0.0 0.0 0.0 {lattice_params[2]}" '
                                f'Properties=species:S:1:pos:R:3:Z:I:1:force:R:3\n'
                            )

                            # Write atomic positions with atomic numbers and forces
                            for pos_line, force_vector in zip(positions, frame_forces):
                                pos_elements = pos_line.split()
                                atom_type = pos_elements[0]
                                x, y, z = pos_elements[1:4]
                                fx, fy, fz = force_vector
                                atomic_number = atomic_numbers[atom_type]
                                output_file.write(f"{atom_type} {x} {y} {z} {atomic_number} {fx:.8f} {fy:.8f} {fz:.8f}\n")

                print(f"{output_xyz_file} generated successfully.")
            except Exception as e:
                print(f"Error processing {subfolder}: {e}")

    return xyz_files_dir  # Return the path to the xyz_files directory

def split_xyz_files(xyz_files_dir, train_ratio=0.7, val_ratio=0.2, test_ratio=0.1):
    """
    Splits each .xyz file in the xyz_files directory into train, validation, and test datasets.

    Args:
        xyz_files_dir (str): Path to the directory containing subfolders with .xyz files.
        train_ratio (float): Ratio of frames to include in the training set.
        val_ratio (float): Ratio of frames to include in the validation set.
        test_ratio (float): Ratio of frames to include in the testing set.

    Returns:
        None
    """
    for subfolder in os.listdir(xyz_files_dir):
        subfolder_path = os.path.join(xyz_files_dir, subfolder)

        if os.path.isdir(subfolder_path):
            for xyz_file in os.listdir(subfolder_path):
                if xyz_file.endswith(".xyz"):
                    # Skip already processed files
                    if "_train" in xyz_file or "_val" in xyz_file or "_test" in xyz_file:
                        print(f"Skipping already processed file: {xyz_file}")
                        continue
                    input_xyz_file = os.path.join(subfolder_path, xyz_file)
                    condition_name = xyz_file.replace(".xyz", "")

                    # Output file paths
                    train_file = os.path.join(subfolder_path, f"{condition_name}_train.xyz")
                    val_file = os.path.join(subfolder_path, f"{condition_name}_val.xyz")
                    test_file = os.path.join(subfolder_path, f"{condition_name}_test.xyz")

                    try:
                        # Read the .xyz file and identify frames
                        with open(input_xyz_file, "r") as f:
                            lines = f.readlines()

                        # Split frames into train, val, and test
                        frames = []
                        frame = []
                        for line in lines:
                            frame.append(line)
                            if len(frame) >= int(frame[0].strip()) + 2:  # Frame complete
                                frames.append(frame)
                                frame = []

                        random.shuffle(frames)

                        # Compute sizes
                        train_size = int(len(frames) * train_ratio)
                        val_size = int(len(frames) * val_ratio)

                        train_frames = frames[:train_size]
                        val_frames = frames[train_size:train_size + val_size]
                        test_frames = frames[train_size + val_size:]

                        def write_to_file(path, frames):
                            with open(path, "w") as f:
                                for frame in frames:
                                    f.writelines(frame)

                        write_to_file(train_file, train_frames)
                        write_to_file(val_file, val_frames)
                        write_to_file(test_file, test_frames)

                        print(f"Processed: {xyz_file}")

                    except Exception as e:
                        print(f"Error processing {xyz_file}: {e}")
                        
                        


def merge_test_files(xyz_files_dir, output_file_name="merged_test.xyz"):
    """
    Merges all files containing the keyword "test.xyz" from subfolders into a single file in the main directory.

    Args:
        xyz_files_dir (str): Path to the main directory containing subfolders with test.xyz files.
        output_file_name (str): Name of the merged output file to be saved in the main directory.

    Returns:
        str: Path to the merged_test.xyz file.
    """
    merged_file_path = os.path.join(xyz_files_dir, output_file_name)

    with open(merged_file_path, "w") as merged_file:
        for subfolder in os.listdir(xyz_files_dir):
            subfolder_path = os.path.join(xyz_files_dir, subfolder)

            if os.path.isdir(subfolder_path):
                for file_name in os.listdir(subfolder_path):
                    if "test.xyz" in file_name:
                        file_path = os.path.join(subfolder_path, file_name)
                        
                        try:
                            # Read and append content to the merged file
                            with open(file_path, "r") as f:
                                lines = f.readlines()
                                merged_file.writelines(lines)
                                merged_file.write("\n")  # Add a blank line between files for clarity
                            
                            print(f"Merged: {file_path}")

                        except Exception as e:
                            print(f"Error reading file {file_path}: {e}")

    print(f"Merged test files saved to: {merged_file_path}")
    return merged_file_path


def check_frame_overlap(xyz_files_dir):
    """
    Checks for overlap of frames between train, validation, and test .xyz files for each condition
    and verifies that the total frames in all splits match the primary .xyz file.

    Args:
        xyz_files_dir (str): Path to the directory containing subfolders with .xyz files.

    Returns:
        None
    """
    for subfolder in os.listdir(xyz_files_dir):
        subfolder_path = os.path.join(xyz_files_dir, subfolder)

        if os.path.isdir(subfolder_path):
            # Locate the primary, train, val, and test files
            primary_file, train_file, val_file, test_file = None, None, None, None
            for xyz_file in os.listdir(subfolder_path):
                if xyz_file.endswith(".xyz") and not any(ext in xyz_file for ext in ["_train", "_val", "_test"]):
                    primary_file = os.path.join(subfolder_path, xyz_file)
                elif xyz_file.endswith("_train.xyz"):
                    train_file = os.path.join(subfolder_path, xyz_file)
                elif xyz_file.endswith("_val.xyz"):
                    val_file = os.path.join(subfolder_path, xyz_file)
                elif xyz_file.endswith("_test.xyz"):
                    test_file = os.path.join(subfolder_path, xyz_file)

            # Ensure all files exist
            if not (primary_file and train_file and val_file and test_file):
                print(f"One or more files (primary, train, val, test) are missing in {subfolder}. Skipping overlap check.")
                continue

            try:
                # Extract frames from each file
                def extract_frames(file_path):
                    frames = set()
                    with open(file_path, "r") as f:
                        lines = f.readlines()
                        frame = []
                        for line in lines:
                            frame.append(line.strip())
                            if len(frame) >= int(frame[0]) + 2:  # Complete frame
                                frames.add("".join(frame))  # Add as a single string
                                frame = []
                    return frames

                primary_frames = extract_frames(primary_file)
                train_frames = extract_frames(train_file)
                val_frames = extract_frames(val_file)
                test_frames = extract_frames(test_file)

                # Check for overlaps
                overlap_train_val = train_frames & val_frames
                overlap_train_test = train_frames & test_frames
                overlap_val_test = val_frames & test_frames

                # Check for total frame count consistency
                total_split_frames = len(train_frames) + len(val_frames) + len(test_frames)
                if total_split_frames != len(primary_frames):
                    print(f"Frame mismatch detected for {subfolder}:")
                    print(f"  Primary file: {len(primary_frames)} frames")
                    print(f"  Train+Val+Test: {total_split_frames} frames")
                else:
                    print(f"Frame counts match for {subfolder}. Total frames: {len(primary_frames)}")

                # Print results for overlaps
                if not overlap_train_val and not overlap_train_test and not overlap_val_test:
                    print(f"No overlap detected for {subfolder}.")
                else:
                    print(f"Overlap detected for {subfolder}:")
                    if overlap_train_val:
                        print(f"  Overlap between train and val: {len(overlap_train_val)} frames.")
                    if overlap_train_test:
                        print(f"  Overlap between train and test: {len(overlap_train_test)} frames.")
                    if overlap_val_test:
                        print(f"  Overlap between val and test: {len(overlap_val_test)} frames.")

            except Exception as e:
                print(f"Error checking overlap for {subfolder}: {e}")




def generate_deepmd_ready_data(refined_data_dir):
    """
    Converts .xyz files (train, validation, and test) in the xyz_files directory to DeepMD-ready data
    and saves them in train, val, and test subdirectories under the deePMD_ready directory.
    Additionally, processes a "merged_test.xyz" file if present in the xyz_files directory and saves it in the test directory.

    Args:
        refined_data_dir (str): Path to the refined_data directory.

    Returns:
        None
    """
    # Determine paths for xyz_files and deePMD_ready directories
    training_data_dir = os.path.dirname(refined_data_dir)
    xyz_files_dir = os.path.join(training_data_dir, "xyz_files")
    deepmd_ready_dir = os.path.join(training_data_dir, "deePMD_ready")

    # Ensure train, val, and test directories exist within deePMD_ready
    data_splits = ["train", "val", "test"]
    split_dirs = {split: os.path.join(deepmd_ready_dir, split) for split in data_splits}
    for split_dir in split_dirs.values():
        os.makedirs(split_dir, exist_ok=True)

    # Function to check for NaN values in .npy files
    def check_nan_in_npy(output_dir):
        set_dir = os.path.join(output_dir, "set.000")
        if not os.path.exists(set_dir):
            print(f"Directory {set_dir} does not exist, skipping NaN check.")
            return

        for npy_file in os.listdir(set_dir):
            npy_path = os.path.join(set_dir, npy_file)
            if npy_file.endswith(".npy"):
                data = np.load(npy_path)
                if np.isnan(data).any():
                    print(f"NaN values found in {npy_path}")
                else:
                    print(f"No NaN values in {npy_path}")

    # Process each subfolder in xyz_files
    for condition_folder in os.listdir(xyz_files_dir):
        condition_path = os.path.join(xyz_files_dir, condition_folder)

        if os.path.isdir(condition_path):
            for split in data_splits:
                split_file = os.path.join(condition_path, f"{condition_folder}_{split}.xyz")
                if not os.path.exists(split_file):
                    print(f"File {split_file} not found. Skipping {split} for {condition_folder}.")
                    continue

                # Create output directory for this condition in the respective split directory
                output_deepmd_dir = os.path.join(split_dirs[split], condition_folder)
                if os.path.exists(output_deepmd_dir):
                    print(f"DeepMD-ready data for {condition_folder} ({split}) already exists. Skipping conversion.")
                    continue

                try:
                    # Load the .xyz file as a MultiSystems object
                    multi_systems = dpdata.MultiSystems.from_file(split_file, fmt="quip/gap/xyz")

                    # Extract the first system (key=0 for MultiSystems)
                    system = multi_systems.systems[list(multi_systems.systems.keys())[0]]

                    # Sort atom types for consistency
                    system.sort_atom_types()

                    # Convert the system to DeepMD format and save
                    system.to("deepmd/npy", output_deepmd_dir)

                    print(f"Converted {condition_folder} ({split}) to DeepMD-ready data and saved in: {output_deepmd_dir}")

                    # Check for NaN values in the generated npy files
                    check_nan_in_npy(output_deepmd_dir)

                except Exception as e:
                    print(f"Error processing {condition_folder} ({split}): {e}")

    # Process the merged_test.xyz file if it exists
    merged_test_file = os.path.join(xyz_files_dir, "merged_test.xyz")
    if os.path.exists(merged_test_file):
        try:
            # Path to save the DeepMD-ready data for merged_test
            merged_test_dir = os.path.join(split_dirs["test"], "merged_test")

            # Load the .xyz file as a MultiSystems object
            multi_systems = dpdata.MultiSystems.from_file(merged_test_file, fmt="quip/gap/xyz")

            # Extract the first system (key=0 for MultiSystems)
            system = multi_systems.systems[list(multi_systems.systems.keys())[0]]

            # Sort atom types for consistency
            system.sort_atom_types()

            # Convert the system to DeepMD format and save
            system.to("deepmd/npy", merged_test_dir)

            print(f"Converted merged_test.xyz to DeepMD-ready data and saved in: {merged_test_dir}")

            # Check for NaN values in the generated npy files
            check_nan_in_npy(merged_test_dir)

        except Exception as e:
            print(f"Error processing merged_test.xyz: {e}")
