import { z } from "zod";

export const createDeviceBodySchema = z.object({
	name: z.string().min(1),
	assignedGroupId: z.string().min(1),
});

export const sendServerMessageBodySchema = z.object({
	serverDeviceId: z.string().min(1),
	messageContent: z.string().min(1),
	recieverDeviceId: z.string().min(1),
});

export const sendClientMessageBodySchema = z.object({
	serverDeviceId: z.string().min(1),
	messageContent: z.string().min(1),
	clientDeviceId: z.string().min(1),
});

const commandSchema = z.object({
	name: z.string().min(1),
	command: z.string().min(1),
	aliases: z.array(z.string()),
});

export const addClientCommandBodySchema = z.object({
	clientDeviceId: z.string().min(1),
	command: commandSchema,
});

export const addServerCommandBodySchema = z.object({
	serverDeviceId: z.string().min(1),
	command: commandSchema,
});
