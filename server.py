import asyncio
import json
import websockets
import os
from pymongo import MongoClient, DESCENDING

# --- CONFIGURATION ---
# REPLACE with your actual Atlas connection string
MONGO_URI = "mongodb+srv://admin:password@cluster0.mongodb.net/?retryWrites=true&w=majority"

client = MongoClient(MONGO_URI)
db = client['mahehub_db']
events_col = db['events']
users_col = db['users']
registrations_col = db['registrations']

def fetch_all_events():
    # MongoDB doesn't use SQL JOIN. We fetch events and count registrations separately.
    events = list(events_col.find().sort("created_at", DESCENDING))
    
    formatted_events = []
    for e in events:
        # This replaces your SQL COUNT(r.id) logic
        reg_count = registrations_col.count_documents({"event_id": e['id']})
        
        formatted_events.append({
            "id": e['id'],
            "name": e['name'],
            "club": e['club'],
            "desc": e['description'], # Mapping 'description' to 'desc' for your frontend
            "status": e.get('status', 'pending'),
            "reg_count": reg_count,
            "date": e.get('date'),
            "time": e.get('time')
        })
    return formatted_events

# --- WEBSOCKET LOGIC ---
CLIENTS = {}

async def broadcast_sync():
    all_data = fetch_all_events()
    message = json.dumps({"type": "SYNC_DATA", "payload": all_data})
    for ws in list(CLIENTS.keys()):
        try:
            await ws.send(message)
        except:
            if ws in CLIENTS: del CLIENTS[ws]

async def handle_connection(websocket):
    CLIENTS[websocket] = None
    try:
        async for message in websocket:
            data = json.loads(message)
            msg_type = data.get("type")

            # 1. AUTHENTICATION (Restored exactly as your original)
            if msg_type == "STUDENT_AUTH":
                email = data.get("email")
                password = data.get("password")
                username = data.get("username")
                
                ALLOWED_ADMINS = ["tejasnj14@gmail.com", "anupvenu@gmail.com", "abhay.sg2006@gmail.com"]
                MASTER_PASS = "12345678"

                user = users_col.find_one({"email": email})

                if not user:
                    if not username:
                        await websocket.send(json.dumps({"type": "AUTH_RESPONSE", "status": "not_found"}))
                    else:
                        users_col.insert_one({
                            "email": email, "username": username, 
                            "password": password, "role": "student"
                        })
                        await websocket.send(json.dumps({
                            "type": "AUTH_RESPONSE", "status": "success", 
                            "user": {"email": email, "username": username, "role": "student"}
                        }))
                else:
                    if (email in ALLOWED_ADMINS and password == MASTER_PASS) or (user['password'] == password):
                        await websocket.send(json.dumps({
                            "type": "AUTH_RESPONSE", "status": "success", 
                            "user": {"email": email, "username": user['username'], "role": user.get('role', 'student')}
                        }))
                    else:
                        await websocket.send(json.dumps({"type": "AUTH_RESPONSE", "status": "error", "message": "Incorrect Password"}))

            # 2. ROLE REGISTRATION
            elif msg_type == "REGISTER":
                CLIENTS[websocket] = data.get("role")
                await websocket.send(json.dumps({"type": "SYNC_DATA", "payload": fetch_all_events()}))

            # 3. NEW EVENT
            elif msg_type == "NEW_EVENT_REQUEST":
                p = data['payload']
                events_col.insert_one({
                    "id": p['id'], "name": p['name'], "club": p['club'],
                    "description": p['desc'], "status": "pending",
                    "date": p.get('date'), "time": p.get('time'),
                    "created_at": os.times().elapsed # Using system time for sorting
                })
                await broadcast_sync()

            # 4. STUDENT REGISTRATION (Registration Count Logic)
            elif msg_type == "STUDENT_REGISTER":
                registrations_col.update_one(
                    {"event_id": data.get("event_id"), "student_email": data.get("email")},
                    {"$set": {"event_id": data.get("event_id"), "student_email": data.get("email")}},
                    upsert=True
                )
                await broadcast_sync()

            # 5. ADMIN DECISION & LIVE NOTIFICATION
            elif msg_type == "EVENT_DECISION":
                events_col.update_one({"id": data['id']}, {"$set": {"status": data['status']}})
                updated_ev = events_col.find_one({"id": data['id']})
                await broadcast_sync()

                if data["status"] == "approve" and updated_ev:
                    live_msg = json.dumps({
                        "type": "POST_LIVE_EVENT", 
                        "payload": {
                            "id": updated_ev['id'], "name": updated_ev['name'], 
                            "club": updated_ev['club'], "date": updated_ev.get('date'),
                            "time": updated_ev.get('time')
                        }
                    })
                    for ws, role in CLIENTS.items():
                        if role == "student":
                            try: await ws.send(live_msg)
                            except: pass

    except Exception as e: print(f"Socket Error: {e}")
    finally:
        if websocket in CLIENTS: del CLIENTS[websocket]

async def main():
    port = int(os.environ.get("PORT", 3000))
    # Note: Use "0.0.0.0" for Render deployment
    async with websockets.serve(handle_connection, "0.0.0.0", port):
        print(f"🚀 MaheHub Backend (Atlas) Online on Port {port}")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
