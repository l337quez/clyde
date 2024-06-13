from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QSpacerItem, QSizePolicy)

class AboutTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.info_layout = QVBoxLayout()

        # Reducir márgenes y espaciado
        self.info_layout.setContentsMargins(0, 10, 0, 0)  # Sin márgenes alrededor del layout
        self.info_layout.setSpacing(0)  # Sin espacio entre widgets

        self.version_label = QLabel(
            "<b>GNU Clyde</b> is a cross-platform program (GNU Linux, Windows) that helps us <br> " 
            "organize tasks, credentials in projects. It is designed for backend and Devops developers.")
        self.version_label.setContentsMargins(10, 10, 0, 0)  # Sin márgenes alrededor de la etiqueta
        self.info_layout.addWidget(self.version_label)

        self.version_label = QLabel("<b>version:</b> v0.0.1 Alpha")
        self.version_label.setContentsMargins(10, 10, 0, 0)  # Sin márgenes alrededor de la etiqueta
        self.info_layout.addWidget(self.version_label)

        self.lisence_label = QLabel("<b>license:</b> GPL V3")
        self.lisence_label.setContentsMargins(10, 10, 0, 0)  # Sin márgenes alrededor de la etiqueta
        self.info_layout.addWidget(self.lisence_label)


        self.project_description_label = QLabel("<b>packaged:</b> Ronal Forero")
        self.project_description_label.setContentsMargins(10, 10, 0, 0)  # Sin márgenes alrededor de la etiqueta
        self.info_layout.addWidget(self.project_description_label)

        self.project_description_label = QLabel("<b>translated:</b> Ronal Forero")
        self.project_description_label.setContentsMargins(10, 10, 0, 0)  # Sin márgenes alrededor de la etiqueta
        self.info_layout.addWidget(self.project_description_label)

        
        self.project_description_label = QLabel("<b>tested:</b> Ronal Forero")
        self.project_description_label.setContentsMargins(10, 10, 0, 0)  # Sin márgenes alrededor de la etiqueta
        self.info_layout.addWidget(self.project_description_label)

        self.project_description_label = QLabel("<b>development by:</b> Ronal Forero")
        self.project_description_label.setContentsMargins(10, 10, 0, 0)  # Sin márgenes alrededor de la etiqueta
        self.info_layout.addWidget(self.project_description_label)

        # Agregar un espaciador al final para empujar todo hacia arriba
        self.info_layout.addStretch()

        self.setLayout(self.info_layout)
