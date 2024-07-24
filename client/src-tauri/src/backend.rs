use reqwest::{self, Error};
use tauri::Runtime;
use tauri_plugin_store::Store;
use crate::{app::run_command, xata_structs::{self, Device}};


pub async fn handle_device_updates<R: Runtime>(store: Store<R>) -> Result<(), Error> {
    loop {
        let device: Device = store.get("device".to_string()).unwrap().as_object().unwrap().to_owned().into();
        let past_messages = device.messages.clone();
        let request_url = format!("https://spark-api.fly.dev/{device_type}/{device_id}/", device_type = device.device_type, device_id = device.id);
        let updated_device: xata_structs::Device = reqwest::get(&request_url).await?.json().await?;
        println!("past Device {:?}", device.messages );
        println!("updated Device {:?}", updated_device.messages );
        if updated_device != device {
            if past_messages != updated_device.messages {
                let new_messages = updated_device.messages.clone();
                let new_message = new_messages[new_messages.len() - 1].clone();
                if new_message.content.contains("[RUN COMMAND]") {
                    for command in device.commands.clone() {
                        if format!("[RUN COMMAND] {}", command.alias) == new_message.content {
                            run_command(&command.command)
                        }
                    }
                }
            }
            store.insert("device".to_string(), updated_device.to_json_value());
        }
        thread::sleep(std::time::Duration::from_secs(5));
    }
}