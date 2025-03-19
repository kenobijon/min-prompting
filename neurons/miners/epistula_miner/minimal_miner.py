import asyncio
import json
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import uvicorn
from loguru import logger

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
        app = FastAPI()
        
        # Add a simple route for chat completions
        app.add_api_route(
            "/v1/chat/completions",
            self.create_chat_completion,
            methods=["POST"]
        )

        # Run the server
        uvicorn.run(app, host="0.0.0.0", port=8001)

if __name__ == "__main__":
    logger.info("Starting minimal miner...")
    miner = MinimalMiner()
    miner.run()
    logger.info("Minimal miner running on http://0.0.0.0:8001") 