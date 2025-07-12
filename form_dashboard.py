import sys
import sqlite3
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem,
    QDateEdit, QPushButton, QLabel, QHBoxLayout, QSizePolicy, QMenu, QFrame, QLineEdit,
    QComboBox, QDialog, QCompleter
)
from PySide6.QtCore import (
    Qt, QDate
)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from prettytable import PrettyTable
import pyperclip

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

        self.locate_button = QPushButton("Localizar")
        self.locate_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.locate_button.clicked.connect(self.locate)
        self.button_filtrar_layout.addWidget(self.locate_button)

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
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.table_show_context_menu)

        self.table2_layout = QVBoxLayout()
        self.table2_layout.addWidget(QLabel(
            "Listagem analítica de cupons:")
        )
        self.table2 = QTableWidget()
        self.table2_layout.addWidget(self.table2)
        self.tables_layout.addLayout(self.table2_layout, stretch=5)
        self.table2.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table2.customContextMenuRequested.connect(self.table2_show_context_menu)

        # Gráfico
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)

        self.load_data()

    def table_show_context_menu(self, position):
        index = self.table.indexAt(position)
        id_list = self.table.item(index.row(), 3).text() if index.isValid() else None
        if id_list is not None:  
            menu = QMenu(self)
            action = menu.addAction("Produtos por Valor - Gráfico Pizza")
            action.triggered.connect(lambda: self.table_grafico_pizza(id_list))
            action = menu.addAction("Produtos por Valor - Tabela")
            action.triggered.connect(lambda: self.table_produtos_valor(id_list))
            menu.exec(self.table.viewport().mapToGlobal(position))

    def table2_show_context_menu(self, position):
        index = self.table2.indexAt(position)
        id_cupom = self.table2.item(index.row(), 4).text() if index.isValid() else None
        if id_cupom is not None:  
            menu = QMenu(self)
            action = menu.addAction("Ver itens do cupom")
            action.triggered.connect(lambda: self.table2_ver_itens(id_cupom))
            menu.exec(self.table2.viewport().mapToGlobal(position))  
    
    def table_grafico_pizza(self, id_list):
        child = DashboardPie(parent=self, cursor=self.cursor, id_list=id_list)
        child.show()

    def table_produtos_valor(self, id_list):
        child = DashboardProdutosValor(parent=self, cursor=self.cursor, id_list=id_list)
        child.show()

    def table2_ver_itens(self, id_cupom):
        child = DashboardItens(parent=self, cursor=self.cursor, id_cupom=id_cupom)
        child.show()

    def get_cupons(self, filtro=None):
        
        if filtro is None:
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
        if filtro is None:
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

    def locate(self):
        dialog = DashboardLocalizar(parent=self, cursor=self.cursor)
        if dialog.exec():  
            data_inicio = dialog.input_data_inicial.date().toPython().strftime("%Y%m%d000000")
            data_fim = dialog.input_data_final.date().toPython().strftime("%Y%m%d235959")
            cnpj_emitente = dialog.combo_emitente.currentData() 
            produto = dialog.input_produto.text()
            chave_acesso = dialog.input_chave_acesso.text() 

            produto_condition = ""
            if produto:
                palavras = produto.split()
                produto_condition = " and (" + " or ".join(
                    f"i.descricao like '%{palavra}%'" for palavra in palavras 
                ) + ")"

            SELECT_CUPOM = """
                select group_concat(c.id)
                from cupom c
                left outer join cupom_item i on i.id_cupom = c.id
                where (1)
                {}
                {}
                {}
                {}
            """.format(
                f"and c.data_hora_emissao between '{data_inicio}' and '{data_fim}'",
                f"and c.cnpj_emitente = '{cnpj_emitente}'" if cnpj_emitente else "",
                f"and c.chave_acesso = '{chave_acesso}'" if chave_acesso else "",
                produto_condition
            )
            self.cursor.execute(SELECT_CUPOM)
            id_list = self.cursor.fetchone()[0]
            self.get_cupons(filtro=id_list)  

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
                i.desconto,
                round(i.valor_total - i.desconto, 2) as valor_liquido
            from cupom_item i
            where i.id_cupom = ?
            order by i.seq
        """
        cursor.execute(SELECT_CUPOM_ITENS, (id_cupom,))
        rows = cursor.fetchall()

        self.table.setRowCount(len(rows))
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "Seq", "Código", "Descrição", "Qtde", "Un", 
            "Valor Unit", "Valor Total", "Desconto", "Valor Líquido"
        ])
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                item = QTableWidgetItem(str(val))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                if j in [3, 5, 6, 7, 8]:  
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.table.setItem(i, j, item)
        self.table.resizeColumnsToContents()
        self.setMinimumWidth(800)

        btn_copy = QPushButton("Copiar Tabela")
        def copy_table():
            count_selected = 0
            for row in range(self.table.rowCount()):
                if self.table.item(row, 0).isSelected():
                    count_selected += 1            

            table = PrettyTable()            
            headers = [self.table.horizontalHeaderItem(i).text() for i in range(self.table.columnCount())]
            table.field_names = headers
            for row in range(self.table.rowCount()):
                if count_selected != 0:
                    if not self.table.item(row, 0).isSelected():
                        continue
                row_data = []
                for col in range(self.table.columnCount()):
                    item = self.table.item(row, col)
                    row_data.append(item.text() if item else "")
                table.add_row(row_data)
            total_liquido = 0
            for row in range(self.table.rowCount()):
                if count_selected != 0:
                    if not self.table.item(row, 0).isSelected():
                        continue
                item = self.table.item(row, 8)
                if item:
                    try:
                        total_liquido += float(item.text().replace(',', '.'))
                    except ValueError:
                        pass
            total_row = [""] * self.table.columnCount()
            total_row[2] = "TOTAL"
            total_row[8] = f"{total_liquido:.2f}"
            table.add_row(["-" * len(h) for h in headers])
            table.add_row(total_row)

            for idx, header in enumerate(headers):
                if idx in [3, 5, 6, 7, 8]:
                    table.align[header] = "r"
                else:
                    table.align[header] = "l"
            pyperclip.copy(table.get_string())

        btn_copy.clicked.connect(copy_table)
        main_layout.addWidget(btn_copy)

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

class DashboardPie(QMainWindow):
    def __init__(self, parent, cursor, id_list):
        super().__init__(parent)
        
        SELECT_PRODUTOS = """
            select 
                i.descricao,
                sum(valor_total-desconto) as total
            from cupom_item i
            where i.id_cupom in ({})
            group by i.descricao
            order by total desc
        """.format(id_list)

        cursor.execute(SELECT_PRODUTOS)
        rows = cursor.fetchall()

        self.setWindowTitle("Produtos por Valor")
        self.setWindowFlags(
            Qt.Window |
            Qt.WindowStaysOnTopHint |
            Qt.WindowCloseButtonHint
        )
        self.setAttribute(Qt.WA_DeleteOnClose)

        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        self.setCentralWidget(main_widget)

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        main_layout.addWidget(self.canvas)

        ax = self.figure.add_subplot(111)
        ax.clear()

        nomes = [row[0] for row in rows]
        valores = [row[1] for row in rows]
        TOP = 9  # Número máximo de produtos a serem exibidos
        n = [nome for i, nome in enumerate(nomes) if i < TOP]
        v = [valor for i, valor in enumerate(valores) if i < TOP]
        n.append("Outros")
        v.append(sum(valores) - sum(v))

        ax.pie(v, labels=n, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')        

        self.canvas.draw()
        self.resize(800, 600)

class DashboardProdutosValor(QMainWindow):
    def __init__(self, parent, cursor, id_list):
        super().__init__(parent)
        
        SELECT_PRODUTOS = """
            select 
                i.codigo,
                i.descricao,
                round(sum(valor_total-desconto), 2) as total,
                round(sum(qtde), 3) as qtde,
                count(i.codigo) as vezes,
                count(distinct i.id_cupom) as cupons
            from cupom_item i
            where i.id_cupom in ({})
            group by i.descricao
            order by total desc
        """.format(id_list)

        cursor.execute(SELECT_PRODUTOS)
        rows = cursor.fetchall()
        self.setWindowTitle("Produtos por Valor")
        self.setWindowFlags(
            Qt.Window |
            Qt.WindowStaysOnTopHint |
            Qt.WindowCloseButtonHint
        )
        self.setAttribute(Qt.WA_DeleteOnClose)

        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        self.setCentralWidget(main_widget)
        
        self.table = QTableWidget()
        main_layout.addWidget(self.table)

        self.table.setRowCount(len(rows))
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Código", "Produto", "Total", "Qtde", "Vezes", "Cupons"])
        self.table.setColumnWidth(0, 300)
        self.table.setColumnWidth(1, 100)  
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                item = QTableWidgetItem(str(val))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                if j in [2, 3, 4, 5]:
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.table.setItem(i, j, item)
        self.table.resizeColumnsToContents()
        self.resize(800, 600)

class DashboardLocalizar(QDialog):
    def __init__(self, parent, cursor):
        super().__init__(parent)
        self.cursor = cursor
        self.setWindowTitle("Pesquisa de Cupons")
        self.setModal(True)

        layout_principal = QVBoxLayout(self)
        painel_client = QWidget()
        layout_client = QVBoxLayout(painel_client)
        
        data_i = QDate.currentDate().addMonths(-3)
        data_i = QDate(
            data_i.year(),
            data_i.month(),
            1
        ) 
        data_f = QDate.currentDate()
        data_f = QDate(
            data_f.year(),
            data_f.month(),
            data_f.daysInMonth()
        )               
        # linha com o periodo
        layout = QHBoxLayout()        
        field_layout = QVBoxLayout()
        lbl_data_inicial = QLabel("Data Inicial:")
        self.input_data_inicial = QDateEdit()
        self.input_data_inicial.setCalendarPopup(True)
        self.input_data_inicial.setDate(data_i)
        field_layout.addWidget(lbl_data_inicial)
        field_layout.addWidget(self.input_data_inicial)
        container = QWidget()
        container.setLayout(field_layout) 
        layout.addWidget(container, 1)
        # ----------
        field_layout = QVBoxLayout()
        lbl_data_final = QLabel("Data Final:")
        self.input_data_final = QDateEdit()
        self.input_data_final.setCalendarPopup(True)
        self.input_data_final.setDate(data_f)
        field_layout.addWidget(lbl_data_final)
        field_layout.addWidget(self.input_data_final)
        container = QWidget()
        container.setLayout(field_layout)         
        layout.addWidget(container, 1)
        # ----------
        layout_client.addLayout(layout)
        # fim da linha com o periodo

        lbl_emitente = QLabel("Emitente:")
        self.combo_emitente = QComboBox()
        self.get_emitentes()
        layout_client.addWidget(lbl_emitente)
        layout_client.addWidget(self.combo_emitente)

        lbl_produto = QLabel("Produto:")
        self.input_produto = QLineEdit()
        layout_client.addWidget(lbl_produto)
        layout_client.addWidget(self.input_produto)
        lista_produtos = self.get_produtos()

        completer = QCompleter(lista_produtos)
        completer.setFilterMode(Qt.MatchContains)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.input_produto.setCompleter(completer)

        lbl_chave_acesso = QLabel("Chave de Acesso:")
        self.input_chave_acesso = QLineEdit()
        layout_client.addWidget(lbl_chave_acesso)
        layout_client.addWidget(self.input_chave_acesso)

        layout_principal.addWidget(painel_client)

        painel_bottom = QWidget()
        layout_bottom = QHBoxLayout(painel_bottom)
        btn_localizar = QPushButton("Localizar")
        btn_cancelar = QPushButton("Cancelar")
        btn_localizar.clicked.connect(self.accept)
        btn_cancelar.clicked.connect(self.reject)
        layout_bottom.addStretch() 
        layout_bottom.addWidget(btn_localizar)
        layout_bottom.addWidget(btn_cancelar)
        layout_principal.addWidget(painel_bottom)

    def get_emitentes(self):
        SELECT_EMITENTES = """
            SELECT fantasia || ' - ' || endereco, cnpj
            FROM emitente 
            ORDER BY fantasia
        """
        self.cursor.execute(SELECT_EMITENTES)
        rows = self.cursor.fetchall()
        self.combo_emitente.clear()
        self.combo_emitente.addItem("Todos", "")
        for row in rows:
            self.combo_emitente.addItem(row[0], row[1])

    def get_produtos(self):
        SELECT_PRODUTOS = """
            SELECT descricao
            FROM cupom_item
            GROUP BY descricao
            ORDER BY descricao
        """
        self.cursor.execute(SELECT_PRODUTOS)
        rows = self.cursor.fetchall()
        produtos = [row[0] for row in rows]
        result = []
        for produto in produtos:
            palavras = produto.split()
            for palavra in palavras:
                if len(palavra) > 3:  
                    if palavra not in result:
                        result.append(palavra)
        result.sort()
        return result

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Dashboard()
    window.show()
    sys.exit(app.exec())
