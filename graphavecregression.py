import sys
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, 
                             QMenuBar, QMenu, QAction, QFileDialog, QTableWidget, QTableWidgetItem, 
                             QDialog, QDialogButtonBox, QFormLayout, QLineEdit, QComboBox, QPushButton, QLabel, 
                             QRadioButton, QButtonGroup, QHBoxLayout)
from PyQt5.QtCore import Qt, QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.style as mplstyle
import tkinter as tk
from tkinter import ttk
import pandas as pd

numero_version = "Beta-1"
numero_build = "4"

def show_splash():
    splash = tk.Tk()
    splash.title("Splash Screen")
    
    width, height = 300, 200
    screen_width = splash.winfo_screenwidth()
    screen_height = splash.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    splash.geometry(f"{width}x{height}+{x}+{y}")
    splash.attributes("-topmost", 1)
    splash.overrideredirect(True)

    image = tk.PhotoImage(file="./Assets/logo.png")
    label = tk.Label(splash, image=image)
    label.pack()
    
    label = ttk.Label(splash, text="Projet Smoothgressi", font=("Calibri Bold", 16))
    label.pack(expand=True)
    label = ttk.Label(splash, text=f"Version {numero_version} (build {numero_build})", font=("Calibri", 8))
    label.pack(expand=True)
    label = ttk.Label(splash, text="Démarrage en cours...", font=("Calibri", 10))
    label.pack(expand=True)

    splash.after(3500, lambda: [splash.destroy()])
    splash.mainloop()

class TableInputMethodDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Méthode d\'entrée des données')

        layout = QVBoxLayout()
        label = QLabel(f"Selectionnez une methode d'entrée des données")
        layout.addWidget(label)

        self.manual_radio = QRadioButton('Entrer les données manuellement')
        self.file_radio = QRadioButton('Importer depuis un fichier (Exel ou CSV)')
        self.manual_radio.setChecked(True)

        self.radio_group = QButtonGroup(self)
        self.radio_group.addButton(self.manual_radio)
        self.radio_group.addButton(self.file_radio)

        layout.addWidget(self.manual_radio)
        layout.addWidget(self.file_radio)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        layout.addWidget(self.buttonBox)

        self.setLayout(layout)

    def is_manual(self):
        return self.manual_radio.isChecked()

class StartupDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Bienvenue')
        
        self.create_radio = QRadioButton('Créer un nouveau graphique')
        self.edit_radio = QRadioButton('Modifier un graphique existant')
        self.create_radio.setChecked(True)

        self.radio_group = QButtonGroup(self)
        self.radio_group.addButton(self.create_radio)
        self.radio_group.addButton(self.edit_radio)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        
        layout = QVBoxLayout()
        label = QLabel(f"Bienvenue dans Projet Smoothgressi (ver .{numero_version}), veuillez choisir une option :")
        layout.addWidget(label)
        
        layout.addWidget(self.create_radio)
        layout.addWidget(self.edit_radio)
        layout.addWidget(self.buttonBox)

        self.setLayout(layout)

    def getChoice(self):
        return self.create_radio.isChecked()

class GraphApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f'Graphique X-Y - Projet Smoothgressi (ver. {numero_version})')
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)

        self.layout = QVBoxLayout(self.main_widget)
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)

        self.graph_title = ''
        self.x_label = ''
        self.x_unit = ''
        self.y_label = ''
        self.y_unit = ''
        self.x_values = []
        self.y_values = []
        self.regression_model = 'Affine'
        self.available_themes = [
            'Solarize_Light2', 'bmh', 'classic', 'dark_background', 'fast', 'fivethirtyeight', 'ggplot', 'grayscale', 
            'seaborn-v0_8', 'seaborn-v0_8-bright', 'seaborn-v0_8-colorblind', 'seaborn-v0_8-dark', 'seaborn-v0_8-dark-palette', 
            'seaborn-v0_8-darkgrid', 'seaborn-v0_8-deep', 'seaborn-v0_8-muted', 'seaborn-v0_8-notebook', 'seaborn-v0_8-paper', 
            'seaborn-v0_8-pastel', 'seaborn-v0_8-poster', 'seaborn-v0_8-talk', 'seaborn-v0_8-ticks', 'seaborn-v0_8-white', 
            'seaborn-v0_8-whitegrid', 'tableau-colorblind10'
        ]
        self.current_theme = 'classic'

        self.createMenu()
        self.resize(800, 600)

        QTimer.singleShot(500, self.showStartupDialog)

    def createMenu(self):
        menubar = self.menuBar()

        graph_menu = menubar.addMenu('Fichier')

        create_graph_action = QAction('Créer un graphique', self)
        create_graph_action.triggered.connect(self.openGraphSettingsDialog)
        graph_menu.addAction(create_graph_action)

        save_graph_action = QAction('Enregistrer le graphique', self)
        save_graph_action.triggered.connect(self.saveGraph)
        graph_menu.addAction(save_graph_action)

        load_graph_action = QAction('Charger un graphique', self)
        load_graph_action.triggered.connect(self.loadGraph)
        graph_menu.addAction(load_graph_action)

        regression_menu = menubar.addMenu('Régression')
        affine_action = QAction('Affine', self)
        affine_action.triggered.connect(lambda: self.setRegressionModel('Affine'))
        regression_menu.addAction(affine_action)

        linear_action = QAction('Linéaire', self)
        linear_action.triggered.connect(lambda: self.setRegressionModel('Linéaire'))
        regression_menu.addAction(linear_action)

        parabole_action = QAction('Parabole', self)
        parabole_action.triggered.connect(lambda: self.setRegressionModel('Parabole'))
        regression_menu.addAction(parabole_action)

        theme_menu = menubar.addMenu('Thème')
        for theme in self.available_themes:
            theme_action = QAction(theme, self)
            theme_action.triggered.connect(lambda checked, t=theme: self.changeTheme(t))
            theme_menu.addAction(theme_action)

        # Nouveau menu pour "Aide" avec "À propos"
        help_menu = menubar.addMenu('Aide')
        about_action = QAction('À propos', self)
        about_action.triggered.connect(self.showAboutDialog)
        help_menu.addAction(about_action)

    def showStartupDialog(self):
        startup_dialog = StartupDialog()
        if startup_dialog.exec_() == QDialog.Accepted:
            if startup_dialog.getChoice():
                self.openGraphSettingsDialog()
            else:
                self.loadGraph()

    def showAboutDialog(self):
        about_dialog = AboutDialog(self)
        about_dialog.exec_()

    def setRegressionModel(self, model):
        self.regression_model = model
        self.plotGraph(self.x_values, self.y_values)

    def changeTheme(self, theme):
        self.current_theme = theme
        mplstyle.use(theme)
        self.plotGraph(self.x_values, self.y_values)

    def openGraphSettingsDialog(self):
        settings_dialog = GraphSettingsDialog(self)
        if settings_dialog.exec_() == QDialog.Accepted:
            self.graph_title = settings_dialog.title_input.text()
            self.x_label = settings_dialog.x_label_input.text()
            self.x_unit = settings_dialog.x_unit_input.text()
            self.y_label = settings_dialog.y_label_input.text()
            self.y_unit = settings_dialog.y_unit_input.text()
            self.openTableDialog()

    def openTableDialog(self):
        # Ouvrir le choix entre saisie manuelle et import de fichier
        input_method_dialog = TableInputMethodDialog(self)
        if input_method_dialog.exec_() == QDialog.Accepted:
            if input_method_dialog.is_manual():
                # Si l'utilisateur choisit l'entrée manuelle, ouvrir la boîte de dialogue pour saisir les données
                dialog = TableInputDialog(self, self.x_label, self.y_label)
                if dialog.exec_() == QDialog.Accepted:
                    self.x_values, self.y_values = dialog.getValues()
                    self.plotGraph(self.x_values, self.y_values)
            else:
                # Si l'utilisateur choisit d'importer un fichier
                self.importDataFromFile()

    def importDataFromFile(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Importer les données", "", "Fichiers Excel (*.xlsx);;Fichiers CSV (*.csv)", options=options)
        
        if file_name:
            # Lire le fichier et extraire les deux premières colonnes
            if file_name.endswith('.xlsx'):
                data = pd.read_excel(file_name)
            elif file_name.endswith('.csv'):
                data = pd.read_csv(file_name)

            # Assurer que seules les deux premières colonnes sont prises et la première ligne est considérée comme titre et unité
            if len(data.columns) >= 2:
                self.x_values = data.iloc[1:, 0].astype(float).tolist()  # Convertir en float
                self.y_values = data.iloc[1:, 1].astype(float).tolist()
                self.x_label = data.columns[0]  # Titre pour l'axe X
                self.y_label = data.columns[1]  # Titre pour l'axe Y
                self.x_unit = data.iloc[0, 0]   # Unité pour l'axe X (première ligne)
                self.y_unit = data.iloc[0, 1]   # Unité pour l'axe Y (première ligne)

                self.plotGraph(self.x_values, self.y_values)
            else:
                print("Erreur : Le fichier doit contenir au moins deux colonnes.")

    def plotGraph(self, x, y):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.plot(x, y, 'o', label='Données')  
        ax.set_title(self.graph_title)
        ax.set_xlabel(f'{self.x_label} ({self.x_unit})')
        ax.set_ylabel(f'{self.y_label} ({self.y_unit})')
        ax.grid(True)

        if self.regression_model == 'Affine':
            self.plotAffineRegression(ax, x, y)
        elif self.regression_model == 'Linéaire':
            self.plotLinearRegression(ax, x, y)
        elif self.regression_model == 'Parabole':
            self.plotParabolaRegression(ax, x, y)

        self.canvas.draw()

    def plotAffineRegression(self, ax, x, y):
        coeffs = np.polyfit(x, y, 1)
        ax.plot(x, np.polyval(coeffs, x), label='Régression affine', color='red')
        ax.legend()

    def plotLinearRegression(self, ax, x, y):
        coeffs = np.polyfit(x, y, 1)
        ax.plot(x, np.polyval(coeffs, x), label='Régression linéaire', color='green')
        ax.legend()

    def plotParabolaRegression(self, ax, x, y):
        coeffs = np.polyfit(x, y, 2)
        ax.plot(x, np.polyval(coeffs, x), label='Régression parabolique', color='blue')
        ax.legend()

    def saveGraph(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Enregistrer le graphique", "", "Images (*.png);;PDF (*.pdf)", options=options)
        if file_name:
            self.figure.savefig(file_name)

    def loadGraph(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Charger un graphique", "", "Fichiers (*.png *.pdf)", options=options)
        if file_name:
            print("Graphique chargé :", file_name)

class GraphSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Paramètres du graphique')

        layout = QFormLayout()

        self.title_input = QLineEdit()
        self.x_label_input = QLineEdit()
        self.x_unit_input = QLineEdit()
        self.y_label_input = QLineEdit()
        self.y_unit_input = QLineEdit()

        layout.addRow('Titre du graphique:', self.title_input)
        layout.addRow('Axe X - Label:', self.x_label_input)
        layout.addRow('Axe X - Unité:', self.x_unit_input)
        layout.addRow('Axe Y - Label:', self.y_label_input)
        layout.addRow('Axe Y - Unité:', self.y_unit_input)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        layout.addWidget(self.buttonBox)
        self.setLayout(layout)

class TableInputDialog(QDialog):
    def __init__(self, parent=None, x_label='', y_label=''):
        super().__init__(parent)
        self.setWindowTitle('Entrée de données')

        layout = QVBoxLayout()
        self.table = QTableWidget(10, 2)
        self.table.setHorizontalHeaderLabels([x_label, y_label])
        layout.addWidget(self.table)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        layout.addWidget(self.buttonBox)

        self.setLayout(layout)

    def getValues(self):
        x_values = []
        y_values = []
        for row in range(self.table.rowCount()):
            x_item = self.table.item(row, 0)
            y_item = self.table.item(row, 1)
            if x_item and y_item:
                x_values.append(float(x_item.text()))
                y_values.append(float(y_item.text()))
        return x_values, y_values

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("À propos")

        layout = QVBoxLayout()

        about_label = QLabel(f"Projet Smoothgressi\nVersion : {numero_version}\nNumero de build : {numero_build}\nDévloppé par colin524, nopy234536758 et Tonboti")
        about_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(about_label)

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        buttonBox.accepted.connect(self.accept)
        layout.addWidget(buttonBox)

        self.setLayout(layout)

if __name__ == "__main__":
    show_splash()

    app = QApplication(sys.argv)
    window = GraphApp()
    window.show()
    sys.exit(app.exec_())
