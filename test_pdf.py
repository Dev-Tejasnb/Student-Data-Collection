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
        response = await client.post('/api/auth/login', json={'username': 'testadmin', 'password': 'password123'})
        token = response.json()['access_token']
        headers = {'Authorization': 'Bearer ' + token}
        
        # Test PDF export all
        response = await client.get('/api/admin/students/pdf', headers=headers)
        print(f'PDF export all: {response.status_code}')
        print(f'Response: {response.text}')

asyncio.run(test())