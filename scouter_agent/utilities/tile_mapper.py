# Converts between screen coordinates and tile indices

class TileMapper:
    def __init__(self, tile_width, tile_height, origin):
        self.w = tile_width
        self.h = tile_height
        self.x0, self.y0 = origin

    def grid_to_screen(self, i, j):
        x = self.x0 + (self.w / 2) * (i - j)
        y = self.y0 + (self.h / 2) * (i + j)
        return int(x), int(y)

    def screen_to_grid(self, x, y):
        dx = x - self.x0
        dy = y - self.y0
        i = (dx / (self.w / 2) + dy / (self.h / 2)) / 2
        j = (dy / (self.h / 2) - dx / (self.w / 2)) / 2
        return int(round(i)), int(round(j))