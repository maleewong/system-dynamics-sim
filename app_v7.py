import streamlit as st
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import re
import json # ⚡ เพิ่ม import json สำหรับจัดการไฟล์

# ==========================================
# 1. การตั้งค่าหน้ากระดานปฏิบัติการ (Fit Layout)
# ==========================================
st.set_page_config(page_title="System Dynamics Simulator", layout="wide")

st.title("🌊 System Dynamics Simulator")
st.caption("ระบบจำลองสถานการณ์: ออกแบบโครงสร้างและปรับแต่งตัวแปรแบบเรียลไทม์")

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

def reset_simulation_state():
    st.session_state.sim_calculated = False
    st.session_state.baseline_results = None
    st.session_state.bounds = {} 

def sanitize_name(name):
    return re.sub(r'\W', '_', name.strip())

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
            else:
                st.session_state.parameters[p_name] = p_val
                reset_simulation_state()
                st.rerun()
            
    elif obj_type == "💧 Flow (ท่อ/วาล์ว)":
        f_name_input = st.text_input("ชื่อ (เช่น birth, dead)", key="input_add_flow_name").strip()
        available_vars = list(st.session_state.parameters.keys()) + list(st.session_state.stocks.keys())
        if available_vars:
            st.caption("💡 ตัวแปรที่ใช้ได้: " + ", ".join([f"`{v}`" for v in available_vars]) + ", `t` (เวลา)")
            f_form = st.text_input("สูตร (เช่น k1 * pop หรือ sin(t)*pop)", value="0.0", key="input_add_flow_form")
        else:
            f_form = "0.0"
            st.warning("⚠️ ไม่มีตัวแปรบนกระดาน (แต่สามารถใช้ `t` ได้)")
            
        if st.sidebar.button("วาง Flow", use_container_width=True) and f_name_input:
            f_name = sanitize_name(f_name_input)
            if f_name in all_current_names: st.sidebar.error(f"⚠️ '{f_name}' ถูกใช้แล้ว")
            elif f_name[0].isdigit(): st.sidebar.error("⚠️ ห้ามขึ้นต้นด้วยตัวเลข")
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
            st.session_state.flows[flow_to_edit] = {"formula": updated_formula}
            reset_simulation_state() 
            st.rerun()

with st.sidebar.expander("🔴 D. ลบวัตถุ / เส้นเชื่อม", expanded=False):
    delete_target_type = st.selectbox("เลือกสิ่งที่ต้องการลบ", ["วัตถุ", "เส้นเชื่อม"])
    if delete_target_type == "วัตถุ":
        all_objects = list(st.session_state.stocks.keys()) + list(st.session_state.parameters.keys()) + list(st.session_state.flows.keys())
        obj_to_delete = st.selectbox("เลือกวัตถุ:", all_objects if all_objects else ["-"])
        if st.button("❌ ลบวัตถุ", type="primary", use_container_width=True) and obj_to_delete != "-":
            for prefix in ["sandbox_p_", "sandbox_s_", "set_p_min_", "set_p_max_", "set_s_min_", "set_s_max_"]:
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

if st.sidebar.button("🚨 ล้างกระดานใหม่ทั้งหมด", type="secondary", use_container_width=True):
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
    "edges": st.session_state.edges
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
            reset_simulation_state()
            st.sidebar.success("โหลดโมเดลสำเร็จ!")
            st.rerun()
        except Exception as e:
            st.sidebar.error(f"⚠️ เกิดข้อผิดพลาดในการอ่านไฟล์: {e}")

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
    allowed_math_funcs = {'np', 'sin', 'cos', 'tan', 'exp', 'log', 'sqrt', 't'}
    for f_name, flow_data in st.session_state.flows.items():
        formula = flow_data["formula"]
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
# 4. Row 1: แผนภาพแนวคิด 
# ====================================================
st.subheader("🧩 1. โครงสร้างระบบ (Conceptual Diagram)")

if not st.session_state.stocks and not st.session_state.parameters and not st.session_state.flows:
    st.info("🔲 กระดานว่างเปล่า: เลือกโมเดลตัวอย่างด้านซ้ายเพื่อเริ่มต้น")
else:
    view_mode = st.checkbox("🔍 เปิดโหมดขยายขนาดกระดานกราฟิก (Enlarged Inspection Mode)", value=False, 
                            help="เปิดเมื่อต้องการส่องดูชื่อตัวแปรและสูตรยาวๆ ชัดๆ")
    
    if view_mode:
        dot = "digraph G {\n  rankdir=LR;\n  splines=true;\n  overlap=false;\n  node [fontname=\"Tahoma\", fontsize=13, margin=\"0.2,0.15\"];\n\n"
    else:
        dot = "digraph G {\n  rankdir=LR;\n  splines=true;\n  overlap=false;\n  node [fontname=\"Tahoma\", fontsize=10, margin=\"0.12,0.08\"];\n\n"
        
    for s_name, s_init in st.session_state.stocks.items():
        dot += f'  "{s_name}" [shape=box, style=filled, fillcolor="#9ecae1", penwidth=2.0, label="{s_name}\\n[Init: {s_init}]"];\n'
    for p_name, p_val in st.session_state.parameters.items():
        dot += f'  "{p_name}" [shape=circle, style=filled, fillcolor="#fff7bc", label="{p_name}\\n({p_val})"];\n'
    for f_name, flow_data in st.session_state.flows.items():
        formula = flow_data["formula"]
        dot += f'  "{f_name}" [shape=diamond, style=filled, fillcolor="#fde0dd", penwidth=1.5, label="💧 {f_name}\\n[{formula}]"];\n'
    
    dot += "\n"
    for edge in st.session_state.edges:
        n_from, n_to, e_type = edge["from"], edge["to"], edge["type"]
        if e_type == "information":
            dot += f'  "{n_from}" -> "{n_to}" [style=dashed, color="#22c55e", penwidth=1.5, arrowhead=vee];\n'
        elif e_type == "inflow":
            dot += f'  "{n_from}" -> "{n_to}" [color="#3182bd", penwidth=3.0, label=" + "];\n'
        elif e_type == "outflow":
            dot += f'  "{n_from}" -> "{n_to}" [color="#de2d26", penwidth=3.0, label=" - "];\n'
    dot += "}"
    
    if view_mode:
        st.graphviz_chart(dot, use_container_width=False)
        st.caption("💡 เคล็ดลับ: คุณสามารถแก้ไข เพิ่มวัตถุ หรือจัดการสูตรที่แถบเมนูด้านซ้ายได้ตลอดเวลา")
    else:
        st.graphviz_chart(dot, use_container_width=False)

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
        
        base_context = {
            "sin": np.sin, "cos": np.cos, "tan": np.tan,
            "exp": np.exp, "log": np.log, "sqrt": np.sqrt
        }
        base_context.update(st.session_state.parameters)
        
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
            fig = go.Figure()
            for i, (s_name, y_values) in enumerate(st.session_state.baseline_results["history"].items()):
                c = color_palette[i % len(color_palette)]
                fig.add_trace(go.Scatter(
                    x=st.session_state.baseline_results["time"], 
                    y=y_values, 
                    mode='lines', 
                    name=s_name,
                    line=dict(width=2.5, color=c)
                ))
                
            fig.update_layout(
                xaxis_title="Time",
                yaxis_title="Value",
                margin=dict(l=20, r=20, t=30, b=20),
                height=350,
                font=dict(family="Tahoma"),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                xaxis=dict(showgrid=True, gridwidth=1, gridcolor='LightGray', griddash='dash'),
                yaxis=dict(showgrid=True, gridwidth=1, gridcolor='LightGray', griddash='dash')
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("💡 กดปุ่มสีแดง 'รันผลจำลอง' เพื่อดูผลลัพธ์โครงสร้างหลัก")
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
                
        base_context_s = {
            "sin": np.sin, "cos": np.cos, "tan": np.tan,
            "exp": np.exp, "log": np.log, "sqrt": np.sqrt
        }
        base_context_s.update(tuned_parameters)
        
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
        
        if sandbox_overflow:
            fig2.add_annotation(
                text="Numerical Explosion Detected!<br>Adjust sliders to stable values.",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(color="red", size=16),
                align="center"
            )
        else:
            for i, s_name in enumerate(st.session_state.stocks.keys()):
                c = color_palette[i % len(color_palette)]
                
                if display_design == "🔹 ซ้อนทับ Baseline (Overlay)" and st.session_state.baseline_results:
                    base_y = st.session_state.baseline_results["history"].get(s_name, [])
                    if len(base_y) == len(st.session_state.baseline_results["time"]):
                        fig2.add_trace(go.Scatter(
                            x=st.session_state.baseline_results["time"], 
                            y=base_y, 
                            mode='lines', 
                            name=f"{s_name} (Base)",
                            line=dict(width=1.5, color=c, dash='dash'),
                            opacity=0.5
                        ))
                
                tune_y = sandbox_history[s_name]
                fig2.add_trace(go.Scatter(
                    x=sandbox_time, 
                    y=tune_y, 
                    mode='lines', 
                    name=f"{s_name} (Tuned)",
                    line=dict(width=2.5, color=c)
                ))
            
        fig2.update_layout(
            xaxis_title="Time",
            yaxis_title="Value",
            margin=dict(l=20, r=20, t=30, b=20),
            height=400,
            font=dict(family="Tahoma"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            xaxis=dict(showgrid=True, gridwidth=1, gridcolor='LightGray', griddash='dot'),
            yaxis=dict(showgrid=True, gridwidth=1, gridcolor='LightGray', griddash='dot')
        )
        st.plotly_chart(fig2, use_container_width=True)