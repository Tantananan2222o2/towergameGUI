import pygame

class Disc:
    def __init__(self, size, image_path, peg_x, ground_y, index):
        self.size = size
        self.image = pygame.transform.scale(pygame.image.load(image_path), (110 - (10 * (5 - size)), 66 - (6 * (5 - size))))
        self.peg_x = peg_x
        self.pos = [peg_x - self.image.get_width() // 2 + 19, ground_y - (index * 15)]
        self.dragging = False
        self.falling = False
        self.target_y = None

    def draw(self, screen):
        screen.blit(self.image, tuple(self.pos))