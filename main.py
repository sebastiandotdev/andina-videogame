import pygame
from os.path import join

"""
`pygame.init()` Inicializa el juego en Python
`pygame.display.set_caption("Platformer")` Guarda el titulo del juego
"""
pygame.init()
pygame.display.set_caption("Platformer")

"""
`WIDTH` and `HEIGHT` Son las dimesiones de la ventana del juego
`FSP` Son los frames por segundo
`PLAYER_SPEED` Son la velocidad del jugador
"""
WIDTH = 1000
HEIGHT = 800
FSP = 60
PLAYER_SPEED = 5

"""
`pygame.display.set_mode((WIDTH, HEIGHT))` Crea la ventana del juego
`window` Es la ventana del juego
"""
window = pygame.display.set_mode((WIDTH, HEIGHT))


"""
**Esta función es la que se encarga de cargar la imagen de fondo.**
**Cualquier imagen mientras se encuentre en la carpeta assets se cargará con esta función.**

`name`: Nombre del archivo de la imagen
`pygame.image.load(join("assets", name))`: Carga la imagen en memoria
`_, height, width, _ = image.get_rect()` Esto es para obtener la dimensiones de la imagen

- **La variable `tiles` es una lista de tuplas que contiene las posiciones de cada tile.**

**Tiles:** 
Un tile es un elemento de la imagen que se muestra en la ventana del juego.
Cada tile tiene una posición en la imagen y una posición en la ventana.
"""
def get_background(name: str):
    image = pygame.image.load(join("assets", name))
    _, _, width, height = image.get_rect()

    tiles = []

    """
    `for x in range(WIDTH // width + 1):` Esto es para obtener la cantidad de tiles en la imagen. Horizontales. 
    `for y in range(HEIGHT // height + 1):` Esto es para obtener la cantidad de tiles en la imagen. verticales.
    `pos = (x * width, y * height)` Esto es para obtener la posición de cada tile en la imagen. 
    `tiles.append(pos)` Esto es para agregar la posición de cada tile a la lista `tiles`.
    """
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
