"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.authRouter = void 0;
const express_1 = __importDefault(require("express"));
const auth_1 = require("./auth");
const jwt_1 = require("../utils/jwt");
const lodash_1 = require("lodash");
exports.authRouter = express_1.default.Router();
exports.authRouter.get("/session/refresh", auth_1.refreshAccessTokenHandler);
exports.authRouter.get("/session/user", (req, res) => {
    const accessToken = (req.headers.authorization || "")
        .replace("Bearer", "")
        .replace(" ", "");
    const decoded = (0, jwt_1.verifyJwt)(accessToken, "accessTokenPublicKey");
    const user = (0, lodash_1.get)(decoded, "user");
    if (user) {
        return res.status(200).json(res.locals.user);
    }
    return res.status(401).send("Invalid token");
});
