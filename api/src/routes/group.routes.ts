import express, { Request, Response } from "express";
import * as db from "../database/group.db";
import { StatusCodes } from "http-status-codes";
import { Group } from "../xata";
import { requireUser } from "src/auth/auth";
import log from "src/utils/logger";

export const groupRouter = express.Router();
// TODO: Implement ID10T error handling
groupRouter.get("/groups", async (req: Request, res: Response) => {
	try {
		const groups = await db.getAllGroups();
		if (groups) {
			return res.status(StatusCodes.OK).json(groups);
		}
		return res
			.status(StatusCodes.NOT_FOUND)
			.json({ error: "No groups found" });
	} catch (err) {
		return res
			.status(StatusCodes.INTERNAL_SERVER_ERROR)
			.json({ error: err });
	}
});

groupRouter.get("/groups/:userId", async (req: Request, res: Response) => {
	try {
		const groups = await db.getGroupsByUserId(req.params.userId);
		if (groups) {
			return res.status(StatusCodes.OK).json(groups);
		}
		return res
			.status(StatusCodes.NOT_FOUND)
			.json({ error: "No groups found" });
	} catch (err) {
		return res
			.status(StatusCodes.INTERNAL_SERVER_ERROR)
			.json({ error: err });
	}
});

groupRouter.get("/group/:id", async (req: Request, res: Response) => {
	try {
		const group = await db.getGroupById(req.params.id);
		if (group) {
			return res.status(StatusCodes.OK).json(group);
		}
		return res
			.status(StatusCodes.NOT_FOUND)
			.json({ error: "Group not found" });
	} catch (err) {
		return res
			.status(StatusCodes.INTERNAL_SERVER_ERROR)
			.json({ error: err });
	}
});

groupRouter.post("/group", requireUser, async (req: Request, res: Response) => {
	try {
		const { name, devices, messages } = req.body;
		const group = await db.createGroup({
			name,
			devices,
			messages,
			assignedUser: res.locals.user.id,
		} as Group);
		if (!group) {
			return res
				.status(StatusCodes.INTERNAL_SERVER_ERROR)
				.json({ error: "Failed to create group" });
		}
		return res.status(StatusCodes.CREATED).json(group);
	} catch (error) {
		return res
			.status(StatusCodes.INTERNAL_SERVER_ERROR)
			.json({ error: error });
	}
});

groupRouter.put("/group", requireUser, async (req: Request, res: Response) => {
	try {
		const group = req.body as Group;
		if (!group) {
			return res
				.status(StatusCodes.BAD_REQUEST)
				.json({ error: "Invalid request" });
		}
		const updatedGroup = await db.updateGroup(group);
		if (updatedGroup) {
			return res.status(StatusCodes.OK).json(updatedGroup);
		}
		return res
			.status(StatusCodes.INTERNAL_SERVER_ERROR)
			.json({ error: "Failed to update group" });
	} catch (error) {
		return res
			.status(StatusCodes.INTERNAL_SERVER_ERROR)
			.json({ error: error });
	}
});

groupRouter.post("/group/addCommand", requireUser, async (req: Request, res: Response) => {
	try {
		const { groupId, command } = req.body;
		if (!groupId || !command) {
			return res
				.status(StatusCodes.BAD_REQUEST)
				.json({ error: "Invalid request" });
		}
		log.info("adding command " + command + " to group " + groupId)
		let group = await db.getGroupById(groupId)
		const newGroup = await db.addCommandToGroup(group, command);
		if (newGroup) {
			log.info("added command " + command + " to group " + groupId)
			return res.status(StatusCodes.OK).json(newGroup);
		}
		return res
			.status(StatusCodes.NOT_FOUND)
			.json({ error: "Group not found" });
	} catch (error) {
		return res
			.status(StatusCodes.INTERNAL_SERVER_ERROR)
			.json({ error: error });
	}
});

groupRouter.delete(
	"/group/:id",
	requireUser,
	async (req: Request, res: Response) => {
		try {
			const group = await db.deleteGroup(req.params.id);
			if (group) {
				return res
					.status(StatusCodes.OK)
					.json(await db.deleteGroup(req.params.id));
			}
			return res
				.status(StatusCodes.NOT_FOUND)
				.json({ error: "Group not found" });
		} catch (error) {
			return res
				.status(StatusCodes.INTERNAL_SERVER_ERROR)
				.json({ error: error });
		}
	}
);

groupRouter.post(
	"/group/addDevice",
	requireUser,
	async (req: Request, res: Response) => {
		try {
			const { groupId, deviceId, deviceType } = req.body;
			if (!groupId || !deviceId || !deviceType) {
				return res
					.status(StatusCodes.BAD_REQUEST)
					.json({ error: "Invalid request" });
			}
			const group = await db.addDeviceToGroup(
				groupId,
				deviceId,
				deviceType
			);
			if (group) {
				return res.status(StatusCodes.OK).json(group);
			}
			return res
				.status(StatusCodes.NOT_FOUND)
				.json({ error: "Group not found" });
		} catch (error) {
			return res
				.status(StatusCodes.INTERNAL_SERVER_ERROR)
				.json({ error: error });
		}
	}
);
