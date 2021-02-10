from noise import pnoise1, pnoise2

class PerlinNoise:

    def __init__(self, seed=None, octaves=2, persistence=0.5, lacunarity=6, scale=1):
    
        self.seed = 200 if seed is None else seed
        self.octaves = octaves
        self.persistence = persistence
        self.lacunarity = lacunarity
        self.scale = scale

    def calc2d(self, norm_coord):

        return self.scale*pnoise2(
            norm_coord[0],
            norm_coord[1],
            octaves=self.octaves,
            persistence=self.persistence,
            lacunarity=self.lacunarity,
            repeatx=1,
            repeaty=1,
            base=self.seed)

    def calc1d(self, norm_coord):

        return self.scale*pnoise1(
            norm_coord,
            octaves=self.octaves,
            persistence=self.persistence,
            lacunarity=self.lacunarity,
            repeat=1,
            base=self.seed)
