export type Device = {
    name?:string,
    messages?: string ,
    assignedGroup?: { id: string} ,
    assignedUser?: { id: string},
    id?: string,
    deviceCommands?: Command[],
}

export type PublicUser = {
    username: string,
    id: string,
    settings: UserSettings,
}
export type UserSettings= {
    primaryCommunicationMethod: 'api' | 'nats' | 'localhost',
}

export type Command = {
    command: string,
    name: string,
    aliases: string[],
}
