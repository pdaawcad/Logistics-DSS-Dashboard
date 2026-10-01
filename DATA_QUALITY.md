# ผลตรวจคุณภาพข้อมูลจำลอง

ข้อมูลนี้เป็นข้อมูลจำลอง ไม่ใช่ผลการดำเนินงานจริงของบริษัทขนส่ง

ผ่านการตรวจ 28 เงื่อนไข และจำนวนแถว CSV ตรงกับ summary.json ทุกตาราง

| เงื่อนไข | ผล | รายละเอียด |
|---|---|---|
| unique_shipments | PASS | 12000 |
| unique_trips | PASS | 1653 |
| unique_vehicles | PASS | 46 |
| unique_drivers | PASS | 70 |
| unique_customers | PASS | 300 |
| unique_hubs | PASS | 11 |
| unique_routes | PASS | 20 |
| unique_shipment_events | PASS | 83786 |
| unique_shipment_legs | PASS | 24152 |
| shipment_count | PASS | 12000 |
| chiangmai_largest | PASS | {'H_CNX': 4200, 'H_BKK': 1800, 'H_SSK': 840, 'H_KSN': 960, 'H_KKC': 1200, 'H_NMA': 720, 'H_RET': 600, 'H_UTH': 720, 'H_RYG': 480, 'H_LPT': 480} |
| shipment_foreign_keys | PASS | customers, hubs, routes |
| leg_foreign_keys | PASS | shipment-trip links |
| event_foreign_keys | PASS | shipment, hub, trip |
| no_future_events | PASS | events censored at snapshot |
| no_future_actuals | PASS | future timestamps blank |
| capacity_constraints | PASS | weight and body volume |
| vehicle_no_overlaps | PASS | outbound plus empty return reserved |
| vehicle_rest_gaps | PASS | 12h linehaul / 10h local before reuse; modelling rule, not legal certification |
| maintenance_no_trip_overlap | PASS | unavailable periods respected |
| cancelled_without_legs | PASS | no transport allocation to pre-dispatch cancellation |
| daily_utilization_bounds | PASS | hours denominator explicit |
| cost_settlement_reconciliation | PASS | six categories sum to trip cost |
| allocation_reconciliation | PASS | weights allocated with cent-preserving rounding |
| manifest_weight | PASS | linked cargo = booked truck load |
| fuel_arithmetic | PASS | litres x price benchmark |
| shipment_milestone_order | PASS | booking -> linehaul -> hub -> out for delivery -> delivered |
| otd_null_rules | PASS | unfinished/cancelled not scored on-time |
