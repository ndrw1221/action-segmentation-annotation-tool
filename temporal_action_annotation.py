import sys
import os
import typing
from PyQt5 import QtCore, QtGui
import cv2
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap, QFont
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QPushButton,
    QFileDialog,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QSlider,
    QLineEdit,
    QDialog,
    QListWidget,
    QGroupBox,
    QListWidgetItem,
    QAction,
)


class VideoPlayerApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.current_frame = 0
        self.is_playing = False
        self.frames = []
        self.fps = 30
        self.actions = {}
        self.video_name = ""

        self.keyPress()

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Temporal action annotatation tool")
        self.setGeometry(450, 200, 1200, 700)
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        font_14 = QFont()
        font_14.setPointSize(14)

        self.video = QLabel(self)
        self.action = QListWidget()
        self.action.itemSelectionChanged.connect(self.updateButtonState)

        self.delete_action_button = QPushButton("Delete", self)
        self.delete_action_button.setEnabled(False)
        self.delete_action_button.clicked.connect(self.delete_action)
        self.delete_action_button.setFocusPolicy(Qt.ClickFocus)

        self.frame_label = QLabel("Frame: 0", self)

        self.slider = QSlider(1, self)
        self.slider.setEnabled(False)
        self.slider.valueChanged.connect(self.onSliderChange)
        self.slider.setFocusPolicy(Qt.ClickFocus)

        self.load_button = QPushButton("Load Video (L)", self)
        self.load_button.clicked.connect(self.loadVideo)
        self.load_button.setFocusPolicy(Qt.ClickFocus)

        self.play_button = QPushButton("Play (Space)", self)
        self.play_button.setEnabled(False)
        self.play_button.clicked.connect(self.playVideo)
        self.play_button.setFocusPolicy(Qt.ClickFocus)

        self.forward_button = QPushButton("Forward (→)", self)
        self.forward_button.setEnabled(False)
        self.forward_button.clicked.connect(self.forwardFrame)
        self.forward_button.setFocusPolicy(Qt.ClickFocus)

        self.backward_button = QPushButton("Backward (←)", self)
        self.backward_button.setEnabled(False)
        self.backward_button.clicked.connect(self.backwardFrame)
        self.backward_button.setFocusPolicy(Qt.ClickFocus)

        self.add_action_button = QPushButton("Add Action (A)", self)
        self.add_action_button.setEnabled(False)
        self.add_action_button.clicked.connect(self.addTemporalAction)
        self.add_action_button.setFocusPolicy(Qt.ClickFocus)

        self.action_start_button = QPushButton("Action Start (F)", self)
        self.action_start_button.setEnabled(False)
        self.action_start_button.clicked.connect(self.temporalActionStart)
        self.action_start_button.setFocusPolicy(Qt.ClickFocus)

        self.action_end_button = QPushButton("Action End (D)", self)
        self.action_end_button.setEnabled(False)
        self.action_end_button.clicked.connect(self.temporalActionEnd)
        self.action_end_button.setFocusPolicy(Qt.ClickFocus)

        self.output_annotation_button = QPushButton("Output Annotation (O)", self)
        self.output_annotation_button.setEnabled(False)
        self.output_annotation_button.clicked.connect(self.outputAnnotation)
        self.output_annotation_button.setFocusPolicy(Qt.ClickFocus)

        group_box = QGroupBox("Actions")
        group_box.setFont(font_14)

        group_box_layout = QVBoxLayout()
        group_box_layout.addWidget(self.action)
        group_box_layout.addWidget(self.delete_action_button)
        group_box.setLayout(group_box_layout)

        self.hbox_vid = QHBoxLayout()
        self.hbox_vid.addStretch(1)
        self.hbox_vid.addWidget(self.video)
        self.hbox_vid.addStretch(1)
        self.hbox_vid.addWidget(group_box)
        self.hbox_vid.addStretch(1)

        self.hbox_1 = QHBoxLayout()
        self.hbox_1.addWidget(self.load_button)
        self.hbox_1.addWidget(self.play_button)
        self.hbox_1.addWidget(self.backward_button)
        self.hbox_1.addWidget(self.forward_button)

        self.hbox_2 = QHBoxLayout()
        self.hbox_2.addWidget(self.add_action_button)
        self.hbox_2.addWidget(self.action_start_button)
        self.hbox_2.addWidget(self.action_end_button)
        self.hbox_2.addWidget(self.output_annotation_button)

        self.vbox = QVBoxLayout()
        self.vbox.addStretch(1)
        self.vbox.addLayout(self.hbox_vid)
        self.vbox.addStretch(1)
        self.vbox.addWidget(self.frame_label)
        self.vbox.addWidget(self.slider)
        self.vbox.addLayout(self.hbox_1)
        self.vbox.addLayout(self.hbox_2)

        central_widget.setLayout(self.vbox)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateFrame)

    def updateButtonState(self, mode=None):
        if mode == "init":
            self.play_button.setEnabled(True)
            self.forward_button.setEnabled(True)
            self.backward_button.setEnabled(True)
            self.add_action_button.setEnabled(True)
            self.slider.setEnabled(True)
            self.slider.setRange(0, len(self.frames) - 1)
            self.slider.setValue(0)

        item_selected = self.action.selectedItems()
        if item_selected:
            self.action_start_button.setEnabled(True)
            self.action_end_button.setEnabled(True)
            self.delete_action_button.setEnabled(True)
        else:
            self.action_start_button.setEnabled(False)
            self.action_end_button.setEnabled(False)
            self.delete_action_button.setEnabled(False)

    def loadVideo(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Video File",
            "",
            "Video Files (*.mp4 *.avi *.mkv *.mov *.flv);;All Files (*)",
            options=options,
        )

        if file_path:
            video_capture = cv2.VideoCapture(file_path)
            self.frames = []
            self.video_name = os.path.basename(file_path)

            while True:
                ret, frame = video_capture.read()
                if not ret:
                    break
                self.frames.append(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

            frame = self.frames[0]
            height, width, channel = frame.shape
            bytes_per_line = 3 * width
            q_img = QImage(
                frame.data, width, height, bytes_per_line, QImage.Format_RGB888
            )
            pixmap = QPixmap.fromImage(q_img)
            self.video.setPixmap(pixmap)

            self.updateButtonState("init")

    def playVideo(self):
        if self.current_frame == len(self.frames) - 1:
            self.current_frame = 0

        if not self.is_playing:
            self.is_playing = True
            self.timer.start(round(1000 / self.fps))
            self.play_button.setText("Pause")

        else:
            self.stopVideo()

    def stopVideo(self):
        if self.is_playing:
            self.is_playing = False
            self.timer.stop()
            self.play_button.setText("Play")

    def forwardFrame(self):
        if not self.is_playing:
            self.current_frame += 1
            if self.current_frame > len(self.frames) - 1:
                self.current_frame = len(self.frames) - 1
            self.updateFrame()

    def backwardFrame(self):
        if not self.is_playing:
            self.current_frame -= 1
            if self.current_frame < 0:
                self.current_frame = 0
            self.updateFrame()

    def onSliderChange(self):
        if not self.is_playing:
            self.current_frame = self.slider.value()
            self.updateFrame()

            if self.slider.value() < len(self.frames) - 1:
                self.play_button.setText("Play")

    def updateFrame(self):
        if not self.current_frame < len(self.frames) - 1:
            self.stopVideo()
            self.play_button.setText("Restart")

        else:
            if self.is_playing:
                self.current_frame += 1

            frame = self.frames[self.current_frame]
            height, width, channel = frame.shape
            bytes_per_line = 3 * width
            q_img = QImage(
                frame.data, width, height, bytes_per_line, QImage.Format_RGB888
            )
            pixmap = QPixmap.fromImage(q_img)
            self.video.setPixmap(pixmap)
            self.frame_label.setText(f"Frame: {self.current_frame}")
            self.slider.setValue(self.current_frame)

    def addTemporalAction(self):
        dialog = ActionNameInputDialog()
        result = dialog.exec_()

        if result == QDialog.Accepted:
            action_name = dialog.action_input.text()
            if action_name:
                print(f"Added action {action_name}")
                self.actions[action_name] = [None, None]
                new_action = QListWidgetItem(action_name)
                self.action.addItem(new_action)
                self.action.setCurrentItem(new_action)
                self.output_annotation_button.setEnabled(True)

    def temporalActionStart(self):
        action = self.action.currentItem().text()
        if action:
            self.actions[action][0] = self.current_frame
            # self.updateItem()
            print(self.actions)

    def temporalActionEnd(self):
        action = self.action.currentItem().text()
        if action:
            self.actions[action][1] = self.current_frame
            # self.updateItem()
            print(self.actions)

    def outputAnnotation(self):
        file_name, file_extension = os.path.splitext(self.video_name)

        output_format = ["Null"] * len(self.frames)
        for action in self.actions:
            duration = self.actions[action]
            for i in range(duration[0], duration[1] + 1):
                output_format[i] = action

        with open(f"./output/{file_name}.txt", "w") as file:
            for line in output_format:
                file.write(line + "\n")

        dialog = OuputAnnotationDialog()
        dialog.exec_()
        print(f"{file_name}.txt created successfully.")

    def delete_action(self):
        selected_action = self.action.currentItem()
        if selected_action:
            row = self.action.row(selected_action)
            self.action.takeItem(row)
            del self.actions[selected_action.text()]
            self.updateButtonState()
            print(f"'{selected_action.text()}' is deleted.")

    def keyPress(self):
        # L or l for loading video
        self.loadVideoAction = QAction("Load video", self)
        self.loadVideoAction.setShortcut("L")
        self.loadVideoAction.triggered.connect(lambda: self.load_button.click())
        self.addAction(self.loadVideoAction)
        # Spacebar to play and pause video
        self.playVideoAction = QAction("Play video", self)
        self.playVideoAction.setShortcut("Space")
        self.playVideoAction.triggered.connect(lambda: self.play_button.click())
        self.addAction(self.playVideoAction)
        # Left arrow to backward one frame
        self.backwardAction = QAction("Previous frame", self)
        self.backwardAction.setShortcut("Left")
        self.backwardAction.triggered.connect(lambda: self.backward_button.click())
        self.addAction(self.backwardAction)
        # Rigth arrow to forward one frame
        self.forwardAction = QAction("Next frame", self)
        self.forwardAction.setShortcut("Right")
        self.forwardAction.triggered.connect(lambda: self.forward_button.click())
        self.addAction(self.forwardAction)
        # A or a to add temporal acion
        self.addActionAction = QAction("Add action", self)
        self.addActionAction.setShortcut("A")
        self.addActionAction.triggered.connect(lambda: self.add_action_button.click())
        self.addAction(self.addActionAction)
        # F or f to mark action start
        self.actionStartAction = QAction("Mark action start", self)
        self.actionStartAction.setShortcut("F")
        self.actionStartAction.triggered.connect(
            lambda: self.action_start_button.click()
        )
        self.addAction(self.actionStartAction)
        # D or d to make action end
        self.actionEndAction = QAction("Mark action end", self)
        self.actionEndAction.setShortcut("D")
        self.actionEndAction.triggered.connect(lambda: self.action_end_button.click())
        self.addAction(self.actionEndAction)
        # O or o to make action end
        self.outputAnnotationAction = QAction("Output annotation", self)
        self.outputAnnotationAction.setShortcut("O")
        self.outputAnnotationAction.triggered.connect(
            lambda: self.output_annotation_button.click()
        )
        self.addAction(self.outputAnnotationAction)


class ActionNameInputDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle(" ")

        font = QFont()
        font.setPointSize(16)

        self.action_input = QLineEdit()
        self.action_input.setPlaceholderText("Enter action name")
        self.action_input.setFont(font)

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)

        Vlayout = QVBoxLayout()
        Vlayout.addWidget(self.action_input)
        Vlayout.addWidget(ok_button)

        self.setLayout(Vlayout)


class OuputAnnotationDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle(" ")

        font = QFont()
        font.setPointSize(16)

        label = QLabel("Annotation output success.")
        label.setFont(font)

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)

        Vlayout = QVBoxLayout()
        Vlayout.addWidget(label)
        Vlayout.addWidget(ok_button)

        self.setLayout(Vlayout)


def main():
    app = QApplication(sys.argv)
    window = VideoPlayerApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
