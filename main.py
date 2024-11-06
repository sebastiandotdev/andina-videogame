import pygame
from os.path import join

pygame.init()
pygame.display.set_caption("Platformer")

WIDTH = 1000
HEIGHT = 800
FSP = 60
PLAYER_SPEED = 5

window = pygame.display.set_mode((WIDTH, HEIGHT))


def get_background(name: str):
    image = pygame.image.load(join("assets", name))
    _, _, width, height = image.get_rect()

    tiles = []

    for x in range(WIDTH // width + 1):
        for y in range(HEIGHT // height + 1):
            pos = (x * width, y * height)
            tiles.append(pos)

    return tiles, image


def draw(window, background, bg_image):
    for tile in background:
        window.blit(bg_image, tile)

    pygame.display.update()


def main(window):
    background, bg_image = get_background("blue.png")
    run = True

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
        draw(window, background, bg_image)

    pygame.quit()
    quit()


if __name__ == "__main__":
    main(window)
