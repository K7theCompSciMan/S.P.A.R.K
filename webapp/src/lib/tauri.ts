import { invoke } from "@tauri-apps/api/tauri"


export const setStore = async (key: string, value: unknown) => {
    invoke('set_store', { path: "stores/store.json", key, value})
}
export const getStore = async (key: string) => {
    return invoke("get_store", { path: "stores/store.json", key})
}