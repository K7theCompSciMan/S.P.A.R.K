// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::{path::PathBuf, sync::{Arc, Mutex}, thread}; // Add this line to import PathBuf

use client::handle_device_updates;
use tauri::{self, EventLoopMessage, Manager};
use tauri_plugin_store::{with_store, StoreBuilder, StoreCollection};
use tauri_runtime_wry::Wry;
mod app;
mod tray;
mod client;
mod xata_structs;
mod server;
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
      let store_path = app.path_resolver().resolve_resource("stores/store.json").expect("Failed to resolve resource");
      let mut back_store = StoreBuilder::new(app.handle(), store_path.clone()).build();
      let _ = with_store(app.handle(), app.state::<StoreCollection<Wry<EventLoopMessage>>>(), store_path.clone(), |store| {
        let _= store.entries().into_iter().for_each(|(key, value)| {
          back_store.insert(key.to_string(), value.clone()).expect("Error inserting to back_store");
        });
        Ok(())
      });
      // println!("Store: {:?}", back_store);
      // thread::spawn(move || {
      //   let store = Arc::new(Mutex::new(back_store));
      //   handle_device_updates(store).expect("Error handling device updates");
      // });
      Ok(())
    })
    .build(tauri::generate_context!())
    .expect("error while running tauri application")
    .run(|_app_handle, _event| {}); 

}
