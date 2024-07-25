// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::{borrow::BorrowMut, path::PathBuf, sync::{Arc, Mutex, MutexGuard}, thread}; // Add this line to import PathBuf

use backend::handle_device_updates;
use tauri::{self, async_runtime::handle, AppHandle, EventLoopMessage, Manager, Wry};
use tauri_plugin_store::{with_store, Store, StoreBuilder, StoreCollection};
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
    })
    .setup(|app| {
      let store = StoreBuilder::new(app.handle(), "C:/Code/S.P.A.R.K/client/stores/store.json".parse()?).build();
      
      thread::spawn(move || {
        let store = Arc::new(Mutex::new(store));
        handle_device_updates(store).expect("Error handling device updates");
      });
      Ok(())
    })
    .build(tauri::generate_context!())
    .expect("error while running tauri application")
    .run(|_app_handle, _event| {}); 

}
