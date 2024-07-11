"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
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
exports.groupRouter = void 0;
const express_1 = __importDefault(require("express"));
const db = __importStar(require("../db/group.db"));
const http_status_codes_1 = require("http-status-codes");
exports.groupRouter = express_1.default.Router();
// TODO: Implement ID10T error handling
exports.groupRouter.get("/groups", (req, res) => __awaiter(void 0, void 0, void 0, function* () {
    try {
        const groups = yield db.getAllGroups();
        if (groups) {
            return res.status(http_status_codes_1.StatusCodes.OK).json(groups);
        }
        return res
            .status(http_status_codes_1.StatusCodes.NOT_FOUND)
            .json({ error: "No groups found" });
    }
    catch (err) {
        return res
            .status(http_status_codes_1.StatusCodes.INTERNAL_SERVER_ERROR)
            .json({ error: err });
    }
}));
exports.groupRouter.get("/group/:id", (req, res) => __awaiter(void 0, void 0, void 0, function* () {
    try {
        const group = yield db.getGroupById(req.params.id);
        if (group) {
            return res.status(http_status_codes_1.StatusCodes.OK).json(group);
        }
        return res
            .status(http_status_codes_1.StatusCodes.NOT_FOUND)
            .json({ error: "Group not found" });
    }
    catch (err) {
        return res
            .status(http_status_codes_1.StatusCodes.INTERNAL_SERVER_ERROR)
            .json({ error: err });
    }
}));
exports.groupRouter.post("/group", (req, res) => __awaiter(void 0, void 0, void 0, function* () {
    try {
        const { name, devices, messages } = req.body;
        if (!name || !devices || !messages) {
            return res
                .status(http_status_codes_1.StatusCodes.BAD_REQUEST)
                .json({ error: "Invalid request" });
        }
        const group = yield db.createGroup({
            name,
            devices,
            messages,
        });
        if (!group) {
            return res
                .status(http_status_codes_1.StatusCodes.INTERNAL_SERVER_ERROR)
                .json({ error: "Failed to create group" });
        }
        return res.status(http_status_codes_1.StatusCodes.CREATED).json(group);
    }
    catch (error) {
        return res
            .status(http_status_codes_1.StatusCodes.INTERNAL_SERVER_ERROR)
            .json({ error: error });
    }
}));
exports.groupRouter.put("/group", (req, res) => __awaiter(void 0, void 0, void 0, function* () {
    try {
        const group = req.body;
        if (!group) {
            return res
                .status(http_status_codes_1.StatusCodes.BAD_REQUEST)
                .json({ error: "Invalid request" });
        }
        const updatedGroup = yield db.updateGroup(group);
        if (updatedGroup) {
            return res.status(http_status_codes_1.StatusCodes.OK).json(updatedGroup);
        }
        return res
            .status(http_status_codes_1.StatusCodes.INTERNAL_SERVER_ERROR)
            .json({ error: "Failed to update group" });
    }
    catch (error) {
        return res
            .status(http_status_codes_1.StatusCodes.INTERNAL_SERVER_ERROR)
            .json({ error: error });
    }
}));
exports.groupRouter.delete("/group/:id", (req, res) => __awaiter(void 0, void 0, void 0, function* () {
    res.json(yield db.deleteGroup(req.params.id));
}));
exports.groupRouter.post("/group/addDevice", (req, res) => __awaiter(void 0, void 0, void 0, function* () {
    res.json(yield db.addDeviceToGroup(req.body.groupId, req.body.deviceId, req.body.deviceType));
}));
