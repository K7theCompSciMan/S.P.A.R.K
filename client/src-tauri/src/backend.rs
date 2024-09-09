use std::{ops::DerefMut, sync::{Arc, Mutex}, thread};

use reqwest::{self, Error};
use tauri::Runtime;
use tauri_plugin_store::Store;
use crate::{app::run_command, xata_structs::{self, Device}};
use crate::{store};

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

pub fn handle_device_updates_api_call() -> Result<(), Error> {
    let path = "stores/store.json".to_string();
    let mut device: Device = serde_json::from_value::<Device>(store::get(path.clone(), "device".to_string())).unwrap_or(default_device());
    println!("Device from store: {:?}", device);
    let mut device_type = serde_json::from_value::<String>(store::get(path.clone(), "deviceType".to_string())).unwrap_or("default".to_string());
    loop {
        if device.id!="default".to_string() && device_type!="none".to_string() {
            let past_messages = device.messages.clone();
            let request_url = format!("https://spark-api.fly.dev/device/{device_type}/{device_id}/", device_type = device_type, device_id = device.id);
            let updated_device: Device = reqwest::blocking::get(&request_url)?.json()?;
            println!("Getting Updated Device: {:?}", updated_device);
            // println!("_____________________________________________");
            println!("past Device Messages {:?}", device.messages );
            println!("updated Device Messages {:?}", updated_device.messages );
            
            if updated_device != device {
                println!("updated device different from store");
                if past_messages != updated_device.messages {
                    let new_messages = updated_device.messages.clone();
                    let new_message = new_messages[new_messages.len() - 1].clone();
                    println!("recieved message {:?}", new_message);
                    if new_message.content.contains("[RUN COMMAND]") {
                        for command in updated_device.deviceCommands.clone() {
                            if format!("[RUN COMMAND] {}", command.alias) == new_message.content {
                                run_command(&command.command)
                            }
                        }
                    }
                }
                let _ =store::set(path.clone(), "device".to_string(), updated_device.to_json_value());
            }
        }
        else { 
            println!("____________________________");
            println!("No device or device type set");
        }
        println!();
        thread::sleep(std::time::Duration::from_secs(10));
        device = serde_json::from_value::<Device>(store::get(path.clone(), "device".to_string())).unwrap_or(default_device());
        println!("Device from store: {:?}", device);
        device_type = serde_json::from_value::<String>(store::get(path.clone(), "deviceType".to_string())).unwrap_or("default".to_string());
    }
}