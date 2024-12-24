use serde::{Deserialize, Serialize};
use serde_json::{json, Value}; // Import the `json` macro from the `serde_json` crate


#[derive(Deserialize, Debug, Clone, PartialEq)]
pub struct Device {
    pub name: String,
    pub id: String,
    pub assignedUser: AssignedUser ,
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
        "deviceCommands": self.deviceCommands,
    })
}
}

#[derive(Serialize, Deserialize, Debug, Clone, PartialEq)]
pub struct User {
    pub id: String,
    pub username: String,
    pub settings: UserSettings,
}

#[derive(Serialize, Deserialize, Debug, Clone, PartialEq)]
pub struct AssignedUser {
    pub id: String
}
#[derive(Serialize, Deserialize, Debug, Clone, PartialEq)]
pub struct UserSettings {
    pub primaryCommunicationMethod: String
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
    pub name: String,
    pub aliases: Vec<String>,
    pub command: String
}

impl PartialEq for Command {
    fn eq(&self, other: &Self) -> bool {
        self.name == other.name
            && self.command == other.command
            && self.aliases == other.aliases
    }
}
