def convert_path_separator(input_path):
    """
    Convert the path separator from a single backslash to double backslashes.

    Parameters:
    - input_path (str): The input file path with single backslashes.

    Returns:
    - str: The converted file path with double backslashes.
    """
    converted_path = input_path.replace('\\', r'\\\\')
    return converted_path