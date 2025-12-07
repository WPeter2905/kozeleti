# Közéleti Tevékenység Pontozó

A Streamlit-based web application for grading public service activities (közéleti tevékenység) with 7 evaluation criteria, persistent data storage, and automatic Word document generation.

## Features

- **Student Management**: Load students from CSV and manage scoring data
- **7 Grading Criteria**: Evaluate students on multiple dimensions:
  1. Hallgatók száma (Number of Students)
  2. Célok megvalósulása (Goal Achievement)
  3. Szükséges tudás (Required Knowledge)
  4. Határidő betartása (Deadline Compliance)
  5. Önállóság (Independence)
  6. Fordított idő (Time Invested)
  7. Viselkedés (Behavior)

- **Numeric Point System**: Each criterion has a range of points (0-15 max) with automatic grade text mapping
- **Persistent Storage**: Scores are saved to `scores.json` and automatically loaded on restart
- **Category & Description Fields**: Add custom category (5 chars) and detailed description for each student
- **OSSZEG Calculation**: Automatic monetary calculation (points × 2500)
- **Word Document Generation**: Fill a Word template (`sablon.docx`) with student data and generate formatted documents
- **Blank Row Removal**: Automatically removes template blank rows while preserving formatting

## Installation

### Requirements
- Python 3.6+
- pip

### Setup

1. Clone the repository:
```bash
git clone https://github.com/WPeter2905/kozeleti.git
cd kozeleti
```

2. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Starting the App

Run the application:
```bash
python start.py
```

This will automatically open `http://localhost:8501` in your browser.

Alternatively:
```bash
streamlit run app.py
```

Or use the shell script:
```bash
bash run.sh
```

### Input Data

Prepare a `data.csv` file with semicolon-separated student data:
```csv
name;neptun;major;time
Student Name;NEPTUN1;Major;Year
```

### Word Template

Create a `sablon.docx` Word document with these placeholders:
- `[NÉV]`, `[NEPTUN]`, `[SZAK]`, `[ÉV]` - Student info
- `[KATEGORIA]` - Category
- `[ÖSSZ_PONT]`, `[MAX_PONT]`, `[OSSZEG]` - Points and amount
- `[LEIRAS]` - Description
- `[TEV1_PONT]` through `[TEV7_PONT]` - Points for each criterion
- `[TEV1_SZOV]` through `[TEV7_SZOV]` - Grade text for each criterion

## Output

- Generated Word documents: `filled_documents/` directory
- Persistent scores: `scores.json`

## File Structure

```
├── app.py                 # Main Streamlit application
├── fill_word_template.py  # Standalone Word filler script
├── start.py              # Auto-launcher script
├── run.sh                # Shell script launcher
├── requirements.txt      # Python dependencies
├── data.csv             # Student input data
├── sablon.docx          # Word template
├── scores.json          # Persistent scoring data (auto-created)
├── filled_documents/    # Generated documents (auto-created)
└── README.md            # This file
```

## Technologies

- **Streamlit** - Web UI framework
- **Pandas** - Data handling
- **python-docx** - Word document generation

## License

MIT License - See LICENSE file for details

---

**Status**: Active Development  
**Language**: Hungarian UI with English documentation  
**Author**: WPeter2905