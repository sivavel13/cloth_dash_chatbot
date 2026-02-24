import json
import pickle
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

# load knowledge base
with open("../data/knowledge_base.json", "r", encoding="utf-8") as f:
    data = json.load(f)

questions = [item["question"] for item in data]

embeddings = model.encode(questions)

# save vectors INSIDE backend folder
with open("vectors.pkl", "wb") as f:
    pickle.dump((embeddings, data), f)

print("vectors.pkl created successfully")