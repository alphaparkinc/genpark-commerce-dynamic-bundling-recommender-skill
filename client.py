"""
Autonomous Commerce Dynamic Bundling & Cross-Sell Recommender (Zero External Dependencies)
Calculates cross-category product affinity, guarantees merchant profitability margins, and outputs bundles.
"""
import time
import math
import hashlib
import json
from typing import Dict, Any, List, Optional

CATEGORY_AFFINITY_WEIGHTS = {
    ("electronics", "accessories"): 0.85,
    ("travel", "luggage"): 0.90,
    ("groceries", "beverages"): 0.75,
    ("fitness", "nutrition"): 0.80,
    ("apparel", "footwear"): 0.70
}

class CommerceDynamicBundlingRecommender:
    def __init__(self, min_merchant_margin_pct: float = 0.15):
        self.min_margin = min_merchant_margin_pct

    def _get_category_affinity(self, cat_a: str, cat_b: str) -> float:
        cat_a = cat_a.lower()
        cat_b = cat_b.lower()
        if (cat_a, cat_b) in CATEGORY_AFFINITY_WEIGHTS:
            return CATEGORY_AFFINITY_WEIGHTS[(cat_a, cat_b)]
        if (cat_b, cat_a) in CATEGORY_AFFINITY_WEIGHTS:
            return CATEGORY_AFFINITY_WEIGHTS[(cat_b, cat_a)]
        return 0.35 if cat_a == cat_b else 0.15

    def recommend_dynamic_bundles(
        self,
        cart_items: List[Dict[str, Any]],
        catalog_candidates: List[Dict[str, Any]],
        max_bundles: int = 3
    ) -> Dict[str, Any]:
        """
        Synthesizes personalized bundles by matching cart items with complementary catalog candidates.
        Applies a margin-safe bundle discount (e.g. 10-15% off) while maintaining profitability.
        """
        if not cart_items or not catalog_candidates:
            return {"bundles": [], "total_options": 0}

        cart_subtotal = sum(float(i.get("price", 0.0)) for i in cart_items)
        cart_categories = [i.get("category", "general") for i in cart_items]
        cart_skus = {i.get("sku") for i in cart_items}

        candidates_scored = []
        for cand in catalog_candidates:
            sku = cand.get("sku")
            if sku in cart_skus:
                continue

            price = float(cand.get("price", 0.0))
            cost = float(cand.get("cost", price * 0.60)) # Estimated cost if not provided
            cand_cat = cand.get("category", "general")

            # Affinity score
            max_aff = max(self._get_category_affinity(cc, cand_cat) for cc in cart_categories)

            # Profitability margin
            margin_dollars = price - cost
            margin_ratio = margin_dollars / max(1.0, price)

            if margin_ratio < self.min_margin:
                continue # Skip unprofitable candidates

            composite_fitness = 0.65 * max_aff + 0.35 * margin_ratio
            candidates_scored.append({"item": cand, "score": composite_fitness, "margin_ratio": margin_ratio})

        candidates_scored.sort(key=lambda x: x["score"], reverse=True)
        top_candidates = candidates_scored[:max_bundles]

        bundles = []
        for rank, c_entry in enumerate(top_candidates):
            addon = c_entry["item"]
            addon_price = float(addon.get("price", 0.0))
            addon_cost = float(addon.get("cost", addon_price * 0.60))

            standalone_total = cart_subtotal + addon_price
            # Safe discount: 12% off add-on item
            discount_amount = round(addon_price * 0.12, 2)
            bundle_price = round(standalone_total - discount_amount, 2)

            savings_pct = round((discount_amount / standalone_total) * 100.0, 1)

            bundles.append({
                "bundle_id": f"BNDL-OPT-{rank+1}",
                "headline": f"Bundle & Save: Add {addon.get('name')} for just ${round(addon_price - discount_amount, 2)}",
                "recommended_item": addon,
                "standalone_total_usd": round(standalone_total, 2),
                "bundle_price_usd": bundle_price,
                "instant_savings_usd": discount_amount,
                "savings_pct": savings_pct,
                "affinity_score": round(c_entry["score"], 3)
            })

        return {
            "cart_items_count": len(cart_items),
            "cart_subtotal_usd": round(cart_subtotal, 2),
            "total_bundles_generated": len(bundles),
            "bundles": bundles
        }
