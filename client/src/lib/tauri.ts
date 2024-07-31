import {Store} from "tauri-plugin-store-api";
import { resolveResource } from '@tauri-apps/api/path'


export let store: Store;

export const initStore = async () => {
    const resourcePath = await resolveResource('stores/store.json');
    store = new Store(resourcePath);
}

export const setStore = async (key: string, value: unknown) => {
    await store.set(key, value);
    await store.save() ;
}
export const getStore = async (key: string) => {
    return await store.get(key);
}