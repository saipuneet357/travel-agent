import redis
from redis.commands.search.query import Query
from ml_api import get_embeddings
import numpy as np
import json
import uuid

# Figure out a way to query the prompt based on prompt id, as we will be storing the prompt id in our offline store.

class RedisClient:
    def __init__(self, host='localhost', port=6379, db=0):
        self.redis_client = redis.Redis(host=host, port=port, db=db)
    

    def get_redis_client(self):
        return self.redis_client


    def insert_prompts(self, data):
        pipeline = self.redis_client.pipeline()
        
        for prompt in data:
            uid = uuid.uuid4()
            redis_key = f"prompts:{uid}"
            pipeline.json().set(redis_key, "$", prompt)

            prompt_text = prompt['prompt']
            prompt_embedding = get_embeddings([prompt_text])[0]
            pipeline.json().set(redis_key, "$.prompt_embedding", prompt_embedding)

            pipeline.json().set(redis_key, "$.prompt_id", str(uid))

            # Setting Expiry
            pipeline.expire(redis_key, 60 * 60 * 24)
        
        pipeline.execute()

        return str(uid)


    def search_prompt(self, prompt_text, distance_threshold=0.2):
        query = (
            Query('(*)=>[KNN 3 @vector $query_vector AS vector_score]')
            .sort_by('vector_score')
            .dialect(2)
        )
        
        # Query the vector database and return the nearest response
        search_result = self.redis_client.ft('idx:prompts_vss').search(query, {'query_vector': np.array(get_embeddings([prompt_text])[0], dtype=np.float32).tobytes()})
        least_score = 1
        least_score_doc = None
        for doc in search_result.docs:
            if float(doc.vector_score) < float(least_score) and float(doc.vector_score) <= float(distance_threshold):
                least_score = float(doc.vector_score)
                least_score_doc = doc

        if least_score_doc is not None:
            # response = json.loads(least_score_doc.json)['response']
            # return response
            yield True
            yield from json.loads(least_score_doc.json)['response']
        else:
            yield False


if __name__ == "__main__":
    pass
    # FT.CREATE idx:prompts_vss ON JSON PREFIX 1 prompts: SCORE 1.0  
    # SCHEMA  
    #     $.prompt TEXT WEIGHT 1.0 NOSTEM    
    #     $.response TEXT WEIGHT 1.0 NOSTEM    
    #     $.prompt_embedding AS vector VECTOR FLAT 6 TYPE FLOAT32 DIM 384 DISTANCE_METRIC COSINE
