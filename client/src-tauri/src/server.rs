use std::os::windows::thread;

use pv_recorder::PvRecorderBuilder;

pub fn handle_sample() {
    
}

pub fn read_audio() {

}

pub fn record_audio() {
    
}

pub fn setup()  {
    let frame_length = 512;
    let recorder = PvRecorderBuilder::new(frame_length).init()?;
    recorder.start()?;
    while recorder.is_recording() {
        let frame = recorder.read()?;
        println!("frame {:?}", frame);
    }
    thread::sleep(Duration::from_secs(5));
    recorder.stop()?;
}

pub async fn transcribe_audio() {

}

pub async fn handle_server_updates() {
    
}