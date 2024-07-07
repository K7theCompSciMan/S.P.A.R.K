import express, {Request, Response} from 'express';
import  * as db from '../db/group.db';

export const groupRouter = express.Router();
// TODO: Implement ID10T error handling
groupRouter.get('/groups', async (req: Request, res: Response) => {
    res.json(await db.getAllGroups());
});

groupRouter.get('/group/:id', async (req: Request, res: Response) => {
    res.json(await db.getGroupById(req.params.id));
});

groupRouter.post('/group', async (req: Request, res: Response) => {
    res.json(await db.createGroup(req.body));
});

groupRouter.put('/group', async (req: Request, res: Response) => {
    res.json(await db.updateGroup(req.body));
});

groupRouter.delete('/group/:id', async (req: Request, res: Response) => {
    res.json(await db.deleteGroup(req.params.id));
});

groupRouter.post('/group/addDevice', async (req: Request, res: Response) => {
    res.json(await db.addDeviceToGroup(req.body.groupId, req.body.deviceId, req.body.deviceType));
})