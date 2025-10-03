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

    # Default APR bucket edges and labels
    DEFAULT_APR_BUCKET_EDGES = [(15,20),(20,25),(25,30),(30,35),(35,40),(40,45),(45,50),(50,60),(60,70)]
    DEFAULT_APR_BELOW_LABEL = "<15"
    DEFAULT_APR_ABOVE_LABEL = ">70"

    def __init__(self, config: Optional[Config] = None):
        self.cfg = config or Config()
        self.rules = self.cfg.optimizer
        self.weights = self.rules.get("priority_weights", {"apr": 0.6, "term_fit": 0.35, "origination_count": 0.05})
        # Load APR bucket edges and labels from config if available, else use defaults
        apr_bucket_cfg = self.rules.get("apr_bucket_edges", None)
        if apr_bucket_cfg is not None:
            # Expecting a dict with 'edges', 'below_label', 'above_label'
            self.apr_bucket_edges = apr_bucket_cfg.get("edges", self.DEFAULT_APR_BUCKET_EDGES)
            self.apr_below_label = apr_bucket_cfg.get("below_label", self.DEFAULT_APR_BELOW_LABEL)
            self.apr_above_label = apr_bucket_cfg.get("above_label", self.DEFAULT_APR_ABOVE_LABEL)
        else:
            self.apr_bucket_edges = self.DEFAULT_APR_BUCKET_EDGES
            self.apr_below_label = self.DEFAULT_APR_BELOW_LABEL
            self.apr_above_label = self.DEFAULT_APR_ABOVE_LABEL

    # ------------- helpers -------------
    def _bucket_apr(self, apr: float) -> str:
        if pd.isna(apr):
            return "Unknown"
        for lo, hi in self.apr_bucket_edges:
            if lo <= apr < hi:
                return f"{lo}-{hi}"
        if apr >= self.apr_bucket_edges[-1][1]:
            return self.apr_above_label
        return self.apr_below_label

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
