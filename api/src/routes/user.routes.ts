import express, { NextFunction, Request, Response } from "express";
import { User } from "../xata";
import { StatusCodes } from "http-status-codes";
import * as db from "../db/user.db";
export const userRouter = express.Router();
import bcrypt from "bcryptjs";
import { PublicUser } from "../models/user.model";
import { requireUser, signAccessToken, signRefreshToken } from "../auth/auth";
userRouter.get("/users", async (req: Request, res: Response) => {
  try {
    const users = await db.getUsers();
    if (!users) {
      res.status(StatusCodes.NOT_FOUND).send("No users found");
    }
    return res.status(StatusCodes.OK).json(users);
  } catch (error) {
    return res.status(StatusCodes.INTERNAL_SERVER_ERROR).json(error);
  }
});

userRouter.get("/user/:id", async (req: Request, res: Response) => {
  try {
    const user = await db.getUserById(req.params.id);
    if (!user) {
      res.status(StatusCodes.NOT_FOUND).send("User not found");
    }
    const publicUser = new PublicUser(user);
    return res.status(StatusCodes.OK).json({ user: publicUser });
  } catch (error) {
    return res.status(StatusCodes.INTERNAL_SERVER_ERROR).json(error);
  }
});

userRouter.post("/register", async (req: Request, res: Response) => {
  try {
    const { username, email, password } = req.body;
    if (!username || !email || !password) {
      return res.status(StatusCodes.BAD_REQUEST).send("Invalid input");
    }
    const user = await db.getUserByName(email);
    if (user) {
      return res
        .status(StatusCodes.BAD_REQUEST)
        .send("User with the same name already exists");
    }
    
    const newUser = await db.createUser({ username, password } as User);
    if (!newUser) {
      return res
        .status(StatusCodes.INTERNAL_SERVER_ERROR)
        .send("User not created");
    }
    // sign tokens
    const accessToken = signAccessToken(newUser);
    const refreshToken = signRefreshToken(newUser);

    const publicNewUser = new PublicUser(newUser);

    return res
      .status(StatusCodes.CREATED)
      .json({ user: publicNewUser, accessToken, refreshToken });
  } catch (error) {
    return res.status(StatusCodes.INTERNAL_SERVER_ERROR).json(error);
  }
});

userRouter.post("/login", async (req: Request, res: Response) => {
  try {
    const { username, password } = req.body;

    if (!username || !password) {
      return res.status(StatusCodes.BAD_REQUEST).send("Invalid input");
    }

    const user = await db.getUserByName(username);

    if (!user) {
      return res
        .status(StatusCodes.NOT_FOUND)
        .send("Invalid Email or Password");
    }

    const isPasswordValid = await db.checkPassword(user.id, password);

    if (!isPasswordValid) {
      return res
        .status(StatusCodes.UNAUTHORIZED)
        .send("Invalid Email or Password");
    }

    // sign tokens
    const accessToken = signAccessToken(user);
    const refreshToken = signRefreshToken(user);
    // log.info(`User logged in ${user} | accessToken: ${accessToken} | refreshToken: ${refreshToken}`);
    const publicUser = new PublicUser(user);
    return res
      .status(StatusCodes.OK)
      .send({ user: publicUser, accessToken, refreshToken });
  } catch (error) {
    return res.status(StatusCodes.INTERNAL_SERVER_ERROR).json(error);
  }
});

userRouter.put("/user", requireUser, async (req: Request, res: Response) => {
  try {
    const user = res.locals.user.user as User;

    if (!user) {
      return res
        .status(StatusCodes.NOT_FOUND)
        .send("User not in res.locals.user");
    }

    const updateUser = await db.updateUser({ ...req.body, id: user.id });
    const publicUser = new PublicUser(updateUser!);
    return res.status(StatusCodes.OK).json({ user: publicUser });
  } catch (error) {
    return res.status(StatusCodes.INTERNAL_SERVER_ERROR).json(error);
  }
});

userRouter.delete("/user", requireUser, async (req: Request, res: Response) => {
  try {
    const user = res.locals.user.user as User;
    if (!user) {
      return res.status(StatusCodes.NOT_FOUND).send("User not signed in");
    }

    await db.deleteUser(user.id);

    return res.status(StatusCodes.OK).send("User deleted");
  } catch (error) {
    return res.status(StatusCodes.INTERNAL_SERVER_ERROR).json({ error });
  }
});

userRouter.get("/me", requireUser, async (req: Request, res: Response) => {
  return res.status(StatusCodes.OK).json(res.locals.user);
});
