from io import StringIO
from typing import IO

import numpy as np
import matplotlib
import matplotlib.pyplot as plt


def plot_histogram(input_file_name: str, url_like: str, method: str, output_file: IO[bytes]) -> None:
    with open(input_file_name, 'r') as f:
        s = f.read()
        s = s.replace('"', '')
        table = np.loadtxt(StringIO(s), dtype={  # type: ignore
            'names': ('time', 'target_processing_time', 'elb_status_code'),
            'formats': ('<U34', '<f', '<i4'),
        }, delimiter=',', skiprows=1)
    series = table['target_processing_time']
    upper_limit = np.percentile(series, 99.9)  # type: ignore
    counts, bins = np.histogram(series, bins=30, range=(0.0, upper_limit))  # type: ignore
    plt.hist(bins[:-1], bins, weights=counts)  # type: ignore
    matplotlib.style.use('bmh')
    plt.title(f'{url_like} [{method}] wo 99.9%')
    plt.xlabel('seconds')
    plt.ylabel('count')
    plt.savefig(output_file)  # type: ignore
    plt.close()
