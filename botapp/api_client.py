import aiohttp
import os
from typing import List, Dict, Any

API_BASE = os.getenv('BOT_API_BASE_URL', 'http://localhost:8000/api')


class APIClient:
    def __init__(self):
        self.base_url = API_BASE
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def get_specialities(self) -> List[Dict[str, Any]]:
        """Get list of specialities"""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f'{self.base_url}/specialities/') as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data.get('results', data) if isinstance(data, dict) else data
            except Exception as e:
                print(f"Error fetching specialities: {e}")
        return []

    async def get_doctors(self, speciality_id: int) -> List[Dict[str, Any]]:
        """Get doctors by speciality"""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f'{self.base_url}/doctors/?speciality={speciality_id}') as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data.get('results', data) if isinstance(data, dict) else data
            except Exception as e:
                print(f"Error fetching doctors: {e}")
        return []

    async def get_available_days(self, doctor_id: int) -> List[str]:
        """Get available days for doctor"""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f'{self.base_url}/slots/available-days/?doctor={doctor_id}') as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        dates = [item.get('date') for item in (data.get('results', data) if isinstance(data, dict) else data)]
                        return [d for d in dates if d]
            except Exception as e:
                print(f"Error fetching available days: {e}")
        return []

    async def get_slots(self, doctor_id: int, date: str) -> List[Dict[str, Any]]:
        """Get slots for specific date"""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f'{self.base_url}/slots/?doctor={doctor_id}&date={date}') as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data.get('results', data) if isinstance(data, dict) else data
            except Exception as e:
                print(f"Error fetching slots: {e}")
        return []

    async def create_appointment(self, token: str, slot_id: int, complaint: str = '') -> Dict[str, Any]:
        """Create appointment"""
        async with aiohttp.ClientSession() as session:
            try:
                headers = {'Authorization': f'Bearer {token}'}
                payload = {'slot': slot_id, 'complaint': complaint}
                async with session.post(f'{self.base_url}/appointments/', json=payload, headers=headers) as resp:
                    if resp.status in [200, 201]:
                        return await resp.json()
                    else:
                        error = await resp.text()
                        return {'error': error}
            except Exception as e:
                return {'error': str(e)}
        return {'error': 'Unknown error'}

    async def get_my_appointments(self, token: str) -> List[Dict[str, Any]]:
        """Get patient's appointments"""
        async with aiohttp.ClientSession() as session:
            try:
                headers = {'Authorization': f'Bearer {token}'}
                async with session.get(f'{self.base_url}/appointments/my/', headers=headers) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data.get('results', data) if isinstance(data, dict) else data
            except Exception as e:
                print(f"Error fetching appointments: {e}")
        return []
