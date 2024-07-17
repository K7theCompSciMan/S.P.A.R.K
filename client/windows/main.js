const { app, BrowserWindow } = require('electron')

const createWindow = () => {
    const win = new BrowserWindow({})
    win.maximize()
    win.setMenu(null)
    win.loadURL('http://localhost:5173/')
}

app.whenReady().then(() => {
    createWindow()
})