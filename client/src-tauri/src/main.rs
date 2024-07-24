// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::{borrow::Borrow, sync::{Arc}, thread};
use std::path::PathBuf; // Add this line to import PathBuf

use backend::handle_device_updates;
use tauri::{self, App, EventLoopMessage, Manager, Wry};
use tauri_plugin_store::{with_store, StoreCollection};
mod app;
mod tray;
mod backend;
mod xata_structs;
fn main() {
  tauri::Builder::default()
    .plugin(tauri_plugin_store::Builder::default().build())
    .invoke_handler(tauri::generate_handler![app::start_app, app::run_command])
    .system_tray(tray::init_tray())
    .on_system_tray_event(tray::system_tray_event_handler)
    .on_window_event(|event| match event.event() {
      tauri::WindowEvent::CloseRequested { api, .. } => {
        event.window().hide().unwrap();
        api.prevent_close();
      }
      _ => {}
    }).setup(|app| Ok({
      let _store = with_store(app.app_handle(), app.state::<StoreCollection>(),  PathBuf::from("C:/Code/S.P.A.R.K/client/stores/store.json"), |store| {
        handle_device_updates<Wry<EventLoopMessage>>(store);
      }).expect("failed to handle device updates");
    }))
    .run(tauri::generate_context!())
    .expect("error while running tauri application");

}
