# HiLUX-explore

By James McKee  
https://github.com/JamesMcKee 
September 2025

This Python script processes and visualises data from a velocity map ion imaging experiment using the HiLUX dataset. It reads multiple HDF5 files, extracts key ion detection parameters, and generates plots to support analysis of molecular fragmentation and spatial ion distributions.

## Features

- Reads and combines data from multiple `.h5` files
- Plots time-of-flight (ToF) histogram
- Calibrates ToF to mass/charge (m/z) using reference peaks
- Generates 2D histograms of:
  - ToF vs x-position
  - x vs y for user-defined TOF ranges
- Accepts flexible command-line options for:
  - Input directory
  - Custom TOF ranges
  - Displaying plots interactively
  - Saving all plots into a timestamped PDF


## Dependencies

This script requires the following Python packages:

- `numpy`
- `matplotlib`
- `h5py`
- `argparse` (standard library)

These are listed in the requirements.txt file, install with: pip install -r requirements.txt


## Usage

Run the script from the command line:

python hilux_explore.py -d "C:/path/to/data" -r "(10000,10400)" "(8450,8850)" "(7000,7400)" --show --savepdf


### Arguments

| Option        | Description                                                                 |
|---------------|-----------------------------------------------------------------------------|
| `-d` / `--directory` | Path to the folder containing `.h5` files                              |
| `-r` / `--ranges`    | One or more time-of-flight (TOF) ranges in nanoseconds, formatted as `(start,end)` |
| `--show`      | Display plots interactively                                                 |
| `--savepdf`   | Save all generated plots into a single timestamped PDF in the data folder   |

Note: TOF values should be provided in nanoseconds (ns), consistent with the units used in the test dataset.


## Calibration Details

ToF is converted to m/z using the nonlinear relation:

m/z = (a * ToF + b)^2


Where `a` and `b` are fitted using:
- C₆H₆I⁺ → ToF ≈ 12000 ns, m/z = 204
- H₂O⁺ → ToF ≈ 6100 ns, m/z = 18


## Output

- Plots are saved as `hilux_plots_YYYY-MM-DD_HH-MM.pdf` in the specified data directory
- Console output includes calibration coefficients and m/z ranges for each TOF window


## License

This project is intended for private use and educational purposes.  
If reused or adapted, please credit the original author.
