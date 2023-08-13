import uvicorn
import routers
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

tags_metadata = [
    {
        "name": "account",
        "description": "Операции с аккаунтом",
    },
    {
        "name": "events",
        "description": "Операции с событиями",
    },
]

origins = ["*"]
app = FastAPI(openapi_tags=tags_metadata)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["POST", "PUT", "GET", "DELETE"],
    allow_headers=["*"]
)
oauth2_scheme = routers.oauth2_scheme
app.include_router(routers.router)


if __name__ == "__main__":
    uvicorn.run(app, host="100.73.220.5", port=80)
