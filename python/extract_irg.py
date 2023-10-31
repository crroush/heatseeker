import argparse
import numpy as np
from matplotlib import pyplot as plt
import matplotlib.cm as cm
import struct
import glob
import os
from PIL import Image

from dataclasses import dataclass
@dataclass
class IrgHeader:
    unknown_header: int
    first_image_size: int
    first_image_width: int
    first_image_height: int
    pad1: int
    second_image_size: int
    second_image_width: int
    second_image_height: int
    pad2: int
    third_image_size: int
    third_image_width: int
    third_image_height: int
    emissivity: int
    reflective_temperature: int
    ambient_temperature: int
    distance: int
    unknown: int
    transmissivity: int
    padding: int
    unknown2: int
    unknown3: int
    def print(self):
        print("Unknown Header     : ", self.unknown_header)
        print("First Image Size   : ", self.first_image_size)
        print("First Image Width  : ", self.first_image_width)
        print("First Image Height : ", self.first_image_height)
        print("Pad?               : ", self.pad1)
        print("Second Image Size  : ", self.second_image_size)
        print("Second Image Width : ", self.second_image_width)
        print("Second Image Height: ", self.second_image_height)
        print("Pad                : ", self.pad2)
        print("Third Image Size   : ", self.third_image_size)
        print("Third Image Width  : ", self.third_image_width)
        print("Third Image Height : ", self.third_image_height)
        print("Emissivity                 : ", self.emissivity/10000)
        print("Reflective Temperature (K) : ", self.reflective_temperature/10000)
        print("Ambient Temperature    (K) : ", self.ambient_temperature/10000)
        print("Distance (meters)          : ", self.distance/10000)
        print("Unknown                    : ", self.unknown)
        print("Transmissivity             : ", self.transmissivity/10000)
        print("Padding                    : ", self.padding)
        print("Unknown                    : ", self.unknown2)
        print("Unknown                    : ", self.unknown3)


def extract_data_from_binary(file_path, print_header=False):
    with open(file_path, 'rb') as file:
        # Extract thermal header
        thermal_header = file.read(128)
        # Map to the ICD
        format_str = '<iIHHbIHHBIHHIIIIIIIH14xB'
        data = struct.unpack(format_str, thermal_header[:75])
        irg_header = IrgHeader(*data)
        if print_header:
            irg_header.print()

        if thermal_header[0x7E] == 0xAC and thermal_header[0x7F] == 0xCA:
           diff_start = 0x80
        else:
           diff_start = 0x100
        thermal_header = file.seek(diff_start)

        # Extract grayscale image
        grayscale_data = np.frombuffer(
                file.read(irg_header.first_image_size),
                dtype=np.uint8).reshape(irg_header.first_image_width,
                                        irg_header.first_image_height)

        # Extract raw thermal data
        thermal_data = np.frombuffer(
                file.read(2*irg_header.second_image_size),
                dtype=np.uint16).reshape(irg_header.second_image_width,
                                        irg_header.second_image_height)

        jpg_color_image = np.frombuffer(file.read(1350), dtype=np.uint8)

    return {
        "grayscale_data": grayscale_data,
        "thermal_data": thermal_data,
        "jpg_color_image": jpg_color_image
    }
def save_as_jpg(data, filename, cmap='inferno'):
    # Normalize data to 0-1 range
    data_normalized = (data - data.min()) / (data.max() - data.min())

    # Apply colormap to get RGB values
    rgb_image = (cm.get_cmap(cmap)(data_normalized)[:, :, :3] * 255).astype(np.uint8)

    img = Image.fromarray(rgb_image)
    img.save(filename)
def main():
    parser = argparse.ArgumentParser(
            description="Extract and plot data from binary file.")
    parser.add_argument("file_path", nargs="*", help="Path to the binary file.")
    parser.add_argument( "-p", "--plot", action='store_true',
            help="Plots each of the files")
    parser.add_argument( "-s", "--save", action='store_true',
            help="Saves each of the images as a file")
    parser.add_argument("--outdir", type=str, default=".",
                        help="Specify the directory to save the output JPGs.")
    args = parser.parse_args()

    # Ensure the output directory exists
    if not os.path.exists(args.outdir):
        os.makedirs(args.outdir)

    for file in args.file_path:
        extracted_data = extract_data_from_binary(file)

        # Save grayscale_data and thermal_data as separate JPG files
        base_name = os.path.basename(file).split('.')[0]
        gray_filename = os.path.join(args.outdir, f"{base_name}_bw.jpg")
        thermal_filename = os.path.join(args.outdir, f"{base_name}_thermal.jpg")

        if args.save:
            save_as_jpg(extracted_data["grayscale_data"], gray_filename,
                    cmap="gray")
            save_as_jpg(extracted_data["thermal_data"], thermal_filename)

        if args.plot:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

            # Plotting histogram corrected preview on the first subplot
            ax1.imshow(extracted_data["grayscale_data"], cmap='gray')
            ax1.set_title("Histogram Corrected Preview")
            ax1.axis('off')
            fig.colorbar(plt.cm.ScalarMappable(cmap='gray'),
                ax=ax1, label="Pixel Value")

            # Plotting raw thermal data on the second subplot
            thermal_data = extracted_data["thermal_data"] / 10.0
            # Convert from Kelvin to Fahrenheit
            thermal_data_fahrenheit = (thermal_data - 273.15) * 9/5 + 32
            im = ax2.imshow(thermal_data_fahrenheit, cmap='inferno')
            ax2.set_title("Thermal Data")
            ax2.axis('off')
            fig.colorbar(im, ax=ax2, label="Temperature (°F)")

            plt.tight_layout()
            plt.show()


if __name__ == "__main__":
    main()

