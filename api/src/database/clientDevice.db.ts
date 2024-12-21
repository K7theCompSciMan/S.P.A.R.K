import { ClientDevice, getXataClient, Message, ServerDevice } from "src/xata";
import { configDotenv } from "dotenv";
import { getGroupById, updateGroup } from "./group.db";
import { createMessage, deleteMessage } from "./message.db";
import { Command } from "src/models/command.model";
import { getGroupFromServerDevice, updateServerDevice } from "./serverDevice.db";
configDotenv({ path: "../../.env" });
const xata = getXataClient();

export const getAllClientDevices = async () => {
	return (await xata.db.clientDevice.getAll()) as ClientDevice[];
};

export const getClientDeviceById = async (id: string) => {
	return (await getAllClientDevices()).filter(
		(ClientDevice) => ClientDevice.id === id
	)[0];
};

export const createClientDevice = async (ClientDevice?: ClientDevice) => {
	if (ClientDevice) return await xata.db.clientDevice.create(ClientDevice);
	return await xata.db.clientDevice.create({});
};

export const updateClientDevice = async (ClientDevice: ClientDevice) => {
	return await xata.db.clientDevice.update(ClientDevice);
};
export const getMessagesFromClientDeviceId = async (clientDeviceId: string) => {
	return (await getClientDeviceById(clientDeviceId)).messages as Message[];
};

export const deleteClientDevice = async (ClientDeviceId: string) => {
	const messages = await getMessagesFromClientDeviceId(ClientDeviceId);
	messages.forEach((m) => deleteMessage(m.id));
	return await xata.db.clientDevice.delete(ClientDeviceId);
};

export const getGroupFromClientDevice = async (ClientDevice: ClientDevice) => {
	if (ClientDevice && ClientDevice.assignedGroup) {
		return getGroupById(ClientDevice.assignedGroup.id);
	}
	throw new Error("Server Device not found or not assigned to a group");
};
export const sendMessageToServerFromClient = async (
	serverDevice: ServerDevice,
	messageContent: string,
	clientDevice: ClientDevice
) => {
	const group = await getGroupFromServerDevice(serverDevice);
	const message = await createMessage({
		content: messageContent,
		to: serverDevice.id,
		from: clientDevice.id,
		fromDeviceType: "client",
	} as Message);
	serverDevice.messages.push(message);
	clientDevice.messages.push(message);
	group.messages.push(message);
	await updateServerDevice(serverDevice);
	await updateClientDevice(clientDevice);
	await updateGroup(group);
	return message;
};

export const addCommand = async (
	clientDevice: ClientDevice,
	command: Command
) => {
	clientDevice.deviceCommands.push(command);
	return await updateClientDevice(clientDevice);
};
