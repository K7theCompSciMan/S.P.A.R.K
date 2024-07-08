import express, { NextFunction, Request, Response } from "express";
import { refreshAccessTokenHandler } from "./auth";
import { verifyJwt } from "../utils/jwt";
import { User } from "../xata";
import { get } from "lodash";
export const authRouter = express.Router();

authRouter.get("/session/refresh", refreshAccessTokenHandler);
authRouter.get("/session/user", (req: Request, res: Response) => {
	const accessToken = (req.headers.authorization || "")
		.replace("Bearer", "")
		.replace(" ", "");
	const decoded = verifyJwt<User>(accessToken, "accessTokenPublicKey");
	const user = get(decoded, "user") as unknown as User | null;
	if (user) {
		return res.status(200).json(res.locals.user);
	}
	return res.status(401).send("Invalid token");
});
