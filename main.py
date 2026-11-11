import os
os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2'

from kivymd.app import MDApp

class ModbusClientApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark" 
        self.theme_cls.primary_palette = "Blue"
        pass

if __name__ == "__main__":
    ModbusClientApp().run()