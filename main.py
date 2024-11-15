import os
import random
import math
import pygame
from os import listdir
from os.path import isfile, join

pygame.init()

pygame.display.set_caption("Platformer")

WIDTH, HEIGHT = 1000, 800
FPS = 60
PLAYER_VEL = 5

window = pygame.display.set_mode((WIDTH, HEIGHT))


def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]


def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    path = join("assets", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path, f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0, 0), rect)
            sprites.append(pygame.transform.scale2x(surface))

        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites

    return all_sprites


def get_block(size):
    path = join("assets", "floor", "terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(96, 0, size, size)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)


class Player(pygame.sprite.Sprite):
    COLOR = (255, 0, 0)
    GRAVITY = 1
    GROWTH_SCALE = 5
    SPRITES = load_sprite_sheets("character", "main", 32, 32, True)
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.is_big = False
        self.hit_count = 0
        self.sprite = self.SPRITES["idle_left"][0]  # Set a default sprite
        self.update_sprite()  # Initialize sprite and mask

    def jump(self):
        self.y_vel = -self.GRAVITY * 8
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def make_hit(self):
        self.hit = True

    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def loop(self, fps):
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)

        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps * 2:
            self.hit = False
            self.hit_count = 0

        self.fall_count += 1

        # Verifica si el jugador ha aterrizado en el suelo y detén la caída
        if (
            self.rect.bottom >= HEIGHT - 50
        ):  # Suponiendo que el suelo está a una altura de 50 píxeles del fondo
            self.rect.bottom = HEIGHT - 50
            self.landed()

        self.update_sprite()

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0  # Reset vertical velocity when landing
        self.jump_count = 0  # Reset jump count

    def hit_head(self):
        self.count = 0
        self.y_vel *= -1

    def eat_apple(self):
        if not self.is_big:
            # Guardar el tamaño original
            self.original_width, self.original_height = (
                self.rect.width,
                self.rect.height,
            )
            bottom = self.rect.bottom

            # Doblar tamaño
            self.rect.width *= 2
            self.rect.height *= 2
            self.rect.bottom = bottom

            self.sprite = pygame.transform.scale(
                self.sprite, (self.rect.width, self.rect.height)
            )
            self.is_big = True
            self.update()

    def return_to_normal(self):
        if self.is_big:
            # Cambiar el estado y restaurar el tamaño
            self.is_big = False
            bottom = self.rect.bottom
            self.rect.width, self.rect.height = (
                self.original_width,
                self.original_height,
            )
            self.rect.bottom = bottom

            # Resetear todos los sprites a su tamaño original
            for key in self.SPRITES:
                self.SPRITES[key] = [
                    pygame.transform.scale(
                        sprite, (32, 32)
                    )
                    for sprite in self.SPRITES[key]
                ]

            # Asegúrate de actualizar la máscara para la nueva escala
            self.update()

    def update_sprite(self):
        sprite_sheet = "idle"
        if self.hit:
            sprite_sheet = "hit"
        elif self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"
        elif self.y_vel > self.GRAVITY * 2:
            sprite_sheet = "fall"
        elif self.x_vel != 0:
            sprite_sheet = "run"

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self, win, offset_x):
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))

        # Create reflection
        reflection = pygame.transform.flip(self.sprite, False, True)
        reflection.set_alpha(128)  # Make reflection semi-transparent

        # Calculate reflection position (below the character)
        reflection_y = (
            self.rect.bottom + 5
        )  # Add small gap between character and reflection

        # Draw the reflection
        win.blit(reflection, (self.rect.x - offset_x, reflection_y))


class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))


class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)  # Ensure the mask is correct


class Apple(Object):
    SPRITES = load_sprite_sheets("objects", "apple", 32, 32)

    def __init__(self, x, y):
        super().__init__(x, y, 32, 32)
        self.sprites = self.SPRITES["apple"]
        self.animation_count = 0
        self.image = self.sprites[self.animation_count]
        self.mask = pygame.mask.from_surface(self.image)
        self.speed = 2
        self.eaten = False

    def update(self, objects):
        if not self.eaten:
            # Caer
            self.rect.y += self.speed
            # Verifica la colisión con los objetos
            vertical_collide = handle_vertical_collision(self, objects, self.speed)
            if vertical_collide:
                self.speed = 0  # Detiene la caída cuando colisiona
            # Actualiza la animación
            self.animation_count += 1
            if self.animation_count >= len(self.sprites) * 10:
                self.animation_count = 0
            self.image = self.sprites[self.animation_count // 10]
            self.mask = pygame.mask.from_surface(self.image)

    def eat(self):
        self.eaten = True
        self.image = self.sprites[0]  # Manzana en estado comido
        self.mask = pygame.mask.from_surface(self.image)

    def draw(self, win, offset_x):
        if not self.eaten:
            win.blit(self.image, (self.rect.x - offset_x, self.rect.y))


class Tree(Object):
    def __init__(self, x, y):
        # Initialize with larger dimensions for the tree
        super().__init__(x, y, 64, 96)  # Adjust size as needed
        self.image = pygame.image.load(
            join("assets", "objects", "tree", "tree.png")
        ).convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.width, self.height))
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.bottom = HEIGHT - 85  # Ajusta según la altura del suelo


def get_background(name):
    # Cargar la imagen de fondo
    image = pygame.image.load(join("assets", "background", name))

    # Escalar la imagen a un cuarto de su tamaño original para que se vea mucho más lejana
    scaled_width = image.get_width() // 4
    scaled_height = image.get_height() // 4
    image = pygame.transform.scale(image, (scaled_width, scaled_height))

    tiles = []

    # Calcular el número de mosaicos necesarios para llenar la pantalla
    for i in range(WIDTH // scaled_width + 1):
        for j in range(HEIGHT // scaled_height + 1):
            pos = (i * scaled_width, j * scaled_height)
            tiles.append(pos)

    return tiles, image


def draw(window, background, bg_image, player, objects, offset_x):
    for tile in background:
        window.blit(bg_image, tile)

    for obj in objects:
        obj.draw(window, offset_x)

    player.draw(window, offset_x)

    pygame.display.update()


def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            if dy > 0:  # Moving downward (falling)
                player.rect.bottom = obj.rect.top
                # Only call landed() if the object is the player
                if isinstance(player, Player):
                    player.landed()  # Call to land method
                collided_objects.append(obj)
            elif dy < 0:  # Moving upward (hitting head)
                player.rect.top = obj.rect.bottom
                player.hit_head()  # Call to hit_head method
                collided_objects.append(obj)

    return collided_objects


def collide(player, objects, dx):
    player.move(dx, 0)
    player.update()
    collided_object = None
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            collided_object = obj
            break

    player.move(-dx, 0)
    player.update()
    return collided_object


def handle_move(player, objects):
    keys = pygame.key.get_pressed()

    player.x_vel = 0
    collide_left = collide(player, objects, -PLAYER_VEL * 2)
    collide_right = collide(player, objects, PLAYER_VEL * 2)

    if keys[pygame.K_LEFT] and not collide_left:
        player.move_left(PLAYER_VEL)
    if keys[pygame.K_RIGHT] and not collide_right:
        player.move_right(PLAYER_VEL)

    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)
    to_check = [collide_left, collide_right, *vertical_collide]


def main(window):
    clock = pygame.time.Clock()
    background, bg_image = get_background("selva.jpg")

    block_size = 96

    player = Player(100, 100, 50, 50)
    player.update()  # Ensure the mask is created for player
    apple = Apple(
        WIDTH // 2 - 16, HEIGHT - block_size * 2 - 32
    )  # Ajuste de posición para centrar en el camino
    # Create tree object
    tree = Tree(WIDTH - 200, HEIGHT - block_size - 96)  # Position the tree
    floor = [
        Block(i * block_size, HEIGHT - block_size, block_size)
        for i in range(-WIDTH // block_size, (WIDTH * 2) // block_size)
    ]
    objects = [
        *floor,
        Block(0, HEIGHT - block_size * 2, block_size),
        Block(block_size * 3, HEIGHT - block_size * 4, block_size),
        apple,
        tree,
    ]

    offset_x = 0
    scroll_area_width = 200

    all_sprites = pygame.sprite.Group()
    all_sprites.add(apple)

    run = True
    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.jump_count < 2:
                    player.jump()

        if apple:
            apple.update(objects)

        player.loop(FPS)
        handle_move(player, objects)
        draw(window, background, bg_image, player, objects, offset_x)

        if (
            apple
            and not apple.eaten
            and player.mask
            and apple.mask
            and pygame.sprite.collide_mask(player, apple)
        ):
            # Scale all sprites in the player's sprite sheet
            for key in player.SPRITES:
                player.SPRITES[key] = [
                    pygame.transform.scale(
                        sprite, (sprite.get_width() * 2, sprite.get_height() * 2)
                    )
                    for sprite in player.SPRITES[key]
                ]
            player.eat_apple()

            # Remove apple from objects list and mark as eaten
            objects.remove(apple)
            apple.eaten = True
            all_sprites.remove(apple)
            apple = None

            # Inside the main game loop
            if player.is_big and pygame.sprite.collide_mask(player, tree):
                player.return_to_normal()

        if (
            (player.rect.right - offset_x >= WIDTH - scroll_area_width)
            and player.x_vel > 0
        ) or ((player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
            offset_x += player.x_vel

    pygame.quit()
    quit()


if __name__ == "__main__":
    main(window)
