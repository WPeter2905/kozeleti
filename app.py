import streamlit as st
import pandas as pd
from typing import List, Dict, Any
import json
import os
import subprocess
from pathlib import Path

# --- Criteria definitions (copied from main.py) ---
tev1_szov = ["0-150 hallgató","200-300 hallgató","350-500 hallgató","550-700 hallgató","750+ hallgató"]
tev1_pont = [3, 6, 10, 14, 15]
tev2_szov =["A tevékenység vonatkozásában megfogalmazott célok nem vagy elhanyagolható mértékben tükrözték az elvárt eredmény(eke)t", "A tevékenység vonatkozásában megfogalmazott célok átlagos mértékben tükrözték az elvárt eredmény(eke)t" ,"A tevékenység vonatkozásában megfogalmazott célok átlagon felüli mértékben tükrözték az elvárt eredmény(eke)t", "A tevékenység vonatkozásában megfogalmazott célok kiválóan / teljes mértékben tükrözték az elvárt eredmény(eke)t"] 
tev2_pont =[2, 6, 8, 10]
tev3_szov = ["A tevékenység megvalósítása nem vagy elhanyagolható mértékben igényel speciális tudást vagy háttérismeretet és a tevékenység nem komplex","A tevékenység megvalósítása átlagos mértékű speciális tudást igényel és komplex a tevékenység","A tevékenység megvalósítása jelentős mértékű háttérismeretet, speciális tudást igényel és komplex a tevékenység"]
tev3_pont = [2, 6, 10]
tev4_szov = ["A határidőket nem, vagy csak többszöri felszólításra tartotta be", "A határidőket egyszeri felszólításra tartotta be", "A határidőket önmagától betartotta"]
tev4_pont = [1, 3, 5]
tev5_szov = ["A tevékenységet önállóan nem vagy alig tudta megvalósítani", "A tevékenységet részleges önállósággal tudta megvalósítani", "A tevékenységet teljes önállósággal tudta megvalósítani"]
tev5_pont = [1, 3, 5]
tev6_szov = ["A tevékenységet végző személy nem vagy elhanyagolható mértékben fordított időt a tevékenység megvalósítására", "A tevékenységet végző személy átlagos mértékben fordított időt a tevékenység megvalósítására", "A tevékenységet végző személy  jelentős időmennyiséget fordított a tevékenység megvalósítására"]
tev6_pont = [1, 6, 8]
tev7_szov = ["Jelen szempont a közéleti tevékenység végzése szempontjából nem releváns","az esetek többségében inaktív viselkedést tanúsított.", "az esetek többségében átlagosan aktív viselkedést tanúsított.", "az esetek többségében proaktív viselkedést tanúsított."]
tev7_pont = [0, 2, 6, 8]

CRITERIA = [
    {"name": "1. Hallgatók száma", "szov": tev1_szov, "pont": tev1_pont},
    {"name": "2. Célok megvalósulása", "szov": tev2_szov, "pont": tev2_pont},
    {"name": "3. Szükséges tudás", "szov": tev3_szov, "pont": tev3_pont},
    {"name": "4. Határidő betartása", "szov": tev4_szov, "pont": tev4_pont},
    {"name": "5. Önállóság", "szov": tev5_szov, "pont": tev5_pont},
    {"name": "6. Fordított idő", "szov": tev6_szov, "pont": tev6_pont},
    {"name": "7. Viselkedés", "szov": tev7_szov, "pont": tev7_pont},
]

# Persistence file path
SCORES_FILE = Path('scores.json')


def save_scores(students: List[Dict[str, Any]]):
    """Save student scores to JSON file."""
    data = []
    for s in students:
        data.append({
            'name': s['name'],
            'time': s['time'],
            'neptun': s['neptun'],
            'major': s['major'],
            'pontszam': s['pontszam'],
            'is_relevant': s['is_relevant'],
            'is_done': s['is_done'],
            'leiras': s.get('leiras', ''),
            'kategoria': s.get('kategoria', ''),
        })
    with open(SCORES_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_scores(students: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Load saved scores from JSON file and merge with current student list."""
    if not SCORES_FILE.exists():
        return students
    
    try:
        with open(SCORES_FILE, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
        
        # Create a map of neptun -> saved scores
        saved_map = {item['neptun']: item for item in saved_data}
        
        # Merge saved data into current students
        for s in students:
            if s['neptun'] in saved_map:
                saved = saved_map[s['neptun']]
                s['pontszam'] = saved.get('pontszam', [None] * len(CRITERIA))
                s['is_relevant'] = saved.get('is_relevant', [True] * len(CRITERIA))
                s['is_done'] = saved.get('is_done', False)
                s['leiras'] = saved.get('leiras', '')
                s['kategoria'] = saved.get('kategoria', '')
        
        return students
    except Exception as e:
        st.warning(f"Hiba a scores.json betöltésekor: {e}")
        return students


def get_grade_ranges(points_list: List[int]) -> List[tuple]:
    """
    Convert points list to grade ranges.
    E.g., [3, 6, 10, 14, 15] → [(0, 3), (4, 6), (7, 10), (11, 14), (15, 15)]
    """
    if not points_list:
        return []
    
    ranges = []
    prev = 0
    for p in points_list:
        if p < prev:
            continue  # Skip if out of order
        ranges.append((prev, p))
        prev = p + 1
    
    return ranges


def point_to_grade_index(point_value: int, points_list: List[int]) -> int:
    """Convert actual point value to grade index (0-based)."""
    if point_value is None or point_value == 0:
        return -1  # No selection
    
    ranges = get_grade_ranges(points_list)
    for idx, (min_p, max_p) in enumerate(ranges):
        if min_p <= point_value <= max_p:
            return idx
    
    return -1


def grade_index_to_point(grade_idx: int, points_list: List[int]) -> int:
    """Convert grade index to the corresponding maximum point value."""
    if grade_idx < 0 or grade_idx >= len(points_list):
        return 0
    return points_list[grade_idx]



def load_students(path: str) -> List[Dict[str, Any]]:
    df = pd.read_csv(path, sep=';')
    students = []
    for _, row in df.iterrows():
        students.append({
            'name': row.get('name', ''),
            'time': row.get('time', ''),
            'neptun': row.get('neptun', ''),
            'major': row.get('major', ''),
            'pontszam': [None] * len(CRITERIA),
            'is_relevant': [True] * len(CRITERIA),
            'is_done': False,
            'leiras': '',
            'kategoria': '',
        })
    return students


def calculate_total(st: Dict[str, Any]) -> int:
    total = 0
    for i, p in enumerate(st['pontszam']):
        if p is not None and st['is_relevant'][i]:
            total += p
    return total


def calculate_osszeg(total_points: int) -> int:
    """Calculate OSSZEG (total money): points × 2500"""
    return total_points * 2500


def ensure_state(path='data.csv'):
    if 'students' not in st.session_state:
        students = load_students(path)
        # Load any previously saved scores
        students = load_scores(students)
        st.session_state['students'] = students


def student_dataframe(students: List[Dict[str, Any]]) -> pd.DataFrame:
    rows = []
    for s in students:
        row = {
            'name': s['name'],
            'time': s['time'],
            'neptun': s['neptun'],
            'major': s['major'],
            'is_done': s['is_done'],
        }
        for i in range(len(CRITERIA)):
            row[f'p_{i}'] = s['pontszam'][i]
            row[f'rel_{i}'] = s['is_relevant'][i]
        rows.append(row)
    return pd.DataFrame(rows)


def get_grade_ranges(points_list: List[int]) -> List[tuple]:
    """Convert points list to grade ranges for filling Word doc."""
    if not points_list:
        return []
    
    ranges = []
    prev = 0
    for p in points_list:
        if p < prev:
            continue
        ranges.append((prev, p))
        prev = p + 1
    
    return ranges


def point_to_grade_index_word(point_value: int, points_list: List[int]) -> int:
    """Convert actual point value to grade index for Word filling."""
    if point_value is None or point_value == 0:
        return -1
    
    ranges = get_grade_ranges(points_list)
    for idx, (min_p, max_p) in enumerate(ranges):
        if min_p <= point_value <= max_p:
            return idx
    
    return -1


def get_grade_text_word(point_value: int, criteria_dict: Dict) -> str:
    """Get grade text for Word document."""
    if point_value is None or point_value == 0:
        return criteria_dict['szov'][0]
    
    pts = criteria_dict['pont']
    texts = criteria_dict['szov']
    grade_idx = point_to_grade_index_word(point_value, pts)
    
    if grade_idx >= 0 and grade_idx < len(texts):
        return texts[grade_idx]
    else:
        return texts[0] if texts else "N/A"


def fill_word_document(student: Dict[str, Any], template_path: Path = Path('sablon.docx')):
    """Fill Word template with student data and return path to filled document.

    This collects all inserted values and then calls a helper that transfers
    paragraph formatting from the preceding blank paragraph before deleting it.
    That preserves the template's visual style while removing the extra blank rows.
    """
    from docx import Document

    try:
        output_dir = Path('filled_documents')
        output_dir.mkdir(exist_ok=True)

        doc = Document(str(template_path))

        # Collect filled values so we can locate where to remove the preceding blank paragraph
        filled_values: List[str] = []

        def put(key: str, value: Any):
            replace_text_in_doc(doc, key, str(value))
            filled_values.append(str(value))

        # Basic student info
        put('[NÉV]', student['name'])
        put('[NEPTUN]', student['neptun'])
        put('[SZAK]', student['major'])
        put('[ÉV]', student['time'])
        put('[KATEGORIA]', student.get('kategoria', ''))

        # Totals
        total = 0
        for i, p in enumerate(student['pontszam']):
            if p is not None and student['is_relevant'][i]:
                total += p

        put('[ÖSSZ_PONT]', total)

        max_total = sum(max(c['pont']) for c in CRITERIA)
        put('[MAX_PONT]', max_total)

        osszeg = calculate_osszeg(total)
        put('[OSSZEG]', osszeg)

        put('[LEIRAS]', student.get('leiras', ''))

        # Criteria values
        for i, crit in enumerate(CRITERIA):
            point_value = student['pontszam'][i]
            is_relevant = student['is_relevant'][i]

            pt_str = str(point_value) if point_value is not None else '0'
            put(f'[TEV{i+1}_PONT]', pt_str)

            if not is_relevant:
                grade_text = "Jelen szempont a közéleti tevékenység végzése szempontjából nem releváns"
            elif point_value is not None:
                grade_text = get_grade_text_word(point_value, crit)
            else:
                grade_text = "Nincs választás"

            put(f'[TEV{i+1}_SZOV]', grade_text)

        # Transfer paragraph formatting and remove preceding blank rows where needed
        transfer_format_and_remove_prev_blank(doc, filled_values)

        # Save
        output_file = output_dir / f"{student['name']}_{student['neptun']}.docx"
        doc.save(str(output_file))
        return output_file

    except Exception as e:
        st.error(f"Hiba a Word dokumentum kitöltésekor: {e}")
        return None


def replace_text_in_doc(doc, old_text: str, new_text: str):
    """Replace text in Word document, handling runs properly and removing one blank line before each placeholder."""
    # Replace in paragraphs
    for paragraph in doc.paragraphs:
        if old_text in paragraph.text:
            # Build full text from runs
            full_text = ''.join(run.text for run in paragraph.runs)
            if old_text in full_text:
                # Replace the text first
                new_full_text = full_text.replace(old_text, new_text)
                # Clear all runs
                for run in paragraph.runs:
                    run.text = ""
                # Add new text to first run
                if paragraph.runs:
                    paragraph.runs[0].text = new_full_text
                else:
                    paragraph.add_run(new_full_text)
    
    # Replace in tables
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    if old_text in paragraph.text:
                        full_text = ''.join(run.text for run in paragraph.runs)
                        if old_text in full_text:
                            # Replace the text
                            new_full_text = full_text.replace(old_text, new_text)
                            for run in paragraph.runs:
                                run.text = ""
                            if paragraph.runs:
                                paragraph.runs[0].text = new_full_text
                            else:
                                paragraph.add_run(new_full_text)


def transfer_format_and_remove_prev_blank(doc, filled_values: List[str]):
    """For each filled value, find paragraphs containing it, and if the
    immediately preceding sibling paragraph is blank, transfer paragraph and
    run formatting from that blank paragraph into the filled paragraph,
    then remove the blank paragraph element from the document tree.

    This preserves the template styling while eliminating the empty row.
    """
    from docx.text.paragraph import Paragraph

    def _transfer_and_remove(paragraph):
        # previous sibling element
        prev_elm = paragraph._p.getprevious()
        if prev_elm is None:
            return
        # ensure it's a paragraph element
        if not prev_elm.tag.endswith('}p'):
            return
        try:
            prev_para = Paragraph(prev_elm, paragraph._parent)
        except Exception:
            return

        if prev_para.text and prev_para.text.strip():
            return

        # Transfer paragraph-level formatting
        try:
            paragraph.style = prev_para.style
        except Exception:
            pass
        try:
            paragraph.alignment = prev_para.alignment
        except Exception:
            pass
        # Transfer spacing and indentation if present
        try:
            paragraph.paragraph_format.left_indent = prev_para.paragraph_format.left_indent
            paragraph.paragraph_format.right_indent = prev_para.paragraph_format.right_indent
            paragraph.paragraph_format.first_line_indent = prev_para.paragraph_format.first_line_indent
            paragraph.paragraph_format.space_before = prev_para.paragraph_format.space_before
            paragraph.paragraph_format.space_after = prev_para.paragraph_format.space_after
        except Exception:
            pass

        # Transfer run-level formatting: apply first non-empty run font of prev to first run of paragraph
        try:
            if prev_para.runs and paragraph.runs:
                src_font = prev_para.runs[0].font
                dst_font = paragraph.runs[0].font
                # Copy common attributes if set
                for attr in ('name', 'size', 'bold', 'italic', 'underline', 'color'):
                    try:
                        val = getattr(src_font, attr)
                        if val is not None:
                            setattr(dst_font, attr, val)
                    except Exception:
                        pass
        except Exception:
            pass

        # Remove the blank previous paragraph element
        try:
            prev_elm.getparent().remove(prev_elm)
        except Exception:
            pass

    # Iterate through the document paragraphs and table cell paragraphs
    # For each filled value, locate matching paragraphs and process them.
    for value in filled_values:
        if not value:
            continue

        # top-level paragraphs
        for paragraph in list(doc.paragraphs):
            if value in paragraph.text:
                _transfer_and_remove(paragraph)

        # paragraphs inside tables
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for paragraph in list(cell.paragraphs):
                        if value in paragraph.text:
                            _transfer_and_remove(paragraph)


def remove_preceding_newline(doc, placeholder: str):
    """Remove newline character before a placeholder. (Deprecated)"""
    pass


def main():
    st.set_page_config(layout='wide', page_title='Közéleti pontozó', initial_sidebar_state='expanded')
    
    # Compact CSS: reduce margins and padding
    st.markdown("""
    <style>
    .element-container {
        margin-bottom: 0.5rem !important;
    }
    [data-testid="stVerticalBlock"] > [style*="flex-direction: column"] > [data-testid="stVerticalBlock"] {
        gap: 0 !important;
    }
    h2 { margin-top: 0.3rem !important; margin-bottom: 0.3rem !important; }
    h3 { margin-top: 0.2rem !important; margin-bottom: 0.2rem !important; }
    </style>
    """, unsafe_allow_html=True)
    
    st.title('Közéleti tevékenység pontozó')

    ensure_state('data.csv')
    students = st.session_state['students']

    # Define helper callbacks early
    import re

    def make_slider_callback(sidx_local, idx_local, sel_key_local):
        def _cb():
            val = st.session_state.get(sel_key_local, 0)
            # treat 0 as no selection
            st.session_state['students'][sidx_local]['pontszam'][idx_local] = int(val) if int(val) != 0 else None
            st.session_state['_last_update'] = st.session_state.get('_last_update', 0) + 1
            # Save to disk
            save_scores(st.session_state['students'])
            try:
                if hasattr(st, 'experimental_rerun'):
                    st.experimental_rerun()
            except Exception:
                pass
        return _cb

    def make_rel_callback(sidx_local, idx_local, rel_key_local):
        def _cb():
            val = st.session_state.get(rel_key_local, True)
            st.session_state['students'][sidx_local]['is_relevant'][idx_local] = bool(val)
            st.session_state['_last_update'] = st.session_state.get('_last_update', 0) + 1
            # Save to disk
            save_scores(st.session_state['students'])
        return _cb

    def make_done_callback(sidx_local, done_key_local):
        def _cb():
            val = st.session_state.get(done_key_local, False)
            st.session_state['students'][sidx_local]['is_done'] = bool(val)
            st.session_state['_last_update'] = st.session_state.get('_last_update', 0) + 1
            # Save to disk
            save_scores(st.session_state['students'])
        return _cb
    
    def make_leiras_callback(sidx_local, desc_key_local):
        def _cb():
            val = st.session_state.get(desc_key_local, '')
            st.session_state['students'][sidx_local]['leiras'] = str(val)[:500]
            st.session_state['_last_update'] = st.session_state.get('_last_update', 0) + 1
            save_scores(st.session_state['students'])
        return _cb
    
    def make_kategoria_callback(sidx_local, kat_key_local):
        def _cb():
            val = st.session_state.get(kat_key_local, '')
            st.session_state['students'][sidx_local]['kategoria'] = str(val)[:5]
            st.session_state['_last_update'] = st.session_state.get('_last_update', 0) + 1
            save_scores(st.session_state['students'])
        return _cb

    def _grade_slider_callback(sidx_local, idx_local, sel_key_local, pts_local):
        """Callback for numeric input: store the entered point value."""
        point_val = st.session_state.get(sel_key_local, 0)
        if point_val is None or point_val < 0:
            st.session_state['students'][sidx_local]['pontszam'][idx_local] = None
        else:
            # Clamp to max valid point
            max_pt = max(pts_local) if pts_local else 0
            point_val = min(point_val, max_pt)
            st.session_state['students'][sidx_local]['pontszam'][idx_local] = int(point_val)
        
        st.session_state['_last_update'] = st.session_state.get('_last_update', 0) + 1
        save_scores(st.session_state['students'])
        try:
            if hasattr(st, 'experimental_rerun'):
                st.experimental_rerun()
        except Exception:
            pass
    with st.sidebar:
        st.header('Hallgatók')
        opts = [f"{s['name']} — {calculate_total(s)}p ({calculate_osszeg(calculate_total(s))}){' ✓' if s['is_done'] else ''}" for s in students]
        if opts:
            # Persist selected student index in session state
            if 'selected_student_idx' not in st.session_state:
                st.session_state['selected_student_idx'] = 0
            sel = st.radio('Válassz hallgatót', options=list(range(len(opts))), format_func=lambda i: opts[i], key='selected_student_idx')
        else:
            st.info('Nincs betöltött hallgató')
            return
        st.markdown(f"Összesen: **{len(students)}**")

    sidx = sel
    
    # Header row with student info and metrics inline
    header_cols = st.columns([3, 1, 1, 1, 1])
    with header_cols[0]:
        st.markdown(f"## {students[sidx]['name']}")
        st.caption(f"Neptun: {students[sidx]['neptun']} — Szak: {students[sidx]['major']} — Év: {students[sidx]['time']}")
    
    with header_cols[1]:
        total = calculate_total(students[sidx])
        st.metric('Összpontszám', f"{total}p")
    
    with header_cols[2]:
        max_total = sum(max(c['pont']) for c in CRITERIA)
        st.metric('Max', f"{max_total}p")
    
    with header_cols[3]:
        osszeg = calculate_osszeg(calculate_total(students[sidx]))
        st.metric('OSSZEG', f"{osszeg}")
    
    with header_cols[4]:
        done_key = f'done_{sidx}'
        if done_key not in st.session_state:
            st.session_state[done_key] = students[sidx]['is_done']
        st.checkbox('Kész', value=st.session_state[done_key], key=done_key, on_change=make_done_callback(sidx, done_key))

    st.markdown('---')

    # Criteria

    def get_description_for_value(crit_local, val_local):
        if val_local is None or val_local == 0:
            return 'Nincs választás'
        pts = crit_local['pont']
        texts = crit_local['szov']
        # find highest index where point <= val_local
        idx = 0
        for j, p in enumerate(pts):
            if val_local >= p:
                idx = j
        # clamp
        if idx < 0:
            idx = 0
        if idx >= len(texts):
            idx = len(texts) - 1
        return texts[idx]

    for i, crit in enumerate(CRITERIA):
        st.markdown(f"**{crit['name']}**")
        col1, col2 = st.columns([3, 1])
        
        rel_key = f'rel_{sidx}_{i}'
        sel_key = f'sel_{sidx}_{i}'
        
        # relevance checkbox (narrow column)
        with col2:
            if rel_key not in st.session_state:
                st.session_state[rel_key] = students[sidx]['is_relevant'][i]
            is_relevant = st.checkbox('Rel.', value=st.session_state[rel_key], key=rel_key, on_change=make_rel_callback(sidx, i, rel_key))
        
        # numeric input + description (wide column)
        with col1:
            if not is_relevant:
                # Show "not relevant" message
                st.caption("⚠️ Jelen szempont a közéleti tevékenység végzése szempontjából nem releváns")
            else:
                pts = crit['pont']
                texts = crit['szov']
                max_pt = max(pts) if pts else 0
                
                # Current point value stored
                current_point = students[sidx]['pontszam'][i]
                if current_point is None:
                    current_point = 0
                
                if sel_key not in st.session_state:
                    st.session_state[sel_key] = int(current_point)
                
                input_col, desc_col = st.columns([2, 3])
                with input_col:
                    # Numeric input from 0 to max_pt
                    point_val = st.number_input(
                        'Pont',
                        min_value=0,
                        max_value=int(max_pt),
                        value=int(st.session_state.get(sel_key, 0)),
                        step=1,
                        key=sel_key,
                        on_change=lambda sidx_l=sidx, idx_l=i, sel_k=sel_key, pts_l=pts: _grade_slider_callback(sidx_l, idx_l, sel_k, pts_l),
                        label_visibility='collapsed'
                    )
                
                with desc_col:
                    # Map point value to grade text
                    # When 0, show first grade text; otherwise find based on threshold
                    if point_val == 0:
                        desc = texts[0] if texts else 'Nincs választás'
                    else:
                        grade_idx = point_to_grade_index(int(point_val), pts)
                        if grade_idx >= 0 and grade_idx < len(texts):
                            desc = texts[grade_idx]
                        else:
                            desc = texts[0] if texts else 'Nincs választás'
                    st.caption(desc)

    st.markdown('---')
    
    # Category field (max 5 characters)
    kat_key = f'kategoria_{sidx}'
    if kat_key not in st.session_state:
        st.session_state[kat_key] = students[sidx].get('kategoria', '')
    st.text_input(
        'Kategória',
        value=st.session_state.get(kat_key, ''),
        max_chars=5,
        key=kat_key,
        on_change=make_kategoria_callback(sidx, kat_key),
        placeholder='Max 5 karakter'
    )
    
    # Description field (single for entire student) - hidden but stored
    desc_key = f'leiras_{sidx}'
    if desc_key not in st.session_state:
        st.session_state[desc_key] = students[sidx]['leiras']
    st.text_area(
        'Leírás',
        value=st.session_state.get(desc_key, ''),
        max_chars=500,
        key=desc_key,
        on_change=make_leiras_callback(sidx, desc_key),
        placeholder='Max 500 karakter...',
        height=80,
        label_visibility='collapsed'
    )
    
    st.markdown('---')
    # Actions
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button('Mentés (letöltés CSV)'):
            df = student_dataframe(students)
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button('Letöltés CSV', data=csv, file_name='scored_students.csv', mime='text/csv')
    with c2:
        if st.button('Word doksi kitöltés'):
            filled_doc = fill_word_document(students[sidx])
            if filled_doc:
                st.success(f"Dokumentum elkészült: {filled_doc.name}")
                # Open the document
                try:
                    subprocess.Popen(['open', str(filled_doc)])
                except Exception as e:
                    st.warning(f"Hiba a dokumentum megnyitásakor: {e}")
    with c3:
        if st.button('Frissít listát'):
            # Try to rerun for Streamlit versions that expose the helper.
            # Some Streamlit installations may not have `experimental_rerun` (different versions),
            # so fall back to a harmless session-state update and a message.
            try:
                if hasattr(st, 'experimental_rerun'):
                    st.experimental_rerun()
                else:
                    st.session_state['_last_update'] = st.session_state.get('_last_update', 0) + 1
                    st.success('Lista frissítve')
            except Exception:
                st.session_state['_last_update'] = st.session_state.get('_last_update', 0) + 1
                st.success('Lista frissítve')


if __name__ == '__main__':
    main()

