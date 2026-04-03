import { Request, Response, NextFunction } from "express";
import { StatusCodes } from "http-status-codes";
import { ZodTypeAny } from "zod";

export const validateBody =
	(schema: ZodTypeAny) =>
	(req: Request, res: Response, next: NextFunction) => {
		const parsed = schema.safeParse(req.body);
		if (!parsed.success) {
			return res.status(StatusCodes.BAD_REQUEST).json({
				error: "Invalid request body",
				details: parsed.error.flatten(),
			});
		}
		req.body = parsed.data;
		next();
	};
