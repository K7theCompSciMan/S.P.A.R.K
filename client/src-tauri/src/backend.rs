//! backend.rs — Supabase Realtime listener
//!
//! Subscribes to the `client_devices` and `server_devices` Postgres tables via
//! Supabase Realtime (websocket) so the app reacts to pushed updates instantly
//! instead of polling or using NATS.
//!
//! The Supabase Realtime client is a plain WebSocket speaking the Phoenix
//! channel protocol, so we use the `tungstenite` crate — no NATS dependency.

use std::thread;
use crate::{app::run_command, store, xata_structs::{Device, User, AssignedUser, Group, UserSettings}};
use serde::Deserialize;
use serde_json::Value;

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

fn resolve_store_path() -> String {
    if let Some(proj_dirs) = directories::ProjectDirs::from("com", "spark", "ai.assistant") {
        let data_dir = proj_dirs.data_dir();
        std::fs::create_dir_all(data_dir).ok();
        data_dir
            .join("stores")
            .join("store.json")
            .to_string_lossy()
            .to_string()
    } else {
        "stores/store.json".to_string()
    }
}

fn default_device() -> Device {
    Device {
        name: "default".to_string(),
        id: "default".to_string(),
        assignedUser: AssignedUser { id: "default".to_string() },
        assignedGroup: Group { id: "default".to_string() },
        messages: vec![],
        deviceCommands: vec![],
    }
}

fn default_user() -> User {
    User {
        id: "default".to_string(),
        username: "default".to_string(),
        settings: UserSettings {
            primaryCommunicationMethod: "realtime".to_string(),
        },
    }
}

// ---------------------------------------------------------------------------
// Realtime payload shape from Supabase
// ---------------------------------------------------------------------------

#[derive(Deserialize, Debug)]
struct RealtimePayload {
    #[serde(rename = "type")]
    event_type: Option<String>,
    payload: Option<RealtimeRecord>,
}

#[derive(Deserialize, Debug)]
struct RealtimeRecord {
    record: Option<Value>,
}

// ---------------------------------------------------------------------------
// Supabase Realtime subscription via raw WebSocket
// ---------------------------------------------------------------------------
//
// Supabase Realtime speaks the Phoenix channel wire protocol over a WS URL:
//   wss://<project>.supabase.co/realtime/v1/websocket?apikey=<anon_key>&vsn=1.0.0
//
// We join the topic `realtime:public:client_devices:id=eq.<device_id>` so we
// only receive rows that belong to *this* device, avoiding unnecessary traffic.

fn realtime_url(supabase_url: &str, anon_key: &str) -> String {
    let base = supabase_url
        .trim_end_matches('/')
        .replace("https://", "wss://")
        .replace("http://", "ws://");
    format!(
        "{base}/realtime/v1/websocket?apikey={anon_key}&vsn=1.0.0",
    )
}

fn join_message(topic: &str, ref_id: u64) -> String {
    serde_json::json!({
        "topic": topic,
        "event": "phx_join",
        "payload": {
            "config": {
                "broadcast": { "self": false },
                "presence": { "key": "" },
                "postgres_changes": [
                    {
                        "event": "UPDATE",
                        "schema": "public",
                        "table": "client_devices",
                        "filter": ""   // filled in per-device below
                    }
                ]
            }
        },
        "ref": ref_id.to_string()
    })
    .to_string()
}

fn heartbeat_message(ref_id: u64) -> String {
    serde_json::json!({
        "topic": "phoenix",
        "event": "heartbeat",
        "payload": {},
        "ref": ref_id.to_string()
    })
    .to_string()
}

/// Spawns the Realtime listener on a background thread.
/// Reads `supabaseUrl` and `supabaseAnonKey` from the Tauri store so the
/// Rust side never needs them hard-coded.
pub fn handle_device_updates_api_call() -> Result<(), Box<dyn std::error::Error>> {
    let path = resolve_store_path();

    let supabase_url = store::get(path.clone(), "supabaseUrl".to_string())
        .as_str()
        .unwrap_or_default()
        .to_string();
    let anon_key = store::get(path.clone(), "supabaseAnonKey".to_string())
        .as_str()
        .unwrap_or_default()
        .to_string();

    // If the store doesn't have the keys yet (first launch before login),
    // just return — the frontend will call into Rust once the user logs in.
    if supabase_url.is_empty() || anon_key.is_empty() {
        println!("[backend] Supabase keys not in store yet, skipping Realtime setup.");
        return Ok(());
    }

    let device: Device = serde_json::from_value(store::get(path.clone(), "device".to_string()))
        .unwrap_or_else(|_| default_device());

    if device.id == "default" || device.id.is_empty() {
        println!("[backend] No device registered yet, skipping Realtime setup.");
        return Ok(());
    }

    let device_id = device.id.clone();
    let ws_url = realtime_url(&supabase_url, &anon_key);

    thread::Builder::new()
        .name("supabase-realtime".to_string())
        .spawn(move || {
            run_realtime_loop(ws_url, device_id, path, device);
        })?;

    Ok(())
}

fn run_realtime_loop(ws_url: String, device_id: String, path: String, mut current_device: Device) {
    use tungstenite::{connect, Message as WsMessage};

    loop {
        println!("[realtime] Connecting to Supabase Realtime…");
        match connect(&ws_url) {
            Err(e) => {
                println!("[realtime] Connection failed: {e}. Retrying in 5s…");
                thread::sleep(std::time::Duration::from_secs(5));
                continue;
            }
            Ok((mut socket, _)) => {
                println!("[realtime] Connected.");

                // Join the channel filtered to this device's row
                let table = "client_devices";
                let topic = format!("realtime:public:{table}:id=eq.{device_id}");
                let join = join_message(&topic, 1);
                if socket.send(WsMessage::Text(join)).is_err() {
                    continue;
                }

                let mut heartbeat_ref: u64 = 2;
                let mut last_heartbeat = std::time::Instant::now();

                loop {
                    // Send a heartbeat every 30 s to keep the socket alive
                    if last_heartbeat.elapsed() > std::time::Duration::from_secs(30) {
                        let hb = heartbeat_message(heartbeat_ref);
                        heartbeat_ref += 1;
                        if socket.send(WsMessage::Text(hb)).is_err() {
                            println!("[realtime] Lost connection during heartbeat, reconnecting…");
                            break;
                        }
                        last_heartbeat = std::time::Instant::now();
                    }

                    // Non-blocking read
                    match socket.read() {
                        Err(tungstenite::Error::Io(ref e))
                            if e.kind() == std::io::ErrorKind::WouldBlock =>
                        {
                            thread::sleep(std::time::Duration::from_millis(200));
                            continue;
                        }
                        Err(e) => {
                            println!("[realtime] Read error: {e}, reconnecting…");
                            break;
                        }
                        Ok(WsMessage::Text(text)) => {
                            handle_realtime_message(&text, &mut current_device, &path);
                        }
                        Ok(WsMessage::Ping(data)) => {
                            let _ = socket.send(WsMessage::Pong(data));
                        }
                        Ok(WsMessage::Close(_)) => {
                            println!("[realtime] Server closed connection, reconnecting…");
                            break;
                        }
                        _ => {}
                    }
                }

                thread::sleep(std::time::Duration::from_secs(3));
            }
        }
    }
}

fn handle_realtime_message(text: &str, current_device: &mut Device, path: &str) {
    let Ok(msg) = serde_json::from_str::<Value>(text) else { return };

    // Only handle postgres_changes UPDATE events
    let event = msg.get("event").and_then(|v| v.as_str()).unwrap_or("");
    if event != "postgres_changes" {
        return;
    }

    let Some(payload) = msg.get("payload") else { return };
    let Some(data) = payload.get("data") else { return };
    let Some(record) = data.get("record") else { return };

    // Parse the updated device record
    let Ok(updated_device) = serde_json::from_value::<Device>(record.clone()) else {
        println!("[realtime] Could not parse device record from Realtime payload");
        return;
    };

    // Check for new messages with run commands
    if updated_device.messages.len() > current_device.messages.len() {
        if let Some(new_msg) = updated_device.messages.last() {
            if new_msg.content.contains("[RUN COMMAND]") {
                for command in &updated_device.deviceCommands {
                    if format!("[RUN COMMAND] {}", command.name) == new_msg.content {
                        println!("[realtime] Running command: {}", command.command);
                        run_command(&command.command);
                    }
                }
            }
        }
    }

    // Persist updated device to store so the UI can react
    store::set(
        path.to_string(),
        "device".to_string(),
        updated_device.to_json_value(),
    );
    *current_device = updated_device;
    println!("[realtime] Device state updated from Realtime push.");
}