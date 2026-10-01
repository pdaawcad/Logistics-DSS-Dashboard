"""Serialize existing source tables for the browser; no warehouse/mining stage."""
import csv, json
from pathlib import Path
root = Path(__file__).resolve().parent
source = root.parent / 'data'
numeric = {'weight_kg','volume_m3','parcel_count','customer_charge_thb','delay_minutes','recognized_transport_cost_thb','customer_rating','delivery_attempt_count','actual_round_trip_km','actual_outbound_km','driving_hours','actual_fuel_litres','planned_round_trip_km','planned_freight_cost_thb','actual_freight_cost_thb','actual_fuel_cost_thb','shipment_count','load_weight_kg','load_volume_m3','latitude','longitude','standard_outbound_km','standard_return_km','planned_truck_outbound_hours','target_booking_share','experience_years','prior_safety_score','capacity_kg','capacity_m3','gross_vehicle_weight_kg','baseline_km_per_litre','amount_thb','allocated_freight_cost_thb','available_hours','occupied_hours','maintenance_hours','departure_count'}
def table(name):
    with (source / (name+'.csv')).open(encoding='utf-8-sig',newline='') as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        for k,v in row.items():
            if v == '': row[k] = None
            elif v in ('True','False'): row[k] = v == 'True'
            elif k in numeric: row[k] = float(v)
    keys = list(rows[0])
    return {'columns':keys,'rows':[[r[k] for k in keys] for r in rows]}
names = ['shipments','trips','vehicles','drivers','hubs','routes','vehicle_models','trip_costs','trip_driver_assignments','vehicle_daily','sources','vehicle_maintenance']
data = {n:table(n) for n in names}
data['meta'] = json.loads((source/'summary.json').read_text(encoding='utf-8-sig'))
(root/'assets/data.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
details = {n:table(n) for n in ['shipment_events','shipment_legs']}
(root/'assets/details.json').write_text(json.dumps(details,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
boundary_source = root.parent / 'data/reference/natural_earth_countries.geojson'
if boundary_source.exists():
    countries = json.loads(boundary_source.read_text(encoding='utf-8-sig'))
    near = [f for f in countries['features'] if f['properties']['ADMIN'] in ['Thailand','Laos','Cambodia','Myanmar','Vietnam','Malaysia']]
    for f in near: f['properties'] = {'name':f['properties']['ADMIN']}
    (root/'assets/boundaries.json').write_text(json.dumps({'type':'FeatureCollection','features':near},separators=(',',':')),encoding='utf-8')
elif not (root/'assets/boundaries.json').exists():
    raise FileNotFoundError('Keep the supplied assets/boundaries.json, or add Natural Earth source to data/reference/natural_earth_countries.geojson')
print('Dashboard data ready:', (root/'assets/data.json').stat().st_size, 'bytes')
