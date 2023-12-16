from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty,ListProperty, BoundedNumericProperty, ObjectProperty
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.uix.image import Image
from kivy.lang import Builder
from kivy.core.window import Window
import random


kv_string = '''
<RunDinoGame>:
    canvas.before:
        Color:
            rgba: 0.5, 0.5, 1, 1  # Cor do fundo (azul claro, ajuste conforme necessário)
        Rectangle:
            pos: self.pos
            size: self.size
    
    Image:
        id: ground_image
        source: 'imagens/solo.png'
        pos: root.ground_pos[0], root.ground_pos[1] + 210
        size: self.texture_size

    Image:
        id: dino_image
        source: 'imagens/DinoRun1.png'
        pos: self.parent.center_x - self.width / 2-400, self.parent.center_y - self.height / 2-100
'''

Builder.load_string(kv_string)

# Configuração da janela
Window.size = (800, 600)

class Cloud(Image):
    velocity_x = NumericProperty(0)

    def move(self):
        self.x -= self.velocity_x
# Classe do Dinossauro
class Dino(Widget):
    velocity_x = BoundedNumericProperty(0, min=-10, max=10)
    velocity_y = BoundedNumericProperty(0, min=-10, max=10)

    def move(self):
        self.pos = Vector(self.velocity_x, self.velocity_y) + self.pos

        # Limita o movimento do dinossauro à tela
        if self.pos[1] < 0:
            self.pos[1] = 0

    def jump(self):
        self.velocity_y = 4  # Alterado para 4 para subir
        Clock.schedule_once(self.stop_jump, 0.5)  # Agendado para parar o salto após 0.5 segundos

    def stop_jump(self, dt):
        self.velocity_y = 0


# Classe do Jogo
class RunDinoGame(Widget):
    cloud_image_path = 'imagens/Nuvem.png'
    clouds = ListProperty([])
    ground_image_path = 'imagens/solo.png'
    dino_image_paths = ['imagens/DinoRun1.png', 'imagens/DinoRun2.png']
    current_dino_index = 0
    ground_speed = 2
    dino = ObjectProperty(None)
    ground_pos = ListProperty([0, 0])

    def __init__(self, **kwargs):
        super(RunDinoGame, self).__init__(**kwargs)
        self.ground_pos = [0, 0]
        Clock.schedule_interval(self.update, 1.0 / 60.0)
        Clock.schedule_interval(self.change_dino_image, 0.175)
        Clock.schedule_interval(self.spawn_clouds, 2.5)
    
    def spawn_clouds(self, dt):
        if all(cloud.x < -self.width for cloud in self.clouds):
            # Gera de 1 a 4 nuvens aleatoriamente
            num_clouds = random.randint(1, 4)

            # Adiciona nuvens à lista de nuvens
            for _ in range(num_clouds):
                cloud = Cloud(source=self.cloud_image_path)
                cloud.pos = (self.width + random.randint(50, 200), random.randint(self.height // 2, self.height))
                cloud.velocity_x = random.uniform(1, 4)  # Velocidade horizontal aleatória
                self.clouds.append(cloud)
                self.add_widget(cloud)

    def on_touch_down(self, touch):
        self.dino.jump()

    def update(self, dt):
        # Move o solo
        self.ground_pos[0] -= self.ground_speed
        if self.ground_pos[0] <= -self.width:
            self.ground_pos[0] = 0
        self.dino.move()
        for cloud in self.clouds:
            cloud.move()

            # Remove nuvens que saíram da tela
            if cloud.x > self.width:
                self.clouds.remove(cloud)
                self.remove_widget(cloud)

    def change_dino_image(self, dt):
        # Atualiza o caminho da imagem
        self.ids.dino_image.source = self.dino_image_paths[self.current_dino_index]

        # Avança para a próxima imagem na lista
        self.current_dino_index = (self.current_dino_index + 1) % len(self.dino_image_paths)

# Classe do Aplicativo
class RunDinoApp(App):
    def build(self):
        game = RunDinoGame()
        game.dino = Dino()
        return game

if __name__ == '__main__':
    RunDinoApp().run()
