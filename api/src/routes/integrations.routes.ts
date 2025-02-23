import express, {Request, Response} from "express";
import { requireUser } from "../auth/auth";
import * as db from '../database/user.db';
import { StatusCodes } from "http-status-codes";

export const integrationRouter = express.Router();

integrationRouter.get("/integrations", requireUser, async (req: Request, res: Response) => {
    try {
        const integrations = await db.getIntegrations(res.locals.user);
        if (!integrations) {
            res.status(StatusCodes.NOT_FOUND).send(`No integrations found for user ${res.locals.user.id}`);
        }
        return res.status(StatusCodes.OK).json(integrations);
    } catch (error) {
        return res.status(StatusCodes.INTERNAL_SERVER_ERROR).json(error);
    }
});

integrationRouter.post("/integrations", requireUser, async (req: Request, res: Response) => {
    try {
        const integrations = await db.getIntegrations(res.locals.user);
        if (!integrations) {
            res.status(StatusCodes.NOT_FOUND).send(`No integrations found for user ${res.locals.user.id}`);
        }
        const newIntegrations = await db.addIntegration(res.locals.user, req.body);
        if (!newIntegrations) {
            res.status(StatusCodes.INTERNAL_SERVER_ERROR).send(`Failed to add integration for user ${res.locals.user.id}`);
        }
        return res.status(StatusCodes.OK).json(integrations);
    } catch (error) {
        return res.status(StatusCodes.INTERNAL_SERVER_ERROR).json(error);
    }
});

integrationRouter.delete("/integrations", requireUser, async (req: Request, res: Response) => {
    try {
        const integrations = await db.getIntegrations(res.locals.user);
        if (!integrations) {
            res.status(StatusCodes.NOT_FOUND).send(`No integrations found for user ${res.locals.user.id}`);
        }
        const newIntegrations = await db.removeIntegration(res.locals.user, req.body);
        if (!newIntegrations) {
            res.status(StatusCodes.INTERNAL_SERVER_ERROR).send(`Failed to remove integration for user ${res.locals.user.id}`);
        }
        return res.status(StatusCodes.OK).json(integrations);
    } catch (error) {
        return res.status(StatusCodes.INTERNAL_SERVER_ERROR).json(error);
    }
});