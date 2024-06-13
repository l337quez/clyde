import subprocess
from PySide6.QtCore import QThread, Signal

class BackupThread(QThread):
    status_signal = Signal(str)
    finished_signal = Signal()

    def __init__(self, db_name, file_path, parent=None):
        super(BackupThread, self).__init__(parent)
        self.db_name = db_name
        self.file_path = file_path

    def run(self):
        try:
            # Ruta completa al ejecutable mongodump
            subprocess.run(['C:\\Program Files\\MongoDB\\Server\\7.0\\bin\\mongodump.exe', '--db', self.db_name, '--out', self.file_path], check=True)
            self.status_signal.emit(f"Respaldo guardado en: {self.file_path}")
        except subprocess.CalledProcessError as e:
            self.status_signal.emit(f"Error al respaldar la base de datos: {e}")
        except FileNotFoundError:
            self.status_signal.emit("Error: 'mongodump' no encontrado. Asegúrate de que está instalado y en el PATH.")
        self.finished_signal.emit()

class LoadThread(QThread):
    status_signal = Signal(str)
    finished_signal = Signal()

    def __init__(self, db_name, file_path, parent=None):
        super(LoadThread, self).__init__(parent)
        self.db_name = db_name
        self.file_path = file_path

    def run(self):
        try:
            # Ruta completa al ejecutable mongorestore
            subprocess.run(['C:\\ruta\\a\\tus\\ejecutables\\mongorestore.exe', '--drop', '--db', self.db_name, self.file_path], check=True)
            self.status_signal.emit(f"Respaldo cargado desde: {self.file_path}")
        except subprocess.CalledProcessError as e:
            self.status_signal.emit(f"Error al cargar el respaldo de la base de datos: {e}")
        except FileNotFoundError:
            self.status_signal.emit("Error: 'mongorestore' no encontrado. Asegúrate de que está instalado y en el PATH.")
        self.finished_signal.emit()
