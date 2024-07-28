import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, QPushButton


class ChatWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('本地聊天')
        self.setGeometry(100, 100, 1200, 400)

        # 创建对话框部件
        self.dialog_frame = QWidget(self)
        self.dialog_frame.setFixedSize(1200, 360)
        self.dialog_frame.setStyleSheet('QWidget { border: 2px solid gray; }')

        # 创建对话框布局
        dialog_layout = QVBoxLayout()

        # 聊天记录展示
        self.chat_area = QTextEdit(self)
        self.chat_area.setReadOnly(True)
        dialog_layout.addWidget(self.chat_area)

        # 信息输入布局
        message_layout = QHBoxLayout()
        self.talker_input = QLineEdit(self)
        self.talker_input.setPlaceholderText('请输入...')
        self.talker_input_button = QPushButton('发送', self)
        self.talker_input_button.clicked.connect(self.send_message)
        message_layout.addWidget(self.talker_input)
        message_layout.addWidget(self.talker_input_button)

        # 将信息输入布局添加到对话框布局中
        dialog_layout.addLayout(message_layout)

        # 将对话框布局设置为对话框部件的布局
        self.dialog_frame.setLayout(dialog_layout)

        # 将对话框部件添加到主布局中
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.dialog_frame)
        self.setLayout(main_layout)

    def send_message(self):
        message = self.talker_input.text()
        if message:
            self.chat_area.append(f"User: {message}")
            self.talker_input.clear()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    chat = ChatWidget()
    chat.show()
    sys.exit(app.exec_())
