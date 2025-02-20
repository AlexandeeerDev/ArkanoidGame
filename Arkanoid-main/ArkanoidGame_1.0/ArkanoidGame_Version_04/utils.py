import pygame

def draw_text_centered(text, font, color, surface, x, y):
    """ Función para mostrar texto en pantalla y centrarlo """
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect(center=(x, y))
    surface.blit(text_obj, text_rect)
