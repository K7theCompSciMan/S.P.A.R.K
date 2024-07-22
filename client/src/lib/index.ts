export type Device = {
    name?:string,
    messages?: string ,
    assignedGroup?: { id: string} ,
    assignedUser?: { id: string},
    id?: string
}

export type PublicUser = {
    username: string,
    id: string
}

export type Command = {
    command: string,
    alias: string,
}
