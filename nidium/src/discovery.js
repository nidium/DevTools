const dgram = require('dgram');
const DISCOVER_MSG = "ping";
const DISCOVER_TIMEOUT = 5000;

const g_KnownInstance = {};
const g_Client = dgram.createSocket("udp4");
let g_CleanTimer = -1;
let g_DisoverTimer = -1;

module.exports = {
    start: function() {
        g_CleanTimer = setInterval(() => {
            for (let k in g_KnownInstance) {
                const item = g_KnownInstance[k];
                if (item.lastSeen + DISCOVER_TIMEOUT < Date.now()) {
                    this.onlost(item.ip, item.port);
                    delete g_KnownInstance[k];
                }
            }
        }, 1000);

        g_Client.bind(() => {
            g_Client.setBroadcast(true);

            g_DisoverTimer = setInterval(() => {
                g_Client.send(DISCOVER_MSG, 0, DISCOVER_MSG.length, 1234, "255.255.255.255");
            }, 500);

            g_Client.on("message", (msg, rinfo) => {
                let key = rinfo.address + ":" + rinfo.port;
                if (!g_KnownInstance[key]) {
                    g_KnownInstance[key] = {
                        "lastSeen": Date.now(),
                        "ip": rinfo.address,
                        "port": rinfo.port,
                        "title": msg
                    }
                    this.ondiscover(g_KnownInstance[key]);
                } else {
					g_KnownInstance[key].lastSeen = Date.now();
				}
            });
        });
    },

    stop: function() {
        clearTimeout(g_CleanTimer);
        clearTimeout(g_DisoverTimer);
        g_Client.close();
    }
}
