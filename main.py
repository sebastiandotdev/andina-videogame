import pygame
import numpy as np

# Inicializamos Pygame
pygame.init()

# Configuración de pantalla y colores
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Juego estilo Mario con Transformaciones Lineales")
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Variables del personaje
character = pygame.Rect(100, 450, 40, 40)  # Rectángulo que representa al personaje
character_color = (0, 128, 255)
character_velocity_x = 0
character_velocity_y = 0
gravity = 0.5
is_jumping = False
scale_factor = 1.0
rotation_angle = 0

# Plataformas
platforms = [pygame.Rect(50, 500, 700, 20), pygame.Rect(400, 400, 150, 20)]

# Enemigo
enemy = pygame.Rect(600, 450, 40, 40)

# Función para aplicar transformaciones y dibujar al personaje
def draw_transformed_character(surface, rect, scale, angle):
    scaled_size = (int(rect.width * scale), int(rect.height * scale))
    transformed_surface = pygame.Surface(scaled_size, pygame.SRCALPHA)
    pygame.draw.rect(transformed_surface, character_color, transformed_surface.get_rect())
    
    # Rotación
    rotated_surface = pygame.transform.rotate(transformed_surface, angle)
    new_rect = rotated_surface.get_rect(center=rect.center)
    surface.blit(rotated_surface, new_rect)

# Ciclo principal del juego
running = True
while running:
    screen.fill(WHITE)  # Fondo blanco

    # Eventos del juego
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    keys = pygame.key.get_pressed()
    
    # Movimiento horizontal
    character_velocity_x = 0
    if keys[pygame.K_LEFT]:
        character_velocity_x = -5
    if keys[pygame.K_RIGHT]:
        character_velocity_x = 5
    
    # Saltar
    if keys[pygame.K_SPACE] and not is_jumping:
        character_velocity_y = -10
        is_jumping = True
    
    # Transformaciones aplicadas con teclas adicionales
    if keys[pygame.K_s]:
        scale_factor += 0.1  # Escalado
    if keys[pygame.K_d]:
        scale_factor = max(0.5, scale_factor - 0.1)
    if keys[pygame.K_r]:
        rotation_angle += 5  # Rotación en grados
    if keys[pygame.K_p]:
        character.y = HEIGHT - character.height  # Proyección en el suelo

    # Actualización de posición y gravedad
    character.x += character_velocity_x
    character_velocity_y += gravity
    character.y += character_velocity_y

    # Colisión con plataformas
    for platform in platforms:
        if character.colliderect(platform) and character_velocity_y >= 0:
            character.y = platform.y - character.height
            character_velocity_y = 0
            is_jumping = False

    # Colisión con enemigos y reflejo (rebote)
    if character.colliderect(enemy):
        character_velocity_x *= -1  # Invertimos la dirección (reflexión)

    # Dibujar plataformas y enemigos
    for platform in platforms:
        pygame.draw.rect(screen, BLACK, platform)
    pygame.draw.rect(screen, RED, enemy)  # Enemigo en rojo

    # Dibujamos al personaje con sus transformaciones
    draw_transformed_character(screen, character, scale_factor, rotation_angle)

    pygame.display.flip()  # Actualizamos la pantalla
    pygame.time.delay(30)

# Finalizamos Pygame
pygame.quit()
