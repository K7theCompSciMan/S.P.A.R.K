use json::JsonValue::Null;
use serde::{Deserialize, Serialize};
use serde_json::{json, Value}; // Import the `json` macro from the `serde_json` crate


#[derive(Deserialize, Debug, Clone, PartialEq)]
pub struct Device {
    pub name: String,
    pub id: String,
    pub assignedUser: User,
    pub assignedGroup: Group,
    pub messages: Vec<Message>,
    pub deviceCommands: Vec<Command>,

}
impl Device {
pub fn to_json_value(&self) -> Value {
    json!({
        "name": self.name,
        "id": self.id,
        "assignedUser": self.assignedUser,
        "assignedGroup": self.assignedGroup,
        "messages": self.messages,
        "commands": self.deviceCommands,
    })
}
}
#[derive(Serialize, Deserialize, Debug, Clone, PartialEq)]
pub struct User {
    pub id: String
}

#[derive(Serialize, Deserialize, Debug, Clone, PartialEq)]
pub struct Group {
    pub id: String
}

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct Message {
    pub id: String,
    pub from: String,
    pub to: String,
    pub status: Option<i8>,
    pub content: String,
    pub fromDeviceType: String,
}

impl PartialEq for Message {
    fn eq(&self, other: &Self) -> bool {
        self.id == other.id
            && self.from == other.from
            && self.to == other.to
            && self.status == other.status
            && self.content == other.content
            && self.fromDeviceType == other.fromDeviceType
    }
}

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct Command {
    pub alias: String,
    pub command: String
}

impl PartialEq for Command {
    fn eq(&self, other: &Self) -> bool {
        self.alias == other.alias
            && self.command == other.command
    }
}
