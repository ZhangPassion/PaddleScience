# Copyright (c) 2023 PaddlePaddle Authors. All Rights Reserved.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Dict
from typing import Optional
from typing import Tuple
from typing import Union

import matplotlib
import matplotlib as mpl
import numpy as np
import paddle
from matplotlib import pyplot as plt
from matplotlib.legend_handler import HandlerBase
from matplotlib.patches import Rectangle
from mpl_toolkits.mplot3d.art3d import Line3DCollection

from ppsci.utils import logger

cnames = [
    "bisque",
    "black",
    "blanchedalmond",
    "blue",
    "blueviolet",
    "brown",
    "burlywood",
    "cadetblue",
    "chartreuse",
    "orangered",
    "orchid",
    "palegoldenrod",
    "palegreen",
]

CMAPS = [
    "Reds",
    "Blues",
    "Greys",
    "Purples",
    "Greens",
    "Oranges",
    "YlOrBr",
    "YlOrRd",
    "OrRd",
    "PuRd",
    "RdPu",
    "BuPu",
    "GnBu",
    "PuBu",
    "YlGnBu",
    "PuBuGn",
    "BuGn",
    "YlGn",
]


def _save_plot_from_1d_array(filename, coord, value, value_keys, num_timestamp=1):
    """Save plot from given 1D data.

    Args:
        filename (str): Filename.
        coord (np.ndarray): Coordinate array.
        value (Dict[str, np.ndarray]): Dict of value array.
        value_keys (List[str]): Value keys.
        num_timestamp (int, optional): Number of timestamps coord/value contains. Defaults to 1.
    """
    fig, a = plt.subplots(len(value_keys), num_timestamp, squeeze=False)
    fig.subplots_adjust(hspace=0.8)

    len_ts = len(coord) // num_timestamp
    for t in range(num_timestamp):
        st = t * len_ts
        ed = (t + 1) * len_ts
        coord_t = coord[st:ed]

        for i, key in enumerate(value_keys):
            _value_t: np.ndarray = value[st:ed, i]
            a[i][t].scatter(
                coord_t,
                _value_t,
                color=cnames[i],
                label=key,
            )
            if num_timestamp > 1:
                a[i][t].set_title(f"{key}(t={t})")
            else:
                a[i][t].set_title(f"{key}")
            a[i][t].grid()
            a[i][t].legend()

        if num_timestamp == 1:
            fig.savefig(filename, dpi=300)
        else:
            fig.savefig(f"{filename}_{t}", dpi=300)

    if num_timestamp == 1:
        logger.info(f"1D result is saved to {filename}.png")
    else:
        logger.info(
            f"1D result is saved to {filename}_0.png"
            f" ~ {filename}_{num_timestamp - 1}.png"
        )


def save_plot_from_1d_dict(
    filename, data_dict, coord_keys, value_keys, num_timestamp=1
):
    """Plot dict data as file.

    Args:
        filename (str): Output filename.
        data_dict (Dict[str, Union[np.ndarray, paddle.Tensor]]): Data in dict.
        coord_keys (List[str]): List of coord key. such as ["x", "y"].
        value_keys (List[str]): List of value key. such as ["u", "v"].
        num_timestamp (int, optional): Number of timestamp in data_dict. Defaults to 1.
    """
    space_ndim = len(coord_keys) - int("t" in coord_keys)
    if space_ndim not in [1, 2, 3]:
        raise ValueError(f"ndim of space coord ({space_ndim}) should be 1, 2 or 3")

    coord = [data_dict[k] for k in coord_keys if k != "t"]
    value = [data_dict[k] for k in value_keys] if value_keys else None

    if isinstance(coord[0], paddle.Tensor):
        coord = [x.numpy() for x in coord]
    else:
        coord = [x for x in coord]
    coord = np.concatenate(coord, axis=1)

    if value is not None:
        if isinstance(value[0], paddle.Tensor):
            value = [x.numpy() for x in value]
        else:
            value = [x for x in value]
        value = np.concatenate(value, axis=1)

    _save_plot_from_1d_array(filename, coord, value, value_keys, num_timestamp)


def _save_plot_from_2d_array(
    filename: str,
    visu_data: Tuple[np.ndarray, ...],
    visu_keys: Tuple[str, ...],
    num_timestamp: int = 1,
    stride: int = 1,
    xticks: Optional[Tuple[float, ...]] = None,
    yticks: Optional[Tuple[float, ...]] = None,
):
    """Save plot from given 2D data.

    Args:
        filename (str): Filename.
        visu_data (Tuple[np.ndarray, ...]): Data that requires visualization.
        visu_keys (Tuple[str, ...]]): Keys for visualizing data. such as ["u", "v"].
        num_timestamp (int, optional): Number of timestamps coord/value contains. Defaults to 1.
        stride (int, optional): The time stride of visualization. Defaults to 1.
        xticks (Optional[Tuple[float,...]]): The list of xtick locations. Defaults to None.
        yticks (Optional[Tuple[float,...]]): The list of ytick locations. Defaults to None.
    """

    plt.close("all")
    mpl.rcParams["xtick.labelsize"] = 5
    mpl.rcParams["ytick.labelsize"] = 5

    fig, ax = plt.subplots(
        len(visu_keys),
        num_timestamp,
        squeeze=False,
        sharey=True,
        figsize=(num_timestamp, len(visu_keys)),
    )
    fig.subplots_adjust(hspace=0.3)
    target_flag = any(["target" in key for key in visu_keys])
    for i, data in enumerate(visu_data):
        if target_flag is False or "target" in visu_keys[i]:
            c_max = np.amax(data)
            c_min = np.amin(data)

        for t_idx in range(num_timestamp):
            t = t_idx * stride
            ax[i, t_idx].imshow(
                data[t, :, :],
                extent=[xticks.min(), xticks.max(), yticks.min(), yticks.max()],
                cmap="inferno",
                origin="lower",
                vmax=c_max,
                vmin=c_min,
            )
            if xticks is not None:
                ax[i, t_idx].set_xticks(xticks)
            if yticks is not None:
                ax[i, t_idx].set_yticks(yticks)

            ax[i, t_idx].set_title(f"t={t}", fontsize=8)
            if t_idx == 0:
                ax[i, 0].set_ylabel(visu_keys[i], fontsize=8)

        p0 = ax[i, -1].get_position().get_points().flatten()
        ax_cbar = fig.add_axes([p0[2] + 0.005, p0[1], 0.0075, p0[3] - p0[1]])
        ticks = np.linspace(0, 1, 5)
        tickLabels = np.linspace(c_min, c_max, 5)
        tickLabels = [f"{t0:02.2f}" for t0 in tickLabels]
        cbar = mpl.colorbar.ColorbarBase(
            ax_cbar, cmap=plt.get_cmap("inferno"), orientation="vertical", ticks=ticks
        )
        cbar.set_ticklabels(tickLabels, fontsize=5)
    plt.savefig(f"{filename}", dpi=300)


def save_plot_from_2d_dict(
    filename: str,
    data_dict: Dict[str, Union[np.ndarray, paddle.Tensor]],
    visu_keys: Tuple[str, ...],
    num_timestamp: int = 1,
    stride: int = 1,
    xticks: Optional[Tuple[float, ...]] = None,
    yticks: Optional[Tuple[float, ...]] = None,
):
    """Plot 2d dict data as file.

    Args:
        filename (str): Output filename.
        data_dict (Dict[str, Union[np.ndarray, paddle.Tensor]]): Data in dict.
        visu_keys (Tuple[str, ...]): Keys for visualizing data. such as ["u", "v"].
        num_timestamp (int, optional): Number of timestamp in data_dict. Defaults to 1.
        stride (int, optional): The time stride of visualization. Defaults to 1.
        xticks (Optional[Tuple[float,...]]): The list of xtick locations. Defaults to None.
        yticks (Optional[Tuple[float,...]]): The list of ytick locations. Defaults to None.
    """
    visu_data = [data_dict[k] for k in visu_keys]
    if isinstance(visu_data[0], paddle.Tensor):
        visu_data = [x.numpy() for x in visu_data]
    _save_plot_from_2d_array(
        filename, visu_data, visu_keys, num_timestamp, stride, xticks, yticks
    )


# Interface to LineCollection:
def _colorline3d(
    x, y, z, t=None, cmap=plt.get_cmap("viridis"), linewidth=1, alpha=1.0, ax=None
):
    """
    Plot a colored line with coordinates x and y
    Optionally specify colors in the array z
    Optionally specify a colormap, a norm function and a line width
    https://stackoverflow.com/questions/52884221/how-to-plot-a-matplotlib-line-plot-using-colormap
    """
    # Default colors equally spaced on [0, 1]:
    if t is None:
        t = np.linspace(0.25, 1.0, len(x))
    if ax is None:
        ax = plt.gca()

    points = np.array([x, y, z]).T.reshape(-1, 1, 3)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)

    colors = np.array([cmap(i) for i in t])
    lc = Line3DCollection(segments, colors=colors, linewidth=linewidth, alpha=alpha)
    ax.add_collection(lc)
    ax.scatter(x, y, z, c=colors, marker="*", alpha=alpha)  # Adding line markers


class HandlerColormap(HandlerBase):
    """Class for creating colormap legend rectangles.

    Args:
        cmap (matplotlib.cm): Matplotlib colormap.
        num_stripes (int, optional): Number of countour levels (strips) in rectangle. Defaults to 8.
    """

    def __init__(self, cmap: matplotlib.cm, num_stripes: int = 8, **kw):
        HandlerBase.__init__(self, **kw)
        self.cmap = cmap
        self.num_stripes = num_stripes

    def create_artists(
        self, legend, orig_handle, xdescent, ydescent, width, height, fontsize, trans
    ):
        stripes = []
        for i in range(self.num_stripes):
            s = Rectangle(
                [xdescent + i * width / self.num_stripes, ydescent],
                width / self.num_stripes,
                height,
                fc=self.cmap((2 * i + 1) / (2 * self.num_stripes)),
                transform=trans,
            )
            stripes.append(s)
        return stripes


def _save_plot_from_3d_array(
    filename: str,
    visu_data: Tuple[np.ndarray, ...],
    visu_keys: Tuple[str, ...],
    num_timestamp: int = 1,
):
    """Save plot from given 3D data.

    Args:
        filename (str): Filename.
        visu_data (Tuple[np.ndarray, ...]): Data that requires visualization.
        visu_keys (Tuple[str, ...]]): Keys for visualizing data. such as ["u", "v"].
        num_timestamp (int, optional): Number of timestamps coord/value contains. Defaults to 1.
    """

    fig = plt.figure(figsize=(10, 10))
    len_ts = len(visu_data[0]) // num_timestamp
    for t in range(num_timestamp):
        ax = fig.add_subplot(1, num_timestamp, t + 1, projection="3d")
        st = t * len_ts
        ed = (t + 1) * len_ts
        visu_data_t = [data[st:ed] for data in visu_data]
        cmaps = []
        for i, data in enumerate(visu_data_t):
            cmap = plt.get_cmap(CMAPS[i % len(CMAPS)])
            _colorline3d(data[:, 0], data[:, 1], data[:, 2], cmap=cmap, ax=ax)
            cmaps.append(cmap)
        cmap_handles = [Rectangle((0, 0), 1, 1) for _ in visu_keys]
        handler_map = dict(
            zip(cmap_handles, [HandlerColormap(cm, num_stripes=8) for cm in cmaps])
        )
        # Create custom legend with color map rectangels
        ax.legend(
            handles=cmap_handles,
            labels=visu_keys,
            handler_map=handler_map,
            loc="upper right",
            framealpha=0.95,
        )
        if num_timestamp == 1:
            fig.savefig(filename, dpi=300)
        else:
            fig.savefig(f"{filename}_{t}", dpi=300)

    if num_timestamp == 1:
        logger.info(f"3D result is saved to {filename}.png")
    else:
        logger.info(
            f"3D result is saved to {filename}_0.png"
            f" ~ {filename}_{num_timestamp - 1}.png"
        )


def save_plot_from_3d_dict(
    filename: str,
    data_dict: Dict[str, Union[np.ndarray, paddle.Tensor]],
    visu_keys: Tuple[str, ...],
    num_timestamp: int = 1,
):
    """Plot dict data as file.

    Args:
        filename (str): Output filename.
        data_dict (Dict[str, Union[np.ndarray, paddle.Tensor]]): Data in dict.
        visu_keys (Tuple[str, ...]): Keys for visualizing data. such as ["u", "v"].
        num_timestamp (int, optional): Number of timestamp in data_dict. Defaults to 1.
    """

    visu_data = [data_dict[k] for k in visu_keys]
    if isinstance(visu_data[0], paddle.Tensor):
        visu_data = [x.numpy() for x in visu_data]

    _save_plot_from_3d_array(filename, visu_data, visu_keys, num_timestamp)
