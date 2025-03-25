import pymongo
import asyncio

async def GetCollection(Client: pymongo.MongoClient, Database: str, Collection: str):
    database: pymongo.database.Database = Client[Database]  # Zugriff auf die Datenbank
    collection: pymongo.collection.Collection = database[Collection]  # Zugriff auf die Collection
    
    return collection  



