from kivy.app import App#The line from kivy.app import App is used to import the App class from the kivy.app module. This App class is 
#essential when creating Kivy applications because it serves as the base class for your app.
from kivy.uix.widget import Widget#This imports the Widget class from the kivy.uix.widget module. The Widget class is the base class for 
#all UI elements in Kivy.
from kivy.graphics import Rectangle#This imports the Rectangle class from the kivy.graphics module. Rectangle is used for drawing 
#rectangular shapes.
from kivy.core.window import Window#This imports the Window class from the kivy.core.window module. Window provides access to window 
#management, including setting window size and position.
from kivy.clock import Clock#This imports the Clock class from the kivy.clock module. Clock is used for scheduling events and tasks to
#run at specific intervals.
from kivy.core.audio import SoundLoader#This imports the SoundLoader class from the kivy.core.audio module. SoundLoader is used to load 
#and play audio files.
from kivy.uix.label import CoreLabel#This imports the CoreLabel class from the kivy.uix.label module. CoreLabel is a lower-level label 
#class used for rendering text without the full overhead of a widget.
import random#This imports the built-in random module, which provides functions for generating random numbers and selecting random items.

# This class represents the main game environment.
# Initializes the widget and its parent class.
class GameWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Keyboard Setup
        #Requests access to the keyboard and binds keypress and key release events.
        self._keyboard = Window.request_keyboard(
            self._on_keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_key_down)
        self._keyboard.bind(on_key_up=self._on_key_up)
        
        # Score labal
        # Initializes a score label to display the score.
        self._score_label = CoreLabel(text="Score: 0",font_size=20)
        self._score_label.refresh()
        self._score = 0

        self.register_event_type("on_frame")
        # Canvas Setup
        # Draws the background and initializes a texture for the score label.
        with self.canvas:
            Rectangle(source="files/background.png", pos=(0, 0),
                      size=(Window.width, Window.height))
            self._score_instruction = Rectangle(texture=self._score_label.texture, pos=(
                0, Window.height - 50), size=self._score_label.texture.size)
        #  Key and Entity Storage
        # Tracks keys currently pressed and active game entities.
        self.keysPressed = set()
        self._entities = set()

        Clock.schedule_interval(self._on_frame, 0)

        self.sound = SoundLoader.load("files/music.wav")
        self.sound.play()

        Clock.schedule_interval(self.spawn_enemies, 2)

    def spawn_enemies(self, dt):
        for i in range(5):
            random_x = random.randint(0, Window.width)
            y = Window.height
            random_speed = random.randint(100, 300)
            self.add_entity(Enemy((random_x, y), random_speed))

    def _on_frame(self, dt):
        self.dispatch("on_frame", dt)

    def on_frame(self, dt):
        pass

    @property
    def score(self):
        return self._score

    @score.setter
    def score(self, value):
        self._score = value
        self._score_label.text = "Score: " + str(value)
        self._score_label.refresh()
        self._score_instruction.texture = self._score_label.texture
        self._score_instruction.size = self._score_label.texture.size

    def add_entity(self, entity):
        self._entities.add(entity)
        self.canvas.add(entity._instruction)

    def remove_entity(self, entity):
        if entity in self._entities:
            self._entities.remove(entity)
            self.canvas.remove(entity._instruction)

    def collides(self, e1, e2):
        r1x = e1.pos[0]
        r1y = e1.pos[1]
        r2x = e2.pos[0]
        r2y = e2.pos[1]
        r1w = e1.size[0]
        r1h = e1.size[1]
        r2w = e2.size[0]
        r2h = e2.size[1]

        if (r1x < r2x + r2w and r1x + r1w > r2x and r1y < r2y + r2h and r1y + r1h > r2y):
            return True
        else:
            return False

    def colliding_entities(self, entity):
        result = set()
        for e in self._entities:
            if self.collides(e, entity) and e != entity:
                result.add(e)
        return result

    def _on_keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_key_down)
        self._keyboard.unbind(on_key_up=self._on_key_up)
        self._keyboard = None

    def _on_key_down(self, keyboard, keycode, text, modifiers):
        self.keysPressed.add(keycode[1])

    def _on_key_up(self, keyboard, keycode):
        text = keycode[1]
        if text in self.keysPressed:
            self.keysPressed.remove(text)


class Entity(object):
    def __init__(self):
        self._pos = (0, 0)
        self._size = (50, 50)
        self._source = ""
        self._instruction = Rectangle(
            pos=self._pos, size=self._size, source=self._source)

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, value):
        self._pos = value
        self._instruction.pos = self._pos

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        self._size = value
        self._instruction.size = self._size

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, value):
        self._source = value
        self._instruction.source = self._source


class Bullet(Entity):
    def __init__(self, pos, speed=200):
        super().__init__()
        sound = SoundLoader.load("files/bullet.wav")
        sound.play()
        self._speed = speed
        self.pos = pos
        self.source = "files/bullet.png"
        game.bind(on_frame=self.move_step)

    def stop_callbacks(self):
        game.unbind(on_frame=self.move_step)

    def move_step(self, sender, dt):
        # check for collision/out of bounds
        if self.pos[1] > Window.height:
            self.stop_callbacks()
            game.remove_entity(self)
            return
        for e in game.colliding_entities(self):
            if isinstance(e, Enemy):
                game.add_entity(Explosion(self.pos))
                self.stop_callbacks()
                game.remove_entity(self)
                e.stop_callbacks()
                game.remove_entity(e)
                game.score += 1
                return

        # move
        step_size = self._speed * dt
        new_x = self.pos[0]
        new_y = self.pos[1] + step_size
        self.pos = (new_x, new_y)


class Enemy(Entity):
    def __init__(self, pos, speed=200):
        super().__init__()
        self._speed = speed
        self.pos = pos
        self.source = "files/enemy.png"
        game.bind(on_frame=self.move_step)

    def stop_callbacks(self):
        game.unbind(on_frame=self.move_step)

    def move_step(self, sender, dt):
        # check for collision/out of bounds
        if self.pos[1] < 0:
            self.stop_callbacks()
            game.remove_entity(self)
            game.score -= 1
            return
        for e in game.colliding_entities(self):
            if e == game.player:
                game.add_entity(Explosion(self.pos))
                self.stop_callbacks()
                game.remove_entity(self)
                game.score -= 1
                return

        # move
        step_size = self._speed * dt
        new_x = self.pos[0]
        new_y = self.pos[1] - step_size
        self.pos = (new_x, new_y)


class Explosion(Entity):
    def __init__(self, pos):
        super().__init__()
        self.pos = pos
        sound = SoundLoader.load("files/explosion.wav")
        self.source = "files/explosion.png"
        sound.play()
        Clock.schedule_once(self._remove_me, 0.1)

    def _remove_me(self, dt):
        game.remove_entity(self)


done = False


class Player(Entity):
    def __init__(self):
        super().__init__()
        self.source = "files/player (1).png"
        game.bind(on_frame=self.move_step)
        self._shoot_event = Clock.schedule_interval(self.shoot_step, 0.5)
        self.pos = (400, 0)

    def stop_callbacks(self):
        game.unbind(on_frame=self.move_step)
        self._shoot_event.cancel()

    def shoot_step(self, dt):
        # shoot
        if "spacebar" in game.keysPressed:
            x = self.pos[0]
            y = self.pos[1] + 50
            game.add_entity(Bullet((x, y)))

    def move_step(self, sender, dt):
        # move
        step_size = 200 * dt
        newx = self.pos[0]
        newy = self.pos[1]
        if "a" in game.keysPressed:
            newx -= step_size
        if "d" in game.keysPressed:
            newx += step_size
        self.pos = (newx, newy)


game = GameWidget()
game.player = Player()
game.player.pos = (Window.width - Window.width/3, 0)
game.add_entity(game.player)

player2 = Player()
player2.pos = (Window.width/3, 0)
game.add_entity(player2)

player3 = Player()
player3.pos = (Window.width/6,0)
game.add_entity(player3)

class MyApp(App):
    def build(self):
        return game


if __name__ == "__main__":
    app = MyApp()
    app.run()