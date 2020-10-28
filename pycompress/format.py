def format_bytes(size):
    power = 1024
    n = 0
    power_labels = {0: '', 1: 'k', 2: 'M'}
    while size > power:
        size /= power
        n += 1
    return f"{int(size)} {power_labels[n]}b"