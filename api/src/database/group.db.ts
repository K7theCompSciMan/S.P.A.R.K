import { configDotenv } from "dotenv";
import { ClientDevice, Group, ServerDevice } from "../xata";
import { getXataClient } from "../xata";
import { Command } from "src/models/command.model";
import log from "src/utils/logger";
import { getServerDeviceById, addCommand as addCommandToServer} from "./serverDevice.db";
import { addCommand, getClientDeviceById } from "./clientDevice.db";
configDotenv({ path: "../../.env" });
const xata = getXataClient();

export const getAllGroups = async () => {
	return (await xata.db.group.getAll()) as Group[];
};

export const getGroupById = async (id: string) => {
	return (await getAllGroups()).filter((group) => group.id === id)[0];
};

export const getGroupsByUserId = async (userId: string) => {
	return (await getAllGroups()).filter(
		(group) => group.assignedUser?.id === userId
	);
};

export const createGroup = async (group?: Group) => {
	if (group) return await xata.db.group.create(group);
	return await xata.db.group.create({});
};

export const addDeviceToGroup = async (
	groupId: string,
	deviceId: string,
	deviceType: string
) => {
	const group = await getGroupById(groupId);
	if (group) {
		if (group.devices[deviceType].includes(deviceId)) {
			return "Device Already in Group";
		}
		group.devices[deviceType].push(deviceId);
		return await updateGroup(group);
	}
	return null;
};

export const updateGroup = async (group: Group) => {
	return await xata.db.group.update(group);
};

export const addCommandToGroup = async (group: Group, command: Command) => {
	group.groupCommands.push({ ...command } as Command);
	let servers = group.devices["server"] as string[];
	let clients = group.devices["client"] as string[];
	log.info(`groupCommands: ${group.groupCommands}`);
	servers.forEach(async (serverId: string) => {
		const server = await getServerDeviceById(serverId);
		log.info(`Adding command to server ${server.id}`);
		await addCommandToServer(server, command);
	});
	clients.forEach(async (clientId: string) => {
		const client = await getClientDeviceById(clientId);
		log.info(`Adding command to client ${client.id}`);
		await addCommand(client, command);
	});
	return await updateGroup(group);
};

export const deleteGroup = async (groupId: string) => {
	return await xata.db.group.delete(groupId);
};
