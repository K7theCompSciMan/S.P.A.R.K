import type { ClientDevice, Message, ServerDevice } from './supabase';

export type Device = {
	name?: string;
	messages?: Message[];
	assignedGroup?: { id: string };
	assigned_group_id?: string;
	assignedUser?: { id: string };
	assigned_user_id?: string;
	id?: string;
	deviceCommands?: Command[];
	device_commands?: Command[];
	type?: string;
	aliases?: string[];
};

export type PublicUser = {
	id: string;
	email: string;
	username: string;
	settings: UserSettings;
};
export type UserSettings = {
	primaryCommunicationMethod: 'api' | 'nats' | 'localhost' | 'realtime';
};

export type Command = {
	command: string;
	name: string;
	aliases: string[];
};

export const deviceToSpecificDevice = (device: Device): Partial<ClientDevice | ServerDevice> => ({
	name: device.name!,
	messages: device.messages!,
	assigned_group_id: device.assignedGroup?.id ?? device.assigned_group_id ?? '',
	assigned_user_id: device.assignedUser?.id ?? device.assigned_user_id ?? '',
	id: device.id!,
	device_commands: device.deviceCommands ?? device.device_commands ?? [],
	aliases: device.aliases ?? []
});