from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFrame
)
import json

class FormGravarBanco(QMainWindow):
    cupom = None
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gravar Consulta SAT no Banco de Dados")
        self.setGeometry(100, 100, 600, 400)

        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        self.setCentralWidget(main_widget)

        client_panel = QFrame()
        client_layout = QVBoxLayout(client_panel)
        client_panel.setFrameShape(QFrame.Shape.StyledPanel)
        main_layout.addWidget(client_panel)

        row_layout = QHBoxLayout()
        client_layout.addLayout(row_layout)
        self.add_field(row_layout, "Data/Hora Emissão", "23/04/2025 - 11:12:22", stretch=6)
        self.add_field(row_layout, "Valor Total", "565,38", stretch=4)

        row_layout = QHBoxLayout()
        client_layout.addLayout(row_layout)
        self.add_field(row_layout, "Chave de Acesso", "35250447603246000111590010366852296731129035")        

        row_layout = QHBoxLayout()
        client_layout.addLayout(row_layout)
        self.add_field(row_layout, "CNPJ", "47.603.246/0001-11", stretch=4)
        self.add_field(row_layout, "Fantasia", "SUPERMERCADO MICHELASSI", stretch=6)

        row_layout = QHBoxLayout()
        client_layout.addLayout(row_layout)
        self.add_field(row_layout, "Endereço", "RUA GONCALVES DIAS, Nº 35 - Não Informado")

        row_layout = QHBoxLayout()
        client_layout.addLayout(row_layout)
        self.add_field(row_layout, "Bairro", "CENTRO", stretch=4)
        self.add_field(row_layout, "CEP", "17250-043", stretch=2)
        self.add_field(row_layout, "Município", "BARIRI", stretch=4)

        bottom_panel = QFrame()
        bottom_layout = QHBoxLayout(bottom_panel)
        bottom_panel.setFrameShape(QFrame.Shape.StyledPanel)
        main_layout.addWidget(bottom_panel)

        btn_save = QPushButton("Salvar")
        btn_cancel = QPushButton("Cancelar")
        bottom_layout.addWidget(btn_save)
        bottom_layout.addWidget(btn_cancel)

    def add_field(self, layout, label_text, default_value, stretch=0):
        field_layout = QVBoxLayout()
        label = QLabel(label_text)
        label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        edit = QLineEdit()
        edit.setText(default_value)
        edit.setObjectName(label_text)
        edit.setReadOnly(True)
        field_layout.addWidget(label)
        field_layout.addWidget(edit)

        if isinstance(layout, QHBoxLayout):
            container = QWidget()
            container.setLayout(field_layout)
            layout.addWidget(container, stretch)
        else:
            layout.addLayout(field_layout)
    
    def load(self, data):
        self.cupom = data
        self.findChild(QLineEdit, "Data/Hora Emissão").setText(data["data_hora_emissao"])
        self.findChild(QLineEdit, "Valor Total").setText(data["valor_total"])
        self.findChild(QLineEdit, "Chave de Acesso").setText(data["chave_acesso"])
        self.findChild(QLineEdit, "CNPJ").setText(data["emitente"]["cnpj"])
        self.findChild(QLineEdit, "Fantasia").setText(data["emitente"]["fantasia"])
        self.findChild(QLineEdit, "Endereço").setText(data["emitente"]["endereco"])
        self.findChild(QLineEdit, "Bairro").setText(data["emitente"]["bairro"])
        self.findChild(QLineEdit, "CEP").setText(data["emitente"]["cep"])
        self.findChild(QLineEdit, "Município").setText(data["emitente"]["municipio"])

if __name__ == "__main__":    
    with open('./json/35250447603246000111590012086000099842701376.json') as f:
        app = QApplication([])
        cupom = json.load(f)
        window = FormGravarBanco()
        window.load(cupom)
        window.show()
        app.exec()