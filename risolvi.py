import sys
import time
from datetime import timedelta

class Nodo():
    def __init__(self, stato, genitore, azione):
        self.stato = stato
        self.genitore = genitore
        self.azione = azione


class FrontieraPila():
    def __init__(self):
        self.frontiera = []

    def add(self, nodo):
        self.frontiera.append(nodo)

    def contains_stato(self, stato):
        return any(nodo.stato == stato for nodo in self.frontiera)

    def empty(self):
        return len(self.frontiera) == 0

    def remove(self):
        if self.empty():
            raise Exception("empty frontier")
        else:
            nodo = self.frontiera[-1]
            self.frontiera = self.frontiera[:-1]
            return nodo


class FrontieraCoda(FrontieraPila):

    def remove(self):
        if self.empty():
            raise Exception("empty frontier")
        else:
            nodo = self.frontiera[0]
            self.frontiera = self.frontiera[1:]
            return nodo

class Maze():

    def __init__(self, nomeFile):
        
        # legge il file del labirinto e imposta altezza e larghezza del labirinto
        with open(nomeFile) as f:
            contenuti = f.read()

        # Verifica che il file contenga almeno uno stato inizial (= un ingresso) e uno finale (= una uscita)
        if contenuti.count("A") != 1:
            raise Exception("Un labirinto deve avere esattamente un punto di partenza")
        if contenuti.count("B") != 1:
            raise Exception("Un labirinto deve avere esattamente un obiettivo")

        # Calcola l'altezza e la larghezza del labirinto
        contenuti = contenuti.splitlines()
        self.altezza = len(contenuti)
        self.larghezza = max(len(line) for line in contenuti)

        # tiene traccia dei muri del labirinto
        self.muri = []
        for i in range(self.altezza):
            riga = []
            for j in range(self.larghezza):
                try:
                    if contenuti[i][j] == "A":
                        self.start = (i, j)
                        riga.append(False)
                    elif contenuti[i][j] == "B":
                        self.goal = (i, j)
                        riga.append(False)
                    elif contenuti[i][j] == " ":
                        riga.append(False)
                    else:
                        riga.append(True)
                except IndexError:
                    riga.append(False)
            self.muri.append(riga)

        self.solution = None


    def print(self):
        solution = self.solution[1] if self.solution is not None else None
        print()
        for i, riga in enumerate(self.muri):
            for j, col in enumerate(riga):
                if col:
                    print("█", end="")
                elif (i, j) == self.start:
                    print("A", end="")
                elif (i, j) == self.goal:
                    print("B", end="")
                elif solution is not None and (i, j) in solution:
                    print("*", end="")
                else:
                    print(" ", end="")
            print()
        print()


    def neighbors(self, stato):
        riga, col = stato
        candidati = [
            ("su", (riga - 1, col)),
            ("giu", (riga + 1, col)),
            ("sin", (riga, col - 1)),
            ("des", (riga, col + 1))
        ]

        risultato = []
        for azione, (r, c) in candidati:
            if 0 <= r < self.altezza and 0 <= c < self.larghezza and not self.muri[r][c]:
                risultato.append((azione, (r, c)))
        return risultato


    def solve(self,frontier):
        """Finds a solution to maze, if one exists."""
        
        # Keep track of number of statos explored
        self.num_explored = 0

        # Initialize frontier to just the starting position
        start = Nodo(stato=self.start, genitore=None, azione=None)
        # frontier = FrontieraPila()
        frontier.add(start)

        # Initialize an empty explored set
        self.explored = set()

        # Keep looping until solution found
        while True:

            # If nothing left in frontier, then no path
            if frontier.empty():
                raise Exception("no solution")

            # Choose a Nodo from the frontier
            Nodo = frontier.remove()
            self.num_explored += 1

            # If Nodo is the goal, then we have a solution
            if Nodo.stato == self.goal:
                aziones = []
                cells = []
                while Nodo.genitore is not None:
                    aziones.append(Nodo.azione)
                    cells.append(Nodo.stato)
                    Nodo = Nodo.genitore
                aziones.reverse()
                cells.reverse()
                self.solution = (aziones, cells)
                return

            # Mark Nodo as explored
            self.explored.add(Nodo.stato)

            # Add neighbors to frontier
            for azione, stato in self.neighbors(Nodo.stato):
                if not frontier.contains_stato(stato) and stato not in self.explored:
                    child = Nodo(stato=stato, genitore=Nodo, azione=azione)
                    frontier.add(child)


    def output_image(self, nomeFile, show_solution=True, show_explored=False):
        from PIL import Image, ImageDraw
        cell_size = 50
        cell_border = 2

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.larghezza * cell_size, self.altezza * cell_size),
            "black"
        )
        draw = ImageDraw.Draw(img)

        solution = self.solution[1] if self.solution is not None else None
        for i, riga in enumerate(self.muri):
            for j, col in enumerate(riga):

                # Walls
                if col:
                    fill = (40, 40, 40)

                # Start
                elif (i, j) == self.start:
                    fill = (255, 0, 0)

                # Goal
                elif (i, j) == self.goal:
                    fill = (0, 171, 28)

                # Solution
                elif solution is not None and show_solution and (i, j) in solution:
                    fill = (220, 235, 113)

                # Explored
                elif solution is not None and show_explored and (i, j) in self.explored:
                    fill = (212, 97, 85)

                # Empty cell
                else:
                    fill = (237, 240, 252)

                # Draw cell
                draw.rectangle(
                    ([(j * cell_size + cell_border, i * cell_size + cell_border),
                      ((j + 1) * cell_size - cell_border, (i + 1) * cell_size - cell_border)]),
                    fill=fill
                )

        img.save(nomeFile)


if len(sys.argv) != 2:
    sys.exit("Usage: python maze.py maze.txt")



m = Maze(sys.argv[1])
print("Maze:")
m.print()
print("Solving with FrontieraPila...")
start_time = time.time_ns()
m.solve(FrontieraPila())
print("statos Explored:", m.num_explored)
elapsed_time_secs = time.time_ns() - start_time
msg = "Execution took: %s microsecs (Wall clock time)" % timedelta(microseconds=round(elapsed_time_secs/1000))
print(msg)    
print("Solution:")
m.print()
m.output_image("maze-stack.png", show_explored=True)

print("Solving with FrontieraCoda...")
start_time = time.time_ns()
m.solve(FrontieraCoda())
print("statos Explored:", m.num_explored)
elapsed_time_secs = time.time_ns() - start_time
msg = "Execution took: %s microsecs (Wall clock time)" % timedelta(microseconds=round(elapsed_time_secs/1000))
print(msg)    
print("Solution:")
m.print()
m.output_image("maze-stack.png", show_explored=True)