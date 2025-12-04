import pandas as pd
import numpy as np

class Executor:
    """
    Applies qualitative LLM decisions to the current state and computes 
    the next week's state using deterministic, constraint-aware logic.
    """

    def __init__(self, budget_increase_factor=0.15, bid_reduction_factor=0.10):
        self.BUDGET_INCREASE_FACTOR = budget_increase_factor
        self.BID_REDUCTION_FACTOR = bid_reduction_factor
        self.MIN_CPC = 0.5 # Example constraint

    def _apply_campaign_budget_actions(self, campaigns_df, decisions):
        """Applies budget increase/decrease actions to campaigns."""
        campaigns_df = campaigns_df.set_index('campaign_id')
        
        for action in decisions.get("campaign_budget_actions", []):
            campaign_id = action["campaign_id"]
            action_type = action["type"]
            
            if campaign_id in campaigns_df.index:
                current_budget = campaigns_df.loc[campaign_id, 'weekly_budget_allocated']
                
                if action_type == "increase_budget":
                    new_budget = current_budget * (1 + self.BUDGET_INCREASE_FACTOR)
                    # Constraint: Cap increase at 30% for now (as per prompt builder's old constraint)
                    max_budget = current_budget * 1.30
                    campaigns_df.loc[campaign_id, 'weekly_budget_allocated'] = min(new_budget, max_budget)
                
                elif action_type == "decrease_budget":
                    new_budget = current_budget * (1 - self.BUDGET_INCREASE_FACTOR)
                    # Constraint: Minimum budget is 100
                    campaigns_df.loc[campaign_id, 'weekly_budget_allocated'] = max(new_budget, 100)
                    
        return campaigns_df.reset_index()

    def _apply_ad_group_bid_actions(self, ad_groups_df, decisions):
        """Applies bid increase/decrease actions to ad groups."""
        ad_groups_df = ad_groups_df.set_index('ad_group_id')
        
        for action in decisions.get("ad_group_bid_actions", []):
            ad_group_id = action["ad_group_id"]
            action_type = action["type"]
            
            if ad_group_id in ad_groups_df.index:
                current_bid = ad_groups_df.loc[ad_group_id, 'avg_bid']
                
                if action_type == "raise_bid":
                    new_bid = current_bid * (1 + self.BID_REDUCTION_FACTOR)
                    ad_groups_df.loc[ad_group_id, 'avg_bid'] = new_bid
                
                elif action_type == "lower_bid":
                    new_bid = current_bid * (1 - self.BID_REDUCTION_FACTOR)
                    # Constraint: Enforce minimum bid
                    ad_groups_df.loc[ad_group_id, 'avg_bid'] = max(new_bid, self.MIN_CPC)
                    
        return ad_groups_df.reset_index()

    def _apply_audience_suppression(self, audiences_df, decisions):
        """Applies audience suppression/activation actions."""
        # For simplicity, we'll just mark the audience for suppression
        suppressed_audiences = {
            action["audience_id"] 
            for action in decisions.get("audience_targeting_actions", []) 
            if action["type"] == "suppress"
        }
        
        audiences_df['is_suppressed'] = audiences_df['audience_id'].apply(
            lambda x: 1 if x in suppressed_audiences else 0
        )
        return audiences_df

    def _generate_next_week_data(self, df, next_week):
        """
        Generates the next week's row by copying the current row and resetting
        performance metrics. This is a simulation step.
        """
        next_df = df.copy()
        next_df['week'] = next_week
        
        # Reset performance metrics for the new week (simulation)
        # In a real system, these would be populated by the ad platform
        for col in ['weekly_budget_spent', 'weekly_impressions', 'weekly_clicks', 
                    'weekly_conversions', 'weekly_conversion_value', 'roas',
                    'impressions', 'clicks', 'conversions', 'conversion_value', 
                    'ctr', 'cvr']:
            if col in next_df.columns:
                next_df[col] = 0
                
        # For ad_groups, we need to handle the budget allocation based on suppression
        if 'ad_group_id' in next_df.columns:
            # Simple simulation: if ad_group's audience is suppressed, set budget to 0
            # This requires joining with the audience data, but for now, we'll assume
            # the ad_group budget is set by the campaign budget allocation logic
            # and the suppression logic will be handled by the prompt builder/LLM
            # For now, we'll just ensure the budget is carried over.
            pass

        return next_df

    def execute_decisions(self, data, decisions):
        """
        Main execution function.
        1. Applies decisions to the latest week's data.
        2. Generates the next week's data rows.
        3. Returns the new rows to be appended to the original CSVs.
        """
        
        # 1. Get latest week's data
        latest_week = data["campaigns"]["week"].max()
        next_week = latest_week + 1
        
        campaigns_df = data["campaigns"][data["campaigns"]["week"] == latest_week].copy()
        ad_groups_df = data["ad_groups"][data["ad_groups"]["week"] == latest_week].copy()
        audiences_df = data["audiences"][data["audiences"]["week"] == latest_week].copy()

        # 2. Apply decisions to the latest week's data (updates budgets/bids/suppression flags)
        campaigns_df = self._apply_campaign_budget_actions(campaigns_df, decisions)
        ad_groups_df = self._apply_ad_group_bid_actions(ad_groups_df, decisions)
        audiences_df = self._apply_audience_suppression(audiences_df, decisions)
        
        # 3. Generate next week's rows
        next_campaigns_df = self._generate_next_week_data(campaigns_df, next_week)
        next_ad_groups_df = self._generate_next_week_data(ad_groups_df, next_week)
        
        # Drop the temporary 'is_suppressed' column before appending to CSV
        if 'is_suppressed' in audiences_df.columns:
            audiences_df = audiences_df.drop(columns=['is_suppressed'])
            
        next_audiences_df = self._generate_next_week_data(audiences_df, next_week)
        
        # 4. Budget Re-balancing (Crucial Step: Ensure total campaign budget is balanced)
        # This is a placeholder for a more complex re-balancing logic.
        # For now, we'll assume the LLM's actions are relative to the current total.
        # A more robust system would re-distribute the total budget across all campaigns.
        
        # 5. Return the new rows
        return {
            "campaigns": next_campaigns_df,
            "ad_groups": next_ad_groups_df,
            "audiences": next_audiences_df,
            "next_week": next_week
        }