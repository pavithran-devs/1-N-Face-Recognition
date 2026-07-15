import os
import csv
import asyncio
import numpy as np
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.config.settings import get_settings
from app.database.engine import AsyncSessionLocal
from app.models.candidate import Candidate
from app.models.face_embedding import FaceEmbedding

async def main():
    print("=== Start All-to-All Candidate Similarity Comparison ===")
    
    # 1. Fetch all candidates and their embeddings from the database
    print("Fetching all candidates and their embeddings from database...")
    async with AsyncSessionLocal() as session:
        stmt = select(Candidate).options(selectinload(Candidate.embeddings))
        result = await session.execute(stmt)
        candidates = result.scalars().all()
        
    print(f"Fetched {len(candidates)} candidates from PostgreSQL.")
    
    # 2. Extract valid embeddings
    embeddings = []
    metadata = []  # list of dict: {uuid, candidate_id, name, email}
    
    for cand in candidates:
        if not cand.embeddings:
            continue
        for emb_record in cand.embeddings:
            emb_vector = np.array(emb_record.embedding, dtype=np.float32)
            # Ensure it is L2-normalized
            norm = np.linalg.norm(emb_vector)
            if norm > 1e-10:
                emb_vector = emb_vector / norm
            embeddings.append(emb_vector)
            metadata.append({
                "uuid": str(cand.id),
                "candidate_id": cand.candidate_id,
                "name": cand.name,
                "email": cand.email
            })
            
    num_embeddings = len(embeddings)
    print(f"Loaded {num_embeddings} valid embeddings for comparison.")
    if num_embeddings < 2:
        print("Not enough embeddings to perform comparison.")
        return
        
    # Convert list of vectors to a single NumPy matrix of shape (N, 512)
    E = np.vstack(embeddings)
    
    # 3. Compute the cosine similarity matrix
    print("Computing all-to-all similarity matrix...")
    # S has shape (N, N) where S[i, j] is the cosine similarity between embedding i and j
    S = np.dot(E, E.T)
    
    # 4. Find pairs above threshold (exclude self-comparison and duplicate pairs)
    # i.e., only consider i < j
    pairs = []
    for i in range(num_embeddings):
        for j in range(i + 1, num_embeddings):
            cand_a = metadata[i]
            cand_b = metadata[j]
            
            same_profile = (cand_a["uuid"] == cand_b["uuid"])
            score = float(S[i, j])
            
            pairs.append({
                "candidate_a_id": cand_a["candidate_id"],
                "candidate_a_name": cand_a["name"],
                "candidate_a_email": cand_a["email"],
                "candidate_b_id": cand_b["candidate_id"],
                "candidate_b_name": cand_b["name"],
                "candidate_b_email": cand_b["email"],
                "similarity_score": score,
                "same_profile": same_profile
            })
            
    # 5. Sort by similarity score descending
    pairs.sort(key=lambda x: x["similarity_score"], reverse=True)
    
    # 6. Save results to CSV
    csv_file = "/home/pavithranraj/Desktop/1:N Face recognition/face_identification/all_to_all_duplicates.csv"
    with open(csv_file, mode='w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            "candidate_a_id", "candidate_a_name", "candidate_a_email",
            "candidate_b_id", "candidate_b_name", "candidate_b_email",
            "similarity_score", "same_profile"
        ])
        writer.writeheader()
        writer.writerows(pairs)
        
    print(f"CSV results written to {csv_file}")
    
    # 7. Print top matches (excluding same_profile, above 0.30)
    print("\n=== TOP 20 HIGHLY SIMILAR/DUPLICATE PAIRS (EXCLUDING SAME PROFILE) ===")
    printed_count = 0
    for p in pairs:
        if p["same_profile"]:
            continue
        if p["similarity_score"] < 0.25:
            break
        printed_count += 1
        print(f"Score: {p['similarity_score']:.4f} | "
              f"Profile A: {p['candidate_a_name']} ({p['candidate_a_id']}) <-> "
              f"Profile B: {p['candidate_b_name']} ({p['candidate_b_id']})")
        if printed_count >= 20:
            break
            
    if printed_count == 0:
        print("No duplicate/highly similar pairs found above score 0.25.")
        
    # Statistics of similarities (excluding same-profile)
    diff_scores = [p["similarity_score"] for p in pairs if not p["same_profile"]]
    if diff_scores:
        print("\n=== COMPARISON STATISTICS ===")
        print(f"Total cross-comparisons: {len(diff_scores)}")
        print(f"Max similarity score: {np.max(diff_scores):.4f}")
        print(f"Min similarity score: {np.min(diff_scores):.4f}")
        print(f"Average similarity score: {np.mean(diff_scores):.4f}")
        print(f"Number of pairs scoring >= 0.60: {sum(1 for s in diff_scores if s >= 0.60)}")
        print(f"Number of pairs scoring >= 0.50: {sum(1 for s in diff_scores if s >= 0.50)}")
        print(f"Number of pairs scoring >= 0.40: {sum(1 for s in diff_scores if s >= 0.40)}")
        print("=============================")

if __name__ == "__main__":
    asyncio.run(main())
