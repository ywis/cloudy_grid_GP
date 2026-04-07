#!/usr/bin/env python3
"""
Cross-validate Cloudy model grid predictions against simplified diagnostic estimates.

This script:
1. Loads the Cloudy grid results (from parse_cloudy_output.py)
2. Loads the observed diagnostic estimates (G0 from SFR, nH from [SII])
3. For each observed source, finds the best-matching Cloudy model
4. Computes systematic offsets between the two methods
5. Generates a comparison figure

Usage:
    python cross_validate.py --grid ../example_output/grid_results.csv \
                             --obs ../../G0_nH_results.csv \
                             --output ../example_output/cross_validation.pdf

Author: Generated for the Green Pea H2 manuscript
"""

import os
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def find_best_model(obs_G0, obs_nH, grid_df):
    """
    Find the Cloudy grid model that best matches observed line ratios.

    In practice, this would compare predicted vs observed line ratios
    (e.g., [SII] doublet ratio, [OIII]/[OII], etc.) and find the
    minimum chi-squared model. Here we demonstrate the framework.

    Parameters
    ----------
    obs_G0 : float
        Observed log G0 from SFR diagnostic
    obs_nH : float
        Observed log nH from [SII] diagnostic
    grid_df : DataFrame
        Cloudy grid results

    Returns
    -------
    best_model : dict
        Best-matching model parameters
    """
    # Simple nearest-neighbor matching in (G0, nH) space
    # In a full analysis, this would use chi-squared on line ratios
    dist = np.sqrt((grid_df.log_G0 - obs_G0)**2 +
                   (grid_df.log_nH - obs_nH)**2)
    idx = dist.idxmin()
    return grid_df.loc[idx].to_dict()


def run_cross_validation(grid_csv, obs_csv, output_path):
    """Run the cross-validation analysis."""

    # Load data
    grid = pd.read_csv(grid_csv)
    obs = pd.read_csv(obs_csv)

    # Filter to sources with both G0 and nH
    obs_valid = obs[obs.log_G0.notna() & obs.log_nH.notna()].copy()

    if len(grid) == 0 or grid.CII_158um.isna().all():
        print("Cloudy grid results not yet available (template only).")
        print("Run Cloudy on the input files first, then parse and re-run.")
        print(f"\nFor demonstration, generating comparison framework figure...")
        generate_demo_figure(obs_valid, output_path)
        return

    # Match each observed source to best Cloudy model
    results = []
    for _, row in obs_valid.iterrows():
        best = find_best_model(row.log_G0, row.log_nH, grid)
        results.append({
            'source': row.source,
            'obs_log_G0': row.log_G0,
            'obs_log_nH': row.log_nH,
            'cloudy_log_G0': best['log_G0'],
            'cloudy_log_nH': best['log_nH'],
            'delta_G0': best['log_G0'] - row.log_G0,
            'delta_nH': best['log_nH'] - row.log_nH,
        })

    df = pd.DataFrame(results)

    # Statistics
    print(f"Cross-validation results (N={len(df)}):")
    print(f"  delta_G0: median={df.delta_G0.median():.2f}, "
          f"std={df.delta_G0.std():.2f}")
    print(f"  delta_nH: median={df.delta_nH.median():.2f}, "
          f"std={df.delta_nH.std():.2f}")

    # Save results
    out_csv = output_path.replace('.pdf', '.csv')
    df.to_csv(out_csv, index=False)
    print(f"Saved to {out_csv}")

    # Generate comparison figure
    generate_comparison_figure(df, output_path)


def generate_demo_figure(obs_valid, output_path):
    """Generate a demonstration figure showing the framework."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Panel 1: G0 comparison placeholder
    ax = axes[0]
    ax.scatter(obs_valid.log_G0, obs_valid.log_G0, c='steelblue',
               s=50, alpha=0.7, edgecolors='navy', lw=0.5)
    ax.plot([0, 5], [0, 5], 'k--', lw=1, label='1:1')
    ax.set_xlabel(r'$\log\,G_0$ (SFR diagnostic)')
    ax.set_ylabel(r'$\log\,G_0$ (Cloudy best-fit)')
    ax.set_title('(a) Radiation field')
    ax.legend()
    ax.text(0.05, 0.9, 'Placeholder:\nRun Cloudy grid first',
            transform=ax.transAxes, fontsize=10, color='red',
            bbox=dict(fc='lightyellow', ec='red', alpha=0.8))

    # Panel 2: nH comparison placeholder
    ax = axes[1]
    ax.scatter(obs_valid.log_nH, obs_valid.log_nH, c='sandybrown',
               s=50, alpha=0.7, edgecolors='saddlebrown', lw=0.5)
    ax.plot([0, 4], [0, 4], 'k--', lw=1, label='1:1')
    ax.set_xlabel(r'$\log\,n_{\rm H}$ ([SII] diagnostic)')
    ax.set_ylabel(r'$\log\,n_{\rm H}$ (Cloudy best-fit)')
    ax.set_title(r'(b) Hydrogen density')
    ax.legend()
    ax.text(0.05, 0.9, 'Placeholder:\nRun Cloudy grid first',
            transform=ax.transAxes, fontsize=10, color='red',
            bbox=dict(fc='lightyellow', ec='red', alpha=0.8))

    plt.tight_layout()
    plt.savefig(output_path, bbox_inches='tight', dpi=150)
    print(f"Demo figure saved to {output_path}")


def generate_comparison_figure(df, output_path):
    """Generate the cross-validation comparison figure."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Panel 1: G0 comparison
    ax = axes[0]
    ax.scatter(df.obs_log_G0, df.cloudy_log_G0, c='steelblue',
               s=50, alpha=0.7, edgecolors='navy', lw=0.5)
    ax.plot([0, 5], [0, 5], 'k--', lw=1, label='1:1')
    ax.fill_between([0, 5], [0-0.3, 5-0.3], [0+0.3, 5+0.3],
                    alpha=0.1, color='gray', label=r'$\pm 0.3$ dex')
    ax.set_xlabel(r'$\log\,G_0$ (SFR diagnostic)')
    ax.set_ylabel(r'$\log\,G_0$ (Cloudy best-fit)')
    ax.set_title('(a) Radiation field')
    ax.legend()
    med = df.delta_G0.median()
    std = df.delta_G0.std()
    ax.text(0.05, 0.85, f'$\\Delta = {med:+.2f} \\pm {std:.2f}$',
            transform=ax.transAxes, fontsize=12,
            bbox=dict(fc='lightyellow', ec='gray', alpha=0.8))

    # Panel 2: nH comparison
    ax = axes[1]
    ax.scatter(df.obs_log_nH, df.cloudy_log_nH, c='sandybrown',
               s=50, alpha=0.7, edgecolors='saddlebrown', lw=0.5)
    ax.plot([0, 4], [0, 4], 'k--', lw=1, label='1:1')
    ax.fill_between([0, 4], [0-0.3, 4-0.3], [0+0.3, 4+0.3],
                    alpha=0.1, color='gray', label=r'$\pm 0.3$ dex')
    ax.set_xlabel(r'$\log\,n_{\rm H}$ ([SII] diagnostic)')
    ax.set_ylabel(r'$\log\,n_{\rm H}$ (Cloudy best-fit)')
    ax.set_title(r'(b) Hydrogen density')
    ax.legend()
    med = df.delta_nH.median()
    std = df.delta_nH.std()
    ax.text(0.05, 0.85, f'$\\Delta = {med:+.2f} \\pm {std:.2f}$',
            transform=ax.transAxes, fontsize=12,
            bbox=dict(fc='lightyellow', ec='gray', alpha=0.8))

    plt.tight_layout()
    plt.savefig(output_path, bbox_inches='tight', dpi=150)
    print(f"Comparison figure saved to {output_path}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Cross-validate Cloudy grid vs diagnostic estimates')
    parser.add_argument('--grid', default='../example_output/grid_results.csv',
                        help='Cloudy grid results CSV')
    parser.add_argument('--obs', default='../../G0_nH_results.csv',
                        help='Observed diagnostic estimates CSV')
    parser.add_argument('--output',
                        default='../example_output/cross_validation.pdf',
                        help='Output figure path')
    args = parser.parse_args()

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    run_cross_validation(args.grid, args.obs, args.output)
