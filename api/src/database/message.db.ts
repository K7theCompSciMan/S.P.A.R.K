import { Message, getXataClient } from "src/xata";
import { configDotenv } from "dotenv";
configDotenv({ path: "../../.env" });
const xata = getXataClient();

export const getAllMessages = async () => {
    return (await xata.db.message.getAll()) as Message[];
};

export const getMessageById = async (id: string) => {
    return (await getAllMessages()).filter(
        (message) => message.id === id
    )[0];
};

export const createMessage = async (message?: Message) => {
    if (message) return await xata.db.message.create(message);
    return await xata.db.message.create({});
};

export const updateMessage = async (message: Message) => {
    return await xata.db.message.update(message);
};

export const deleteMessage = async (messageId: string) => {
    return await xata.db.message.delete(messageId);
};

