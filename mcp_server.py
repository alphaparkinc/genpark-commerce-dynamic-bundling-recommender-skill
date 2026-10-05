"""MCP Server for Commerce Dynamic Bundling Recommender."""
import sys
import json
import time
from client import CommerceDynamicBundlingRecommender

recommender = CommerceDynamicBundlingRecommender()

def handle_call_tool(params):
    name = params.get("name")
    args = params.get("arguments", {})
    if name != "recommend_commerce_bundles":
        raise ValueError(f"Unknown tool: {name}")

    action = args.get("action", "recommend_dynamic_bundles")
    if action == "recommend_dynamic_bundles":
        return recommender.recommend_dynamic_bundles(
            cart_items=args.get("cart_items", []),
            catalog_candidates=args.get("catalog_candidates", []),
            max_bundles=int(args.get("max_bundles", 3))
        )
    else:
        raise ValueError(f"Invalid action: {action}")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("Running self-test...")
        cart = [{"sku": "CAM-01", "name": "Insta360 Action Cam", "price": 399.99, "category": "electronics"}]
        catalog = [
            {"sku": "BAT-02", "name": "Dual Spare Battery Pack", "price": 49.99, "cost": 20.0, "category": "accessories"},
            {"sku": "SHOE-09", "name": "Running Shoes", "price": 120.0, "cost": 60.0, "category": "footwear"}
        ]
        res = recommender.recommend_dynamic_bundles(cart, catalog, max_bundles=2)
        assert res["total_bundles_generated"] >= 1
        assert res["bundles"][0]["recommended_item"]["sku"] == "BAT-02"
        print("Self-test PASSED!")
        sys.exit(0)

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            msg_id = req.get("id")
            method = req.get("method")
            if method == "initialize":
                resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "serverInfo": {"name": "CommerceDynamicBundlingRecommender", "version": "1.0.0"},
                        "capabilities": {"tools": {}}
                    }
                }
            elif method == "tools/list":
                resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "tools": [{
                            "name": "recommend_commerce_bundles",
                            "description": "Dynamic product bundling: analyze shopping cart items, identify high-affinity cross-sell products, apply margin-safe discounts, and synthesize compelling bundle proposals.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "action": {"type": "string", "enum": ["recommend_dynamic_bundles"]},
                                    "cart_items": {"type": "array"},
                                    "catalog_candidates": {"type": "array"},
                                    "max_bundles": {"type": "integer"}
                                },
                                "required": ["action"]
                            }
                        }]
                    }
                }
            elif method == "tools/call":
                res = handle_call_tool(req.get("params", {}))
                resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}
                }
            else:
                resp = {"jsonrpc": "2.0", "id": msg_id, "result": {}}
            print(json.dumps(resp), flush=True)
        except Exception as e:
            err_resp = {"jsonrpc": "2.0", "id": None, "error": {"code": -32000, "message": str(e)}}
            print(json.dumps(err_resp), flush=True)

if __name__ == "__main__":
    main()
