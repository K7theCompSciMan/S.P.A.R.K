import { ClientDevice, getXataClient, Message, ServerDevice } from "src/xata";
import { configDotenv } from "dotenv";
import { getGroupById, updateGroup } from "./group.db";
import { createMessage } from "./message.db";
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

export const deleteClientDevice = async (ClientDeviceId: string) => {
	return await xata.db.clientDevice.delete(ClientDeviceId);
};

export const getGroupFromClientDevice = async (ClientDevice: ClientDevice) => {
    if (ClientDevice && ClientDevice.assignedGroup) {
        return getGroupById(ClientDevice.assignedGroup.id);
    }
    throw new Error("Server Device not found or not assigned to a group");
}
export const sendMessageToClientFromServer = async (
	serverDevice: ServerDevice,
	messageContent: string,
	clientDevice: ClientDevice
) => {
    const group = await getGroupFromClientDevice(serverDevice);
    const message = await createMessage({ content: messageContent, to: serverDevice.id, from: clientDevice.id } as Message);
    serverDevice.messages.push(message);
    clientDevice.messages.push(message);
    group.messages.push(message);
    await updateClientDevice(serverDevice);
    await updateClientDevice(clientDevice);
    await updateGroup(group);
};
