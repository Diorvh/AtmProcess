from dataclasses import dataclass

import numpy as np
from scipy.signal import savgol_filter

_ANGLE_BLOCK_SIZE = 256  # 分块限制临时坐标矩阵的内存占用


@dataclass(frozen=True)
class SideSamplingGeometry:
    angles: np.ndarray
    indices: tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]
    weights: tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]

    def calculate_inverted_profile(self, image: np.ndarray) -> np.ndarray:
        flat = image.ravel()
        values = sum(flat[index] * weight for index, weight in zip(self.indices, self.weights))
        return np.iinfo(image.dtype).max - np.sum(values, axis=1)


@dataclass(frozen=True)
class AtomizationSamplingGeometry:
    image_shape: tuple[int, int]
    left: SideSamplingGeometry
    right: SideSamplingGeometry

    def calculate_profiles(self, image: np.ndarray):
        if image.shape != self.image_shape:
            raise ValueError("图像尺寸与雾化采样缓存不一致")
        return (
            [self.left.angles, self.left.calculate_inverted_profile(image)],
            [self.right.angles, self.right.calculate_inverted_profile(image)],
        )


def build_sampling_geometry(
    image_shape: tuple[int, int],
    x_left: int,
    x_right: int,
    y: int,
    r_max: int,
    theta_left: int,
    theta_right: int,
    num_avg_left: int,
    r_start_left: int,
    num_avg_right: int,
    r_start_right: int,
) -> AtomizationSamplingGeometry:
    left_steps = np.arange(899, theta_left - 1, -1, dtype=np.int32)
    right_steps = np.arange(900, theta_right, dtype=np.int32)
    left_starts = np.where(left_steps - theta_left >= num_avg_left, 0, r_start_left)
    right_starts = np.where(theta_right - right_steps >= num_avg_right, 0, r_start_right)
    return AtomizationSamplingGeometry(
        image_shape,
        _build_side_geometry(image_shape, left_steps, x_left, y, r_max, left_starts),
        _build_side_geometry(image_shape, right_steps, x_right, y, r_max, right_starts),
    )


def _build_side_geometry(image_shape, theta_steps, origin_x, origin_y, r_max, radius_starts) -> SideSamplingGeometry:
    radii = np.arange(r_max + 1, dtype=np.float64)
    theta = np.deg2rad(theta_steps * 0.1 + 0.05)[:, None]
    rows = origin_y + (radii[None, :] + 0.5) * np.sin(theta)
    columns = origin_x - (radii[None, :] + 0.5) * np.cos(theta)
    valid = radii[None, :] >= radius_starts[:, None]
    valid &= (rows >= 0) & (rows <= image_shape[0] - 1)
    valid &= (columns >= 0) & (columns <= image_shape[1] - 1)

    row1 = np.clip(np.floor(rows).astype(np.int32), 0, image_shape[0] - 1)
    column1 = np.clip(np.floor(columns).astype(np.int32), 0, image_shape[1] - 1)
    row2 = np.minimum(row1 + 1, image_shape[0] - 1)
    column2 = np.minimum(column1 + 1, image_shape[1] - 1)
    row_fraction = rows - row1
    column_fraction = columns - column1
    area_weights = np.pi * (2 * radii + 1) * 0.1 / 360
    weights = area_weights[None, :] * valid
    weight_sums = np.sum(weights, axis=1)[:, None]
    if np.any(weight_sums == 0):
        raise ValueError("雾化锥角计算区域内没有有效像素")

    def flat_indices(row, column):
        return (row * image_shape[1] + column).astype(np.int32)

    return SideSamplingGeometry(
        theta_steps * 0.1 + 0.05,
        (
            flat_indices(row1, column1),
            flat_indices(row2, column1),
            flat_indices(row1, column2),
            flat_indices(row2, column2),
        ),
        (
            (1 - row_fraction) * (1 - column_fraction) * weights / weight_sums,
            row_fraction * (1 - column_fraction) * weights / weight_sums,
            (1 - row_fraction) * column_fraction * weights / weight_sums,
            row_fraction * column_fraction * weights / weight_sums,
        ),
    )


def calculate_grayavg_byangle(args):
    img, x_left, x_right, y, r_max, theta_left, theta_right, num_avg_left, r_start_left, num_avg_right, r_start_right = args

    left_theta_steps = np.arange(theta_left[0], theta_left[1] - 1, -1, dtype=np.int32)
    right_theta_steps = np.arange(theta_right[0], theta_right[1], dtype=np.int32)
    left_radius_starts = np.where(left_theta_steps - theta_left[1] >= num_avg_left, 0, r_start_left)
    right_radius_starts = np.where(theta_right[1] - right_theta_steps >= num_avg_right, 0, r_start_right)

    left_values = _calculate_side_profile(img, left_theta_steps, x_left, y, r_max, left_radius_starts)
    right_values = _calculate_side_profile(img, right_theta_steps, x_right, y, r_max, right_radius_starts)
    left_angles = left_theta_steps * 0.1 + 0.05
    right_angles = right_theta_steps * 0.1 + 0.05
    return [left_angles, left_values], [right_angles, right_values]


def _calculate_side_profile(img, theta_steps, origin_x, origin_y, r_max, radius_starts):
    """按角度分块计算一侧的面积加权平均灰度曲线。"""
    radii = np.arange(r_max + 1, dtype=np.float64)
    area_weights = np.pi * (2 * radii + 1) * 0.1 / 360
    profile = np.empty(theta_steps.size, dtype=np.float64)

    for block_start in range(0, theta_steps.size, _ANGLE_BLOCK_SIZE):
        block_end = min(block_start + _ANGLE_BLOCK_SIZE, theta_steps.size)
        block_theta = np.deg2rad(theta_steps[block_start:block_end] * 0.1 + 0.05)[:, None]
        block_radii = radii[None, :]
        sample_x = origin_x - (block_radii + 0.5) * np.cos(block_theta)
        sample_y = origin_y + (block_radii + 0.5) * np.sin(block_theta)

        valid = block_radii >= radius_starts[block_start:block_end, None]
        valid &= (sample_y >= 0) & (sample_y <= img.shape[0] - 1)
        valid &= (sample_x >= 0) & (sample_x <= img.shape[1] - 1)

        gray = _bilinear_interpolate(img, sample_y, sample_x)
        weights = area_weights[None, :] * valid
        weight_sums = np.sum(weights, axis=1)
        if np.any(weight_sums == 0):
            raise ValueError("雾化锥角计算区域内没有有效像素")
        profile[block_start:block_end] = np.sum(gray * weights, axis=1) / weight_sums

    return profile


def _bilinear_interpolate(img, rows, columns):
    """使用旧算法的双线性公式批量插值整个坐标矩阵。"""
    row1 = np.clip(np.floor(rows).astype(np.intp), 0, img.shape[0] - 1)
    column1 = np.clip(np.floor(columns).astype(np.intp), 0, img.shape[1] - 1)
    row2 = np.minimum(row1 + 1, img.shape[0] - 1)
    column2 = np.minimum(column1 + 1, img.shape[1] - 1)
    row_fraction = rows - row1
    column_fraction = columns - column1

    return (
        (1 - row_fraction) * (1 - column_fraction) * img[row1, column1]
        + row_fraction * (1 - column_fraction) * img[row2, column1]
        + (1 - row_fraction) * column_fraction * img[row1, column2]
        + row_fraction * column_fraction * img[row2, column2]
    )


def calculate_atm_angle_thres_p2(args):
    res_left, res_right, num_avg_left, num_avg_right, thres_ratio_left, thres_ratio_right, window_length, polyorder = args

    max_left = np.average(res_left[1][:num_avg_left])
    min_left = np.average(res_left[1][-num_avg_left:])
    thres_left = min_left + (max_left - min_left) * thres_ratio_left

    max_right = np.average(res_right[1][:num_avg_right])
    min_right = np.average(res_right[1][-num_avg_right:])
    thres_right = min_right + (max_right - min_right) * thres_ratio_right

    filtered_left = [res_left[0], savgol_filter(res_left[1], window_length, polyorder)]
    filtered_right = [res_right[0], savgol_filter(res_right[1], window_length, polyorder)]
    angle_left_pos = find_last_greater_equal(filtered_left[1], thres_left)
    angle_right_pos = find_last_greater_equal(filtered_right[1], thres_right)
    return res_left[0][angle_left_pos], res_right[0][angle_right_pos]


def calculate_atm_angle_thres(args):
    img, x_left, x_right, y, r_max, theta_left, theta_right, num_avg_left, r_start_left, num_avg_right, r_start_right, thres_ratio_left, thres_ratio_right, window_length, polyorder = args
    res_left, res_right = calculate_grayavg_byangle((
        img,
        x_left,
        x_right,
        y,
        r_max,
        (899, theta_left),
        (900, theta_right),
        num_avg_left,
        r_start_left,
        num_avg_right,
        r_start_right,
    ))
    return calculate_atm_angle_thres_p2((
        res_left,
        res_right,
        num_avg_left,
        num_avg_right,
        thres_ratio_left,
        thres_ratio_right,
        window_length,
        polyorder,
    ))


def find_last_greater_equal(arr, thres):
    indices = np.where(arr[::-1] >= thres)[0]
    if indices.size == 0:
        return -1
    return arr.size - indices[0] - 1
