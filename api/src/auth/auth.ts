import User, { PublicUser } from "../models/user.model";
import { signJwt, verifyJwt } from "../utils/jwt";
import { Session } from "./session";
import { Request, Response, NextFunction } from "express";
import { get } from "lodash";
import { STATUS_CODES } from "http";

/**
 * The function `signRefreshToken` generates a refresh token for a user and returns it.
 * @param {User} user - The `user` parameter is an object that represents a user in your system. It
 * likely contains information such as the user's ID, username, email, and other relevant details.
 * @returns The function `signRefreshToken` returns a signed refresh token for the provided user.
 */
export function signRefreshToken(user: User) {
	const publicUser = new PublicUser(user);
	// log.info(`Signing refresh token for user ${publicUser}`);
	const session = new Session(publicUser);
	// log.info(`Session created for user ${session.user}`);
	const refreshToken = signJwt({ session }, "refreshTokenPrivateKey", {
		expiresIn: "1w",
	});
	// log.info(`Refresh token created for user ${session.user}`);
	return refreshToken;
}

/**
 * The function `signAccessToken` generates and signs an access token for a user.
 * @param {User} user - The `user` parameter is an object that represents a user in your application.
 * It is used to create a signed access token for the user.
 * @returns The function `signAccessToken` is returning the access token that is generated using the
 * `signJwt` function with the user's information and a specific expiration time of 15 minutes.
 */
export function signAccessToken(user: User) {
	const publicUser = new PublicUser(user);
	// log.info(`Signing access token for user ${publicUser.id}`);
	const accessToken = signJwt({ user: publicUser }, "accessTokenPrivateKey", {
		expiresIn: "15m",
	});
	if(accessToken === "Error signing JWT") {
		throw new Error("Error signing JWT");
	}
	// log.info(`Access token created ${accessToken}`);
	return accessToken;
}

/**
 * The function `deserializeUser` extracts and verifies an access token from the request headers, then
 * attaches the decoded user information to the response locals.
 * @param {Request} req - The `req` parameter in the `deserializeUser` function stands for the request
 * object. It contains information about the HTTP request that is being made, such as the request
 * headers, body, parameters, and query strings. This parameter is typically used to extract data sent
 * by the client to the server.
 * @param {Response} res - The `res` parameter in the `deserializeUser` function stands for the
 * response object in Express.js. It is used to send a response back to the client making the request.
 * You can use methods on the `res` object to send data, set headers, and end the response among other
 * things
 * @param {NextFunction} next - The `next` parameter in the `deserializeUser` function is a callback
 * function that is used to pass control to the next middleware function in the stack. When called, it
 * invokes the next middleware function in the stack. This is commonly used in Express.js middleware
 * functions to move to the next middleware in
 * @returns The `deserializeUser` function is returning a Promise, as it is an async function. The
 * return value of the function is `next()`, which is a function that passes control to the next
 * middleware function in the stack.
 */
export const deserializeUser = async (
	req: Request,
	res: Response,
	next: NextFunction
) => {
	const accessToken = (req.headers.authorization || "")
		.replace("Bearer", "")
		.replace(" ", "");
	// log.info(accessToken)
	if (!accessToken) {
		// log.info(`No token found in deserializeUser ${accessToken}`);
		return next();
	}
	// log.info(`Token found in deserializeUser`);
	const decoded = verifyJwt<User>(accessToken, "accessTokenPublicKey");
	const user = get(decoded, "user") as unknown as User | null;
	if (user !== null) {
		res.locals.user = user;
		// // log.info(`User ${res.locals.user.email} found in request, and logged`);
	}
	return next();
};

/**
 * The function `refreshAccessTokenHandler` verifies a refresh token, generates a new access token, and
 * returns it in a JSON response.
 * @param {Request} req - The `req` parameter in the `refreshAccessTokenHandler` function is an object
 * representing the HTTP request. It contains information about the incoming request such as headers,
 * body, parameters, etc. In this specific function, the `req` parameter is used to extract the refresh
 * token from the request headers using
 * @param {Response} res - The `res` parameter in the `refreshAccessTokenHandler` function is an
 * instance of the Express Response object. It is used to send a response back to the client making the
 * request. In this function, it is used to send status codes and JSON data back to the client after
 * processing the refresh token
 * @returns The `refreshAccessTokenHandler` function returns a response with a status code of 200 and a
 * JSON object containing the newly generated access token.
 */
export const refreshAccessTokenHandler = async (
	req: Request,
	res: Response
) => {
	const refreshToken = get(req, "headers.x-refresh") as string;
	// log.info(`Received refresh token in refresh handler`);
	const decoded = verifyJwt<Session>(
		refreshToken,
		"refreshTokenPublicKey"
	) as Session | null;
	const session = get(decoded, "session") as unknown as Session | null;
	if (!session) {
		return res.status(401).send("Invalid token");
	}
	if (!session.valid) {
		return res.status(401).send("Invalid session");
	}

	const user = session.user;
	// log.info(`User ${user.id} found in session`);

	if (!user) {
		return res.status(401).send("Invalid user");
	}

	const accessToken = signAccessToken(user);
	return res.status(200).json({ accessToken });
};

export const requireUser = (
	req: Request,
	res: Response,
	next: NextFunction
) => {
	// console.log(res.locals.user.id)
	if (
		res.locals.user &&
		res.locals.user.id &&
		res.locals.user.username
	) {
		// console.log(res.locals.user.id)
		return next();
	}
	return res.status(403).send("Unauthorized");
};
