import sys
import os
import tempfile
import re
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox,
    QGroupBox, QFormLayout, QSpinBox, QDateEdit, QFrame
)
from PySide6.QtCore import QDate
from receipt_generator import generate_receipt_pdf
from utils import amount_to_words

COUNTER_FILE = os.path.join(os.path.dirname(__file__), "receipt_counter.txt")


class ReceiptApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lead The Way - Receipt Generator")
        self.setMinimumSize(760, 620)
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
        self.setStyleSheet("""
            QWidget {
                background: #f4f7fb;
                color: #132238;
                font-size: 13px;
            }
            QGroupBox {
                background: #ffffff;
                border: 1px solid #d7dfeb;
                border-radius: 12px;
                font-weight: 600;
                margin-top: 14px;
                padding: 18px 16px 14px 16px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 14px;
                padding: 0 6px;
                color: #1f4aa8;
            }
            QLabel[role="title"] {
                color: #16315f;
                font-size: 26px;
                font-weight: 700;
            }
            QLabel[role="subtitle"] {
                color: #5a6b86;
                font-size: 12px;
            }
            QLabel[role="summaryValue"] {
                color: #0f2b57;
                font-size: 18px;
                font-weight: 700;
            }
            QLineEdit, QDateEdit, QSpinBox {
                background: #fbfcfe;
                border: 1px solid #c8d3e1;
                border-radius: 8px;
                padding: 8px 10px;
                min-height: 20px;
            }
            QLineEdit:focus, QDateEdit:focus, QSpinBox:focus {
                border: 1px solid #1f4aa8;
                background: #ffffff;
            }
            QPushButton {
                min-height: 38px;
                border-radius: 10px;
                font-weight: 600;
                padding: 0 18px;
            }
            QPushButton#saveButton {
                background: #1f4aa8;
                color: white;
                border: none;
            }
            QPushButton#saveButton:hover {
                background: #163b88;
            }
            QPushButton#printButton {
                background: #e9eef8;
                color: #16315f;
                border: 1px solid #c8d3e1;
            }
            QPushButton#printButton:hover {
                background: #dde7f6;
            }
            QFrame#summaryCard {
                background: #eef4ff;
                border: 1px solid #d4e1f7;
                border-radius: 12px;
            }
        """)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(28, 24, 28, 24)
        main_layout.setSpacing(18)

        title_label = QLabel("Receipt Generator")
        title_label.setProperty("role", "title")
        subtitle_label = QLabel("Create and save Lead The Way money receipts.")
        subtitle_label.setProperty("role", "subtitle")

        header_layout = QVBoxLayout()
        header_layout.setSpacing(2)
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        main_layout.addLayout(header_layout)

        form_group = QGroupBox("Receipt Information")
        form_layout = QVBoxLayout()
        form_layout.setSpacing(14)

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
        self.total_label.setProperty("role", "summaryValue")
        self.words_label = QLabel("Zero Taka Only")
        self.words_label.setWordWrap(True)

        self.mr_no.setPlaceholderText("Enter receipt number")
        self.student_name.setPlaceholderText("Student full name")
        self.student_class.setPlaceholderText("Class or batch")
        self.month.setPlaceholderText("Month")
        self.day.setPlaceholderText("Day")
        self.time.setPlaceholderText("Time")

        self.admission_fee.valueChanged.connect(self.update_total)
        self.monthly_fee.valueChanged.connect(self.update_total)
        self.misc_fee.valueChanged.connect(self.update_total)

        details_group = QGroupBox("Student Details")
        details_form = QFormLayout()
        details_form.setContentsMargins(0, 4, 0, 0)
        details_form.setHorizontalSpacing(18)
        details_form.setVerticalSpacing(12)
        details_form.addRow("MR No:", self.mr_no)
        details_form.addRow("Student Name:", self.student_name)
        details_form.addRow("Class:", self.student_class)
        details_form.addRow("Month:", self.month)
        details_form.addRow("Day:", self.day)
        details_form.addRow("Time:", self.time)
        details_form.addRow("Date:", self.date)
        details_group.setLayout(details_form)

        fees_group = QGroupBox("Fee Breakdown")
        fees_form = QFormLayout()
        fees_form.setContentsMargins(0, 4, 0, 0)
        fees_form.setHorizontalSpacing(18)
        fees_form.setVerticalSpacing(12)
        fees_form.addRow("Admission / Session Fee:", self.admission_fee)
        fees_form.addRow("Monthly Tuition Fee:", self.monthly_fee)
        fees_form.addRow("Miscellaneous:", self.misc_fee)
        fees_group.setLayout(fees_form)

        summary_group = QGroupBox("Receipt Summary")
        summary_layout = QVBoxLayout()
        summary_layout.setContentsMargins(0, 4, 0, 0)
        summary_layout.setSpacing(10)

        summary_card = QFrame()
        summary_card.setObjectName("summaryCard")
        summary_card_layout = QFormLayout()
        summary_card_layout.setContentsMargins(16, 14, 16, 14)
        summary_card_layout.setHorizontalSpacing(18)
        summary_card_layout.setVerticalSpacing(10)
        summary_card_layout.addRow("Total:", self.total_label)
        summary_card_layout.addRow("In Words:", self.words_label)
        summary_card.setLayout(summary_card_layout)

        summary_layout.addWidget(summary_card)
        summary_group.setLayout(summary_layout)

        form_layout.addWidget(details_group)
        form_layout.addWidget(fees_group)
        form_layout.addWidget(summary_group)

        form_group.setLayout(form_layout)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)

        self.save_btn = QPushButton("Save PDF")
        self.save_btn.setObjectName("saveButton")
        self.print_btn = QPushButton("Print")
        self.print_btn.setObjectName("printButton")

        self.save_btn.clicked.connect(self.save_pdf)
        self.print_btn.clicked.connect(self.print_pdf)

        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.print_btn)
        main_layout.addWidget(form_group)
        main_layout.addLayout(button_layout)

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
