import os

"""
icon_filepath = get_icon_path('some_icon.png')
print(icon_filepath)
"""

def get_icon_path(icon_name):
    current_dir = os.path.dirname(os.path.abspath(__file__))

    icon_path = os.path.join(current_dir, icon_name)

    icon_path = icon_path.replace("\\", "/")
    return icon_path
