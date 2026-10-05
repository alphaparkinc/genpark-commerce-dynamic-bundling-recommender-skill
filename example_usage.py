"""Example usage for CommerceDynamicBundlingRecommender."""
import sys
import json
from client import CommerceDynamicBundlingRecommender

sys.stdout.reconfigure(encoding='utf-8')

def main():
    print("=== Commerce Dynamic Bundling & Cross-Sell Recommender Demo ===")
    recommender = CommerceDynamicBundlingRecommender()

    current_cart = [
        {"sku": "SONY-XM5", "name": "Sony Noise-Cancelling Headphones", "price": 329.99, "category": "electronics"}
    ]

    candidate_catalog = [
        {"sku": "CASE-EVA", "name": "Hard Shell Travel Case", "price": 29.99, "cost": 10.0, "category": "accessories"},
        {"sku": "CABLE-AUX", "name": "Gold-Plated Audio Cable", "price": 14.99, "cost": 4.50, "category": "accessories"},
        {"sku": "PROTEIN-WHEY", "name": "Whey Protein 2lb", "price": 45.0, "cost": 22.0, "category": "nutrition"}
    ]

    print("\n--- Generating High-Affinity Cart Add-On Bundles (Meta Muse Shopping) ---")
    results = recommender.recommend_dynamic_bundles(current_cart, candidate_catalog, max_bundles=2)
    print(f"Cart Subtotal: ${results['cart_subtotal_usd']}")
    for b in results["bundles"]:
        print(f"\n[{b['bundle_id']}] {b['headline']}")
        print(f"  Standalone: ${b['standalone_total_usd']} -> Bundle: ${b['bundle_price_usd']} (Save ${b['instant_savings_usd']})")

if __name__ == "__main__":
    main()
