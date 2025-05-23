import { configDotenv } from "dotenv";
import { User } from "../xata";
import { getXataClient } from "../xata";
import bcrypt from "bcryptjs";
import { defaultIntegrations, defaultUserSettings, PublicUser } from "src/models/user.model";
import { Integration } from "src/models/integrations.model";

configDotenv();
const xata = getXataClient();

export const getUsers = async (): Promise<User[]> => {
	return await xata.db.user.getAll();
};
export const getUserById = async (id: string): Promise<User> => {
	return (await getUsers()).filter((user) => user.id === id)[0];
};
export const createUser = async (userData: User): Promise<User | null> => {
	const hashedPassword = await bcrypt.hash(userData.password!, 10);
	const user = await xata.db.user.create({
		username: userData.username,
		password: hashedPassword,
		settings: defaultUserSettings,
		integrations: defaultIntegrations,
	});
	return user;
};

export const updateUser = async (userData: User): Promise<User | null> => {
	return await xata.db.user.update(userData.id, userData);
};

export const deleteUser = async (id: string): Promise<User | null> => {
	return await xata.db.user.delete(id);
};

export const checkPassword = async (
	id: string,
	password: string
): Promise<boolean> => {
	const user = await getUserById(id);

	if (user) {
		return bcrypt.compare(password, user.password!);
	}

	return false;
};

export const getUserByName = async (username: string): Promise<User | null> => {
	const users = await getUsers();
	return users.filter((user) => user.username === username)[0];
};
//integrations
export const getIntegrations = async (user: PublicUser): Promise<Integration[]> => {
	return (await getUserById(user.id)).integrations;
}
export const addIntegration = async (user: PublicUser, integration: Integration): Promise<Integration[]> => {
    const userIntegrations = await getIntegrations(user);
	if (userIntegrations.find((i) => i.id == integration.id)) {
		console.log("Integration already added");
		return userIntegrations;
	}
    userIntegrations.push(integration);
    await updateUser({ ...user, integrations: userIntegrations });
    return userIntegrations;
}
export const removeIntegration = async (user: PublicUser, integration: Integration): Promise<Integration[]> => {
    const userIntegrations = await getIntegrations(user);
    userIntegrations.splice(userIntegrations.indexOf(integration), 1);
    await updateUser({ ...user, integrations: userIntegrations });
    return userIntegrations;
}