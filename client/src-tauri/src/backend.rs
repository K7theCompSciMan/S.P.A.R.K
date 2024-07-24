use std::thread;

use reqwest::{self, Error};
use tauri::Runtime;
use tauri_plugin_store::Store;
use crate::{app::run_command, xata_structs::{self, Device}};

fn default_device() -> Device {
    Device {
        name: "default".to_string(),
        id: "default".to_string(),
        assignedUser: xata_structs::User { id: "default".to_string() },
        assignedGroup: xata_structs::Group { id: "default".to_string() },
        messages: vec![],
        deviceCommands: vec![],
    }

}

fn handle_server_device() {
    loop {
        println!("Server Device Running");
    }
}

pub fn handle_device_updates<R: Runtime>( store: &mut Store<R>) -> Result<(), Error> {
    loop {
        let device: Device = serde_json::from_value::<Device>(store.get("device".to_string()).unwrap().clone()).unwrap_or(default_device());
        let device_type = serde_json::from_value::<String>(store.get("deviceType".to_string()).unwrap().clone()).unwrap_or("none".to_string());
        
        if device.id!="default".to_string() && device_type!="none".to_string(){
            let past_messages = device.messages.clone();
            let request_url = format!("https://spark-api.fly.dev/device/{device_type}/{device_id}/", device_type = device_type, device_id = device.id);
            let updated_device: xata_structs::Device = reqwest::blocking::get(&request_url)?.json()?;
            println!("past Device Messages {:?}", device.messages );
            println!("updated Device Messages {:?}", updated_device.messages );
            if device_type == "server" {
                thread::spawn(|| {
                    handle_server_device();
                });
            }
            if updated_device != device {
                if past_messages != updated_device.messages {
                    let new_messages = updated_device.messages.clone();
                    let new_message = new_messages[new_messages.len() - 1].clone();
                    if new_message.content.contains("[RUN COMMAND]") {
                        for command in device.deviceCommands.clone() {
                            if format!("[RUN COMMAND] {}", command.alias) == new_message.content {
                                run_command(&command.command)
                            }
                        }
                    }
                }
                let _ =store.insert("device".to_string(), updated_device.to_json_value()).expect("Error saving new device to store");
            }
        }
        else { 
            println!("No device or device type set");
        }
        thread::sleep(std::time::Duration::from_secs(5));
    }
}