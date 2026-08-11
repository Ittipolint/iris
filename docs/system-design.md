# Module Overview
ระบบ IT Ticket Tracker (MVP) ถูกออกแบบเป็นเว็บแอปแบบแยกส่วนโดยใช้ FastAPI ฝั่ง backend และ HTML/Tailwind CSS/Vanilla JavaScript ฝั่ง frontend เพื่อรองรับงานหลัก 5 อย่างคือ Create ticket, List, Get by ID, Update Status, และ Summary counts

โครงสร้างโปรเจกต์ที่ใช้:

- `apps/backend/router/`
  - รวม API endpoints ที่รับ request จาก frontend และส่งต่อไปยัง service layer
  - แยก router ตามหน้าที่ เช่น ticket operations และ summary
- `apps/backend/schemas/`
  - เก็บ Pydantic models สำหรับ request/response และ validation rules
  - ใช้ enum สำหรับ `category`, `priority`, และ `status`
- `apps/backend/services/`
  - เก็บ business logic ทั้งหมด
  - ดูแล in-memory Python list, การสร้าง id, การ filter, การ update status, และการคำนวณ summary
- `tests/`
  - เก็บ automated test scripts สำหรับยืนยัน endpoint, validation, seed control, และ summary logic
- `frontend/`
  - เก็บหน้า HTML, Tailwind styling, และ Vanilla JavaScript สำหรับเรียก API และ render ticket list, form, filter, และ summary

การไหลของข้อมูล:

1. ผู้ใช้กรอกข้อมูลหรือเลือก filter ใน frontend
2. JavaScript ส่ง request ไปยัง FastAPI endpoint
3. Router ตรวจสอบ schema เบื้องต้นแล้วส่งต่อให้ service
4. Service ทำงานกับ in-memory store และคืนผลลัพธ์
5. Frontend render ข้อมูลใหม่ เช่น list, summary, หรือ error message

# Data Model Schema
ระบบใช้ in-memory data model เดียวคือ `Ticket` โดยไม่มี database จริงและไม่มี authentication/role ใด ๆ

## Ticket
- `id: str`
  - รูปแบบ `TKT-xxx`
  - `xxx` เป็นเลข 3 หลัก เช่น `TKT-001`
  - ระบบเป็นผู้สร้างค่า `id`
- `category: Literal["Hardware", "Software", "Network", "Account"]`
- `priority: Literal["Low", "Medium", "High"]`
- `status: Literal["Open", "In Progress", "Resolved"]`
  - ค่าเริ่มต้นเมื่อสร้าง ticket ใหม่คือ `Open`

## Create Ticket Request
- `category`
- `priority`

## Update Status Request
- `status`

## List Query Parameters
- `status` เป็น optional query parameter
- ใช้สำหรับ filter list ตามสถานะที่กำหนดเท่านั้น

## Summary Response
- `total`
- `open`
- `in_progress`
- `resolved`

## Seed Data
- ต้องมี seed อย่างน้อย 3 รายการ
- Seed ต้องครอบคลุมสถานะ `Open`, `In Progress`, และ `Resolved`
- Seed control ต้องเปิดหรือปิดได้ผ่าน configuration เพื่อให้ automated tests กำหนด initial state เองได้
- เมื่อ seed ถูกปิด ระบบต้องเริ่มจากรายการว่างและให้ test เติมข้อมูลตามที่ต้องการ
- เมื่อ seed ถูกเปิด ระบบต้อง preload ข้อมูลตัวอย่างเข้า in-memory store ตอนเริ่ม app หรือก่อนรันทดสอบ

## In-Memory Store Rules
- ข้อมูลทั้งหมดเก็บใน Python list ภายใน service layer
- การสร้าง ticket ใหม่ต้อง append เข้า list เดิม
- การ update status ต้องแก้ไขรายการเดิมใน list โดยอ้างอิง `id`
- summary counts ต้องคำนวณจาก list ปัจจุบันทุกครั้ง ไม่ใช้ค่า cache

# API Endpoints Contract
ทุก endpoint ใช้ JSON เป็นหลักและสอดคล้องกับ schema ที่กำหนดไว้

## `POST /tickets`
สร้าง ticket ใหม่

Request body:
```json
{
  "category": "Hardware",
  "priority": "High"
}
```

Response:
- `201 Created`
- ส่งกลับ ticket ที่สร้างแล้วพร้อม `id` และ `status: "Open"`

Validation:
- `category` ต้องอยู่ในชุดที่กำหนด
- `priority` ต้องอยู่ในชุดที่กำหนด
- missing required fields ต้องได้ `422 Unprocessable Entity`

## `GET /tickets`
ดึงรายการ ticket ทั้งหมด

Query:
- `status` optional สำหรับ filter

Response:
- `200 OK`
- คืน array ของ ticket ตาม filter ถ้ามี
- ถ้าไม่พบรายการให้คืน array ว่าง

## `GET /tickets/{id}`
ดึง ticket ตาม `id`

Response:
- `200 OK` เมื่อพบ ticket
- `404 Not Found` เมื่อไม่พบ ticket ที่ตรงกับ `id`

Path rule:
- `id` ต้องมีรูปแบบ `TKT-xxx`

## `PATCH /tickets/{id}/status`
อัปเดตสถานะของ ticket

Request body:
```json
{
  "status": "Resolved"
}
```

Response:
- `200 OK` เมื่ออัปเดตสำเร็จ
- `404 Not Found` เมื่อไม่พบ ticket
- `422 Unprocessable Entity` เมื่อ status ไม่อยู่ในชุดที่กำหนด

Behavior:
- เปลี่ยน status ได้เฉพาะค่าที่อนุญาต
- หากส่ง status เดิมซ้ำ ระบบยังตอบสำเร็จได้ แต่ต้องไม่ทำให้ summary counts เพี้ยน

## `GET /summary`
คืนจำนวน ticket ตามสถานะ

Response:
```json
{
  "total": 3,
  "open": 1,
  "in_progress": 1,
  "resolved": 1
}
```

Behavior:
- นับจากข้อมูลปัจจุบันใน list
- ต้องสอดคล้องกับข้อมูลจริงใน `GET /tickets`

# Frontend Flow
frontend เป็นหน้าเดียวที่ใช้ Vanilla JavaScript เรียก API และ render state ตามข้อมูลล่าสุด

## Page Initialization
- โหลด summary counts และ ticket list ตอนเปิดหน้า
- ถ้า seed เปิดอยู่ หน้าแรกจะเห็นข้อมูลตัวอย่างทันที
- ถ้า seed ปิดอยู่ list และ summary จะเริ่มจาก state ว่าง

## Create Ticket Flow
1. ผู้ใช้เลือก `category` และ `priority`
2. กด submit form
3. JavaScript ส่ง `POST /tickets`
4. ถ้าสำเร็จ ให้ล้าง form
5. รีเฟรช summary และ ticket list
6. ถ้า error ให้แสดง validation message บนหน้าเดิม

## List and Filter Flow
1. หน้าโหลดรายการ ticket ผ่าน `GET /tickets`
2. ผู้ใช้เลือก filter status
3. JavaScript เรียก `GET /tickets?status=...`
4. ถ้าไม่มีข้อมูลให้แสดง empty state

## Get by ID Flow
- ใช้เมื่อ frontend ต้องการดูรายละเอียดของ ticket เฉพาะตัว
- ดึงข้อมูลด้วย `GET /tickets/{id}`
- ใช้แสดงรายละเอียดหรือยืนยัน state ก่อน update status

## Update Status Flow
1. ผู้ใช้กด action เพื่อเปลี่ยนสถานะของ ticket
2. JavaScript ส่ง `PATCH /tickets/{id}/status`
3. ถ้าสำเร็จ ให้รีเฟรช summary และ list ทันที
4. ถ้าไม่สำเร็จ ให้แสดง error และคงรายการเดิมไว้

## UI Behavior
- ใช้ Tailwind CSS สำหรับ layout, table, form, badge, และ empty state
- ใช้สีหรือ badge แยกสถานะ `Open`, `In Progress`, `Resolved`
- summary cards แสดง count ของแต่ละสถานะและ total

# Validation and Error Handling
การ validate หลักใช้ Pydantic และกฎเชิงธุรกิจใช้ service layer

## Validation Rules
- `category` รับเฉพาะ `Hardware`, `Software`, `Network`, `Account`
- `priority` รับเฉพาะ `Low`, `Medium`, `High`
- `status` รับเฉพาะ `Open`, `In Progress`, `Resolved`
- `id` ต้องตรงรูปแบบ `TKT-xxx`
- create request ต้องมี required fields ครบ
- `status` ตอนสร้าง ticket ต้อง default เป็น `Open`

## Error Handling
- ใช้ `422 Unprocessable Entity` สำหรับ validation failure
- ใช้ `404 Not Found` สำหรับ ticket id ที่ไม่มีอยู่จริง
- ใช้ error response แบบอ่านง่ายสำหรับ frontend เช่น `{ "detail": "..." }`
- frontend ต้องแสดง error message จาก backend โดยไม่ทำให้หน้าพัง

## Edge Behavior in Design
- เมื่อ filter แล้วไม่พบรายการ ต้องแสดง empty state ไม่ใช่ error
- เมื่อ update status เป็นค่าเดิม ให้ถือว่า operation ไม่ทำลายข้อมูล
- summary counts ต้อง update หลังทุก mutation เพื่อไม่ให้ข้อมูลค้าง
- ถ้าข้อมูล ticket เปลี่ยนระหว่างที่ผู้ใช้กำลังดูรายการ ต้องให้ frontend refetch ข้อมูลล่าสุดเพื่อให้แสดง state ปัจจุบัน

## Service-Level Guardrails
- service ต้องเป็นจุดเดียวที่แก้ไข in-memory data
- router ไม่ควรแก้ list โดยตรง
- summary ต้องคำนวณจาก source of truth เดียวกันกับ list

# Implementation Steps
1. สร้าง Pydantic enums และ request/response schemas ใน `apps/backend/schemas/`
2. สร้าง service layer ใน `apps/backend/services/` สำหรับ in-memory CRUD, id generation, filter, status update, summary, และ seed toggle
3. สร้าง router ใน `apps/backend/router/` สำหรับ `POST /tickets`, `GET /tickets`, `GET /tickets/{id}`, `PATCH /tickets/{id}/status`, และ `GET /summary`
4. สร้าง FastAPI app entrypoint เพื่อรวม router และ initialize seed data ตาม config
5. สร้าง frontend page ใน `frontend/` สำหรับ form, filter, list, summary, empty state, และ error display
6. เขียน Vanilla JavaScript สำหรับ fetch data, submit create form, change filter, และ update status
7. สร้าง tests ใน `tests/` เพื่อยืนยัน validation, filter, update flow, summary accuracy, seed on/off behavior, และ id format
8. ตรวจให้แน่ใจว่าไม่มี field, rule, หรือ endpoint เกินกว่าที่ requirement กำหนด