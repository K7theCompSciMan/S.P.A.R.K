import type { ClientDevice, Message, ServerDevice } from './xata';

export type Device = {
	name?: string;
	messages?: Message[];
	assignedGroup?: { id: string };
	assignedUser?: { id: string };
	id?: string;
	deviceCommands?: Command[];
	type?: string;
    aliases?: string[];
};

export type PublicUser = {
	username: string;
	id: string;
	settings: UserSettings;
};
export type UserSettings = {
	primaryCommunicationMethod: 'api' | 'nats' | 'localhost';
};

export type Command = {
	command: string;
	name: string;
	aliases: string[];
};

export const deviceToSpecificDevice = (device: Device) => {
	if (device.type === 'client') {
		return {
			name: device.name!,
			messages: device.messages!,
			assignedGroup: device.assignedGroup!,
			assignedUser: device.assignedUser!,
			id: device.id!,
			deviceCommands: device.deviceCommands!,
            aliases: device.aliases!
		} as ClientDevice;
	} else {
		return {
			name: device.name!,
			messages: device.messages!,
			assignedGroup: device.assignedGroup!,
			assignedUser: device.assignedUser!,
			id: device.id!,
			deviceCommands: device.deviceCommands!,
            aliases: device.aliases!
		} as ServerDevice;
	}
};
