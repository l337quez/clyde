from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QSpacerItem, QSizePolicy)

class AboutTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.info_layout = QVBoxLayout()

        self.info_layout.setContentsMargins(0, 10, 0, 0)
        self.info_layout.setSpacing(0)

        self.version_label = QLabel(
            "<b>GNU Mau</b> is a cross-platform program (GNU Linux, Windows) that helps us <br> " 
            "organize tasks, credentials in projects. It is designed for backend and Devops developers.")
        self.version_label.setContentsMargins(10, 10, 0, 0)
        self.info_layout.addWidget(self.version_label)

        self.version_label = QLabel("<b>version:</b> v0.0.3 Alpha")
        self.version_label.setContentsMargins(10, 10, 0, 0)
        self.info_layout.addWidget(self.version_label)

        self.lisence_label = QLabel("<b>license:</b> GPL V3")
        self.lisence_label.setContentsMargins(10, 10, 0, 0) 
        self.info_layout.addWidget(self.lisence_label)


        self.project_description_label = QLabel("<b>packaged:</b> Ronal Forero")
        self.project_description_label.setContentsMargins(10, 10, 0, 0)  
        self.info_layout.addWidget(self.project_description_label)

        self.project_description_label = QLabel("<b>translated:</b> Ronal Forero")
        self.project_description_label.setContentsMargins(10, 10, 0, 0)  
        self.info_layout.addWidget(self.project_description_label)

        
        self.project_description_label = QLabel("<b>tested:</b> Kelly Gomez")
        self.project_description_label.setContentsMargins(10, 10, 0, 0)  
        self.info_layout.addWidget(self.project_description_label)

        self.project_description_label = QLabel("<b>designer:</b> Ronal Forero")
        self.project_description_label.setContentsMargins(10, 10, 0, 0)  
        self.info_layout.addWidget(self.project_description_label)

        self.project_description_label = QLabel("<b>development by:</b> Ronal Forero")
        self.project_description_label.setContentsMargins(10, 10, 0, 0)  
        self.info_layout.addWidget(self.project_description_label)

        self.info_layout.addStretch()
        self.setLayout(self.info_layout)
