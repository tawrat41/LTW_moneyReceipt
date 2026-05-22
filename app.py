import sys
import os
import tempfile
import re
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox,
    QGroupBox, QFormLayout, QSpinBox, QDateEdit
)
from PySide6.QtCore import Qt, QDate
from receipt_generator import generate_receipt_pdf
from utils import amount_to_words

COUNTER_FILE = os.path.join(os.path.dirname(__file__), "receipt_counter.txt")


class ReceiptApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lead The Way - Receipt Generator")
        self.setMinimumSize(900, 650)
        self.next_mr_no = self.load_next_mr_no()
        self.setup_ui()

    def load_next_mr_no(self):
        try:
            if os.path.exists(COUNTER_FILE):
                with open(COUNTER_FILE, "r", encoding="ascii") as file:
                    value = file.read().strip()
                    if value.isdigit():
                        return max(1, int(value))
        except OSError:
            pass
        return 101

    def save_next_mr_no(self):
        try:
            with open(COUNTER_FILE, "w", encoding="ascii") as file:
                file.write(str(self.next_mr_no))
        except OSError:
            QMessageBox.warning(self, "Warning", "Could not save the next MR number.")

    def increment_mr_no(self):
        current_value = self.mr_no.text().strip()
        if current_value.isdigit():
            self.next_mr_no = int(current_value) + 1
        else:
            self.next_mr_no += 1

        self.mr_no.setText(str(self.next_mr_no))
        self.save_next_mr_no()

    def setup_ui(self):
        main_layout = QHBoxLayout()

        # LEFT PANEL
        form_group = QGroupBox("Receipt Information")
        form_layout = QFormLayout()

        self.mr_no = QLineEdit(str(self.next_mr_no))
        self.student_name = QLineEdit()
        self.student_class = QLineEdit()
        self.month = QLineEdit()
        self.day = QLineEdit()
        self.time = QLineEdit()
        self.date = QDateEdit()
        self.date.setCalendarPopup(True)
        self.date.setDisplayFormat("dd MMM yyyy")
        self.date.setDate(QDate.currentDate())

        self.admission_fee = QSpinBox()
        self.admission_fee.setMaximum(1000000)

        self.monthly_fee = QSpinBox()
        self.monthly_fee.setMaximum(1000000)

        self.misc_fee = QSpinBox()
        self.misc_fee.setMaximum(1000000)

        self.total_label = QLabel("0")
        self.words_label = QLabel("Zero Taka Only")
        self.words_label.setWordWrap(True)

        self.admission_fee.valueChanged.connect(self.update_total)
        self.monthly_fee.valueChanged.connect(self.update_total)
        self.misc_fee.valueChanged.connect(self.update_total)

        form_layout.addRow("MR No:", self.mr_no)
        form_layout.addRow("Student Name:", self.student_name)
        form_layout.addRow("Class:", self.student_class)
        form_layout.addRow("Month:", self.month)
        form_layout.addRow("Day:", self.day)
        form_layout.addRow("Time:", self.time)
        form_layout.addRow("Date:", self.date)

        form_layout.addRow("Admission / Session Fee:", self.admission_fee)
        form_layout.addRow("Monthly Tuition Fee:", self.monthly_fee)
        form_layout.addRow("Miscellaneous:", self.misc_fee)

        form_layout.addRow("Total:", self.total_label)
        form_layout.addRow("In Words:", self.words_label)

        form_group.setLayout(form_layout)

        # BUTTONS
        button_layout = QHBoxLayout()

        self.save_btn = QPushButton("Save PDF")
        self.print_btn = QPushButton("Print")

        self.save_btn.clicked.connect(self.save_pdf)
        self.print_btn.clicked.connect(self.print_pdf)

        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.print_btn)

        left_layout = QVBoxLayout()
        left_layout.addWidget(form_group)
        left_layout.addLayout(button_layout)

        # RIGHT PREVIEW
        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout()

        self.preview_label = QLabel("Receipt Preview\n(Fill the form)")
        self.preview_label.setAlignment(Qt.AlignTop)
        self.preview_label.setStyleSheet("""
            QLabel {
                background: white;
                border: 1px solid #ccc;
                padding: 20px;
                font-size: 14px;
            }
        """)

        preview_layout.addWidget(self.preview_label)
        preview_group.setLayout(preview_layout)

        self.mr_no.textChanged.connect(self.update_preview)
        self.student_name.textChanged.connect(self.update_preview)
        self.student_class.textChanged.connect(self.update_preview)
        self.month.textChanged.connect(self.update_preview)
        self.day.textChanged.connect(self.update_preview)
        self.time.textChanged.connect(self.update_preview)
        self.date.dateChanged.connect(self.update_preview)

        main_layout.addLayout(left_layout, 1)
        main_layout.addWidget(preview_group, 1)

        self.setLayout(main_layout)

    def get_total(self):
        return (
            self.admission_fee.value() +
            self.monthly_fee.value() +
            self.misc_fee.value()
        )

    def update_total(self):
        total = self.get_total()
        self.total_label.setText(str(total))
        self.words_label.setText(amount_to_words(total))
        self.update_preview()

    def update_preview(self):
        preview = f"""
LEAD THE WAY

MR No: {self.mr_no.text()}
Student: {self.student_name.text()}
Class: {self.student_class.text()}
Month: {self.month.text()}
Day: {self.day.text()}
Time: {self.time.text()}
Date: {self.date.text()}

Admission Fee: {self.admission_fee.value()}
Monthly Fee: {self.monthly_fee.value()}
Miscellaneous: {self.misc_fee.value()}

TOTAL: {self.get_total()}

{amount_to_words(self.get_total())}
"""
        self.preview_label.setText(preview)

    def collect_data(self):
        return {
            "mr_no": self.mr_no.text().strip() or str(self.next_mr_no),
            "student_name": self.student_name.text(),
            "student_class": self.student_class.text(),
            "month": self.month.text(),
            "day": self.day.text(),
            "time": self.time.text(),
            "date": self.date.date().toString("dd MMM yyyy"),
            "admission_fee": self.admission_fee.value(),
            "monthly_fee": self.monthly_fee.value(),
            "misc_fee": self.misc_fee.value(),
            "total": self.get_total(),
            "words": amount_to_words(self.get_total())
        }

    def build_default_filename(self):
        student_name = self.student_name.text().strip() or "student"
        month = self.month.text().strip() or "month"
        base_name = f"{student_name}_{month}"
        safe_name = re.sub(r'[<>:"/\\\\|?*]+', "_", base_name)
        safe_name = re.sub(r"\s+", "_", safe_name).strip("._")
        return f"{safe_name or 'receipt'}.pdf"

    def save_pdf(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Receipt",
            self.build_default_filename(),
            "PDF Files (*.pdf)"
        )

        if file_path:
            generate_receipt_pdf(file_path, self.collect_data())
            self.increment_mr_no()
            QMessageBox.information(self, "Success", "Receipt saved successfully.")

    def print_pdf(self):
        temp_file = os.path.join(tempfile.gettempdir(), "receipt_temp.pdf")
        generate_receipt_pdf(temp_file, self.collect_data())
        self.increment_mr_no()

        os.startfile(temp_file, "print")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ReceiptApp()
    window.show()
    sys.exit(app.exec())
