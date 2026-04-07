# Cloudy PDR Model Grid for Green Pea Galaxies

This repository contains the Cloudy photoionization model grid used in the paper:

> **Molecular Gas Content of Green Pea Galaxies: Insights from [CII], CO, and HI Observations**

## Overview

We construct a grid of plane-parallel PDR models using [Cloudy](https://gitlab.nublado.org/cloudy/cloudy/-/wikis/home) (version 17.02; Ferland et al. 2017) to constrain the interstellar radiation field intensity (G0) and hydrogen number density (nH) in our sample of Green Pea galaxies. The grid is designed to cross-validate the simplified diagnostic estimates derived from optical emission-line ratios.

## Grid Parameters

| Parameter | Range | Step | Units |
|-----------|-------|------|-------|
| log G0 | 1.00 -- 4.00 | 0.25 dex | Habing field |
| log nH | 1.00 -- 4.00 | 0.25 dex | cm^-3 |

Total number of models: **169** (13 x 13)

## Physical Setup

The models adopt the following physical conditions, chosen to match the properties of Green Pea galaxies:

- **Geometry**: Plane-parallel, constant-pressure slab
- **Radiation field**: Composite of CMB (z = 0) and a starburst SED from Leitherer et al. (1999), with stellar age = 4 Myr
- **Metallicity**: Z/Z_sun = 0.2, corresponding to 12 + log(O/H) ~ 8.0 (Asplund et al. 2009)
- **Dust**: ISM grains (graphite + silicate) and PAHs, with abundances scaled linearly with metallicity
- **Stopping criteria**: Temperature < 10 K or log N_H = 22 cm^-2

## Directory Structure

```
cloudy_grid_GP/
├── README.md                  # This file
├── input_files/               # Cloudy input files (.in)
│   ├── G1.00_n1.00.in        # Model: log G0=1.00, log nH=1.00
│   ├── G1.00_n1.25.in        # Model: log G0=1.00, log nH=1.25
│   ├── ...                    # (169 files total)
│   ├── lines.dat              # Emission line list for output
│   └── run_grid.sh            # Batch execution script
├── scripts/                   # Python processing scripts
│   ├── generate_cloudy_inputs.py   # Generate all .in files
│   ├── parse_cloudy_output.py      # Parse Cloudy output -> CSV
│   └── cross_validate.py           # Cross-validate with diagnostics
└── example_output/            # Example/template output
    └── grid_results.csv       # Template CSV (populated after running Cloudy)
```

## Usage

### 1. Generate Input Files (optional, already provided)

```bash
cd scripts
python generate_cloudy_inputs.py
```

This creates 169 `.in` files in `input_files/`.

### 2. Run the Cloudy Grid

Ensure Cloudy v17.02 is installed and `cloudy.exe` is in your PATH.

```bash
cd input_files
bash run_grid.sh 4    # Run with 4 parallel processes
```

Alternatively, run individual models:

```bash
cloudy.exe -r G2.00_n2.50
```

### 3. Parse Output

After Cloudy completes, extract emission line luminosities:

```bash
cd scripts
python parse_cloudy_output.py --input_dir ../input_files --output ../example_output/grid_results.csv
```

### 4. Cross-Validate

Compare Cloudy predictions with simplified diagnostic estimates:

```bash
cd scripts
python cross_validate.py --grid ../example_output/grid_results.csv \
                         --obs /path/to/G0_nH_results.csv \
                         --output ../example_output/cross_validation.pdf
```

## Key Output Lines

The following emission lines are tracked in the grid output:

| Line | Wavelength | Diagnostic Use |
|------|-----------|----------------|
| [CII] | 157.636 um | PDR cooling, H2 tracer |
| [OI] | 63.168 um | PDR cooling |
| [OI] | 145.525 um | PDR cooling |
| [OIII] | 88.332 um | Ionization parameter |
| [OIII] | 5006.84 A | Ionization parameter |
| [OII] | 3726/3729 A | Ionization parameter |
| [SII] | 6717/6731 A | Electron density |
| H-alpha | 6562.81 A | SFR indicator |
| H-beta | 4861.33 A | Reddening |

## Requirements

- [Cloudy v17.02](https://gitlab.nublado.org/cloudy/cloudy) (Ferland et al. 2017, RMxAA, 53, 385)
- Python >= 3.8
- numpy, pandas, matplotlib

## References

- Asplund, M., Grevesse, N., Sauval, A. J., & Scott, P. 2009, ARA&A, 47, 481
- Ferland, G. J., et al. 2017, RMxAA, 53, 385
- Leitherer, C., et al. 1999, ApJS, 123, 3
- Madden, S. C., et al. 2020, A&A, 643, A141
- Wolfire, M. G., et al. 2003, ApJ, 587, 278

## License

This code is released under the MIT License. If you use this grid in your research, please cite the associated paper.
