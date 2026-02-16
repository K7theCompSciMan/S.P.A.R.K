import { deviceToSpecificDevice, type Device, type Command } from '$lib';
import { setStore } from './tauri';

const API_BASE = 'https://spark-api.fly.dev';

export async function getDeviceApi(id: string, type: string, token: string) {
    const res = await fetch(`${API_BASE}/device/${type}/${id}`, {
        headers: { authorization: `Bearer ${token}` }
    });
    return res.ok ? await res.json() : null;
}

export async function updateDeviceApi(device: Device, token: string, thisDeviceId?: string) {
    const specificDevice = deviceToSpecificDevice(device);
    const type = device.type === 'client' ? 'client' : 'server';
    
    const res = await fetch(`${API_BASE}/device/${type}/`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', authorization: `Bearer ${token}` },
        body: JSON.stringify({ ...specificDevice, id: device.id })
    });

    if (res.ok && device.id === thisDeviceId) {
        await setStore('device', specificDevice);
        await setStore('deviceType', type);
    }
    return res;
}

export async function deleteMessageApi(id: string, token: string) {
    return await fetch(`${API_BASE}/device/message/${id}`, {
        method: 'DELETE',
        headers: { authorization: `Bearer ${token}` }
    });
}