use std::{ops::DerefMut, sync::{Arc, Mutex}, thread::{self, current}};
use futures_core::stream::Stream;
use futures_util::StreamExt;
use reqwest::{self, Error};
use tauri::{api::process::CommandEvent, Runtime};
use tauri_plugin_store::Store;
use crate::{app::run_command, xata_structs::{self, Device, User}};
use crate::{store};
use tauri::api::process::Command;
use async_nats;
use std::{io::{prelude::*, BufReader}, net::{TcpListener, TcpStream}};

pub struct Reception {
    pub message: String,
}

impl std::str::FromStr for Reception {
    type Err = String;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        let message = s.split("\r\n\r\n").collect::<Vec<&str>>()[1].to_string();
        Ok(Reception { message })
    }
}

fn default_device() -> Device {
    Device {
        name: "default".to_string(),
        id: "default".to_string(),
        assignedUser: default_user(),
        assignedGroup: xata_structs::Group { id: "default".to_string() },
        messages: vec![],
        deviceCommands: vec![],
    }

}
fn default_user() -> User {
    User { id: "default".to_string(), username: "default".to_string(), settings: xata_structs::UserSettings { primaryCommunicationMethod: "nats".to_string() } }
}

pub fn handle_server_device_updates() {
    tauri::async_runtime::spawn(async move {
        loop {
            println!("Checking if server is running");
            if serde_json::from_value(store::get("stores/store.json".to_string(), "runningServerBackend".to_string())).unwrap_or(false) {
                println!("Server is running");
                let (mut rx, mut child) = Command::new_sidecar("server")
                .expect("failed to setup `server` sidecar")
                .args(["rec_cq9do7pk946ki2d08fo0",
                    "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjp7ImlkIjoicmVjX2NxODdjMjltMGRlMmJ0MzlsbW1nIiwidXNlcm5hbWUiOiJLZXNhdmFuIn0sImlhdCI6MTcyNDExNjk5N30.ae5Y86J74WadBSckxmWxR0Htiev7_VAgs1G327ovQ4oGitLNOhrhj4EETOiSjXZlstMc-kMSmOofqBUcb41DW9uVVMNjFTkuLBSgf-YYCQhj3M2wn2IJyJIu3BHXxDU6aOlacFrK3lCmoxYTX7EGkcrZ6NU_XEyoJCwyqPzHXYCRgT_pnG5ANRHFBYi5hB1qMHzXGgHOWinAdDJYvCCS9v4VLl-wX9E9YdOiEJuJ18hdpkLHkZhCsmaVV0gbdqbEOUWoF3iISTzL1wzBkN3q24iNUcimEe01ab7yB2yOwewhvqf9wuxVfoM7iNhh6pmolIurqVPZKNlq5b6ttirlDg", 
                    "stores/store.json"])
                .spawn()
                .expect("Failed to spawn packaged node");
                // child.write("rec_cq9do7pk946ki2d08fo0 eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjp7ImlkIjoicmVjX2NxODdjMjltMGRlMmJ0MzlsbW1nIiwidXNlcm5hbWUiOiJLZXNhdmFuIn0sImlhdCI6MTcyNDExNjk5N30.ae5Y86J74WadBSckxmWxR0Htiev7_VAgs1G327ovQ4oGitLNOhrhj4EETOiSjXZlstMc-kMSmOofqBUcb41DW9uVVMNjFTkuLBSgf-YYCQhj3M2wn2IJyJIu3BHXxDU6aOlacFrK3lCmoxYTX7EGkcrZ6NU_XEyoJCwyqPzHXYCRgT_pnG5ANRHFBYi5hB1qMHzXGgHOWinAdDJYvCCS9v4VLl-wX9E9YdOiEJuJ18hdpkLHkZhCsmaVV0gbdqbEOUWoF3iISTzL1wzBkN3q24iNUcimEe01ab7yB2yOwewhvqf9wuxVfoM7iNhh6pmolIurqVPZKNlq5b6ttirlDg".as_bytes());
                while let Some(event) = rx.recv().await {
                    if let CommandEvent::Stdout(line) = event {
                        let mut current_server_output = serde_json::from_value::<Vec<String>>(store::get("stores/store.json".to_string(), "serverOutput".to_string())).unwrap_or(Vec::<String>::new());
                        current_server_output.push(line.clone());
                        store::set("stores/store.json".to_string(), "serverOutput".to_string(), current_server_output.into());
                        println!("server output: {}", line.clone());
                    }
                    else {
                        println!("server output: {:?}", event);
                    }
                    if !serde_json::from_value(store::get("stores/store.json".to_string(), "runningServerBackend".to_string())).unwrap_or(false) {
                        println!("Server is not running");
                        let _ = child.kill();
                        break;
                    }
                    println!("Server Running");
                }
            }
            else {
                println!("Server is not running")
            }
        }
    });
}

async fn run_nats_backend(subject: &str, device: Device, path: String) -> Result<(), async_nats::Error> {
    // Connect to the NATS server
    let client = async_nats::connect("0.0.0.0").await?;

    let new_subject = format!("{}", subject);
    // Subscribe to the "messages" subject
    let mut subscriber = client.subscribe(new_subject.clone()).await.unwrap();

    // Publish messages to the "messages" new_subject.clone()
    for _ in 0..10 {
        client.publish(new_subject.clone(), "data".into()).await?;
    }

    // Receive and process messages
    while let Some(message) = subscriber.next().await {
        let message_content: &str = std::str::from_utf8(&message.payload).unwrap();
        println!("Received message {:?}", message_content);
        if message_content.contains("[RUN COMMAND]") {
            for command in device.deviceCommands.clone() {
                if format!("[RUN COMMAND] {}", command.alias) == message_content {
                    run_command(&command.command)
                }
            }
        }
        if message_content.contains("Uptade Device: ") {
            let updated_device: Device = serde_json::from_str(message_content.replace("Uptade Device: ", "").as_str()).unwrap();
            store::set(path.clone(), "device".to_string(), updated_device.to_json_value());

        }
    }

    Ok(())
}

pub fn run_localhost_backend(path: String) -> Result<(), Error> {
    fn handle_connection(mut stream: TcpStream, mut messages: Vec<String>) {
        let mut buffer = [0; 1024];
        stream.read(&mut buffer).unwrap();
        if buffer.starts_with(b"GET / HTTP/1.1") {
            let status_line = "HTTP/1.1 200 OK";
            let length = messages.len();
            let response = format!(
                "{status_line}\r\nContent-Length: {length}\r\n\r\n{:?}", messages
            );
            println!("Recieved GET request, responding: {:?}", response);    
            stream.write(response.as_bytes()).unwrap();
            stream.flush().unwrap();
        }     
        else if buffer.starts_with(b"POST / HTTP/1.1") {
            let status_line = "HTTP/1.1 200 OK";
            let x = std::str::from_utf8(&buffer).unwrap();
            let  reception: Reception = x.to_string().parse::<Reception>().unwrap();
            let message = reception.message;
            messages.push(message.clone());
            let length = messages.len();
            let response = format!(
                "{status_line}\r\nContent-Length: {length}\r\n\r\n{:?}", messages 
            );
            println!("Recieved POST request with message: {message}, responding: {:?}", response);
            stream.write(response.as_bytes()).unwrap();
            stream.flush().unwrap();
        }
    } 
    let messages = vec!["test".to_string()];
    let listener = TcpListener::bind("127.0.0.1:4173").unwrap();

    for stream in listener.incoming() {
        let stream = stream.unwrap();

        handle_connection(stream, messages.clone());
    }
    return Ok(());
}


pub fn handle_device_updates_api_call() -> Result<(), Error> {
    let path = "stores/store.json".to_string();
    let mut device: Device = serde_json::from_value::<Device>(store::get(path.clone(), "device".to_string())).unwrap_or(default_device());
    // println!("Device from store: {:?}", device);
    let mut device_type = serde_json::from_value::<String>(store::get(path.clone(), "deviceType".to_string())).unwrap_or("default".to_string());
    if device_type.clone() == "server" {
        handle_server_device_updates();
    }
    let mut primary_communication_method = serde_json::from_value::<User>(store::get(path.clone(), "user".to_string())).unwrap_or(default_user()).settings.primaryCommunicationMethod ;
    if primary_communication_method == "nats" {
        tauri::async_runtime::spawn(async move {
            let _ = run_nats_backend(&device.id.clone().to_string(), device.clone(), path.clone()).await;
        });
        return Ok(());
    }
    else if primary_communication_method == "localhost" {
        tauri::async_runtime::spawn(async move {
            let _ = run_localhost_backend(path.clone());
        });
        return Ok(());
    }
    else {
        loop {
            let mut running_backend = serde_json::from_value::<bool>(store::get(path.clone(), "runningClientBackend".to_string())).unwrap_or(false);
            if device.id!="default".to_string() && device_type!="none".to_string() && running_backend {            
                let past_messages = device.messages.clone();
                let request_url = format!("https://spark-api.fly.dev/device/{device_type}/{device_id}/", device_type = device_type, device_id = device.id);
                let updated_device: Device = reqwest::blocking::get(&request_url)?.json()?;
                // println!("Getting Updated Device: {:?}", updated_device);
                // println!("_____________________________________________");
                // println!("past Device Messages {:?}", device.messages );
                // println!("updated Device Messages {:?}", updated_device.messages );
                
                if updated_device != device {
                    // println!("updated device different from store");
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
                    let _ =store::set(path.clone(), "device".to_string(), updated_device.to_json_value());
                }
            }
            else { 
                // println!("____________________________");
                // println!("No device or device type set");
            }
            // println!();
            thread::sleep(std::time::Duration::from_secs(10));
            println!("Getting updated device from store");
            device = serde_json::from_value::<Device>(store::get(path.clone(), "device".to_string())).unwrap_or(default_device());
            // println!("Device from store: {:?}", device);
            device_type = serde_json::from_value::<String>(store::get(path.clone(), "deviceType".to_string())).unwrap_or("default".to_string());
        }
    }
}