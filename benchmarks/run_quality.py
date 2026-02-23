import os
import argparse
import numpy as np
import pandas as pd
from tabulate import tabulate
from tqdm import tqdm
from sklearn.metrics import precision_recall_curve, auc
from concurrent.futures import ProcessPoolExecutor
from benchmarks.utils import (
    get_base_files, ensure_dir, generate_augmentations, 
    get_hash_lp, get_hash_ih
)
import imagehash

# Algorithms configuration
ALGORITHMS = [
    ("aHash", imagehash.average_hash, "ahash"),
    ("dHash", imagehash.dhash, "dhash"),
    ("pHash", imagehash.phash, "phash"),
    ("wHash", imagehash.whash, "whash"),
]

def prepare_quality_dataset(base_images, output_dir, fmt="JPEG"):
    print(f"Preparing quality dataset in {output_dir}...")
    ensure_dir(output_dir)
    all_files = []
    ground_truth = {}
    
    with ProcessPoolExecutor() as executor:
        futures = [executor.submit(generate_augmentations, p, output_dir, fmt) for p in base_images]
        for f in tqdm(futures, desc="Generating augmentations"):
            results = f.result()
            for path, base_name in results:
                all_files.append(path)
                ground_truth[path] = base_name
                
    return all_files, ground_truth

def evaluate_quality(files, ground_truth):
    print(f"Evaluating quality metrics on {len(files)} images...")
    hashes = {f: {} for f in files}
    
    for p in tqdm(files, desc="Computing hashes"):
        for name, ih_func, lp_attr in ALGORITHMS:
            hashes[p][f"{name}_ih"] = get_hash_ih(p, ih_func)
            hashes[p][f"{name}_lp"] = get_hash_lp(p, lp_attr)

    n = len(files)
    y_true = []
    dist_vectors = {f"{a[0]}_{lib}": [] for a in ALGORITHMS for lib in ["ih", "lp"]}

    print(f"Comparing {n*(n-1)//2} pairs...")
    for i in range(n):
        f1 = files[i]
        b1 = ground_truth[f1]
        for j in range(i+1, n):
            f2 = files[j]
            b2 = ground_truth[f2]
            y_true.append(1 if b1 == b2 else 0)
            
            for key in dist_vectors.keys():
                h1, h2 = hashes[f1][key], hashes[f2][key]
                if isinstance(h1, int):
                    dist = bin(h1 ^ h2).count('1')
                else:
                    dist = h1 - h2
                dist_vectors[key].append(dist)

    results = []
    y_true_arr = np.array(y_true)
    for key, dists in dist_vectors.items():
        dists_arr = np.array(dists)
        precision, recall, _ = precision_recall_curve(y_true_arr, -dists_arr)
        
        # Best F1
        best_f1 = 0
        for t in range(0, 20): # typical range for hashing
            preds = (dists_arr <= t).astype(int)
            tp = ((preds == 1) & (y_true_arr == 1)).sum()
            fp = ((preds == 1) & (y_true_arr == 0)).sum()
            fn = ((preds == 0) & (y_true_arr == 1)).sum()
            p = tp / (tp + fp) if (tp + fp) > 0 else 0
            r = tp / (tp + fn) if (tp + fn) > 0 else 0
            f1 = 2 * p * r / (p + r) if (p + r) > 0 else 0
            best_f1 = max(best_f1, f1)

        algo, lib = key.rsplit('_', 1)
        results.append({
            "Algorithm": algo, "Library": "imagehash" if lib == "ih" else "libphash",
            "PR-AUC": round(auc(recall, precision), 4),
            "Best F1": round(best_f1, 4)
        })

    print("\n" + tabulate(pd.DataFrame(results).sort_values(["Algorithm", "Library"]), 
                          headers='keys', tablefmt='pipe', showindex=False))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run quality benchmarks.")
    parser.add_argument("--format", choices=["jpeg", "png"], default="jpeg")
    parser.add_argument("--limit", type=int, default=50, help="Base images limit")
    args = parser.parse_args()
    
    base_dir = f"benchmarks/data/{args.format}"
    ext = "jpg" if args.format == "jpeg" else "png"
    base_files = get_base_files(base_dir, ext)[:args.limit]
    
    if not base_files:
        print(f"No base images in {base_dir}. Run generate_data.py first.")
    else:
        files, gt = prepare_quality_dataset(base_files, base_dir, "JPEG" if args.format == "jpeg" else "PNG")
        evaluate_quality(files, gt)
