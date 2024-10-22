import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, 
                             QMenuBar, QMenu, QAction, QFileDialog, QTableWidget, QTableWidgetItem, 
                             QDialog, QDialogButtonBox, QFormLayout, QLineEdit)
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import tkinter as tk

import tkinter as tk
from tkinter import ttk, messagebox


def show_splash():
    # Créer la fenêtre du splash screen
    splash = tk.Tk()
    splash.title("Splash Screen")
    
    # Taille et positionnement de la fenêtre de splash
    width, height = 300, 200
    screen_width = splash.winfo_screenwidth()
    screen_height = splash.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    splash.geometry(f"{width}x{height}+{x}+{y}")
    splash.attributes("-topmost", 1)
    splash.overrideredirect(True)

    # Load an image (PNG or GIF format)
    image = tk.PhotoImage(file="./Assets/logo.png")  # Replace with your image file

    # Create a label widget to display the image
    label = tk.Label(splash, image=image)
    label.pack()

    # Ajouter un message à la fenêtre de splash
    label = ttk.Label(splash, text="Projet Smoothgressi", font=("Calibri Bold", 16))
    label.pack(expand=True)
    label = ttk.Label(splash, text="Version Alpha-1 (build 1)", font=("Calibri", 8))
    label.pack(expand=True)
    label = ttk.Label(splash, text="Demmarage en cours...", font=("Calibri", 10))
    label.pack(expand=True)

    messagebox.showwarning("Version obsolete", "Cette version est obsolete et ne doit être utilisée que en cas de besoin")

    # Fixer la durée du splash (3000ms = 3 secondes)
    splash.after(3500, lambda: [splash.destroy()])

    splash.mainloop()


class GraphApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Graphique X-Y - Projet Smoothgressi (alpha-1)')
        
        # Création de l'interface principale avec un widget central
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)

        # Layout principal
        self.layout = QVBoxLayout(self.main_widget)

        # Canvas pour afficher le graphique
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)

        # Initialisation des données du graphique
        self.graph_title = ''
        self.x_label = ''
        self.x_unit = ''
        self.y_label = ''
        self.y_unit = ''
        self.x_values = []
        self.y_values = []

        # Création du menu
        self.createMenu()

        self.resize(800, 600)

    def createMenu(self):
        # Menu principal
        menubar = self.menuBar()

        # Menu "Graphique"
        graph_menu = menubar.addMenu('Fichier')

        # Action pour créer un graphique
        create_graph_action = QAction('Créer un graphique', self)
        create_graph_action.triggered.connect(self.openGraphSettingsDialog)
        graph_menu.addAction(create_graph_action)

        # Action pour enregistrer un graphique
        save_graph_action = QAction('Enregistrer le graphique', self)
        save_graph_action.triggered.connect(self.saveGraph)
        graph_menu.addAction(save_graph_action)

        # Action pour charger un graphique
        load_graph_action = QAction('Charger un graphique', self)
        load_graph_action.triggered.connect(self.loadGraph)
        graph_menu.addAction(load_graph_action)

    def openGraphSettingsDialog(self):
        # Ouvrir la fenêtre pour entrer les informations du graphique
        settings_dialog = GraphSettingsDialog(self)
        if settings_dialog.exec_() == QDialog.Accepted:
            # Récupérer les paramètres du graphique
            self.graph_title = settings_dialog.title_input.text()
            self.x_label = settings_dialog.x_label_input.text()
            self.x_unit = settings_dialog.x_unit_input.text()
            self.y_label = settings_dialog.y_label_input.text()
            self.y_unit = settings_dialog.y_unit_input.text()

            # Ouvrir la fenêtre pour entrer les valeurs après les paramètres du graphique
            self.openTableDialog()

    def openTableDialog(self):
        # Ouvrir la fenêtre pour entrer les valeurs et passer les noms des axes
        dialog = TableInputDialog(self, self.x_label, self.y_label)
        if dialog.exec_() == QDialog.Accepted:
            self.x_values, self.y_values = dialog.getValues()
            self.plotGraph(self.x_values, self.y_values)

    def plotGraph(self, x, y):
        # Effacer l'ancienne figure
        self.figure.clear()

        # Créer un nouvel axe et tracer le graphique
        ax = self.figure.add_subplot(111)
        ax.plot(x, y, marker='o')
        ax.set_title(self.graph_title)
        ax.set_xlabel(f'{self.x_label} ({self.x_unit})')
        ax.set_ylabel(f'{self.y_label} ({self.y_unit})')
        ax.grid(True)

        # Redessiner le canvas
        self.canvas.draw()

    def saveGraph(self):
        # Enregistrer le graphique dans un fichier
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Enregistrer le graphique", "", "Graphique X-Y (*.sgxy);;Tous les fichiers (*)", options=options)
        if file_name:
            with open(file_name, 'w') as file:
                # Sauvegarder les paramètres du graphique
                file.write(f"{self.graph_title}\n")
                file.write(f"{self.x_label}\n")
                file.write(f"{self.x_unit}\n")
                file.write(f"{self.y_label}\n")
                file.write(f"{self.y_unit}\n")
                # Sauvegarder les valeurs de X et Y
                file.write(' '.join(map(str, self.x_values)) + '\n')
                file.write(' '.join(map(str, self.y_values)) + '\n')

    def loadGraph(self):
        # Charger un graphique à partir d'un fichier
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Charger un graphique", "", "Graphique X-Y (*.sgxy);;Tous les fichiers (*)", options=options)
        if file_name:
            with open(file_name, 'r') as file:
                # Charger les paramètres du graphique
                self.graph_title = file.readline().strip()
                self.x_label = file.readline().strip()
                self.x_unit = file.readline().strip()
                self.y_label = file.readline().strip()
                self.y_unit = file.readline().strip()
                # Charger les valeurs de X et Y
                self.x_values = list(map(float, file.readline().strip().split()))
                self.y_values = list(map(float, file.readline().strip().split()))

                # Tracer le graphique avec les données chargées
                self.plotGraph(self.x_values, self.y_values)

class TableInputDialog(QDialog):
    def __init__(self, parent=None, x_label='X', y_label='Y'):
        super().__init__(parent)
        self.setWindowTitle('Entrer les valeurs dans le tableau')
        
        # Configuration de la table pour entrer les valeurs avec les noms des axes
        self.table = QTableWidget(5, 2)  # 5 lignes, 2 colonnes (X et Y)
        self.table.setHorizontalHeaderLabels([x_label, y_label])  # Noms des axes

        # Boutons OK et Annuler
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        
        # Disposition
        layout = QVBoxLayout()
        layout.addWidget(self.table)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)

    def accept(self):
        # Récupérer les valeurs saisies dans le tableau
        self.x_values = []
        self.y_values = []
        for row in range(self.table.rowCount()):
            x_item = self.table.item(row, 0)
            y_item = self.table.item(row, 1)
            if x_item and y_item:
                try:
                    x = float(x_item.text())
                    y = float(y_item.text())
                    self.x_values.append(x)
                    self.y_values.append(y)
                except ValueError:
                    continue
        super().accept()

    def getValues(self):
        return self.x_values, self.y_values

class GraphSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Créer un graphique')

        # Création des champs de saisie pour le titre et les axes
        self.title_input = QLineEdit()
        self.x_label_input = QLineEdit()
        self.x_unit_input = QLineEdit()
        self.y_label_input = QLineEdit()
        self.y_unit_input = QLineEdit()

        # Disposition des champs dans un formulaire
        layout = QFormLayout()
        layout.addRow('Titre du graphique:', self.title_input)
        layout.addRow('Nom de l\'axe des abscisses:', self.x_label_input)
        layout.addRow('Unité de l\'axe des abscisses:', self.x_unit_input)
        layout.addRow('Nom de l\'axe des ordonnées:', self.y_label_input)
        layout.addRow('Unité de l\'axe des ordonnées:', self.y_unit_input)

        # Boutons OK et Annuler
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        # Ajout des widgets au layout principal
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)

if __name__ == '__main__':
    show_splash()
    app = QApplication(sys.argv)
    window = GraphApp()
    window.show()
    sys.exit(app.exec_())
