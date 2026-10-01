# พจนานุกรมข้อมูล

CSV เป็น UTF-8 BOM, JSON เป็น UTF-8; CSV ช่องว่าง = null ไม่ใช่ศูนย์; ทุกเวลา +07:00

## fuel_price_reference.csv

1 row per report month; not daily actuals

| ฟิลด์ | ชนิด | หน่วย | ว่างได้ | ความหมาย |
|---|---|---|---|---|
| `fuel_price_id` | text |  | ไม่ได้ | คีย์ราคาดีเซล benchmark รายเดือน |
| `reference_month` | text |  | ไม่ได้ | เดือนรายงานที่ให้ราคาน้ำมัน benchmark |
| `fuel_type` | text |  | ไม่ได้ | ประเภทเชื้อเพลิง Diesel ของกองรถ |
| `benchmark_thb_per_litre` | decimal | THB per unit | ไม่ได้ | ค่าราคาดีเซลจากรายงาน EPPO ใช้เป็น benchmark ทั้งเดือน ไม่ใช่ค่าเฉลี่ย |
| `source_id` | text |  | ไม่ได้ | รหัสแหล่งอ้างอิงสาธารณะ |
| `is_observed_daily_price` | boolean |  | ไม่ได้ | False เพราะใช้ราคาฐานจากรายงาน ไม่ได้มีราคาซื้อจริงรายวัน |

## sources.csv

1 row per public reference source

| ฟิลด์ | ชนิด | หน่วย | ว่างได้ | ความหมาย |
|---|---|---|---|---|
| `source_id` | text |  | ไม่ได้ | รหัสแหล่งอ้างอิงสาธารณะ |
| `publisher` | text |  | ไม่ได้ | ผู้เผยแพร่แหล่งอ้างอิง |
| `title` | text |  | ไม่ได้ | ชื่อแหล่งอ้างอิง |
| `url` | text |  | ไม่ได้ | URL แหล่งข้อมูลต้นฉบับ |
| `reference_period` | text |  | ไม่ได้ | ช่วงเวลาของแหล่งอ้างอิง แยกจากงวดข้อมูลจำลอง |
| `used_for` | text |  | ไม่ได้ | สิ่งที่นำแหล่งอ้างอิงมาใช้ในแบบจำลอง |
| `limitation` | text |  | ไม่ได้ | ข้อจำกัดการนำแหล่งอ้างอิงมาใช้ |

## hubs.csv

1 row per fictional hub in a real province

| ฟิลด์ | ชนิด | หน่วย | ว่างได้ | ความหมาย |
|---|---|---|---|---|
| `hub_id` | text |  | ไม่ได้ | รหัสศูนย์จำลอง |
| `hub_name` | text |  | ไม่ได้ | ชื่อศูนย์จำลองในจังหวัดจริง |
| `province` | text |  | ไม่ได้ | ชื่อจังหวัดจริงที่ใช้ในสถานการณ์ |
| `region` | text |  | ไม่ได้ | กลุ่มภูมิภาคในโครงงาน |
| `latitude` | decimal |  | ไม่ได้ | ละติจูด WGS84 จุดประมาณศูนย์เมืองที่ตั้งสมมติ |
| `longitude` | decimal |  | ไม่ได้ | ลองจิจูด WGS84 จุดประมาณศูนย์เมืองที่ตั้งสมมติ |
| `coordinates_basis` | text |  | ไม่ได้ | คำอธิบายจุดพิกัดของศูนย์สมมติ |

## routes.csv

1 row per outbound linehaul lane or local delivery loop

| ฟิลด์ | ชนิด | หน่วย | ว่างได้ | ความหมาย |
|---|---|---|---|---|
| `route_id` | text |  | ไม่ได้ | รหัสเส้นทางระหว่างศูนย์หรือวงรอบส่งในเมือง |
| `route_kind` | text |  | ไม่ได้ | เส้นทางระหว่างศูนย์หรือวงรอบส่งในเมือง |
| `origin_hub_id` | text |  | ไม่ได้ | คีย์ศูนย์ต้นทาง |
| `destination_hub_id` | text |  | ไม่ได้ | คีย์ศูนย์ปลายทาง |
| `destination_province` | text |  | ไม่ได้ | จังหวัดปลายทางจริงของสถานการณ์สมมติ |
| `destination_region` | text |  | ไม่ได้ | กลุ่มภูมิภาคที่กำหนดในโครงงาน ไม่ใช่พิกัด GPS |
| `standard_outbound_km` | decimal | km | ได้ | ระยะทางขาออกที่ OSRM คำนวณจากจุดศูนย์เมืองสมมติ |
| `standard_return_km` | decimal | km | ได้ | ระยะทางกลับที่คำนวณแยก ไม่สมมติว่าต้องเท่าขาออก |
| `osrm_car_duration_hours` | decimal | hours | ได้ | ระยะเวลาคำนวณ profile รถยนต์ ไม่ใช่เวลาจริงหรือเวลารับประกันรถบรรทุก |
| `planned_truck_outbound_hours` | decimal | hours | ได้ | เวลาแผนสมมติ standard_outbound_km/62 + 0.75 ชั่วโมง |
| `target_booking_share` | decimal |  | ได้ | สัดส่วนตามสถานการณ์ที่ผู้ใช้เลือก ไม่ใช่สัดส่วนตลาดจริง |
| `distance_basis` | text |  | ไม่ได้ | คำอธิบายวิธีเลือกฐานระยะทาง |
| `distance_source_id` | text |  | ได้ | ที่มาของฐานระยะทาง null สำหรับ local loop ซึ่งสมมติทั้งหมด |
| `route_api_url` | text |  | ได้ | คำขอ OSRM ที่ใช้ดึงฐานระยะทางของเส้นทางนี้ |
| `distance_reference_date` | ISO8601 date |  | ได้ | วันที่ขอ route จากแผนที่ ไม่ใช่วันวิ่งรถ |

## vehicle_models.csv

1 row per model with referenced GVW and assumed operational parameters

| ฟิลด์ | ชนิด | หน่วย | ว่างได้ | ความหมาย |
|---|---|---|---|---|
| `model_code` | text |  | ไม่ได้ | รหัสรุ่นรถ NLR/NPR/FTR |
| `vehicle_type` | text |  | ไม่ได้ | ประเภทและขนาดรถอิงชนิดรุ่นที่เลือก |
| `gross_vehicle_weight_kg` | integer | kg | ไม่ได้ | น้ำหนักรวมรถและบรรทุกจากสเปกผู้ผลิต ไม่ใช่น้ำหนักสินค้า |
| `assumed_tare_kg` | integer | kg | ไม่ได้ | น้ำหนักรถรวมตัวถังที่สมมติ |
| `capacity_kg` | integer | kg | ไม่ได้ | GVW ลบน้ำหนักรถสมมติ เป็นเพดานปฏิบัติงานจำลอง |
| `capacity_m3` | integer | m3 | ไม่ได้ | ปริมาตรบรรทุกสมมติ ไม่ใช่สเปกตัวถังรับรอง |
| `baseline_km_per_litre` | decimal |  | ไม่ได้ | อัตราประหยัดน้ำมันตั้งต้นสมมติ ไม่ใช่ผลทดสอบผู้ผลิต |
| `maintenance_thb_per_km` | decimal | THB per unit | ไม่ได้ | ต้นทุนซ่อมบำรุงเฉลี่ยสมมติต่อ กม. |
| `depreciation_thb_per_km` | decimal | THB per unit | ไม่ได้ | ต้นทุนค่าเสื่อมต่อ กม. สมมติ |
| `crew_hourly_cost_thb` | integer | THB | ไม่ได้ | ค่าแรง/ต้นทุนคนขับต่อชั่วโมงสมมติ ไม่ใช่อัตราค่าจ้างจริง |
| `gvw_source_id` | text |  | ไม่ได้ | คีย์อ้างอิงน้ำหนักรวมรถจากผู้ผลิต |
| `other_parameters_basis` | text |  | ไม่ได้ | ระบุว่าสเปกปฏิบัติการนอกจาก GVW เป็นสมมติฐาน |

## vehicles.csv

1 row per fictional physical vehicle

| ฟิลด์ | ชนิด | หน่วย | ว่างได้ | ความหมาย |
|---|---|---|---|---|
| `vehicle_id` | text |  | ไม่ได้ | รหัสรถจำลอง |
| `vehicle_label` | text |  | ไม่ได้ | ชื่อรถจำลอง ไม่มีทะเบียนจริง |
| `model_code` | text |  | ไม่ได้ | รหัสรุ่นรถ NLR/NPR/FTR |
| `operation_type` | text |  | ไม่ได้ | หน้าที่รถ LINEHAUL หรือ LAST_MILE |
| `home_hub_id` | text |  | ไม่ได้ | ศูนย์ประจำที่รถและคนขับต้องกลับ |
| `fuel_type` | text |  | ไม่ได้ | ประเภทเชื้อเพลิง Diesel ของกองรถ |
| `commissioned_date` | ISO8601 date |  | ไม่ได้ | วันนำรถเข้ากองรถที่สมมติ |
| `is_synthetic` | boolean |  | ไม่ได้ | True สำหรับระเบียนจำลอง |

## drivers.csv

1 row per fictional driver with prior profile, not outcomes from this dataset

| ฟิลด์ | ชนิด | หน่วย | ว่างได้ | ความหมาย |
|---|---|---|---|---|
| `driver_id` | text |  | ไม่ได้ | รหัสคนขับจำลอง |
| `driver_name` | text |  | ไม่ได้ | ชื่อคนขับสมมติ |
| `home_hub_id` | text |  | ไม่ได้ | ศูนย์ประจำที่รถและคนขับต้องกลับ |
| `assigned_vehicle_id` | text |  | ไม่ได้ | รถประจำของคนขับจำลอง |
| `experience_years` | integer |  | ไม่ได้ | ประสบการณ์คนขับสมมติ ณ ต้นงวด |
| `prior_safety_score` | decimal |  | ไม่ได้ | คะแนนความปลอดภัยสมมติก่อนช่วงข้อมูล |
| `prior_fuel_skill_factor` | decimal |  | ไม่ได้ | ตัวคูณทักษะประหยัดน้ำมันสมมติก่อนช่วงข้อมูล |
| `licence_type` | text |  | ไม่ได้ | สมมติว่ามีใบอนุญาตขับรถที่เหมาะสม ไม่มีเลขใบอนุญาตจริง |
| `is_synthetic` | boolean |  | ไม่ได้ | True สำหรับระเบียนจำลอง |

## vehicle_maintenance.csv

1 row per vehicle unavailability interval

| ฟิลด์ | ชนิด | หน่วย | ว่างได้ | ความหมาย |
|---|---|---|---|---|
| `maintenance_id` | text |  | ไม่ได้ | คีย์ช่วงซ่อมบำรุง |
| `vehicle_id` | text |  | ไม่ได้ | รหัสรถจำลอง |
| `unavailable_from` | ISO8601 timestamp +07:00 |  | ไม่ได้ | เริ่มช่วงที่รถไม่พร้อมใช้งาน |
| `unavailable_until` | ISO8601 timestamp +07:00 |  | ไม่ได้ | สิ้นสุดช่วงที่รถไม่พร้อมใช้งานแบบ exclusive |
| `maintenance_type` | text |  | ไม่ได้ | ประเภทการหยุดรถซ่อมบำรุงที่สมมติ |
| `is_synthetic` | boolean |  | ไม่ได้ | True สำหรับระเบียนจำลอง |

## customers.csv

1 row per fictional customer

| ฟิลด์ | ชนิด | หน่วย | ว่างได้ | ความหมาย |
|---|---|---|---|---|
| `customer_id` | text |  | ไม่ได้ | รหัสลูกค้าจำลอง |
| `customer_name` | text |  | ไม่ได้ | ชื่อลูกค้าจำลอง ไม่มีข้อมูลส่วนบุคคลจริง |
| `customer_type` | text |  | ไม่ได้ | กลุ่มลูกค้าสมมติ B2B/B2C/VIP |
| `province` | text |  | ไม่ได้ | ชื่อจังหวัดจริงที่ใช้ในสถานการณ์ |
| `destination_hub_id` | text |  | ไม่ได้ | คีย์ศูนย์ปลายทาง |
| `is_synthetic` | boolean |  | ไม่ได้ | True สำหรับระเบียนจำลอง |

## calendar.csv

1 row per calendar date in the booking period

| ฟิลด์ | ชนิด | หน่วย | ว่างได้ | ความหมาย |
|---|---|---|---|---|
| `date_key` | integer |  | ไม่ได้ | คีย์วันที่จำนวนเต็ม YYYYMMDD |
| `date` | ISO8601 date |  | ไม่ได้ | วันที่ปฏิทิน ค.ศ. |
| `year` | integer |  | ไม่ได้ | ปี ค.ศ. |
| `quarter` | integer |  | ไม่ได้ | ไตรมาสปฏิทิน 1-4 |
| `month` | integer |  | ไม่ได้ | เดือนเลข 1-12 |
| `day` | integer |  | ไม่ได้ | เลขวันที่ในเดือน |
| `iso_weekday` | integer |  | ไม่ได้ | วันในสัปดาห์ 1=จันทร์ ถึง 7=อาทิตย์ |
| `is_weekend` | boolean |  | ไม่ได้ | เสาร์/อาทิตย์ของปฏิทิน |
| `is_campaign_day` | boolean |  | ไม่ได้ | ธงวันกิจกรรมสมมติ เลขวันเท่ากับเดือนหรือวันที่ 12-16 เม.ย. ไม่ได้แทนปฏิทินวันหยุดราชการ |
| `is_monsoon_context` | boolean |  | ไม่ได้ | ธงบริบทฤดูฝนตั้งแต่ 15 พ.ค. ไม่ใช่ผลสังเกตฝนจริง |

## route_conditions.csv

1 row per date and linehaul lane; forecasts separate from observations

| ฟิลด์ | ชนิด | หน่วย | ว่างได้ | ความหมาย |
|---|---|---|---|---|
| `condition_id` | text |  | ไม่ได้ | รหัสสภาพเส้นทางรายวัน |
| `date` | ISO8601 date |  | ไม่ได้ | วันที่ปฏิทิน ค.ศ. |
| `route_id` | text |  | ไม่ได้ | รหัสเส้นทางระหว่างศูนย์หรือวงรอบส่งในเมือง |
| `traffic_forecast_level` | integer |  | ไม่ได้ | ระดับจราจรพยากรณ์จำลอง 1=เบา 2=ปานกลาง 3=หนาแน่น |
| `rain_forecast_flag` | boolean |  | ไม่ได้ | ผลพยากรณ์ฝนจำลองที่รู้ล่วงหน้า |
| `observed_rain_flag` | boolean |  | ไม่ได้ | ฝนที่จำลองว่าทราบภายหลัง ห้ามใช้ทำนายก่อน dispatch |
| `forecast_available_at` | ISO8601 timestamp +07:00 |  | ไม่ได้ | เวลาที่พยากรณ์จำลองพร้อมใช้งาน |
| `observation_available_at` | ISO8601 timestamp +07:00 |  | ไม่ได้ | เวลาที่ผลสังเกตอากาศจำลองถูกทราบ |
| `season_context_source_id` | text |  | ไม่ได้ | คีย์ข้อมูลฤดูกาลทั่วไปจาก TMD ไม่ใช่ข้อมูลฝนรายวัน |
| `is_synthetic` | boolean |  | ไม่ได้ | True สำหรับระเบียนจำลอง |

## shipments.csv

1 row per booked consignment, not per parcel or truck trip

| ฟิลด์ | ชนิด | หน่วย | ว่างได้ | ความหมาย |
|---|---|---|---|---|
| `shipment_id` | text |  | ไม่ได้ | รหัสรายการส่งสินค้า หนึ่งรายการอาจมีหลายกล่อง |
| `customer_id` | text |  | ไม่ได้ | รหัสลูกค้าจำลอง |
| `origin_hub_id` | text |  | ไม่ได้ | คีย์ศูนย์ต้นทาง |
| `destination_hub_id` | text |  | ไม่ได้ | คีย์ศูนย์ปลายทาง |
| `route_id` | text |  | ไม่ได้ | รหัสเส้นทางระหว่างศูนย์หรือวงรอบส่งในเมือง |
| `created_at` | ISO8601 timestamp +07:00 |  | ไม่ได้ | เวลารับคำสั่งส่งสินค้า |
| `service_level` | text |  | ไม่ได้ | ระดับบริการสมมติ STANDARD/EXPRESS/ECONOMY |
| `sla_calendar_days` | integer |  | ไม่ได้ | จำนวนวันปฏิทินหลังวันที่รับงานถึงกำหนดส่ง 18:00 |
| `promised_delivery_at` | ISO8601 timestamp +07:00 |  | ไม่ได้ | กำหนดส่งตาม SLA ของบริษัทจำลอง |
| `weight_kg` | decimal | kg | ไม่ได้ | น้ำหนักรวมของ shipment สมมติ |
| `volume_m3` | decimal | m3 | ไม่ได้ | ปริมาตรรวมสินค้าของ shipment สมมติ |
| `parcel_count` | integer |  | ไม่ได้ | จำนวนกล่องสมมติ ceil(weight/20) ไม่ใช่จำนวน shipment |
| `is_fragile` | boolean |  | ไม่ได้ | ธงสินค้าแตกหักง่ายสมมติ |
| `customer_charge_thb` | decimal | THB | ไม่ได้ | ค่าบริการจำลองที่แจ้งเมื่อรับงาน แยกจากต้นทุนขนส่ง ไม่ถือเป็นรายได้ที่รับรู้แล้ว |
| `cancelled_at` | ISO8601 timestamp +07:00 |  | ได้ | เวลายกเลิกก่อนบรรทุกสินค้า |
| `linehaul_departure_at` | ISO8601 timestamp +07:00 |  | ได้ | เวลา shipment ออกจากอุบลในเที่ยวระหว่างจังหวัด |
| `destination_hub_arrival_at` | ISO8601 timestamp +07:00 |  | ได้ | เวลาที่ shipment ถึงศูนย์ปลายทาง |
| `first_out_for_delivery_at` | ISO8601 timestamp +07:00 |  | ได้ | เวลาออกส่งถึงลูกค้าครั้งแรก |
| `actual_delivery_at` | ISO8601 timestamp +07:00 |  | ได้ | เวลาส่งถึงลูกค้าจำลองจริงในแบบจำลอง ค่าว่างหากยังไม่ส่งถึง ณ snapshot |
| `delivery_attempt_count` | integer |  | ไม่ได้ | จำนวนครั้งที่การลองส่งมีผลแล้วก่อน snapshot |
| `shipment_status` | text |  | ไม่ได้ | สถานะล่าสุด ณ snapshot; ความล่าช้าดู is_ontime/is_overdue_open แยก |
| `delay_minutes` | integer | minutes | ได้ | นาทีที่ช้ากว่ากำหนด เฉพาะรายการส่งสำเร็จ |
| `is_ontime` | boolean |  | ได้ | ตรงเวลาหรือไม่ เฉพาะ DELIVERED เท่านั้น |
| `is_overdue_open` | boolean |  | ไม่ได้ | ยังไม่ส่งสำเร็จและเลยกำหนด ณ snapshot |
| `recognized_transport_cost_thb` | decimal | THB | ไม่ได้ | ต้นทุนที่รับรู้แล้วจาก legs ของเที่ยวที่ปิดต้นทุน ไม่ใช่ต้นทุนครบทั้งหมดหากยังไม่ settle |
| `all_transport_costs_settled` | boolean |  | ไม่ได้ | ทุกเที่ยวรวมการกลับรถปิดต้นทุนแล้วหรือไม่ |
| `customer_rating` | decimal |  | ได้ | คะแนนลูกค้าหลังส่ง เป็นตัวแปรหลังเหตุการณ์ |
| `snapshot_at` | ISO8601 timestamp +07:00 |  | ไม่ได้ | เวลาตัดข้อมูลคงที่ 2025-09-30T23:59:59+07:00 |
| `is_synthetic` | boolean |  | ไม่ได้ | True สำหรับระเบียนจำลอง |

## shipment_events.csv

1 row per observed synthetic milestone as of snapshot

| ฟิลด์ | ชนิด | หน่วย | ว่างได้ | ความหมาย |
|---|---|---|---|---|
| `event_id` | text |  | ไม่ได้ | คีย์ประวัติสถานะ |
| `shipment_id` | text |  | ไม่ได้ | รหัสรายการส่งสินค้า หนึ่งรายการอาจมีหลายกล่อง |
| `event_type` | text |  | ไม่ได้ | ขั้นตอนการส่งสินค้า ดูสถานะ events ใน README |
| `event_at` | ISO8601 timestamp +07:00 |  | ไม่ได้ | เวลา milestone ที่เกิดแล้ว ณ snapshot |
| `hub_id` | text |  | ไม่ได้ | รหัสศูนย์จำลอง |
| `trip_id` | text |  | ได้ | รหัสเที่ยวรถที่รวมการกลับศูนย์ประจำ |
| `is_synthetic` | boolean |  | ไม่ได้ | True สำหรับระเบียนจำลอง |

## trips.csv

1 row per vehicle tour including return to home hub; linehaul or last mile

| ฟิลด์ | ชนิด | หน่วย | ว่างได้ | ความหมาย |
|---|---|---|---|---|
| `trip_id` | text |  | ไม่ได้ | รหัสเที่ยวรถที่รวมการกลับศูนย์ประจำ |
| `route_id` | text |  | ไม่ได้ | รหัสเส้นทางระหว่างศูนย์หรือวงรอบส่งในเมือง |
| `trip_kind` | text |  | ไม่ได้ | เที่ยวระหว่างจังหวัดหรือเที่ยวส่งถึงลูกค้า |
| `vehicle_id` | text |  | ไม่ได้ | รหัสรถจำลอง |
| `origin_hub_id` | text |  | ไม่ได้ | คีย์ศูนย์ต้นทาง |
| `destination_hub_id` | text |  | ไม่ได้ | คีย์ศูนย์ปลายทาง |
| `condition_id` | text |  | ไม่ได้ | รหัสสภาพเส้นทางรายวัน |
| `planned_departure_at` | ISO8601 timestamp +07:00 |  | ไม่ได้ | กำหนดออกเดินทางเดิม รวมเวลาโหลด 30 นาที |
| `planned_completion_at` | ISO8601 timestamp +07:00 |  | ไม่ได้ | กำหนดจบเที่ยวตามตารางก่อนทราบผลจริง |
| `actual_departure_at` | ISO8601 timestamp +07:00 |  | ได้ | เวลาออกเดินทางจำลองที่เกิดแล้ว |
| `actual_destination_arrival_at` | ISO8601 timestamp +07:00 |  | ได้ | เวลา linehaul ถึงศูนย์ปลายทาง ไม่ใช่เวลาส่งถึงลูกค้า |
| `actual_return_departure_at` | ISO8601 timestamp +07:00 |  | ได้ | เวลาออกจากศูนย์ปลายทางกลับอุบล |
| `actual_completion_at` | ISO8601 timestamp +07:00 |  | ได้ | เวลารถจบเที่ยวและกลับศูนย์ประจำก่อน snapshot |
| `trip_status` | text |  | ไม่ได้ | สถานะรถ PLANNED/IN_TRANSIT/AT_DESTINATION/RETURNING/COMPLETED |
| `shipment_count` | integer |  | ไม่ได้ | จำนวน shipment ใน manifest เที่ยวนี้ |
| `load_weight_kg` | decimal | kg | ไม่ได้ | ผลรวมน้ำหนัก shipment ที่บรรทุกเที่ยวนี้ |
| `load_volume_m3` | decimal | m3 | ไม่ได้ | ผลรวมปริมาตรสินค้าที่บรรทุกเที่ยวนี้ |
| `planned_round_trip_km` | decimal | km | ไม่ได้ | ระยะทางแผนทั้งรอบรวมกลับ |
| `actual_round_trip_km` | decimal | km | ได้ | ระยะทางจำลองเต็มเที่ยวรวมขากลับ แสดงเมื่อเที่ยวเสร็จ |
| `actual_outbound_km` | decimal | km | ได้ | ระยะทางขาออกที่เสร็จแล้ว สำหรับ last mile คือทั้งวงรอบเมื่อเสร็จ |
| `driving_hours` | decimal | hours | ได้ | ชั่วโมงขับจำลองทั้งเที่ยว ไม่รวมพักปลายทาง แสดงเมื่อปิดเที่ยว |
| `actual_fuel_litres` | decimal | litres | ได้ | ลิตรน้ำมันจำลองสำหรับทั้งขาไปและกลับ แสดงเมื่อปิดเที่ยว |
| `fuel_price_id` | text |  | ไม่ได้ | คีย์ราคาดีเซล benchmark รายเดือน |
| `planned_freight_cost_thb` | decimal | THB | ไม่ได้ | งบประมาณต้นทุนเที่ยวจากแบบจำลองก่อนปิดเที่ยว |
| `actual_freight_cost_thb` | decimal | THB | ได้ | ผลรวมต้นทุนจำลอง 6 หมวด ณ ปิดเที่ยว |
| `actual_fuel_cost_thb` | decimal | THB | ได้ | ต้นทุนน้ำมันที่ปิดแล้ว เป็นส่วนหนึ่งของต้นทุนรวม |
| `cost_is_settled` | boolean |  | ไม่ได้ | ปิดเที่ยวและรับรู้ต้นทุนแล้ว |
| `cost_basis` | text |  | ไม่ได้ | ที่มาของสูตรต้นทุน แยกสมมติฐานกับราคาน้ำมันอ้างอิง |
| `is_synthetic` | boolean |  | ไม่ได้ | True สำหรับระเบียนจำลอง |

## trip_driver_assignments.csv

1 row per driver assigned to one trip

| ฟิลด์ | ชนิด | หน่วย | ว่างได้ | ความหมาย |
|---|---|---|---|---|
| `assignment_id` | text |  | ไม่ได้ | คีย์การมอบหมายคนขับต่อเที่ยว |
| `trip_id` | text |  | ไม่ได้ | รหัสเที่ยวรถที่รวมการกลับศูนย์ประจำ |
| `driver_id` | text |  | ไม่ได้ | รหัสคนขับจำลอง |
| `crew_slot` | integer |  | ไม่ได้ | ตำแหน่งคนขับ 1/2 ในลูกเรือของเที่ยว |
| `reservation_start_at` | ISO8601 timestamp +07:00 |  | ได้ | เริ่มจองเวลาคนขับจริงในแบบจำลอง ถ้ายังไม่เริ่มจะว่าง |
| `reservation_end_at` | ISO8601 timestamp +07:00 |  | ได้ | สิ้นสุดจริงแสดงเมื่อสิ้นสุดก่อน snapshot เท่านั้น |
| `planned_assignment` | boolean |  | ไม่ได้ | การมอบหมายเที่ยวที่ยังไม่เริ่ม ณ snapshot |
| `is_synthetic` | boolean |  | ไม่ได้ | True สำหรับระเบียนจำลอง |

## trip_costs.csv

1 row per cost category per completed trip

| ฟิลด์ | ชนิด | หน่วย | ว่างได้ | ความหมาย |
|---|---|---|---|---|
| `cost_id` | text |  | ไม่ได้ | คีย์ต้นทุนต่อเที่ยวและหมวด |
| `trip_id` | text |  | ไม่ได้ | รหัสเที่ยวรถที่รวมการกลับศูนย์ประจำ |
| `category` | text |  | ไม่ได้ | หมวดต้นทุน ดูรายชื่อ 6 หมวดใน README |
| `amount_thb` | decimal | THB | ไม่ได้ | จำนวนเงินในหมวดต้นทุนของเที่ยวที่ปิดแล้ว |
| `recognized_at` | ISO8601 timestamp +07:00 |  | ไม่ได้ | เวลาจบเที่ยวและรับรู้ต้นทุน |
| `basis` | text |  | ไม่ได้ | วิธีได้มาของจำนวนเงินในแบบจำลอง |
| `is_synthetic` | boolean |  | ไม่ได้ | True สำหรับระเบียนจำลอง |

## shipment_legs.csv

1 row per shipment carried on one trip; retry is another last-mile trip

| ฟิลด์ | ชนิด | หน่วย | ว่างได้ | ความหมาย |
|---|---|---|---|---|
| `shipment_leg_id` | text |  | ไม่ได้ | คีย์เชื่อม shipment และเที่ยวที่รับขนจริงหรือวางแผนไว้ |
| `shipment_id` | text |  | ไม่ได้ | รหัสรายการส่งสินค้า หนึ่งรายการอาจมีหลายกล่อง |
| `trip_id` | text |  | ไม่ได้ | รหัสเที่ยวรถที่รวมการกลับศูนย์ประจำ |
| `leg_type` | text |  | ไม่ได้ | ช่วง LINEHAUL หรือ LAST_MILE |
| `delivery_attempt` | integer |  | ได้ | ครั้งที่ลองส่งในเที่ยว last mile; null สำหรับ linehaul |
| `allocated_freight_cost_thb` | decimal | THB | ได้ | ต้นทุนทั้งเที่ยวที่แบ่งให้ shipment ตามน้ำหนัก |
| `allocation_basis` | text |  | ไม่ได้ | หลักเกณฑ์แบ่งต้นทุนเที่ยวให้ shipment |
| `is_synthetic` | boolean |  | ไม่ได้ | True สำหรับระเบียนจำลอง |

## vehicle_daily.csv

1 row per vehicle per calendar day

| ฟิลด์ | ชนิด | หน่วย | ว่างได้ | ความหมาย |
|---|---|---|---|---|
| `vehicle_day_id` | text |  | ไม่ได้ | คีย์รถหนึ่งคันต่อวัน |
| `vehicle_id` | text |  | ไม่ได้ | รหัสรถจำลอง |
| `date` | ISO8601 date |  | ไม่ได้ | วันที่ปฏิทิน ค.ศ. |
| `available_hours` | decimal | hours | ไม่ได้ | 24 ชั่วโมงลบช่วง maintenance ของวันนั้น |
| `occupied_hours` | integer | hours | ไม่ได้ | เวลาครอบครองรถรวมพักปลายทาง ไม่ใช่ชั่วโมงเครื่องยนต์ |
| `departure_count` | integer |  | ไม่ได้ | จำนวนเที่ยวที่ออกเดินทางจริงในวันนั้น |
| `is_active` | boolean |  | ไม่ได้ | มีเวลาครอบครองรถมากกว่า 0 ชั่วโมงในวันนั้น รวมเที่ยวต่อเนื่องข้ามวัน |
| `maintenance_hours` | integer | hours | ไม่ได้ | เวลาที่รถไม่พร้อมใช้งานจาก maintenance ในวันนั้น |
| `occupied_definition` | text |  | ไม่ได้ | นิยามชั่วโมงครอบครองที่รวมพัก/กลับรถ |
| `is_synthetic` | boolean |  | ไม่ได้ | True สำหรับระเบียนจำลอง |
