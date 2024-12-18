# Define the atom indices for the dihedral (adjusted for VMD's 0-based indexing)
# Update these indices based on your VMD atom selection
set atom1 1  ;
set atom2 0  ;
set atom3 4 ;
set atom4 2  ;

# Debugging: Print the atom indices to ensure they are correct
puts "Atom indices for dihedral calculation: $atom1 $atom2 $atom3 $atom4"

# Output file to save dihedral angles
set outfile "dihedral_angles.out"
set fp [open $outfile w]
puts $fp "# Frame Dihedral_Angle(deg)"

# Get the number of frames in the trajectory
set num_frames [molinfo top get numframes]
puts "Number of frames: $num_frames"

# Loop over all frames
for {set frame 0} {$frame < $num_frames} {incr frame} {
    # Go to the current frame
    animate goto $frame

    # Calculate the dihedral angle in degrees
    # The atom indices must be passed as a list
    set angle [measure dihed [list $atom1 $atom2 $atom3 $atom4]]

    # Write the frame number and angle to the file
    puts $fp "$frame $angle"
}

# Close the output file
close $fp
puts "Dihedral angles written to $outfile"
