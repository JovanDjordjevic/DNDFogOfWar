import pygame
import sys
from tkinter import Tk, filedialog


class DNDFogOfWarAppState:
    def __init__(self):
        self.running = True
        self.left_mouse_down = False
        self.right_mouse_down = False
        self.x_offset = 0
        self.y_offset = 0


class DNDFogOfWarAppConfig:
    def __init__(self):
        self.brush_radius = 30
        self.image_movement_speed = 500
        self.zoom_in_scale = 1.1
        self.zoom_out_scale = 0.9
        self.framerate = 60


class DNDFogOfWarApp:
    def __init__(self):
        pygame.init()

        self.image = self.load_image()
        if not self.image:
            self.cleanup()

        self.original_image_width = self.image.get_width()
        self.original_image_height = self.image.get_height()

        self.screen_width = min(self.original_image_width, 1920)
        self.screen_height = min(self.original_image_height, 1080)
        self.screen = pygame.display.set_mode(
            (self.screen_width, self.screen_height), pygame.RESIZABLE
        )
        pygame.display.set_caption("DND Fog of War")

        self.black_layer = pygame.Surface(
            (self.original_image_width, self.original_image_height), pygame.SRCALPHA
        )
        self.black_layer.fill((0, 0, 0, 255))

        self.app_state = DNDFogOfWarAppState()
        self.app_config = DNDFogOfWarAppConfig()

    def load_image(self):
        Tk().withdraw()
        image_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")]
        )
        if image_path:
            image = pygame.image.load(image_path)
            print(
                f"Original image width: {image.get_width()}, height: {image.get_height()}"
            )
            return image
        return None

    def cleanup(self):
        pygame.quit()
        sys.exit()

    def resize_obj(self, obj, new_obj_width, new_obj_height):
        resized_obj = pygame.transform.scale(obj, (new_obj_width, new_obj_height))
        return resized_obj

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.app_state.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # left mouse button
                    self.app_state.left_mouse_down = True
                elif event.button == 3:  # right mouse button
                    self.app_state.right_mouse_down = True
                elif event.button == 4:  # mouse wheel up
                    self.image = pygame.transform.smoothscale(
                        self.image,
                        (
                            self.image.get_width() * self.app_config.zoom_in_scale,
                            self.image.get_height() * self.app_config.zoom_in_scale,
                        ),
                    )
                    self.black_layer = pygame.transform.scale(
                        self.black_layer,
                        (
                            self.black_layer.get_width()
                            * self.app_config.zoom_in_scale,
                            self.black_layer.get_height()
                            * self.app_config.zoom_in_scale,
                        ),
                    )
                elif event.button == 5:  # mouse wheel down
                    self.image = pygame.transform.smoothscale(
                        self.image,
                        (
                            self.image.get_width() * self.app_config.zoom_out_scale,
                            self.image.get_height() * self.app_config.zoom_out_scale,
                        ),
                    )
                    self.black_layer = pygame.transform.scale(
                        self.black_layer,
                        (
                            self.black_layer.get_width()
                            * self.app_config.zoom_out_scale,
                            self.black_layer.get_height()
                            * self.app_config.zoom_out_scale,
                        ),
                    )
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # left mouse button
                    self.app_state.left_mouse_down = False
                elif event.button == 3:  # right mouse button
                    self.app_state.right_mouse_down = False
            elif event.type == pygame.VIDEORESIZE:
                screen_width, screen_height = event.w, event.h
                self.screen = pygame.display.set_mode(
                    (screen_width, screen_height), pygame.RESIZABLE
                )

    def handle_pressed_keys(self):
        keys = pygame.key.get_pressed()
        offset = self.app_config.image_movement_speed / self.app_config.framerate

        if keys[pygame.K_LEFT]:
            self.app_state.x_offset += offset
        if keys[pygame.K_RIGHT]:
            self.app_state.x_offset -= offset
        if keys[pygame.K_UP]:
            self.app_state.y_offset += offset
        if keys[pygame.K_DOWN]:
            self.app_state.y_offset -= offset

    def update_surfaces(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()

        if self.app_state.left_mouse_down:
            pygame.draw.circle(
                self.black_layer,
                (0, 0, 0, 0),
                (mouse_x - self.app_state.x_offset, mouse_y - self.app_state.y_offset),
                self.app_config.brush_radius,
            )

        if self.app_state.right_mouse_down:
            pygame.draw.circle(
                self.black_layer,
                (0, 0, 0, 255),
                (mouse_x - self.app_state.x_offset, mouse_y - self.app_state.y_offset),
                self.app_config.brush_radius,
            )

    def redraw_all(self):
        # blit all surfaces and flip dispaly buffers
        self.screen.fill((100, 100, 100))
        self.screen.blit(self.image, (self.app_state.x_offset, self.app_state.y_offset))
        self.screen.blit(
            self.black_layer, (self.app_state.x_offset, self.app_state.y_offset)
        )
        pygame.display.flip()

    def run(self):
        clock = pygame.time.Clock()
        while self.app_state.running:
            clock.tick(self.app_config.framerate)
            self.handle_events()
            self.handle_pressed_keys()
            self.update_surfaces()
            self.redraw_all()
        self.cleanup()


if __name__ == "__main__":
    app = DNDFogOfWarApp()
    app.run()
