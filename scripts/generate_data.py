"""Reproducible synthetic Ubon logistics data. Python standard library only."""
from __future__ import annotations
import calendar, csv, hashlib, heapq, json, math, random, zipfile
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
TZ = timezone(timedelta(hours=7))
START = datetime(2025, 4, 1, tzinfo=TZ)
END = datetime(2025, 9, 30, 23, 59, 59, tzinfo=TZ)
SEED = 20251002
rng = random.Random(SEED)
tables = {}
internal_trips = {}
reservations = defaultdict(list)
maintenance = defaultdict(list)

def stamp(x):
    return x.isoformat(timespec='seconds') if x else None

def visible(x):
    return stamp(x) if x and x <= END else None

def iso(x):
    return datetime.fromisoformat(x) if x else None

def add(name, row):
    tables.setdefault(name, []).append(row)
    return row

def minute(x):
    return x.replace(second=0, microsecond=0)

def split_money(total, weights):
    """Largest remainder allocation, so cents reconcile exactly."""
    cents = int(round(total * 100))
    denominator = sum(weights)
    exact = [cents * w / denominator for w in weights]
    base = [math.floor(x) for x in exact]
    for i in sorted(range(len(base)), key=lambda i: exact[i]-base[i], reverse=True)[:cents-sum(base)]:
        base[i] += 1
    return [x / 100 for x in base]

sources = [
    {'source_id':'SRC_OSRM','publisher':'OSRM / OpenStreetMap contributors','title':'Route API','url':'https://project-osrm.org/docs/v5.24.0/api/','reference_period':'retrieved 2026-10-02','used_for':'Driving-network distance benchmark; API car duration, not truck time','limitation':'City-centre coordinates assumed; current map applied to synthetic 2025; car profile does not enforce truck restrictions'},
    {'source_id':'SRC_OSM','publisher':'OpenStreetMap contributors','title':'OpenStreetMap attribution','url':'https://www.openstreetmap.org/copyright','reference_period':'retrieved 2026-10-02','used_for':'Road-network attribution','limitation':'Route estimates are not observed GPS or a historical map snapshot'},
    {'source_id':'SRC_ISUZU','publisher':'ISUZU TRUCKS Thailand','title':'Truck specifications','url':'https://truck.isuzu-tis.com/product','reference_period':'retrieved 2026-10-02','used_for':'NLR GVW 4400 kg; NPR GVW 8500 kg; FTR GVW 15000 kg','limitation':'GVW includes vehicle and cargo. Tare, usable payload, body volume and fuel efficiency are simulation assumptions; not a 2025 configuration certification'},
    {'source_id':'SRC_NCA_CNX','publisher':'Nakhonchai Air','title':'Ubon Ratchathani - Chiang Mai route','url':'https://www.nakhonchaiair.com/ncaweb/th/route/25','reference_period':'page updated 2026-02-09; retrieved 2026-10-02','used_for':'Cross-check only: operator route 1043 km; published route detail 13h15; actual timetable includes longer journeys','limitation':'Passenger-bus route, different from OSRM road path; neither value is asserted as measured truck travel time'},
    {'source_id':'SRC_THP','publisher':'Thailand Post','title':'Domestic EMS delivery standard','url':'https://www.thailandpost.co.th/un/article_detail/faq/94/735','reference_period':'retrieved 2026-10-02','used_for':'Market context: 1-2 working-day benchmark, with cutoffs and remote-area exceptions','limitation':'This dataset uses its own 1/2/3 calendar-day SLA. No Thailand Post tariffs or service guarantees are applied to this fictional operator'},
    {'source_id':'SRC_TMD','publisher':'Thai Meteorological Department','title':'Monsoon-season context','url':'https://tmd.go.th/climate/generalizedmonsoonindex','reference_period':'general seasonal context; retrieved 2026-10-02','used_for':'Broad May-October monsoon context','limitation':'Daily rain, forecast error, traffic and delay probabilities are simulated, not actual 2025 weather records'},
]
fuel_urls = {
    4:'https://www.eppo.go.th/index.php/th/petroleum/gas/link-erc-pipeline/item/download/25562_1ecf6385226f1e42d3be78141172c29d',
    5:'https://www.eppo.go.th/epposite/index.php/th/corporate-eppo/ethics/item/download/25622_a3b8192b151aa50e11310896c668961f',
    6:'https://www.eppo.go.th/index.php/en/component/k2/item/download/25808_6d042169850424dfa4b4e6a255b7118d',
    7:'https://www.eppo.go.th/index.php/en/component/k2/item/download/25810_3395fd2f21d5f639850a5a9ce1803baa',
    8:'https://www.eppo.go.th/index.php/en/component/k2/item/download/25973_488d069ba4cc4b95a73d598248598d67',
    9:'https://www.eppo.go.th/index.php/en/component/k2/item/download/25989_c6db1ca5ad952ca88cf1ad5863afc8f7',
}
for month, url in fuel_urls.items():
    sid = f'SRC_EPPO_{month:02}'
    sources.append({'source_id':sid,'publisher':'Energy Policy and Planning Office (EPPO)','title':f'Retail fuel price comparison 2025-{month:02}','url':url,'reference_period':f'2025-{month:02}','used_for':'Thailand diesel reference 31.94 THB/litre','limitation':'A report reference price, not a daily observed pump-price series or a monthly average'})
    add('fuel_price_reference', {'fuel_price_id':f'FUEL2025{month:02}','reference_month':f'2025-{month:02}','fuel_type':'Diesel','benchmark_thb_per_litre':31.94,'source_id':sid,'is_observed_daily_price':False})
tables['sources'] = sources

route_refs = json.loads((DATA/'reference/route_benchmarks.json').read_text(encoding='utf-8-sig'))
assert len(route_refs) == 10
add('hubs', {'hub_id':'H_UBP','hub_name':'ศูนย์จำลองอุบลราชธานี','province':'อุบลราชธานี','region':'Northeast','latitude':15.2448,'longitude':104.8575,'coordinates_basis':'Assumed approximate city centre, not a real warehouse'})
for ref in route_refs:
    code = ref['code']
    hid = 'H_'+code
    add('hubs', {'hub_id':hid,'hub_name':'ศูนย์จำลอง'+ref['province'],'province':ref['province'],'region':ref['region'],'latitude':ref['latitude'],'longitude':ref['longitude'],'coordinates_basis':'Assumed approximate city centre, not a real warehouse'})
    add('routes', {'route_id':'R_'+code,'route_kind':'LINEHAUL','origin_hub_id':'H_UBP','destination_hub_id':hid,'destination_province':ref['province'],'destination_region':ref['region'],'standard_outbound_km':ref['outbound_km'],'standard_return_km':ref['return_km'],'osrm_car_duration_hours':ref['car_duration_hours'],'planned_truck_outbound_hours':round(ref['outbound_km']/62 + 0.75,3),'target_booking_share':ref['destination_share'],'distance_basis':'OSRM current car road-network estimate','distance_source_id':'SRC_OSRM','route_api_url':ref['reference_url'],'distance_reference_date':'2026-10-02'})
    add('routes', {'route_id':'L_'+code,'route_kind':'LAST_MILE','origin_hub_id':hid,'destination_hub_id':hid,'destination_province':ref['province'],'destination_region':ref['region'],'standard_outbound_km':None,'standard_return_km':None,'osrm_car_duration_hours':None,'planned_truck_outbound_hours':None,'target_booking_share':None,'distance_basis':'Simulated hub loop: 20 + 1.8 x stops km; no real customer addresses','distance_source_id':None,'route_api_url':None,'distance_reference_date':None})
routes = {x['route_id']:x for x in tables['routes']}

models = {
    'NLR':{'vehicle_type':'4-wheel box truck','gross_vehicle_weight_kg':4400,'assumed_tare_kg':2600,'capacity_kg':1800,'capacity_m3':10,'baseline_km_per_litre':8.8,'maintenance_thb_per_km':1.1,'depreciation_thb_per_km':0.9,'crew_hourly_cost_thb':70},
    'NPR':{'vehicle_type':'6-wheel medium box truck','gross_vehicle_weight_kg':8500,'assumed_tare_kg':4500,'capacity_kg':4000,'capacity_m3':20,'baseline_km_per_litre':7.5,'maintenance_thb_per_km':1.7,'depreciation_thb_per_km':1.3,'crew_hourly_cost_thb':85},
    'FTR':{'vehicle_type':'6-wheel large box truck','gross_vehicle_weight_kg':15000,'assumed_tare_kg':7000,'capacity_kg':8000,'capacity_m3':40,'baseline_km_per_litre':5.5,'maintenance_thb_per_km':2.5,'depreciation_thb_per_km':1.9,'crew_hourly_cost_thb':95},
}
tables['vehicle_models'] = [{'model_code':k,**v,'gvw_source_id':'SRC_ISUZU','other_parameters_basis':'SIMULATED_ASSUMPTION'} for k,v in models.items()]
fleet = {}
crew_by_vehicle = {}
available = {}
driver_counter = 0
def create_vehicle(model, home, n, kind):
    global driver_counter
    vid = f'V{n:03}'
    row = add('vehicles', {'vehicle_id':vid,'vehicle_label':f'รถจำลอง-{n:03}','model_code':model,'operation_type':kind,'home_hub_id':home,'fuel_type':'Diesel','commissioned_date':'2024-01-01','is_synthetic':True})
    fleet[vid] = row
    available[vid] = START
    crew_by_vehicle[vid] = []
    for seat in range(2 if kind=='LINEHAUL' else 1):
        driver_counter += 1
        did = f'D{driver_counter:03}'
        crew_by_vehicle[vid].append(did)
        add('drivers', {'driver_id':did,'driver_name':f'คนขับจำลอง-{driver_counter:03}','home_hub_id':home,'assigned_vehicle_id':vid,'experience_years':rng.randint(1,18),'prior_safety_score':round(rng.uniform(70,99),1),'prior_fuel_skill_factor':round(rng.uniform(0.90,1.08),3),'licence_type':'Simulated appropriate truck licence','is_synthetic':True})
    for m in (5,8):
        day = 1 + ((n*7) % 23)
        a = datetime(2025,m,day,tzinfo=TZ)
        b = a+timedelta(days=2)
        maintenance[vid].append((a,b))
        add('vehicle_maintenance', {'maintenance_id':f'M{n:03}{m:02}','vehicle_id':vid,'unavailable_from':stamp(a),'unavailable_until':stamp(b),'maintenance_type':'Scheduled service','is_synthetic':True})
for n in range(1,25):
    create_vehicle('NPR' if n<=12 else 'FTR','H_UBP',n,'LINEHAUL')
next_vehicle=25
for ref in route_refs:
    for j in range(4 if ref['code']=='CNX' else 2):
        create_vehicle('NLR','H_'+ref['code'],next_vehicle,'LAST_MILE')
        next_vehicle+=1
drivers = {x['driver_id']:x for x in tables['drivers']}
for i, ref in enumerate(route_refs):
    for j in range(30):
        n=i*30+j+1
        add('customers', {'customer_id':f'C{n:04}','customer_name':f'ลูกค้าจำลอง-{n:04}','customer_type':rng.choices(['B2B','B2C','VIP'],[0.65,0.30,0.05])[0],'province':ref['province'],'destination_hub_id':'H_'+ref['code'],'is_synthetic':True})
customers_by_hub = defaultdict(list)
for x in tables['customers']:
    customers_by_hub[x['destination_hub_id']].append(x['customer_id'])

condition_map = {}
day = START.date()
while day <= END.date():
    add('calendar', {'date_key':int(day.strftime('%Y%m%d')),'date':day.isoformat(),'year':day.year,'quarter':(day.month-1)//3+1,'month':day.month,'day':day.day,'iso_weekday':day.isoweekday(),'is_weekend':day.weekday()>=5,'is_campaign_day':day.day==day.month or date(2025,4,12)<=day<=date(2025,4,16),'is_monsoon_context':day>=date(2025,5,15)})
    for ref in route_refs:
        wet_prob = {4:0.15,5:0.32,6:0.42,7:0.48,8:0.57,9:0.60}[day.month]
        rain = rng.random()<wet_prob
        forecast = rain if rng.random()>0.15 else not rain
        traffic = rng.choices([1,2,3],[0.25,0.55,0.20])[0]
        row = add('route_conditions', {'condition_id':day.strftime('%Y%m%d')+'_'+ref['code'],'date':day.isoformat(),'route_id':'R_'+ref['code'],'traffic_forecast_level':traffic,'rain_forecast_flag':forecast,'observed_rain_flag':rain,'forecast_available_at':stamp(datetime.combine(day,datetime.min.time(),TZ)),'observation_available_at':stamp(datetime.combine(day,datetime.min.time(),TZ)+timedelta(hours=23)),'season_context_source_id':'SRC_TMD','is_synthetic':True})
        condition_map[(day,'R_'+ref['code'])] = row
    day += timedelta(days=1)

def choose_vehicle(candidates, earliest, duration, load_kg, load_m3):
    choices=[]
    for vid in candidates:
        model=models[fleet[vid]['model_code']]
        if load_kg>model['capacity_kg'] or load_m3>model['capacity_m3']:
            continue
        start=max(earliest,available[vid])
        if fleet[vid]['operation_type']=='LAST_MILE':
            start=delivery_window(start)
        while True:
            hit=next(((a,b) for a,b in maintenance[vid] if start<b and start+duration>a),None)
            if not hit:
                break
            start=hit[1]
            if fleet[vid]['operation_type']=='LAST_MILE':
                start=delivery_window(start)
        choices.append((start,rng.random(),vid))
    assert choices, 'No vehicle with suitable payload'
    start,_,vid=min(choices)
    return vid,start

def make_trip(kind, route_id, planned_start, cargo, attempt=1):
    route=routes[route_id]
    load=round(sum(s['weight_kg'] for s in cargo),3)
    volume=round(sum(s['volume_m3'] for s in cargo),4)
    day_key=min(planned_start.date(),END.date())
    condition=condition_map[(day_key,'R_'+route_id[2:])]
    rain=condition['observed_rain_flag']
    traffic=condition['traffic_forecast_level']
    candidates=[v for v,x in fleet.items() if x['operation_type']==kind and x['home_hub_id']==route['origin_hub_id']]
    if kind=='LINEHAUL':
        km_out=round(route['standard_outbound_km']*rng.uniform(1.00,1.05),3)
        km_back=round(route['standard_return_km']*rng.uniform(1.00,1.03),3)
        drive_out=km_out/rng.uniform(58,65)
        drive_back=km_back/rng.uniform(58,65)
        dwell=12 if km_out>400 else 8
        disruption=rng.random() < 0.055+0.075*rain+0.025*(traffic==3)
        wait_hours=rng.uniform(8,32) if disruption else rng.uniform(0.2,2.2)
        outbound_hours=drive_out+0.6+wait_hours
        total_hours=0.5+outbound_hours+dwell+drive_back+0.6
        planned_hours=0.5+route['planned_truck_outbound_hours']+dwell+route['standard_return_km']/62+0.6
    else:
        km_out=round((20+1.8*len(cargo))*rng.uniform(0.90,1.12),3)
        km_back=0
        drive_out=km_out/rng.uniform(24,32)
        drive_back=0
        dwell=0
        wait_hours=rng.uniform(0.2,1.2) + (0.5 if rain else 0)
        outbound_hours=drive_out+0.12*len(cargo)+wait_hours
        total_hours=0.5+outbound_hours
        planned_hours=0.5+km_out/28+0.12*len(cargo)
    duration=timedelta(hours=total_hours)
    vid,reserved_start=choose_vehicle(candidates,planned_start,duration,load,volume)
    model=models[fleet[vid]['model_code']]
    actual_depart=reserved_start+timedelta(minutes=30)
    hub_arrival=actual_depart+timedelta(hours=outbound_hours) if kind=='LINEHAUL' else None
    return_depart=hub_arrival+timedelta(hours=dwell) if hub_arrival else None
    finish=reserved_start+duration
    trip_id=f'T{len(tables.get("trips",[]))+1:05}'
    crew=crew_by_vehicle[vid]
    fuel_skill=sum(drivers[d]['prior_fuel_skill_factor'] for d in crew)/len(crew)
    eff=model['baseline_km_per_litre']*fuel_skill*(1-0.13*load/model['capacity_kg'])*(1-0.025*(traffic-1))*(1-0.04*rain)
    litres=round(km_out/eff+km_back/(model['baseline_km_per_litre']*fuel_skill),3)
    km=round(km_out+km_back,3)
    crew_hours=drive_out+drive_back+0.12*len(cargo)+1
    costs={
        'FUEL':round(litres*31.94,2),
        'DRIVER_AND_ALLOWANCE':round(crew_hours*model['crew_hourly_cost_thb']*len(crew)+(180*len(crew) if kind=='LINEHAUL' and dwell==12 else 0),2),
        'TOLL_ESTIMATE':round(rng.uniform(80,220) if route_id.endswith(('BKK','RYG')) and kind=='LINEHAUL' else 0,2),
        'MAINTENANCE_ACCRUAL':round(km*model['maintenance_thb_per_km'],2),
        'DEPRECIATION_ACCRUAL':round(km*model['depreciation_thb_per_km'],2),
        'HANDLING':round(20*len(cargo) if kind=='LINEHAUL' else 8*len(cargo),2),
    }
    total_cost=round(sum(costs.values()),2)
    settled=finish<=END
    planned_km=round(route['standard_outbound_km']+route['standard_return_km'],3) if kind=='LINEHAUL' else round(20+1.8*len(cargo),3)
    planned_fuel=round(planned_km/model['baseline_km_per_litre']*31.94,2)
    planned_crew_hours=planned_km/(62 if kind=='LINEHAUL' else 28)+0.12*len(cargo)+1
    planned_toll=150 if route_id.endswith(('BKK','RYG')) and kind=='LINEHAUL' else 0
    planned_cost=round(planned_fuel+planned_crew_hours*model['crew_hourly_cost_thb']*len(crew)+planned_km*(model['maintenance_thb_per_km']+model['depreciation_thb_per_km'])+costs['HANDLING']+planned_toll+(180*len(crew) if dwell==12 else 0),2)
    status='PLANNED' if actual_depart>END else ('COMPLETED' if settled else ('RETURNING' if return_depart and return_depart<=END else ('AT_DESTINATION' if hub_arrival and hub_arrival<=END else 'IN_TRANSIT')))
    add('trips', {'trip_id':trip_id,'route_id':route_id,'trip_kind':kind,'vehicle_id':vid,'origin_hub_id':route['origin_hub_id'],'destination_hub_id':route['destination_hub_id'],'condition_id':condition['condition_id'],'planned_departure_at':stamp(planned_start+timedelta(minutes=30)),'planned_completion_at':stamp(planned_start+timedelta(hours=planned_hours)),'actual_departure_at':visible(actual_depart),'actual_destination_arrival_at':visible(hub_arrival),'actual_return_departure_at':visible(return_depart),'actual_completion_at':visible(finish),'trip_status':status,'shipment_count':len(cargo),'load_weight_kg':load,'load_volume_m3':volume,'planned_round_trip_km':planned_km,'actual_round_trip_km':km if settled else None,'actual_outbound_km':km_out if kind=='LINEHAUL' and hub_arrival<=END else (km_out if kind=='LAST_MILE' and settled else None),'driving_hours':round(drive_out+drive_back,3) if settled else None,'actual_fuel_litres':litres if settled else None,'fuel_price_id':f'FUEL2025{min(planned_start.month,9):02}','planned_freight_cost_thb':planned_cost,'actual_freight_cost_thb':total_cost if settled else None,'actual_fuel_cost_thb':costs['FUEL'] if settled else None,'cost_is_settled':settled,'cost_basis':'Synthetic cost model; fuel unit-price benchmark from EPPO','is_synthetic':True})
    available[vid]=finish+timedelta(hours=12 if kind=='LINEHAUL' else 10)
    reservations[vid].append((reserved_start,finish,trip_id))
    for slot,did in enumerate(crew,1):
        add('trip_driver_assignments', {'assignment_id':trip_id+'_'+did,'trip_id':trip_id,'driver_id':did,'crew_slot':slot,'reservation_start_at':visible(reserved_start),'reservation_end_at':visible(finish),'planned_assignment':actual_depart>END,'is_synthetic':True})
    internal_trips[trip_id]={'start':reserved_start,'depart':actual_depart,'arrival':hub_arrival,'return_depart':return_depart,'finish':finish,'cargo':cargo,'cost':total_cost,'costs':costs,'drive_out':drive_out,'drive_back':drive_back,'vehicle':vid}
    if settled:
        for category,amount in costs.items():
            add('trip_costs', {'cost_id':trip_id+'_'+category,'trip_id':trip_id,'category':category,'amount_thb':amount,'recognized_at':stamp(finish),'basis':'Synthetic settlement/accrual; not a real invoice','is_synthetic':True})
    allocated=split_money(total_cost,[s['weight_kg'] for s in cargo])
    for s,amount in zip(cargo,allocated):
        add('shipment_legs', {'shipment_leg_id':f'{s["shipment_id"]}_{trip_id}','shipment_id':s['shipment_id'],'trip_id':trip_id,'leg_type':kind,'delivery_attempt':attempt if kind=='LAST_MILE' else None,'allocated_freight_cost_thb':amount if settled else None,'allocation_basis':'Weight-based, including empty return on linehaul; completed trips only','is_synthetic':True})
    return trip_id

def event(sid, name, when, hub, trip=None):
    if when<=END:
        add('shipment_events', {'event_id':f'E{len(tables.get("shipment_events",[]))+1:07}','shipment_id':sid,'event_type':name,'event_at':stamp(when),'hub_id':hub,'trip_id':trip,'is_synthetic':True})

# 600 manifests x 20 bookings. Province quota follows the user-selected scenario.
route_sequence=[]
for ref in route_refs:
    route_sequence += ['R_'+ref['code']]*round(600*ref['destination_share'])
assert len(route_sequence)==600
rng.shuffle(route_sequence)
departures=[]
for m,count in zip(range(4,10),[70,85,95,110,115,125]):
    for _ in range(count):
        departures.append(datetime(2025,m,rng.randint(1,calendar.monthrange(2025,m)[1]),rng.randint(8,18),rng.choice([0,15,30,45]),tzinfo=TZ))
departures.sort()
pending_local=[]
shipment_internals={}
for n,(planned,route_id) in enumerate(zip(departures,route_sequence)):
    route=routes[route_id]
    hid=route['destination_hub_id']
    cargo=[]
    for j in range(20):
        sid=f'S{n*20+j+1:06}'
        booked=planned-timedelta(hours=rng.uniform(2,5))
        service=rng.choices(['STANDARD','EXPRESS','ECONOMY'],[0.65,0.25,0.10])[0]
        sla=1 if service=='EXPRESS' else (3 if service=='ECONOMY' else (1 if route['standard_outbound_km']<250 else 2))
        promised=datetime.combine(booked.date()+timedelta(days=sla),datetime.min.time(),TZ)+timedelta(hours=18)
        weight=round(max(5,min(180,rng.lognormvariate(4.1,0.65))),2)
        volume=round(weight/rng.uniform(160,300),4)
        cancelled=rng.random()<0.025
        s=add('shipments', {'shipment_id':sid,'customer_id':rng.choice(customers_by_hub[hid]),'origin_hub_id':'H_UBP','destination_hub_id':hid,'route_id':route_id,'created_at':stamp(booked),'service_level':service,'sla_calendar_days':sla,'promised_delivery_at':stamp(promised),'weight_kg':weight,'volume_m3':volume,'parcel_count':max(1,math.ceil(weight/20)),'is_fragile':rng.random()<0.12,'customer_charge_thb':round((70+weight*4+route['standard_outbound_km']*0.20)*({'STANDARD':1,'EXPRESS':1.30,'ECONOMY':0.85}[service]),2),'cancelled_at':stamp(booked+timedelta(hours=1)) if cancelled else None,'linehaul_departure_at':None,'destination_hub_arrival_at':None,'first_out_for_delivery_at':None,'actual_delivery_at':None,'delivery_attempt_count':0,'shipment_status':'CANCELLED' if cancelled else 'ACCEPTED','delay_minutes':None,'is_ontime':None,'is_overdue_open':False,'recognized_transport_cost_thb':0,'all_transport_costs_settled':False,'customer_rating':None,'snapshot_at':stamp(END),'is_synthetic':True})
        shipment_internals[sid]={'row':s,'promise':promised,'delivery':None,'first_out':None,'attempts':[],'linehaul':None,'cancelled':cancelled}
        event(sid,'BOOKED',booked,'H_UBP')
        if cancelled:
            event(sid,'CANCELLED',booked+timedelta(hours=1),'H_UBP')
        else:
            event(sid,'ACCEPTED',booked+timedelta(minutes=10),'H_UBP')
            cargo.append(s)
    if not cargo:
        continue
    tid=make_trip('LINEHAUL',route_id,planned,cargo)
    trip=internal_trips[tid]
    for s in cargo:
        sid=s['shipment_id']
        shipment_internals[sid]['linehaul']=tid
        event(sid,'LOADED_LINEHAUL',trip['start'],'H_UBP',tid)
        event(sid,'DEPARTED_ORIGIN',trip['depart'],'H_UBP',tid)
        event(sid,'ARRIVED_DESTINATION_HUB',trip['arrival'],hid,tid)
    pending_local.append((trip['arrival']+timedelta(hours=1),hid,cargo))

def delivery_window(x):
    x=minute(x)
    if x.hour<8:
        return x.replace(hour=8,minute=0)
    if x.hour>=16:
        return (x+timedelta(days=1)).replace(hour=8,minute=0)
    return x

def last_mile_batches(cargo):
    result=[]
    batch=[]
    kg=m3=0
    for s in cargo:
        if batch and (kg+s['weight_kg']>1800 or m3+s['volume_m3']>10 or len(batch)>=20):
            result.append(batch)
            batch=[]
            kg=m3=0
        batch.append(s)
        kg+=s['weight_kg'];m3+=s['volume_m3']
    if batch:
        result.append(batch)
    return result

local_queue=[]
job_number=0
for earliest,hid,cargo in pending_local:
    for batch in last_mile_batches(cargo):
        job_number+=1
        heapq.heappush(local_queue,(delivery_window(earliest),job_number,hid,batch,1))
while local_queue:
        earliest,_,hid,batch,attempt=heapq.heappop(local_queue)
        tid=make_trip('LAST_MILE','L_'+hid[2:],earliest,batch,attempt=attempt)
        trip=internal_trips[tid]
        failed=[]
        for i,s in enumerate(batch):
            sid=s['shipment_id']
            info=shipment_internals[sid]
            if info['first_out'] is None:
                info['first_out']=trip['depart']
            moment=trip['depart']+(trip['finish']-trip['depart'])*((i+1)/(len(batch)+1))
            event(sid,'OUT_FOR_DELIVERY',trip['depart'],hid,tid)
            success=attempt==2 or rng.random()>=0.06
            info['attempts'].append((trip['depart'],moment,success))
            if success:
                info['delivery']=moment
                event(sid,'DELIVERED',moment,hid,tid)
            else:
                event(sid,'DELIVERY_ATTEMPT_FAILED',moment,hid,tid)
                failed.append(s)
        if failed:
            job_number+=1
            heapq.heappush(local_queue,(delivery_window(trip['finish']+timedelta(hours=24)),job_number,hid,failed,2))

legs_by_ship=defaultdict(list)
for leg in tables['shipment_legs']:
    legs_by_ship[leg['shipment_id']].append(leg)
for sid,info in shipment_internals.items():
    s=info['row']
    legs=legs_by_ship[sid]
    s['recognized_transport_cost_thb']=round(sum(x['allocated_freight_cost_thb'] or 0 for x in legs),2)
    s['all_transport_costs_settled']=bool(legs) and all(x['allocated_freight_cost_thb'] is not None for x in legs)
    if info['cancelled']:
        continue
    trunk=internal_trips[info['linehaul']]
    s['linehaul_departure_at']=visible(trunk['depart'])
    s['destination_hub_arrival_at']=visible(trunk['arrival'])
    s['first_out_for_delivery_at']=visible(info['first_out'])
    s['actual_delivery_at']=visible(info['delivery'])
    s['delivery_attempt_count']=sum(x[1]<=END for x in info['attempts'])
    if s['actual_delivery_at']:
        late=max(0,(info['delivery']-info['promise']).total_seconds()/60)
        s['delay_minutes']=round(late,2)
        s['is_ontime']=late==0
        s['shipment_status']='DELIVERED'
        s['customer_rating']=round(max(1,min(5,rng.gauss(4.5 if late==0 else 3.4,0.45))),1)
    else:
        s['shipment_status']='OUT_FOR_DELIVERY' if s['first_out_for_delivery_at'] else ('AT_DESTINATION_HUB' if s['destination_hub_arrival_at'] else ('IN_TRANSIT' if s['linehaul_departure_at'] else 'ACCEPTED'))
        observed_attempts=[a for a in info['attempts'] if a[0]<=END]
        if observed_attempts and not observed_attempts[-1][2] and observed_attempts[-1][1]<=END:
            s['shipment_status']='AWAITING_REDELIVERY'
        s['is_overdue_open']=info['promise']<END
tables['shipment_events'].sort(key=lambda x:(x['shipment_id'],x['event_at'],x['event_id']))
tables['trips'].sort(key=lambda x:x['trip_id'])

# Explicit daily denominator. Occupancy includes driving, service and destination dwell.
def overlap_hours(a,b,c,d):
    return max(0,(min(b,d)-max(a,c)).total_seconds()/3600)
day=START.date()
while day<=END.date():
    a=datetime.combine(day,datetime.min.time(),TZ);b=min(a+timedelta(days=1),END+timedelta(seconds=1))
    for vid in fleet:
        down=sum(overlap_hours(x,y,a,b) for x,y in maintenance[vid])
        busy=sum(overlap_hours(x,min(y,END),a,b) for x,y,_ in reservations[vid] if x<=END)
        departures_count=sum(a<=internal_trips[t]['depart']<b and internal_trips[t]['depart']<=END for _,_,t in reservations[vid])
        add('vehicle_daily', {'vehicle_day_id':vid+'_'+day.strftime('%Y%m%d'),'vehicle_id':vid,'date':day.isoformat(),'available_hours':round((b-a).total_seconds()/3600-down,4),'occupied_hours':round(busy,4),'departure_count':departures_count,'is_active':busy>0,'maintenance_hours':round(down,4),'occupied_definition':'Reserved trip time including dwell and empty return; not engine-on hours','is_synthetic':True})
    day+=timedelta(days=1)

# Independent integrity checks on actual output semantics.
checks=[]
def check(name, ok, detail):
    checks.append({'check':name,'passed':bool(ok),'detail':detail})
    if not ok:
        raise ValueError(name+': '+str(detail))
for table,key in [('shipments','shipment_id'),('trips','trip_id'),('vehicles','vehicle_id'),('drivers','driver_id'),('customers','customer_id'),('hubs','hub_id'),('routes','route_id'),('shipment_events','event_id'),('shipment_legs','shipment_leg_id')]:
    values=[x[key] for x in tables[table]]
    check('unique_'+table,len(values)==len(set(values)),len(values))
check('shipment_count',len(tables['shipments'])==12000,len(tables['shipments']))
bookings=Counter(s['destination_hub_id'] for s in tables['shipments'])
delivered=Counter(s['destination_hub_id'] for s in tables['shipments'] if s['shipment_status']=='DELIVERED')
check('chiangmai_largest',bookings['H_CNX']==4200 and max(delivered,key=delivered.get)=='H_CNX',dict(bookings))
hub_ids={x['hub_id'] for x in tables['hubs']};cust_ids={x['customer_id'] for x in tables['customers']};trip_ids={x['trip_id'] for x in tables['trips']};ship_ids=set(shipment_internals)
check('shipment_foreign_keys',all(s['customer_id'] in cust_ids and s['origin_hub_id'] in hub_ids and s['destination_hub_id'] in hub_ids and s['route_id'] in routes for s in tables['shipments']),'customers, hubs, routes')
check('leg_foreign_keys',all(x['shipment_id'] in ship_ids and x['trip_id'] in trip_ids for x in tables['shipment_legs']),'shipment-trip links')
check('event_foreign_keys',all(x['shipment_id'] in ship_ids and x['hub_id'] in hub_ids and (x['trip_id'] is None or x['trip_id'] in trip_ids) for x in tables['shipment_events']),'shipment, hub, trip')
check('no_future_events',all(iso(x['event_at'])<=END for x in tables['shipment_events']),'events censored at snapshot')
check('no_future_actuals',all(not value or iso(value)<=END for t in tables['trips'] for key,value in t.items() if key.startswith('actual_') and key.endswith('_at')),'future timestamps blank')
check('capacity_constraints',all(t['load_weight_kg']<=models[fleet[t['vehicle_id']]['model_code']]['capacity_kg'] and t['load_volume_m3']<=models[fleet[t['vehicle_id']]['model_code']]['capacity_m3'] for t in tables['trips']),'weight and body volume')
check('vehicle_no_overlaps',all(all(x[1]<=y[0] for x,y in zip(sorted(items),sorted(items)[1:])) for items in reservations.values()),'outbound plus empty return reserved')
check('vehicle_rest_gaps',all(all(x[1]+timedelta(hours=12 if fleet[v]['operation_type']=='LINEHAUL' else 10)<=y[0] for x,y in zip(sorted(items),sorted(items)[1:])) for v,items in reservations.items()),'12h linehaul / 10h local before reuse; modelling rule, not legal certification')
check('maintenance_no_trip_overlap',all(not (a<y and b>x) for v,items in reservations.items() for a,b,_ in items for x,y in maintenance[v]),'unavailable periods respected')
check('cancelled_without_legs',all(not legs_by_ship[sid] for sid,i in shipment_internals.items() if i['cancelled']),'no transport allocation to pre-dispatch cancellation')
check('daily_utilization_bounds',all(-0.001<=r['occupied_hours']<=r['available_hours']+0.001<=24.001 for r in tables['vehicle_daily']),'hours denominator explicit')
cost_by_trip=defaultdict(float);allocation_by_trip=defaultdict(float);manifest_by_trip=defaultdict(list)
for c in tables['trip_costs']:cost_by_trip[c['trip_id']]+=c['amount_thb']
for leg in tables['shipment_legs']:
    allocation_by_trip[leg['trip_id']]+=leg['allocated_freight_cost_thb'] or 0
    manifest_by_trip[leg['trip_id']].append(shipment_internals[leg['shipment_id']]['row'])
check('cost_settlement_reconciliation',all(abs(cost_by_trip[t['trip_id']]-(t['actual_freight_cost_thb'] or 0))<0.005 for t in tables['trips']),'six categories sum to trip cost')
check('allocation_reconciliation',all(abs(allocation_by_trip[t['trip_id']]-(t['actual_freight_cost_thb'] or 0))<0.005 for t in tables['trips']),'weights allocated with cent-preserving rounding')
check('manifest_weight',all(abs(sum(s['weight_kg'] for s in manifest_by_trip[t['trip_id']])-t['load_weight_kg'])<0.001 for t in tables['trips']),'linked cargo = booked truck load')
check('fuel_arithmetic',all(not t['cost_is_settled'] or abs(round(t['actual_fuel_litres']*31.94,2)-t['actual_fuel_cost_thb'])<0.005 for t in tables['trips']),'litres x price benchmark')
check('shipment_milestone_order',all(not s['actual_delivery_at'] or iso(s['created_at'])<=iso(s['linehaul_departure_at'])<=iso(s['destination_hub_arrival_at'])<=iso(s['first_out_for_delivery_at'])<=iso(s['actual_delivery_at']) for s in tables['shipments']),'booking -> linehaul -> hub -> out for delivery -> delivered')
check('otd_null_rules',all((s['is_ontime'] is None)==(s['shipment_status']!='DELIVERED') for s in tables['shipments']),'unfinished/cancelled not scored on-time')

summary_month=[]
for month in range(4,10):
    ss=[s for s in tables['shipments'] if iso(s['created_at']).month==month]
    dd=[s for s in ss if s['shipment_status']=='DELIVERED']
    oo=sum(s['is_ontime'] for s in dd)
    summary_month.append({'booking_month':f'2025-{month:02}','bookings':len(ss),'delivered':len(dd),'cancelled':sum(s['shipment_status']=='CANCELLED' for s in ss),'open':sum(s['shipment_status'] not in ('DELIVERED','CANCELLED') for s in ss),'on_time':oo,'otd_percent':round(100*oo/len(dd),2) if dd else None,'recognized_transport_cost_thb':round(sum(s['recognized_transport_cost_thb'] for s in ss),2)})
summary_dest=[]
for ref in route_refs:
    ss=[s for s in tables['shipments'] if s['destination_hub_id']=='H_'+ref['code']]
    dd=[s for s in ss if s['shipment_status']=='DELIVERED']
    summary_dest.append({'province':ref['province'],'bookings':len(ss),'booking_share_percent':round(100*len(ss)/12000,2),'delivered':len(dd),'on_time':sum(s['is_ontime'] for s in dd),'otd_percent':round(100*sum(s['is_ontime'] for s in dd)/len(dd),2),'osrm_outbound_km':ref['outbound_km']})
dd=[s for s in tables['shipments'] if s['shipment_status']=='DELIVERED']
summary={'dataset_id':'ubon-logistics-synthetic-v1','seed':SEED,'snapshot_at':stamp(END),'reference_retrieval_date':'2026-10-02','is_synthetic':True,'record_counts':{k:len(v) for k,v in tables.items()},'shipment_status_counts':dict(Counter(s['shipment_status'] for s in tables['shipments'])),'otd_completed_shipments_percent':round(100*sum(s['is_ontime'] for s in dd)/len(dd),2),'overdue_open_shipments':sum(s['is_overdue_open'] for s in tables['shipments']),'total_recognized_transport_cost_thb':round(sum(x['amount_thb'] for x in tables['trip_costs']),2),'months':summary_month,'destinations':summary_dest,'quality_checks':checks}

assumptions={
    'seed':SEED,'period_start':stamp(START),'snapshot_at':stamp(END),'timezone':'Asia/Bangkok (+07:00)',
    'origin':'อุบลราชธานี','destination_shares':{r['province']:r['destination_share'] for r in route_refs},
    'demand_basis':'User-selected scenario: Chiang Mai largest; all destination shares assumed, not market survey data',
    'booking_count':12000,'manifest_count':600,'bookings_per_manifest':20,
    'monthly_manifest_counts':dict(zip(['2025-04','2025-05','2025-06','2025-07','2025-08','2025-09'],[70,85,95,110,115,125])),
    'pre_dispatch_cancel_probability':0.025,'customer_unavailable_first_attempt_probability':0.06,
    'weight_kg':'clip(lognormal(mu=4.1,sigma=0.65),5,180); consignments may contain multiple parcels',
    'volume_m3':'weight / uniform(160,300) kg/m3; not based on carrier dimensional-weight tariffs',
    'sla':'EXPRESS 1 calendar day; STANDARD 1 day if <250 km else 2 days; ECONOMY 3 days. Deadline 18:00 +07. Operates seven days; no holiday exclusion. Market context only from EMS, not an EMS SLA.',
    'last_mile_km':'(20 + 1.8 x stop count) x uniform(0.90,1.12), including return to local hub; fully assumed',
    'linehaul_distance':'OSRM outbound/return benchmark multiplied by synthetic detour factor; not historical 2025 measurement',
    'linehaul_empty_return':True,'linehaul_crew_size':2,'last_mile_crew_size':1,
    'vehicle_reuse_rest_hours':{'LINEHAUL':12,'LAST_MILE':10},
    'route_drive_speed_kmh':{'LINEHAUL':'uniform(58,65)','LAST_MILE':'uniform(24,32)'},
    'destination_dwell_hours':'12 if >400 km, otherwise 8; off-duty/dwell between outbound and return',
    'linehaul_disruption_probability':'0.055 + 0.075*observed_rain + 0.025*(traffic_forecast_level==3)',
    'linehaul_wait_hours':'uniform(8,32) when disruption; otherwise uniform(0.2,2.2)',
    'rain_probabilities':{'04':0.15,'05':0.32,'06':0.42,'07':0.48,'08':0.57,'09':0.60},
    'rain_forecast_correct_probability':0.85,'traffic_level_probabilities':[0.25,0.55,0.20],
    'fuel_efficiency':'baseline_km_per_litre * prior_fuel_skill_factor * (1-0.13*load_ratio)*(1-0.025*(traffic-1))*(1-0.04*rain); return empty uses baseline * skill',
    'vehicle_models':models,
    'driver_allowance':'crew hours=(outbound+return driving hours)+0.12*shipment_count+1; cost=crew hours*assumed crew hourly cost*crew size; add 180 THB/crew for long overnight trip. Not observed wages.',
    'toll':'uniform(80,220) THB for BKK/RYG linehaul, otherwise zero; assumed budget, not official toll quotation',
    'handling':'20 THB per consignment on linehaul, 8 THB per consignment on each last-mile attempt',
    'recognition':'All costs recognized on trip completion. Delivered shipments can have unsettled empty-return costs. No future actuals in snapshot.',
    'allocation':'Allocate full completed-trip cost by consignment weight with cent-preserving largest remainder; include empty return; never copy full trip cost onto every shipment.',
    'fleet_occupied_hours':'Vehicle reserved time including travel, service and destination dwell. Available hours=24-maintenance; not engine-on utilization.',
    'personal_data':'All customer/driver names and identifiers are fictional; no real plates, phone numbers, home addresses or GPS logs',
    'model_validation_limit':'Synthetic train/test metrics demonstrate method only. Not evidence of accuracy on real logistics operations.',
}

DATA.mkdir(parents=True,exist_ok=True)
for name,rows in tables.items():
    with (DATA/(name+'.csv')).open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]))
        writer.writeheader();writer.writerows(rows)
(DATA/'logistics_data.json').write_text(json.dumps({'metadata':assumptions,'tables':tables},ensure_ascii=False,separators=(',',':')),encoding='utf-8')
(DATA/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
(DATA/'assumptions.json').write_text(json.dumps(assumptions,ensure_ascii=False,indent=2),encoding='utf-8')

grain={
    'shipments':'1 row per booked consignment, not per parcel or truck trip',
    'trips':'1 row per vehicle tour including return to home hub; linehaul or last mile',
    'shipment_legs':'1 row per shipment carried on one trip; retry is another last-mile trip',
    'shipment_events':'1 row per observed synthetic milestone as of snapshot',
    'trip_driver_assignments':'1 row per driver assigned to one trip',
    'trip_costs':'1 row per cost category per completed trip',
    'vehicle_daily':'1 row per vehicle per calendar day',
    'vehicle_maintenance':'1 row per vehicle unavailability interval',
    'vehicle_models':'1 row per model with referenced GVW and assumed operational parameters',
    'vehicles':'1 row per fictional physical vehicle',
    'drivers':'1 row per fictional driver with prior profile, not outcomes from this dataset',
    'customers':'1 row per fictional customer',
    'hubs':'1 row per fictional hub in a real province',
    'routes':'1 row per outbound linehaul lane or local delivery loop',
    'calendar':'1 row per calendar date in the booking period',
    'route_conditions':'1 row per date and linehaul lane; forecasts separate from observations',
    'fuel_price_reference':'1 row per report month; not daily actuals',
    'sources':'1 row per public reference source',
}
descriptions={
    'shipment_id':'รหัสรายการส่งสินค้า หนึ่งรายการอาจมีหลายกล่อง','trip_id':'รหัสเที่ยวรถที่รวมการกลับศูนย์ประจำ','vehicle_id':'รหัสรถจำลอง','driver_id':'รหัสคนขับจำลอง','customer_id':'รหัสลูกค้าจำลอง','hub_id':'รหัสศูนย์จำลอง','route_id':'รหัสเส้นทางระหว่างศูนย์หรือวงรอบส่งในเมือง','condition_id':'รหัสสภาพเส้นทางรายวัน',
    'created_at':'เวลารับคำสั่งส่งสินค้า','promised_delivery_at':'กำหนดส่งตาม SLA ของบริษัทจำลอง','actual_delivery_at':'เวลาส่งถึงลูกค้าจำลองจริงในแบบจำลอง ค่าว่างหากยังไม่ส่งถึง ณ snapshot','delay_minutes':'นาทีที่ช้ากว่ากำหนด เฉพาะรายการส่งสำเร็จ','is_ontime':'ตรงเวลาหรือไม่ เฉพาะ DELIVERED เท่านั้น','is_overdue_open':'ยังไม่ส่งสำเร็จและเลยกำหนด ณ snapshot','recognized_transport_cost_thb':'ต้นทุนที่รับรู้แล้วจาก legs ของเที่ยวที่ปิดต้นทุน ไม่ใช่ต้นทุนครบทั้งหมดหากยังไม่ settle','all_transport_costs_settled':'ทุกเที่ยวรวมการกลับรถปิดต้นทุนแล้วหรือไม่','customer_charge_thb':'ค่าบริการจำลองที่แจ้งเมื่อรับงาน แยกจากต้นทุนขนส่ง ไม่ถือเป็นรายได้ที่รับรู้แล้ว',
    'standard_outbound_km':'ระยะทางขาออกที่ OSRM คำนวณจากจุดศูนย์เมืองสมมติ','standard_return_km':'ระยะทางกลับที่คำนวณแยก ไม่สมมติว่าต้องเท่าขาออก','actual_round_trip_km':'ระยะทางจำลองเต็มเที่ยวรวมขากลับ แสดงเมื่อเที่ยวเสร็จ','actual_outbound_km':'ระยะทางขาออกที่เสร็จแล้ว สำหรับ last mile คือทั้งวงรอบเมื่อเสร็จ','planned_freight_cost_thb':'งบประมาณต้นทุนเที่ยวจากแบบจำลองก่อนปิดเที่ยว','actual_freight_cost_thb':'ผลรวมต้นทุนจำลอง 6 หมวด ณ ปิดเที่ยว','allocated_freight_cost_thb':'ต้นทุนทั้งเที่ยวที่แบ่งให้ shipment ตามน้ำหนัก','cost_is_settled':'ปิดเที่ยวและรับรู้ต้นทุนแล้ว','reservation_start_at':'เริ่มจองเวลาคนขับจริงในแบบจำลอง ถ้ายังไม่เริ่มจะว่าง','reservation_end_at':'สิ้นสุดจริงแสดงเมื่อสิ้นสุดก่อน snapshot เท่านั้น','planned_assignment':'การมอบหมายเที่ยวที่ยังไม่เริ่ม ณ snapshot',
    'gross_vehicle_weight_kg':'น้ำหนักรวมรถและบรรทุกจากสเปกผู้ผลิต ไม่ใช่น้ำหนักสินค้า','assumed_tare_kg':'น้ำหนักรถรวมตัวถังที่สมมติ','capacity_kg':'GVW ลบน้ำหนักรถสมมติ เป็นเพดานปฏิบัติงานจำลอง','capacity_m3':'ปริมาตรบรรทุกสมมติ ไม่ใช่สเปกตัวถังรับรอง','baseline_km_per_litre':'อัตราประหยัดน้ำมันตั้งต้นสมมติ ไม่ใช่ผลทดสอบผู้ผลิต','fuel_price_id':'คีย์ราคาดีเซล benchmark รายเดือน','benchmark_thb_per_litre':'ค่าราคาดีเซลจากรายงาน EPPO ใช้เป็น benchmark ทั้งเดือน ไม่ใช่ค่าเฉลี่ย','observed_rain_flag':'ฝนที่จำลองว่าทราบภายหลัง ห้ามใช้ทำนายก่อน dispatch','rain_forecast_flag':'ผลพยากรณ์ฝนจำลองที่รู้ล่วงหน้า','prior_safety_score':'คะแนนความปลอดภัยสมมติก่อนช่วงข้อมูล','prior_fuel_skill_factor':'ตัวคูณทักษะประหยัดน้ำมันสมมติก่อนช่วงข้อมูล','customer_rating':'คะแนนลูกค้าหลังส่ง เป็นตัวแปรหลังเหตุการณ์','occupied_hours':'เวลาครอบครองรถรวมพักปลายทาง ไม่ใช่ชั่วโมงเครื่องยนต์','available_hours':'24 ชั่วโมงลบช่วง maintenance ของวันนั้น','source_id':'รหัสแหล่งอ้างอิงสาธารณะ','distance_source_id':'ที่มาของฐานระยะทาง null สำหรับ local loop ซึ่งสมมติทั้งหมด','target_booking_share':'สัดส่วนตามสถานการณ์ที่ผู้ใช้เลือก ไม่ใช่สัดส่วนตลาดจริง',
}
descriptions.update({
    'actual_completion_at':'เวลารถจบเที่ยวและกลับศูนย์ประจำก่อน snapshot','actual_departure_at':'เวลาออกเดินทางจำลองที่เกิดแล้ว','actual_destination_arrival_at':'เวลา linehaul ถึงศูนย์ปลายทาง ไม่ใช่เวลาส่งถึงลูกค้า','actual_fuel_cost_thb':'ต้นทุนน้ำมันที่ปิดแล้ว เป็นส่วนหนึ่งของต้นทุนรวม','actual_fuel_litres':'ลิตรน้ำมันจำลองสำหรับทั้งขาไปและกลับ แสดงเมื่อปิดเที่ยว','actual_return_departure_at':'เวลาออกจากศูนย์ปลายทางกลับอุบล','allocation_basis':'หลักเกณฑ์แบ่งต้นทุนเที่ยวให้ shipment','amount_thb':'จำนวนเงินในหมวดต้นทุนของเที่ยวที่ปิดแล้ว','assigned_vehicle_id':'รถประจำของคนขับจำลอง','assignment_id':'คีย์การมอบหมายคนขับต่อเที่ยว','basis':'วิธีได้มาของจำนวนเงินในแบบจำลอง','cancelled_at':'เวลายกเลิกก่อนบรรทุกสินค้า','category':'หมวดต้นทุน ดูรายชื่อ 6 หมวดใน README','commissioned_date':'วันนำรถเข้ากองรถที่สมมติ','coordinates_basis':'คำอธิบายจุดพิกัดของศูนย์สมมติ','cost_basis':'ที่มาของสูตรต้นทุน แยกสมมติฐานกับราคาน้ำมันอ้างอิง','cost_id':'คีย์ต้นทุนต่อเที่ยวและหมวด','crew_hourly_cost_thb':'ค่าแรง/ต้นทุนคนขับต่อชั่วโมงสมมติ ไม่ใช่อัตราค่าจ้างจริง','crew_slot':'ตำแหน่งคนขับ 1/2 ในลูกเรือของเที่ยว','customer_name':'ชื่อลูกค้าจำลอง ไม่มีข้อมูลส่วนบุคคลจริง','customer_type':'กลุ่มลูกค้าสมมติ B2B/B2C/VIP',
    'date':'วันที่ปฏิทิน ค.ศ.','date_key':'คีย์วันที่จำนวนเต็ม YYYYMMDD','day':'เลขวันที่ในเดือน','delivery_attempt':'ครั้งที่ลองส่งในเที่ยว last mile; null สำหรับ linehaul','delivery_attempt_count':'จำนวนครั้งที่การลองส่งมีผลแล้วก่อน snapshot','departure_count':'จำนวนเที่ยวที่ออกเดินทางจริงในวันนั้น','depreciation_thb_per_km':'ต้นทุนค่าเสื่อมต่อ กม. สมมติ','destination_hub_arrival_at':'เวลาที่ shipment ถึงศูนย์ปลายทาง','destination_hub_id':'คีย์ศูนย์ปลายทาง','destination_province':'จังหวัดปลายทางจริงของสถานการณ์สมมติ','destination_region':'กลุ่มภูมิภาคที่กำหนดในโครงงาน ไม่ใช่พิกัด GPS','distance_basis':'คำอธิบายวิธีเลือกฐานระยะทาง','distance_reference_date':'วันที่ขอ route จากแผนที่ ไม่ใช่วันวิ่งรถ','driver_name':'ชื่อคนขับสมมติ','driving_hours':'ชั่วโมงขับจำลองทั้งเที่ยว ไม่รวมพักปลายทาง แสดงเมื่อปิดเที่ยว','event_at':'เวลา milestone ที่เกิดแล้ว ณ snapshot','event_id':'คีย์ประวัติสถานะ','event_type':'ขั้นตอนการส่งสินค้า ดูสถานะ events ใน README','experience_years':'ประสบการณ์คนขับสมมติ ณ ต้นงวด','first_out_for_delivery_at':'เวลาออกส่งถึงลูกค้าครั้งแรก','forecast_available_at':'เวลาที่พยากรณ์จำลองพร้อมใช้งาน','fuel_type':'ประเภทเชื้อเพลิง Diesel ของกองรถ','gvw_source_id':'คีย์อ้างอิงน้ำหนักรวมรถจากผู้ผลิต','home_hub_id':'ศูนย์ประจำที่รถและคนขับต้องกลับ','hub_name':'ชื่อศูนย์จำลองในจังหวัดจริง',
    'is_active':'มีเวลาครอบครองรถมากกว่า 0 ชั่วโมงในวันนั้น รวมเที่ยวต่อเนื่องข้ามวัน','is_campaign_day':'ธงวันกิจกรรมสมมติ เลขวันเท่ากับเดือนหรือวันที่ 12-16 เม.ย. ไม่ได้แทนปฏิทินวันหยุดราชการ','is_fragile':'ธงสินค้าแตกหักง่ายสมมติ','is_monsoon_context':'ธงบริบทฤดูฝนตั้งแต่ 15 พ.ค. ไม่ใช่ผลสังเกตฝนจริง','is_observed_daily_price':'False เพราะใช้ราคาฐานจากรายงาน ไม่ได้มีราคาซื้อจริงรายวัน','is_synthetic':'True สำหรับระเบียนจำลอง','is_weekend':'เสาร์/อาทิตย์ของปฏิทิน','iso_weekday':'วันในสัปดาห์ 1=จันทร์ ถึง 7=อาทิตย์','latitude':'ละติจูด WGS84 จุดประมาณศูนย์เมืองที่ตั้งสมมติ','leg_type':'ช่วง LINEHAUL หรือ LAST_MILE','licence_type':'สมมติว่ามีใบอนุญาตขับรถที่เหมาะสม ไม่มีเลขใบอนุญาตจริง','limitation':'ข้อจำกัดการนำแหล่งอ้างอิงมาใช้','linehaul_departure_at':'เวลา shipment ออกจากอุบลในเที่ยวระหว่างจังหวัด','load_volume_m3':'ผลรวมปริมาตรสินค้าที่บรรทุกเที่ยวนี้','load_weight_kg':'ผลรวมน้ำหนัก shipment ที่บรรทุกเที่ยวนี้','longitude':'ลองจิจูด WGS84 จุดประมาณศูนย์เมืองที่ตั้งสมมติ',
    'maintenance_hours':'เวลาที่รถไม่พร้อมใช้งานจาก maintenance ในวันนั้น','maintenance_id':'คีย์ช่วงซ่อมบำรุง','maintenance_thb_per_km':'ต้นทุนซ่อมบำรุงเฉลี่ยสมมติต่อ กม.','maintenance_type':'ประเภทการหยุดรถซ่อมบำรุงที่สมมติ','model_code':'รหัสรุ่นรถ NLR/NPR/FTR','month':'เดือนเลข 1-12','observation_available_at':'เวลาที่ผลสังเกตอากาศจำลองถูกทราบ','occupied_definition':'นิยามชั่วโมงครอบครองที่รวมพัก/กลับรถ','operation_type':'หน้าที่รถ LINEHAUL หรือ LAST_MILE','origin_hub_id':'คีย์ศูนย์ต้นทาง','osrm_car_duration_hours':'ระยะเวลาคำนวณ profile รถยนต์ ไม่ใช่เวลาจริงหรือเวลารับประกันรถบรรทุก','other_parameters_basis':'ระบุว่าสเปกปฏิบัติการนอกจาก GVW เป็นสมมติฐาน','parcel_count':'จำนวนกล่องสมมติ ceil(weight/20) ไม่ใช่จำนวน shipment','planned_completion_at':'กำหนดจบเที่ยวตามตารางก่อนทราบผลจริง','planned_departure_at':'กำหนดออกเดินทางเดิม รวมเวลาโหลด 30 นาที','planned_round_trip_km':'ระยะทางแผนทั้งรอบรวมกลับ','planned_truck_outbound_hours':'เวลาแผนสมมติ standard_outbound_km/62 + 0.75 ชั่วโมง','province':'ชื่อจังหวัดจริงที่ใช้ในสถานการณ์','publisher':'ผู้เผยแพร่แหล่งอ้างอิง','quarter':'ไตรมาสปฏิทิน 1-4','recognized_at':'เวลาจบเที่ยวและรับรู้ต้นทุน','reference_month':'เดือนรายงานที่ให้ราคาน้ำมัน benchmark','reference_period':'ช่วงเวลาของแหล่งอ้างอิง แยกจากงวดข้อมูลจำลอง','region':'กลุ่มภูมิภาคในโครงงาน',
    'route_api_url':'คำขอ OSRM ที่ใช้ดึงฐานระยะทางของเส้นทางนี้','route_kind':'เส้นทางระหว่างศูนย์หรือวงรอบส่งในเมือง','season_context_source_id':'คีย์ข้อมูลฤดูกาลทั่วไปจาก TMD ไม่ใช่ข้อมูลฝนรายวัน','service_level':'ระดับบริการสมมติ STANDARD/EXPRESS/ECONOMY','shipment_count':'จำนวน shipment ใน manifest เที่ยวนี้','shipment_leg_id':'คีย์เชื่อม shipment และเที่ยวที่รับขนจริงหรือวางแผนไว้','shipment_status':'สถานะล่าสุด ณ snapshot; ความล่าช้าดู is_ontime/is_overdue_open แยก','sla_calendar_days':'จำนวนวันปฏิทินหลังวันที่รับงานถึงกำหนดส่ง 18:00','snapshot_at':'เวลาตัดข้อมูลคงที่ 2025-09-30T23:59:59+07:00','title':'ชื่อแหล่งอ้างอิง','traffic_forecast_level':'ระดับจราจรพยากรณ์จำลอง 1=เบา 2=ปานกลาง 3=หนาแน่น','trip_kind':'เที่ยวระหว่างจังหวัดหรือเที่ยวส่งถึงลูกค้า','trip_status':'สถานะรถ PLANNED/IN_TRANSIT/AT_DESTINATION/RETURNING/COMPLETED','unavailable_from':'เริ่มช่วงที่รถไม่พร้อมใช้งาน','unavailable_until':'สิ้นสุดช่วงที่รถไม่พร้อมใช้งานแบบ exclusive','url':'URL แหล่งข้อมูลต้นฉบับ','used_for':'สิ่งที่นำแหล่งอ้างอิงมาใช้ในแบบจำลอง','vehicle_day_id':'คีย์รถหนึ่งคันต่อวัน','vehicle_label':'ชื่อรถจำลอง ไม่มีทะเบียนจริง','vehicle_type':'ประเภทและขนาดรถอิงชนิดรุ่นที่เลือก','volume_m3':'ปริมาตรรวมสินค้าของ shipment สมมติ','weight_kg':'น้ำหนักรวมของ shipment สมมติ','year':'ปี ค.ศ.',
})
fk={'shipments':{'customer_id':'customers.customer_id','origin_hub_id':'hubs.hub_id','destination_hub_id':'hubs.hub_id','route_id':'routes.route_id'},'trips':{'vehicle_id':'vehicles.vehicle_id','route_id':'routes.route_id','condition_id':'route_conditions.condition_id','fuel_price_id':'fuel_price_reference.fuel_price_id'},'shipment_legs':{'shipment_id':'shipments.shipment_id','trip_id':'trips.trip_id'},'shipment_events':{'shipment_id':'shipments.shipment_id','trip_id':'trips.trip_id','hub_id':'hubs.hub_id'},'trip_driver_assignments':{'driver_id':'drivers.driver_id','trip_id':'trips.trip_id'},'trip_costs':{'trip_id':'trips.trip_id'},'vehicle_daily':{'vehicle_id':'vehicles.vehicle_id'},'vehicles':{'model_code':'vehicle_models.model_code','home_hub_id':'hubs.hub_id'},'drivers':{'home_hub_id':'hubs.hub_id','assigned_vehicle_id':'vehicles.vehicle_id'},'vehicle_maintenance':{'vehicle_id':'vehicles.vehicle_id'},'routes':{'origin_hub_id':'hubs.hub_id','destination_hub_id':'hubs.hub_id'},'customers':{'destination_hub_id':'hubs.hub_id'}}
dictionary=[]
for name,rows in tables.items():
    for key in rows[0]:
        vals=[r[key] for r in rows]
        example=next((x for x in vals if x is not None),None)
        typ='boolean' if isinstance(example,bool) else ('integer' if isinstance(example,int) else ('decimal' if isinstance(example,float) else 'text'))
        unit=next((u for suffix,u in [('_thb','THB'),('_kg','kg'),('_km','km'),('_m3','m3'),('_hours','hours'),('_minutes','minutes'),('_litres','litres')] if key.endswith(suffix)),None)
        if 'thb_per' in key:unit='THB per unit'
        if key.endswith('_at') or key.endswith(('_from','_until')):typ='ISO8601 timestamp +07:00'
        if key.endswith('_date') or key=='date':typ='ISO8601 date'
        basis='REAL_REFERENCE' if name in ('sources','fuel_price_reference') or (name=='vehicle_models' and key=='gross_vehicle_weight_kg') else ('MAP_ESTIMATE' if name=='routes' and key in ('standard_outbound_km','standard_return_km','osrm_car_duration_hours') else 'SYNTHETIC_OR_DERIVED')
        dictionary.append({'table':name,'column':key,'type':typ,'unit':unit,'nullable':any(x is None for x in vals),'foreign_key':fk.get(name,{}).get(key),'description_th':descriptions.get(key,'ข้อมูลจำลอง/ค่าที่คำนวณ ดูสูตรและความหมายใน README และ assumptions.json'),'provenance':basis,'example':example})
with (DATA/'data_dictionary.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(dictionary[0]));w.writeheader();w.writerows(dictionary)
md=['# พจนานุกรมข้อมูล','', 'CSV เป็น UTF-8 BOM, JSON เป็น UTF-8; CSV ช่องว่าง = null ไม่ใช่ศูนย์; ทุกเวลา +07:00','']
for name,rows in tables.items():
    md += [f'## {name}.csv', '', grain[name], '', '| ฟิลด์ | ชนิด | หน่วย | ว่างได้ | ความหมาย |','|---|---|---|---|---|']
    for d in dictionary:
        if d['table']==name:md.append(f'| `{d["column"]}` | {d["type"]} | {d["unit"] or ""} | {"ได้" if d["nullable"] else "ไม่ได้"} | {d["description_th"]} |')
    md.append('')
(ROOT/'DATA_DICTIONARY.md').write_text('\n'.join(md),encoding='utf-8')
print(json.dumps({'record_counts':summary['record_counts'],'statuses':summary['shipment_status_counts'],'otd_percent':summary['otd_completed_shipments_percent'],'recognized_cost_thb':summary['total_recognized_transport_cost_thb'],'checks_passed':len(checks),'chiangmai_bookings':bookings['H_CNX']},ensure_ascii=False,indent=2))
