// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::{path::PathBuf, sync::{Arc, Mutex, MutexGuard}, thread}; // Add this line to import PathBuf

use backend::handle_device_updates;
use tauri::{self, AppHandle, Manager, Wry};
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
    })
    .setup(|app| Ok({
      let arc_app_handle = Arc::new(Mutex::new(app.app_handle().clone())).clone();
      
      thread::spawn(move || {
          let app_handle: MutexGuard<AppHandle> = match arc_app_handle.lock() {
              Ok(guard) => guard,
              Err(poisoned) => {
                  // Handle mutex poisoning
                  let guard = poisoned.into_inner();
                  println!("Thread recovered from mutex poisoning: {:?}", *guard);
                  guard
              }
          };
          with_store(app_handle.clone(),
          app_handle.clone().state::<StoreCollection<Wry>>(), 
          PathBuf::from("C:/Code/S.P.A.R.K/stores/store.json"), 
          |store| Ok({
              let store = Arc::new(Mutex::new(store));  
              handle_device_updates(store).unwrap();
          }))
      });
    }))
    .run(tauri::generate_context!())
    .expect("error while running tauri application");

}
