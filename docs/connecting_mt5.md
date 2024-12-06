# การเชื่อมต่อและดึงข้อมูลจาก MetaTrader 5

## ทำไมถึงใช้ Async/Await แทน Thread หรือ Loop Interval

### 1. ประสิทธิภาพการใช้ทรัพยากร
- **Single Thread with Event Loop**: ใช้ event loop จัดการงานหลายๆ อย่างใน thread เดียว
- **ประหยัด Memory**: ไม่ต้องสร้าง thread ใหม่
- **ลด Overhead**: ไม่มี context switching ระหว่าง threads

### 2. การจัดการ Concurrency
- **Non-blocking I/O**: ทำงานแบบไม่ block การทำงานอื่น
- **Task Management**: จัดการหลาย tasks พร้อมกันได้ง่าย
- **Error Handling**: จัดการ errors ได้ดีกว่าใช้ threads

### 3. ความแม่นยำของเวลา
- **Real-time Data**: ไม่พลาดข้อมูลสำคัญเพราะไม่ต้องใช้ sleep()
- **ตอบสนองทันที**: รับข้อมูลราคาได้ทันทีที่มีการเปลี่ยนแปลง
- **ลด Latency**: ความหน่วงของข้อมูลต่ำ

### 4. การควบคุมโปรแกรม
- **Graceful Shutdown**: หยุดโปรแกรมได้ทันทีด้วย KeyboardInterrupt
- **Code Readability**: โค้ดอ่านง่าย เข้าใจง่าย
- **Maintenance**: ดูแลรักษาโค้ดได้ง่าย

### 5. การขยายระบบ
- **Scalability**: เพิ่ม symbols ที่ติดตามได้ง่าย
- **Extensibility**: เพิ่ม callbacks สำหรับการประมวลผลได้
- **Integration**: เชื่อมต่อกับระบบอื่นๆ ได้ง่าย

## วิธีการใช้งาน

### การเริ่มต้น
```python
price_stream = MT5AsyncStream()
price_stream.add_callback(on_price_change)
await price_stream.start(["EURUSD", "USDJPY"])
```

### การแสดงผล
- แสดงข้อมูลบัญชี (Balance, Equity, Margin)
- แสดงราคาปัจจุบัน (Bid, Ask, Last)
- แสดง Positions ที่เปิดอยู่
- ใช้สีแยกแยะข้อมูล:
  - กำไร (สีเขียว)
  - ขาดทุน (สีแดง)
  - Buy Position (สีน้ำเงิน)
  - Sell Position (สีเหลือง)

### การหยุดการทำงาน
- กด Ctrl+C เพื่อหยุดโปรแกรม
- ระบบจะ shutdown MT5 connection อัตโนมัติ

## ข้อควรระวัง
1. ต้องเปิด MT5 และ login ก่อนใช้งาน
2. ตรวจสอบ internet connection
3. ระวังการใช้ memory เมื่อติดตามหลาย symbols
4. ควรมีระบบ logging เพื่อติดตามการทำงาน