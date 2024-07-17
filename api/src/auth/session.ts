import { Device } from "src/models/device.model";
import { PublicUser } from "../models/user.model";

export class Session {
    user: PublicUser;
    device: Device;
    valid: boolean = true;
    dateCreated: Date;
    endDate: Date;
    constructor(user: PublicUser, device: Device){
        this.user = user;
        this.dateCreated = new Date(Date.now());
        this.endDate= new Date(Date.now() + 1000 * 60 * 60 * 24 * 7)
        this.valid = true;
        this.device = device;
    }
    invalidate(){
        this.valid = false;
    }

}
