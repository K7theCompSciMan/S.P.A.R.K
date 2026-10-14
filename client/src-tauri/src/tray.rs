use tauri::{
    AppHandle, CustomMenuItem, Manager as _, SystemTray, SystemTrayEvent, SystemTrayMenu,
    SystemTrayMenuItem,
};

pub fn init_tray() -> SystemTray {
    let quit = CustomMenuItem::new("quit", "Quit");
    let hide = CustomMenuItem::new("hide", "Hide");
    let show = CustomMenuItem::new("show", "Show");

    let tray_menu = SystemTrayMenu::new()
        .add_item(quit)
        .add_native_item(SystemTrayMenuItem::Separator)
        .add_item(show)
        .add_native_item(SystemTrayMenuItem::Separator)
        .add_item(hide);

    SystemTray::new().with_menu(tray_menu)
}

pub fn system_tray_event_handler(app: &AppHandle, event: SystemTrayEvent) {
    match event {
        SystemTrayEvent::MenuItemClick { id, .. } => match id.as_str() {
            "quit" => {
                app.exit(0);
            }
            "hide" => {
                if let Some(w) = app.get_window("main") {
                    let _ = w.hide();
                }
            }
            "show" => {
                if let Some(w) = app.get_window("main") {
                    let _ = w.show();
                    let _ = w.set_focus();
                }
            }
            _ => {}
        },
        SystemTrayEvent::LeftClick { .. } => {
            if let Some(window) = app.get_window("main") {
                // On macOS left-click on the menu-bar icon should toggle visibility.
                // On other platforms we just show/focus.
                #[cfg(target_os = "macos")]
                {
                    match window.is_visible() {
                        Ok(true) => {
                            let _ = window.hide();
                            return;
                        }
                        _ => {}
                    }
                }
                let _ = window.show();
                let _ = window.set_focus();
            }
        }
        _ => {}
    }
}