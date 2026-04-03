import express, { Request, Response } from "express";
import { StatusCodes } from "http-status-codes";
import { requireUser } from "src/auth/auth";
import { validateBody } from "src/middleware/validateBody";
import {
	addClientCommandBodySchema,
	addServerCommandBodySchema,
	createDeviceBodySchema,
	sendClientMessageBodySchema,
	sendServerMessageBodySchema,
} from "src/schemas/device.schemas";
import * as deviceService from "src/services/device.service";

export const deviceRouter = express.Router();

deviceRouter.get("/devices", requireUser, async (_req: Request, res: Response) => {
	try {
		const result = await deviceService.listAllDevices();
		if (result.ok) {
			return res.status(StatusCodes.OK).json(result.body);
		}
		return res.status(StatusCodes.NOT_FOUND).json({ error: result.error });
	} catch (err) {
		return res.status(StatusCodes.INTERNAL_SERVER_ERROR).json({ error: err });
	}
});

deviceRouter.get(
	"/devices/clients",
	requireUser,
	async (_req: Request, res: Response) => {
		try {
			const result = await deviceService.listClientDevices();
			if (result.ok) {
				return res.status(StatusCodes.OK).json(result.body);
			}
			return res.status(StatusCodes.NOT_FOUND).json({ error: result.error });
		} catch (err) {
			return res.status(StatusCodes.INTERNAL_SERVER_ERROR).json({ error: err });
		}
	}
);

deviceRouter.get(
	"/devices/servers",
	requireUser,
	async (_req: Request, res: Response) => {
		try {
			const result = await deviceService.listServerDevices();
			if (result.ok) {
				return res.status(StatusCodes.OK).json(result.body);
			}
			return res.status(StatusCodes.NOT_FOUND).json({ error: result.error });
		} catch (err) {
			return res.status(StatusCodes.INTERNAL_SERVER_ERROR).json({ error: err });
		}
	}
);

deviceRouter.get("/device/client/:id", async (req: Request, res: Response) => {
	try {
		const result = await deviceService.getClientDevice(req.params.id);
		if (result.ok) {
			return res.status(StatusCodes.OK).json(result.body);
		}
		return res.status(StatusCodes.NOT_FOUND).json({ error: result.error });
	} catch (err) {
		return res.status(StatusCodes.INTERNAL_SERVER_ERROR).json({ error: err });
	}
});

deviceRouter.get("/device/server/:id", async (req: Request, res: Response) => {
	try {
		const result = await deviceService.getServerDevice(req.params.id);
		if (result.ok) {
			return res.status(StatusCodes.OK).json(result.body);
		}
		return res.status(StatusCodes.NOT_FOUND).json({ error: result.error });
	} catch (err) {
		return res.status(StatusCodes.INTERNAL_SERVER_ERROR).json({ error: err });
	}
});

deviceRouter.post(
	"/device/client",
	requireUser,
	validateBody(createDeviceBodySchema),
	async (req: Request, res: Response) => {
		try {
			const { name, assignedGroupId } = req.body;
			const result = await deviceService.createClientDevice({
				name,
				assignedGroupId,
				user: res.locals.user,
			});
			if (result.ok) {
				return res.status(result.status).json(result.body);
			}
			return res.status(result.status).json({ error: result.error });
		} catch (error) {
			return res.status(StatusCodes.INTERNAL_SERVER_ERROR).json({ error: error });
		}
	}
);

deviceRouter.post(
	"/device/server",
	requireUser,
	validateBody(createDeviceBodySchema),
	async (req: Request, res: Response) => {
		try {
			const { name, assignedGroupId } = req.body;
			const result = await deviceService.createServerDevice({
				name,
				assignedGroupId,
				user: res.locals.user,
			});
			if (result.ok) {
				return res.status(result.status).json(result.body);
			}
			return res.status(result.status).json({ error: result.error });
		} catch (error) {
			return res.status(StatusCodes.INTERNAL_SERVER_ERROR).json({ error: error });
		}
	}
);

deviceRouter.post(
	"/device/server/sendMessage",
	requireUser,
	validateBody(sendServerMessageBodySchema),
	async (req: Request, res: Response) => {
		try {
			const result = await deviceService.sendServerToDeviceMessage({
				...req.body,
				user: res.locals.user,
			});
			if (result.ok) {
				return res.status(result.status).json(result.body);
			}
			return res.status(result.status).json({ error: result.error });
		} catch (error) {
			return res.status(StatusCodes.INTERNAL_SERVER_ERROR).json({ error: error });
		}
	}
);

deviceRouter.post(
	"/device/client/sendMessage",
	requireUser,
	validateBody(sendClientMessageBodySchema),
	async (req: Request, res: Response) => {
		try {
			const result = await deviceService.sendClientToServerMessage({
				...req.body,
				user: res.locals.user,
			});
			if (result.ok) {
				return res.status(result.status).json(result.body);
			}
			return res.status(result.status).json({ error: result.error });
		} catch (error) {
			return res.status(StatusCodes.INTERNAL_SERVER_ERROR).json({ error: error });
		}
	}
);

deviceRouter.put("/device/client", requireUser, async (req: Request, res: Response) => {
	try {
		const result = await deviceService.updateClientDevice(req.body);
		if (result.ok) {
			return res.status(result.status).json(result.body);
		}
		return res.status(result.status).json({ error: result.error });
	} catch (error) {
		return res.status(StatusCodes.INTERNAL_SERVER_ERROR).json({ error: error });
	}
});

deviceRouter.put("/device/server", requireUser, async (req: Request, res: Response) => {
	try {
		const result = await deviceService.updateServerDevice(req.body);
		if (result.ok) {
			return res.status(result.status).json(result.body);
		}
		return res.status(result.status).json({ error: result.error });
	} catch (error) {
		return res.status(StatusCodes.INTERNAL_SERVER_ERROR).json({ error: error });
	}
});

deviceRouter.post(
	"/device/client/addCommand",
	requireUser,
	validateBody(addClientCommandBodySchema),
	async (req: Request, res: Response) => {
		try {
			const { clientDeviceId, command } = req.body;
			const result = await deviceService.addClientCommand(clientDeviceId, command);
			if (result.ok) {
				return res.status(result.status).json(result.body);
			}
			return res.status(result.status).json({ error: result.error });
		} catch (error) {
			return res.status(StatusCodes.INTERNAL_SERVER_ERROR).json({ error: error });
		}
	}
);

deviceRouter.post(
	"/device/server/addCommand",
	requireUser,
	validateBody(addServerCommandBodySchema),
	async (req: Request, res: Response) => {
		try {
			const { serverDeviceId, command } = req.body;
			const result = await deviceService.addServerCommand(serverDeviceId, command);
			if (result.ok) {
				return res.status(result.status).json(result.body);
			}
			return res.status(result.status).json({ error: result.error });
		} catch (error) {
			return res.status(StatusCodes.INTERNAL_SERVER_ERROR).json({ error: error });
		}
	}
);

deviceRouter.delete(
	"/device/message/:id",
	requireUser,
	async (req: Request, res: Response) => {
		try {
			const result = await deviceService.removeMessage(req.params.id);
			if (result.ok) {
				return res.status(result.status).json(result.body);
			}
			return res.status(result.status).json({ error: result.error });
		} catch (error) {
			return res.status(StatusCodes.INTERNAL_SERVER_ERROR).json({ error: error });
		}
	}
);

deviceRouter.delete(
	"/device/client/:id",
	requireUser,
	async (req: Request, res: Response) => {
		try {
			const result = await deviceService.deleteClientDeviceById(req.params.id);
			if (result.ok) {
				return res.status(result.status).json(result.body);
			}
			return res.status(result.status).json({ error: result.error });
		} catch (error) {
			return res.status(StatusCodes.INTERNAL_SERVER_ERROR).json({ error: error });
		}
	}
);

deviceRouter.delete(
	"/device/server/:id",
	requireUser,
	async (req: Request, res: Response) => {
		try {
			const result = await deviceService.deleteServerDeviceById(req.params.id);
			if (result.ok) {
				return res.status(result.status).json(result.body);
			}
			return res.status(result.status).json({ error: result.error });
		} catch (error) {
			return res.status(StatusCodes.INTERNAL_SERVER_ERROR).json({ error: error });
		}
	}
);
