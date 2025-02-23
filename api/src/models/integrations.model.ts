export type UserInfo = {
    api_key?: string;
    api_secret?: string;
}

export type Platform = {
    name: string;
    actions: string[];
    objects: string[];
    modifiers: string[];
}

export type Integration ={
    id: number
    type: 'media' | 'management' | 'communication';
    sub_type?: 'film' | 'music';
    connected_platform: Platform;
}


export class Platforms {
    static Spotify: Platform = {
        name: 'spotify',
        actions: ['play', 'pause', 'stop', 'skip', 'shuffle', 'repeat', 'loop', 'resume', 'rewind', 'forward'],
        objects: ['song', 'video', 'playlist', 'track', 'album', 'movie', 'episode', 'audio', 'music', 'stream'],
        modifiers: ['next', 'previous', 'current', 'random', 'favorite', 'liked', 'recommended', 'this']
    }
    static Default: Platform = {
        name: 'default',
        actions: [],
        objects: [],
        modifiers: []
    }
}