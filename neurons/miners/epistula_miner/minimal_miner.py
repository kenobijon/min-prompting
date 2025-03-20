import asyncio
import json
import requests
import netaddr
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import uvicorn
from loguru import logger
from bittensor.core.extrinsics.serving import serve_extrinsic
from shared import settings

# Load settings
settings.shared_settings = settings.SharedSettings.load(mode="miner")
shared_settings = settings.shared_settings

class MinimalMiner:
    def __init__(self):
        self.should_exit = False

    async def create_chat_completion(self, request: Request):
        async def dummy_stream():
            # Dummy response
            dummy_response = {
                "choices": [{
                    "delta": {"content": "This is a dummy response from the minimal miner. "},
                    "index": 0,
                    "finish_reason": None
                }]
            }
            yield f"data: {json.dumps(dummy_response)}\n\n"
            await asyncio.sleep(0.1)
            
            # End of stream
            end_response = {
                "choices": [{
                    "delta": {},
                    "index": 0,
                    "finish_reason": "stop"
                }]
            }
            yield f"data: {json.dumps(end_response)}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(dummy_stream(), media_type="text/event-stream")

    def run(self):
        # Get external IP
        external_ip = None
        if not external_ip or external_ip == "[::]":
            try:
                external_ip = requests.get("https://checkip.amazonaws.com").text.strip()
                netaddr.IPAddress(external_ip)
            except Exception:
                logger.error("Failed to get external IP")

        logger.info(
            f"Serving miner endpoint {external_ip}:{shared_settings.AXON_PORT} on network: {shared_settings.SUBTENSOR_NETWORK} with netuid: {shared_settings.NETUID}"
        )

        # Serve the extrinsic
        serve_success = serve_extrinsic(
            subtensor=shared_settings.SUBTENSOR,
            wallet=shared_settings.WALLET,
            ip=external_ip,
            port=shared_settings.AXON_PORT,
            protocol=4,
            netuid=shared_settings.NETUID,
        )
        if not serve_success:
            logger.error("Failed to serve endpoint")
            return

        app = FastAPI()
        
        # Add a simple route for chat completions
        app.add_api_route(
            "/v1/chat/completions",
            self.create_chat_completion,
            methods=["POST"]
        )

        # Run the server
        uvicorn.run(app, host="0.0.0.0", port=shared_settings.AXON_PORT)

if __name__ == "__main__":
    logger.info("Starting minimal miner...")
    miner = MinimalMiner()
    miner.run()
    logger.info(f"Minimal miner running on http://0.0.0.0:{shared_settings.AXON_PORT}") 