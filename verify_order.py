import asyncio
import httpx
from app.main import app
from app.database import connect_to_mongo, get_database
from app.auth.security import get_password_hash
import datetime

async def test():
    await connect_to_mongo()
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url='http://test') as client:
        from app.database import get_database
        db = await get_database()
        await db.users.delete_many({})
        await db.users.insert_one({
            'username': 'testadmin',
            'password_hash': get_password_hash('password123'),
            'role': 'admin',
            'is_active': True,
            'created_at': datetime.datetime.now(datetime.timezone.utc)
        })
        
        # Test student form submission with JSON (simulating frontend)
        response = await client.post('/api/students', json={'name': 'Test Student 1', 'batch': 'Batch - 1', 'course': 'BCA', 'college': 'Test College', 'admission_through': 'NEET'}, headers={'Content-Type': 'application/json'})
        print('1. POST /api/students (first student):', response.status_code, response.json())
        
        response = await client.post('/api/students', json={'name': 'Test Student 2', 'batch': 'Batch - 1', 'course': 'BCA', 'college': 'Test College', 'admission_through': 'NEET'}, headers={'Content-Type': 'application/json'})
        print('2. POST /api/students (second student):', response.status_code, response.json())
        
        response = await client.post('/api/students', json={'name': 'Test Student 3', 'batch': 'Batch - 1', 'course': 'BCA', 'college': 'Test College', 'admission_through': 'NEET'}, headers={'Content-Type': 'application/json'})
        print('3. POST /api/students (third student):', response.status_code, response.json())
        
        # Test listing students - should be ordered oldest first
        db = await get_database()
        await db.users.delete_many({})
        await db.users.insert_one({
            'username': 'testadmin',
            'password_hash': get_password_hash('password123'),
            'role': 'admin',
            'is_active': True,
            'created_at': datetime.datetime.now(datetime.timezone.utc)
        })
        
        response = await client.post('/api/auth/login', data={'username': 'testadmin', 'password': 'password123'})
        token = response.json()['access_token']
        headers = {'Authorization': 'Bearer ' + token}
        
        response = await client.get('/api/admin/students', headers=headers)
        students = response.json()['data']['students']
        print('Student order (should be oldest first):')
        for i, s in enumerate(students[:5]):
            print(f'  {i+1}. {s["name"]} - {s["created_at"]}')

asyncio.run(test())