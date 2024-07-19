import {Store} from "tauri-plugin-store-api";

export const store = new Store("../stores/store.json");

export const setStore = async (key: string, value: unknown) => {
    try {
    console.log("setStore", key, value);
    await store.set(key, value);
    await store.save() ;}
    catch (e) {
        console.error(e);
    }
}
export const getStore = async (key: string) => {
    return await store.get(key);
}