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
Object.defineProperty(exports, "__esModule", { value: true });
exports.deleteGroup = exports.updateGroup = exports.addDeviceToGroup = exports.createGroup = exports.getGroupById = exports.getAllGroups = void 0;
const dotenv_1 = require("dotenv");
const xata_1 = require("../xata");
(0, dotenv_1.configDotenv)({ path: "../../.env" });
const xata = (0, xata_1.getXataClient)();
const getAllGroups = () => __awaiter(void 0, void 0, void 0, function* () {
    return (yield xata.db.group.getAll());
});
exports.getAllGroups = getAllGroups;
const getGroupById = (id) => __awaiter(void 0, void 0, void 0, function* () {
    return (yield (0, exports.getAllGroups)()).filter((group) => group.id === id)[0];
});
exports.getGroupById = getGroupById;
const createGroup = (group) => __awaiter(void 0, void 0, void 0, function* () {
    if (group)
        return yield xata.db.group.create(group);
    return yield xata.db.group.create({});
});
exports.createGroup = createGroup;
const addDeviceToGroup = (groupId, deviceId, deviceType) => __awaiter(void 0, void 0, void 0, function* () {
    const group = yield (0, exports.getGroupById)(groupId);
    if (group) {
        if (group.devices[deviceType].includes(deviceId)) {
            return "Device Already in Group";
        }
        group.devices[deviceType].push(deviceId);
        return yield (0, exports.updateGroup)(group);
    }
    return null;
});
exports.addDeviceToGroup = addDeviceToGroup;
const updateGroup = (group) => __awaiter(void 0, void 0, void 0, function* () {
    return yield xata.db.group.update(group);
});
exports.updateGroup = updateGroup;
const deleteGroup = (groupId) => __awaiter(void 0, void 0, void 0, function* () {
    return yield xata.db.group.delete(groupId);
});
exports.deleteGroup = deleteGroup;
