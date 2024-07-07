import User, { PublicUser } from "../models/user.model";
import { signJwt, verifyJwt } from "../utils/jwt";
import { Session } from "./session";
import { Request, Response, NextFunction } from "express";
import { get } from "lodash";
import { STATUS_CODES } from "http";

export function signRefreshToken(user: User) {
    const publicUser = new PublicUser(user);
    // log.info(`Signing refresh token for user ${publicUser}`);
    const session = new Session(publicUser);
    // log.info(`Session created for user ${session.user}`);
    const refreshToken = signJwt({session}, "refreshTokenPrivateKey", {
        expiresIn: "1w"
    });
    // log.info(`Refresh token created for user ${session.user}`);
    return refreshToken;
}

export function signAccessToken(user: User) {
    const publicUser = new PublicUser(user);
    // log.info(`Signing access token for user ${publicUser.id}`);
    const accessToken = signJwt({user: publicUser}, "accessTokenPrivateKey", {
        expiresIn: "15m"    
    });
    // log.info(`Access token created ${accessToken}`);
    return accessToken;
}

export const deserializeUser = async (req: Request, res: Response, next: NextFunction) => {
	const accessToken = (req.headers.authorization || "").replace("Bearer", "").replace(" ", "");
	// log.info(accessToken)
	if(!accessToken){
		// log.info(`No token found in deserializeUser ${accessToken}`);
		return next();
	}
	// log.info(`Token found in deserializeUser`);
	const decoded = verifyJwt<User>(accessToken, "accessTokenPublicKey");
    const user = get(decoded, "user") as unknown as User | null;
	if(user !== null){
		res.locals.user = user;
        // // log.info(`User ${res.locals.user.email} found in request, and logged`);
	}
	return next();
}

export const refreshAccessTokenHandler = async (req: Request, res: Response) => {
    const refreshToken = get(req, "headers.x-refresh") as string;
    // log.info(`Received refresh token in refresh handler`);
    const decoded = verifyJwt<Session>(refreshToken, "refreshTokenPublicKey") as Session | null;
    const session = get(decoded, "session") as unknown as Session | null;
    if(!session){
        return res.status(401).send("Invalid token");
    }
    if(!session.valid){
        return res.status(401).send("Invalid session");
    }

    const user = session.user;
    // log.info(`User ${user.id} found in session`);

    if(!user){
        return res.status(401).send("Invalid user");
    }

    const accessToken = signAccessToken(user);
    return res.status(200).json({accessToken});
};

export const requireUser = (req: Request, res: Response, next: NextFunction) => {
    // console.log(res.locals.user.id)
    if(res.locals.user && res.locals.user.id && res.locals.user.email && res.locals.user.username){
        // console.log(res.locals.user.id)
        return next();
    }
    return res.status(403).send("Unauthorized");
};
