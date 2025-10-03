from __future__ import annotations
from typing import Optional
import pandas as pd

from .config import Config
class DisbursementOptimizer:
    """
    Greedy, explainable portfolio optimizer to approximate target mix under hard limits.

    Inputs:
      - candidates_df: rows = disbursement requests with at least:
          ['loan_id','customer_id','amount','apr','term','industry','payer_rank']
      - aum_total: total target origination amount for the day
    Manifest (abaco_manifest.json):
      - optimizer_constraints.target_mix (apr/line/industry/payer)
      - hard_limits (caps)
      - priority_weights (apr/term_fit/origination_count)
    """

    def __init__(self, config: Optional[Config] = None):
        self.cfg = config or Config()
        self.rules = self.cfg.optimizer
        self.weights = self.rules.get("priority_weights", {"apr": 0.6, "term_fit": 0.35, "origination_count": 0.05})

    # ------------- helpers -------------
    @staticmethod
    def _bucket_apr(apr: float) -> str:
        if pd.isna(apr):
            return "Unknown"
        edges = [(15,20),(20,25),(25,30),(30,35),(35,40),(40,45),(45,50),(50,60),(60,70)]
        for lo, hi in edges:
            if lo <= apr < hi:
                return f"{lo}-{hi}"
        return ">70" if apr >= 70 else "<15"

    @staticmethod
    def _bucket_line(amount: float) -> str:
        if amount <= 3000: return "<=3k"
        if amount <= 10000: return "<=10k"
        if amount <= 50000: return "<=50k"
        if amount <= 100000: return "<=100k"
        if amount <= 150000: return "<=150k"
        if amount <= 200000: return "<=200k"
        if amount <= 250000: return "<=250k"
        return ">250k"

    @staticmethod
    def _payer_bucket(rank: int) -> str:
        if rank <= 1: return "Top1"
        if rank <= 10: return "Top10"
        return "Rest"
