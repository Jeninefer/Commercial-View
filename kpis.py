from dataclasses import dataclass

@dataclass
class StartupSnapshot:
    mrr: float
    total_customers: int
    pre_money: float | None = None
    post_money: float | None = None

def compute_arr(mrr: float) -> float:
    return float(mrr) * 12.0

def compute_post_money(pre_money: float, new_money: float) -> float:
    return float(pre_money) + float(new_money)

def update_snapshot(snap: dict, new_money: float | None = None) -> dict:
    mrr = snap["startup"]["mrr"]
    snap["startup"]["arr"] = compute_arr(mrr)
    if new_money is not None and snap["valuation"]["pre_money"] is not None:
        snap["valuation"]["post_money"] = compute_post_money(
            snap["valuation"]["pre_money"], new_money
        )
    return snap
