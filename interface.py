import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                             QWidget, QTableWidget, QTableWidgetItem, QPushButton,
                             QHeaderView, QDialog, QLineEdit, QLabel, QDialogButtonBox, QMessageBox, QComboBox)
from PyQt5.QtCore import Qt

import sqlite3

# фрагмент исходного кода с созданием базы данных
conn = sqlite3.connect("services.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS services (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    labor REAL NOT NULL,
    materials REAL NOT NULL,
    overhead REAL NOT NULL,
    markup REAL NOT NULL
)
""")
conn.commit()


class CreateRecordWindow(QDialog): # 
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Создание записи')

        self.init_ui()
        self.load_services()

    def init_ui(self):
        """Создание пользовательского интерфейса"""
        self.setFixedSize(500, 400)
        create_record_layout = QVBoxLayout()

        # Поле выбора услуги
        service_layout = QHBoxLayout()
        service_label = QLabel('Услуга:')
        service_label.setFixedWidth(150)
        self.service_combo = QComboBox()
        self.service_combo.currentTextChanged.connect(self.update_price)
        service_layout.addWidget(service_label)
        service_layout.addWidget(self.service_combo)
        create_record_layout.addLayout(service_layout)

        # Поле выбора категории товаров
        category_layout = QHBoxLayout()
        category_label = QLabel('Категория товаров:')
        category_label.setFixedWidth(150)
        self.category_combo = QComboBox()
        self.category_combo.addItems([
            'Телевизоры',
            'Мониторы',
            'Холодильники',
            'Стиральные машины'
        ])
        category_layout.addWidget(category_label)
        category_layout.addWidget(self.category_combo)
        create_record_layout.addLayout(category_layout)

        # Поле отображения цены
        price_layout = QHBoxLayout()
        price_label = QLabel('Цена услуги:')
        price_label.setFixedWidth(150)
        self.price_display = QLineEdit()
        self.price_display.setReadOnly(True)
        price_layout.addWidget(price_label)
        price_layout.addWidget(self.price_display)
        create_record_layout.addLayout(price_layout)

        # Кнопки OK и Отмена
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        create_record_layout.addWidget(button_box)

        self.setLayout(create_record_layout)

    def load_services(self):
        """Загрузка списка услуг из базы данных"""
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT name FROM services ORDER BY name')
            services = cursor.fetchall()
            for service in services:
                self.service_combo.addItem(service[0])
            # Обновляем цену для первого элемента
            if self.service_combo.count() > 0:
                self.update_price(self.service_combo.currentText())
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка загрузки услуг: {str(e)}')

    def update_price(self, service_name):
        """Обновление цены в зависимости от выбранной услуги"""
        if not service_name:
            self.price_display.setText('')
            return

        try:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT materials, overhead, markup, labor
                FROM services
                WHERE name = ?
            ''', (service_name,))
            result = cursor.fetchone()

            if result:
                # Считаем сумму всех параметров (пропускаем None)
                total_price = sum(float(val) if val is not None else 0 for val in result)
                self.price_display.setText(f'{total_price:.2f}')
            else:
                self.price_display.setText('0.00')
        except Exception as e:
            QMessageBox.warning(self, 'Предупреждение', f'Не удалось рассчитать цену: {str(e)}')
            self.price_display.setText('Ошибка расчёта')

    def get_record_data(self):
        """Возвращает данные для новой записи"""
        service = self.service_combo.currentText()
        category = self.category_combo.currentText()
        price_text = self.price_display.text()

        try:
            price = float(price_text) if price_text else 0.0
        except ValueError:
            price = 0.0

        return {
            'service': service,
            'category': category,
            'price': price
        }


class AddServiceWindow(QDialog): # окно ввода параметров
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Добавление услуги')
        self.setFixedSize(500, 300)
        add_service_layout = QVBoxLayout()

        description_label = QLabel("Введите все необходимые данные:")
        description_label.setWordWrap(True)
        
        name_layout = QHBoxLayout()
        name_label = QLabel("Название услуги:")
        self.name = QLineEdit() # будет меняться
        self.name.setPlaceholderText("Введите название услуги")
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name)

        labor_layout = QHBoxLayout()
        labor_label = QLabel("Трудозатраты:")
        self.labor = QLineEdit()
        self.labor.setPlaceholderText("Трудозатраты")
        labor_layout.addWidget(labor_label)
        labor_layout.addWidget(self.labor)

        materials_layout = QHBoxLayout()
        materials_label = QLabel("Материалы:")
        self.materials = QLineEdit()
        self.materials.setPlaceholderText("Материалы")
        materials_layout.addWidget(materials_label)
        materials_layout.addWidget(self.materials)

        overhead_layout = QHBoxLayout()
        overhead_label = QLabel("Накладные расходы:")
        self.overhead = QLineEdit()
        self.overhead.setPlaceholderText("Накладные расходы")
        overhead_layout.addWidget(overhead_label)
        overhead_layout.addWidget(self.overhead)

        markup_layout = QHBoxLayout()
        markup_label = QLabel("Наценка (в процентах):")
        self.markup = QLineEdit()
        self.markup.setPlaceholderText("Наценка (%)")
        markup_layout.addWidget(markup_label)
        markup_layout.addWidget(self.markup)

        write_button = QPushButton("Записать в базу данных")
        write_button.clicked.connect(self.add_data)

        add_service_layout.addWidget(description_label)
        add_service_layout.addLayout(name_layout)
        add_service_layout.addLayout(labor_layout)
        add_service_layout.addLayout(materials_layout)
        add_service_layout.addLayout(overhead_layout)
        add_service_layout.addLayout(markup_layout)
        add_service_layout.addWidget(write_button)

        self.setLayout(add_service_layout)

    def add_data(self):
        cursor.execute("""INSERT INTO services (name, labor, materials, overhead, markup) VALUES (?, ?, ?, ?, ?)""",
        (self.name.text(), float(self.labor.text()), float(self.materials.text()), float(self.overhead.text()), float(self.markup.text())))
        conn.commit() # добавить какой-то сигнал о записи (???)
        QMessageBox.information(self, 'Успех', f'Услуга "{self.name.text()}" успешно добавлена!')


class EditServiceDialog(QDialog):
    def __init__(self, service_name, labor, materials, overhead, markup, parent=None):
        super().__init__(parent)
        self.service_name = service_name
        self.setWindowTitle("Изменение параметров услуги")
        self.setFixedSize(500, 400)
        self.setModal(True)
        self.setup_ui(labor, materials, overhead, markup)

    def setup_ui(self, labor, materials, overhead, markup):
        layout = QVBoxLayout()

        # Заголовок с названием услуги
        name_label = QLabel(f"Услуга: {self.service_name}")
        name_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(name_label)
        layout.addSpacing(15)

        # Поле для трудозатрат
        layout.addWidget(QLabel("Трудозатраты:"))
        self.labor_edit = QLineEdit()
        self.labor_edit.setPlaceholderText(str(labor))
        layout.addWidget(self.labor_edit)

        # Поле для материалов
        layout.addWidget(QLabel("Материалы:"))
        self.materials_edit = QLineEdit()
        self.materials_edit.setPlaceholderText(str(materials))
        layout.addWidget(self.materials_edit)

        # Поле для накладных расходов
        layout.addWidget(QLabel("Накладные расходы:"))
        self.overhead_edit = QLineEdit()
        self.overhead_edit.setPlaceholderText(str(overhead))
        layout.addWidget(self.overhead_edit)

        # Поле для наценки
        layout.addWidget(QLabel("Наценка (%):"))
        self.markup_edit = QLineEdit()
        self.markup_edit.setPlaceholderText(str(markup))
        layout.addWidget(self.markup_edit)

        # Кнопки
        button_layout = QHBoxLayout()
        ok_button = QPushButton("Ок")
        cancel_button = QPushButton("Отмена")

        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def get_values(self):
        """Возвращает введённые значения или None, если поля пустые"""
        labor = self.labor_edit.text().strip()
        materials = self.materials_edit.text().strip()
        overhead = self.overhead_edit.text().strip()
        markup = self.markup_edit.text().strip()

        return {
            'labor': labor if labor else None,
            'materials': materials if materials else None,
            'overhead': overhead if overhead else None,
            'markup': markup if markup else None
        }


class ListServiceWindow(QDialog): # окно просмотра списка услуг
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Список услуг')
        self.setFixedSize(700, 500)
        list_service_layout = QVBoxLayout()

        cursor.execute("SELECT id, name FROM services")
        rows = cursor.fetchall()

        self.service_table = QTableWidget()
        self.service_table.setColumnCount(1)
        self.service_table.setHorizontalHeaderLabels(['Наименование услуги'])
        self.service_table.setRowCount(len(rows))

        for row, name in enumerate(rows):
            self.service_table.setItem(row, 0, QTableWidgetItem(name[1]))

        self.service_table.resizeColumnsToContents()

        show_btn = QPushButton('Подробнее...')
        show_btn.clicked.connect(self.show_selected_service)

        delete_button = QPushButton('Удалить')
        delete_button.clicked.connect(self.delete_selected_service)

        change_btn = QPushButton('Изменить параметры услуги')
        change_btn.clicked.connect(self.change_selected_service)

        calculate_btn = QPushButton('Подсчитать стоимость услуги')
        calculate_btn.clicked.connect(self.calculate_selected_service)

        list_service_layout.addWidget(self.service_table)
        list_service_layout.addWidget(show_btn)
        list_service_layout.addWidget(delete_button)
        list_service_layout.addWidget(change_btn)
        list_service_layout.addWidget(calculate_btn)

        self.setLayout(list_service_layout)

    def show_selected_service(self):
        current_item = self.service_table.currentItem()
        if not current_item:
            QMessageBox.warning(self, 'Ошибка', 'Сначала выберите услугу в таблице!')
            return
        
        service_name = current_item.text()

        info_table = QTableWidget()

        info_table.setColumnCount(4)
        info_table.setRowCount(1)
        info_table.setHorizontalHeaderLabels(['Трудозатраты', 'Материалы', 'Накладные расходы', 'Наценка (в процентах)'])

        cursor.execute('''
            SELECT labor, materials, overhead, markup
            FROM services
            WHERE name = ?
        ''', (service_name,))
        result = cursor.fetchone()

        info_table.setItem(0, 0, QTableWidgetItem(str(result[0])))
        info_table.setItem(0, 1, QTableWidgetItem(str(result[1])))
        info_table.setItem(0, 2, QTableWidgetItem(str(result[2])))
        info_table.setItem(0, 3, QTableWidgetItem(str(result[3])))

        info_table.resizeColumnsToContents()

        dlg = QDialog()
        dlg.setFixedSize(1000, 300)
        dlg.setWindowTitle('Параметры услуги')
        info_layout = QVBoxLayout()
        info_layout.addWidget(info_table)
        dlg.setLayout(info_layout)
        dlg.exec_()
        
    
    def delete_selected_service(self):
        """Удаление выбранной услуги из базы данных"""
        # Получаем текущую выбранную ячейку
        current_item = self.service_table.currentItem()
        if not current_item:
            QMessageBox.warning(self, 'Ошибка', 'Сначала выберите услугу в таблице!')
            return
        
        service_name = current_item.text()
        
        # Подтверждение удаления
        reply = QMessageBox.question(
            self,
            'Подтверждение удаления',
            f'Вы уверены, что хотите удалить услугу "{service_name}"?\n'
            f'Будут удалены ВСЕ данные, связанные с этой услугой!',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # Удаляем запись из базы данных
                cursor.execute('DELETE FROM services WHERE name = ?', (service_name,))
                conn.commit()
                
                # Обновляем таблицу
                QMessageBox.information(self, 'Успех', f'Услуга "{service_name}" успешно удалена!')
            except Exception as e:
                QMessageBox.critical(self, 'Ошибка', f'Ошибка при удалении: {str(e)}')

    def change_selected_service(self):
        """Изменение выбранной услуги из базы данных"""
        # Получаем текущую выбранную ячейку
        current_item = self.service_table.currentItem()
        if not current_item:
            QMessageBox.warning(self, 'Ошибка', 'Сначала выберите услугу в таблице!')
            return
        
        service_name = current_item.text()

        cursor.execute('''SELECT labor, materials, overhead, markup FROM services WHERE name = ?''', (service_name,))

        result = cursor.fetchone()

        labor, materials, overhead, markup = result

        edit_dialog = EditServiceDialog(
                service_name, labor, materials, overhead, markup, self
            )

        if edit_dialog.exec_() == QDialog.Accepted:
            # Получаем новые значения от пользователя
            new_values = edit_dialog.get_values()

            # Обновляем запись в базе данных
            update_query = """
                    UPDATE services
                    SET labor = COALESCE(?, labor),
                        materials = COALESCE(?, materials),
                        overhead = COALESCE(?, overhead),
                        markup = COALESCE(?, markup)
                    WHERE name = ?
                """
            cursor.execute(update_query, (
                    new_values['labor'],
                    new_values['materials'],
                    new_values['overhead'],
                    new_values['markup'],
                    service_name)
                )
            conn.commit()

            QMessageBox.information(self, "Успех", "Параметры услуги успешно обновлены!")

    def calculate_selected_service(self):
        current_item = self.service_table.currentItem()
        if not current_item:
            QMessageBox.warning(self, 'Ошибка', 'Сначала выберите услугу в таблице!')
            return
        
        service_name = current_item.text()

        info_table = QTableWidget()

        info_table.setColumnCount(2)
        info_table.setRowCount(1)
        info_table.setHorizontalHeaderLabels(['Себестоимость', 'Цена'])

        cursor.execute('''
            SELECT labor, materials, overhead, markup
            FROM services
            WHERE name = ?
        ''', (service_name,))
        result = cursor.fetchone()

        cost = result[0] + result[1] + result[2]
        price = cost + cost * result[3] / 100

        info_table.setItem(0, 0, QTableWidgetItem(str(cost)))
        info_table.setItem(0, 1, QTableWidgetItem(str(price)))

        info_table.resizeColumnsToContents()

        dlg = QDialog()
        dlg.setWindowTitle('Себестоимость и цена услуги')
        dlg.setFixedSize(500, 300)
        info_layout = QVBoxLayout()
        info_layout.addWidget(info_table)
        dlg.setLayout(info_layout)
        dlg.exec_()


class ServiceApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Инициализация базы данных
        self.init_database()

        # Создание интерфейса
        self.init_ui()

        # Загрузка данных в таблицу
        self.load_records()

    def init_database(self):
        """Инициализация базы данных"""
        # Таблица записей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service TEXT NOT NULL,
                category TEXT NOT NULL,
                price REAL NOT NULL
            )
        ''')

        # Добавляем тестовые данные, если таблица пуста
        cursor.execute('SELECT COUNT(*) FROM services')
        if cursor.fetchone()[0] == 0:
            test_services = [
                ('Консультация', 2.5, 0, 50.0, 0.2),
                ('Диагностика', 1.0, 10.0, 30.0, 0.15),
                ('Ремонт', 5.0, 200.0, 100.0, 0.3),
                ('Обслуживание', 3.0, 50.0, 70.0, 0.25)
            ]
            cursor.executemany(
                'INSERT INTO services (name, labor, materials, overhead, markup) VALUES (?, ?, ?, ?, ?)',
                test_services
            )
            conn.commit()

    def init_ui(self):
        # настройка главного окна
        self.setWindowTitle('Управление услугами')
        self.setGeometry(100, 100, 800, 600)

        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Основной layout
        main_layout = QVBoxLayout()

        # панель кнопок сверху, кнопки соответствуют исходному меню
        button_panel = self.create_button_panel()
        main_layout.addLayout(button_panel)

        # таблица услуг
        self.table = self.create_service_table()
        main_layout.addWidget(self.table)

        central_widget.setLayout(main_layout)

    def create_button_panel(self):
        """Создаёт панель кнопок сверху"""
        layout = QHBoxLayout()

        # Кнопка «Создать запись»
        create_btn = QPushButton('Создать запись')
        create_btn.clicked.connect(self.on_create_clicked)
        layout.addWidget(create_btn)

        # Кнопка "Добавить услугу"
        add_btn = QPushButton('Добавить услугу')
        add_btn.clicked.connect(self.on_add_clicked)
        layout.addWidget(add_btn)

        # Кнопка "Список услуг"
        list_btn = QPushButton('Список услуг')
        list_btn.clicked.connect(self.on_list_clicked)
        layout.addWidget(list_btn)

        # растягиваемый пробел для выравнивания кнопок влево
        layout.addStretch()

        return layout

    def create_service_table(self):
        """Создаёт таблицу услуг"""
        self.table = QTableWidget()

        # Устанавливаем 4 столбца
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['Наименование услуги', 'Категория', 'Код услуги', 'Цена'])

        # Настраиваем растяжение столбцов
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Наименование — растягивается
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Категория — по содержимому
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Код — по содержимому
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Цена — по содержимому

        return self.table
    
    def on_create_clicked(self):
        """Открывает окно создания новой записи и добавляет данные в таблицу"""
        # Создаём окно создания записи
        create_dialog = CreateRecordWindow(parent=self)

        if create_dialog.exec_() == QDialog.Accepted:
            # Получаем данные из диалогового окна
            record_data = create_dialog.get_record_data()

            try:
                # Вставляем новую запись в базу данных (ID генерируется автоматически)
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO records (service, category, price)
                    VALUES (?, ?, ?)
                ''', (record_data['service'], record_data['category'], record_data['price']))
                conn.commit()

                # Получаем ID последней вставленной записи
                record_id = cursor.lastrowid

                # Добавляем запись в таблицу основного окна
                row_position = self.table.rowCount()
                self.table.insertRow(row_position)

                # Заполняем ячейки таблицы
                self.table.setItem(row_position, 0, QTableWidgetItem(str(record_id)))
                self.table.setItem(row_position, 1, QTableWidgetItem(record_data['service']))
                self.table.setItem(row_position, 2, QTableWidgetItem(record_data['category']))
                self.table.setItem(row_position, 3, QTableWidgetItem(f'{record_data["price"]:.2f}'))

                self.table.resizeColumnsToContents()

                QMessageBox.information(
                    self,
                    'Успех',
                    f'Запись успешно создана!\n'
                    f'ID: {record_id}\n'
                    f'Услуга: {record_data["service"]}\n'
                    f'Категория: {record_data["category"]}\n'
                    f'Цена: {record_data["price"]:.2f}'
                )

            except Exception as e:
                QMessageBox.critical(
                    self,
                    'Ошибка',
                    f'Ошибка при создании записи: {str(e)}'
                )

    def load_records(self):
        """Загрузка записей из базы данных в таблицу"""
        # Очищаем таблицу
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT id, service, category, price FROM records ORDER BY id')
            records = cursor.fetchall()

            # Заполняем таблицу
            for record in records:
                row_position = self.table.rowCount()
                self.table.insertRow(row_position)
                for column, value in enumerate(record):
                    item = QTableWidgetItem(str(value))
                    self.table.setItem(row_position, column, item)
            self.table.resizeColumnsToContents()
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка загрузки записей: {str(e)}')

    def on_add_clicked(self):
        """Обработчик кнопки «Добавить услугу»"""
        dlg = AddServiceWindow()
        dlg.exec_()

    def on_list_clicked(self):
        """Обработчик кнопки «Список услуг»"""
        dlg = ListServiceWindow()
        dlg.exec_()


def main():
    app = QApplication(sys.argv)
    window = ServiceApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()