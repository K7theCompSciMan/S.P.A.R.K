use std::{ops::DerefMut, sync::{Arc, Mutex}, thread};

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

pub fn handle_server_device() {
    loop {
        println!("Server Device Running"); 
    }
}

pub fn handle_device_updates<R: Runtime>( store: Arc<Mutex<Store<R>>>) -> Result<(), Error> {
    let mut binding = match store.lock() {
        Ok(guard) => {
            guard},
        Err(poisoned) => {
            // Handle mutex poisoning
            let guard = poisoned.into_inner();
            println!("Thread recovered from mutex poisoning: {:?}", *guard);
            guard
        }
    };
    let store: &mut Store<R> = binding.deref_mut();
    store.load().expect("Error loading store");
    let mut device: Device = serde_json::from_value::<Device>(store.get("device".to_string()).unwrap().clone()).unwrap_or(default_device());
    let mut device_type = serde_json::from_value::<String>(store.get("deviceType".to_string()).unwrap().clone()).unwrap_or("none".to_string());
    if device_type == "server" {
        thread::spawn(|| {
                handle_server_device();
            });
    }
    loop {
        if device.id!="default".to_string() && device_type!="none".to_string() {
            let past_messages = device.messages.clone();
            let request_url = format!("https://spark-api.fly.dev/device/{device_type}/{device_id}/", device_type = device_type, device_id = device.id);
            let updated_device: Device = reqwest::blocking::get(&request_url)?.json()?;
            // println!("_____________________________________________");
            // println!("past Device Messages {:?}", device.messages );
            // println!("updated Device Messages {:?}", updated_device.messages );
            
            if updated_device != device {
                if past_messages != updated_device.messages {
                    let new_messages = updated_device.messages.clone();
                    let new_message = new_messages[new_messages.len() - 1].clone();
                    // println!("recieved message {:?}", new_message);
                    if new_message.content.contains("[RUN COMMAND]") {
                        for command in updated_device.deviceCommands.clone() {
                            if format!("[RUN COMMAND] {}", command.alias) == new_message.content {
                                run_command(&command.command)
                            }
                        }
                    }
                }
                let _ =store.insert("device".to_string(), updated_device.to_json_value()).expect("Error saving new device to store");
                store.save().expect("Error saving store");
                store.load().expect("Error loading store");
            }
        }
        else { 
            println!("____________________________");
            println!("No device or device type set");
        }
        store.save().expect("Error saving store");
        store.load().expect("Error loading store");
        thread::sleep(std::time::Duration::from_secs(10));
        store.load().expect("Error loading store");
        store.save().expect("Error saving store");
        device = serde_json::from_value::<Device>(store.get("device".to_string()).unwrap().clone()).unwrap();
        device_type = serde_json::from_value::<String>(store.get("deviceType".to_string()).unwrap().clone()).unwrap();
    }
}