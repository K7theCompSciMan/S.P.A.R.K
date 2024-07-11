"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Session = void 0;
class Session {
    constructor(user) {
        this.valid = true;
        this.user = user;
        this.dateCreated = new Date(Date.now());
        this.endDate = new Date(Date.now() + 1000 * 60 * 60 * 24 * 7);
        this.valid = true;
    }
    invalidate() {
        this.valid = false;
    }
}
exports.Session = Session;
