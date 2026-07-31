import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import re
import ast
import json # ⚡ เพิ่ม import json สำหรับจัดการไฟล์
from scipy.interpolate import interp1d # ⚡ เพิ่ม interp1d สำหรับ Time Series Lookup

# ==========================================
# 1. การตั้งค่าหน้ากระดานปฏิบัติการ (Fit Layout)
# ==========================================
st.set_page_config(page_title="System Dynamics Simulator", page_icon="🌊", layout="wide")

# ==========================================
# 0. ธีมและสไตล์ (Custom CSS Design System)
# ==========================================
st.markdown("""
<style>
    :root {
        --sd-primary:   #2563eb;
        --sd-primary-2: #0ea5e9;
        --sd-accent:    #f97316;
        --sd-bg-soft:   #f8fafc;
        --sd-ink:       #0f172a;
        --sd-line:      #e2e8f0;
    }

    /* พื้นหลังหลัก */
    .stApp { background: linear-gradient(180deg, #f8fafc 0%, #eef2ff 100%); }

    /* หัวข้อใหญ่ */
    h1 { font-weight: 800 !important; letter-spacing: -0.5px;
         background: linear-gradient(90deg, var(--sd-primary), var(--sd-primary-2));
         -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    h2, h3 { font-weight: 700 !important; color: var(--sd-ink) !important; }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
        border-right: 1px solid #1e293b;
    }
    section[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
    section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 { color: #f8fafc !important; }

    /* ⚡ กล่องกรอกข้อมูล (text/number/select) พื้นหลังสว่าง ตัวหนังสือต้องเข้ม ไม่ใช่ขาว */
    section[data-testid="stSidebar"] input,
    section[data-testid="stSidebar"] textarea {
        color: #0f172a !important;
        background-color: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 8px !important;
        caret-color: #0f172a !important;
    }
    section[data-testid="stSidebar"] input::placeholder,
    section[data-testid="stSidebar"] textarea::placeholder { color: #94a3b8 !important; }

    /* Dropdown (selectbox) ปิด/เปิด และ popover รายการตัวเลือก */
    section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        border-radius: 8px !important;
        border: 1px solid #cbd5e1 !important;
    }
    section[data-testid="stSidebar"] div[data-baseweb="select"] * { color: #0f172a !important; }
    div[data-baseweb="popover"] * { color: #0f172a !important; }
    div[data-baseweb="popover"] li { background-color: #ffffff !important; }
    div[data-baseweb="popover"] li:hover { background-color: #eef2ff !important; }

    /* ⚡ ปุ่ม +/- ของ number_input และไอคอนขั้นบันได — ใช้ทั้งแอป ไม่ใช่แค่ sidebar
       (บางไอคอนของ Streamlit วาดด้วย stroke ไม่ใช่ fill เลยแก้ทั้งคู่ พร้อมขยายขนาดให้เห็นชัด) */
    button[data-testid^="stNumberInputStep"] {
        background-color: #eef2ff !important;
        border: 1px solid #94a3b8 !important;
        border-radius: 6px !important;
        min-width: 24px !important;
        min-height: 24px !important;
        opacity: 1 !important;
    }
    button[data-testid^="stNumberInputStep"]:hover {
        background-color: #c7d2fe !important; border-color: var(--sd-primary) !important;
    }
    button[data-testid^="stNumberInputStep"] svg {
        fill: #1e293b !important;
        stroke: #1e293b !important;
        width: 12px !important;
        height: 12px !important;
    }

    /* ⚡ ป้ายโค้ด `แบบนี้` ที่ใช้บอกชื่อตัวแปร/ฟังก์ชัน — ต้องอ่านออกทั้งพื้นและตัวหนังสือ */
    section[data-testid="stSidebar"] code {
        color: #0f172a !important;
        background-color: #e0e7ff !important;
        border-radius: 5px !important;
        padding: 1px 5px !important;
    }

    /* ⚡ กล่อง Expander ("A. สร้างวัตถุบนกระดาน" ฯลฯ) — ให้เป็นการ์ดเข้มมีขอบ อ่านง่ายชัดเจน */
    section[data-testid="stSidebar"] div[data-testid="stExpander"] {
        background-color: #1e293b !important;
        border: 1px solid #334155 !important;
        border-radius: 12px !important;
        overflow: hidden;
    }
    section[data-testid="stSidebar"] div[data-testid="stExpander"] summary {
        background-color: #1e293b !important;
        padding: 10px 12px !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stExpander"] summary:hover {
        background-color: #27364d !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stExpander"] summary p {
        color: #f8fafc !important;
        font-weight: 700 !important;
        font-size: 15.5px !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stExpander"] svg { fill: #f8fafc !important; }

    /* ⚡ Label ของทุก widget (file_uploader, text_input, number_input, selectbox, slider,
       radio, multiselect ฯลฯ) — เดิมใช้ font เล็ก/บางกว่าตัวหนังสือในปุ่มมาก ทำให้
       "อัปโหลดโมเดล" ดูเล็กกว่า "ดาวน์โหลดโมเดล" ทั้งที่ควรมีน้ำหนักสายตาเท่ากัน
       ปรับให้ label ทุกตัวในแอปใช้ขนาด/น้ำหนักเดียวกันหมด เพื่อความสม่ำเสมอ */
    div[data-testid="stWidgetLabel"] p {
        font-size: 15px !important;
        font-weight: 600 !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stWidgetLabel"] p {
        color: #f1f5f9 !important;
    }

    section[data-testid="stSidebar"] .stButton>button p {
        font-size: 15px !important;
    }
    section[data-testid="stSidebar"] .stButton>button {
        border-radius: 10px; border: 1px solid #334155; background: #1e293b;
        transition: all 0.15s ease-in-out;
    }
    section[data-testid="stSidebar"] .stButton>button:hover {
        border-color: var(--sd-primary-2); background: #27364d; transform: translateY(-1px);
    }

    /* ⚡ ปุ่มลบ / ปุ่มอันตราย (type="primary" ในเมนูฝั่งซ้าย) — เดิมโดนกฎปุ่มทั่วไปด้านบน
       ทับด้วย specificity ที่สูงกว่า ทำให้กลายเป็นสีเข้มกลืนกับปุ่มอื่นจนแยกไม่ออกว่าเป็นปุ่มลบ
       ใส่ !important เพื่อการันตีว่าชนะ cascade แน่นอน พร้อมให้เป็นสีแดงสื่อถึงการกระทำที่ทำลายข้อมูล */
    section[data-testid="stSidebar"] .stButton>button[kind="primary"] {
        background: linear-gradient(90deg, #dc2626, #ef4444) !important;
        border: 1px solid #b91c1c !important;
        box-shadow: 0 2px 8px rgba(220,38,38,0.35) !important;
    }
    section[data-testid="stSidebar"] .stButton>button[kind="primary"] p {
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 15px !important;
    }
    section[data-testid="stSidebar"] .stButton>button[kind="primary"]:hover {
        background: linear-gradient(90deg, #b91c1c, #dc2626) !important;
        border-color: #991b1b !important;
        transform: translateY(-1px);
    }

    /* ⚡ ปุ่ม "ดาวน์โหลดโมเดล (Save JSON)" — เดิมพื้นขาว ตัวหนังสือขาวมองไม่เห็น */
    section[data-testid="stSidebar"] div[data-testid="stDownloadButton"] button {
        background-color: #1e293b !important;
        border: 1px solid #334155 !important;
        border-radius: 10px !important;
        transition: all 0.15s ease-in-out;
    }
    section[data-testid="stSidebar"] div[data-testid="stDownloadButton"] button p {
        color: #f8fafc !important; font-weight: 600 !important; font-size: 15px !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stDownloadButton"] button:hover {
        background-color: #27364d !important; border-color: var(--sd-primary-2) !important;
    }

    /* ⚡ กล่อง "อัปโหลดโมเดล (Load JSON)" — โซนลาก-วางไฟล์และปุ่ม Browse files */
    section[data-testid="stSidebar"] div[data-testid="stFileUploader"] section {
        background-color: #ffffff !important;
        border: 2px dashed #cbd5e1 !important;
        border-radius: 12px !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stFileUploader"] section * {
        color: #334155 !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stFileUploader"] section small {
        color: #94a3b8 !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stFileUploader"] button {
        background-color: #f1f5f9 !important;
        border: 1px solid #cbd5e1 !important;
        color: #0f172a !important;
        border-radius: 8px !important;
        font-size: 15px !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stFileUploader"] svg {
        fill: #64748b !important;
    }
    /* ไฟล์ที่อัปโหลดแล้ว (แถบชื่อไฟล์ + ปุ่มลบ) ที่ปรากฏใต้กล่องลาก-วาง */
    section[data-testid="stSidebar"] div[data-testid="stFileUploaderFile"] {
        background-color: #1e293b !important; border-radius: 8px !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stFileUploaderFile"] * {
        color: #e2e8f0 !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stFileUploaderFile"] svg {
        fill: #e2e8f0 !important;
    }
    /* ⚡ ปุ่ม "×" ลบไฟล์ที่แนบไว้แล้ว — เดิมพื้นหลังของปุ่มเองเป็นวงกลมสีอ่อนจางๆ ที่ไม่มีกฎ
       ไหนคลุมถึง (กฎก่อนหน้านี้ตั้งแค่สี svg/ตัวหนังสือ ไม่ได้ตั้งพื้นหลังปุ่ม) ให้เป็นสีแดงชัดเจน
       เหมือนปุ่มลบอื่นๆ ในธีม */
    section[data-testid="stSidebar"] div[data-testid="stFileUploaderFile"] button {
        background-color: #ef4444 !important;
        border: 1px solid #b91c1c !important;
        border-radius: 50% !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stFileUploaderFile"] button svg {
        fill: #ffffff !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stFileUploaderFile"] button:hover {
        background-color: #dc2626 !important;
    }
    /* ไอคอน "?" คำอธิบายเพิ่มเติม (tooltip help) */
    section[data-testid="stSidebar"] [data-testid="stTooltipIcon"] svg {
        fill: #94a3b8 !important;
    }

    /* การ์ด/กล่องเนื้อหาหลัก */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 16px !important;
    }

    /* ปุ่มหลักในพื้นที่ทำงาน */
    .stButton>button[kind="primary"] {
        border-radius: 12px; font-weight: 700; border: none;
        background: linear-gradient(90deg, var(--sd-primary), var(--sd-primary-2));
        box-shadow: 0 4px 14px rgba(37,99,235,0.35);
    }
    .stButton>button[kind="primary"]:hover { filter: brightness(1.08); }

    /* กล่อง metric / status */
    div[data-testid="stMetric"] {
        background: #ffffff; border: 1px solid var(--sd-line); border-radius: 14px;
        padding: 10px 14px; box-shadow: 0 1px 3px rgba(15,23,42,0.06);
    }

    /* เส้นคั่น */
    hr { border-color: var(--sd-line) !important; }

    /* แถบ badge เล็กๆ — ⚡ รอบก่อนใส่ !important แล้วแต่ specificity ยังแพ้กฎกว้างของ sidebar
       (section[data-testid="stSidebar"] * มี specificity สูงกว่า .sd-badge เฉยๆ แม้มี !important
       ทั้งคู่ ตัวที่ specificity สูงกว่าชนะเสมอ ไม่ใช่ตัวที่มาทีหลัง) แก้โดยใส่ selector scope
       แบบเดียวกับกฎกว้างให้ specificity เท่ากันหรือสูงกว่า จะได้ชนะแน่นอน */
    section[data-testid="stSidebar"] span.sd-badge {
        display:inline-block !important; padding: 2px 10px !important; border-radius: 999px !important;
        background: #e0e7ff !important; color: #3730a3 !important;
        font-size: 0.78rem !important; font-weight: 600 !important;
        margin-right: 6px !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("🌊 System Dynamics Simulator")
st.caption("ระบบจำลองสถานการณ์: ออกแบบโครงสร้างและปรับแต่งตัวแปรแบบเรียลไทม์ • รองรับการนำเข้าข้อมูลจริง (CSV) และการประมาณค่าแบบ Interpolation")

st.markdown("---")

# ==========================================
# 2. เริ่มต้นสถานะระบบหลักด้วย Session State
# ==========================================
if 'stocks' not in st.session_state:
    st.session_state.stocks = {} 
if 'parameters' not in st.session_state:
    st.session_state.parameters = {} 
if 'flows' not in st.session_state:
    st.session_state.flows = {} 
if 'edges' not in st.session_state:
    st.session_state.edges = [] 
if 'sim_calculated' not in st.session_state:
    st.session_state.sim_calculated = False 
if 'baseline_results' not in st.session_state:
    st.session_state.baseline_results = None
if 'bounds' not in st.session_state:
    st.session_state.bounds = {}
if 'timeseries' not in st.session_state:
    st.session_state.timeseries = {}  # ⚡ เก็บข้อมูล CSV ที่นำเข้า: {name: {"time": [...], "value": [...], "kind": "linear"}}

def reset_simulation_state():
    st.session_state.sim_calculated = False
    st.session_state.baseline_results = None
    st.session_state.bounds = {} 

def sanitize_name(name):
    return re.sub(r'\W', '_', name.strip())

# ⚡ ฟังก์ชันคณิตศาสตร์ที่อนุญาตให้ใช้ในสูตร Flow/Parameter ทั้งหมด
def _mod(a, b): return a % b
def _ite(cond, a, b): return a if cond else b

MATH_FUNCS = {
    "sin": np.sin, "cos": np.cos, "tan": np.tan,
    "exp": np.exp, "log": np.log, "log10": np.log10, "sqrt": np.sqrt,
    "min": min, "max": max, "abs": abs, "round": round, "mod": _mod,
    "if_then_else": _ite,
}
RESERVED_NAMES = set(MATH_FUNCS.keys()) | {"t"}

# ⚡ รายการชนิด AST node ที่อนุญาตให้ปรากฏในสูตรได้ (whitelist)
# การ "ไม่รวม" ast.Attribute ในนี้คือหัวใจของการปิดช่องโหว่ sandbox-escape แบบคลาสสิกของ
# Python eval() เช่น "().__class__.__bases__[0].__subclasses__()" ที่สามารถไล่หา
# subprocess.Popen มารันคำสั่งระบบได้ แม้จะตั้ง __builtins__=None แล้วก็ตาม
# (ยืนยันด้วย stress test ก่อน deploy จริงว่า __builtins__=None เพียงอย่างเดียวไม่พอ)
_ALLOWED_AST_NODES = (
    ast.Expression, ast.BinOp, ast.UnaryOp, ast.BoolOp, ast.Compare,
    ast.Call, ast.Name, ast.Load, ast.Constant, ast.IfExp,
    ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow, ast.Mod, ast.FloorDiv,
    ast.USub, ast.UAdd, ast.Not, ast.And, ast.Or,
    ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE,
)

def validate_formula_syntax(formula, extra_allowed_calls=None):
    """⚡ ตรวจสอบสูตรก่อนบันทึกจริงในทุกจุดของแอป (สร้าง Flow ใหม่, แก้ไขสูตรใน C,
    และด่านตรวจตรรกะระบบ) สองชั้น:
    1) Syntax ต้องถูกต้อง (กันปัญหาแบบ 'max(k1, ,k2)' ที่ comma เกินแล้วเงียบๆ
       กลายเป็นค่า 0.0 ตอนรันจริงโดยไม่มีอะไรแจ้งเตือน)
    2) โครงสร้างต้องอยู่ในกรอบที่ปลอดภัย (whitelist AST node + ชื่อฟังก์ชันที่เรียกได้)
       กันไม่ให้ผู้ใช้แอบพิมพ์สูตรที่จริงๆ แล้วเป็นโค้ดอันตราย เช่นการไล่ object graph
       ของ Python เพื่อรันคำสั่งระบบ
    extra_allowed_calls: ชื่อฟังก์ชันเพิ่มเติมที่อนุญาตให้เรียกได้ (เช่นชื่อตัวแปร CSV
    time-series อย่าง Ia ที่ถูกเรียกใช้แบบ Ia(t) ในสูตร)
    คืนค่า (True, None) ถ้าสูตรถูกต้องและปลอดภัย หรือ (False, ข้อความ error) ถ้าไม่ผ่าน"""
    formula_str = str(formula).replace('^', '**')
    try:
        tree = ast.parse(formula_str, mode='eval')
    except SyntaxError as e:
        return False, f"สูตรผิดไวยากรณ์ (Syntax Error): {e.msg} — ตำแหน่งประมาณ {e.text.strip() if e.text else ''}"
    except Exception as e:
        return False, f"สูตรมีปัญหา: {e}"

    allowed_calls = set(MATH_FUNCS.keys()) | (set(extra_allowed_calls) if extra_allowed_calls else set())
    for node in ast.walk(tree):
        if not isinstance(node, _ALLOWED_AST_NODES):
            return False, f"ไม่อนุญาตให้ใช้ {type(node).__name__} ในสูตร (เพื่อความปลอดภัย)"
        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                return False, "เรียกใช้ฟังก์ชันได้เฉพาะชื่อฟังก์ชันตรงๆ เท่านั้น"
            if node.func.id not in allowed_calls:
                return False, f"ไม่รู้จักฟังก์ชัน `{node.func.id}` — ใช้ได้เฉพาะฟังก์ชันที่รองรับเท่านั้น"

    try:
        compile(formula_str, '<string>', 'eval')
    except Exception as e:
        return False, f"สูตรมีปัญหา: {e}"
    return True, None

def build_lookup_functions(timeseries_inputs):
    """สร้างฟังก์ชัน interpolation จากข้อมูล CSV แต่ละชุด เพื่อใช้เป็น exogenous input เช่น Ia(t)"""
    lookups = {}
    for name, data in timeseries_inputs.items():
        t_arr = np.array(data["time"], dtype=float)
        v_arr = np.array(data["value"], dtype=float)
        order = np.argsort(t_arr)
        t_arr, v_arr = t_arr[order], v_arr[order]
        kind = data.get("kind", "linear")
        try:
            f = interp1d(
                t_arr, v_arr, kind=kind,
                bounds_error=False,
                fill_value=(v_arr[0], v_arr[-1])  # ⚡ clamp ค่านอกช่วงข้อมูลด้วยค่าแรก/ค่าสุดท้าย กัน error
            )
        except ValueError:
            # ⚡ เผื่อกรณีโหลดไฟล์ JSON ที่มี timeseries แบบ cubic แต่จุดข้อมูลไม่พอ (<4 จุด)
            # ซึ่งข้ามการเช็คตอนอัปโหลด CSV ปกติมาได้ — fallback เป็น linear แทนไม่ให้แอปพัง
            f = interp1d(t_arr, v_arr, kind="linear", bounds_error=False, fill_value=(v_arr[0], v_arr[-1]))
        lookups[name] = (lambda fn: (lambda tt: float(fn(tt))))(f)
    return lookups

def build_base_context(parameters, timeseries_inputs):
    ctx = dict(MATH_FUNCS)
    ctx.update(build_lookup_functions(timeseries_inputs))
    ctx.update(parameters)
    return ctx

def compute_derivatives(t, stocks, compiled_flows, edges, base_context):
    flow_rates = {}
    
    eval_context = base_context.copy()
    eval_context["t"] = t
    eval_context.update(stocks)
    
    for f_name, compiled_code in compiled_flows.items():
        try: 
            rate = eval(compiled_code, {"__builtins__": None, "np": np}, eval_context)
            if np.isnan(rate) or np.isinf(rate):
                rate = 0.0
        except: 
            rate = 0.0
        flow_rates[f_name] = float(rate)
        
    derivatives = {s_name: 0.0 for s_name in stocks.keys()}
    for edge in edges:
        if edge["type"] == "inflow" and edge["to"] in derivatives:
            derivatives[edge["to"]] += flow_rates.get(edge["from"], 0.0)
        if edge["type"] == "outflow" and edge["from"] in derivatives:
            derivatives[edge["from"]] -= flow_rates.get(edge["to"], 0.0)
    return derivatives

# ==========================================
# แผงโหลดต้นแบบระบบจำลองด่วน (Sidebar)
# ==========================================
st.sidebar.markdown("### 🚀 โมเดลต้นแบบ")
if st.sidebar.button("📊 1. Logistic Growth Model", use_container_width=True):
    st.session_state.stocks = {"pop": 100.0}
    st.session_state.parameters = {"k1": 0.10, "cap": 150.0}
    st.session_state.flows = {"birth": {"formula": "k1 * pop * (1 - pop / cap)"}}
    st.session_state.edges = [
        {"from": "k1", "to": "birth", "type": "information"},
        {"from": "pop", "to": "birth", "type": "information"},
        {"from": "cap", "to": "birth", "type": "information"},
        {"from": "birth", "to": "pop", "type": "inflow"}
    ]
    reset_simulation_state()
    st.rerun()

if st.sidebar.button("✨ 2. Exponential Growth Model", use_container_width=True):
    st.session_state.stocks = {"pop": 100.0}
    st.session_state.parameters = {"k1": 0.10, "k2": 0.05}
    st.session_state.flows = {
        "birth": {"formula": "k1 * pop"},
        "dead": {"formula": "k2 * pop"}
    }
    st.session_state.edges = [
        {"from": "k1", "to": "birth", "type": "information"},
        {"from": "pop", "to": "birth", "type": "information"},
        {"from": "k2", "to": "dead", "type": "information"},
        {"from": "pop", "to": "dead", "type": "information"},
        {"from": "birth", "to": "pop", "type": "inflow"},
        {"from": "pop", "to": "dead", "type": "outflow"}
    ]
    reset_simulation_state()
    st.rerun()

if st.sidebar.button("🦠 3. SIR Epidemic Model", use_container_width=True):
    st.session_state.stocks = {"S": 990.0, "I": 10.0, "R": 0.0}
    st.session_state.parameters = {"beta": 0.30, "gamma": 0.10, "N": 1000.0}
    st.session_state.flows = {
        "infection": {"formula": "beta * S * I / N"},
        "recovery": {"formula": "gamma * I"}
    }
    st.session_state.edges = [
        {"from": "beta", "to": "infection", "type": "information"},
        {"from": "S", "to": "infection", "type": "information"},
        {"from": "I", "to": "infection", "type": "information"},
        {"from": "N", "to": "infection", "type": "information"},
        {"from": "gamma", "to": "recovery", "type": "information"},
        {"from": "I", "to": "recovery", "type": "information"},
        {"from": "S", "to": "infection", "type": "outflow"},
        {"from": "infection", "to": "I", "type": "inflow"},
        {"from": "I", "to": "recovery", "type": "outflow"},
        {"from": "recovery", "to": "R", "type": "inflow"}
    ]
    reset_simulation_state()
    st.rerun()

if st.sidebar.button("🦊 4. Lotka-Volterra Model", use_container_width=True):
    st.session_state.stocks = {"prey": 80.0, "predator": 30.0}
    st.session_state.parameters = {"alpha": 0.10, "beta": 0.005, "delta": 0.002, "gamma": 0.10}
    st.session_state.flows = {
        "prey_growth": {"formula": "alpha * prey"},
        "predation": {"formula": "beta * prey * predator"},
        "pred_growth": {"formula": "delta * prey * predator"},
        "pred_mortality": {"formula": "gamma * predator"}
    }
    st.session_state.edges = [
        {"from": "alpha", "to": "prey_growth", "type": "information"},
        {"from": "prey", "to": "prey_growth", "type": "information"},
        {"from": "beta", "to": "predation", "type": "information"},
        {"from": "prey", "to": "predation", "type": "information"},
        {"from": "predator", "to": "predation", "type": "information"},
        {"from": "delta", "to": "pred_growth", "type": "information"},
        {"from": "prey", "to": "pred_growth", "type": "information"},
        {"from": "predator", "to": "pred_growth", "type": "information"},
        {"from": "gamma", "to": "pred_mortality", "type": "information"},
        {"from": "predator", "to": "pred_mortality", "type": "information"},
        {"from": "prey_growth", "to": "prey", "type": "inflow"},
        {"from": "prey", "to": "predation", "type": "outflow"},
        {"from": "pred_growth", "to": "predator", "type": "inflow"},
        {"from": "predator", "to": "pred_mortality", "type": "outflow"}
    ]
    reset_simulation_state()
    st.rerun()

# เครื่องมือสร้างโมเดล (Sidebar Builders)
st.sidebar.header("🛠️ เครื่องมือสร้างโมเดล")
with st.sidebar.expander("🟢 A. สร้างวัตถุบนกระดาน", expanded=True):
    obj_type = st.radio("ประเภทวัตถุ:", ["📦 Stock (สะสม)", "⚪ Parameter (ค่าคงที่)", "💧 Flow (ท่อ/วาล์ว)"])
    all_current_names = list(st.session_state.stocks.keys()) + list(st.session_state.parameters.keys()) + list(st.session_state.flows.keys())
    
    if obj_type == "📦 Stock (สะสม)":
        s_name_input = st.text_input("ชื่อ (เช่น pop, stock)", key="input_add_stock_name").strip()
        s_val = st.number_input("ค่าเริ่มต้น", value=100.0, step=1.0, key="input_add_stock_val")
        if st.sidebar.button("วาง Stock", use_container_width=True) and s_name_input:
            s_name = sanitize_name(s_name_input)
            if s_name in all_current_names: st.sidebar.error(f"⚠️ '{s_name}' ถูกใช้แล้ว")
            elif s_name[0].isdigit(): st.sidebar.error("⚠️ ห้ามขึ้นต้นด้วยตัวเลข")
            elif s_name in RESERVED_NAMES or s_name in st.session_state.timeseries: st.sidebar.error(f"⚠️ '{s_name}' เป็นชื่อสงวน (ฟังก์ชัน/ข้อมูล Time Series)")
            else:
                st.session_state.stocks[s_name] = s_val
                reset_simulation_state()
                st.rerun()

    elif obj_type == "⚪ Parameter (ค่าคงที่)":
        p_name_input = st.text_input("ชื่อ (เช่น k1, cap)", key="input_add_param_name").strip()
        p_val = st.number_input("ค่าพารามิเตอร์", value=0.10, format="%.3f", key="input_add_param_val")
        if st.sidebar.button("วาง Parameter", use_container_width=True) and p_name_input:
            p_name = sanitize_name(p_name_input)
            if p_name in all_current_names: st.sidebar.error(f"⚠️ '{p_name}' ถูกใช้แล้ว")
            elif p_name[0].isdigit(): st.sidebar.error("⚠️ ห้ามขึ้นต้นด้วยตัวเลข")
            elif p_name in RESERVED_NAMES or p_name in st.session_state.timeseries: st.sidebar.error(f"⚠️ '{p_name}' เป็นชื่อสงวน (ฟังก์ชัน/ข้อมูล Time Series)")
            else:
                st.session_state.parameters[p_name] = p_val
                reset_simulation_state()
                st.rerun()

    elif obj_type == "💧 Flow (ท่อ/วาล์ว)":
        f_name_input = st.text_input("ชื่อ (เช่น birth, dead)", key="input_add_flow_name").strip()
        available_vars = list(st.session_state.parameters.keys()) + list(st.session_state.stocks.keys())
        ts_funcs = [f"{n}(t)" for n in st.session_state.timeseries.keys()]
        if available_vars:
            hint = "💡 ตัวแปรที่ใช้ได้: " + ", ".join([f"`{v}`" for v in available_vars]) + ", `t` (เวลา)"
            if ts_funcs:
                hint += " • ข้อมูลนำเข้า: " + ", ".join([f"`{f}`" for f in ts_funcs])
            hint += "  \n🧮 ฟังก์ชัน: `min()`, `max()`, `abs()`, `round()`, `mod()`, `if_then_else(cond, a, b)`, `sin/cos/tan/exp/log/sqrt`"
            st.caption(hint)
            f_form = st.text_input("สูตร (เช่น k1 * pop หรือ sin(t)*pop)", value="0.0", key="input_add_flow_form")
        else:
            f_form = "0.0"
            st.warning("⚠️ ไม่มีตัวแปรบนกระดาน (แต่สามารถใช้ `t` ได้)")
            
        if st.sidebar.button("วาง Flow", use_container_width=True) and f_name_input:
            f_name = sanitize_name(f_name_input)
            formula_ok, formula_err = validate_formula_syntax(f_form, extra_allowed_calls=st.session_state.timeseries.keys())
            if f_name in all_current_names: st.sidebar.error(f"⚠️ '{f_name}' ถูกใช้แล้ว")
            elif f_name[0].isdigit(): st.sidebar.error("⚠️ ห้ามขึ้นต้นด้วยตัวเลข")
            elif f_name in RESERVED_NAMES or f_name in st.session_state.timeseries: st.sidebar.error(f"⚠️ '{f_name}' เป็นชื่อสงวน (ฟังก์ชัน/ข้อมูล Time Series)")
            elif not formula_ok: st.sidebar.error(f"⚠️ {formula_err}")
            else:
                st.session_state.flows[f_name] = {"formula": f_form}
                reset_simulation_state()
                st.rerun()

with st.sidebar.expander("🟡 B. เชื่อมโยงความสัมพันธ์", expanded=False):
    all_elements = list(st.session_state.stocks.keys()) + list(st.session_state.parameters.keys()) + list(st.session_state.flows.keys())
    e_from = st.selectbox("ต้นทาง (From)", all_elements if all_elements else ["-"])
    e_to = st.selectbox("ปลายทาง (To)", all_elements if all_elements else ["-"])
    
    link_behavior = st.radio("เลือกประเภทเส้นเชื่อม:", [
        "🟢 ส่งข้อมูลเข้าสูตร (Information Link)",
        "🔹 ท่อไหลเข้ากล่องสะสม (Inflow) [เครื่องหมาย +]",
        "🔻 ท่อไหลออกจากกล่องสะสม (Outflow) [เครื่องหมาย -]"
    ])
    
    if st.sidebar.button("⚡ ลากเส้นเชื่อม", use_container_width=True):
        if e_from != "-" and e_to != "-" and e_from != e_to:
            edge_type = None
            
            if link_behavior == "🟢 ส่งข้อมูลเข้าสูตร (Information Link)":
                if (e_from in st.session_state.stocks or e_from in st.session_state.parameters) and e_to in st.session_state.flows:
                    edge_type = "information"
                else:
                    st.sidebar.error("⚠️ เส้นส่งข้อมูล (Information) ต้องลากจาก Stock หรือ Parameter ไปหากล่อง Flow เท่านั้น")
                    
            elif link_behavior == "🔹 ท่อไหลเข้ากล่องสะสม (Inflow) [เครื่องหมาย +]":
                if e_from in st.session_state.flows and e_to in st.session_state.stocks:
                    edge_type = "inflow"
                else:
                    st.sidebar.error("⚠️ ท่อไหลเข้า (Inflow) ต้องตั้งต้นจากกล่อง Flow วิ่งไปหากล่อง Stock เท่านั้นเพื่อบวกค่า (+)")
                    
            elif link_behavior == "🔻 ท่อไหลออกจากกล่องสะสม (Outflow) [เครื่องหมาย -]":
                if e_from in st.session_state.stocks and e_to in st.session_state.flows:
                    edge_type = "outflow"
                else:
                    st.sidebar.error("⚠️ ท่อไหลออก (Outflow) ต้องตั้งต้นจากกล่อง Stock วิ่งไปหากล่อง Flow เท่านั้นเพื่อลบค่า (-)")
            
            if edge_type:
                new_edge = {"from": e_from, "to": e_to, "type": edge_type}
                if new_edge not in st.session_state.edges:
                    st.session_state.edges.append(new_edge)
                    reset_simulation_state()
                    st.rerun()

with st.sidebar.expander("🔵 C. แก้ไขสูตร Flow", expanded=False):
    if st.session_state.flows:
        flow_to_edit = st.selectbox("เลือกวาล์วที่จะแก้:", list(st.session_state.flows.keys()))
        current_formula = st.session_state.flows[flow_to_edit]["formula"]
        updated_formula = st.text_input("พิมพ์สูตรใหม่:", value=current_formula, key=f"edit_f_{flow_to_edit}")
        if st.button("💾 บันทึก", use_container_width=True):
            formula_ok, formula_err = validate_formula_syntax(updated_formula, extra_allowed_calls=st.session_state.timeseries.keys())
            if not formula_ok:
                st.error(f"⚠️ {formula_err}")
            else:
                st.session_state.flows[flow_to_edit] = {"formula": updated_formula}
                reset_simulation_state()
                st.rerun()

with st.sidebar.expander("🔴 D. ลบวัตถุ / เส้นเชื่อม", expanded=False):
    delete_target_type = st.selectbox("เลือกสิ่งที่ต้องการลบ", ["วัตถุ", "เส้นเชื่อม"])
    if delete_target_type == "วัตถุ":
        all_objects = list(st.session_state.stocks.keys()) + list(st.session_state.parameters.keys()) + list(st.session_state.flows.keys())
        obj_to_delete = st.selectbox("เลือกวัตถุ:", all_objects if all_objects else ["-"])
        if st.button("❌ ลบวัตถุ", type="primary", use_container_width=True) and obj_to_delete != "-":
            for prefix in ["sandbox_p_", "sandbox_s_", "set_p_min_", "set_p_max_", "set_s_min_", "set_s_max_",
                           "quickedit_p_", "quickedit_s_", "_qsync_p_", "_qsync_s_"]:
                key_to_pop = f"{prefix}{obj_to_delete}"
                if key_to_pop in st.session_state: 
                    del st.session_state[key_to_pop]
                    
            if obj_to_delete in st.session_state.stocks: del st.session_state.stocks[obj_to_delete]
            elif obj_to_delete in st.session_state.parameters: del st.session_state.parameters[obj_to_delete]
            elif obj_to_delete in st.session_state.flows: del st.session_state.flows[obj_to_delete]
            st.session_state.edges = [e for e in st.session_state.edges if e["from"] != obj_to_delete and e["to"] != obj_to_delete]
            reset_simulation_state()
            st.rerun()
    else:
        edge_list_options = [f"{i}: [{e['from']}] -> [{e['to']}] ({e['type']})" for i, e in enumerate(st.session_state.edges)]
        selected_edge_str = st.selectbox("เลือกเส้นเชื่อม:", edge_list_options if edge_list_options else ["-"])
        if st.button("❌ ลบเส้น", type="primary", use_container_width=True) and selected_edge_str != "-":
            idx_to_remove = int(selected_edge_str.split(":")[0])
            if idx_to_remove < len(st.session_state.edges):
                st.session_state.edges.pop(idx_to_remove)
            reset_simulation_state()
            st.rerun()

if st.sidebar.button("🚨 ล้างกระดานใหม่ทั้งหมด", type="primary", use_container_width=True):
    st.session_state.clear()
    st.rerun()

# ====================================================
# ⚡ ใหม่: ส่วนจัดการไฟล์นำเข้า/ส่งออก (Save & Load Model)
# ====================================================
st.sidebar.markdown("---")
st.sidebar.header("💾 จัดการไฟล์โมเดล")

# ส่วนที่ 1: การดาวน์โหลด (Save Model)
model_data = {
    "stocks": st.session_state.stocks,
    "parameters": st.session_state.parameters,
    "flows": st.session_state.flows,
    "edges": st.session_state.edges,
    "timeseries": st.session_state.timeseries
}
json_string = json.dumps(model_data, indent=4)
st.sidebar.download_button(
    label="📥 ดาวน์โหลดโมเดล (Save JSON)",
    data=json_string,
    file_name="sd_model.json",
    mime="application/json",
    use_container_width=True,
    help="บันทึกโครงสร้างระบบทั้งหมดเก็บไว้ในเครื่องของคุณ"
)

# ส่วนที่ 2: การอัปโหลด (Load Model)
uploaded_file = st.sidebar.file_uploader("📤 อัปโหลดโมเดล (Load JSON)", type=["json"], help="นำไฟล์ .json ที่เคยบันทึกไว้กลับมาใช้งาน")
if uploaded_file is not None:
    if st.sidebar.button("✅ ยืนยันการโหลดโมเดล", use_container_width=True):
        try:
            loaded_data = json.load(uploaded_file)
            st.session_state.stocks = loaded_data.get("stocks", {})
            st.session_state.parameters = loaded_data.get("parameters", {})
            st.session_state.flows = loaded_data.get("flows", {})
            st.session_state.edges = loaded_data.get("edges", [])
            st.session_state.timeseries = loaded_data.get("timeseries", {})
            reset_simulation_state()
            st.sidebar.success("โหลดโมเดลสำเร็จ!")
            st.rerun()
        except Exception as e:
            st.sidebar.error(f"⚠️ เกิดข้อผิดพลาดในการอ่านไฟล์: {e}")

# ====================================================
# ⚡ ใหม่: นำเข้าข้อมูลจริงเป็น Time Series Input (CSV)
# ใช้สำหรับตัวแปรภายนอกระบบ (Exogenous input) เช่น Ia(t) ในโมเดล
# Glucose-Insulin ที่มีข้อมูลอินซูลินในเลือดจริงจากการวัด
# ====================================================
st.sidebar.markdown("---")
st.sidebar.header("📈 นำเข้าข้อมูล Time Series (CSV)")

with st.sidebar.expander("🟣 E. เพิ่มตัวแปรจากไฟล์ CSV", expanded=False):
    st.caption("ไฟล์ต้องมีอย่างน้อย 2 คอลัมน์: เวลา และค่าตัวเลขที่วัดได้ (เช่น เวลา, Insulin)")
    ts_csv_file = st.file_uploader("เลือกไฟล์ CSV", type=["csv"], key="ts_csv_uploader")

    if ts_csv_file is not None:
        try:
            df_ts_raw = pd.read_csv(ts_csv_file)
            cols = list(df_ts_raw.columns)
            ts_time_col = st.selectbox("คอลัมน์เวลา (time)", cols, index=0, key="ts_time_col")
            ts_val_col = st.selectbox("คอลัมน์ค่าตัวแปร (value)", cols, index=min(1, len(cols)-1), key="ts_val_col")
            ts_name_input = st.text_input("ตั้งชื่อตัวแปร (เช่น Ia)", value="Ia", key="ts_name_input").strip()
            ts_kind = st.radio(
                "วิธี Interpolation", ["linear", "cubic"], horizontal=True, key="ts_kind_radio",
                help="linear ปลอดภัยกว่าเมื่อข้อมูลมี noise, cubic ให้เส้นโค้ง smooth กว่าแต่เสี่ยง overshoot"
            )

            if st.button("✅ สร้าง Lookup Function", use_container_width=True) and ts_name_input:
                ts_name_clean = sanitize_name(ts_name_input)
                all_current_names_ts = (list(st.session_state.stocks.keys()) +
                                         list(st.session_state.parameters.keys()) +
                                         list(st.session_state.flows.keys()))
                if ts_name_clean in all_current_names_ts:
                    st.sidebar.error(f"⚠️ '{ts_name_clean}' ถูกใช้เป็นชื่อ Stock/Parameter/Flow แล้ว")
                elif ts_name_clean in RESERVED_NAMES:
                    st.sidebar.error(f"⚠️ '{ts_name_clean}' เป็นชื่อสงวน (ฟังก์ชันคณิตศาสตร์)")
                else:
                    t_vals = pd.to_numeric(df_ts_raw[ts_time_col], errors="coerce")
                    v_vals = pd.to_numeric(df_ts_raw[ts_val_col], errors="coerce")
                    valid_mask = t_vals.notna() & v_vals.notna()
                    t_clean = t_vals[valid_mask].tolist()
                    v_clean = v_vals[valid_mask].tolist()
                    # ⚡ เช็คจำนวนจุดข้อมูลก่อนบันทึก กัน error ตอนรันจริง (cubic spline ต้องการ
                    # อย่างน้อย 4 จุด ไม่งั้น scipy จะ raise error ตอนสร้าง interpolator ทีหลัง)
                    if len(t_clean) < 2:
                        st.sidebar.error("⚠️ ต้องมีข้อมูลอย่างน้อย 2 จุดที่เป็นตัวเลขถูกต้อง (ตรวจสอบว่าเลือกคอลัมน์ถูกต้องไหม)")
                    elif ts_kind == "cubic" and len(t_clean) < 4:
                        st.sidebar.error(f"⚠️ ข้อมูลมีแค่ {len(t_clean)} จุด แต่ cubic spline ต้องการอย่างน้อย 4 จุด — เลือก 'linear' แทน หรือเพิ่มข้อมูลให้ครบ")
                    else:
                        st.session_state.timeseries[ts_name_clean] = {
                            "time": t_clean,
                            "value": v_clean,
                            "kind": ts_kind
                        }
                        reset_simulation_state()
                        st.sidebar.success(f"เพิ่ม `{ts_name_clean}(t)` สำเร็จ! ใช้ในสูตร Flow ได้ทันที")
                        st.rerun()
        except Exception as e:
            st.sidebar.error(f"⚠️ อ่านไฟล์ไม่สำเร็จ: {e}")

    if st.session_state.timeseries:
        st.markdown("**ตัวแปร Time Series ที่ใช้งานอยู่:**")
        for ts_n, ts_d in st.session_state.timeseries.items():
            c_ts1, c_ts2 = st.columns([3, 1])
            c_ts1.markdown(
                f"<span class='sd-badge'>{ts_n}(t)</span> "
                f"<small>{len(ts_d['time'])} จุด • {ts_d['kind']}</small>",
                unsafe_allow_html=True
            )
            if c_ts2.button("🗑️ ลบ", key=f"del_ts_{ts_n}", type="primary"):
                del st.session_state.timeseries[ts_n]
                reset_simulation_state()
                st.rerun()

# ====================================================
# 3. ด่านตรวจตรรกะระบบ (System Integrity Check)
# ====================================================
checklist = []
logic_pass = True

if not st.session_state.stocks:
    checklist.append("🎯 **ขั้นตอน 1:** สร้างกล่อง **Stock** (เช่น ประชากร, ปริมาณ)")
    logic_pass = False
elif not st.session_state.flows:
    checklist.append("🎯 **ขั้นตอน 2:** สร้าง **Flow** เพื่อควบคุมอัตราการไหล")
    logic_pass = False
else:
    allowed_math_funcs = RESERVED_NAMES | {'np'} | set(st.session_state.timeseries.keys())
    for f_name, flow_data in st.session_state.flows.items():
        formula = flow_data["formula"]

        # ⚡ เช็คก่อนว่าสูตรคอมไพล์เป็น Python expression ได้จริงไหม และปลอดภัยไหม (กันทั้ง
        # ปัญหาแบบ "max(k1, ,k2)" ที่มี comma เกิน และกันสูตรที่จริงๆ เป็นโค้ดอันตราย)
        formula_ok, formula_err = validate_formula_syntax(formula, extra_allowed_calls=st.session_state.timeseries.keys())
        if not formula_ok:
            checklist.append(f"⚠️ **{formula_err}** ใน `{f_name}` — ตอนนี้ระบบจะคำนวณ Flow นี้เป็น 0.0 เสมอจนกว่าจะแก้")
            logic_pass = False
            continue  # ⚡ สูตรพังอยู่แล้ว ไม่ต้องเช็ค token ต่อ (ผลลัพธ์ regex จะสับสนโดยใช่เหตุ)

        tokens = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', formula)
        
        for token in tokens:
            if token not in st.session_state.stocks and token not in st.session_state.parameters and token not in allowed_math_funcs:
                checklist.append(f"⚠️ **สูตรผิดพลาด:** พบคำว่า `{token}` ใน `{f_name}` แต่ไม่มีวัตถุนี้อยู่")
                logic_pass = False
                
        valid_tokens = [t for t in tokens if t in st.session_state.stocks or t in st.session_state.parameters]
        connected_inputs = [e["from"] for e in st.session_state.edges if e["to"] == f_name and e["type"] == "information"]
        
        for token in valid_tokens:
            if token not in connected_inputs:
                checklist.append(f"⚠️ **เชื่อมข้อมูลไม่ครบ:** `{f_name}` ใช้ตัวแปร `{token}` แต่ยังไม่ได้ลากเส้นเชื่อมข้อมูลหากัน")
                logic_pass = False

        has_material_link = any(e["from"] == f_name and e["type"] == "inflow" for e in st.session_state.edges) or \
                             any(e["to"] == f_name and e["type"] == "outflow" for e in st.session_state.edges)
        if not has_material_link:
            checklist.append(f"🔍 **คำแนะนำ:** `{f_name}` ลอยอยู่ ลากเส้นไหลเข้า(Inflow) หรือไหลออก(Outflow) สู่ Stock ด้วย")
            logic_pass = False

st.subheader("🎯 สถานะโมเดล (System Status)")
if logic_pass:
    st.success("🟢 โครงสร้างสมบูรณ์! พร้อมประมวลผลด้วย RK4")
else:
    for item in checklist:
        if "ผิดพลาด" in item or "ไม่ครบ" in item: st.error(item)
        else: st.info(item)

st.markdown("---")

# ====================================================
# ⚡ ใหม่: พรีวิวข้อมูล Time Series ที่นำเข้า vs เส้น Interpolation
# ====================================================
if st.session_state.timeseries:
    with st.expander(f"📈 พรีวิวข้อมูล Time Series ที่นำเข้า ({len(st.session_state.timeseries)} ตัวแปร)", expanded=False):
        ts_lookups_preview = build_lookup_functions(st.session_state.timeseries)
        for ts_n, ts_d in st.session_state.timeseries.items():
            t_raw = np.array(ts_d["time"], dtype=float)
            v_raw = np.array(ts_d["value"], dtype=float)
            order = np.argsort(t_raw)
            t_raw, v_raw = t_raw[order], v_raw[order]
            t_fine = np.linspace(t_raw.min(), t_raw.max(), max(200, len(t_raw) * 8))
            v_fine = [ts_lookups_preview[ts_n](tt) for tt in t_fine]

            fig_ts = go.Figure()
            fig_ts.add_trace(go.Scatter(
                x=t_fine, y=v_fine, mode='lines', name=f"{ts_n}(t) — interpolated ({ts_d['kind']})",
                line=dict(width=2.5, color="#2563eb")
            ))
            fig_ts.add_trace(go.Scatter(
                x=t_raw, y=v_raw, mode='markers', name=f"{ts_n} — ข้อมูลดิบจาก CSV",
                marker=dict(size=8, color="#f97316", line=dict(width=1, color="white"))
            ))
            fig_ts.update_layout(
                title=f"ตัวแปรนำเข้า: {ts_n}(t)",
                xaxis_title="Time", yaxis_title="Value",
                height=280, margin=dict(l=20, r=20, t=40, b=20),
                font=dict(family="Tahoma"),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                plot_bgcolor="white",
                xaxis=dict(showgrid=True, gridwidth=1, gridcolor='#e2e8f0'),
                yaxis=dict(showgrid=True, gridwidth=1, gridcolor='#e2e8f0')
            )
            st.plotly_chart(fig_ts, use_container_width=True)
            st.caption(f"⚠️ นอกช่วง t = [{t_raw.min():.2f}, {t_raw.max():.2f}] ระบบจะ clamp ค่าให้คงที่เท่ากับจุดปลายสุด (extrapolation แบบ flat) — หากรันโมเดลนานกว่านี้ ผลลัพธ์ในช่วงนอกข้อมูลจริงจะไม่ reliable")

    st.markdown("---")

# ====================================================
# 4. Row 1: แผนภาพแนวคิด 
# ====================================================
st.subheader("🧩 1. โครงสร้างระบบ (Conceptual Diagram)")

if not st.session_state.stocks and not st.session_state.parameters and not st.session_state.flows:
    st.info("🔲 กระดานว่างเปล่า: เลือกโมเดลตัวอย่างด้านซ้ายเพื่อเริ่มต้น")
else:
    view_mode = st.checkbox("🔍 เปิดโหมดขยายขนาดกระดานกราฟิก (Enlarged Inspection Mode)", value=False, 
                            help="เปิดเมื่อต้องการส่องดูชื่อตัวแปรและสูตรยาวๆ ชัดๆ")

    # ⚡ จองตำแหน่งของ diagram ไว้ก่อน แล้วค่อยเติมเนื้อหาทีหลัง (หลังประมวลผล Quick Edit)
    # เพื่อให้ diagram แสดง "ค่าล่าสุด" ทันทีในรอบ rerun เดียวกัน ไม่ต้องรอกดปุ่มรันข้างล่าง
    diagram_slot = st.container()

    def _gv_esc(text):
        # ⚡ escape ให้ปลอดภัยสำหรับ Graphviz label (กัน diagram พังถ้าสูตรมี " หรือ \)
        return str(text).replace("\\", "\\\\").replace('"', '\\"')

    def _short(text, n=28):
        text = str(text)
        return text if len(text) <= n else text[:n-1] + "…"

    # ====================================================
    # ⚡ แก้ไขค่าได้ทันทีจากตรงนี้ (Quick Edit) — ประมวลผลก่อนสร้าง diagram
    # หมายเหตุ: ตัวไดอะแกรมเป็นภาพ SVG นิ่งจาก Graphviz คลิกที่ตัวรูปโดยตรงไม่ได้
    # (ต้องใช้ diagram library แบบโต้ตอบได้ เช่น React Flow ถึงจะทำได้จริง)
    # ช่องด้านล่างนี้คือทางลัดที่ทำได้ใน Streamlit ตอนนี้ — แก้ค่าปุ๊บ diagram ด้านบน
    # จะอัปเดตทันที ส่วนกราฟข้อ 2/3 จะถูกรีเซ็ตให้กด "รันผลจำลอง" ใหม่เพื่อความถูกต้อง
    # ====================================================
    if st.session_state.parameters or st.session_state.stocks:
        with st.expander("✏️ แก้ไขค่าด่วนจากโครงสร้างนี้ (Quick Edit)", expanded=False):
            st.caption("ปรับค่าตรงนี้ได้เลย ไม่ต้องเปิดเมนูด้านซ้าย — diagram ด้านบนอัปเดตทันที ส่วนกราฟข้อ 2/3 ต้องกดรันใหม่")

            if st.session_state.parameters:
                st.markdown("**⚪ Parameter**")
                qp_cols = st.columns(min(4, len(st.session_state.parameters)) or 1)
                for i, (p_name, p_val) in enumerate(st.session_state.parameters.items()):
                    qkey = f"quickedit_p_{p_name}"
                    synced_key = f"_qsync_p_{p_name}"
                    if st.session_state.get(synced_key) != p_val:
                        st.session_state[qkey] = float(p_val)
                        st.session_state[synced_key] = p_val
                    with qp_cols[i % len(qp_cols)]:
                        new_val = st.number_input(p_name, format="%.4f", key=qkey)
                    if new_val != p_val:
                        st.session_state.parameters[p_name] = new_val
                        st.session_state[synced_key] = new_val
                        reset_simulation_state()

            if st.session_state.stocks:
                st.markdown("**📦 Stock (ค่าเริ่มต้น)**")
                qs_cols = st.columns(min(4, len(st.session_state.stocks)) or 1)
                for i, (s_name, s_init) in enumerate(st.session_state.stocks.items()):
                    qkey = f"quickedit_s_{s_name}"
                    synced_key = f"_qsync_s_{s_name}"
                    if st.session_state.get(synced_key) != s_init:
                        st.session_state[qkey] = float(s_init)
                        st.session_state[synced_key] = s_init
                    with qs_cols[i % len(qs_cols)]:
                        new_s_val = st.number_input(s_name, format="%.4f", key=qkey)
                    if new_s_val != s_init:
                        st.session_state.stocks[s_name] = new_s_val
                        st.session_state[synced_key] = new_s_val
                        reset_simulation_state()

    # ⚡ ตอนนี้ st.session_state.parameters / stocks เป็นค่าล่าสุดแล้ว (รวมค่าที่เพิ่งแก้ใน Quick Edit)
    # ค่อยสร้างสตริง dot ของ diagram จากค่าล่าสุดนี้
    fs_main = 14 if view_mode else 11
    fs_sub  = 12 if view_mode else 9

    dot = (
        "digraph G {\n"
        "  rankdir=LR;\n"
        "  splines=true;\n"
        "  overlap=false;\n"
        "  bgcolor=\"transparent\";\n"
        f'  node [fontname="Tahoma", fontsize={fs_main}, margin="0.18,0.12"];\n'
        f'  edge [fontname="Tahoma", fontsize={fs_sub}];\n\n'
    )

    # 📦 Stock — กล่องมุมโค้ง โทนน้ำเงินเข้ม (ตัวสะสม)
    for s_name, s_init in st.session_state.stocks.items():
        dot += (f'  "{_gv_esc(s_name)}" [shape=box, style="rounded,filled", fillcolor="#2563eb", '
                f'color="#1e40af", penwidth=2.0, fontcolor="white", '
                f'label="📦 {_gv_esc(s_name)}\\nInit = {_gv_esc(s_init)}"];\n')

    # ⚪ Parameter (Converter) — วงรี โทนส้มอ่อน
    for p_name, p_val in st.session_state.parameters.items():
        dot += (f'  "{_gv_esc(p_name)}" [shape=ellipse, style=filled, fillcolor="#ffedd5", '
                f'color="#ea580c", penwidth=1.6, fontcolor="#7c2d12", '
                f'label="⚪ {_gv_esc(p_name)}\\n{_gv_esc(p_val)}"];\n')

    # 💧 Flow — ทรงกระบอก (คล้ายวาล์ว/ท่อ) โทนฟ้าอมเขียว
    for f_name, flow_data in st.session_state.flows.items():
        formula = _short(flow_data["formula"], 30)
        dot += (f'  "{_gv_esc(f_name)}" [shape=cylinder, style=filled, fillcolor="#cffafe", '
                f'color="#0891b2", penwidth=1.8, fontcolor="#164e63", '
                f'label="💧 {_gv_esc(f_name)}\\n{_gv_esc(formula)}"];\n')

    # 🟣 Time Series (CSV) — โน้ตรูปเอกสาร โทนม่วง แสดงว่าตัวแปรนี้มาจากข้อมูลจริง
    used_ts = set()
    for f_name, flow_data in st.session_state.flows.items():
        for ts_n in st.session_state.timeseries.keys():
            if re.search(rf'\b{re.escape(ts_n)}\b', flow_data["formula"]):
                used_ts.add(ts_n)
    for ts_n in used_ts:
        dot += (f'  "{_gv_esc(ts_n)}__ts" [shape=note, style=filled, fillcolor="#f3e8ff", '
                f'color="#9333ea", penwidth=1.6, fontcolor="#581c87", '
                f'label="📈 {_gv_esc(ts_n)}(t)\\nCSV data"];\n')

    dot += "\n"
    for edge in st.session_state.edges:
        n_from, n_to, e_type = _gv_esc(edge["from"]), _gv_esc(edge["to"]), edge["type"]
        if e_type == "information":
            dot += f'  "{n_from}" -> "{n_to}" [style=dashed, color="#16a34a", penwidth=1.4, arrowhead=vee];\n'
        elif e_type == "inflow":
            dot += (f'  "{n_from}" -> "{n_to}" [color="#2563eb", penwidth=3.0, arrowhead=normal, '
                     f'label=<<FONT POINT-SIZE="15"><B> + </B></FONT>>, fontcolor="#2563eb"];\n')
        elif e_type == "outflow":
            dot += (f'  "{n_from}" -> "{n_to}" [color="#dc2626", penwidth=3.0, arrowhead=normal, '
                     f'label=<<FONT POINT-SIZE="15"><B> − </B></FONT>>, fontcolor="#dc2626"];\n')

    for f_name, flow_data in st.session_state.flows.items():
        for ts_n in used_ts:
            if re.search(rf'\b{re.escape(ts_n)}\b', flow_data["formula"]):
                dot += f'  "{_gv_esc(ts_n)}__ts" -> "{_gv_esc(f_name)}" [style=dotted, color="#9333ea", penwidth=1.6, arrowhead=vee];\n'

    dot += "}"

    with diagram_slot:
        st.graphviz_chart(dot, use_container_width=False)
        legend_cols = st.columns(5)
        legend_cols[0].markdown("📦 <span style='color:#2563eb'>**Stock**</span>", unsafe_allow_html=True)
        legend_cols[1].markdown("⚪ <span style='color:#ea580c'>**Parameter**</span>", unsafe_allow_html=True)
        legend_cols[2].markdown("💧 <span style='color:#0891b2'>**Flow**</span>", unsafe_allow_html=True)
        legend_cols[3].markdown("📈 <span style='color:#9333ea'>**CSV Input**</span>", unsafe_allow_html=True)
        legend_cols[4].markdown("┄┄ <span style='color:#16a34a'>**Info Link**</span>", unsafe_allow_html=True)
        if view_mode:
            st.caption("💡 เคล็ดลับ: คุณสามารถแก้ไข เพิ่มวัตถุ หรือจัดการสูตรที่แถบเมนูด้านซ้ายได้ตลอดเวลา")

st.markdown("---")

# ====================================================
# 5. Row 2: กราฟหลัก (Fit-Size Baseline Graph)
# ====================================================
st.subheader("📈 2. กราฟหลัก (Baseline)")

col_time1, col_time2, col_time3 = st.columns([1, 2, 1])
with col_time1:
    max_time_limit = st.number_input("⚙️ เวลาจำลองสูงสุด (Max Limit)", min_value=10, value=300, step=10)
with col_time2:
    sim_time_horizon = st.slider("⏱️ ระยะเวลาจำลอง ", min_value=10, max_value=int(max_time_limit), value=min(100, int(max_time_limit)), step=10)
with col_time3:
    dt = st.number_input("🔬 ขนาดสเต็ปเวลา (dt)", min_value=0.01, max_value=2.0, value=0.25, step=0.05, format="%.2f", 
                         help="ค่าน้อย=แม่นยำแต่คำนวณนาน, ค่ามาก=ประมวลผลเร็วแต่อาจไม่เสถียร")

steps = int(sim_time_horizon / dt)
color_palette = px.colors.qualitative.Plotly

if logic_pass:
    if st.button("🚀 รันผลจำลอง (Run Simulation)", type="primary", use_container_width=True):
        st.session_state.sim_calculated = True
        
        current_stocks = {name: val for name, val in st.session_state.stocks.items()}
        history = {name: [val] for name, val in current_stocks.items()}
        time_axis = [0.0]
        numerical_error_flag = False
        
        compiled_flows = {}
        for f_name, flow_data in st.session_state.flows.items():
            try:
                formula_str = flow_data["formula"].replace('^', '**')
                compiled_flows[f_name] = compile(formula_str, '<string>', 'eval')
            except SyntaxError:
                compiled_flows[f_name] = compile("0.0", '<string>', 'eval')
        
        base_context = build_base_context(st.session_state.parameters, st.session_state.timeseries)
        
        for step in range(steps):
            current_t = step * dt 
            
            k1 = compute_derivatives(current_t, current_stocks, compiled_flows, st.session_state.edges, base_context)
            stocks_k2 = {s: current_stocks[s] + 0.5 * dt * k1[s] for s in current_stocks}
            k2 = compute_derivatives(current_t + 0.5 * dt, stocks_k2, compiled_flows, st.session_state.edges, base_context)
            stocks_k3 = {s: current_stocks[s] + 0.5 * dt * k2[s] for s in current_stocks}
            k3 = compute_derivatives(current_t + 0.5 * dt, stocks_k3, compiled_flows, st.session_state.edges, base_context)
            stocks_k4 = {s: current_stocks[s] + dt * k3[s] for s in current_stocks}
            k4 = compute_derivatives(current_t + dt, stocks_k4, compiled_flows, st.session_state.edges, base_context)
            
            for s in current_stocks.keys():
                next_val = current_stocks[s] + (dt / 6.0) * (k1[s] + 2.0 * k2[s] + 2.0 * k3[s] + k4[s])
                if np.isnan(next_val) or np.isinf(next_val) or abs(next_val) > 1e12:
                    numerical_error_flag = True
                    break
                current_stocks[s] = next_val
                history[s].append(next_val)
                
            if numerical_error_flag:
                st.error("🚨 ตรวจพบปัญหาการคำนวณเชิงตัวเลข (Numerical Overflow/NaN) ในระบบหลัก กรุณาปรับค่าตัวแปรให้เหมาะสม")
                st.session_state.sim_calculated = False
                break
                
            time_axis.append(current_t + dt)
            
        if not numerical_error_flag:
            st.session_state.baseline_results = {"time": time_axis, "history": history}
        
    if st.session_state.sim_calculated and st.session_state.baseline_results:
        _, plot_col, _ = st.columns([1, 8, 1])
        with plot_col:
            all_stock_names = list(st.session_state.baseline_results["history"].keys())
            time_vals = st.session_state.baseline_results["time"]

            ctrl_c1, ctrl_c2 = st.columns([2, 1])
            with ctrl_c1:
                selected_stocks = st.multiselect(
                    "🧮 เลือกตัวแปรที่จะแสดงบนกราฟ", options=all_stock_names,
                    default=all_stock_names, key="baseline_plot_select"
                )
            with ctrl_c2:
                scale_mode = st.radio(
                    "มุมมองสเกล", ["ค่าจริง", "Normalize 0-1", "แกน Y คู่"],
                    horizontal=True, key="baseline_scale_mode",
                    help="ใช้เมื่อตัวแปรมี scale ต่างกันมาก เช่น G (~100) กับ X (~0.001) — ถ้าโชว์ด้วยแกนเดียวกัน เส้นที่ค่าน้อยจะแบนราบมองไม่เห็นเลย"
                )

            if not selected_stocks:
                st.warning("⚠️ กรุณาเลือกอย่างน้อย 1 ตัวแปรเพื่อแสดงผล")
            else:
                if scale_mode == "แกน Y คู่" and len(selected_stocks) != 2:
                    st.info("💡 โหมด 'แกน Y คู่' ใช้ได้เมื่อเลือกตัวแปรพอดี 2 ตัวเท่านั้น — แสดงแบบ 'ค่าจริง' แทนไปก่อน")
                    scale_mode = "ค่าจริง"

                fig = go.Figure()
                for i, s_name in enumerate(selected_stocks):
                    y_values = st.session_state.baseline_results["history"][s_name]
                    c = color_palette[i % len(color_palette)]
                    trace_kwargs = {}
                    if scale_mode == "Normalize 0-1":
                        y_arr = np.array(y_values, dtype=float)
                        y_min, y_max = float(y_arr.min()), float(y_arr.max())
                        y_plot = (y_arr - y_min) / (y_max - y_min) if y_max > y_min else np.full_like(y_arr, 0.5)
                    elif scale_mode == "แกน Y คู่":
                        y_plot = y_values
                        if i == 1:
                            trace_kwargs = {"yaxis": "y2"}
                    else:
                        y_plot = y_values
                    fig.add_trace(go.Scatter(
                        x=time_vals, y=y_plot, mode='lines', name=s_name,
                        line=dict(width=2.5, color=c), **trace_kwargs
                    ))

                layout_kwargs = dict(
                    xaxis_title="Time",
                    margin=dict(l=20, r=20, t=30, b=20),
                    height=350,
                    font=dict(family="Tahoma"),
                    plot_bgcolor="white",
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    xaxis=dict(showgrid=True, gridwidth=1, gridcolor='#e2e8f0', griddash='dash'),
                )
                if scale_mode == "แกน Y คู่":
                    layout_kwargs["yaxis"] = dict(
                        title=selected_stocks[0], showgrid=True, gridwidth=1,
                        gridcolor='#e2e8f0', griddash='dash', color=color_palette[0]
                    )
                    layout_kwargs["yaxis2"] = dict(
                        title=selected_stocks[1], overlaying='y', side='right',
                        showgrid=False, color=color_palette[1 % len(color_palette)]
                    )
                else:
                    layout_kwargs["yaxis_title"] = "Value (Normalized 0-1)" if scale_mode == "Normalize 0-1" else "Value"
                    layout_kwargs["yaxis"] = dict(showgrid=True, gridwidth=1, gridcolor='#e2e8f0', griddash='dash')
                fig.update_layout(**layout_kwargs)
                st.plotly_chart(fig, use_container_width=True)

            result_df = pd.DataFrame({"time": time_vals})
            for s_name in all_stock_names:
                result_df[s_name] = st.session_state.baseline_results["history"][s_name]
            st.download_button(
                "📥 ดาวน์โหลดผลลัพธ์ (CSV)",
                data=result_df.to_csv(index=False),
                file_name="simulation_results.csv",
                mime="text/csv",
                use_container_width=True
            )
else:
    st.warning("🔒 กราฟถูกล็อก: กรุณาแก้ไขตรรกะตัวแปรและสูตรให้เสร็จสิ้นก่อน")

# ====================================================
# 6. Row 3: แผงควบคุม Sandbox
# ====================================================
if st.session_state.sim_calculated and st.session_state.baseline_results:
    st.markdown("---")
    st.subheader("📊 3. แผงวิเคราะห์ & ปรับจูนตัวแปร")
    
    with st.expander("⚙️ กำหนดขอบเขต Min/Max ของสไลเดอร์", expanded=False):
        cp1, cp2 = st.columns(2)
        for i, (p_name, p_val) in enumerate(st.session_state.parameters.items()):
            if f"p_min_{p_name}" not in st.session_state.bounds: st.session_state.bounds[f"p_min_{p_name}"] = 0.0
            if f"p_max_{p_name}" not in st.session_state.bounds: st.session_state.bounds[f"p_max_{p_name}"] = max(1.0, float(p_val) * 2.0)
            target_col = cp1 if i % 2 == 0 else cp2
            with target_col:
                sub_c1, sub_c2 = st.columns(2)
                val_min = sub_c1.number_input(f"📉 Min `{p_name}`", value=float(st.session_state.bounds[f"p_min_{p_name}"]), format="%.4f", key=f"set_p_min_{p_name}")
                val_max = sub_c2.number_input(f"📈 Max `{p_name}`", value=float(st.session_state.bounds[f"p_max_{p_name}"]), format="%.4f", key=f"set_p_max_{p_name}")
                if val_min < val_max:
                    st.session_state.bounds[f"p_min_{p_name}"] = val_min
                    st.session_state.bounds[f"p_max_{p_name}"] = val_max
                
        cs1, cs2 = st.columns(2)
        for i, (s_name, s_init) in enumerate(st.session_state.stocks.items()):
            if f"s_min_{s_name}" not in st.session_state.bounds: st.session_state.bounds[f"s_min_{s_name}"] = 0.0
            if f"s_max_{s_name}" not in st.session_state.bounds: st.session_state.bounds[f"s_max_{s_name}"] = max(100.0, float(s_init) * 2.0)
            target_col = cs1 if i % 2 == 0 else cs2
            with target_col:
                sub_c1, sub_c2 = st.columns(2)
                val_s_min = sub_c1.number_input(f"📉 Min `{s_name}`", value=float(st.session_state.bounds[f"s_min_{s_name}"]), format="%.2f", key=f"set_s_min_{s_name}")
                val_s_max = sub_c2.number_input(f"📈 Max `{s_name}`", value=float(st.session_state.bounds[f"s_max_{s_name}"]), format="%.2f", key=f"set_s_max_{s_name}")
                if val_s_min < val_s_max:
                    st.session_state.bounds[f"s_min_{s_name}"] = val_s_min
                    st.session_state.bounds[f"s_max_{s_name}"] = val_s_max

    col_sliders, col_tune_graph = st.columns([2, 3])
    tuned_parameters = {}
    tuned_initial_stocks = {}
    
    with col_sliders:
        st.markdown("##### ⚪ ปรับค่าคงที่ (Parameters)")
        for p_name, p_val in st.session_state.parameters.items():
            p_min = float(st.session_state.bounds.get(f"p_min_{p_name}", 0.0))
            p_max = float(st.session_state.bounds.get(f"p_max_{p_name}", 1.0))
            if p_min >= p_max: p_max = p_min + 1.0 
            
            val_key = f"sandbox_p_{p_name}"
            if val_key not in st.session_state:
                st.session_state[val_key] = float(np.clip(float(p_val), p_min, p_max))
            else:
                st.session_state[val_key] = float(np.clip(st.session_state[val_key], p_min, p_max))
                
            step_size = 0.0001 if (p_max - p_min) <= 1.0 else (0.01 if (p_max - p_min) <= 10.0 else 1.0)
            
            tuned_parameters[p_name] = st.slider(
                f"`{p_name}`", 
                min_value=p_min, 
                max_value=p_max, 
                step=step_size, 
                format="%.4f", 
                key=val_key
            )
            
        st.markdown("##### 📦 ปรับค่าเริ่มต้น (Initial Stocks)")
        for s_name, s_init in st.session_state.stocks.items():
            s_min = float(st.session_state.bounds.get(f"s_min_{s_name}", 0.0))
            s_max = float(st.session_state.bounds.get(f"s_max_{s_name}", 100.0))
            if s_min >= s_max: s_max = s_min + 10.0
            
            val_key = f"sandbox_s_{s_name}"
            if val_key not in st.session_state:
                st.session_state[val_key] = float(np.clip(float(s_init), s_min, s_max))
            else:
                st.session_state[val_key] = float(np.clip(st.session_state[val_key], s_min, s_max))
                
            tuned_initial_stocks[s_name] = st.slider(f"`{s_name}`", min_value=s_min, max_value=s_max, step=1.0, key=val_key)
            
        st.markdown("##### 🎨 รูปแบบกราฟ")
        display_design = st.radio("เลือกมุมมอง:", ["🔹 ซ้อนทับ Baseline (Overlay)", "🟢 ซ่อน Baseline (Simulate Only)"])

        st.markdown("##### 🧮 ตัวเลือกการแสดงผล")
        tuning_all_stocks = list(st.session_state.stocks.keys())
        tuning_selected_stocks = st.multiselect(
            "เลือกตัวแปรที่จะแสดง", options=tuning_all_stocks,
            default=tuning_all_stocks, key="tuning_plot_select"
        )
        tuning_scale_mode = st.radio(
            "มุมมองสเกล", ["ค่าจริง", "Normalize 0-1", "แกน Y คู่"], horizontal=True, key="tuning_scale_mode",
            help="เลือก Normalize เมื่อตัวแปรมี scale ต่างกันมาก เช่น G (~100) กับ X (~0.001) จะได้เห็นรูปทรงการเปลี่ยนแปลงของทั้งคู่ชัดเจน หรือใช้ 'แกน Y คู่' เพื่อดูค่าจริงของทั้ง 2 ตัวพร้อมกัน (ต้องเลือกตัวแปรพอดี 2 ตัว)"
        )
            
    with col_tune_graph:
        sandbox_stocks = {name: val for name, val in tuned_initial_stocks.items()}
        sandbox_history = {name: [val] for name, val in sandbox_stocks.items()}
        sandbox_time = [0.0]
        sandbox_overflow = False
        
        compiled_flows_s = {}
        for f_name, flow_data in st.session_state.flows.items():
            try:
                formula_str = flow_data["formula"].replace('^', '**')
                compiled_flows_s[f_name] = compile(formula_str, '<string>', 'eval')
            except SyntaxError:
                compiled_flows_s[f_name] = compile("0.0", '<string>', 'eval')
                
        base_context_s = build_base_context(tuned_parameters, st.session_state.timeseries)
        
        for step in range(steps):
            current_t = step * dt 
            
            k1_s = compute_derivatives(current_t, sandbox_stocks, compiled_flows_s, st.session_state.edges, base_context_s)
            stocks_k2_s = {s: sandbox_stocks[s] + 0.5 * dt * k1_s[s] for s in sandbox_stocks}
            k2_s = compute_derivatives(current_t + 0.5 * dt, stocks_k2_s, compiled_flows_s, st.session_state.edges, base_context_s)
            stocks_k3_s = {s: sandbox_stocks[s] + 0.5 * dt * k2_s[s] for s in sandbox_stocks}
            k3_s = compute_derivatives(current_t + 0.5 * dt, stocks_k3_s, compiled_flows_s, st.session_state.edges, base_context_s)
            stocks_k4_s = {s: sandbox_stocks[s] + dt * k3_s[s] for s in sandbox_stocks}
            k4_s = compute_derivatives(current_t + dt, stocks_k4_s, compiled_flows_s, st.session_state.edges, base_context_s)
            
            for s in sandbox_stocks.keys():
                next_val_s = sandbox_stocks[s] + (dt / 6.0) * (k1_s[s] + 2.0 * k2_s[s] + 2.0 * k3_s[s] + k4_s[s])
                if np.isnan(next_val_s) or np.isinf(next_val_s) or abs(next_val_s) > 1e12:
                    sandbox_overflow = True
                    break
                sandbox_stocks[s] = next_val_s
                sandbox_history[s].append(next_val_s)
                
            if sandbox_overflow:
                break
            sandbox_time.append(current_t + dt)
            
        fig2 = go.Figure()
        plot_stocks = tuning_selected_stocks if tuning_selected_stocks else list(st.session_state.stocks.keys())
        effective_scale_mode = tuning_scale_mode

        if sandbox_overflow:
            fig2.add_annotation(
                text="Numerical Explosion Detected!<br>Adjust sliders to stable values.",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(color="red", size=16),
                align="center"
            )
        else:
            if effective_scale_mode == "แกน Y คู่" and len(plot_stocks) != 2:
                st.info("💡 โหมด 'แกน Y คู่' ใช้ได้เมื่อเลือกตัวแปรพอดี 2 ตัวเท่านั้น — แสดงแบบ 'ค่าจริง' แทนไปก่อน")
                effective_scale_mode = "ค่าจริง"

            for i, s_name in enumerate(plot_stocks):
                c = color_palette[i % len(color_palette)]
                trace_kwargs = {"yaxis": "y2"} if (effective_scale_mode == "แกน Y คู่" and i == 1) else {}

                tune_y_raw = sandbox_history[s_name]
                base_y_raw = None
                if display_design == "🔹 ซ้อนทับ Baseline (Overlay)" and st.session_state.baseline_results:
                    candidate = st.session_state.baseline_results["history"].get(s_name, [])
                    if len(candidate) == len(st.session_state.baseline_results["time"]):
                        base_y_raw = candidate

                if effective_scale_mode == "Normalize 0-1":
                    combined = list(tune_y_raw) + (list(base_y_raw) if base_y_raw is not None else [])
                    arr = np.array(combined, dtype=float)
                    y_min, y_max = float(arr.min()), float(arr.max())

                    def _norm(vals, _min=y_min, _max=y_max):
                        a = np.array(vals, dtype=float)
                        return (a - _min) / (_max - _min) if _max > _min else np.full_like(a, 0.5)

                    tune_y = _norm(tune_y_raw)
                    base_y = _norm(base_y_raw) if base_y_raw is not None else None
                else:
                    tune_y = tune_y_raw
                    base_y = base_y_raw

                if base_y is not None:
                    fig2.add_trace(go.Scatter(
                        x=st.session_state.baseline_results["time"], 
                        y=base_y, 
                        mode='lines', 
                        name=f"{s_name} (Base)",
                        line=dict(width=1.5, color=c, dash='dash'),
                        opacity=0.5,
                        **trace_kwargs
                    ))

                fig2.add_trace(go.Scatter(
                    x=sandbox_time, 
                    y=tune_y, 
                    mode='lines', 
                    name=f"{s_name} (Tuned)",
                    line=dict(width=2.5, color=c),
                    **trace_kwargs
                ))

        fig2_layout_kwargs = dict(
            xaxis_title="Time",
            margin=dict(l=20, r=20, t=30, b=20),
            height=400,
            font=dict(family="Tahoma"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            plot_bgcolor="white",
            xaxis=dict(showgrid=True, gridwidth=1, gridcolor='#e2e8f0', griddash='dot'),
        )
        if not sandbox_overflow and effective_scale_mode == "แกน Y คู่":
            fig2_layout_kwargs["yaxis"] = dict(
                title=plot_stocks[0], showgrid=True, gridwidth=1,
                gridcolor='#e2e8f0', griddash='dot', color=color_palette[0]
            )
            fig2_layout_kwargs["yaxis2"] = dict(
                title=plot_stocks[1], overlaying='y', side='right',
                showgrid=False, color=color_palette[1 % len(color_palette)]
            )
        else:
            fig2_layout_kwargs["yaxis_title"] = "Value (Normalized 0-1)" if effective_scale_mode == "Normalize 0-1" else "Value"
            fig2_layout_kwargs["yaxis"] = dict(showgrid=True, gridwidth=1, gridcolor='#e2e8f0', griddash='dot')
        fig2.update_layout(**fig2_layout_kwargs)
        st.plotly_chart(fig2, use_container_width=True)