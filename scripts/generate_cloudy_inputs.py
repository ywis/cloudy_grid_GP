#!/usr/bin/env python3
"""
Generate Cloudy (v17.02) input files for a G0-nH PDR model grid.

Grid parameters:
    log G0  = 1.00 to 4.00 (step 0.25 dex)  -- Habing field units
    log nH  = 1.00 to 4.00 (step 0.25 dex)  -- cm^-3

Physics:
    - Plane-parallel, constant-pressure slab
    - Composite radiation field: CMB + Leitherer+1999 starburst SED (age=4 Myr)
    - Metallicity: 12+log(O/H) ~ 8.0 (Z ~ 0.2 Z_sun)
    - Dust: ISM grains (graphite + silicate) + PAHs, scaled to metallicity
    - Stopping criteria: T < 10 K or log N_H = 22 cm^-2

Output:
    - Input files written to ../input_files/
    - One .in file per (G0, nH) combination
    - A master run script (run_grid.sh) for batch execution

Reference:
    Ferland et al. 2017, RMxAA, 53, 385
    Leitherer et al. 1999, ApJS, 123, 3
    Wolfire et al. 2003, ApJ, 587, 278

Author: Generated for the Green Pea H2 manuscript
"""

import os
import numpy as np

# ============================================================
# Grid parameters
# ============================================================
log_G0_min, log_G0_max, log_G0_step = 1.00, 4.00, 0.25
log_nH_min, log_nH_max, log_nH_step = 1.00, 4.00, 0.25

log_G0_arr = np.arange(log_G0_min, log_G0_max + 0.01, log_G0_step)
log_nH_arr = np.arange(log_nH_min, log_nH_max + 0.01, log_nH_step)

# ============================================================
# Physical parameters
# ============================================================
# Metallicity: 12+log(O/H) = 8.0 => Z/Z_sun ~ 0.2
# (using Z_sun: 12+log(O/H)_sun = 8.69, Asplund+2009)
Z_frac = 0.2  # relative to solar

# Starburst SED: Leitherer+1999, age = 4 Myr, Z = 0.004 (closest to 0.2 Z_sun)
# In Cloudy: "table starburst" command

# Stopping criteria
T_stop = 10.0        # K
log_NH_stop = 22.0   # cm^-2

# ============================================================
# Output directory
# ============================================================
outdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'input_files')
os.makedirs(outdir, exist_ok=True)

# ============================================================
# Generate input files
# ============================================================
run_commands = []
n_models = 0

for log_G0 in log_G0_arr:
    for log_nH in log_nH_arr:
        # Model name
        model_name = f"G{log_G0:.2f}_n{log_nH:.2f}"
        fname = os.path.join(outdir, f"{model_name}.in")

        # Convert G0 (Habing) to Cloudy's "intensity" command
        # Habing field: G0 = 1 corresponds to 1.6e-3 erg/s/cm^2 (FUV 6-13.6 eV)
        # Cloudy uses log of intensity in erg/s/cm^2
        # log(flux) = log(G0) + log(1.6e-3) = log(G0) - 2.796
        log_flux = log_G0 + np.log10(1.6e-3)

        # Build Cloudy input
        lines = []
        lines.append(f"title GP_PDR_grid {model_name}")
        lines.append(f"#")
        lines.append(f"# === Radiation field ===")
        lines.append(f"# CMB at z=0")
        lines.append(f"CMB")
        lines.append(f"# Starburst SED: Leitherer+1999, age=4 Myr, Z=0.004")
        lines.append(f"table SED \"starburst99.mod\" age=4.0e6 years")
        lines.append(f"# FUV intensity: log G0 = {log_G0:.2f} Habing")
        lines.append(f"intensity {log_flux:.4f} range 6.0 to 13.6 Ryd")
        lines.append(f"#")
        lines.append(f"# === Gas properties ===")
        lines.append(f"hden {log_nH:.2f} log")
        lines.append(f"constant pressure")
        lines.append(f"#")
        lines.append(f"# === Abundances: scaled to Z/Z_sun = {Z_frac:.2f} ===")
        lines.append(f"abundances planetary nebula, scale={Z_frac:.2f}")
        lines.append(f"#")
        lines.append(f"# === Grains: ISM + PAH, scaled to metallicity ===")
        lines.append(f"grains ISM {np.log10(Z_frac):.3f} log")
        lines.append(f"grains PAH {np.log10(Z_frac):.3f} log")
        lines.append(f"#")
        lines.append(f"# === Stopping criteria ===")
        lines.append(f"stop temperature {T_stop:.1f}K")
        lines.append(f"stop column density {log_NH_stop:.1f} log")
        lines.append(f"#")
        lines.append(f"# === Output ===")
        lines.append(f"set save prefix \"{model_name}\"")
        lines.append(f"save overview \".ovr\" last")
        lines.append(f"save continuum \".con\" last units microns")
        lines.append(f"save lines, emissivity \".ems\" last")
        lines.append(f"save lines list \".lin\" \"lines.dat\" last")
        lines.append(f"save PDR \".pdr\" last")
        lines.append(f"save heating \".het\" last")
        lines.append(f"save cooling \".col\" last")
        lines.append(f"#")

        with open(fname, 'w') as f:
            f.write('\n'.join(lines) + '\n')

        run_commands.append(f"cloudy.exe -r {model_name}")
        n_models += 1

# ============================================================
# Write the line list file (lines.dat)
# ============================================================
lines_dat = os.path.join(outdir, "lines.dat")
line_list = [
    "# Key emission lines for PDR analysis",
    "# Format: label wavelength",
    "C  2 157.636m",
    "O  1 63.1679m",
    "O  1 145.525m",
    "O  3 88.3323m",
    "O  3 5006.84A",
    "O  3 4958.91A",
    "O  2 3726.03A",
    "O  2 3728.81A",
    "N  2 6583.45A",
    "S  2 6716.44A",
    "S  2 6730.82A",
    "H  1 6562.81A",
    "H  1 4861.33A",
    "TOTL 4861.33A",
    "end of lines",
]
with open(lines_dat, 'w') as f:
    f.write('\n'.join(line_list) + '\n')

# ============================================================
# Write batch run script
# ============================================================
run_script = os.path.join(outdir, "run_grid.sh")
with open(run_script, 'w') as f:
    f.write("#!/bin/bash\n")
    f.write("# Batch run script for Cloudy PDR grid\n")
    f.write(f"# Total models: {n_models}\n")
    f.write("# Usage: cd input_files && bash run_grid.sh\n")
    f.write("# Requires: Cloudy v17.02 installed and 'cloudy.exe' in PATH\n\n")
    f.write("NPROC=${1:-4}  # Number of parallel processes (default: 4)\n\n")
    f.write("echo \"Running ${NPROC} parallel Cloudy processes...\"\n")
    f.write("echo \"Total models: " + str(n_models) + "\"\n\n")
    f.write("run_model() {\n")
    f.write("    local model=$1\n")
    f.write("    echo \"Running $model ...\"\n")
    f.write("    cloudy.exe -r $model\n")
    f.write("}\n")
    f.write("export -f run_model\n\n")
    f.write("# Generate model list and run in parallel\n")
    f.write("ls *.in | sed 's/.in$//' | xargs -P $NPROC -I {} bash -c 'run_model \"{}\"'\n\n")
    f.write("echo \"Grid complete.\"\n")

os.chmod(run_script, 0o755)

print(f"Generated {n_models} Cloudy input files in {outdir}")
print(f"Grid: log G0 = {log_G0_min}-{log_G0_max} ({len(log_G0_arr)} values)")
print(f"Grid: log nH = {log_nH_min}-{log_nH_max} ({len(log_nH_arr)} values)")
print(f"Line list: {lines_dat}")
print(f"Run script: {run_script}")
