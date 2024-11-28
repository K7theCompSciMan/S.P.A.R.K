import { User } from "../xata";

export class  PublicUser{
    id: string;
    username: string;
    settings: UserSettings;

    constructor(user: User){
        this.id = user.id;
        this.username = user.username!;
        this.settings = user.settings!;
    }
}
export class UserSettings{
    primaryCommunicationMethod: string;
    constructor(settings: UserSettings){
        this.primaryCommunicationMethod = settings.primaryCommunicationMethod;
    }
}
export default User