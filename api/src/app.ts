import express from "express";
import * as dotevnv from "dotenv";
import cors from "cors";
import helmet from "helmet";
import { userRouter } from "./routes/user.routes";
import { groupRouter } from "./routes/group.routes";
import { authRouter } from "./auth/auth.router";
import { deserializeUser } from "./auth/auth";
import { deviceRouter } from "./routes/device.routes";

dotevnv.config();

if (!process.env.PORT) {
	console.log(`No port value specified...`);
}

const PORT = parseInt(process.env.PORT as string, 10);

const app = express();

app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(cors());
app.use(helmet());
app.use(deserializeUser);
app.use("/", authRouter);
app.use("/", userRouter);
app.use("/", groupRouter);
app.use("/", deviceRouter);
app.listen(PORT, () => {
	console.log(`Server is listening on port ${PORT}`);
});
app.get("/", (req, res) => {
	res.send("Hello World");
})
