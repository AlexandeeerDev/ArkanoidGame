import multiprocessing
import subprocess

def run_game():
    """Ejecuta la ventana principal del juego."""
    subprocess.run(["python", "main.py"])

def run_viewer():
    """Ejecuta la ventana secundaria para la visualización."""
    subprocess.run(["python", "viewer.py"])

if __name__ == "__main__":
    # Crear procesos para la ventana principal y la ventana de visualización
    p1 = multiprocessing.Process(target=run_game)
    p2 = multiprocessing.Process(target=run_viewer)

    # Iniciar ambos procesos
    p1.start()
    p2.start()

    # Esperar a que ambos procesos terminen
    p1.join()
    p2.join()
