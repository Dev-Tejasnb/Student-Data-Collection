import asyncio
import httpx
from app.main import app
from app.database import connect_to_mongo
from app.auth.security import create_access_token, get_password_hash
import datetime

async def test():
    await connect_to_mongo()
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url='http://test') as client:
        # Test public student submission
        response = await client.post('/api/students', json={'name': 'Test Student', 'course': 'BCA', 'college': 'Test College', 'admission_through': 'KCET'})
        print(f'1. Create student: {response.status_code}')
        
        # Create admin user
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
        print(f'2. Login: {response.status_code}')
        token = response.json()['access_token']
        headers = {'Authorization': 'Bearer ' + token}
        
        # Test student listing
        response = await client.get('/api/admin/students', headers=headers)
        print(f'3. List students: {response.status_code}')
        
        # Test stats
        response = await client.get('/api/admin/students/stats', headers=headers)
        print(f'4. Stats: {response.status_code}')
        
        # Test get student
        list_resp = await client.get('/api/admin/students', headers=headers)
        if list_resp.json()['data']['students']:
            student_id = list_resp.json()['data']['students'][0]['id']
            response = await client.get('/api/admin/students/' + student_id, headers=headers)
            print(f'5. Get student: {response.status_code}')
            
            # Test update student
            response = await client.put('/api/admin/students/' + student_id, headers=headers, json={'name': 'Updated Name'})
            print(f'6. Update student: {response.status_code}')
            
            # Test PDF export all (new endpoint)
            response = await client.get('/api/admin/students/export/pdf', headers=headers)
            print(f'7. PDF export all: {response.status_code} - Content-Type: {response.headers.get("content-type")}')
            
            # Test PDF export individual
            response = await client.get('/api/admin/students/' + student_id + '/pdf', headers=headers)
            print(f'8. PDF export individual: {response.status_code} - Content-Type: {response.headers.get("content-type")}')
            
            # Test delete student (admin only)
            response = await client.delete('/api/admin/students/' + student_id, headers=headers)
            print(f'9. Delete student: {response.status_code}')
        
        # Test user management (admin only)
        response = await client.post('/api/auth/users', headers=headers, json={'username': 'newstaff', 'password': 'password123', 'role': 'staff'})
        print(f'10. Create user: {response.status_code}')
        
        response = await client.get('/api/auth/users', headers=headers)
        print(f'11. List users: {response.status_code}')
        
        # Test staff permissions (should work for listing but not deleting)
        await db.users.insert_one({
            'username': 'staffuser',
            'password_hash': get_password_hash('password123'),
            'role': 'staff',
            'is_active': True,
            'created_at': datetime.datetime.now(datetime.timezone.utc)
        })
        staff_token = create_access_token({'sub': 'staffuser'})
        staff_headers = {'Authorization': 'Bearer ' + staff_token}
        
        response = await client.get('/api/admin/students', headers=staff_headers)
        print(f'12. Staff list students: {response.status_code}')
        
        # Staff should NOT be able to delete
        list_resp = await client.get('/api/admin/students', headers=headers)
        if list_resp.json()['data']['students']:
            student_id = list_resp.json()['data']['students'][0]['id']
            response = await client.delete('/api/admin/students/' + student_id, headers=staff_headers)
            print(f'13. Staff delete student (should fail): {response.status_code} - {response.json()}')

asyncio.run(test())