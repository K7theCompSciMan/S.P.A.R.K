"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.signJwt = void 0;
exports.verifyJwt = verifyJwt;
const jsonwebtoken_1 = __importDefault(require("jsonwebtoken"));
const dotenv_1 = require("dotenv");
(0, dotenv_1.configDotenv)();
const signJwt = (payload, keyName, options) => {
    try {
        const key = Buffer.from(getEnv(keyName), "base64").toString("ascii");
        return jsonwebtoken_1.default.sign(payload, key, Object.assign(Object.assign({}, (options && options)), { algorithm: "RS256" }));
    }
    catch (err) {
        return "Error signing JWT";
    }
};
exports.signJwt = signJwt;
function verifyJwt(token, keyName) {
    // log.info(`Verifying JWT for token ${token}`);
    const publicKey = Buffer.from(getEnv(keyName), "base64").toString("ascii");
    // log.info(`Got key ${publicKey}`);
    try {
        const decoded = jsonwebtoken_1.default.verify(token, publicKey);
        return decoded;
    }
    catch (err) {
        return null;
    }
}
function getEnv(key) {
    const value = process.env[key];
    if (!value) {
        throw new Error(`Environment variable ${key} not set`);
    }
    return value;
}
