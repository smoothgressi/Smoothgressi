import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout,
    QFileDialog, QCheckBox, QComboBox, QWidget
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal


class BuildThread(QThread):
    build_complete = pyqtSignal(bool)

    def __init__(self, command):
        super().__init__()
        self.command = command

    def run(self):
        exit_code = os.system(self.command)
        self.build_complete.emit(exit_code == 0)


class PyInstallerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Utilitaire de build PyInstaller")
        self.setGeometry(100, 100, 600, 350)
        
        # Initialize paths
        self.script_path = ""
        self.files_and_folders = []
        self.output_folder = ""
        self.icon_path = ""  # <-- icône personnalisée
        
        # Main layout
        main_layout = QVBoxLayout()
        
        # Script selection
        self.script_label = QLabel("Sélectionez un script Python a build : ")
        main_layout.addWidget(self.script_label)
        
        self.select_script_button = QPushButton("Choisir un script")
        self.select_script_button.clicked.connect(self.select_script)
        main_layout.addWidget(self.select_script_button)
        
        # Files selection
        self.files_label = QLabel("Sélectionner des fichiers supplementaires a inclure : ")
        main_layout.addWidget(self.files_label)
        
        self.select_files_button = QPushButton("Choisir des fichiers")
        self.select_files_button.clicked.connect(self.select_files)
        main_layout.addWidget(self.select_files_button)
        
        # Output folder selection
        self.output_label = QLabel("Sélectionner le dossier de sortie : ")
        main_layout.addWidget(self.output_label)
        
        self.select_output_button = QPushButton("Choisir le dossier")
        self.select_output_button.clicked.connect(self.select_output_folder)
        main_layout.addWidget(self.select_output_button)

        # Icon selection
        self.icon_label = QLabel("Aucune icône sélectionnée")
        main_layout.addWidget(self.icon_label)

        self.select_icon_button = QPushButton("Choisir une icône (.ico)")
        self.select_icon_button.clicked.connect(self.select_icon)
        main_layout.addWidget(self.select_icon_button)
        
        # Dropdown for mode
        self.mode_label = QLabel("Mode de l'application : ")
        main_layout.addWidget(self.mode_label)
        
        self.mode_dropdown = QComboBox()
        self.mode_dropdown.addItem("Console")
        self.mode_dropdown.addItem("Windowed")
        main_layout.addWidget(self.mode_dropdown)
        
        # Onefile option
        self.onefile_checkbox = QCheckBox("Empaqueter en un seul fichier")
        main_layout.addWidget(self.onefile_checkbox)
        
        # Build button
        self.build_button = QPushButton("Construire l'executable")
        self.build_button.clicked.connect(self.build_executable)
        main_layout.addWidget(self.build_button)
        
        # Status label
        self.status_label = QLabel("Crée par colin524 pour le projet Smoothgressi")
        main_layout.addWidget(self.status_label)
        
        # Set main widget
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def select_script(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Python Script", "", "Python Files (*.py)")
        if file_path:
            self.script_path = file_path
            self.script_label.setText(f"Selected script: {os.path.basename(file_path)}")
    
    def select_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Files and Folders")
        if files:
            self.files_and_folders.extend(files)
            self.files_label.setText("Files/Folders selected: " + ", ".join([os.path.basename(f) for f in self.files_and_folders]))
    
    def select_output_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder_path:
            self.output_folder = folder_path
            self.output_label.setText(f"Output folder: {self.output_folder}")

    def select_icon(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Icon", "", "Icon Files (*.ico)")
        if file_path:
            self.icon_path = file_path
            self.icon_label.setText(f"Icône sélectionnée: {os.path.basename(file_path)}")
    
    def build_executable(self):
        if not self.script_path or not self.output_folder:
            self.status_label.setText("Veuillez sélectionner le script et le dossier de sortie.")
            return
        
        self.set_ui_enabled(False)
        self.setWindowTitle("Construction - Utilitaire de build PyInstaller")
        
        # Base command
        command = f"pyinstaller --distpath '{self.output_folder}' "
        
        if self.onefile_checkbox.isChecked():
            command += "--onefile "
        
        if self.mode_dropdown.currentText() == "Windowed":
            command += "--noconsole "
        
        # Ajout de l'icône si sélectionnée
        if self.icon_path:
            command += f"--icon '{self.icon_path}' "
        
        for item in self.files_and_folders:
            command += f"--add-data '{item};.' "
        
        command += f"'{self.script_path}'"
        
        self.status_label.setText("Construction en cours, veuillez patienter...")
        QApplication.processEvents()
        
        self.build_thread = BuildThread(command)
        self.build_thread.build_complete.connect(self.on_build_complete)
        self.build_thread.start()

    def on_build_complete(self, success):
        self.set_ui_enabled(True)
        self.setWindowTitle("Utilitaire de build PyInstaller")
        
        if success:
            self.status_label.setText("Votre fichier a été build avec succès ✅")
        else:
            self.status_label.setText("❌ Une erreur est survenue, vérifiez l'output pour plus d'infos.")

    def set_ui_enabled(self, enabled):
        self.build_button.setDisabled(not enabled)
        self.select_files_button.setDisabled(not enabled)
        self.select_output_button.setDisabled(not enabled)
        self.select_script_button.setDisabled(not enabled)
        self.select_icon_button.setDisabled(not enabled)
        self.mode_dropdown.setDisabled(not enabled)
        self.onefile_checkbox.setDisabled(not enabled)


if __name__ == "__main__":
    print("Utilitaire de compilation PyInstaller, crée par colin524 pour Smoothgressi")
    app = QApplication(sys.argv)
    window = PyInstallerGUI()
    window.show()
    sys.exit(app.exec_())
