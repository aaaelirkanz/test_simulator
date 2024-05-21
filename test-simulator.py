import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QFileDialog, QLabel, QTextEdit, QToolBar, QFontComboBox, QComboBox, QCheckBox
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt

class TestSimulationApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.database_path = None  # Track the current database path
        self.initUI()
        self.initDatabase()
        self.current_test_id = None  # Initialize current_test_id
        self.review_mode = False
        self.answer_visible = False

    def initUI(self):
        self.setWindowTitle('Test Simulation App')

        # Apply stylesheet
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QTextEdit {
                background-color: #ffffff;
                border: 1px solid #c0c0c0;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton {
                background-color: #0078d7;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #005fa1;
            }
            QToolBar {
                background-color: #e0e0e0;
                border: none;
            }
            QCheckBox {
                margin: 5px;
            }
            QLabel {
                font-size: 14px;
                color: #333333;
            }
        """)

        # Menu bar
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('File')

        newDBAction = QAction('New Database', self)
        newDBAction.triggered.connect(self.createNewDatabase)
        fileMenu.addAction(newDBAction)

        loadDBAction = QAction('Load Database', self)
        loadDBAction.triggered.connect(self.loadDatabase)
        fileMenu.addAction(loadDBAction)

        openDBAction = QAction('Open Database', self)
        openDBAction.triggered.connect(self.openDatabase)
        fileMenu.addAction(openDBAction)

        # Main widget
        self.mainWidget = QWidget()
        self.setCentralWidget(self.mainWidget)

        # Layout
        self.layout = QVBoxLayout(self.mainWidget)

        # QTextEdit editors
        self.editor1 = CustomQTextEdit()
        self.editor2 = CustomQTextEdit()
        self.layout.addWidget(self.editor1)
        self.layout.addWidget(self.editor2)

        # Feedback label
        self.feedbackLabel = QLabel('')
        self.layout.addWidget(self.feedbackLabel)

        # Buttons layout
        buttonLayout = QHBoxLayout()
        
        self.saveButton = QPushButton('Save Test')
        self.saveButton.clicked.connect(self.saveTest)
        buttonLayout.addWidget(self.saveButton)

        self.newQuestionButton = QPushButton('New Question')
        self.newQuestionButton.clicked.connect(self.newQuestion)
        buttonLayout.addWidget(self.newQuestionButton)

        self.toggleAnswerButton = QPushButton('Show Answer')
        self.toggleAnswerButton.clicked.connect(self.toggleAnswer)
        buttonLayout.addWidget(self.toggleAnswerButton)

        self.layout.addLayout(buttonLayout)

        # Review mode checkbox
        self.reviewModeCheckbox = QCheckBox('Review Mode')
        self.reviewModeCheckbox.stateChanged.connect(self.toggleReviewMode)
        self.layout.addWidget(self.reviewModeCheckbox)

        # Navigation buttons layout
        navButtonLayout = QHBoxLayout()
        
        self.navButtonFirst = QPushButton('<<')
        self.navButtonFirst.clicked.connect(self.navigateFirst)
        navButtonLayout.addWidget(self.navButtonFirst)

        self.navButtonPrev = QPushButton('<')
        self.navButtonPrev.clicked.connect(self.navigatePrev)
        navButtonLayout.addWidget(self.navButtonPrev)

        self.navButtonNext = QPushButton('>')
        self.navButtonNext.clicked.connect(self.navigateNext)
        navButtonLayout.addWidget(self.navButtonNext)

        self.navButtonLast = QPushButton('>>')
        self.navButtonLast.clicked.connect(self.navigateLast)
        navButtonLayout.addWidget(self.navButtonLast)

        self.layout.addLayout(navButtonLayout)

        self.createToolBar()

        self.show()

    def createToolBar(self):
        toolbar = QToolBar()

        fontBox = QFontComboBox()
        fontBox.currentFontChanged.connect(self.setFont)
        toolbar.addWidget(fontBox)

        fontSize = QComboBox()
        fontSize.setEditable(True)
        fontSize.addItems([str(i) for i in range(8, 30, 2)])
        fontSize.currentIndexChanged[str].connect(self.setFontSize)
        toolbar.addWidget(fontSize)

        boldAction = QAction(QIcon.fromTheme('format-text-bold'), 'Bold', self)
        boldAction.triggered.connect(self.setBold)
        toolbar.addAction(boldAction)

        italicAction = QAction(QIcon.fromTheme('format-text-italic'), 'Italic', self)
        italicAction.triggered.connect(self.setItalic)
        toolbar.addAction(italicAction)

        underlineAction = QAction(QIcon.fromTheme('format-text-underline'), 'Underline', self)
        underlineAction.triggered.connect(self.setUnderline)
        toolbar.addAction(underlineAction)

        self.addToolBar(toolbar)

    def setFont(self, font):
        self.editor1.setCurrentFont(font)
        self.editor2.setCurrentFont(font)

    def setFontSize(self, fontSize):
        self.editor1.setFontPointSize(float(fontSize))
        self.editor2.setFontPointSize(float(fontSize))

    def setBold(self):
        fmt = self.editor1.currentCharFormat()
        fmt.setFontWeight(QFont.Bold if not fmt.fontWeight() == QFont.Bold else QFont.Normal)
        self.editor1.setCurrentCharFormat(fmt)
        self.editor2.setCurrentCharFormat(fmt)

    def setItalic(self):
        fmt = self.editor1.currentCharFormat()
        fmt.setFontItalic(not fmt.fontItalic())
        self.editor1.setCurrentCharFormat(fmt)
        self.editor2.setCurrentCharFormat(fmt)

    def setUnderline(self):
        fmt = self.editor1.currentCharFormat()
        fmt.setFontUnderline(not fmt.fontUnderline())
        self.editor1.setCurrentCharFormat(fmt)
        self.editor2.setCurrentCharFormat(fmt)

    def initDatabase(self):
        self.conn = sqlite3.connect('test_simulation.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS tests
                               (id INTEGER PRIMARY KEY, question TEXT, answer TEXT)''')
        self.conn.commit()
        self.feedbackLabel.setText('Database initialized.')

    def createNewDatabase(self):
        db_path, _ = QFileDialog.getSaveFileName(self, "Create New Database", "", "Database Files (*.db)")
        if db_path:
            self.database_path = db_path
            self.conn = sqlite3.connect(db_path)
            self.cursor = self.conn.cursor()
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS tests
                                   (id INTEGER PRIMARY KEY, question TEXT, answer TEXT)''')
            self.conn.commit()
            self.setWindowTitle(f'Test Simulation App - {db_path}')
            self.feedbackLabel.setText('New database created.')

    def loadDatabase(self):
        db_path, _ = QFileDialog.getOpenFileName(self, "Load Database", "", "Database Files (*.db)")
        if db_path:
            self.database_path = db_path
            self.conn = sqlite3.connect(db_path)
            self.cursor = self.conn.cursor()
            self.setWindowTitle(f'Test Simulation App - {db_path}')
            self.feedbackLabel.setText('Database loaded.')

    def openDatabase(self):
        db_path, _ = QFileDialog.getOpenFileName(self, "Open Database", "", "Database Files (*.db)")
        if db_path:
            self.database_path = db_path
            self.conn = sqlite3.connect(db_path)
            self.cursor = self.conn.cursor()
            self.showDatabaseContent()
            self.setWindowTitle(f'Test Simulation App - {db_path}')
            self.feedbackLabel.setText('Database opened.')

    def showDatabaseContent(self):
        self.cursor.execute("SELECT * FROM tests")
        rows = self.cursor.fetchall()
        self.feedbackLabel.setText(f'Database contains {len(rows)} records.')

    def saveTest(self):
        self.feedbackLabel.setText('Saving test...')
        question_content = self.editor1.toHtml()
        answer_content = self.editor2.toHtml()
        self.checkAndSave(question_content, answer_content)

    def checkAndSave(self, question_content, answer_content):
        self.cursor.execute("INSERT INTO tests (question, answer) VALUES (?, ?)", (question_content, answer_content))
        self.conn.commit()
        self.feedbackLabel.setText('Test saved successfully.')

    def newQuestion(self):
        self.editor1.clear()
        self.editor2.clear()
        self.feedbackLabel.setText('Ready for new question.')

    def toggleAnswer(self):
        if self.answer_visible:
            self.editor2.clear()
            self.toggleAnswerButton.setText('Show Answer')
            self.feedbackLabel.setText('Answer hidden.')
        else:
            if self.current_test_id is not None:
                self.cursor.execute("SELECT answer FROM tests WHERE id=?", (self.current_test_id,))
                answer = self.cursor.fetchone()[0]
                self.editor2.setHtml(answer)
                self.toggleAnswerButton.setText('Hide Answer')
                self.feedbackLabel.setText('Answer displayed.')
        self.answer_visible = not self.answer_visible

    def toggleReviewMode(self, state):
        self.review_mode = state == Qt.Checked

    def navigateFirst(self):
        self.cursor.execute("SELECT MIN(id) FROM tests")
        result = self.cursor.fetchone()
        if result:
            self.current_test_id = result[0]
            self.loadTest()

    def navigatePrev(self):
        if self.current_test_id is not None:
            self.cursor.execute("SELECT id FROM tests WHERE id < ? ORDER BY id DESC LIMIT 1", (self.current_test_id,))
            result = self.cursor.fetchone()
            if result:
                self.current_test_id = result[0]
                self.loadTest()

    def navigateNext(self):
        if self.current_test_id is not None:
            self.cursor.execute("SELECT id FROM tests WHERE id > ? ORDER BY id ASC LIMIT 1", (self.current_test_id,))
            result = self.cursor.fetchone()
            if result:
                self.current_test_id = result[0]
                self.loadTest()

    def navigateLast(self):
        self.cursor.execute("SELECT MAX(id) FROM tests")
        result = self.cursor.fetchone()
        if result:
            self.current_test_id = result[0]
            self.loadTest()

    def loadTest(self):
        self.cursor.execute("SELECT question, answer FROM tests WHERE id=?", (self.current_test_id,))
        question, answer = self.cursor.fetchone()
        self.editor1.setHtml(question)
        if self.review_mode:
            self.editor2.clear()
            self.answer_visible = False
            self.toggleAnswerButton.setText('Show Answer')
        else:
            self.editor2.setHtml(answer)
            self.answer_visible = True
            self.toggleAnswerButton.setText('Hide Answer')
        self.feedbackLabel.setText(f'Loaded question {self.current_test_id}.')

class CustomQTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

    def canInsertFromMimeData(self, source):
        if source.hasImage():
            return True
        else:
            return super().canInsertFromMimeData(source)

    def insertFromMimeData(self, source):
        if source.hasImage():
            image = source.imageData()
            image_name = "pasted_image.png"
            image.save(image_name)
            self.insertHtml(f'<img src="{image_name}" />')
        else:
            super().insertFromMimeData(source)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = TestSimulationApp()
    
    sys.exit(app.exec_())
