use std::process::Command;




#[tauri::command]
pub fn start_app(application: &str) {
  // let launchphrase = format!("start {}!", application);
  let output =Command::new("cmd")
.args(["/C", format!("start {}", application).as_mut_str()])
.output()
.expect("failed to execute process, application likely not in start menu");
println!("output: {:?}", output);

}