import {Store} from "tauri-plugin-store-api";

export const store = new Store("C:/Code/S.P.A.R.K/client/stores/store.json");

export const setStore = async (key: string, value: unknown) => {
    await store.set(key, value);
    await store.save() ;
}
export const getStore = async (key: string) => {
    return await store.get(key);
}