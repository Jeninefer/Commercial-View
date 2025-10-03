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
      - optimizer_constraints.hard_limits (caps)
      - optimizer_constraints.priority_weights (apr/term_fit/origination_count)
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
            edges = apr_bucket_cfg.get("edges", self.DEFAULT_APR_BUCKET_EDGES)
            if not all(isinstance(t, (list, tuple)) and len(t) == 2 and t[0] < t[1] for t in edges):
                raise ValueError(f"apr_bucket_edges.edges must be a list of [lo, hi] with lo < hi; got: {edges!r}")
            self.apr_bucket_edges = edges
            self.apr_below_label = apr_bucket_cfg.get("below_label", self.DEFAULT_APR_BELOW_LABEL)
            self.apr_above_label = apr_bucket_cfg.get("above_label", self.DEFAULT_APR_ABOVE_LABEL)
        else:
            self.apr_bucket_edges = self.DEFAULT_APR_BUCKET_EDGES
            self.apr_below_label = self.DEFAULT_APR_BELOW_LABEL
            self.apr_above_label = self.DEFAULT_APR_ABOVE_LABEL

    # ------------- helpers -------------
    @staticmethod
    def _bucket_apr(
        apr: float,
        edges=None,
        below_label=None,
        above_label=None
    ) -> str:
        """
        Static APR bucketing helper. Accepts optional edges/labels, defaults to class constants.
        """
        if pd.isna(apr):
            return "Unknown"
        # Use defaults if not provided
        if edges is None:
            edges = DisbursementOptimizer.DEFAULT_APR_BUCKET_EDGES
        if below_label is None:
            below_label = DisbursementOptimizer.DEFAULT_APR_BELOW_LABEL
        if above_label is None:
            above_label = DisbursementOptimizer.DEFAULT_APR_ABOVE_LABEL
        for lo, hi in edges:
            if lo <= apr < hi:
                return f"{lo}-{hi}"
        if apr >= edges[-1][1]:
            return above_label
        return below_label

    def bucket_apr(self, apr: float) -> str:
        """
        Instance wrapper for APR bucketing using configured edges/labels.
        """
        return self._bucket_apr(
            apr,
            edges=self.apr_bucket_edges,
            below_label=self.apr_below_label,
            above_label=self.apr_above_label,
        )
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
        """
        Bucket payer ranks into 'Top1', 'Top10', or 'Rest'.

        Args:
            rank (int): Payer rank (expected: positive integer, 1 = best).

        Returns:
            str: 'Top1' for rank 1 (inclusive), 'Top10' for ranks 2-10 (inclusive), 'Rest' for rank > 10.
        """
        if rank == 1: return "Top1"
        if rank <= 10: return "Top10"
        return "Rest"
