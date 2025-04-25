from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QPushButton, QTableWidget, QLabel, QSplitter, QMessageBox, QTableWidgetItem
)
import sys
import selenium_sat
import json


class FormConsultaSAT(QMainWindow):
    cupons_lidos = list()
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Formulário de Consulta SAT")
        self.setGeometry(100, 100, 800, 600)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_splitter = QSplitter(Qt.Orientation.Vertical)
        main_layout.addWidget(main_splitter)        

        top_panel = QWidget()
        top_layout = QHBoxLayout(top_panel)
        main_layout.addWidget(top_panel)
        main_splitter.addWidget(top_panel)

        text_panel = QWidget()
        text_layout = QVBoxLayout(text_panel)
        top_layout.addWidget(text_panel)

        label = QLabel("Lista de chaves de acesso")
        label.setEnabled(False)
        text_layout.addWidget(label)

        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Digite aqui as chaves de acesso, uma por linha.")
        text_layout.addWidget(self.text_edit)

        button_panel = QWidget()
        button_layout = QVBoxLayout(button_panel)
        top_layout.addWidget(button_panel)

        self.consult_button = QPushButton("Consultar")
        button_layout.addWidget(self.consult_button)
        self.consult_button.clicked.connect(self.on_consult_button_clicked)

        client_panel = QWidget()
        client_layout = QVBoxLayout(client_panel)
        main_layout.addWidget(client_panel)
        main_splitter.addWidget(client_panel)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        client_layout.addWidget(splitter)

        self.table1 = QTableWidget(0, 4)  
        self.table1.setHorizontalHeaderLabels(["id", "Data Hora", "Valor", "Estabelecimento"])
        self.table1.itemSelectionChanged.connect(self.filtrar_table2)
        self.table1.setColumnHidden(0, True)
        self.table1.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        splitter.addWidget(self.table1)

        self.table2 = QTableWidget(0, 7)  
        self.table2.setHorizontalHeaderLabels(["id", "Seq", "Produto", "Qtde", "Un", "Valor Unit", "Valor Total"])
        self.table2.setColumnHidden(0, True)
        splitter.addWidget(self.table2)

        bottom_panel = QWidget()
        bottom_layout = QHBoxLayout(bottom_panel)
        bottom_layout.setAlignment(Qt.AlignmentFlag.AlignRight)  # Align buttons to the right
        main_layout.addWidget(bottom_panel)

        self.save_button = QPushButton("Salvar")
        bottom_layout.addWidget(self.save_button)
        self.save_button.clicked.connect(self.on_save_button_clicked)

        self.cancel_button = QPushButton("Cancelar")
        bottom_layout.addWidget(self.cancel_button)
        self.cancel_button.clicked.connect(self.on_cancel_button_clicked)

    def on_save_button_clicked(self):
        self.carregar_json_teste()

    def carregar_json_teste(self):
        with open('./json/35250447603246000111590012086000099842701376.json') as f:
            d = json.load(f)
            self.add_cupom_memoria(d)   
            
    def on_cancel_button_clicked(self):
        pass

    def on_consult_button_clicked(self): 
            keys = self.text_edit.toPlainText().splitlines()
            for key in keys:
                if key.strip():  
                    def call_back():
                        msg_box = QMessageBox(self)
                        msg_box.setIcon(QMessageBox.Information)
                        msg_box.setText("Informe o captcha e pesquise.\nVolte aqui e feche esta janela para eu processar o resultado.")
                        msg_box.setStandardButtons(QMessageBox.Close)
                        msg_box.setWindowTitle("Aguardando pesquisa")
                        msg_box.setModal(True)
                        msg_box.show()
                        app.processEvents() 
                        msg_box.exec()
                    self.add_cupom_memoria(selenium_sat.consulta_sat(key.strip(), call_back))    

    def add_cupom_memoria(self, cupom):
        self.cupons_lidos.append(cupom)
        row_position = self.table1.rowCount()
        self.table1.insertRow(row_position)
        self.table1.setItem(row_position, 0, QTableWidgetItem(str(len(self.cupons_lidos))))
        self.table1.setItem(row_position, 1, QTableWidgetItem(cupom['data_hora_emissao']))
        self.table1.setItem(row_position, 2, QTableWidgetItem(cupom['valor_total']))
        self.table1.setItem(row_position, 3, QTableWidgetItem(cupom['emitente']['fantasia']))
        self.table1.resizeColumnsToContents()

        for item in cupom['itens']:
            row_position = self.table2.rowCount()
            self.table2.insertRow(row_position)
            self.table2.setItem(row_position, 0, QTableWidgetItem(str(len(self.cupons_lidos))))
            self.table2.setItem(row_position, 1, QTableWidgetItem(item['seq']))
            self.table2.setItem(row_position, 2, QTableWidgetItem(item['descricao']))
            self.table2.setItem(row_position, 3, QTableWidgetItem(item['qtde']))
            self.table2.setItem(row_position, 4, QTableWidgetItem(item['un']))
            self.table2.setItem(row_position, 5, QTableWidgetItem(item['valor_unit'].replace("X\n", "")))
            self.table2.setItem(row_position, 6, QTableWidgetItem(item['valor_total']))
            
        self.table2.resizeColumnsToContents()

    def filtrar_table2(self):
        selected_rows = self.table1.selectionModel().selectedRows()
        if not selected_rows:
            return
        id = self.table1.item(selected_rows[0].row(), 0).text()
        for row in range(self.table2.rowCount()):
            item = self.table2.item(row, 0)
            self.table2.setRowHidden(row, item.text() != id)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FormConsultaSAT()
    window.show()
    sys.exit(app.exec())