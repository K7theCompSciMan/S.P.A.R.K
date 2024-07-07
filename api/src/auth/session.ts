import { PublicUser } from "../models/user.model";

export class Session {
    user: PublicUser;
    valid: boolean = true;
    dateCreated: Date;
    endDate: Date;
    constructor(user: PublicUser){
        this.user = user;
        this.dateCreated = new Date(Date.now());
        this.endDate= new Date(Date.now() + 1000 * 60 * 60 * 24 * 7)
        this.valid = true;
    }
    invalidate(){
        this.valid = false;
    }

}
