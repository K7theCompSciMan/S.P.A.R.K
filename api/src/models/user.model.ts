import { User } from "../xata";

export class  PublicUser{
    id: string;
    username: string;

    constructor(user: User){
        this.id = user.id;
        this.username = user.username;
    }
}
export default User