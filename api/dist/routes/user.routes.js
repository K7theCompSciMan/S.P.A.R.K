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
exports.userRouter = void 0;
const express_1 = __importDefault(require("express"));
const http_status_codes_1 = require("http-status-codes");
const db = __importStar(require("../db/user.db"));
exports.userRouter = express_1.default.Router();
const user_model_1 = require("../models/user.model");
const auth_1 = require("../auth/auth");
exports.userRouter.get("/users", (req, res) => __awaiter(void 0, void 0, void 0, function* () {
    try {
        const users = yield db.getUsers();
        if (!users) {
            res.status(http_status_codes_1.StatusCodes.NOT_FOUND).send("No users found");
        }
        return res.status(http_status_codes_1.StatusCodes.OK).json(users);
    }
    catch (error) {
        return res.status(http_status_codes_1.StatusCodes.INTERNAL_SERVER_ERROR).json(error);
    }
}));
exports.userRouter.get("/user/:id", (req, res) => __awaiter(void 0, void 0, void 0, function* () {
    try {
        const user = yield db.getUserById(req.params.id);
        if (!user) {
            res.status(http_status_codes_1.StatusCodes.NOT_FOUND).send("User not found");
        }
        const publicUser = new user_model_1.PublicUser(user);
        return res.status(http_status_codes_1.StatusCodes.OK).json({ user: publicUser });
    }
    catch (error) {
        return res.status(http_status_codes_1.StatusCodes.INTERNAL_SERVER_ERROR).json(error);
    }
}));
exports.userRouter.post("/register", (req, res) => __awaiter(void 0, void 0, void 0, function* () {
    try {
        const { username, email, password } = req.body;
        if (!username || !email || !password) {
            return res.status(http_status_codes_1.StatusCodes.BAD_REQUEST).send("Invalid input");
        }
        const user = yield db.getUserByName(email);
        if (user) {
            return res
                .status(http_status_codes_1.StatusCodes.BAD_REQUEST)
                .send("User with the same name already exists");
        }
        const newUser = yield db.createUser({ username, password });
        if (!newUser) {
            return res
                .status(http_status_codes_1.StatusCodes.INTERNAL_SERVER_ERROR)
                .send("User not created");
        }
        // sign tokens
        const accessToken = (0, auth_1.signAccessToken)(newUser);
        const refreshToken = (0, auth_1.signRefreshToken)(newUser);
        const publicNewUser = new user_model_1.PublicUser(newUser);
        return res
            .status(http_status_codes_1.StatusCodes.CREATED)
            .json({ user: publicNewUser, accessToken, refreshToken });
    }
    catch (error) {
        return res.status(http_status_codes_1.StatusCodes.INTERNAL_SERVER_ERROR).json(error);
    }
}));
exports.userRouter.post("/login", (req, res) => __awaiter(void 0, void 0, void 0, function* () {
    try {
        const { username, password } = req.body;
        if (!username || !password) {
            return res.status(http_status_codes_1.StatusCodes.BAD_REQUEST).send("Invalid input");
        }
        const user = yield db.getUserByName(username);
        if (!user) {
            return res
                .status(http_status_codes_1.StatusCodes.NOT_FOUND)
                .send("Invalid Email or Password");
        }
        const isPasswordValid = yield db.checkPassword(user.id, password);
        if (!isPasswordValid) {
            return res
                .status(http_status_codes_1.StatusCodes.UNAUTHORIZED)
                .send("Invalid Email or Password");
        }
        // sign tokens
        const accessToken = (0, auth_1.signAccessToken)(user);
        const refreshToken = (0, auth_1.signRefreshToken)(user);
        // log.info(`User logged in ${user} | accessToken: ${accessToken} | refreshToken: ${refreshToken}`);
        const publicUser = new user_model_1.PublicUser(user);
        return res
            .status(http_status_codes_1.StatusCodes.OK)
            .send({ user: publicUser, accessToken, refreshToken });
    }
    catch (error) {
        return res.status(http_status_codes_1.StatusCodes.INTERNAL_SERVER_ERROR).json(error);
    }
}));
exports.userRouter.put("/user", auth_1.requireUser, (req, res) => __awaiter(void 0, void 0, void 0, function* () {
    try {
        const user = res.locals.user.user;
        if (!user) {
            return res
                .status(http_status_codes_1.StatusCodes.NOT_FOUND)
                .send("User not in res.locals.user");
        }
        const updateUser = yield db.updateUser(Object.assign(Object.assign({}, req.body), { id: user.id }));
        const publicUser = new user_model_1.PublicUser(updateUser);
        return res.status(http_status_codes_1.StatusCodes.OK).json({ user: publicUser });
    }
    catch (error) {
        return res.status(http_status_codes_1.StatusCodes.INTERNAL_SERVER_ERROR).json(error);
    }
}));
exports.userRouter.delete("/user", auth_1.requireUser, (req, res) => __awaiter(void 0, void 0, void 0, function* () {
    try {
        const user = res.locals.user.user;
        if (!user) {
            return res.status(http_status_codes_1.StatusCodes.NOT_FOUND).send("User not signed in");
        }
        yield db.deleteUser(user.id);
        return res.status(http_status_codes_1.StatusCodes.OK).send("User deleted");
    }
    catch (error) {
        return res.status(http_status_codes_1.StatusCodes.INTERNAL_SERVER_ERROR).json({ error });
    }
}));
exports.userRouter.get("/me", auth_1.requireUser, (req, res) => __awaiter(void 0, void 0, void 0, function* () {
    return res.status(http_status_codes_1.StatusCodes.OK).json(res.locals.user);
}));
