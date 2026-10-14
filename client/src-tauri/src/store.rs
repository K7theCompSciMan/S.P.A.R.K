use serde_json;
use std::fs::{self, File};
use std::path::PathBuf;

fn store_path(relative: &str) -> PathBuf {
    if let Some(proj_dirs) = directories::ProjectDirs::from("com", "spark", "ai.assistant") {
        let base = proj_dirs.data_dir().to_path_buf();
        fs::create_dir_all(&base).ok();
        base.join(relative)
    } else {
        PathBuf::from(relative)
    }
}

fn default_store() -> serde_json::Value {
    serde_json::json!({
        "user": {
            "id": "",
            "email": "",
            "username": "",
            "settings": {
                "primaryCommunicationMethod": "realtime"
            }
        },
        "device": {
            "id": "",
            "name": "",
            "messages": [],
            "deviceCommands": []
        },
        "deviceType": "",
        "accessToken": "",
        "refreshToken": "",
        // Written by the frontend's initRealtime() call so the Rust
        // Realtime backend can open a WebSocket without needing env vars.
        "supabaseUrl": "",
        "supabaseAnonKey": "",
        "runningClientBackend": false,
        "runningServerBackend": false
    })
}

fn read_store(path: &PathBuf) -> serde_json::Value {
    if let Some(parent) = path.parent() {
        fs::create_dir_all(parent).ok();
    }
    match File::open(path) {
        Ok(file) => serde_json::from_reader(file).unwrap_or_else(|_| {
            let write = File::create(path).expect("Cannot create store file");
            let defaults = default_store();
            serde_json::to_writer_pretty(write, &defaults).expect("Cannot write defaults");
            defaults
        }),
        Err(_) => {
            let write = File::create(path).expect("Cannot create store file");
            let defaults = default_store();
            serde_json::to_writer_pretty(write, &defaults).expect("Cannot write defaults");
            defaults
        }
    }
}

pub fn get(relative_path: String, key: String) -> serde_json::Value {
    let path = store_path(&relative_path);
    let json = read_store(&path);
    json.get(&key).cloned().unwrap_or(serde_json::Value::Null)
}

pub fn set(relative_path: String, key: String, value: serde_json::Value) {
    let path = store_path(&relative_path);
    let mut json = read_store(&path);
    if let Some(obj) = json.as_object_mut() {
        obj.insert(key, value);
    }
    let write = File::create(&path).expect("Cannot open store for writing");
    serde_json::to_writer_pretty(write, &json).expect("Cannot write store");
}

#[tauri::command]
pub fn get_store(_path: String, key: String) -> serde_json::Value {
    get("stores/store.json".to_string(), key)
}

#[tauri::command]
pub fn set_store(_path: String, key: String, value: serde_json::Value) {
    set("stores/store.json".to_string(), key, value);
}