use tauri::{AppHandle, CustomMenuItem, Manager as _, SystemTray, SystemTrayEvent, SystemTrayMenu, SystemTrayMenuItem};

pub fn init_tray() -> SystemTray {
    let system_tray = SystemTray::new();
    
    let quit = CustomMenuItem::new("quit", "Quit");
    let hide = CustomMenuItem::new("hide", "Hide GUI");
    let show = CustomMenuItem::new("show", "Show GUI");
    let tray_menu = SystemTrayMenu::new()
        .add_item(quit)
        .add_native_item(SystemTrayMenuItem::Separator)
        .add_item(hide)
        .add_native_item(SystemTrayMenuItem::Separator)
        .add_item(show);
    
    system_tray.with_menu(tray_menu)
}

pub fn system_tray_event_handler(app: &AppHandle, event: SystemTrayEvent) {
    match event {
        SystemTrayEvent::MenuItemClick { id, .. } => {
            match id.as_str() {
            "quit" => {
                app.exit(0);
            }
            "hide" => {
                app.get_window("main").unwrap().hide().unwrap();
            }
            "show" => {
                app.get_window("main").unwrap().show().unwrap();
            }
            _ => {}
            }
        }
            _ => {}
    }
}