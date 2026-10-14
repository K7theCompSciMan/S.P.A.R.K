// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::thread;
use tauri::{self, Manager};

mod app;
mod backend;
mod store;
mod tray;
mod xata_structs;

/// Called from the frontend after a successful login so the Rust backend
/// can start (or restart) the Realtime subscription with fresh credentials.
#[tauri::command]
fn init_realtime() {
    thread::Builder::new()
        .name("supabase-realtime".to_string())
        .spawn(|| {
            if let Err(e) = backend::handle_device_updates_api_call() {
                println!("[backend] Realtime init error: {e}");
            }
        })
        .ok();
}

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_store::Builder::default().build())
        .invoke_handler(tauri::generate_handler![
            app::start_app,
            app::run_command,
            store::get_store,
            store::set_store,
            init_realtime,
        ])
        .system_tray(tray::init_tray())
        .on_system_tray_event(tray::system_tray_event_handler)
        .on_window_event(|event| {
            if let tauri::WindowEvent::CloseRequested { api, .. } = event.event() {
                event.window().hide().unwrap();
                api.prevent_close();
            }
        })
        .build(tauri::generate_context!())
        .expect("error while running tauri application")
        .run(|_app_handle, _event| {});
}