from .loader import load_raw, prepare_sensor_df
from .speed import add_speed_columns
from .distance import add_distance_columns
from .running_metrics import compute_running_metrics
from .trajectory import add_position_columns


def run_full_analysis(
    path,  # str | Path | file-like object (e.g. Streamlit's UploadedFile)
    device_name: str | None = None,
):
    """
    Full pipeline: load file → process → compute metrics.

    Parameters
    ----------
    path : str
        Path to a WitMotion TSV export file.
    device_name : str | None
        If the file contains multiple devices, pass the device name to
        analyse only that one. If None, all rows are used.

    Returns
    -------
    df : pd.DataFrame
        Processed DataFrame with speed, distance, and position columns added.
    metrics : dict
        Summary metrics dictionary.
    """
    df = load_raw(path)
    df = prepare_sensor_df(df, device_name=device_name)
    df = add_speed_columns(df)
    df = add_distance_columns(df)
    df = add_position_columns(df)
    metrics = compute_running_metrics(df)
    return df, metrics
