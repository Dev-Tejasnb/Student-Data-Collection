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
        
        # Test login
        response = await client.post('/api/auth/login', data={'username': 'testadmin', 'password': 'password123'})
        print('Login:', response.status_code)
        token = response.json()['access_token']
        headers = {'Authorization': 'Bearer ' + token}
        
        # Test student submission with JSON
        response = await client.post('/api/students', json={'name': 'Test Student', 'batch': 'Batch - 2', 'course': 'BCA', 'college': 'Test College', 'admission_through': 'NEET'}, headers={'Content-Type': 'application/json'})
        print('Create student (JSON):', response.status_code, response.json())
        
        # Test all 4 batch options
        for batch in ['FTB', 'Batch - 1', 'Batch - 2', 'Batch - 3']:
            response = await client.post('/api/students', json={'name': f'Test {batch}', 'batch': batch, 'course': 'BCA', 'college': 'Test College', 'admission_through': 'NEET'}, headers={'Content-Type': 'application/json'})
            print(f'Create student ({batch}):', response.status_code, response.json())
        
        # Test invalid batch
        response = await client.post('/api/students', json={'name': 'Test Invalid', 'batch': 'Invalid Batch', 'course': 'BCA', 'college': 'Test College', 'admission_through': 'NEET'}, headers={'Content-Type': 'application/json'})
        print('Invalid batch:', response.status_code, response.json())
        
        # Test existing records
        from app.database import get_database
        db = await get_database()
        count = await db.students.count_documents({})
        print(f'Total students in DB: {count}')
        
        # Test admin student list with batch filter
        response = await client.post('/api/auth/login', data={'username': 'testadmin', 'password': 'password123'})
        token = response.json()['access_token']
        headers = {'Authorization': 'Bearer ' + token}
        
        response = await client.get('/api/admin/students', headers=headers)
        print('All students:', response.status_code, len(response.json()['data']['students']))
        
        response = await client.get('/api/admin/students?batch=Batch%20-%203', headers=headers)
        print('Batch 3 filter:', response.status_code, len(response.json()['data']['students']))
        
        response = await client.get('/api/admin/students?batch=Batch%20-%202', headers=headers)
        print('Batch 2 filter:', response.status_code, len(response.json()['data']['students']))
        
        response = await client.get('/api/admin/students?batch=Batch%20-%201', headers=headers)
        print('Batch 1 filter:', response.status_code, len(response.json()['data']['students']))
        
        response = await client.get('/api/admin/students?batch=FTB', headers=headers)
        print('FTB filter:', response.status_code, len(response.json()['data']['students']))
        
        # Test stats
        response = await client.get('/api/admin/students/stats', headers=headers)
        print('Stats:', response.status_code, response.json()['data'])
        
        # Test edit student with batch change
        db = await get_database()
        student = await db.students.find_one({})
        student_id = str(student['_id'])
        response = await client.put(f'/api/admin/students/{student_id}', headers=headers, json={'name': 'Updated Name', 'batch': 'Batch - 1'})
        print('Edit student:', response.status_code, response.json())
        
        # Verify change
        updated = await db.students.find_one({'_id': student['_id']})
        print('Updated batch:', updated.get('batch'))

asyncio.run(test())