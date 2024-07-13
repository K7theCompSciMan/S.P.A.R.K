import { Message, getXataClient } from "src/xata";
import { configDotenv } from "dotenv";
import * as client from "./clientDevice.db";
import * as server from "./serverDevice.db";
import { updateGroup } from "./group.db";
import log from "src/utils/logger";
configDotenv({ path: "../../.env" });
const xata = getXataClient();

export const getAllMessages = async () => {
	return (await xata.db.message.getAll()) as Message[];
};

export const getMessageById = async (id: string) => {
	return (await getAllMessages()).filter((message) => message.id === id)[0];
};

export const createMessage = async (message?: Message) => {
	if (message) return await xata.db.message.create(message);
	return await xata.db.message.create({});
};

export const updateMessage = async (message: Message) => {
	return await xata.db.message.update(message);
};

export const deleteMessage = async (messageId: string) => {
	log.info(`Deleting message with id: ${messageId}`);
	const message = await getMessageById(messageId);
    let updatedClientDevice;
    let updatedServerDevice;
    let updatedGroup;
	if (message.fromDeviceType === "client") {
		log.info(`Deleting message which is from client`);
		const clientDevice = await client.getClientDeviceById(message.from!);
		const serverDevice = await server.getServerDeviceById(message.to!);
		if (clientDevice) {
			log.info(`Deleting message from client`);
			const newMessages = clientDevice.messages.filter(
				(msg: Message) => msg.id !== message.id
			);
			updatedClientDevice = await client.updateClientDevice({...clientDevice, messages: newMessages});
		}
		if (serverDevice) {
			log.info(`Deleting message from server`);
			const newMessages = serverDevice.messages.filter(
				(msg: Message) => msg.id !== message.id
			);
			updatedServerDevice = await server.updateServerDevice({...serverDevice, messages: newMessages});
		}
		const group = await server.getGroupFromServerDevice(serverDevice);
		if (group) {
			log.info(`Deleting message from group`);
			const newMessages = group.messages.filter(
				(msg: Message) => msg.id !== message.id
			);
			updatedGroup = await updateGroup({...group, messages: newMessages});
		}
	} else {
		log.info(`Deleting message which is from server`);
		const serverDevice = await server.getServerDeviceById(message.from!);
		const clientDevice = await client.getClientDeviceById(message.to!);
		if (clientDevice) {
			log.info(`Deleting message from client`);
			const newMessages = clientDevice.messages.filter((msg: Message) => {
				msg.id !== message.id;
			});
			log.info(`filtereed message from client`);
			updatedClientDevice = await client.updateClientDevice({...clientDevice, messages: newMessages});
			log.info(`updated client`);
		}
		if (serverDevice) {
			log.info(`Deleting message from server`);
			const newMessages = serverDevice.messages.filter(
				(msg: Message) => msg.id !== message.id
			);
			updatedServerDevice = await server.updateServerDevice({...serverDevice, messages: newMessages});
		}
		const group = await server.getGroupFromServerDevice(serverDevice);
		if (group) {
			const newMessages = group.messages.filter(
				(msg: Message) => msg.id !== message.id
			);
			updatedGroup = await updateGroup({...group, messages: newMessages});
		}
		log.info(`Deleting message from group`);
	}

	return {deleted: await xata.db.message.delete(messageId), updatedClientDevice, updatedServerDevice, updatedGroup};
};
