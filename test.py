import html
import time

import requests
from core.models.database import SessionLocal
from constants import TAGS
import json
from unittest import TestCase

def get_loc(city, address):
    return requests.get(
        f"https://catalog.api.2gis.com/3.0/items/geocode?q={city}, {address}&fields=items.point,items.geometry.centroid&key=56bb8749-bb8f-4d10-b59a-18b87c7214e1"
    ).json().get('result').get('items')[0].get('point')

class MyTest(TestCase):

    def test_check_api_2gis(self):
        a = requests.get('https://catalog.api.2gis.com/3.0/items/geocode?q=Москва, Никитский переулок, 3&fields=items.point,items.geometry.centroid&key=56bb8749-bb8f-4d10-b59a-18b87c7214e1')
        point = json.loads(a.content).get('result').get('items')[0].get('point')
        b = 0

    def test_check_api_timepad(self):
        session = SessionLocal()
        endpoint = "https://api.timepad.ru/v1/events"
        params = {
            'cities': 'Екатеринбург',
            'limit': 100,
            'fields':'description_html,created_at,starts_at,ends_at,name,description_short,categories,status,url,poster_image,location,organization,age_limit,moderation_status,access_status,registration_data',
            # 'fields': ['created_at', 'location'],
            'starts_at_min': '2023-08-13'
        }
        headers = {"Authorization": "Bearer 4fb2fd4835218409729dae27254b97ea33034a16"}
        responce = requests.get(endpoint, params=params, headers=headers).json()
        responce = responce['values']
        a = 0
        orgs_ids = {}
        for event in responce:
            raw_loc = event.get('location')
            city = raw_loc.get('city')
            address = raw_loc.get('address')
            if not city or not address:
                continue
            ext_id = event.get('id')
            org = event.get('organization') or dict()
            org_name = html.unescape(org.get('name'))
            org_id = session.execute(f"""
                SELECT
                    id
                FROM
                    events
                WHERE
                    ext_id = (:ext_id)::text
            """, {'ext_id': ext_id}).fetchall()
            if not org_id:
                # continue
                # if org_id := session.execute(f"""
                #     SELECT
                #         id
                #     FROM
                #         organizations
                #     WHERE
                #         name = :name and
                #         ext_id = :ext_id::text
                # """, {'name':org_name, 'ext_id': ext_id}).fetchall():
                #     org_id = org_id[0][0]
                org_id = session.execute(f"""
                    INSERT INTO
                        organizations (name, url, image_url, subdomain)
                    VALUES
                        (:name, :url, :img_url, :subdomain)
                    RETURNING 
                        id
                    """, {
                        'name': org_name,
                        'url': org.get('url'),
                        'img_url': (org.get('logo_image') or {}).get('default_url'),
                        'subdomain': org.get('subdomain')
                    }
                ).one()[0]
            orgs_ids[org_name] = org_id
            str_location = city +', ' + address
            loc_event = get_loc(city, address)
            fields = ['name', 'created_at', 'starts_at', 'ends_at', 'description_short', 'description_html',
             'url', 'age_limit', 'moderation_status', 'access_status']
            params = {field: event.get(field) for field in fields}
            params.update({
                'name': html.unescape(event.get('name')),
                'image_url': (event.get('poster_image') or {}).get('default_url'),
                'location': str_location,
                'ext_id': ext_id,
                'lat': (loc_event or {}).get('lat'),
                'lon': (loc_event or {}).get('lon')
            })
            str_fields = ''
            str_params = ''
            for key in params:
                str_fields += key + ', ' if key not in ('lat', 'lon') else ''
                str_params += ':' + key  + ', ' if key not in ('lat', 'lon') else ''
            event_id = session.execute(f"""
                INSERT INTO
                    events ({str_fields[:-2]}, geolocation)
                VALUES
                   ({str_params[:-2]}, ST_SetSRID(ST_MakePoint(:lon, :lat), 4326))
                RETURNING
                    id
            """, params).one()[0]
            categories = event.get('categories')
            if categories:
                tags = json.dumps([{
                    'tag_id': TAGS.get(cat.get('name')),
                    'tag_name': cat.get('name')
                } for cat in categories], default=str)
                session.execute(f"""
                    INSERT INTO
                        events_tags (event_id, tag_id, tag_name)
                    SELECT
                        (:event_id)::bigint
                    ,   (md.tag_id)::smallint
                    ,   (md.tag_name)::text
                    FROM
                        jsonb_to_recordset((:tags)::jsonb) as md(
                            tag_id smallint,
                            tag_name text
                        )
                """, {'event_id': event_id, 'tags': tags})
            session.execute(f"""
                INSERT INTO
                    org_events (org_id, event_id)
                VALUES
                    (:org_id, :event_id)
            """, {
                'org_id': org_id,
                'event_id': event_id
            })
            time.sleep(1)
        session.commit()
        session.close()

    def test_check_geopoint(self):
        session = SessionLocal()

        rs = session.execute(f"""
            SELECT
                ST_X(geolocation::geometry) AS lon,
                ST_Y(geolocation::geometry) AS lat
            FROM
                events
        """).all()

        a = 0

    def test_get_events(self):
        from routers import read_events
        session = SessionLocal()
        # from core.models.database import get_session
        # from routers import get_events
        rs = read_events(session=session, id=342)
        a = 0

    def test_subscribe(self):
        from routers import subscribe
        session = SessionLocal()
        a =  subscribe(341,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoZWxsbzNAbWFpbC5ydSIsImV4cCI6MTY5MTk3MTkzMn0.IHq-eonxUq_z0M_A6Gv0rarL5B0T63UzE9EuTmQlEPM', session)
        b= 0
