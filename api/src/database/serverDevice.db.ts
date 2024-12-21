import { ClientDevice, getXataClient, Message } from "src/xata";
import { ServerDevice } from "../xata";
import { configDotenv } from "dotenv";
import { getGroupById, updateGroup } from "./group.db";
import { createMessage } from "./message.db";
import { updateClientDevice } from "./clientDevice.db";
import { Command } from "src/models/command.model";
configDotenv({ path: "../../.env" });
const xata = getXataClient();

export const getAllServerDevices = async () => {
	return (await xata.db.serverDevice.getAll()) as ServerDevice[];
};

export const getServerDeviceById = async (id: string) => {
	return (await getAllServerDevices()).filter(
		(serverDevice) => serverDevice.id === id
	)[0];
};

export const createServerDevice = async (serverDevice?: ServerDevice) => {
	if (serverDevice) return await xata.db.serverDevice.create(serverDevice);
	return await xata.db.serverDevice.create({});
};

export const updateServerDevice = async (serverDevice: ServerDevice) => {
	return await xata.db.serverDevice.update(serverDevice);
};

export const deleteServerDevice = async (serverDeviceId: string) => {
	return await xata.db.serverDevice.delete(serverDeviceId);
};

export const getGroupFromServerDevice = async (serverDevice: ServerDevice) => {
    if (serverDevice && serverDevice.assignedGroup) {
        return getGroupById(serverDevice.assignedGroup.id);
    }
    throw new Error("Server Device not found or not assigned to a group");
}
export const sendMessageToClientFromServer = async (
	serverDevice: ServerDevice,
	messageContent: string,
	clientDevice: ClientDevice
) => {
    const group = await getGroupFromServerDevice(serverDevice);
    const message = await createMessage({ content: messageContent, from: serverDevice.id, to: clientDevice.id, fromDeviceType: "server" } as Message);
    serverDevice.messages.push(message);
    clientDevice.messages.push(message);
    group.messages.push(message);
    await updateServerDevice(serverDevice);
    await updateClientDevice(clientDevice);
    await updateGroup(group);
    return message;
};
export const sendMessageToServerFromServer = async (
	serverDevice: ServerDevice,
	messageContent: string,
	recieverDevice: ServerDevice
) => {
    const group = await getGroupFromServerDevice(serverDevice);
    const message = await createMessage({ content: messageContent, from: serverDevice.id, to: recieverDevice.id, fromDeviceType: "server" } as Message);
    serverDevice.messages.push(message);
    recieverDevice.messages.push(message);
    group.messages.push(message);
    await updateServerDevice(serverDevice);
    await updateServerDevice(recieverDevice);
    await updateGroup(group);
    return message;
};

export const addCommand = async (serverDevice: ServerDevice, command: Command) => {
    serverDevice.deviceCommands.push(command);
    return await updateServerDevice(serverDevice);
}
