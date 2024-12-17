import * as client from "../database/clientDevice.db";
import * as server from "../database/serverDevice.db";
import express, { Request, Response } from "express";
import { StatusCodes } from "http-status-codes";
import { ClientDevice, ServerDevice, User } from "../xata";
import { requireUser } from "src/auth/auth";
import { getGroupById } from "src/database/group.db";
import log from "src/utils/logger";
import { deleteMessage, getMessageById } from "src/database/message.db";
export const deviceRouter = express.Router();

deviceRouter.get("/devices", async (req: Request, res: Response) => {
	try {
		const clientDevices = await client.getAllClientDevices();
		const serverDevices = await server.getAllServerDevices();
		if (clientDevices && serverDevices) {
			return res
				.status(StatusCodes.OK)
				.json({ clientDevices, serverDevices });
		}
		return res
			.status(StatusCodes.NOT_FOUND)
			.json({ error: "No devices found" });
	} catch (err) {
		return res
			.status(StatusCodes.INTERNAL_SERVER_ERROR)
			.json({ error: err });
	}
});

deviceRouter.get("/devices/clients", async (req: Request, res: Response) => {
	try {
		const clientDevices = await client.getAllClientDevices();
		if (clientDevices) {
			return res.status(StatusCodes.OK).json(clientDevices);
		}
		return res
			.status(StatusCodes.NOT_FOUND)
			.json({ error: "No client devices found" });
	} catch (err) {
		return res
			.status(StatusCodes.INTERNAL_SERVER_ERROR)
			.json({ error: err });
	}
});

deviceRouter.get("/devices/servers", async (req: Request, res: Response) => {
	try {
		const serverDevices = await server.getAllServerDevices();
		if (serverDevices) {
			return res.status(StatusCodes.OK).json(serverDevices);
		}
		return res
			.status(StatusCodes.NOT_FOUND)
			.json({ error: "No server devices found" });
	} catch (err) {
		return res
			.status(StatusCodes.INTERNAL_SERVER_ERROR)
			.json({ error: err });
	}
});

deviceRouter.get("/device/client/:id", async (req: Request, res: Response) => {
	try {
		const clientDevice = await client.getClientDeviceById(req.params.id);
		if (clientDevice) {
			return res.status(StatusCodes.OK).json(clientDevice);
		}
		return res
			.status(StatusCodes.NOT_FOUND)
			.json({ error: "Device not found" });
	} catch (err) {
		return res
			.status(StatusCodes.INTERNAL_SERVER_ERROR)
			.json({ error: err });
	}
});

deviceRouter.get("/device/server/:id", async (req: Request, res: Response) => {
	try {
		const serverDevice = await server.getServerDeviceById(req.params.id);
		if (serverDevice) {
			return res.status(StatusCodes.OK).json(serverDevice);
		}
		return res
			.status(StatusCodes.NOT_FOUND)
			.json({ error: "Device not found" });
	} catch (err) {
		return res
			.status(StatusCodes.INTERNAL_SERVER_ERROR)
			.json({ error: err });
	}
});

deviceRouter.post(
	"/device/client",
	requireUser,
	async (req: Request, res: Response) => {
		try {
			const { name, assignedGroupId } = req.body;
			// log.info(req.body)
			// log.info({name, assignedGroupId})
			const group = await getGroupById(assignedGroupId);
			if (!group) {
				log.info(`Group not found`);
				return res
					.status(StatusCodes.NOT_FOUND)
					.json({ error: "Group not found" });
			}
			const clientDevice = await client.createClientDevice({
				name,
				assignedGroup: assignedGroupId,
				assignedUser: res.locals.user,
			} as ClientDevice);
			if (!clientDevice) {
				return res
					.status(StatusCodes.INTERNAL_SERVER_ERROR)
					.json({ error: "Failed to create device" });
			}
			return res.status(StatusCodes.CREATED).json(clientDevice);
		} catch (error) {
			return res
				.status(StatusCodes.INTERNAL_SERVER_ERROR)
				.json({ error: error });
		}
	}
);

deviceRouter.post(
	"/device/server",
	requireUser,
	async (req: Request, res: Response) => {
		try {
			const { name, assignedGroupId } = req.body;
			const group = await getGroupById(assignedGroupId);
			if (!group) {
				log.info(`Group not found`);
			}
			const serverDevice = await server.createServerDevice({
				name,
				assignedGroup: group,
				assignedUser: res.locals.user,
			} as ServerDevice);
			if (!serverDevice) {
				return res
					.status(StatusCodes.INTERNAL_SERVER_ERROR)
					.json({ error: "Failed to create device" });
			}
			return res.status(StatusCodes.CREATED).json(serverDevice);
		} catch (error) {
			return res
				.status(StatusCodes.INTERNAL_SERVER_ERROR)
				.json({ error: error });
		}
	}
);

deviceRouter.post(
	"/device/server/sendMessage",
	requireUser,
	async (req: Request, res: Response) => {
		try {
			const { serverDeviceId, messageContent, recieverDeviceId } =
				req.body;
			if (!serverDeviceId || !messageContent || !recieverDeviceId) {
				return res
					.status(StatusCodes.BAD_REQUEST)
					.json({ error: "Invalid request" });
			}
			const serverDevice = await server.getServerDeviceById(
				serverDeviceId
			);
			let receiverDevice = await client.getClientDeviceById(
				recieverDeviceId
			);
			let deviceType = "client";
			if (!receiverDevice) {
				receiverDevice = await server.getServerDeviceById(
					recieverDeviceId
				);
				deviceType = "server";
			}
			if (!serverDevice || !receiverDevice) {
				return res
					.status(StatusCodes.NOT_FOUND)
					.json({ error: "Device not found" });
			}
			if (
				serverDevice.assignedUser!.id === res.locals.user.id &&
				receiverDevice.assignedUser!.id === res.locals.user.id
			) {
				const message =
					deviceType === "client"
						? await server.sendMessageToClientFromServer(
								serverDevice,
								messageContent,
								receiverDevice
						)
						: await server.sendMessageToServerFromServer(
								serverDevice,
								messageContent,
								receiverDevice
						);
				return res
					.status(StatusCodes.OK)
					.json({ message: `Message Sent "${message.content}"` });
			} else {
				return res
					.status(StatusCodes.FORBIDDEN)
					.json({
						error: "You are not authorized to send a message to or from this device",
					});
			}
		} catch (error) {
			return res
				.status(StatusCodes.INTERNAL_SERVER_ERROR)
				.json({ error: error });
		}
	}
);

deviceRouter.post(
	"/device/client/sendMessage",
	requireUser,
	async (req: Request, res: Response) => {
		try {
			const { serverDeviceId, messageContent, clientDeviceId } = req.body;
			if (!serverDeviceId || !messageContent || !clientDeviceId) {
				return res
					.status(StatusCodes.BAD_REQUEST)
					.json({ error: "Invalid request" });
			}
			const serverDevice = await server.getServerDeviceById(
				serverDeviceId
			);
			const clientDevice = await client.getClientDeviceById(
				clientDeviceId
			);
			if (!serverDevice || !clientDevice) {
				return res
					.status(StatusCodes.NOT_FOUND)
					.json({ error: "Device not found" });
			}
			if (
				serverDevice.assignedUser!.id === res.locals.user.id &&
				clientDevice.assignedUser!.id === res.locals.user.id
			) {
				const message = await client.sendMessageToServerFromClient(
					serverDevice,
					messageContent,
					clientDevice
				);
				return res
					.status(StatusCodes.OK)
					.json({ message: `Message Sent "${message.content}"` });
			} else {
				return res
					.status(StatusCodes.FORBIDDEN)
					.json({
						error: "You are not authorized to send a message to or from this device",
					});
			}
		} catch (error) {
			return res
				.status(StatusCodes.INTERNAL_SERVER_ERROR)
				.json({ error: error });
		}
	}
);

deviceRouter.put(
	"/device/client",
	requireUser,
	async (req: Request, res: Response) => {
		try {
			const clientDevice = req.body as ClientDevice;
			if (!clientDevice || !clientDevice.id) {
				return res
					.status(StatusCodes.BAD_REQUEST)
					.json({ error: "Invalid request" });
			}

			const updatedClientDevice = await client.updateClientDevice(
				clientDevice
			);

			if (updatedClientDevice) {
				return res.status(StatusCodes.OK).json(updatedClientDevice);
			}
			return res
				.status(StatusCodes.INTERNAL_SERVER_ERROR)
				.json({ error: "Failed to update device" });
		} catch (error) {
			return res
				.status(StatusCodes.INTERNAL_SERVER_ERROR)
				.json({ error: error });
		}
	}
);

deviceRouter.put(
	"/device/server",
	requireUser,
	async (req: Request, res: Response) => {
		try {
			const serverDevice = req.body as ServerDevice;
			if (!serverDevice || !serverDevice.id) {
				return res
					.status(StatusCodes.BAD_REQUEST)
					.json({ error: "Invalid request" });
			}

			const updatedserverDevice = await server.updateServerDevice(
				serverDevice
			);

			if (updatedserverDevice) {
				return res.status(StatusCodes.OK).json(updatedserverDevice);
			}
			return res
				.status(StatusCodes.INTERNAL_SERVER_ERROR)
				.json({ error: "Failed to update device" });
		} catch (error) {
			return res
				.status(StatusCodes.INTERNAL_SERVER_ERROR)
				.json({ error: error });
		}
	}
);

deviceRouter.post(
	"/device/client/addCommand",
	requireUser,
	async (req: Request, res: Response) => {
		try {
			const { clientDeviceId, command } = req.body;
			if (!clientDeviceId || !command) {
				return res
					.status(StatusCodes.BAD_REQUEST)
					.json({ error: "Invalid request" });
			}
			const clientDevice = await client.getClientDeviceById(
				clientDeviceId
			);
			if (!clientDevice) {
				return res
					.status(StatusCodes.NOT_FOUND)
					.json({ error: "Client Device not found" });
			}
			const updatedClientDevice = await client.addCommand(
				clientDevice,
				command
			);
			return res.status(StatusCodes.OK).json(updatedClientDevice);
		} catch (error) {
			return res
				.status(StatusCodes.INTERNAL_SERVER_ERROR)
				.json({ error: error });
		}
	}
);

deviceRouter.post(
	"/device/server/addCommand",
	requireUser,
	async (req: Request, res: Response) => {
		try {
			const { serverDeviceId, command } = req.body;
			if (!serverDeviceId || !command) {
				return res
					.status(StatusCodes.BAD_REQUEST)
					.json({ error: "Invalid request" });
			}
			const serverDevice = await server.getServerDeviceById(
				serverDeviceId
			);
			if (!serverDevice) {
				return res
					.status(StatusCodes.NOT_FOUND)
					.json({ error: "server Device not found" });
			}
			const updatedServerDevice = await server.addCommand(
				serverDevice,
				command
			);
			return res.status(StatusCodes.OK).json(updatedServerDevice);
		} catch (error) {
			return res
				.status(StatusCodes.INTERNAL_SERVER_ERROR)
				.json({ error: error });
		}
	}
);

deviceRouter.delete(
	"/device/message/:id",
	requireUser,
	async (req: Request, res: Response) => {
		try {
			const message = await getMessageById(req.params.id);
			if (!message) {
				return res
					.status(StatusCodes.NOT_FOUND)
					.json({ error: "Message not found" });
			}
			const {
				deleted,
				updatedClientDevice,
				updatedServerDevice,
				updatedGroup,
			} = await deleteMessage(req.params.id);
			return res
				.status(StatusCodes.OK)
				.json({
					deleted,
					updatedClientDevice,
					updatedServerDevice,
					updatedGroup,
				});
		} catch (error) {
			log.error(error);
			return res
				.status(StatusCodes.INTERNAL_SERVER_ERROR)
				.json({ error: error });
		}
	}
);

//  TODO: Implement removal of devices from group, and deletion of all messages with that device as either to or from.
deviceRouter.delete(
	"/device/client/:id",
	requireUser,
	async (req: Request, res: Response) => {
		try {
			const clientDevice = await client.deleteClientDevice(req.params.id);
			if (clientDevice) {
				return res.status(StatusCodes.OK).json(clientDevice);
			}
			return res
				.status(StatusCodes.NOT_FOUND)
				.json({ error: "Device not found" });
		} catch (error) {
			return res
				.status(StatusCodes.INTERNAL_SERVER_ERROR)
				.json({ error: error });
		}
	}
);

deviceRouter.delete(
	"/device/server/:id",
	requireUser,
	async (req: Request, res: Response) => {
		try {
			const serverDevice = await server.deleteServerDevice(req.params.id);
			if (serverDevice) {
				return res.status(StatusCodes.OK).json(serverDevice);
			}
			return res
				.status(StatusCodes.NOT_FOUND)
				.json({ error: "Device not found" });
		} catch (error) {
			return res
				.status(StatusCodes.INTERNAL_SERVER_ERROR)
				.json({ error: error });
		}
	}
);
