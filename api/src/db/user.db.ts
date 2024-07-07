import { configDotenv } from "dotenv";
import { User } from "../xata";
import { getXataClient } from "../xata";
import bcrypt from "bcryptjs";

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
