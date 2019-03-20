from pymongo import MongoClient

def copy_sample(orig_coll_name, new_coll_name, count):
    '''Copies a sample of documents into a new collection'''

    client = MongoClient()
    if client.who[new_coll_name].count({}) > 0:
        raise BaseException('Tried to insert sample into existing collection')
    client.who[new_coll_name].insert_many(
        client.who[orig_coll_name].aggregate([{
            '$sample': {'size': count}
        }])
    )
