import { configDotenv } from "dotenv";
import { Group } from "../xata";
import { getXataClient } from "../xata";
configDotenv({ path: "../../.env" });
const xata = getXataClient();

export const getAllGroups = async () => {
	return (await xata.db.group.getAll()) as Group[];
};

export const getGroupById = async (id: string) => {
	return (await getAllGroups()).filter((group) => group.id === id)[0];
};

export const getGroupsByUserId = async (userId: string) => {
	return (await getAllGroups()).filter((group) => group.assignedUser?.id === userId);
}

export const createGroup = async (group?: Group) => {
	if (group) return await xata.db.group.create(group);
	return await xata.db.group.create({});
};

export const addDeviceToGroup = async (
	groupId: string,
	deviceId: string,
	deviceType: string
) => {
	const group = await getGroupById(groupId);
	if (group) {
		if (group.devices[deviceType].includes(deviceId)) {
			return "Device Already in Group";
		}
		group.devices[deviceType].push(deviceId);
		return await updateGroup(group);
	}
	return null;
};

export const updateGroup = async (group: Group) => {
	return await xata.db.group.update(group);
};

export const deleteGroup = async (groupId: string) => {
	return await xata.db.group.delete(groupId);
};
