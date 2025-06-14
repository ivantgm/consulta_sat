import sys
import sqlite3
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem,
    QDateEdit, QPushButton, QLabel, QHBoxLayout, QSizePolicy, QMenu, QFrame, QLineEdit
)
from PySide6.QtCore import (
    Qt, QDate
)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class Dashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Conectar ao banco
        self.conn = sqlite3.connect("banco.db")
        self.cursor = self.conn.cursor()

        self.setWindowTitle("Cupom Fiscal - Dashboard")
        self.setGeometry(100, 100, 800, 600)

        # Widget principal
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Layout principal
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Layout de filtros
        self.filter_layout = QHBoxLayout()
        self.layout.addLayout(self.filter_layout)        

        # Filtros de data
        data_inicial = QDate.currentDate().addMonths(-3)
        data_inicial = QDate(
            data_inicial.year(),
            data_inicial.month(),
            1
        )
        
        self.data_i_layout = QVBoxLayout()
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDate(data_inicial)
        self.data_i_layout.addWidget(QLabel("Data Inicial:"))
        self.data_i_layout.addWidget(self.start_date_edit)
        self.filter_layout.addLayout(self.data_i_layout)
        
        data_f = QDate.currentDate()
        data_f = QDate(
            data_f.year(),
            data_f.month(),
            data_f.daysInMonth()
        )
        self.data_f_layout = QVBoxLayout()
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDate(data_f)
        self.data_f_layout.addWidget(QLabel("Data Final:"))
        self.data_f_layout.addWidget(self.end_date_edit)
        self.filter_layout.addLayout(self.data_f_layout)

        self.button_filtrar_layout = QHBoxLayout()
        self.filter_button = QPushButton("Filtrar")
        self.filter_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.filter_button.clicked.connect(self.load_data)
        self.button_filtrar_layout.addWidget(self.filter_button)
        self.filter_layout.addLayout(self.button_filtrar_layout)

        # Tabela de dados
        self.tables_layout = QHBoxLayout()
        self.layout.addLayout(self.tables_layout)

        self.table_layout = QVBoxLayout()
        self.table_layout.addWidget(QLabel("Agrupamento:"))
        self.table = QTableWidget()
        self.table_layout.addWidget(self.table)
        self.tables_layout.addLayout(self.table_layout, stretch=2)
        self.table.itemSelectionChanged.connect(self.get_cupons)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        self.table2_layout = QVBoxLayout()
        self.table2_layout.addWidget(QLabel(
            "Listagem analítica de cupons, clique com direito para mais opções.")
        )
        self.table2 = QTableWidget()
        self.table2_layout.addWidget(self.table2)
        self.tables_layout.addLayout(self.table2_layout, stretch=5)
        self.table2.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table2.customContextMenuRequested.connect(self.show_context_menu)

        # Gráfico
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)

        self.load_data()

    def show_context_menu(self, position):
        index = self.table2.indexAt(position)
        id_cupom = self.table2.item(index.row(), 4).text() if index.isValid() else None
        if id_cupom is not None:  
            menu = QMenu(self)
            action = menu.addAction("Ver itens do cupom")
            action.triggered.connect(lambda: self.on_row_action(id_cupom))
            menu.exec(self.table2.viewport().mapToGlobal(position))  

    def on_row_action(self, id_cupom):
        child = DashboardItens(parent=self, cursor=self.cursor, id_cupom=id_cupom)
        child.show()

    def get_cupons(self):
        
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            return
        
        SELECT_CUPOM = """
            select 
                substr(c.data_hora_emissao, 7, 2) || '/' ||
                substr(c.data_hora_emissao, 5, 2) || '/' ||
                substr(c.data_hora_emissao, 1, 4) as data,
                c.valor_total,
                e.fantasia,
                e.endereco,
                c.id
            from cupom c
            join emitente e on c.cnpj_emitente = e.cnpj
            where c.id in({})
            order by c.data_hora_emissao
        """
        filtro = self.table.item(selected_rows[0].row(), 3).text()
        self.cursor.execute(SELECT_CUPOM.format(filtro))
        rows = self.cursor.fetchall()

        # Atualizar tabela
        self.table2.setRowCount(len(rows))
        self.table2.setColumnCount(5)
        self.table2.setColumnHidden(4, True)
        self.table2.setHorizontalHeaderLabels(["Data", "Valor", "Emitente", "Endereço", "ID"])

        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                item = QTableWidgetItem(str(val))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                if j == 1:
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.table2.setItem(i, j, item)

        self.table2.resizeColumnsToContents()

    def load_data(self):

        data_inicio = self.start_date_edit.date().toPython()
        data_fim = self.end_date_edit.date().toPython()
        
        data_inicio = data_inicio.strftime("%Y%m%d000000")
        data_fim = data_fim.strftime("%Y%m%d235959")

        SELECT_CUPOM = """
            select                
                substr(c.data_hora_emissao, 5, 2) || '/' ||
                substr(c.data_hora_emissao, 1, 4) as data,   
                round(sum(c.valor_total), 2) as valor_total,
                count(c.id) as qtde_cupons,
                group_concat(c.id) as cupom_ids
            from cupom c
            where c.data_hora_emissao between ? and ?
            group by substr(c.data_hora_emissao, 1, 6)
            order by data
        """
        self.cursor.execute(SELECT_CUPOM, (data_inicio, data_fim))
        rows = self.cursor.fetchall()

        self.table.setRowCount(len(rows))
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Mês/Ano", "Valor", "Cupons", "cupom_ids"])
        self.table.setColumnHidden(3, True)
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                item = QTableWidgetItem(str(val))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                if j in [1, 2]:
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)                
                self.table.setItem(i, j, item)
        self.table.resizeColumnsToContents()
        self.plot_chart(rows)

    def plot_chart(self, data):
        self.figure.clear()
        ax1 = self.figure.add_subplot(111)

        nomes = [row[0] for row in data]
        valores = [row[1] for row in data]
        qtde_cupons = [row[2] for row in data]

        x = range(len(nomes))
        largura = 0.4

        # Primeiro eixo Y (valores)
        barras_valores = ax1.bar(
            [i - largura/2 for i in x], valores, width=largura, label='Valores', color='tab:blue'
        )
        ax1.set_ylabel("Valores", color='tab:blue')
        ax1.tick_params(axis='y', labelcolor='tab:blue')

        # Segundo eixo Y (cupons), compartilhando o mesmo eixo X
        ax2 = ax1.twinx()
        barras_cupons = ax2.bar(
            [i + largura/2 for i in x], qtde_cupons, width=largura, label='Cupons', color='tab:orange'
        )
        ax2.set_ylabel("Cupons", color='tab:orange')
        ax2.tick_params(axis='y', labelcolor='tab:orange')

        # Configurações do eixo X
        ax1.set_xticks(x)
        ax1.set_xticklabels(nomes)
        ax1.set_title("Cupons agrupados por mês/ano")

        self.canvas.draw()

class DashboardItens(QMainWindow):
    def __init__(self, parent, cursor, id_cupom):
        super().__init__(parent)        
        SELECT_CUPOM = """
            select                
                substr(c.data_hora_emissao, 7, 2) || '/' ||
                substr(c.data_hora_emissao, 5, 2) || '/' ||
                substr(c.data_hora_emissao, 1, 4) as data, 
                c.valor_total,
                c.cnpj_emitente,
                e.fantasia,
                e.endereco,
                c.chave_acesso
            from cupom c
            join emitente e on c.cnpj_emitente = e.cnpj
            where c.id = ?
        """
        cursor.execute(SELECT_CUPOM, (id_cupom,))
        row = cursor.fetchone()        
        self.setWindowTitle(f"Itens do cupom")

        self.setWindowFlags(
            Qt.Window |
            Qt.WindowStaysOnTopHint |
            Qt.WindowCloseButtonHint
        )
        self.setAttribute(Qt.WA_DeleteOnClose)
        
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        self.setCentralWidget(main_widget)
        client_panel = QFrame()
        client_layout = QVBoxLayout(client_panel)
        client_panel.setFrameShape(QFrame.Shape.StyledPanel)
        main_layout.addWidget(client_panel)

        row_layout = QHBoxLayout()
        client_layout.addLayout(row_layout)
        self.add_field(row_layout, "Data/Hora Emissão", row[0], stretch=1)
        self.add_field(row_layout, "Valor Total", str(row[1]), stretch=1)
        self.add_field(row_layout, "CNPJ", row[2], stretch=2)
        self.add_field(row_layout, "Fantasia", row[3], stretch=3)

        row_layout = QHBoxLayout()
        client_layout.addLayout(row_layout)        
        self.add_field(row_layout, "Endereço", row[4], stretch=3)
        self.add_field(row_layout, "Chave de Acesso", row[5], stretch=4)

        row_layout = QHBoxLayout()
        client_layout.addLayout(row_layout)
        self.table = QTableWidget()
        row_layout.addWidget(self.table)

        SELECT_CUPOM_ITENS = """            
            select 
                i.seq,
                i.codigo,
                i.descricao,                
                i.qtde,
                i.un,
                i.valor_unit,
                i.valor_total,
                i.desconto
            from cupom_item i
            where i.id_cupom = ?
            order by i.seq
        """
        cursor.execute(SELECT_CUPOM_ITENS, (id_cupom,))
        rows = cursor.fetchall()

        self.table.setRowCount(len(rows))
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Seq", "Código", "Descrição", "Qtde", "Un", 
            "Valor Unit", "Valor Total", "Desconto"
        ])

        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                item = QTableWidgetItem(str(val))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                if j in [3, 5, 6, 7]:  
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.table.setItem(i, j, item)
        self.table.resizeColumnsToContents()
        self.setMinimumWidth(800)



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



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Dashboard()
    window.show()
    sys.exit(app.exec())
