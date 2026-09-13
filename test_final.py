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
        response = await client.post('/api/students', json={'name': 'Test Student', 'batch': 'Batch - 2', 'course': 'BCA', 'college': 'Test College', 'admission_through': 'NEET'}, headers={'Content-Type': 'application/json'})
        print('1. POST /api/students (form submission):', response.status_code)
        
        # Test all 4 batch options
        for batch in ['FTB', 'Batch - 1', 'Batch - 2', 'Batch - 3']:
            response = await client.post('/api/students', json={'name': f'Test {batch}', 'batch': batch, 'course': 'BCA', 'college': 'Test College', 'admission_through': 'NEET'}, headers={'Content-Type': 'application/json'})
            print(f'2. POST /api/students ({batch}): {response.status_code}')
        
        # Test invalid batch
        response = await client.post('/api/students', json={'name': 'Test Invalid', 'batch': 'Invalid Batch', 'course': 'BCA', 'college': 'Test College', 'admission_through': 'NEET'}, headers={'Content-Type': 'application/json'})
        print(f'Invalid batch rejected: {response.status_code}')
        
        # Test existing records preserved
        from app.database import get_database
        db = await get_database()
        count = await db.students.count_documents({})
        print(f'Total students in DB: {count}')
        
        # Test admin student list with batch filter
        response = await client.post('/api/auth/login', data={'username': 'testadmin', 'password': 'password123'})
        token = response.json()['access_token']
        headers = {'Authorization': 'Bearer ' + token}
        
        response = await client.get('/api/admin/students', headers=headers)
        students = response.json()['data']['students']
        print(f'All students: {response.status_code} ({len(students)} students)')
        
        response = await client.get('/api/admin/students?batch=Batch%20-%203', headers=headers)
        students = response.json()['data']['students']
        print(f'Batch 3 filter: {response.status_code} ({len(students)} students)')
        
        response = await client.get('/api/admin/students?batch=Batch%20-%202', headers=headers)
        students = response.json()['data']['students']
        print(f'Batch 2 filter: {response.status_code} ({len(students)} students)')
        
        response = await client.get('/api/admin/students?batch=Batch%20-%201', headers=headers)
        students = response.json()['data']['students']
        print(f'Batch 1 filter: {response.status_code} ({len(students)} students)')
        
        response = await client.get('/api/admin/students?batch=FTB', headers=headers)
        students = response.json()['data']['students']
        print(f'FTB filter: {response.status_code} ({len(students)} students)')
        
        # Test stats
        response = await client.get('/api/admin/students/stats', headers=headers)
        print(f'Stats: {response.status_code} {response.json()["data"]}')
        
        # Test edit student with batch change
        db = await get_database()
        student = await db.students.find_one({})
        student_id = str(student['_id'])
        response = await client.put(f'/api/admin/students/{student_id}', headers=headers, json={'name': 'Updated Name', 'batch': 'Batch - 1'})
        print(f'Edit student: {response.status_code}')
        
        # Verify change
        updated = await db.students.find_one({'_id': student['_id']})
        print(f'Updated batch: {updated.get("batch")}')
        
        # Test PDF export all
        response = await client.get('/api/admin/students/export/pdf', headers=headers)
        print(f'PDF export all: {response.status_code} Content-Type: {response.headers.get("content-type")} PDF: {response.content[:5] == b"%PDF-"}')
        
        # Test PDF export with batch filter
        response = await client.get('/api/admin/students/export/pdf?batch=Batch%20-%203', headers=headers)
        print(f'PDF export Batch 3: {response.status_code} Content-Type: {response.headers.get("content-type")} PDF: {response.content[:5] == b"%PDF-"}')
        
        # Test individual PDF
        db = await get_database()
        student = await db.students.find_one({})
        student_id = str(student['_id'])
        response = await client.get(f'/api/admin/students/{student_id}/pdf', headers=headers)
        print(f'Individual PDF: {response.status_code} Content-Type: {response.headers.get("content-type")} PDF: {response.content[:5] == b"%PDF-"}')
        
        # Test health endpoints
        response = await client.get('/health')
        print(f'GET /health: {response.status_code}')
        response = await client.head('/health')
        print(f'HEAD /health: {response.status_code}')
        
        # Test static files
        response = await client.get('/static/css/style.css')
        print(f'CSS: {response.status_code}')
        response = await client.get('/static/js/index.js')
        print(f'JS index: {response.status_code}')
        response = await client.get('/static/js/auth.js')
        print(f'JS auth: {response.status_code}')
        response = await client.get('/static/js/dashboard.js')
        print(f'JS dashboard: {response.status_code}')

asyncio.run(test())