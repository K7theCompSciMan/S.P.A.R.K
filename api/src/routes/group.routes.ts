import express, { Request, Response } from "express";
import * as db from "../db/group.db";
import { StatusCodes } from "http-status-codes";
import { Group } from "../xata";
import { requireUser } from "src/auth/auth";

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
		if (!name || !devices || !messages) {
			const group = db.createGroup();
			return res
				.status(StatusCodes.OK)
				.json({ group });
		}
		const group = await db.createGroup({
			name,
			devices,
			messages,
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

groupRouter.put("/group", async (req: Request, res: Response) => {
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

groupRouter.delete("/group/:id", async (req: Request, res: Response) => {
	res.json(await db.deleteGroup(req.params.id));
});

groupRouter.post("/group/addDevice", async (req: Request, res: Response) => {
	res.json(
		await db.addDeviceToGroup(
			req.body.groupId,
			req.body.deviceId,
			req.body.deviceType
		)
	);
});
