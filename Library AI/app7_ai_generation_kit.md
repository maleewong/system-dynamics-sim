# App v7 — ชุดเอกสารสำหรับให้ AI สร้างโมเดล (ฉบับรวม)

> **แปะไฟล์นี้ทั้งหมดให้ AI ตัวไหนก็ได้ตอนเริ่มแชทใหม่ แล้วบอกปัญหาที่ต้องการจำลอง**
> ไฟล์นี้รวม 2 ส่วนที่ต้องใช้คู่กันเสมอไว้ในที่เดียว — แปะไฟล์เดียวจบ ไม่ต้องจำว่าต้องมี 2 ไฟล์แยกกันอีกต่อไป

| ส่วน | ตอบคำถามว่า | ถ้าขาดจะเกิดอะไร |
|---|---|---|
| **ส่วนที่ 1 — Schema Spec** | "จะแพ็กเป็น JSON ที่แอปอ่านได้ยังไง" (ไวยากรณ์, edges, ความปลอดภัย, checklist, format ไฟล์) | สูตรถูกฟิสิกส์ แต่ไฟล์ใช้ไม่ได้ (เช่น ลืม info edge, syntax ผิด) |
| **ส่วนที่ 2 — Governing Equations Library** | "ควรใช้สูตรไหนกับปัญหาแบบไหน" (~90 กฎอ้างอิงข้ามสาขา) | ไฟล์ใช้ได้ แต่เลือกกฎผิด/ไม่รู้ว่ามีตัวเลือกอะไรบ้าง |

**ต้องมีทั้งสองส่วนพร้อมกันเสมอ ถึงจะได้ JSON ที่ทั้ง "ใช้งานได้จริง" และ "อิงกฎที่ถูกต้อง" ครบทั้งคู่**

---

# System Dynamics Model JSON — Spec สำหรับให้ AI สร้างโมเดล

> **วิธีใช้:** แปะไฟล์นี้ทั้งหมดให้ AI (Claude, GPT, Gemini ฯลฯ) ตอนเริ่มแชทใหม่ แล้วบอกปัญหาที่ต้องการจำลอง
> AI จะได้ context ครบพอที่จะสร้าง JSON ที่โหลดเข้า `sys-sim.streamlit.app` (v7) หรือ Calibrator (v8) ได้ถูกต้องตั้งแต่ครั้งแรก
> ไม่ต้องรู้จักแอปนี้มาก่อนก็ใช้ได้

---

## 1. โครงสร้าง JSON ทั้งหมด (5 keys บังคับ)

```json
{
  "stocks": { "ชื่อ_stock": ค่าเริ่มต้น_ตัวเลข, ... },
  "parameters": { "ชื่อ_parameter": ค่าคงที่_ตัวเลข, ... },
  "flows": { "ชื่อ_flow": { "formula": "สูตร_ข้อความ" }, ... },
  "edges": [ { "from": "...", "to": "...", "type": "..." }, ... ],
  "timeseries": {}
}
```

- **`stocks`** — ตัวแปรสะสม (สิ่งที่ระบบ "แก้สมการเชิงอนุพันธ์" หา) เช่น ประชากร, น้ำหนัก, ความเข้มข้น ค่าคือค่าเริ่มต้น ณ t=0
- **`parameters`** — ค่าคงที่ (ไม่เปลี่ยนตามเวลา) เช่น อัตราเกิด, ค่าคงที่อัตราปฏิกิริยา
- **`flows`** — อัตราการไหลเข้า/ออกของ stock แต่ละตัว **สูตรต้องเป็น expression บรรทัดเดียว** (ดูกฎสูตรข้อ 3)
- **`edges`** — เส้นเชื่อมทั้งหมด **ต้องมีทั้ง material edge และ information edge แยกกัน** (ข้อ 2 สำคัญมาก อ่านให้ครบ)
- **`timeseries`** — ปกติปล่อยเป็น `{}` (ตัวแปรที่มาจาก CSV จริงจะโหลดแยกในแอป ไม่ต้องฝังในไฟล์นี้)

---

## 2. กฎเรื่อง Edges — จุดที่ผิดบ่อยที่สุด

ทุก flow ต้องมี edge **2 ประเภทแยกกัน** สำหรับตัวแปรเดียวกันได้:

### 2.1 Material edge (การไหลจริงเข้า/ออก stock)
```json
{"from": "stock_ต้นทาง", "to": "ชื่อ_flow", "type": "outflow"}
{"from": "ชื่อ_flow", "to": "stock_ปลายทาง", "type": "inflow"}
```

### 2.2 Information edge (บอกว่า flow นี้ "อ้างอิงค่า" จากตัวแปรไหนบ้าง)
```json
{"from": "ชื่อตัวแปร_ที่ใช้ในสูตร", "to": "ชื่อ_flow", "type": "information"}
```

**⚠️ กฎเหล็ก: ทุก stock และ parameter ที่ปรากฏในสูตรของ flow ใดๆ ต้องมี information edge ชี้เข้า flow นั้นเสมอ — แม้ว่าจะมี material edge อยู่แล้วก็ตาม (material edge ไม่นับเป็น information edge)**

ตัวอย่างที่ถูกต้อง — `birth = k1 * pop * (1 - pop/cap)`:
```json
"edges": [
  {"from": "k1",  "to": "birth", "type": "information"},
  {"from": "pop", "to": "birth", "type": "information"},
  {"from": "cap", "to": "birth", "type": "information"},
  {"from": "birth", "to": "pop", "type": "inflow"}
]
```
สังเกตว่า `pop` มี edge ทั้ง `information` (เพราะใช้ในสูตร) **และ** `inflow` (เพราะเป็นปลายทางที่ birth ไหลเข้า) — ต้องมีครบทั้งคู่ ไม่ใช่อย่างใดอย่างหนึ่ง

**เช็คลิสต์ก่อนส่งมอบ JSON:** ไล่ทุก flow → แตก token ในสูตร (ตัดฟังก์ชัน built-in ออก) → เทียบว่าแต่ละ token มี information edge ชี้เข้า flow นั้นครบทุกตัวหรือยัง

---

## 3. กฎเรื่องสูตร (`formula`)

### 3.1 ฟังก์ชันที่ใช้ได้ (มีแค่นี้ ห้ามใช้นอกเหนือจากนี้)
```
sin, cos, tan, exp, log, log10, sqrt
min, max, abs, round, mod(a,b)
if_then_else(condition, ค่าถ้าจริง, ค่าถ้าเท็จ)
```
ตัวดำเนินการ: `+ - * / ** (หรือ ^ ก็ได้ ระบบแปลงให้)`

### 3.2 ตัวแปรที่ใช้ในสูตรได้
- ชื่อ stock ทุกตัว, ชื่อ parameter ทุกตัว
- `t` (เวลาปัจจุบัน — ใช้ได้เสมอโดยไม่ต้องประกาศ)
- ชื่อ time-series ที่โหลดแยกไว้ในแอป เรียกแบบ **`ชื่อ(t)`** เช่น `Ia(t)`, `T_obs(t)` (ดูข้อ 4)

### 3.3 ข้อห้ามเด็ดขาด (ระบบมี security filter บล็อกอัตโนมัติ)
- **ห้ามใช้ `.` (attribute access) เด็ดขาด** เช่น `x.something`, `().__class__` — ระบบมี AST whitelist บล็อกไว้ ถ้าใช้จะโดนปฏิเสธทันที (ไม่ใช่บั๊ก เป็นการป้องกันความปลอดภัยโดยตั้งใจ)
- ห้ามเรียกฟังก์ชันที่ไม่อยู่ในลิสต์ข้อ 3.1 (เช่น `getattr`, `eval`, `open`, `__import__`)
- ห้ามมี comma เกิน/วงเล็บไม่ครบ — ระบบเช็ค syntax ก่อนบันทึกเสมอ

### 3.4 ตัวอย่างสูตรที่ถูกต้อง
```
k1 * pop * (1 - pop / cap)
beta * S * I / N
min(max_outflow, k_outflow * level)
if_then_else(T_obs(t) < Topt, exp(-4.6*((Topt-T_obs(t))/(Topt-Tmin))**4), exp(-4.6*((T_obs(t)-Topt)/(Tmax-Topt))**4))
```

---

## 4. Time-Series (CSV) — เมื่อมีตัวแปรที่มาจากข้อมูลจริงตามเวลา ไม่ใช่ค่าคงที่

ถ้าสูตรต้องอ้างอิงข้อมูลจริงที่เปลี่ยนตามเวลา (เช่น อุณหภูมิที่วัดจริงแต่ละวัน, ปริมาณอินซูลินในเลือด) — **อย่าใส่เป็น parameter** เพราะ parameter เป็นค่าคงที่เท่านั้น ให้ทำแบบนี้แทน:

1. ในสูตรให้เรียกเป็นฟังก์ชันของเวลา: `T_obs(t)` (ห้ามลืมวงเล็บ `(t)`)
2. **ห้ามใส่ตัวแปรนี้ใน `parameters`** และ **ห้ามสร้าง information edge ให้ตัวแปรนี้** — ระบบจะจับคู่ชื่อฟังก์ชันกับ CSV ที่ผู้ใช้อัปโหลดแยกต่างหากในแอปเองอัตโนมัติ ไม่ต้องประกาศอะไรใน edges เลย
3. บอกผู้ใช้แยกต่างหาก (นอก JSON) ว่าต้องเตรียมไฟล์ CSV คอลัมน์ไหนบ้าง ชื่อตัวแปรอะไร เพื่อไปอัปโหลดเองในแอป

---

## 5. กฎการตั้งชื่อ

- ใช้ตัวอักษรอังกฤษ + underscore เท่านั้น (`Pop_Stock`, `k_decay`) — ห้ามมีช่องว่าง/อักขระพิเศษ
- ห้ามตั้งชื่อซ้ำกับฟังก์ชัน built-in ในข้อ 3.1 หรือคำว่า `t`
- ชื่อ stock/parameter/flow ทุกตัวต้องไม่ซ้ำกันเอง (namespace เดียวกันทั้งหมด)

---

## 6. ทุกครั้งที่สร้าง JSON ควรแนบมาด้วย (ไม่บังคับทางเทคนิค แต่ควรทำเพื่อความรัดกุม)

เพิ่มฟิลด์เสริมต่อท้ายแต่ละ flow ได้ (แอปจะไม่อ่าน ไม่กระทบการรัน แต่มีประโยชน์กับมนุษย์):
```json
"flows": {
  "birth": {
    "formula": "k1 * pop * (1 - pop / cap)",
    "basis": "Logistic Growth Model (Verhulst 1838)",
    "source": "ชื่องาน/เปเปอร์ต้นทาง ถ้ามี",
    "assumptions": ["สิ่งที่ประมาณเอง/ไม่มีข้อมูลจริงรองรับ ต้องระบุให้ชัด"]
  }
}
```

---

## 7. ตัวอย่างไฟล์สมบูรณ์ (Logistic Growth — ใช้เป็นแม่แบบ)

```json
{
    "stocks": { "pop": 100.0 },
    "parameters": { "k1": 0.1, "cap": 150.0 },
    "flows": {
        "birth": {
            "formula": "k1 * pop * (1 - pop / cap)",
            "basis": "Logistic Growth Model (Verhulst 1838)",
            "source": null,
            "assumptions": []
        }
    },
    "edges": [
        {"from": "k1",  "to": "birth", "type": "information"},
        {"from": "pop", "to": "birth", "type": "information"},
        {"from": "cap", "to": "birth", "type": "information"},
        {"from": "birth", "to": "pop", "type": "inflow"}
    ],
    "timeseries": {}
}
```

---

## 8. เช็คลิสต์สุดท้ายก่อนส่งมอบ JSON ให้ผู้ใช้

- [ ] ทุก flow formula ใช้เฉพาะฟังก์ชันในข้อ 3.1
- [ ] ไม่มี `.` (attribute access) ในสูตรไหนเลย
- [ ] ทุก stock/parameter ที่ปรากฏในสูตร มี information edge ชี้เข้า flow นั้นครบ
- [ ] ทุก flow ที่ไหลเข้า/ออก stock มี material edge (`inflow`/`outflow`) ครบ
- [ ] ตัวแปรที่เป็น time-series เรียกแบบ `ชื่อ(t)` และไม่ถูกใส่ใน parameters/edges
- [ ] ชื่อทั้งหมดเป็นอังกฤษ+underscore ไม่ซ้ำกัน ไม่ชนกับ built-in function
- [ ] (แนะนำ) ทุก flow มี `basis`/`source`/`assumptions` กำกับไว้

---

## 9. ก่อนส่ง JSON ให้ผู้ใช้ — ต้องทำ 2 อย่างนี้เสมอ (บังคับ ไม่ใช่ทางเลือก)

### 9.1 แสดงผลการไล่เช็คลิสต์ข้อ 8 ออกมาให้เห็นจริง ไม่ใช่แค่บอกว่า "เช็คแล้ว"

**ห้ามพูดลอยๆ ว่า "ตรวจสอบครบถ้วนแล้ว"** เพราะนั่นเป็นแค่คำอ้าง ไม่ใช่หลักฐาน — ให้ไล่ทีละ flow ทีละ token จริงๆ แล้วแสดงผลออกมา เช่น:

```
เช็ค flow "cooling":
  - token ที่พบในสูตร: k_cool, temp, T_room
  - k_cool → เป็น parameter, มี information edge แล้ว ✅
  - temp   → เป็น stock,     มี information edge แล้ว ✅
  - T_room → เป็น parameter, มี information edge แล้ว ✅
  - ฟังก์ชันที่ใช้: ไม่มี (มีแต่ +, -, *) ✅
  - material edge: temp -[outflow]-> cooling ✅
สรุป: ผ่านครบทุกข้อ
```

ถ้าไล่เช็คแล้วพบว่าข้อไหนไม่ผ่าน **ต้องแก้ JSON ให้ถูกก่อน แล้วไล่เช็คซ้ำใหม่ทั้งหมด** ไม่ใช่แก้เฉพาะจุดที่พังแล้วส่งเลยโดยไม่เช็คซ้ำ

### 9.2 สร้างเป็นไฟล์ `.json` ให้ดาวน์โหลดจริง ไม่ใช่แค่แปะโค้ดในแชท

ผู้ใช้ต้องเอาไฟล์นี้ไปอัปโหลดเข้าแอป (`sys-sim.streamlit.app` หรือ Calibrator) โดยตรง — การแปะ JSON เป็นข้อความในแชทให้ผู้ใช้ copy เองมีโอกาสพลาด (copy ไม่ครบ, เผลอติดตัวอักษรอื่นปน) ให้สร้างเป็นไฟล์แล้วส่งเป็นไฟล์แนบดาวน์โหลดเสมอ

**ข้อควรระวังเรื่องรูปแบบไฟล์:**
- ต้องเป็น **raw JSON เท่านั้น** ห้ามมี ` ```json ` fence, ห้ามมีคอมเมนต์ (`//` หรือ `#`) ปนอยู่ในไฟล์ เพราะ JSON มาตรฐานไม่รองรับคอมเมนต์ — ถ้าฟิลด์ `source` เป็น `null` ให้ใช้ `null` ตรงๆ (ไม่ใช่ string `"null"`)
- ตั้งชื่อไฟล์ให้สื่อความหมาย เช่น `logistic_growth_model.json` ไม่ใช่ `model.json` เฉยๆ
- ก่อนส่งไฟล์ ให้ลองแปลงเป็น JSON object ด้วยตัวเอง (parse ในใจ/ในโค้ดถ้าทำได้) เพื่อยืนยันว่าไฟล์ไม่ syntax error เช่น วงเล็บปีกกาไม่ครบ, comma เกิน/ขาด — ความผิดพลาดแบบนี้ทำให้ผู้ใช้เปิดไฟล์ไม่ได้เลยทั้งไฟล์

-e 

---


# ห้องสมุดกฎควบคุม (Governing Equations Library)

> **สถานะ:** รอบนี้เป็น "seed" ขนาดใหญ่ ยังไม่ผ่านการตรวจสอบเป็นรายข้อ (ดูคำเตือนด้านล่าง)
> **รูปแบบไฟล์:** Markdown (อ่านง่ายสำหรับคนและ AI) — ถ้าต้องการเวอร์ชัน JSON สำหรับให้โปรแกรมอ่านโดยตรง บอกได้ แปลงจากไฟล์นี้ได้ทันทีเพราะโครงสร้างสม่ำเสมอ

## ⚠️ คำเตือนสำคัญ — อ่านก่อนใช้

กฎส่วนใหญ่ในไฟล์นี้มาจากความรู้ทั่วไปที่ผมมี (ไม่ใช่ผลจากการพิสูจน์ทีละข้อ) — เทียบเท่ากับ "จำจากตำรามาเรียง" ไม่ใช่ "ตรวจสอบมาแล้ว" ทุกข้อมีฟิลด์ **`validation_status`** บอกระดับความน่าเชื่อถือไว้ตรงๆ:

| สถานะ | ความหมาย |
|---|---|
| `textbook_standard_unverified_locally` | สูตรมาตรฐานที่รู้จักกันทั่วไป แต่**ยังไม่ได้ตรวจมิติ/รันจริงในระบบนี้** — ใช้เป็นจุดเริ่มต้น ต้องพ่วง verification engine ก่อนเชื่อ |
| `validated_stress_tested` | ทดสอบรันจริงผ่าน RK4 engine ของเราแล้วในบทสนทนานี้ (ไม่ overflow, พฤติกรรมสมเหตุสมผล) แต่ไม่ได้เทียบกับข้อมูลจริง |
| `validated_against_real_data` | ทดสอบกับข้อมูลวัดจริงแล้ว มีตัวเลขความคลาดเคลื่อนกำกับ |

**อย่าเชื่อ `formula_template` ทุกข้อเท่ากันหมด** — ข้อที่เป็น `textbook_standard_unverified_locally` ต้องผ่าน dimensional check ก่อนใช้งานจริงเสมอ

---

## หมวด A: ฟิสิกส์ (Physics)

| ชื่อ | สูตร (Flow) | หน่วยที่ต้องมี | validation_status |
|---|---|---|---|
| 1D Advection | `v_velocity * c_drag * Stock` | v:m/s, c_drag:1/m, Stock:kg, Flow:kg/s | textbook_standard_unverified_locally |
| First-Order Decay | `k_decay * Stock` | k:1/s, Stock:kg, Flow:kg/s | textbook_standard_unverified_locally |
| Newton's Law of Cooling | `h * Area * (Temp_Stock - Temp_Ambient)` | h:W/(m²·K), Area:m², Temp:K, Flow:W | validated_stress_tested (ทดสอบ coffee-cooling แล้ว) |
| Fick's Diffusion (simplified) | `D_coeff * Area * (C_in - C_out) / dx` | D:m²/s, Area:m², C:kg/m³, dx:m, Flow:kg/s | textbook_standard_unverified_locally |
| Torricelli's Law (tank drain) | `Cd * Orifice_Area * sqrt(2*g*height)` | Cd:dimensionless, Area:m², g:m/s², height:m, Flow:m³/s | textbook_standard_unverified_locally |
| Stefan-Boltzmann Radiation | `emiss * sigma * Area * (T^4 - T_amb^4)` | sigma:W/(m²·K⁴), Area:m², T:K, Flow:W | textbook_standard_unverified_locally |
| Frictional Dissipation | `friction_factor * normal_force * velocity` | dimensionless, N, m/s, Flow:W | textbook_standard_unverified_locally |
| Surface Evaporation | `mass_transfer_coeff * Area * (P_sat - P_amb)` | s/m, m², Pa, Flow:kg/s | textbook_standard_unverified_locally |
| Viscous Damping | `damping_coeff * velocity_Stock` | N·s/m, m/s, Flow:N | textbook_standard_unverified_locally |
| Particle Sedimentation (Stokes) | `settling_velocity * Area * Conc_Stock` | m/s, m², kg/m³, Flow:kg/s | textbook_standard_unverified_locally |
| Simple Harmonic Restoring Force | `-k_spring * displacement_Stock` | N/m, m, Flow:N | textbook_standard_unverified_locally |
| RC Circuit Discharge | `Voltage_Stock / (R * C)` | V, Ω, F, Flow:V/s | textbook_standard_unverified_locally |
| RL Circuit Current Decay | `-(R/L) * Current_Stock` | Ω, H, A, Flow:A/s | textbook_standard_unverified_locally |
| Radioactive Decay | `-lambda_decay * N_atoms_Stock` | 1/s, atoms, Flow:atoms/s | textbook_standard_unverified_locally |
| Beer-Lambert Light Attenuation | `-mu_absorption * Intensity_Stock` | 1/m (ต่อความลึก), W/m², Flow:W/m²/m | textbook_standard_unverified_locally |
| Fourier Heat Conduction | `k_thermal * Area * (T_hot - T_cold) / thickness` | W/(m·K), m², K, m, Flow:W | textbook_standard_unverified_locally |
| Gas Leak from Pressurized Tank | `Cd * Orifice_Area * sqrt(2*R_gas*T*(P_Stock-P_amb)/M_molar)` | ซับซ้อน ต้องเช็คหน่วยละเอียด | textbook_standard_unverified_locally |
| Terminal Velocity w/ Drag | `g - (drag_coeff/mass) * velocity_Stock^2` | m/s², 1/(kg·m), m/s, Flow:m/s² | textbook_standard_unverified_locally |

---

## หมวด B: ชีววิทยา/นิเวศวิทยา (Biology/Ecology)

| ชื่อ | สูตร (Flow) | หน่วยที่ต้องมี | validation_status |
|---|---|---|---|
| Logistic Growth | `r * Pop_Stock * (1 - Pop_Stock/K_capacity)` | 1/day, individual, individual, Flow:individual/day | validated_stress_tested |
| Exponential Growth | `birth_rate * Pop_Stock` | 1/day, individual, Flow:individual/day | validated_stress_tested |
| Gompertz Growth (tumor/organism) | `r_growth * Size_Stock * log(K_max/Size_Stock)` | 1/day, g, g, Flow:g/day | textbook_standard_unverified_locally |
| Von Bertalanffy Growth (fish/animal length) | `growth_coeff * (L_infinity - Length_Stock)` | 1/day, cm, cm, Flow:cm/day | textbook_standard_unverified_locally |
| SIR — Transmission | `beta * S_Stock * I_Stock / N_total` | 1/day, individual, individual, Flow:individual/day | validated_stress_tested |
| SIR — Recovery | `gamma * I_Stock` | 1/day, individual, Flow:individual/day | validated_stress_tested |
| SEIR — Incubation (E→I) | `sigma_rate * E_Stock` | 1/day, individual, Flow:individual/day | validated_stress_tested |
| SIS — Waning Immunity (R→S) | `omega_rate * R_Stock` | 1/day, individual, Flow:individual/day | textbook_standard_unverified_locally |
| SIRD — Disease Mortality | `mu_disease * I_Stock` | 1/day, individual, Flow:individual/day | textbook_standard_unverified_locally |
| Lotka-Volterra Predation | `capture_eff * Prey_Stock * Predator_Stock` | 1/(individual·day), individual, individual, Flow | validated_stress_tested |
| Lotka-Volterra Predator Death | `mortality_rate * Predator_Stock` | 1/day, individual, Flow | validated_stress_tested |
| Holling Type II Functional Response | `(a_attack * Prey_Stock) / (1 + a_attack*h_handling*Prey_Stock) * Predator_Stock` | ซับซ้อน ต้องเช็คหน่วยแยก | textbook_standard_unverified_locally |
| Competitive Lotka-Volterra (2 species) | `r1 * N1_Stock * (1 - (N1_Stock + alpha12*N2_Stock)/K1)` | 1/day, individual, dimensionless, individual | textbook_standard_unverified_locally |
| Allee Effect Growth | `r * Pop_Stock * (Pop_Stock/A_threshold - 1) * (1 - Pop_Stock/K)` | 1/day, individual, individual, individual | textbook_standard_unverified_locally |
| Michaelis-Menten Kinetics | `(V_max * Substrate_Stock) / (K_m + Substrate_Stock)` | mol/(m³·s), mol/m³, mol/m³ | textbook_standard_unverified_locally |
| Biomass Respiration | `respiration_rate * Biomass_Stock` | 1/day, kg, Flow:kg/day | textbook_standard_unverified_locally |
| Density-Dependent Migration | `mig_coeff * max(0, Pop_Stock - Density_Threshold)` | 1/day, individual, individual | textbook_standard_unverified_locally |
| Genetic Mutation Flow | `mutation_prob * reproduction_rate * Pop_Stock` | dimensionless, 1/day, individual | textbook_standard_unverified_locally |
| Bioaccumulation (toxin uptake) | `uptake_rate * C_water - elimination_rate * Toxin_Stock` | ซับซ้อน 2 เทอม แยกเป็น 2 flow | textbook_standard_unverified_locally |
| Allometric Metabolic Scaling | `metabolic_coeff * Mass_Stock^0.75` | ต้องเช็คหน่วยตาม exponent | textbook_standard_unverified_locally |
| Monod Growth (nutrient-limited) | `mu_max * (Nutrient_Stock/(Ks+Nutrient_Stock)) * Biomass_Stock` | 1/day, mg/L, mg/L, kg | textbook_standard_unverified_locally |
| Age-Structured Survivorship Decay | `mortality_rate(age) * Cohort_Stock` | ต้องใช้ time-series ถ้า mortality แปรตามอายุจริง | textbook_standard_unverified_locally |
| **Bioenergetic Growth (Ursin/Bolte)** | `(1-a)*b*env_factors*h*W^m - k*W^n` | รายละเอียดตามเปเปอร์ Dampin et al. 2012 | **validated_against_real_data** (คลาดเคลื่อน 0.10% เทียบข้อมูลจริง Nile Tilapia n=37 จุด) |

---

## หมวด C: เคมี (Chemistry)

| ชื่อ | สูตร (Flow) | หน่วยที่ต้องมี | validation_status |
|---|---|---|---|
| Zero-Order Reaction | `k_rate_constant` | mol/(m³·s) | textbook_standard_unverified_locally |
| First-Order Reaction | `k_rate * Reactant_Stock` | 1/s, mol/m³, Flow | validated_stress_tested |
| Second-Order Reaction (A+B) | `k_rate * A_Stock * B_Stock` | m³/(mol·s), mol/m³, mol/m³ | textbook_standard_unverified_locally |
| Arrhenius Temperature-Dependent Rate | `A_factor * exp(-E_act/(R_gas*Temp_K)) * Reactant_Stock` | 1/s, J/mol, J/(mol·K), K | textbook_standard_unverified_locally |
| Reversible Reaction (Forward/Backward) | `k_fwd * Reactant_Stock` / `k_bwd * Product_Stock` | 1/s ทั้งคู่ | validated_stress_tested (A⇌B⇌C ทดสอบแล้ว) |
| Henry's Law Gas Dissolution | `mtc * (H_const * P_partial - Dissolved_Gas_Stock)` | 1/s, mol/(m³·Pa), Pa, mol/m³ | textbook_standard_unverified_locally |
| Acid-Base Neutralization | `k_neutralize * Acid_Stock * Base_Stock` | m³/(mol·s), mol/m³, mol/m³ | textbook_standard_unverified_locally |
| Photochemical Degradation | `quantum_yield * Light_Intensity * Chemical_Stock` | m²/W, W/m², kg | textbook_standard_unverified_locally |
| Catalytic Surface Conversion | `k_catalyst * Surface_Area * Reactant_Stock` | m/s, m², mol/m³ | textbook_standard_unverified_locally |
| Enzyme Competitive Inhibition | `(V_max*Substrate_Stock)/(K_m*(1+Inhibitor_Stock/K_i)+Substrate_Stock)` | ซับซ้อน แยกเช็คทีละเทอม | textbook_standard_unverified_locally |
| Autocatalytic Reaction | `k_auto * Reactant_Stock * Product_Stock` | m³/(mol·s), mol/m³, mol/m³ | textbook_standard_unverified_locally |
| Radioactive Decay Chain (parent→daughter) | `lambda_parent * Parent_Stock` (inflow to daughter) | 1/s, atoms | textbook_standard_unverified_locally |
| Langmuir Adsorption | `k_ads * C_solution * (Site_max - Occupied_Stock) - k_des * Occupied_Stock` | ต้องแยกเป็น 2 flow | textbook_standard_unverified_locally |
| pH Buffer Titration Rate | `k_titrate * (Acid_added_rate - Base_capacity_remaining)` | ต้องนิยามหน่วยเฉพาะเคส | textbook_standard_unverified_locally |

---

## หมวด D: การเงิน/เศรษฐศาสตร์ (Finance/Economics)

| ชื่อ | สูตร (Flow) | หน่วยที่ต้องมี | validation_status |
|---|---|---|---|
| Continuous Compound Interest | `interest_rate * Principal_Stock` | 1/year, USD | textbook_standard_unverified_locally |
| Continuous Discounting | `-discount_rate * Value_Stock` | 1/year, USD | textbook_standard_unverified_locally |
| Straight-Line Depreciation | `(Initial_Value - Salvage_Value) / Useful_Life` | USD, USD, year | textbook_standard_unverified_locally |
| Exponential Depreciation | `depreciation_rate * Asset_Value_Stock` | 1/year, USD | textbook_standard_unverified_locally |
| Elastic Demand Response | `Base_Demand * (Current_Price/Base_Price)^elasticity` | unit/month, USD/unit, USD/unit, dimensionless | textbook_standard_unverified_locally |
| Capital-Driven Production | `capital_productivity * Capital_Stock` | unit/(USD·month), USD | textbook_standard_unverified_locally |
| Inflation Erosion | `inflation_rate * Purchasing_Power_Stock` | 1/year, USD | textbook_standard_unverified_locally |
| Loan Amortization | `Fixed_Payment - (interest_rate * Debt_Stock)` | USD/month, 1/month, USD | textbook_standard_unverified_locally |
| Capital Accumulation (reinvestment) | `reinvestment_fraction * Net_Profit` | dimensionless, USD/year | textbook_standard_unverified_locally |
| Dividend Payout | `payout_ratio * Retained_Earnings_Stock` | 1/year, USD | textbook_standard_unverified_locally |
| **Solow Growth Model** (capital, Cobb-Douglas) | investment: `s_savings * A_tfp * K_Stock^alpha`, depreciation: `delta_dep * K_Stock` | dimensionless, dimensionless, USD, dimensionless / 1/year, USD | validated_stress_tested (ลู่เข้า steady-state ตรงทฤษฎีเป๊ะ) |
| **Bass Diffusion Model** (product adoption) | `(p_innov + q_imit*N_Stock/M_market) * (M_market - N_Stock)` | 1/day, 1/day, adopters, adopters | validated_stress_tested |
| Inventory-Backlog Control | `min(capacity, demand_rate + backlog/adj_time)` | unit/day, unit/day, unit, day | validated_stress_tested |
| Bond Price Convergence to Par | `-k_convergence * (Price_Stock - Par_Value)` | 1/year, USD, USD | textbook_standard_unverified_locally |
| Money Multiplier / Bank Reserves | `-required_reserve_ratio * Deposit_Stock` (outflow to reserves) | dimensionless, USD | textbook_standard_unverified_locally |

---

## หมวด E: สิ่งแวดล้อม/มลพิษ (Environmental)

| ชื่อ | สูตร (Flow) | หน่วยที่ต้องมี | validation_status |
|---|---|---|---|
| Wind Advection of Pollutant | `v_wind * c_drag * Pollutant_Stock` | m/s, 1/m, kg | ตัวอย่างที่ใช้เริ่มบทสนทนานี้ — textbook_standard_unverified_locally |
| Biodegradation (first-order decay) | `k_decay * Pollutant_Stock` | 1/day, kg | textbook_standard_unverified_locally |
| Streeter-Phelps DO Sag (deoxygenation) | `k_d_deoxy * BOD_Stock` | 1/day, mg/L | textbook_standard_unverified_locally |
| Streeter-Phelps DO Sag (reaeration) | `k_r_reox * (DO_sat - DO_Stock)` | 1/day, mg/L, mg/L | textbook_standard_unverified_locally |
| Eutrophication — Nutrient Uptake by Algae | `uptake_rate * Nutrient_Stock * Algae_Stock / (Ks + Nutrient_Stock)` | ต้องเช็คหน่วยตาม Monod form | textbook_standard_unverified_locally |
| Groundwater Contaminant Advection-Dispersion (box chain) | `v_flow*(C_i - C_i-1)/dx + D*(C_i+1 - 2*C_i + C_i-1)/dx^2` | ดู "Spatial via Multi-Box" ด้านล่าง | textbook_standard_unverified_locally |
| Atmospheric CO2 Ocean-Exchange | `k_exchange * (pCO2_atm - pCO2_ocean)` | ppm/year, ppm, ppm | textbook_standard_unverified_locally |
| PM2.5 Deposition (dry deposition) | `v_deposition * Area / Volume * PM25_Stock` | m/s, m², m³, μg/m³ | textbook_standard_unverified_locally |

---

## หมวด F: เภสัชจลนศาสตร์/การแพทย์ (Pharmacokinetics/Medicine)

| ชื่อ | สูตร (Flow) | หน่วยที่ต้องมี | validation_status |
|---|---|---|---|
| One-Compartment Absorption | `ka_absorption * Gut_Stock` | 1/hr, mg | validated_stress_tested |
| One-Compartment Elimination | `ke_elimination * Blood_Stock` | 1/hr, mg | validated_stress_tested |
| Michaelis-Menten (saturable) Elimination | `(Vmax_elim * Blood_Stock) / (Km_elim + Blood_Stock)` | mg/hr, mg, mg | textbook_standard_unverified_locally |
| Periodic Dosing (pulse) | `if_then_else(mod(t, tau_interval) < pulse_width, dose_rate, 0)` | ชม, ชม, mg/hr | validated_stress_tested |
| **Glucose-Insulin (Bergman Minimal Model)** — Glucose utilization | `p1*(G_Stock-Gb_basal) + X_Stock*G_Stock` | 1/min, mg/dL, mg/dL, 1/min | validated_stress_tested |
| **Bergman Minimal Model** — Insulin action decay | `p2 * X_Stock` | 1/min | validated_stress_tested |
| **Bergman Minimal Model** — Insulin action input (จาก CSV จริง) | `p3 * (Ia_obs(t) - Ib_basal)` | ต้องใช้ time-series ดูหมวด I | validated_stress_tested |
| Tumor Growth (Gompertz) | ดูหมวด B — สูตรเดียวกัน | g, g | textbook_standard_unverified_locally |
| Drug-Receptor Binding (mass action) | `kon_rate * Drug_free_Stock * Receptor_free_Stock - koff_rate * Complex_Stock` | ต้องแยกเป็น 2 flow | textbook_standard_unverified_locally |

---

## หมวด G: วิศวกรรม/ระบบควบคุม (Engineering/Control Systems)

| ชื่อ | สูตร (Flow) | หน่วยที่ต้องมี | validation_status |
|---|---|---|---|
| Water Tank with Valve Cap | `min(max_outflow, k_outflow * level_Stock)` | m³/s, 1/s, m | validated_stress_tested |
| P-Controller Error Correction | `Kp_gain * (Setpoint - ProcessValue_Stock)` | 1/(หน่วย·s), หน่วยของ setpoint | textbook_standard_unverified_locally |
| Spring-Mass-Damper (velocity) | `(applied_force - k_spring*x_Stock - c_damp*v_Stock) / mass` | N, N/m, m, N·s/m, m/s, kg | textbook_standard_unverified_locally |
| Heat Exchanger (counter-flow simplified) | `UA_coeff * (T_hot_Stock - T_cold_Stock)` | W/K, K | textbook_standard_unverified_locally |
| Queue Length (M/M/1 fluid approx.) | `arrival_rate - min(service_rate, Queue_Stock/dt_service)` | 1/s, 1/s, คน | textbook_standard_unverified_locally |
| Capacitor Charging (RC) | `(V_source - V_Stock) / (R * C)` | V, V, Ω, F | textbook_standard_unverified_locally |

---

## หมวด H: รูปแบบเชิงพื้นที่แบบง่าย (Spatial via Multi-Box — ไม่ใช่ PDE เต็มรูปแบบ)

⚠️ **ข้อจำกัด:** engine ของเราเป็น lumped ODE เท่านั้น (อ่านหัวข้อ "Spatial dependence" ที่คุยกันไว้ก่อนหน้า) — วิธีนี้คือการ**ประมาณ PDE ด้วยหลาย stock ต่อกันเป็นสาย** (method of lines) ใช้ได้กับ resolution เชิงพื้นที่แบบหยาบเท่านั้น

| Pattern | คำอธิบาย |
|---|---|
| Advection Chain | stock1 → stock2 → stock3 → ... แต่ละ flow คือ `v_flow * stock_i` (ทิศทางเดียว) |
| Dispersion Pair | ระหว่าง stock ที่ติดกัน เพิ่ม flow สองทิศทางเป็นสัดส่วนกับผลต่างความเข้มข้น `D_coeff * (stock_i - stock_j) / dx^2` |
| ตัวอย่างที่ทดสอบแล้ว | Reversible Chemistry A⇌B⇌C (หมวด C) ใช้โครงสร้างเดียวกันเป๊ะ แค่ตีความ "สาร" เป็น "ตำแหน่ง" แทน |

---

## หมวด I: รูปแบบที่ควรใช้ข้อมูล Time-Series จริง แทนสูตรเดา (สำคัญมาก — ตามที่ขอให้ไม่ลืม)

**บทเรียนจากโมเดลปลา tilapia ในบทสนทนานี้:** รอบแรกเดาสูตร sigmoid สำหรับ `b(t)` (ค่าประสิทธิภาพการดูดซึมอาหาร) เพราะไม่มีข้อมูลจริง — ผลจำลองคลาดเคลื่อนจากของจริงเกือบครึ่ง พอเปลี่ยนมาใช้ **ข้อมูลจริงจาก CSV โดยตรง** (`b_obs(t)`) แทนการเดาสูตร ผลคลาดเคลื่อนเหลือแค่ **0.10%** — ต่างกันเป็นระดับความน่าเชื่อถือคนละขั้นเลย

### กฎการตัดสินใจ: เมื่อไหร่ควรใช้ Time-Series แทนสูตร

| สถานการณ์ | ควรทำ |
|---|---|
| มีข้อมูลวัดจริงตามเวลาอยู่แล้ว (เช่น อุณหภูมิ, DO, ความเข้มข้นที่วัดจริง) | ✅ ใช้ CSV time-series (`ชื่อ(t)`) เสมอ ไม่ต้องเดาสูตร |
| ไม่มีข้อมูลจริง แต่รู้กลไกทางฟิสิกส์/ชีวภาพชัดเจน | ใช้สูตรจาก registry นี้ได้ แต่ต้องระบุ `assumptions` ชัดว่าเป็นการประมาณ |
| ไม่มีข้อมูลจริง และไม่แน่ใจกลไก | ⚠️ บอกผู้ใช้ตรงๆ ว่าเป็นการเดา ไม่ควรฝังเป็นค่าคงที่แบบไม่มีคำเตือน |
| ตัวแปรที่ควรจะคงที่ แต่จริงๆ วัดแล้วเปลี่ยนตามเวลา (เช่น `k` ในโมเดลปลาที่จริงแปรตามอุณหภูมิ) | ✅ อย่าฝืนใช้ parameter คงที่ — เปลี่ยนเป็น time-series ถ้ามีข้อมูล หรือเขียนเป็นฟังก์ชันของตัวแปรอื่นที่มีข้อมูลแทน (เช่น `k_obs(t)` หรือ `kmin*exp(j*(T_obs(t)-Tmin))`) |

### รูปแบบทางเทคนิคที่ใช้ได้ในสูตร (อ้างอิงสเปกไฟล์หลัก ข้อ 4)

```
สูตรอ้างอิง time-series ตรงๆ:           p3 * (Ia_obs(t) - Ib_basal)
สูตรผสม parameter คงที่ + time-series:   kmin * exp(j * (T_obs(t) - Tmin))
Periodic/pulse จากเวลา (ไม่ใช่ CSV):      if_then_else(mod(t, tau) < 1, dose, 0)
```

**ข้อควรจำ:** ตัวแปร time-series ไม่ใส่ใน `parameters`, ไม่ต้องมี information edge (ระบบจับคู่อัตโนมัติจากชื่อ) — ผู้ใช้ต้องอัปโหลด CSV แยกต่างหากในแอปเสมอ (ไฟล์ JSON แค่ "เรียกชื่อ" เท่านั้น ไม่ได้ฝังข้อมูลไว้)

---

## สรุปสถิติไฟล์นี้

- รวมทั้งหมด **~90 entries** ใน 7 หมวดสูตร + 2 หมวดรูปแบบพิเศษ (spatial, time-series)
- `validated_against_real_data`: 1 ข้อ (bioenergetic growth ปลา)
- `validated_stress_tested`: ~20 ข้อ (ทดสอบรันจริงในบทสนทนานี้แล้ว)
- `textbook_standard_unverified_locally`: ที่เหลือทั้งหมด — **ต้องผ่าน verification engine ก่อนเชื่อ**

ไฟล์นี้จะโตขึ้นเรื่อยๆ ตามเคสจริงที่แก้กัน — ทุกครั้งที่แก้ปัญหาใหม่ ควรอัปเดต `validation_status` ของ entry ที่เกี่ยวข้องให้ตรงกับสิ่งที่พิสูจน์แล้วจริง ไม่ปล่อยค้างไว้ที่ `textbook_standard_unverified_locally` ทั้งที่จริงๆ ทดสอบผ่านแล้ว

---

## วิธีใช้ 2 ส่วนนี้ร่วมกัน (สรุปสั้นๆ)

1. อ่านปัญหาที่ผู้ใช้อธิบาย
2. เปิดดู **ส่วนที่ 2** หาว่ามีกฎที่ตรง/ใกล้เคียงปัญหานี้ไหม ถ้ามีให้ใช้เป็นฐาน (บอก `validation_status` ของมันด้วยตรงๆ) ถ้าไม่มีให้บอกผู้ใช้ว่ากำลังใช้ความรู้ทั่วไปนอกเหนือ registry
3. เขียน JSON ตามกฎ**ทุกข้อ**ใน **ส่วนที่ 1** (โครงสร้าง, edges, ฟังก์ชันที่ใช้ได้, ข้อห้าม)
4. ไล่เช็ค checklist ข้อ 8 ของส่วนที่ 1 ให้เห็นผลจริง (ตามข้อ 9.1)
5. สร้างไฟล์ `.json` ให้ดาวน์โหลด (ตามข้อ 9.2) — ห้ามแปะโค้ดลอยๆ ในแชท
