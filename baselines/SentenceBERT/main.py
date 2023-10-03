from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import time
import json

def corpus_builder():
    corpus = []
    with open('data/txt_db/tango/OB_best.jsonl', 'r') as f:
        data = f.readlines()
    for line in data:
        corpus.append(json.loads(line)['caption'])
    return corpus

def query_builder():
    query_list = []
    with open('data/txt_db/tango/OB_best.jsonl', 'r') as f:
        data = f.readlines()
    for line in data:
        query_list.append(json.loads(line)['caption'])
    return query_list


## video2text
corpus = corpus_builder()
actual_results = corpus_builder()
query_list = query_builder()

## text2video
# corpus = query_builder()
# actual_results = query_builder()
# query_list = corpus_builder()


model = SentenceTransformer('all-mpnet-base-v2')
encoded_corpus = model.encode(corpus)

## index with ID - gives the exact results (don't compress the vectors)
## This is cosine similarity
index = faiss.IndexIDMap(faiss.IndexFlatIP(768))
## add the vectors to the index
index.add_with_ids(encoded_corpus, np.array(range(len(corpus))))
## serialize the index
faiss.write_index(index, 'index.bin')


## semantic search
def search(query_list, k):
    t=time.time()
    query_vec = model.encode(query_list)
    distances, top_k = index.search(query_vec, k)
    print('total time: {}'.format(time.time()-t))
    results = []
    for top_k_indices in top_k:
        results.append([corpus[idx] for idx in top_k_indices])
    return results, distances



def compute_MRR(predicted_results):
    mrr_rankings = []
    rank = None
    for i, result in enumerate(predicted_results, start=0):
        if actual_results[i] in result:
            # get the index of the relevant doc
            rank = result.index(actual_results[i])
        if rank is not None:
            mrr_rankings.append(rank)

    rr_list = [1 / (rank + 1) for rank in mrr_rankings]
    return sum(rr_list) / len(rr_list)

def compute_MAP(ranked_lists):
    ap_sum = 0
    index = 0
    for ranked_list in ranked_lists:
        precision_sum = 0
        relevant_docs = 0
        if actual_results[index] in ranked_list:  # doc is relevant
            relevant_docs += 1
            ##get the index of the relevant doc
            relevant_index = ranked_list.index(actual_results[index])
            rank = relevant_index + 1
            precision_sum += relevant_docs / (rank + 1)
        if relevant_docs == 0:
            ap_sum += 0
        else:        
            ap_sum += precision_sum / relevant_docs
        index+=1
    map = ap_sum / len(ranked_lists)
    return map

def hits(ranked_lists):
    hits = 0
    index = 0
    for ranked_list in ranked_lists:
        if actual_results[index] in ranked_list:
            hits += 1
        index += 1
    return hits

if __name__ == '__main__':
    
    results, distances = search(query_list, 60)
    print('MRR: {}'.format(compute_MRR(results)))
    ## top k results
    for k in range(1, len(query_list)+1):
        # print('Top {} results'.format(k))
        filtered_results = [lst[:k] for lst in results]
        # print('MAP: {}'.format(compute_MAP(filtered_results)))
        # print('Hit Rate: {}'.format(hits(filtered_results)))

        print('HIT@{}: {} MAP: {}'.format(k, hits(filtered_results), compute_MAP(filtered_results)))