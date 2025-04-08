class MapTile:
    def __init__(self, row: int, col: int):
        self.row = row
        self.col = col

    def __repr__(self):
        return f"MapTile(row={self.row}, col={self.col})"
