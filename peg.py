import pygame

class Peg:
    def __init__(self, x, y, image_path):
        self.x = x
        self.y = y
        self.image = pygame.transform.scale(pygame.image.load(image_path), (40, 150))
        self.discs = []

    def add_disc(self, disc):
        self.discs.append(disc)

    def remove_disc(self, disc):
        self.discs.remove(disc)

    def get_top_disc(self):
        return self.discs[-1] if self.discs else None

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))
        for disc in self.discs:
            disc.draw(screen)