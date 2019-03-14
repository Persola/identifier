from pymongo import MongoClient

def copy_sample(orig_coll_name, new_coll_name, count):
    client = MongoClient()
    client.who[new_coll_name].insert_many(
        client.who[orig_coll_name].aggregate([{
            '$sample': {'size': count}
        }])
    )
