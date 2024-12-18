# Define atom indices for bond calculations (adjust based on your VMD atom selection)
set cc_atom1 0 ;# First atom for C-C bond
set cc_atom2 1 ;# Second atom for C-C bond

set ch_atom1 1 ;# First atom for C-H bond
set ch_atom2 3 ;# Second atom for C-H bond

# Output files to save bond lengths
set cc_outfile "cc_bond_lengths.out"
set ch_outfile "ch_bond_lengths.out"

set cc_fp [open $cc_outfile w]
set ch_fp [open $ch_outfile w]

# Write headers to output files
puts $cc_fp "# Frame C-C_Bond_Length(Å)"
puts $ch_fp "# Frame C-H_Bond_Length(Å)"

# Get the number of frames in the trajectory
set num_frames [molinfo top get numframes]
puts "Number of frames: $num_frames"

# Loop over all frames
for {set frame 0} {$frame < $num_frames} {incr frame} {
    # Go to the current frame
    animate goto $frame

    # Calculate C-C bond length
    set cc_length [measure bond [list $cc_atom1 $cc_atom2]]

    # Calculate C-H bond length
    set ch_length [measure bond [list $ch_atom1 $ch_atom2]]

    # Write frame number and bond lengths to respective files
    puts $cc_fp "$frame $cc_length"
    puts $ch_fp "$frame $ch_length"
}

# Close the output files
close $cc_fp
close $ch_fp

puts "C-C bond lengths written to $cc_outfile"
puts "C-H bond lengths written to $ch_outfile"

