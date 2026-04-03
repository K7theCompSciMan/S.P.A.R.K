import * as client from "../database/clientDevice.db";
import * as server from "../database/serverDevice.db";
import { ClientDevice, ServerDevice, User } from "../xata";
import { getGroupById } from "../database/group.db";
import { deleteMessage, getMessageById } from "../database/message.db";
import { Command } from "../models/command.model";
import log from "../utils/logger";

export async function listAllDevices() {
	const clientDevices = await client.getAllClientDevices();
	const serverDevices = await server.getAllServerDevices();
	if (clientDevices && serverDevices) {
		return { ok: true as const, body: { clientDevices, serverDevices } };
	}
	return { ok: false as const, error: "No devices found" as const };
}

export async function listClientDevices() {
	const clientDevices = await client.getAllClientDevices();
	if (clientDevices) {
		return { ok: true as const, body: clientDevices };
	}
	return { ok: false as const, error: "No client devices found" as const };
}

export async function listServerDevices() {
	const serverDevices = await server.getAllServerDevices();
	if (serverDevices) {
		return { ok: true as const, body: serverDevices };
	}
	return { ok: false as const, error: "No server devices found" as const };
}

export async function getClientDevice(id: string) {
	const clientDevice = await client.getClientDeviceById(id);
	if (clientDevice) {
		return { ok: true as const, body: clientDevice };
	}
	return { ok: false as const, error: "Device not found" as const };
}

export async function getServerDevice(id: string) {
	const serverDevice = await server.getServerDeviceById(id);
	if (serverDevice) {
		return { ok: true as const, body: serverDevice };
	}
	return { ok: false as const, error: "Device not found" as const };
}

export async function createClientDevice(body: {
	name: string;
	assignedGroupId: string;
	user: User;
}) {
	const { name, assignedGroupId, user } = body;
	const group = await getGroupById(assignedGroupId);
	if (!group) {
		log.info(`Group not found`);
		return { ok: false as const, status: 404 as const, error: "Group not found" };
	}
	const clientDevice = await client.createClientDevice({
		name,
		aliases: [name],
		assignedGroup: assignedGroupId,
		assignedUser: user,
	} as unknown as ClientDevice);
	if (!clientDevice) {
		return {
			ok: false as const,
			status: 500 as const,
			error: "Failed to create device",
		};
	}
	return { ok: true as const, status: 201 as const, body: clientDevice };
}

export async function createServerDevice(body: {
	name: string;
	assignedGroupId: string;
	user: User;
}) {
	const { name, assignedGroupId, user } = body;
	const group = await getGroupById(assignedGroupId);
	if (!group) {
		log.info(`Group not found`);
	}
	const serverDevice = await server.createServerDevice({
		name,
		aliases: [name],
		assignedGroup: group,
		assignedUser: user,
	} as unknown as ServerDevice);
	if (!serverDevice) {
		return {
			ok: false as const,
			status: 500 as const,
			error: "Failed to create device",
		};
	}
	return { ok: true as const, status: 201 as const, body: serverDevice };
}

export async function sendServerToDeviceMessage(body: {
	serverDeviceId: string;
	messageContent: string;
	recieverDeviceId: string;
	user: User;
}) {
	const { serverDeviceId, messageContent, recieverDeviceId, user } = body;
	if (!serverDeviceId || !messageContent || !recieverDeviceId) {
		return { ok: false as const, status: 400 as const, error: "Invalid request" };
	}
	const serverDevice = await server.getServerDeviceById(serverDeviceId);
	let receiverDeviceClient = await client.getClientDeviceById(recieverDeviceId);
	let receiverDevice: ClientDevice | ServerDevice | undefined;
	let deviceType = "client";
	if (!receiverDeviceClient) {
		let receiverDeviceServer = await server.getServerDeviceById(
			recieverDeviceId
		);
		deviceType = "server";
		receiverDevice = receiverDeviceServer ?? undefined;
	} else {
		receiverDevice = receiverDeviceClient;
	}
	if (!serverDevice || !receiverDevice) {
		return { ok: false as const, status: 404 as const, error: "Device not found" };
	}
	if (
		serverDevice.assignedUser!.id === user.id &&
		receiverDevice.assignedUser!.id === user.id
	) {
		const message =
			deviceType === "client"
				? await server.sendMessageToClientFromServer(
						serverDevice,
						messageContent,
						receiverDevice as ClientDevice
					)
				: await server.sendMessageToServerFromServer(
						serverDevice,
						messageContent,
						receiverDevice as ServerDevice
					);
		return {
			ok: true as const,
			status: 200 as const,
			body: { message: `Message Sent "${message.content}"` },
		};
	}
	return {
		ok: false as const,
		status: 403 as const,
		error: "You are not authorized to send a message to or from this device",
	};
}

export async function sendClientToServerMessage(body: {
	serverDeviceId: string;
	messageContent: string;
	clientDeviceId: string;
	user: User;
}) {
	const { serverDeviceId, messageContent, clientDeviceId, user } = body;
	if (!serverDeviceId || !messageContent || !clientDeviceId) {
		return { ok: false as const, status: 400 as const, error: "Invalid request" };
	}
	const serverDevice = await server.getServerDeviceById(serverDeviceId);
	const clientDevice = await client.getClientDeviceById(clientDeviceId);
	if (!serverDevice || !clientDevice) {
		return { ok: false as const, status: 404 as const, error: "Device not found" };
	}
	if (
		serverDevice.assignedUser!.id === user.id &&
		clientDevice.assignedUser!.id === user.id
	) {
		const message = await client.sendMessageToServerFromClient(
			serverDevice,
			messageContent,
			clientDevice
		);
		return {
			ok: true as const,
			status: 200 as const,
			body: { message: `Message Sent "${message.content}"` },
		};
	}
	return {
		ok: false as const,
		status: 403 as const,
		error: "You are not authorized to send a message to or from this device",
	};
}

export async function updateClientDevice(clientDevice: ClientDevice) {
	if (!clientDevice || !clientDevice.id) {
		return { ok: false as const, status: 400 as const, error: "Invalid request" };
	}
	const updatedClientDevice = await client.updateClientDevice(clientDevice);
	if (updatedClientDevice) {
		return { ok: true as const, status: 200 as const, body: updatedClientDevice };
	}
	return {
		ok: false as const,
		status: 500 as const,
		error: "Failed to update device",
	};
}

export async function updateServerDevice(serverDevice: ServerDevice) {
	if (!serverDevice || !serverDevice.id) {
		return { ok: false as const, status: 400 as const, error: "Invalid request" };
	}
	const updatedserverDevice = await server.updateServerDevice(serverDevice);
	if (updatedserverDevice) {
		return { ok: true as const, status: 200 as const, body: updatedserverDevice };
	}
	return {
		ok: false as const,
		status: 500 as const,
		error: "Failed to update device",
	};
}

export async function addClientCommand(clientDeviceId: string, command: Command) {
	if (!clientDeviceId || !command) {
		return { ok: false as const, status: 400 as const, error: "Invalid request" };
	}
	const clientDevice = await client.getClientDeviceById(clientDeviceId);
	if (!clientDevice) {
		return { ok: false as const, status: 404 as const, error: "Client Device not found" };
	}
	const updatedClientDevice = await client.addCommand(clientDevice, command);
	return { ok: true as const, status: 200 as const, body: updatedClientDevice };
}

export async function addServerCommand(serverDeviceId: string, command: Command) {
	if (!serverDeviceId || !command) {
		return { ok: false as const, status: 400 as const, error: "Invalid request" };
	}
	const serverDevice = await server.getServerDeviceById(serverDeviceId);
	if (!serverDevice) {
		return { ok: false as const, status: 404 as const, error: "server Device not found" };
	}
	const updatedServerDevice = await server.addCommand(serverDevice, command);
	return { ok: true as const, status: 200 as const, body: updatedServerDevice };
}

export async function removeMessage(messageId: string) {
	const message = await getMessageById(messageId);
	if (!message) {
		return { ok: false as const, status: 404 as const, error: "Message not found" };
	}
	const {
		deleted,
		updatedClientDevice,
		updatedServerDevice,
		updatedGroup,
	} = await deleteMessage(messageId);
	return {
		ok: true as const,
		status: 200 as const,
		body: { deleted, updatedClientDevice, updatedServerDevice, updatedGroup },
	};
}

export async function deleteClientDeviceById(id: string) {
	const clientDevice = await client.deleteClientDevice(id);
	if (clientDevice) {
		return { ok: true as const, status: 200 as const, body: clientDevice };
	}
	return { ok: false as const, status: 404 as const, error: "Device not found" };
}

export async function deleteServerDeviceById(id: string) {
	const serverDevice = await server.deleteServerDevice(id);
	if (serverDevice) {
		return { ok: true as const, status: 200 as const, body: serverDevice };
	}
	return { ok: false as const, status: 404 as const, error: "Device not found" };
}
