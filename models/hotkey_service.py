from pynput import keyboard
from PyQt6.QtCore import QThread, pyqtSignal

class GlobalHotKey(QThread) :
    triggered = pyqtSignal(str)
    
    def run(self) :
        text_input_combination = {keyboard.Key.alt, keyboard.KeyCode(char = "t")}
        
        current_key = set()
        
        def on_press(key) :
            if key == keyboard.Key.alt_l or key == keyboard.Key.alt_r :
                current_key.add(keyboard.Key.alt)
            elif hasattr(key, "char") and key.char is not None :
                key = keyboard.KeyCode(char = key.char.lower())
                current_key.add(key)
            else :
                current_key.add(key)

            if text_input_combination.issubset(current_key) :
                self.triggered.emit("text_input")
        
        def on_release(key) :
            if key == keyboard.Key.alt_l or key == keyboard.Key.alt_r :
                current_key.discard(keyboard.Key.alt)
            elif hasattr(key, "char") and key.char is not None :
                key = keyboard.KeyCode(char = key.char.lower())
                current_key.discard(key)
            else :
                current_key.discard(key)

        with keyboard.Listener(on_press = on_press, on_release = on_release) as listener :
            listener.join()