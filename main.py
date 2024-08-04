import pygame
import sys
from tkinter import Tk, filedialog
import logging

logger = logging.getLogger()

if not logger.hasHandlers():
    logger.addHandler(logging.StreamHandler())

logger.setLevel(logging.INFO)


class DNDFogOfWarAppState:
    def __init__(self):
        self.running = True
        self.left_mouse_down = False
        self.right_mouse_down = False
        self.x_offset = 0
        self.y_offset = 0
        self.brush_radius = 30
        self.current_zoom_level = 100
        self.displaying_legend = False


class DNDFogOfWarAppConfig:
    def __init__(self):
        self.min_brush_radius = 10
        self.max_brush_radius = 300
        self.brush_radius_increment = 10
        self.image_movement_speed = 500
        self.framerate = 60
        self.min_zoom_level = 25
        self.max_zoom_level = 175
        self.zoom_step = 25
        self.min_initial_screen_width = 1920
        self.min_initial_screen_height = 1080
        self.legend_font_size = 36


class DNDFogOfWarApp:
    def __init__(self):
        pygame.init()

        self.app_state = DNDFogOfWarAppState()
        self.app_config = DNDFogOfWarAppConfig()

        # load an image and create differently scaled copies of the same image
        # to use in order to avoid detail loss when zooming in/out
        self.zoom_level_to_image = {}
        self.prepare_images()

        self.image = self.zoom_level_to_image[100]

        self.original_image_width = self.image.get_width()
        self.original_image_height = self.image.get_height()

        self.screen_width = min(
            self.original_image_width, self.app_config.min_initial_screen_width
        )
        self.screen_height = min(
            self.original_image_height, self.app_config.min_initial_screen_height
        )
        self.resize_screen(self.screen_width, self.screen_height)
        pygame.display.set_caption("DND Fog of War")

        self.black_layer = pygame.Surface(
            (self.original_image_width, self.original_image_height), pygame.SRCALPHA
        )
        self.black_layer.fill((0, 0, 0, 255))

        self.legend_font = pygame.font.Font(None, self.app_config.legend_font_size)
        self.legent_text_lines = [
            "Legend:",
            "Toggle legend: L" "Move image around: Arrow keys",
            "Zoom in: MW up",
            "Zoom out: MW down",
            "Erase black layer: LMB",
            "Draw black layer: RMB",
            "Increase brush size: Shift + MW up",
            "Decrease brush size: Shift + MW down",
            "Rotate image 90 degrees: R",
        ]

    def resize_screen(self, new_screen_width, new_screen_height):
        logger.info(f"Resizing screen. {new_screen_width=} {new_screen_height=}")
        self.screen = pygame.display.set_mode(
            (new_screen_width, new_screen_height), pygame.RESIZABLE
        )

    def load_image(self):
        Tk().withdraw()

        image_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")]
        )

        if not image_path:
            self.cleanup()

        image = pygame.image.load(image_path)

        if not image:
            self.cleanup()

        logger.info(
            f"Loaded image: {image_path}. Original image width: {image.get_width()}, height: {image.get_height()}"
        )

        return image

    def prepare_images(self):
        self.original_image = self.load_image()
        original_image_width = self.original_image.get_width()
        original_image_height = self.original_image.get_height()

        for i in range(
            self.app_config.min_zoom_level,
            self.app_config.max_zoom_level + 1,
            self.app_config.zoom_step,
        ):
            scale_factor = i * 0.01
            self.zoom_level_to_image[i] = pygame.transform.smoothscale(
                self.original_image,
                (
                    original_image_width * scale_factor,
                    original_image_height * scale_factor,
                ),
            )

        logger.info(
            f"Prepared {len(self.zoom_level_to_image)} different zoom levels of the original image"
        )

    def cleanup(self):
        logger.info("Exiting application")
        pygame.quit()
        sys.exit()

    def zoom_surfaces(self, new_zoom_level):
        self.app_state.current_zoom_level = new_zoom_level

        self.image = self.zoom_level_to_image[self.app_state.current_zoom_level]
        self.black_layer = pygame.transform.scale(
            self.black_layer,
            (
                self.image.get_width(),
                self.image.get_height(),
            ),
        )

    def zoom_in(self):
        logger.info(
            f"Zooming in surfaces. Current zoom level: {self.app_state.current_zoom_level}"
        )

        new_zoom_level = self.app_state.current_zoom_level + self.app_config.zoom_step
        if new_zoom_level > self.app_config.max_zoom_level:
            logger.info("Zoom level already at maximum. Ignoring zoom in input")
            return

        self.zoom_surfaces(new_zoom_level)

        logger.info(
            f"Zoomed in surfaces. New current zoom level: {self.app_state.current_zoom_level}"
        )

    def zoom_out(self):
        logger.info(
            f"Zooming out surfaces. Current zoom level: {self.app_state.current_zoom_level}"
        )

        new_zoom_level = self.app_state.current_zoom_level - self.app_config.zoom_step
        if new_zoom_level < self.app_config.min_zoom_level:
            logger.info("Zoom level already at minimum. Ignoring zoom out input")
            return

        self.zoom_surfaces(new_zoom_level)

        logger.info(
            f"Zoomed out surfaces. New current zoom level: {self.app_state.current_zoom_level}"
        )

    def rotate_all(self):
        logger.info("Rotating surfaces")
        self.image = pygame.transform.rotate(self.image, 90)
        self.black_layer = pygame.transform.rotate(self.black_layer, 90)

    def toggle_legend(self):
        self.app_state.displaying_legend = not self.app_state.displaying_legend
        logger.info(f"Displaying legend: {self.app_state.displaying_legend}")

    def increase_brush_size(self):
        logger.info("Increasing brush size")
        self.app_state.brush_radius = min(
            self.app_config.max_brush_radius,
            self.app_state.brush_radius + self.app_config.brush_radius_increment,
        )
        logger.info(f"New brush size: {self.app_state.brush_radius}")

    def decrease_brush_size(self):
        logger.info("Decreasing brush size")
        self.app_state.brush_radius = max(
            self.app_config.min_brush_radius,
            self.app_state.brush_radius - self.app_config.brush_radius_increment,
        )
        logger.info(f"New brush size: {self.app_state.brush_radius}")

    def handle_mouse_button_down_event(self, event):
        logger.info("Registered mouse button down event")
        if event.button == 1:  # left mouse button
            self.app_state.left_mouse_down = True
        elif event.button == 3:  # right mouse button
            self.app_state.right_mouse_down = True

    def handle_mouse_button_up_event(self, event):
        logger.info("Registered mouse button up event")
        if event.button == 1:  # left mouse button
            self.app_state.left_mouse_down = False
        elif event.button == 3:  # right mouse button
            self.app_state.right_mouse_down = False

    def handle_mouse_wheel_event(self, event):
        logger.info("Registered mouse wheel")
        keys = pygame.key.get_pressed()
        if event.y > 0:  # mouse wheep up
            if keys[pygame.K_LSHIFT]:
                self.increase_brush_size()
            else:
                self.zoom_in()
        else:
            if keys[pygame.K_LSHIFT]:
                self.decrease_brush_size()
            else:
                self.zoom_out()

    def handle_key_down_event(self, event):
        logger.info(f"Registered key press event. Key: {pygame.key.name(event.key)}")
        if event.key == pygame.K_r:
            self.rotate_all()
        elif event.key == pygame.K_l:
            self.toggle_legend()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.app_state.running = False
            elif event.type == pygame.VIDEORESIZE:
                self.resize_screen(event.w, event.h)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mouse_button_down_event(event)
            elif event.type == pygame.MOUSEBUTTONUP:
                self.handle_mouse_button_up_event(event)
            elif event.type == pygame.MOUSEWHEEL:
                self.handle_mouse_wheel_event(event)
            elif event.type == pygame.KEYDOWN:
                self.handle_key_down_event(event)

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
                self.app_state.brush_radius,
            )

        if self.app_state.right_mouse_down:
            pygame.draw.circle(
                self.black_layer,
                (0, 0, 0, 255),
                (mouse_x - self.app_state.x_offset, mouse_y - self.app_state.y_offset),
                self.app_state.brush_radius,
            )

    def redraw_all(self):
        # blit all surfaces and flip dispaly buffers
        self.screen.fill((100, 100, 100))
        self.screen.blit(self.image, (self.app_state.x_offset, self.app_state.y_offset))
        self.screen.blit(
            self.black_layer, (self.app_state.x_offset, self.app_state.y_offset)
        )

        if self.app_state.displaying_legend:
            for i, text in enumerate(self.legent_text_lines):
                control_text = self.legend_font.render(text, True, (255, 255, 255))
                self.screen.blit(control_text, (20, 20 + i * 30))

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
