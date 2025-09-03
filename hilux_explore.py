#!/bin/python
import numpy as np
import matplotlib.pyplot as plt
import os
import h5py
import argparse
from matplotlib.backends.backend_pdf import PdfPages
from datetime import datetime


# calibration function
def tof_to_mz(tof_ns, a, b):
    return (a * tof_ns + b)**2


# used for letting a user supply their own ToF ranges (in nanoseconds)
def parse_range(range_str):
    # Remove parentheses and split by comma
    range_str = range_str.strip("()")
    start, end = map(int, range_str.split(","))
    return (start, end)


def main():
	parser = argparse.ArgumentParser(description="Explore HiLUX data in this directory path. Provide a directory containing sub-directories for...")
	parser.add_argument(
		"-d", "--directory",
		type=str,
		required=True,
		help="Path to the directory"
	)

	parser.add_argument(
		"-r", "--ranges",
		nargs="+",
		metavar="RANGE",
		help="TOF ranges e.g. (10000,10400) (8450,8850) ..."
	)

	parser.add_argument(
		"--show",
		action="store_true",
		help="Display plots after processing"
	)

	parser.add_argument(
		"--savepdf",
		action="store_true",
		help="Save all plots into a single PDF file"
	)

	args = parser.parse_args()

	if args.ranges:
		# dynamically build TOF ranges with labels A, B, C, and so on...
		labels = [chr(65 + i) for i in range(len(args.ranges))]  # e.g. called A, B, C, etc.

		tof_ranges = {
			label: parse_range(rng)
			for label, rng in zip(labels, args.ranges)
		}


	else:
		# if user doesn't give ranges, use these ones as the default
		tof_ranges = {
			"A": (10000, 10400),
			"B": (8450, 8850),
			"C": (7000, 7400),
		}

		print("TOF Ranges:")


	if os.path.isdir(args.directory):
		print(f"Directory exists: {args.directory}")

		figures = []  # use this list to save figures later
		data_dir = args.directory

		# lists to record the time-of-flight, x, y values
		tof_values = []
		x_values = []
		y_values = []

		# load and combine ToF, x, y data from all HDF5 files found in the directory structure
		for root, dirs, files in os.walk(data_dir):
			for fname in files:
				if fname.endswith(".h5") or fname.endswith(".hdf5"):
					filepath = os.path.join(root, fname)
					with h5py.File(filepath, "r") as f:
						tof_values.append(f["tof"][:])
						x_values.append(f["xpos"][:])
						y_values.append(f["ypos"][:])

		tof_values = np.concatenate(tof_values)
		x_values = np.concatenate(x_values)
		y_values = np.concatenate(y_values)

		print("Loaded arrays:")
		print("ToF:", tof_values.shape, "ns")
		print("x:", x_values.shape, "mm")
		print("y:", y_values.shape, "mm")


		fig = plt.figure(figsize=(8,6))
		plt.hist(tof_values, bins=500, histtype="step", color="blue")
		plt.xlabel("Time of Flight (ns)")
		plt.ylabel("Counts")
		plt.title("Time-of-Flight Spectrum")
		plt.grid(True)
		figures.append(fig) # add to the figures list for saving later
		if args.show:
			plt.show()
		plt.close()


		# Reference peaks used for calibration: 
		# 12000 ns corresponds to C6H6I+ (m/z = 204), 
		# 6100 ns corresponds to H2O+ (m/z = 18)
		# These are used to fit the nonlinear relation between ToF and m/z
		tof_ref = np.array([12000.0, 6100.0])  # in nanoseconds
		mz_ref  = np.array([204.0, 18.0])      # in atomic units

		sqrt_mz = np.sqrt(mz_ref)

		# fit a linear relation i.e. sqrt(m/z) = a*ToF + b
		coeffs = np.polyfit(tof_ref, sqrt_mz, 1)
		a, b = coeffs
		print(f"Calibration coefficients: a = {a}, b = {b}")


		# convert ranges to m/z using the calibration function
		for label, (tmin, tmax) in tof_ranges.items():
		    mz_min, mz_max = tof_to_mz(np.array([tmin, tmax]), coeffs[0], coeffs[1])
		    print(f"{label}: ToF {tmin}-{tmax} ns -> m/z {mz_min:.1f}-{mz_max:.1f}")


		# plot a 2-D histogram of ToF vs. x-position 
		fig = plt.figure(figsize=(8,6))
		plt.hist2d(x_values, tof_values, bins=[200, 200], cmap="viridis")
		plt.colorbar(label="Counts")
		plt.xlabel("x-position (mm)")
		plt.ylabel("Time of Flight (ns)")
		plt.title("2D Histogram: ToF vs x-position")
		figures.append(fig) # adding to figures list for saving later
		if args.show:
			plt.show()
		plt.close()


		# loop through the supplied ToF ranges, make a figure for each one
		for label, (tmin, tmax) in tof_ranges.items():
		    mask = (tof_values >= tmin) & (tof_values <= tmax)
		    x_sel, y_sel = x_values[mask], y_values[mask]


		    fig = plt.figure(figsize=(6,6))
		    plt.hist2d(x_sel, y_sel, bins=200, cmap="plasma")
		    plt.colorbar(label="Counts")
		    plt.xlabel("x-position (mm)")
		    plt.ylabel("y-position (mm)")
		    plt.title(f"x vs y for ToF range {label}: {tmin}–{tmax} ns")
		    plt.axis("equal")
		    figures.append(fig) # adding to figures list for saving later
		    if args.show:
			    plt.show()
		    plt.close()
		plt.close()


		# if the savepdf argument was supplied, save the files to a pdf
		if args.savepdf:
			timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
			filename = f"hilux_plots_{timestamp}.pdf"
			pdf_path = os.path.join(args.directory, filename)

			with PdfPages(pdf_path) as pdf:
				for fig in figures:
					pdf.savefig(fig)
			print(f"Saved all plots to {pdf_path}")

	else:
		print(f"Invalid directory: {args.directory}")

if __name__ == "__main__":
	main()