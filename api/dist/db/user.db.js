"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.getUserByName = exports.checkPassword = exports.deleteUser = exports.updateUser = exports.createUser = exports.getUserById = exports.getUsers = void 0;
const dotenv_1 = require("dotenv");
const xata_1 = require("../xata");
const bcryptjs_1 = __importDefault(require("bcryptjs"));
(0, dotenv_1.configDotenv)();
const xata = (0, xata_1.getXataClient)();
const getUsers = () => __awaiter(void 0, void 0, void 0, function* () {
    return yield xata.db.user.getAll();
});
exports.getUsers = getUsers;
const getUserById = (id) => __awaiter(void 0, void 0, void 0, function* () {
    return (yield (0, exports.getUsers)()).filter((user) => user.id === id)[0];
});
exports.getUserById = getUserById;
const createUser = (userData) => __awaiter(void 0, void 0, void 0, function* () {
    const hashedPassword = yield bcryptjs_1.default.hash(userData.password, 10);
    const user = yield xata.db.user.create({
        username: userData.username,
        password: hashedPassword,
    });
    return user;
});
exports.createUser = createUser;
const updateUser = (userData) => __awaiter(void 0, void 0, void 0, function* () {
    return yield xata.db.user.update(userData.id, userData);
});
exports.updateUser = updateUser;
const deleteUser = (id) => __awaiter(void 0, void 0, void 0, function* () {
    return yield xata.db.user.delete(id);
});
exports.deleteUser = deleteUser;
const checkPassword = (id, password) => __awaiter(void 0, void 0, void 0, function* () {
    const user = yield (0, exports.getUserById)(id);
    if (user) {
        return bcryptjs_1.default.compare(password, user.password);
    }
    return false;
});
exports.checkPassword = checkPassword;
const getUserByName = (username) => __awaiter(void 0, void 0, void 0, function* () {
    const users = yield (0, exports.getUsers)();
    return users.filter((user) => user.username === username)[0];
});
exports.getUserByName = getUserByName;
