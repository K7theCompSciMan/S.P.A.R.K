// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::{path::PathBuf, sync::{Arc, Mutex}, thread}; // Add this line to import PathBuf

use backend::handle_device_updates_api_call;
use tauri::{self, api::process::{Command, CommandEvent}, EventLoopMessage, Manager};
use tauri_plugin_store::{with_store, StoreBuilder, StoreCollection};
use tauri_runtime_wry::Wry;
mod app;
mod tray;
mod backend;
mod xata_structs;
mod store;
fn main() {
  tauri::Builder::default()
    .plugin(tauri_plugin_store::Builder::default().build())
    .invoke_handler(tauri::generate_handler![app::start_app, app::run_command, store::get_store, store::set_store])
    .system_tray(tray::init_tray())
    .on_system_tray_event(tray::system_tray_event_handler)
    .on_window_event(|event| match event.event() {
      tauri::WindowEvent::CloseRequested { api, .. } => {
        event.window().hide().unwrap();
        api.prevent_close();
      }
      _ => {}
    })
    .setup(|_app| {
      // let store_path = app.path_resolver().resolve_resource("stores/store.json").expect("Failed to resolve resource");
      // let mut back_store = StoreBuilder::new(app.handle(), store_path.clone()).build();
      // let _ = with_store(app.handle(), app.state::<StoreCollection<Wry<EventLoopMessage>>>(), store_path.clone(), |store: &mut tauri_plugin_store::Store<Wry<EventLoopMessage>>| {
      //   let _= store.entries().into_iter().for_each(|(key, value)| {
      //     back_store.insert(key.to_string(), value.clone()).expect("Error inserting to back_store");
      //   });
      //   Ok(())
      // });
      // println!("Store: {:?}", back_store);
      
      let _ = thread::Builder::new().name("handle_device_updates_api_call".to_string()).spawn(move || {
        let _ = handle_device_updates_api_call().expect("Error handling device updates");
      });
      Ok(())
    })
    .build(tauri::generate_context!())
    .expect("error while running tauri application")
    .run(|_app_handle, _event| {}); 

}
