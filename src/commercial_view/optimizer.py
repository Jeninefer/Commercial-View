"""Portfolio optimization module."""

from typing import Dict, Optional
import numpy as np
import pandas as pd


class PortfolioOptimizer:
    """Portfolio optimizer with hard limit constraints."""
    
    def __init__(self, rules: Dict, weights: Dict):
        """
        Initialize the optimizer.
        
        Args:
            rules: Dictionary containing hard_limits and other rules
            weights: Dictionary containing scoring weights for apr, term_fit, and origination_count
        """
        self.rules = rules
        self.weights = weights
    
    def _bucket_apr(self, apr: float) -> str:
        """Bucket APR values into ranges."""
        if apr < 5.0:
            return "0-5"
        elif apr < 7.0:
            return "5-7"
        elif apr < 10.0:
            return "7-10"
        else:
            return "10+"
    
    def _bucket_line(self, amount: float) -> str:
        """Bucket line amounts into ranges."""
        if amount < 100000:
            return "0-100k"
        elif amount < 500000:
            return "100k-500k"
        elif amount < 1000000:
            return "500k-1M"
        else:
            return "1M+"
    
    def _payer_bucket(self, rank: int) -> str:
        """Bucket payer ranks."""
        if rank <= 1:
            return "top"
        elif rank <= 3:
            return "mid"
        else:
            return "low"
    
    # ------------- core -------------
    def optimize(self, candidates_df: pd.DataFrame, aum_total: float, target_term: Optional[int] = None) -> pd.DataFrame:
        df = candidates_df.copy()
        if df.empty:
            return df

        # Prepare buckets
        df["apr_bucket"] = df["apr"].astype(float).apply(self._bucket_apr)
        df["line_bucket"] = df["amount"].astype(float).apply(self._bucket_line)
        df["payer_bucket"] = df["payer_rank"].astype(int).apply(self._payer_bucket)

        # Scoring
        w_apr = float(self.weights.get("apr", 0.6))
        w_term = float(self.weights.get("term_fit", 0.35))
        w_cnt = float(self.weights.get("origination_count", 0.05))

        apr_norm = (df["apr"] - df["apr"].min()) / (df["apr"].max() - df["apr"].min() + 1e-9)
        if target_term is not None and "term" in df.columns:
            term_fit = 1.0 - (df["term"].astype(float) - target_term).abs() / (target_term + 1e-9)
            term_fit = term_fit.clip(0.0, 1.0)
        else:
            term_fit = pd.Series(0.5, index=df.index)

        # Favor smaller tickets slightly (to improve mix controllability)
        cnt_bonus = 1.0 - (df["amount"].astype(float) / (df["amount"].astype(float).max() + 1e-9))

        df["score"] = w_apr * apr_norm + w_term * term_fit + w_cnt * cnt_bonus

        # Sort by score desc, then by higher APR (within same score)
        df = df.sort_values(["score", "apr"], ascending=[False, False]).reset_index(drop=True)

        # Running mix trackers
        pick_mask = np.zeros(len(df), dtype=bool)
        cum_amt = 0.0

        def share(series: pd.Series) -> Dict[str, float]:
            tot = series.sum()
            return {} if tot <= 0 else (series / tot).to_dict()

        # Greedy selection with hard-limit checks
        for idx, row in df.iterrows():
            amt = float(row["amount"])
            if cum_amt + amt > aum_total + 1e-6:
                continue

            # Provisional selection
            next_cum_amt = cum_amt + amt
            next_mask = pick_mask.copy()
            next_mask[idx] = True
            cur = df.loc[next_mask]

            # Hard limit checks
            # APR caps
            apr_shares = share(cur["amount"].groupby(cur["apr_bucket"]).sum())
            for bucket, rule in self.rules.get("hard_limits", {}).get("apr", {}).items():
                max_pct = float(rule.get("max_pct", 1.0))
                if apr_shares.get(bucket, 0.0) > max_pct + 1e-9:
                    break
            else:
                # Payer caps (anchor <= 4%)
                anchor_cap = float(self.rules.get("hard_limits", {}).get("payer", {}).get("any_anchor", {}).get("max_pct", 1.0))
                cust_share = cur["amount"].groupby(cur["customer_id"]).sum() / next_cum_amt
                if (cust_share > anchor_cap + 1e-9).any():
                    continue

                # Industry caps (any sector <= 35%)
                ind_cap = float(self.rules.get("hard_limits", {}).get("industry", {}).get("any_sector", {}).get("max_pct", 1.0))
                ind_share = cur["amount"].groupby(cur["industry"]).sum() / next_cum_amt
                if (ind_share > ind_cap + 1e-9).any():
                    continue

                # All hard limits passed → accept
                pick_mask = next_mask
                cum_amt = next_cum_amt

            if cum_amt >= aum_total - 1e-6:
                break

        selected = df.loc[pick_mask].copy()
        selected["selected"] = True
        selected["selected_amount_cum"] = selected["amount"].cumsum()
        return selected
