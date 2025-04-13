class MapTile:
    def __init__(self, row: int, col: int, objects: list = None):
        self.row = row
        self.col = col
        self.objects = objects if objects is not None else []

    def __repr__(self):
        return f"MapTile(row={self.row}, col={self.col}, objects={self.objects})"