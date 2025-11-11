

def get_default_export_formats():
    from import_export.admin import base_formats
    """
    Return available export formats.
    """
    return (
        base_formats.XLS,
        base_formats.XLSX,
        base_formats.JSON
    )
