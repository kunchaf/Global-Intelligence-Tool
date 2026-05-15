def format_population(number):
    """Converts a raw number into a readable string (e.g., 1.2M)"""
    if number is None or not isinstance(number, (int, float)):
        return "Unknown"
    
    if number >= 1_000_000_000:
        return f"{round(number / 1_000_000_000, 2)}B"
    elif number >= 1_000_000:
        return f"{round(number / 1_000_000, 1)}M"
    return f"{number:,}"

def calculate_percentage(part, total):
    """Safe percentage calculation to avoid division by zero"""
    try:
        return f"{round((part / total) * 100, 1)}%"
    except (ZeroDivisionError, TypeError):
        return "0%"