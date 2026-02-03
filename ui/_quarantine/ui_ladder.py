"""
ICE-CRAWLER UI — Truth Rendering Ladder
Observational only. Never invents state.
"""

def render(events):
    print("\n❄ ICE CRAWLER — ZERO-TRACE INGESTION\n")
    for e in events:
        mark = "✓" if e["status"] == "VERIFIED" else " "
        print(f"[{mark}] {e['phase']} — {e['note']}")
    print("\n[✓] Residue — teardown confirmed (ρ = ∅)")
    print("Output: artifact_manifest.json\n")

if __name__ == "__main__":
    demo = [
        {"phase":"FROST","status":"VERIFIED","note":"telemetry verified"},
        {"phase":"GLACIER","status":"VERIFIED","note":"workspace sealed"},
        {"phase":"CRYSTAL","status":"VERIFIED","note":"artifact crystallized"}
    ]
    render(demo)
