import scipy.io
import numpy as np
import os
import plotly.express as px
import zipfile
from config import BIN_LABELS, MM_ORDER

pixel_area = scipy.io.loadmat(r"pixel_area_xmed.mat")["pixel_area"]
pixel_area_norm = pixel_area / np.max(pixel_area)


def sort_module_order(files: list, module_order=MM_ORDER):
    files.sort(
        key=lambda x: module_order.index(x.name.split("-")[0])
        if x.name.split("-")[0] in module_order
        else ValueError("File not in module order")
    )
    return files

def get_data_info(file_list, verbose=False, check_mat=False):
    for file in file_list:
        if not check_mat:
            mat_file = scipy.io.loadmat(file)
        else:
            if file.endswith(".mat"):
                print("matfile loaded")
                mat_file = scipy.io.loadmat(file)
            else:
                continue

        cc_data = mat_file["cc_struct"]["data"][0][0][0][0][0]
        cc_data_dict = {
            "Tube currents or scan steps": cc_data.shape[0],
            "Number of bins": cc_data.shape[1],
            "Capture views": cc_data.shape[2],
            "Pixel rows": cc_data.shape[3],
            "Pixel columns": cc_data.shape[4],
        }
        params = mat_file["cc_struct"]["params"][0][0][0]

        params_info = {}
        for d_type in params.dtype.names:
            params_info[d_type] = params[d_type][0]

        if verbose:
            for msg in cc_data_dict.values():
                print(msg)
            for p in params_info.values():
                print(p)

        return cc_data_dict, params_info, params


# create a function that unzips the files and returns the list of .mat files
def unzip_mat_files(zip_folder):
    parent_dir = os.path.dirname(zip_folder)
    with zipfile.ZipFile(zip_folder, "r") as zip_ref:
        zip_ref.extractall(parent_dir)
    unzipped_folder = zip_folder.replace(".zip", "")  # remove the .zip extension
    mat_filenames = [f for f in os.listdir(unzipped_folder) if f.endswith(".mat")]
    return [os.path.join(unzipped_folder, f) for f in mat_filenames]

def get_number_of_frames(file_name):
    mat_file = scipy.io.loadmat(file_name)
    cc_data = mat_file["cc_struct"]["data"][0][0][0][0][0]
    return cc_data.shape[2]

def process_mat_files_list(
    bin_id, files_list, file_check, area_correction, frame:int = None, mm_order=MM_ORDER
):
    count_maps_A0 = []
    count_maps_A1 = []

    for file in files_list:
        if file_check:
            if not file.endswith(".mat"):
                raise ValueError(f"File {file} does not have a .mat extension")
            
        mat_file = scipy.io.loadmat(file)
        cc_data = mat_file["cc_struct"]["data"][0][0][0][0][0]
        if frame is not None:
            cc_data = cc_data[:, :, frame, :, :]
        else:
            cc_data = np.mean(cc_data, axis=2)
        count_map = cc_data[0, bin_id, :, :]

        if area_correction:
            count_map = np.divide(count_map, pixel_area_norm)

        if file.name.endswith("A0.mat"):
            count_map = np.flip(count_map, axis=0)
            count_map = np.flip(count_map, axis=1)
            count_maps_A0.append(count_map)
        if file.name.endswith("A1.mat"):
            count_maps_A1.append(count_map)

    count_maps_A0 = np.array(count_maps_A0)

    count_maps_A0_comb = np.concatenate(count_maps_A0, axis=0)
    count_maps_A1_comb = np.concatenate(count_maps_A1, axis=0)
    full_count_map = np.concatenate([count_maps_A0_comb, count_maps_A1_comb], axis=1)

    return count_maps_A0, count_maps_A1, full_count_map


def process_mat_files_folder(bin_id, folder, area_correction=True):
    count_maps_A0 = []
    count_maps_A1 = []

    # Iterate through the files in the folder
    for file in os.listdir(folder):
        if file.endswith(".mat"):
            file_path = os.path.join(folder, file)
            mat_file = scipy.io.loadmat(file_path)
            cc_data = mat_file["cc_struct"]["data"][0][0][0][0][0]

            cc_data = np.mean(cc_data, axis=2)  # Average over the N frames
            # print(f"{cc_data.shape = }")

            count_map = cc_data[0, bin_id, :, :]
            if area_correction:
                count_map = np.divide(count_map, pixel_area_norm)
            # print(count_map.shape)

            if file.endswith("A0.mat"):
                # Invert the count map
                count_map = np.flip(count_map, axis=0)
                count_map = np.flip(count_map, axis=1)
                count_maps_A0.append(count_map)
            if file.endswith("A1.mat"):
                count_maps_A1.append(count_map)

    count_maps_A0 = np.array(count_maps_A0)

    count_maps_A0_comb = np.concatenate(count_maps_A0, axis=0)
    count_maps_A1_comb = np.concatenate(count_maps_A1, axis=0)
    full_count_map = np.concatenate([count_maps_A0_comb, count_maps_A1_comb], axis=1)

    return count_maps_A0, count_maps_A1, full_count_map


def clean_ncp(
    full_count_map,
    low_threshold=1,
    high_threshold=1e3,
    verbose=False,
    perform_clean=True,
):
    # find the dead pixels in full_count_map
    dead_pixels = np.where(full_count_map < low_threshold)
    bright_pixels = np.where(full_count_map > high_threshold)
    # manually found ncp
    found_ncp = (np.array([0]), np.array([0]))

    if verbose:
        print(f"{len(dead_pixels[0]) = }")
        for x, y in zip(dead_pixels[0], dead_pixels[1]):
            print(f"Dead pixel at ({x}, {y})")
        print(f"{len(bright_pixels[0]) = }")
        for x, y in zip(bright_pixels[0], bright_pixels[1]):
            print(f"Bright pixel at ({x}, {y})")
        # print(f"{found_ncp[0] = }")

    ncps = (
        np.concatenate([dead_pixels[0], bright_pixels[0], found_ncp[0]]),
        np.concatenate([dead_pixels[1], bright_pixels[1], found_ncp[1]]),
    )

    if perform_clean == False:  # skip the cleaning process
        return full_count_map

    # impute the dead pixels with the mean of the surrounding pixels
    for pixel in zip(ncps[0], ncps[1]):
        x, y = pixel
        # ignore the pixels on the edge
        if (
            x == 0
            or y == 0
            or x == full_count_map.shape[0] - 1
            or y == full_count_map.shape[1] - 1
        ):
            continue
        else:
            surrounding_pixels = full_count_map[
                [x - 1, y, x - 1, x - 1, x, x, x + 1, x + 1],
                [y - 1, y - 1, y, y + 1, y - 1, y + 1, y - 1, y],
            ]
            full_count_map[x, y] = np.mean(surrounding_pixels)

    return full_count_map


def create_plotly_heatmaps(map, color_range=None, colormap="Viridis", figsize=None):
    if color_range is None:
        color_range = [np.min(map), np.max(map)]

    fig = px.imshow(
        map,
        color_continuous_scale=colormap,
        range_color=color_range,
        labels=dict(x="x", y="y", color="value"),
    )

    return fig


def create_heatmaps_w_boxes(
    map, y_borders, x_borders, color_range=None, figsize=(700, 800)
):
    if color_range is None:
        color_range = [np.min(map), np.max(map)]

    fig = px.imshow(
        map,
        color_continuous_scale="Viridis",
        range_color=color_range,
        labels=dict(x="x", y="y", color="value"),
    )

    fig.update_layout(autosize=False, width=figsize[0], height=figsize[1])
    # draw a rectangle around the cropped region

    for key in y_borders:
        fig.add_shape(
            type="rect",
            x0=x_borders[key]["left"],
            y0=y_borders[key]["top"],
            x1=x_borders[key]["right"],
            y1=y_borders[key]["bot"],
            line=dict(
                color="red",
                width=3,
            ),
        )

    # add a title
    fig.update_layout(title_text="Count map")

    # adjust the figure size
    fig.update_layout(autosize=False, width=figsize[0], height=figsize[1])

    return fig


# def get_data_info_v2(file_list, verbose=False):
#     for file in file_list:

#         mat_file = scipy.io.loadmat(file)
#         cc_data = mat_file["cc_struct"]["data"][0][0][0][0][0]
#         cc_data_dict = {
#             "cc_data_shape": cc_data.shape,
#             "Tube currents or scan steps": cc_data.shape[0],
#             "Number of bins": cc_data.shape[1],
#             "Capture views": cc_data.shape[2],
#             "Pixel rows": cc_data.shape[3],
#             "Pixel columns": cc_data.shape[4],
#         }
#         params = mat_file["cc_struct"]["params"][0][0][0]
#         data_type = params.dtype

#         params_info = []
#         for d_type in data_type.names:
#             params_info.append(f"{d_type}: {params[d_type][0]}")

#         if verbose:
#             for msg in cc_data_dict.values():
#                 print(msg)
#             for p in params_info:
#                 print(p)

#         return cc_data_dict, params_info

if __name__ == "__main__":
    print(pixel_area)
