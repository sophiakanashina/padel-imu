def format_metrics(metrics: dict) -> str:
    """Return a human-readable string summary of computed metrics."""
    lines = [
        f"Duration:          {metrics['Duration (s)']:.1f} s",
        f"Total Distance:    {metrics['Total Distance (m)']:.2f} m",
        f"Max Speed:         {metrics['Max Speed (km/h)']:.2f} km/h",
        f"Average Speed:     {metrics['Average Speed (km/h)']:.2f} km/h  (while moving)",
        f"HSR Distance:      {metrics['HSR Distance (m)']:.2f} m  (> 6 km/h)",
        f"HSR Time:          {metrics['HSR Time (s)']:.2f} s",
        f"LSR Distance:      {metrics['LSR Distance (m)']:.2f} m  (≤ 6 km/h)",
        f"LSR Time:          {metrics['LSR Time (s)']:.2f} s",
    ]
    return "\n".join(lines)
