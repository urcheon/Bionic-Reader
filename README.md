# Bionic Reading App

A **desktop application** built with **PySide6** and **PyMuPDF**, providing a **Bionic Reading** experience for PDF and text files. This app allows you to **adjust bold ratio**, **letter spacing**, **line spacing**, **font family**, and **theme** to enhance reading speed and reduce visual strain.  

It also **persists user settings in a JSON** file, so each time you start the application, your last used preferences—like font size, theme (dark/light mode), and spacing—are all loaded automatically.

---

## Features

- **Load PDF or TXT**:
  - Automatically converts PDF text (via PyMuPDF) or reads `.txt` files and displays them in the editor.

- **Bionic Reading**:
  - Uses regex to split words from punctuation and bolds the first part of each word, allowing faster word recognition.

- **Adjustable Reading Settings**:
  - **Bold ratio**: How much of each word is bolded (e.g., 40%).
  - **Font size**: Ranging from 8 to 48pt.
  - **Letter spacing & line spacing**: Increase or decrease spacing for better readability.
  - **Font family**: Choose any system font or load your own.

- **Dark/Light Themes**:
  - Toggle theme with a checkbox, instantly switching between a dark mode and a light mode.

- **Refresh Button**:
  - Refresh the current text with the latest Bionic Reading settings.

- **Export**:
  - Export the processed text to **HTML** or **PDF**.

- **JSON-based Configuration**:
  - Automatically **loads** your last used settings from `config.json` on startup.
  - **Saves** updated settings whenever you change them.

---

## Prerequisites

- **Python 3.7+** (recommended)
- Installed via `pip`:
  - `PySide6` for the GUI
  - `PyMuPDF` for PDF extraction
  - `weasyprint` for exporting to PDF
- (Optional) A local copy of `MiSans-Regular.otf` to load as the default UI font. 
  - You can use any other font if not available.

Example:
```bash
pip install PySide6 PyMuPDF weasyprint fitz 
```

---

## How to Run

1. **Clone** or **download** this repository.
2. Place your custom font (optional) like `MiSans-Regular.otf` in the same directory if needed.
3. **Install** dependencies (PySide6, PyMuPDF, weasyprint).
4. **Run** the Python script:
   ```bash
   python bionic_reading_app.py
   ```
5. On first run, the app creates (or reads) a `config.json` file in the same directory, storing your preferences.

---

## Usage

1. **Load a File**  
   - Click **“加载 PDF / TXT”** to open a `.pdf` or `.txt` file.
   - The text will appear in the main editor area.

2. **Adjust Bionic Reading Parameters**  
   - **加粗比例 (Bold Ratio)**: Move the slider to decide how much of each word is bolded (10–90%).  
   - **字体大小 (Font Size)**: Adjust the spin box to choose a point size.  
   - **字距 (Letter Spacing)** & **行距 (Line Spacing)**: Tweak spacing for better legibility.  
   - **选择字体 (Font Selector)**: Pick a system font from the dropdown.

3. **Toggle Dark Mode**  
   - Check **“深色模式”** to switch to dark theme, or uncheck for light theme.

4. **Refresh Text**  
   - Click **“刷新”** to re-apply Bionic Reading to the **current** editor text with the updated settings.

5. **Export**  
   - Click **“导出为 HTML 或 PDF”** to save the processed text.  
   - Choose a `.html` or `.pdf` file extension in the file dialog.

6. **Automatic Configuration**  
   - Any time you adjust a setting (e.g., bold ratio, font size, or theme), the app saves it to `config.json`.  
   - On the next startup, the app will load these preferences automatically.

---

## File Structure (Example)

```
.
├── BionicReader.py            # Main application script
├── MiSans-Regular.otf         # Optional custom font
└── README.md                  # This README
```

---

## Contributing

Feel free to open issues or submit pull requests if you have improvements, bug fixes, or new features to propose.  

1. Fork/clone this repo.
2. Create a new feature branch.
3. Commit and push changes to your repo.
4. Open a pull request.

---

## License

This project is licensed under [MIT License](https://opensource.org/licenses/MIT). You’re free to use, modify, and distribute it for personal or commercial use.  

Enjoy faster, clearer reading with Bionic Reading App!  