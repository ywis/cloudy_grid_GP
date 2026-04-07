# Cloudy PDR Model Grid for Green Pea Galaxies

This repository contains the Cloudy photoionization model grid used in the paper:

> **Molecular Gas Content of Green Pea Galaxies: Insights from [CII], CO, and HI Observations**

## Overview

We construct a grid of plane-parallel PDR models using [Cloudy](https://gitlab.nublado.org/cloudy/cloudy/-/wikis/home) (version 17.02; Ferland et al. 2017) to constrain the interstellar radiation field intensity (G0) and hydrogen number density (nH) in our sample of Green Pea galaxies.

## Grid Parameters

| Parameter | Range | Step | Units |
|-----------|-------|------|-------|
| log G0 | 1.00 -- 4.00 | 0.25 dex | Habing field |
| log nH | 1.00 -- 4.00 | 0.25 dex | cm^-3 |

Total number of models: **169** (13 x 13)

## Physical Setup

- **Geometry**: Plane-parallel, constant-pressure slab
- **Radiation field**: CMB (z=0) + starburst SED (Leitherer et al. 1999), age = 4 Myr
- **Metallicity**: Z/Zsun = 0.2, 12+log(O/H) ~ 8.0
- **Dust**: ISM grains + PAHs, scaled with metallicity
- **Stopping criteria**: T < 10 K or log N_H = 22 cm^-2

## License

MIT License. Please cite the associated paper if you use this grid.
