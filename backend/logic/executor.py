import pandas as pd
import numpy as np
from backend.logic.policy_loader import policy_loader
from backend.logic.logger import agent_logger

class Executor:
    """
    Applies qualitative LLM decisions to the current state and computes
    the next week's state using deterministic, constraint-aware logic.
    """

    def __init__(self, adobe_client=None, execute_to_adobe=False):
        """
        Initialize executor with optional Adobe client.

        Args:
            adobe_client: AdobeAEPClient or MockAdobeClient instance
            execute_to_adobe: If True, execute actions to Adobe APIs (write mode)
                             If False, only simulate/log actions (read-only mode)
        """
        # Policy values are loaded dynamically via policy_loader
        self.adobe_client = adobe_client
        self.execute_to_adobe = execute_to_adobe

        if self.execute_to_adobe and not self.adobe_client:
            raise ValueError("Adobe client required when execute_to_adobe=True")

    def _deterministic_budget_reallocation(self, campaigns_df):
        """
        Implements deterministic budget reallocation based on ROAS ranking.
        Top 50% of campaigns get a budget increase; bottom 50% get a decrease.
        """
        campaigns_df = campaigns_df.set_index('campaign_id')
        
        # 1. Load policy values
        increase_factor = policy_loader.get_value('budget', 'increase_factor', default=0.15)
        decrease_factor = policy_loader.get_value('budget', 'decrease_factor', default=0.15)
        min_budget = policy_loader.get_value('budget', 'min_budget', default=100.0)
        max_cap_factor = policy_loader.get_value('budget', 'max_increase_cap_factor', default=1.30)
        
        # 2. Rank campaigns by ROAS
        # Campaigns with NaN ROAS are treated as low-performing (pushed to the bottom)
        ranked_campaigns = campaigns_df.sort_values(by='roas', ascending=False, na_position='last')
        
        # 3. Determine split point (top 50% vs bottom 50%)
        split_point = len(ranked_campaigns) // 2
        
        # 4. Apply actions
        for i, (campaign_id, row) in enumerate(ranked_campaigns.iterrows()):
            current_budget = row['weekly_budget_allocated']
            action_type = ""
            new_budget = current_budget

            if i < split_point:
                # Top 50%: Increase Budget
                action_type = "increase_budget"
                new_budget = current_budget * (1 + increase_factor)
                # Constraint: Cap increase
                max_budget = current_budget * max_cap_factor
                new_budget = min(new_budget, max_budget)
            else:
                # Bottom 50%: Decrease Budget
                action_type = "decrease_budget"
                new_budget = current_budget * (1 - decrease_factor)
                # Constraint: Minimum budget
                new_budget = max(new_budget, min_budget)
            
            # 5. Apply and Log
            if new_budget != current_budget:
                campaigns_df.loc[campaign_id, 'weekly_budget_allocated'] = new_budget
                agent_logger.log_numeric_change(campaign_id, 'weekly_budget_allocated', current_budget, new_budget)
                agent_logger.log_action(action_type, campaign_id, {"old_budget": current_budget, "new_budget": new_budget})
                
        return campaigns_df.reset_index()

    def _apply_ad_group_bid_actions(self, ad_groups_df, decisions):
        """Applies bid increase/decrease actions to ad groups."""
        ad_groups_df = ad_groups_df.set_index('ad_group_id')
        
        # Load policy values
        increase_factor = policy_loader.get_value('bid', 'increase_factor', default=0.10)
        decrease_factor = policy_loader.get_value('bid', 'decrease_factor', default=0.10)
        min_cpc = policy_loader.get_value('bid', 'min_cpc', default=0.5)
        
        for action in decisions.get("ad_group_bid_actions", []):
            ad_group_id = action["ad_group_id"]
            action_type = action["type"]
            
            if ad_group_id in ad_groups_df.index:
                current_bid = ad_groups_df.loc[ad_group_id, 'avg_bid']
                new_bid = current_bid
                
                if action_type == "raise_bid":
                    new_bid = current_bid * (1 + increase_factor)
                
                elif action_type == "lower_bid":
                    new_bid = current_bid * (1 - decrease_factor)
                    # Constraint: Enforce minimum bid
                    new_bid = max(new_bid, min_cpc)
                
                if new_bid != current_bid:
                    ad_groups_df.loc[ad_group_id, 'avg_bid'] = new_bid
                    agent_logger.log_numeric_change(ad_group_id, 'avg_bid', current_bid, new_bid)
                    agent_logger.log_action(action_type, ad_group_id, {"old_bid": current_bid, "new_bid": new_bid})
                    
        return ad_groups_df.reset_index()

    def _apply_audience_suppression(self, audiences_df, decisions):
        """Applies audience suppression/activation actions."""
        
        for action in decisions.get("audience_targeting_actions", []):
            audience_id = action["audience_id"]
            action_type = action["type"]
            
            if action_type == "suppress":
                # For simplicity, we'll just mark the audience for suppression
                if audience_id in audiences_df['audience_id'].values:
                    # In a real system, this would update a suppression flag in the DB
                    # Here, we log the action and assume the prompt builder uses this logic
                    agent_logger.log_action(action_type, audience_id)
            
        # The executor does not modify the audience dataframe for suppression in this version,
        # as the logic is handled by the prompt builder/LLM based on the state.
        # We only log the action for traceability.
        return audiences_df

    def _prepare_optimized_data(self, df):
        """
        Prepares the optimized data for the current week by resetting
        performance metrics. This is a simulation step for the *next* iteration.
        The 'week' column is NOT changed, as we are overwriting the current week's data.
        """
        optimized_df = df.copy()
        
        # Reset performance metrics for the new week (simulation)
        # In a real system, these would be populated by the ad platform
        for col in ['weekly_budget_spent', 'weekly_impressions', 'weekly_clicks',
                    'weekly_conversions', 'weekly_conversion_value', 'roas',
                    'impressions', 'clicks', 'conversions', 'conversion_value',
                    'ctr', 'cvr']:
            if col in optimized_df.columns:
                optimized_df[col] = 0
                
        # For ad_groups, we need to handle the budget allocation based on suppression
        if 'ad_group_id' in optimized_df.columns:
            # Simple simulation: if ad_group's audience is suppressed, set budget to 0
            # This requires joining with the audience data, but for now, we'll assume
            # the ad_group budget is set by the campaign budget allocation logic
            # and the suppression logic will be handled by the prompt builder/LLM
            # For now, we'll just ensure the budget is carried over.
            pass

        return optimized_df

    def _rebalance_campaign_budgets(self, campaigns_df, initial_total_budget):
        """
        Enforces budget neutrality by scaling all campaign budgets to match the initial total.
        This ensures that budget increases are funded by budget decreases.
        """
        current_total_budget = campaigns_df['weekly_budget_allocated'].sum()
        
        # Calculate the scaling factor
        if current_total_budget == 0:
            # Avoid division by zero, but this should not happen in a real scenario
            return campaigns_df
            
        scaling_factor = initial_total_budget / current_total_budget
        
        # Apply the scaling factor to all budgets
        campaigns_df['weekly_budget_allocated'] = campaigns_df['weekly_budget_allocated'] * scaling_factor
        
        # Log the rebalancing action
        agent_logger.log_action("budget_rebalance", "SYSTEM", {
            "initial_total": initial_total_budget,
            "current_total": current_total_budget,
            "scaling_factor": scaling_factor
        })
        
        return campaigns_df

    def execute_decisions(self, data, decisions):
        """
        Main execution function.
        1. Applies decisions to the latest week's data.
        2. Enforces budget neutrality.
        3. Prepares the optimized data for the current week (overwriting).
        4. Returns the modified rows to replace the latest week in the original CSVs.
        """
        
        # 1. Get the current week and start logging step
        current_week = data["campaigns"]["week"].iloc[0] # Assumes single-week dataframes
        agent_logger.start_step(current_week)
        
        # Dataframes are already filtered to the current week (this is the data we will modify)
        campaigns_df = data["campaigns"].copy()
        ad_groups_df = data["ad_groups"].copy()
        audiences_df = data["audiences"].copy()

        # Store the initial total budget for rebalancing
        initial_total_budget = campaigns_df['weekly_budget_allocated'].sum()

        # 2. Apply decisions to the latest week's data (updates budgets/bids/suppression flags)
        # Budget Reallocation is now deterministic and replaces the LLM's qualitative budget decisions
        campaigns_df = self._deterministic_budget_reallocation(campaigns_df)
        ad_groups_df = self._apply_ad_group_bid_actions(ad_groups_df, decisions)
        audiences_df = self._apply_audience_suppression(audiences_df, decisions)
        
        # 3. Budget Re-balancing (Crucial Step: Enforce budget neutrality)
        campaigns_df = self._rebalance_campaign_budgets(campaigns_df, initial_total_budget)
        
        # 4. Prepare the optimized data for the current week (resets performance metrics)
        optimized_campaigns_df = self._prepare_optimized_data(campaigns_df)
        optimized_ad_groups_df = self._prepare_optimized_data(ad_groups_df)
        
        # Drop the temporary 'is_suppressed' column before returning
        # NOTE: This column is no longer added by _apply_audience_suppression, but kept for safety
        if 'is_suppressed' in audiences_df.columns:
            audiences_df = audiences_df.drop(columns=['is_suppressed'])
            
        optimized_audiences_df = self._prepare_optimized_data(audiences_df)
        
        # 5. Log final performance metrics (simulated) and end step
        # For this version, we log the new budgets/bids as the key change
        agent_logger.log_final_performance({
            "campaigns_modified": optimized_campaigns_df[['campaign_id', 'weekly_budget_allocated']].to_dict(orient='records'),
            "ad_groups_modified": optimized_ad_groups_df[['ad_group_id', 'avg_bid']].to_dict(orient='records')
        })
        agent_logger.end_step()
        
        # 6. Return the modified rows to replace the latest week
        return {
            "campaigns": optimized_campaigns_df,
            "ad_groups": optimized_ad_groups_df,
            "audiences": optimized_audiences_df,
            "latest_week": current_week # Use current_week
        }