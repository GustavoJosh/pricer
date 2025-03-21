"""
Utility functions for the Sign Business application.
"""

def format_currency(value):
    """Format a value as currency with $ sign and 2 decimal places"""
    if value is None:
        return "-"
    return f"${value:.2f}"

def parse_currency(currency_str):
    """Parse a currency string to float, handling $ signs"""
    if not currency_str or currency_str == "-":
        return None
    return float(currency_str.replace("$", "").strip())

def validate_numeric_input(value_str):
    """Validate that a string can be converted to a number"""
    if not value_str or value_str.strip() == "":
        return None
    
    try:
        return float(value_str.strip())
    except ValueError:
        return False  # indicates error