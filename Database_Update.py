import pymongo

MongoClient: pymongo.MongoClient = pymongo.MongoClient("mongodb://localhost:27017")

def UpdateMain():
    Structure = {
        "GuildID": None,
        "ERLC-Token": None,
        "Roles": [],
        "Shifts": [],
        "Active_Shifts": [],
        "Command_Queue": []
    }

    DB = MongoClient.get_database("Patrolly")
    Collection = DB.get_collection("Guilds")

    for entry in Collection.find():
        update_needed = False
        updated_entry = entry.copy()

        for key, default_value in Structure.items():
            if key not in entry:
                updated_entry[key] = default_value
                update_needed = True

        if update_needed:
            Collection.update_one({"_id": entry["_id"]}, {"$set": updated_entry})

UpdateMain()
