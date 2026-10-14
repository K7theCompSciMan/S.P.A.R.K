use std::process::Command;

/// Opens an application by name.
/// On macOS: uses `open -a <app>`
/// On Windows: uses `cmd /C start <app>`
/// On Linux: uses `xdg-open <app>`
#[tauri::command]
pub fn start_app(application: &str) {
    #[cfg(target_os = "macos")]
    {
        let output = Command::new("open")
            .args(["-a", application])
            .output()
            .expect("failed to execute process");
        println!("output: {:?}", output);
    }

    #[cfg(target_os = "windows")]
    {
        let output = Command::new("cmd")
            .args(["/C", &format!("start {}", application)])
            .output()
            .expect("failed to execute process");
        println!("output: {:?}", output);
    }

    #[cfg(target_os = "linux")]
    {
        let output = Command::new("xdg-open")
            .arg(application)
            .output()
            .expect("failed to execute process");
        println!("output: {:?}", output);
    }
}

/// Runs a shell command string.
/// On macOS/Linux: uses `sh -c <command>`
/// On Windows: uses `cmd /C <command>`
#[tauri::command]
pub fn run_command(command: &str) {
    println!("running Command: {}", command);

    #[cfg(any(target_os = "macos", target_os = "linux"))]
    {
        let output = Command::new("sh")
            .args(["-c", command])
            .output()
            .expect("failed to execute process");
        println!("output: {:?}", output);
    }

    #[cfg(target_os = "windows")]
    {
        let output = Command::new("cmd")
            .args(["/C", command])
            .output()
            .expect("failed to execute process");
        println!("output: {:?}", output);
    }
}