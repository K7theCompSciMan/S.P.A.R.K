import { ClientDevice, ServerDevice } from "src/xata";

export class Device {
    id: string;
    name: string;
    messages: string;
    assignedGroup?: string;
    assignedUser?: string;
    type: string;
    constructor(device: ClientDevice | ServerDevice, type: string){
        this.id = device.id;
        this.name = device.name!;
        this.messages = device.messages;
        this.assignedGroup = device.assignedGroup?.id;
        this.assignedUser = device.assignedUser?.id;
        this.type = type;
    }
}