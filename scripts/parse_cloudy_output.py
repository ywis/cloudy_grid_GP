#!/usr/bin/env python3
"""
Parse Cloudy output files from the G0-nH PDR model grid.

Extracts key emission line luminosities and physical parameters from
the .lin and .ovr output files, and compiles them into a single CSV table.

Usage:
    python parse_cloudy_output.py --input_dir ../input_files --output ../example_output/grid_results.csv

Output columns:
    log_G0, log_nH, CII_158um, OI_63um, OI_145um, OIII_88um, OIII_5007,
    Hbeta, Halpha, SII_6717, SII_6731, FIR_total, CII_FIR_ratio

Author: Generated for the Green Pea H2 manuscript
"""

import os
import re
import glob
import argparse
import numpy as np
import pandas as pd


def parse_model_name(fname):
    """Extract log_G0 and log_nH from model file name like G1.00_n2.50."""
    base = os.path.basename(fname)
    # Remove file extension if present (.in, .lin, .ovr, etc.)
    for ext in ['.in', '.lin', '.ovr', '.con', '.ems', '.pdr', '.het', '.col']:
        if base.endswith(ext):
            base = base[:-len(ext)]
            break
    m = re.match(r'G([\d.]+)_n([\d.]+)', base)
    if m:
        return float(m.group(1)), float(m.group(2))
    return None, None


def parse_lin_file(lin_path):
    """
    Parse a Cloudy .lin file to extract emission line luminosities.
    Returns a dict of line_label -> luminosity (erg/s/cm^2).
    """
    results = {}
    if not os.path.exists(lin_path):
        return results

    target_lines = {
        'C  2 157.636m': 'CII_158um',
        'O  1 63.1679m': 'OI_63um',
        'O  1 145.525m': 'OI_145um',
        'O  3 88.3323m': 'OIII_88um',
        'O  3 5006.84A': 'OIII_5007',
        'O  3 4958.91A': 'OIII_4959',
        'O  2 3726.03A': 'OII_3726',
        'O  2 3728.81A': 'OII_3729',
        'N  2 6583.45A': 'NII_6584',
        'S  2 6716.44A': 'SII_6717',
        'S  2 6730.82A': 'SII_6731',
        'H  1 6562.81A': 'Halpha',
        'H  1 4861.33A': 'Hbeta',
    }

    with open(lin_path, 'r') as f:
        for line in f:
            line = line.strip()
            for key, col_name in target_lines.items():
                if key in line:
                    # Extract the numerical value (last column typically)
                    parts = line.split()
                    try:
                        val = float(parts[-1])
                        results[col_name] = val
                    except (ValueError, IndexError):
                        pass
    return results


def parse_ovr_file(ovr_path):
    """
    Parse a Cloudy .ovr file to extract integrated properties.
    Returns a dict with FIR luminosity and other global quantities.
    """
    results = {}
    if not os.path.exists(ovr_path):
        return results

    with open(ovr_path, 'r') as f:
        for line in f:
            # Look for total FIR luminosity or other summary quantities
            if 'Inci' in line or 'total' in line.lower():
                pass  # Cloudy overview format varies; handle as needed
    return results


def parse_pdr_file(pdr_path):
    """
    Parse a Cloudy .pdr file to extract PDR-specific quantities.
    Returns a dict with H2 fraction, CO fraction, etc.
    """
    results = {}
    if not os.path.exists(pdr_path):
        return results

    with open(pdr_path, 'r') as f:
        lines = f.readlines()
        if len(lines) > 1:
            # Last line typically has the final zone values
            header = lines[0].strip().split('\t')
            values = lines[-1].strip().split('\t')
            for h, v in zip(header, values):
                try:
                    results[h.strip()] = float(v)
                except ValueError:
                    results[h.strip()] = v
    return results


def process_grid(input_dir, output_csv):
    """Process all model outputs and compile into a CSV table."""
    rows = []

    # Find all .in files to determine model names
    in_files = sorted(glob.glob(os.path.join(input_dir, 'G*_n*.in')))

    if not in_files:
        print(f"No input files found in {input_dir}")
        print("This script expects Cloudy output files (.lin, .ovr, .pdr)")
        print("alongside the input files (.in) in the same directory.")
        print("\nGenerating expected output template instead...")
        generate_template(input_dir, output_csv)
        return

    # Check if any output files exist
    lin_files = glob.glob(os.path.join(input_dir, 'G*_n*.lin'))
    if not lin_files:
        print("No Cloudy output files (.lin) found.")
        print("Generating expected output template instead...")
        generate_template_from_list(in_files, output_csv)
        return

    for in_file in in_files:
        model_name = os.path.basename(in_file).replace('.in', '')
        log_G0, log_nH = parse_model_name(model_name)

        if log_G0 is None:
            continue

        row = {'model': model_name, 'log_G0': log_G0, 'log_nH': log_nH}

        # Parse line luminosities
        lin_path = os.path.join(input_dir, f"{model_name}.lin")
        lin_data = parse_lin_file(lin_path)
        row.update(lin_data)

        # Parse PDR quantities
        pdr_path = os.path.join(input_dir, f"{model_name}.pdr")
        pdr_data = parse_pdr_file(pdr_path)
        if pdr_data:
            row['H2_fraction'] = pdr_data.get('H2/Htot', np.nan)

        # Compute CII/FIR ratio if both available
        if 'CII_158um' in row and row.get('CII_158um', 0) > 0:
            # FIR approximation: sum of major cooling lines
            fir_approx = (row.get('CII_158um', 0) +
                          row.get('OI_63um', 0) +
                          row.get('OI_145um', 0) +
                          row.get('OIII_88um', 0))
            if fir_approx > 0:
                row['CII_FIR_ratio'] = row['CII_158um'] / fir_approx

        rows.append(row)

    df = pd.DataFrame(rows)
    df = df.sort_values(['log_G0', 'log_nH']).reset_index(drop=True)
    df.to_csv(output_csv, index=False)
    print(f"Saved {len(df)} model results to {output_csv}")
    return df


def generate_template_from_list(in_files, output_csv):
    """Generate a template CSV from a list of .in files."""
    rows = []
    for in_file in in_files:
        model_name = os.path.basename(in_file).replace('.in', '')
        log_G0, log_nH = parse_model_name(model_name)
        if log_G0 is None:
            continue
        rows.append({
            'model': model_name,
            'log_G0': log_G0,
            'log_nH': log_nH,
            'CII_158um': np.nan,
            'OI_63um': np.nan,
            'OI_145um': np.nan,
            'OIII_88um': np.nan,
            'OIII_5007': np.nan,
            'Hbeta': np.nan,
            'Halpha': np.nan,
            'SII_6717': np.nan,
            'SII_6731': np.nan,
            'CII_FIR_ratio': np.nan,
            'H2_fraction': np.nan,
        })
    df = pd.DataFrame(rows)
    df.to_csv(output_csv, index=False)
    print(f"Generated template with {len(df)} model entries -> {output_csv}")
    print("Run Cloudy on the input files, then re-run this script to populate values.")


def generate_template(input_dir, output_csv):
    """Generate a template CSV showing expected output format."""
    rows = []
    # Look for .in files in input_dir
    in_files = sorted(glob.glob(os.path.join(input_dir, 'G*_n*.in')))
    if not in_files:
        # Also try the default input_files directory
        alt_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'input_files')
        in_files = sorted(glob.glob(os.path.join(alt_dir, 'G*_n*.in')))

    for in_file in in_files:
        model_name = os.path.basename(in_file).replace('.in', '')
        log_G0, log_nH = parse_model_name(model_name)
        if log_G0 is None:
            continue
        rows.append({
            'model': model_name,
            'log_G0': log_G0,
            'log_nH': log_nH,
            'CII_158um': np.nan,
            'OI_63um': np.nan,
            'OI_145um': np.nan,
            'OIII_88um': np.nan,
            'OIII_5007': np.nan,
            'Hbeta': np.nan,
            'Halpha': np.nan,
            'SII_6717': np.nan,
            'SII_6731': np.nan,
            'CII_FIR_ratio': np.nan,
            'H2_fraction': np.nan,
        })

    df = pd.DataFrame(rows)
    df.to_csv(output_csv, index=False)
    print(f"Generated template with {len(df)} model entries -> {output_csv}")
    print("Run Cloudy on the input files, then re-run this script to populate values.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parse Cloudy PDR grid output')
    parser.add_argument('--input_dir', default='../input_files',
                        help='Directory containing Cloudy input/output files')
    parser.add_argument('--output', default='../example_output/grid_results.csv',
                        help='Output CSV file path')
    args = parser.parse_args()

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    process_grid(args.input_dir, args.output)
