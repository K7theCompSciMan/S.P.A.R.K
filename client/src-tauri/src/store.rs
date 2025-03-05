use serde_json;
use std::{fs::File, thread};
fn default_store() -> serde_json::Value {
    return serde_json::json!({
        "user": {
            "id": "",
            "username": "",
            "settings": {
                "primaryCommunicationMethod": "api"
            }
        },
        "device": {
            "id": "",
            "name": "",
            "messages": [],
            "deviceCommands": [],
            "assignedGroup": {
                "id": ""
            },
            "assignedUser": {
                "id": ""
            }
        },
        "deviceType": "",
        "backendNATS": false,
        "runningClientBackend": false,
        "runningServerBackend": false
    });
}
pub fn get(path: String, key: String) -> serde_json::Value {
    let file = File::open(path.clone()).expect("Error opening file");
    let json: serde_json::Value = serde_json::from_reader(file.try_clone().expect("Couldn't clone file")).map_err(|e| {
        if e.is_eof() {
            let write_file = File::create(path.clone()).expect("Error creating file");
            serde_json::to_writer_pretty(write_file, &default_store()).expect("Error writing file");
        }
    }).unwrap();
    return json.get(key).expect("Error getting key").clone();
}

pub fn set(path: String, key: String, value: serde_json::Value) {
    let read_file = File::open(path.clone()).expect("Error creating file");
    // println!("reading from file in set function");
    let json: serde_json::Value = serde_json::from_reader(read_file.try_clone().expect("Couldn't clone file")).expect("Error reading file");
    // println!("read from file in set function");
    let write_file = File::create(path.clone()).expect("Error creating file");
    let mut new_json = json.as_object().unwrap().clone();
    new_json.insert(key, value);
    serde_json::to_writer_pretty(write_file, &new_json).expect("Error writing file");
}

#[tauri::command]
pub fn get_store(path: String, key: String) -> serde_json::Value {
    return get(path, key);
}

#[tauri::command]
pub fn set_store(path: String, key: String, value: serde_json::Value) {
    set(path, key, value);
}

// pub fn main() {
//     println!("{}", format!("user: {:?}", get("stores/store.json".to_string(), "user".to_string())));
//     println!("{}", format!("user: {:?}", get("stores/store.json".to_string(), "user".to_string())));
//     thread::sleep(std::time::Duration::from_secs(2));
//     println!("setting new value");
//     set("stores/store.json".to_string(), "user".to_string(), serde_json::json!({ "id": "rec_cq87c29m0de2bt39lmmg", "username": "KesavanTEST" }));
//     println!("{}",format!("user: {:?}", get("stores/store.json".to_string(), "user".to_string())));
// }