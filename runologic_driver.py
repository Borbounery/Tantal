import asyncio
from runologic import encrypt, decrypt, c_e, c_d
import websockets, base64
import json

PORT = 4174
HEARTBEAT_TIMEOUT = 10 
p_c,ap_c = 5, 3

async def send_data(ws, data):
    return await ws.send(c_e(p_c, base64.b64encode(data.encode("utf-8")).decode("utf-8"), ap_c))
    
async def handle_connection(websocket: websockets.WebSocketClientProtocol):
    try:
        await send_data(websocket, json.dumps({"msg": "send_hash"}))
        data = await websocket.recv()
        data_dict = json.loads(base64.b64decode(c_d(p_c, data, ap_c)).decode("utf-8"))
        k,p,ap = "key",2,16
        if "hash" not in data_dict or not isinstance(data_dict["hash"], str) or len(data_dict["hash"]) != 32:
            await send_data(websocket, json.dumps({"error": "Invalid hash"}))
            await websocket.wait_closed()
            return
        client_hash = data_dict["hash"]
        await send_data(websocket, json.dumps({"msg": "ready"}))
        while True:
            data = await websocket.recv()
            data_dict = json.loads(base64.b64decode(c_d(p_c, data, ap_c)).decode("utf-8"))
            if data_dict.get("msg") == "my_hash":
                await send_data(websocket, json.dumps({"my_hash": client_hash}))  # Send back client hash
            elif data_dict.get("msg") == "heartbeat":
                await send_data(websocket, json.dumps({"msg": "heartbeat"}))
            elif data_dict.get("msg") == "encrypt":
                await send_data(websocket, json.dumps({"msg": "encrypt_success","content":encrypt(data_dict["content"],k,p,ap)}))
            elif data_dict.get("msg") == "decrypt":
                await send_data(websocket, json.dumps({"msg": "decrypt_success","content":decrypt(data_dict["content"],k,p,ap)}))
            elif data_dict.get("msg") == "set_custom_encryption_options":
                k,p,ap = data_dict["L"][0],data_dict["L"][1],data_dict["L"][2]
                await send_data(websocket, json.dumps({"msg": "thanks"}))
    except websockets.ConnectionClosed:
        pass

async def main():
    async with websockets.serve(handle_connection, "localhost", PORT):
        await asyncio.Future()
if __name__ == "__main__":
    asyncio.run(main())

#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