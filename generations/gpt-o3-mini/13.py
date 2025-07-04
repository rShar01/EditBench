import tkinter as tk
import random

# Dimensioni della finestra e impostazioni iniziali
WIDTH, HEIGHT = 600, 600
UPDATE_DELAY = 20  # millisecondi
SPEED = 2  # velocità in pixel per aggiornamento

# Lista per tenere traccia di tutti i quadrati attivi
squares = []

class Square:
    def __init__(self, canvas, x, y, size):
        self.canvas = canvas
        self.size = size
        self.x = x
        self.y = y
        # assegna una direzione casuale (evita la direzione nulla)
        while True:
            self.dx = random.choice([-SPEED, -SPEED//2, SPEED//2, SPEED])
            self.dy = random.choice([-SPEED, -SPEED//2, SPEED//2, SPEED])
            if self.dx != 0 or self.dy != 0:
                break
        # crea il rettangolo sul canvas
        self.id = canvas.create_rectangle(x, y, x+size, y+size, fill=self.random_color())

    def random_color(self):
        # genera un colore casuale
        r = lambda: random.randint(0, 255)
        return f'#{r():02x}{r():02x}{r():02x}'

    def move(self):
        # aggiorna la posizione
        self.x += self.dx
        self.y += self.dy
        self.canvas.move(self.id, self.dx, self.dy)

    def get_coords(self):
        # restituisce le coordinate attuali
        return self.canvas.coords(self.id)

    def collides_with_wall(self):
        x1, y1, x2, y2 = self.get_coords()
        # controlla se il quadrato ha raggiunto o superato i bordi della finestra
        if x1 <= 0 or y1 <= 0 or x2 >= WIDTH or y2 >= HEIGHT:
            return True
        return False

def update():
    global squares
    # Crea una lista temporanea per evitare problemi di modifica durante l'iterazione
    for square in squares[:]:
        square.move()
        if square.collides_with_wall():
            # Elimina il quadrato dal canvas
            square.canvas.delete(square.id)
            squares.remove(square)
            # Calcola il nuovo lato dei quadrati (metà di quello corrente)
            new_size = square.size / 2
            # Calcola il centro del quadrato che ha colpito il muro
            cx = square.x + square.size / 2
            cy = square.y + square.size / 2
            new_x = cx - new_size / 2
            new_y = cy - new_size / 2
            # Genera 2 nuovi quadrati con le dimensioni dimezzate
            new_square1 = Square(square.canvas, new_x, new_y, new_size)
            new_square2 = Square(square.canvas, new_x, new_y, new_size)
            squares.append(new_square1)
            squares.append(new_square2)
    # Pianifica il prossimo aggiornamento
    root.after(UPDATE_DELAY, update)

# Codice invariato all'esterno della sezione evidenziata
root = tk.Tk()
root.title("Quadrati in movimento")

canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="white")
canvas.pack()

# Creazione del quadrato iniziale grande (ad es. dimensione 100)
initial_size = 100
initial_x = (WIDTH - initial_size) / 2
initial_y = (HEIGHT - initial_size) / 2
initial_square = Square(canvas, initial_x, initial_y, initial_size)
squares.append(initial_square)

# Avvia l'aggiornamento continuo
update()

root.mainloop()
