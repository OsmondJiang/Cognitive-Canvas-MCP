import statistics
import math
from typing import Dict, List, Optional, Any, Union
from .display_recommendations import DisplayRecommendations

class StatisticalAnalyzer:
    """
    Statistical Analyzer Tool for automated statistical analysis and data exploration.
    Provides intelligent statistical method selection and comprehensive data analysis.
    """
    
    def __init__(self):
        # conversation_id -> workspaces -> workspace_id -> data
        self.conversations = {}
    
    def _ensure_conv(self, conversation_id: str):
        """Ensure conversation exists in storage"""
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = {"workspaces": {}}

    def _ensure_workspace(self, conversation_id: str, workspace_id: str):
        """Ensure workspace exists (auto-create if needed)"""
        self._ensure_conv(conversation_id)
        if workspace_id not in self.conversations[conversation_id]["workspaces"]:
            self.conversations[conversation_id]["workspaces"][workspace_id] = {
                "analyses": [],
                "data_history": []
            }
    
    def _percentile(self, values: List[float], percentile: float) -> float:
        """Calculate percentile using linear interpolation"""
        sorted_values = sorted(values)
        n = len(sorted_values)
        k = (n - 1) * percentile / 100
        floor_k = int(k)
        ceiling_k = floor_k + 1
        
        if ceiling_k >= n:
            return sorted_values[-1]
        if floor_k < 0:
            return sorted_values[0]
            
        return sorted_values[floor_k] + (k - floor_k) * (sorted_values[ceiling_k] - sorted_values[floor_k])
    
    def _variance(self, values: List[float], ddof: int = 1) -> float:
        """Calculate variance with degrees of freedom correction"""
        if len(values) <= ddof:
            return 0
        mean = statistics.mean(values)
        return sum((x - mean) ** 2 for x in values) / (len(values) - ddof)
    
    def _t_critical(self, df: int, alpha: float = 0.05) -> float:
        """Approximate t-critical value for given degrees of freedom"""
        # Simplified approximation for common cases
        t_table = {
            1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571,
            6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228,
            15: 2.131, 20: 2.086, 25: 2.060, 30: 2.042
        }
        
        if df in t_table:
            return t_table[df]
        elif df > 30:
            return 1.96  # Normal approximation
        else:
            # Linear interpolation for intermediate values
            lower_df = max([k for k in t_table.keys() if k < df])
            upper_df = min([k for k in t_table.keys() if k > df])
            ratio = (df - lower_df) / (upper_df - lower_df)
            return t_table[lower_df] + ratio * (t_table[upper_df] - t_table[lower_df])
    
    def _t_to_p(self, t_stat: float, df: int) -> float:
        """Approximate p-value from t-statistic (two-tailed)"""
        abs_t = abs(t_stat)
        
        # Rough approximation for p-values
        if abs_t > 3.5:
            return 0.001
        elif abs_t > 2.8:
            return 0.01
        elif abs_t > 2.0:
            return 0.05
        elif abs_t > 1.5:
            return 0.1
        else:
            return 0.2
    
    def _pearson_correlation(self, x: List[float], y: List[float]) -> tuple:
        """Calculate Pearson correlation coefficient and approximate p-value"""
        n = len(x)
        if n != len(y) or n < 2:
            return 0, 1
        
        mean_x = statistics.mean(x)
        mean_y = statistics.mean(y)
        
        numerator = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))
        sum_sq_x = sum((x[i] - mean_x) ** 2 for i in range(n))
        sum_sq_y = sum((y[i] - mean_y) ** 2 for i in range(n))
        
        denominator = math.sqrt(sum_sq_x * sum_sq_y)
        
        if denominator == 0:
            return 0, 1
        
        r = numerator / denominator
        
        # Approximate p-value using t-test
        if abs(r) == 1:
            p_value = 0.001
        else:
            t_stat = r * math.sqrt((n - 2) / (1 - r**2))
            p_value = self._t_to_p(t_stat, n - 2)
        
        return r, p_value
    
    def _is_categorical_data(self, values: List) -> bool:
        """Check if data appears to be categorical (non-numeric strings)"""
        if not values:
            return False
        
        # Check if all values are strings that don't represent numbers
        for value in values:
            if isinstance(value, (int, float)):
                return False
            if isinstance(value, str):
                try:
                    float(value)
                    return False  # It's a numeric string
                except ValueError:
                    continue  # It's a non-numeric string, which is good for categorical
            else:
                return False  # Unknown type
        
        return True
    
    def _detect_analysis_type(self, data: Dict, groups: Optional[Dict] = None) -> str:
        """Automatically detect the most appropriate analysis type based on data structure"""
        if groups:
            if len(groups) > 2:
                return "anova_analysis"
            elif len(groups) == 2:
                return "two_group_comparison"
        
        if data:
            if "before" in data and "after" in data:
                return "paired_comparison"
            elif len(data) == 1:
                # Single variable analysis - check if categorical or numerical
                values = list(data.values())[0]
                if self._is_categorical_data(values):
                    return "frequency_analysis"
                else:
                    return "comprehensive_descriptive"
            elif len(data) == 2:
                # Check if this might be categorical data for chi-square
                data_values = list(data.values())
                if self._is_categorical_data(data_values[0]) and self._is_categorical_data(data_values[1]):
                    return "chi_square_test"
                else:
                    return "correlation_analysis"
            elif len(data) >= 2:
                return "correlation_analysis"
        
        return "comprehensive_descriptive"
    
    def _calculate_descriptive_stats(self, values: List[float]) -> Dict:
        """Calculate comprehensive descriptive statistics for a dataset"""
        if not values:
            return {"error": "No data provided"}
        
        try:
            values = [float(v) for v in values]
            n = len(values)
            mean = statistics.mean(values)
            median = statistics.median(values)
            std = statistics.stdev(values) if n > 1 else 0
            
            result = {
                "n": n,
                "mean": round(mean, 3),
                "median": round(median, 3),
                "std": round(std, 3),
                "variance": round(std**2, 3) if n > 1 else 0,
                "min": round(min(values), 3),
                "max": round(max(values), 3),
                "range": round(max(values) - min(values), 3)
            }
            
            # Calculate percentiles for comprehensive analysis
            percentiles = [5, 10, 25, 50, 75, 90, 95, 99]
            percentile_results = {}
            for p in percentiles:
                if n >= 2:  # Need at least 2 data points for meaningful percentiles
                    pval = self._percentile(values, p)
                    percentile_results[f"p{p}"] = round(pval, 3)
            
            result.update(percentile_results)
            
            if n >= 4:
                q1 = percentile_results.get("p25", 0)
                q3 = percentile_results.get("p75", 0)
                iqr = q3 - q1
                result.update({
                    "q1": q1,
                    "q3": q3,
                    "iqr": round(iqr, 3)
                })
                
                # Outlier detection using IQR method
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                outliers = [v for v in values if v < lower_bound or v > upper_bound]
                if outliers:
                    result["outliers"] = [round(o, 3) for o in outliers]
                else:
                    result["outliers"] = []
            
            # Calculate coefficient of variation
            if mean != 0:
                cv = (std / abs(mean)) * 100
                result["coefficient_of_variation"] = round(cv, 2)
            
            # Calculate skewness (simplified)
            if n >= 3 and std > 0:
                skewness = sum((x - mean)**3 for x in values) / (n * std**3)
                result["skewness"] = round(skewness, 3)
            
            # Calculate confidence interval for the mean (95% by default)
            if n > 1:
                se_mean = std / math.sqrt(n)
                t_critical = self._t_critical(n - 1, 0.05)
                margin_error = t_critical * se_mean
                ci_lower = mean - margin_error
                ci_upper = mean + margin_error
                result.update({
                    "mean_se": round(se_mean, 3),
                    "mean_ci_95_lower": round(ci_lower, 3),
                    "mean_ci_95_upper": round(ci_upper, 3)
                })
            
            return result
        except Exception as e:
            return {"error": f"Error calculating descriptive stats: {str(e)}"}
    
    def _perform_t_test(self, group1: List[float], group2: List[float], paired: bool = False) -> Dict:
        """Perform t-test analysis"""
        try:
            group1 = [float(v) for v in group1]
            group2 = [float(v) for v in group2]
            
            if paired:
                if len(group1) != len(group2):
                    return {"error": "Paired t-test requires equal sample sizes"}
                
                # Paired t-test
                differences = [group1[i] - group2[i] for i in range(len(group1))]
                mean_diff = statistics.mean(differences)
                std_diff = statistics.stdev(differences) if len(differences) > 1 else 0
                
                if std_diff == 0:
                    t_stat = float('inf') if mean_diff != 0 else 0
                else:
                    t_stat = mean_diff / (std_diff / math.sqrt(len(differences)))
                
                df = len(differences) - 1
                test_type = "Paired t-test"
                cohens_d = mean_diff / std_diff if std_diff > 0 else 0
                
            else:
                # Independent t-test
                mean1 = statistics.mean(group1)
                mean2 = statistics.mean(group2)
                var1 = self._variance(group1)
                var2 = self._variance(group2)
                n1, n2 = len(group1), len(group2)
                
                # Pooled standard deviation
                pooled_var = ((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2)
                pooled_std = math.sqrt(pooled_var)
                
                if pooled_std == 0:
                    t_stat = float('inf') if mean1 != mean2 else 0
                else:
                    t_stat = (mean1 - mean2) / (pooled_std * math.sqrt(1/n1 + 1/n2))
                
                df = n1 + n2 - 2
                test_type = "Independent t-test"
                cohens_d = (mean1 - mean2) / pooled_std if pooled_std > 0 else 0
                mean_diff = mean1 - mean2
            
            # Calculate p-value (approximate)
            p_value = self._t_to_p(t_stat, df)
            
            # Effect size interpretation
            if abs(cohens_d) < 0.2:
                effect_interpretation = "Small effect"
            elif abs(cohens_d) < 0.5:
                effect_interpretation = "Medium effect"
            elif abs(cohens_d) < 0.8:
                effect_interpretation = "Large effect"
            else:
                effect_interpretation = "Very large effect"
            
            # Statistical indicators without interpretation
            if p_value < 0.001:
                p_display = "p < 0.001"
            elif p_value < 0.01:
                p_display = "p < 0.01"
            elif p_value < 0.05:
                p_display = "p < 0.05"
            else:
                p_display = f"p = {p_value:.3f}"
            
            return {
                "test_type": test_type,
                "t_statistic": round(t_stat, 3),
                "p_value": p_value,
                "p_value_display": p_display,
                "degrees_of_freedom": df,
                "cohens_d": round(cohens_d, 3),
                "effect_size_category": effect_interpretation,
                "mean_difference": round(statistics.mean(group1) - statistics.mean(group2), 3)
            }
        except Exception as e:
            return {"error": f"Error performing t-test: {str(e)}"}
    
    def _perform_anova(self, groups: Dict[str, List[float]]) -> Dict:
        """Perform one-way ANOVA analysis (simplified implementation)"""
        try:
            group_data = []
            group_names = list(groups.keys())
            
            for name, values in groups.items():
                group_data.append([float(v) for v in values])
            
            # Calculate ANOVA components
            all_values = [v for group in group_data for v in group]
            total_mean = statistics.mean(all_values)
            total_n = len(all_values)
            
            # Between-group sum of squares
            ss_between = sum(len(group) * (statistics.mean(group) - total_mean)**2 for group in group_data)
            
            # Within-group sum of squares  
            ss_within = sum(sum((v - statistics.mean(group))**2 for v in group) for group in group_data)
            
            # Degrees of freedom
            df_between = len(groups) - 1
            df_within = total_n - len(groups)
            
            # Mean squares
            ms_between = ss_between / df_between if df_between > 0 else 0
            ms_within = ss_within / df_within if df_within > 0 else 0
            
            # F-statistic
            f_stat = ms_between / ms_within if ms_within > 0 else float('inf')
            
            # Approximate p-value (simplified)
            if f_stat > 5.0:
                p_value = 0.001
            elif f_stat > 3.5:
                p_value = 0.01
            elif f_stat > 2.5:
                p_value = 0.05
            else:
                p_value = 0.1
            
            # Statistical indicators without conclusions
            if p_value < 0.001:
                f_p_display = "p < 0.001"
            elif p_value < 0.01:
                f_p_display = "p < 0.01"
            elif p_value < 0.05:
                f_p_display = "p < 0.05"
            else:
                f_p_display = f"p = {p_value:.3f}"
            
            # Effect size (eta-squared)
            eta_squared = ss_between / (ss_between + ss_within) if (ss_between + ss_within) > 0 else 0
            
            # Effect size interpretation
            if eta_squared < 0.01:
                effect_interpretation = "Small effect"
            elif eta_squared < 0.06:
                effect_interpretation = "Medium effect"
            else:
                effect_interpretation = "Large effect"
            
            # Post-hoc analysis (simplified pairwise comparisons)
            posthoc_results = []
            if p_value < 0.05 and len(groups) > 2:
                for i in range(len(group_names)):
                    for j in range(i + 1, len(group_names)):
                        name1, name2 = group_names[i], group_names[j]
                        group1_data = [float(v) for v in groups[name1]]
                        group2_data = [float(v) for v in groups[name2]]
                        
                        # Simple t-test for post-hoc
                        t_result = self._perform_t_test(group1_data, group2_data, paired=False)
                        mean_diff = statistics.mean(group1_data) - statistics.mean(group2_data)
                        
                        posthoc_results.append({
                            "comparison": f"{name1} vs {name2}",
                            "mean_difference": round(mean_diff, 3),
                            "p_value": t_result.get("p_value", 1.0),
                            "significant": t_result.get("p_value", 1.0) < 0.05
                        })
            
            return {
                "test_type": "One-way ANOVA",
                "f_statistic": round(f_stat, 3),
                "p_value": p_value,
                "p_value_display": f_p_display,
                "df_between": df_between,
                "df_within": df_within,
                "eta_squared": round(eta_squared, 3),
                "effect_size_category": effect_interpretation,
                "posthoc_comparisons": posthoc_results
            }
        except Exception as e:
            return {"error": f"Error performing ANOVA: {str(e)}"}
    
    def _perform_distribution_analysis(self, values: List[float], variable_name: str = "data") -> Dict:
        """Perform comprehensive single-variable distribution analysis"""
        try:
            values = [float(v) for v in values]
            n = len(values)
            
            if n < 2:
                return {"error": "Need at least 2 data points for distribution analysis"}
            
            # Get basic descriptive stats
            desc_stats = self._calculate_descriptive_stats(values)
            if "error" in desc_stats:
                return desc_stats
            
            # Additional distribution analysis
            mean = desc_stats["mean"]
            std = desc_stats["std"]
            median = desc_stats["median"]
            
            result = {
                "variable_name": variable_name,
                "analysis_type": "Single Variable Distribution Analysis",
                "descriptive_statistics": desc_stats
            }
            
            # Distribution shape analysis
            if std > 0 and n >= 3:
                skewness = desc_stats.get("skewness", 0)
                
                # Shape interpretation
                if abs(skewness) < 0.5:
                    shape_desc = "Approximately symmetric"
                elif skewness > 0.5:
                    shape_desc = "Right-skewed (positive skew)"
                else:
                    shape_desc = "Left-skewed (negative skew)"
                
                result["distribution_shape"] = {
                    "skewness": skewness,
                    "shape_description": shape_desc
                }
            
            # Normality assessment (simplified)
            if n >= 8:
                # Simple normality checks
                mean_median_diff = abs(mean - median)
                relative_diff = (mean_median_diff / std) if std > 0 else 0
                
                # Check if data roughly follows 68-95-99.7 rule
                within_1std = sum(1 for v in values if abs(v - mean) <= std) / n
                within_2std = sum(1 for v in values if abs(v - mean) <= 2*std) / n
                
                result["normality_assessment"] = {
                    "mean_median_difference": round(mean_median_diff, 3),
                    "relative_difference": round(relative_diff, 3),
                    "within_1_std_pct": round(within_1std * 100, 1),
                    "within_2_std_pct": round(within_2std * 100, 1),
                    "expected_1std_pct": 68.3,
                    "expected_2std_pct": 95.4,
                    "normality_note": "Normal distribution expectation: ~68% within 1 std, ~95% within 2 std. Small mean-median difference suggests symmetry."
                }
            
            # Percentile-based analysis for performance metrics
            if "p95" in desc_stats and "p50" in desc_stats:
                p50 = desc_stats["p50"]  # median
                p95 = desc_stats["p95"]
                p99 = desc_stats.get("p99", 0)
                
                result["performance_metrics"] = {
                    "p50_median": p50,
                    "p95": p95,
                    "p99": p99,
                    "p95_p50_ratio": round(p95/p50, 2) if p50 > 0 else 0
                }
            
            # Data quality indicators
            if desc_stats.get("outliers"):
                outlier_pct = len(desc_stats["outliers"]) / n * 100
                result["data_quality"] = {
                    "outlier_count": len(desc_stats["outliers"]),
                    "outlier_percentage": round(outlier_pct, 1),
                    "outlier_values": desc_stats["outliers"]
                }
            else:
                result["data_quality"] = {
                    "outlier_count": 0,
                    "outlier_percentage": 0.0
                }
            
            # Variability analysis
            cv = desc_stats.get("coefficient_of_variation", 0)
            if cv is not None:
                if cv < 10:
                    variability_desc = "Low variability"
                elif cv < 25:
                    variability_desc = "Moderate variability" 
                elif cv < 50:
                    variability_desc = "High variability"
                else:
                    variability_desc = "Very high variability"
                
                result["variability_analysis"] = {
                    "coefficient_of_variation": cv,
                    "variability_category": variability_desc
                }
            
            return result
            
        except Exception as e:
            return {"error": f"Error performing distribution analysis: {str(e)}"}
    
    def _perform_chi_square_test(self, var1: List[str], var2: List[str], var1_name: str = "Variable1", var2_name: str = "Variable2") -> Dict:
        """Perform chi-square test of independence for categorical variables"""
        try:
            if len(var1) != len(var2):
                return {"error": "Variables must have equal length for chi-square test"}
            
            if len(var1) < 5:
                return {"error": "Chi-square test requires at least 5 observations"}
            
            # Create contingency table
            contingency_table, categories1, categories2 = self._create_contingency_table(var1, var2)
            
            # Calculate chi-square statistic
            chi_square_result = self._calculate_chi_square_statistic(contingency_table)
            
            if "error" in chi_square_result:
                return chi_square_result
            
            # Calculate degrees of freedom
            df = (len(categories1) - 1) * (len(categories2) - 1)
            
            # Approximate p-value
            chi_square_stat = chi_square_result["chi_square"]
            p_value = self._chi_square_to_p(chi_square_stat, df)
            
            # Effect size (Cramér's V)
            n = len(var1)
            cramers_v = math.sqrt(chi_square_stat / (n * min(len(categories1) - 1, len(categories2) - 1)))
            
            # Effect size interpretation
            if cramers_v < 0.1:
                effect_interpretation = "Negligible association"
            elif cramers_v < 0.3:
                effect_interpretation = "Small association"
            elif cramers_v < 0.5:
                effect_interpretation = "Medium association"
            else:
                effect_interpretation = "Large association"
            
            # P-value display
            if p_value < 0.001:
                p_display = "p < 0.001"
            elif p_value < 0.01:
                p_display = "p < 0.01"
            elif p_value < 0.05:
                p_display = "p < 0.05"
            else:
                p_display = f"p = {p_value:.3f}"
            
            return {
                "test_type": "Chi-square test of independence",
                "variable_1": var1_name,
                "variable_2": var2_name,
                "chi_square_statistic": round(chi_square_stat, 3),
                "degrees_of_freedom": df,
                "p_value": p_value,
                "p_value_display": p_display,
                "cramers_v": round(cramers_v, 3),
                "effect_size_category": effect_interpretation,
                "sample_size": n,
                "contingency_table": contingency_table,
                "categories_1": categories1,
                "categories_2": categories2,
                "expected_frequencies": chi_square_result.get("expected_frequencies", [])
            }
            
        except Exception as e:
            return {"error": f"Error performing chi-square test: {str(e)}"}
    
    def _create_contingency_table(self, var1: List[str], var2: List[str]) -> tuple:
        """Create contingency table from two categorical variables"""
        # Get unique categories
        categories1 = sorted(list(set(var1)))
        categories2 = sorted(list(set(var2)))
        
        # Initialize contingency table
        table = []
        for cat1 in categories1:
            row = []
            for cat2 in categories2:
                count = sum(1 for i in range(len(var1)) if var1[i] == cat1 and var2[i] == cat2)
                row.append(count)
            table.append(row)
        
        return table, categories1, categories2
    
    def _calculate_chi_square_statistic(self, observed: List[List[int]]) -> Dict:
        """Calculate chi-square statistic from contingency table"""
        try:
            rows = len(observed)
            cols = len(observed[0])
            n = sum(sum(row) for row in observed)
            
            if n == 0:
                return {"error": "No observations in contingency table"}
            
            # Calculate row and column totals
            row_totals = [sum(observed[i]) for i in range(rows)]
            col_totals = [sum(observed[i][j] for i in range(rows)) for j in range(cols)]
            
            # Calculate expected frequencies
            expected = []
            for i in range(rows):
                row = []
                for j in range(cols):
                    expected_freq = (row_totals[i] * col_totals[j]) / n
                    row.append(expected_freq)
                expected.append(row)
            
            # Check for low expected frequencies
            low_expected = []
            for i in range(rows):
                for j in range(cols):
                    if expected[i][j] < 5:
                        low_expected.append(f"Cell({i+1},{j+1}): {expected[i][j]:.1f}")
            
            # Calculate chi-square statistic
            chi_square = 0
            for i in range(rows):
                for j in range(cols):
                    if expected[i][j] > 0:
                        chi_square += (observed[i][j] - expected[i][j]) ** 2 / expected[i][j]
            
            result = {
                "chi_square": chi_square,
                "expected_frequencies": expected,
                "row_totals": row_totals,
                "col_totals": col_totals,
                "total_n": n
            }
            
            if low_expected:
                result["warning"] = f"Some expected frequencies < 5: {', '.join(low_expected)}. Results may be unreliable."
            
            return result
            
        except Exception as e:
            return {"error": f"Error calculating chi-square statistic: {str(e)}"}
    
    def _chi_square_to_p(self, chi_square: float, df: int) -> float:
        """Approximate p-value from chi-square statistic (simplified)"""
        # Very rough approximation for demonstration
        # In practice, you'd use a proper chi-square distribution function
        
        if df == 1:
            if chi_square > 10.83:
                return 0.001
            elif chi_square > 6.64:
                return 0.01
            elif chi_square > 3.84:
                return 0.05
            elif chi_square > 2.71:
                return 0.1
            else:
                return 0.2
        elif df == 2:
            if chi_square > 13.82:
                return 0.001
            elif chi_square > 9.21:
                return 0.01
            elif chi_square > 5.99:
                return 0.05
            elif chi_square > 4.61:
                return 0.1
            else:
                return 0.2
        elif df == 3:
            if chi_square > 16.27:
                return 0.001
            elif chi_square > 11.34:
                return 0.01
            elif chi_square > 7.81:
                return 0.05
            elif chi_square > 6.25:
                return 0.1
            else:
                return 0.2
        else:
            # For higher df, use rough approximation
            critical_005 = df + 2.32 * math.sqrt(2 * df)
            critical_001 = df + 3.09 * math.sqrt(2 * df)
            
            if chi_square > critical_001:
                return 0.001
            elif chi_square > critical_005:
                return 0.01
            elif chi_square > df + 1.64 * math.sqrt(2 * df):
                return 0.05
            else:
                return 0.1
    
    def _calculate_frequency_distribution(self, values: List[str], variable_name: str) -> Dict:
        """Calculate frequency distribution for categorical variable"""
        try:
            # Count frequencies
            frequency_dict = {}
            for value in values:
                frequency_dict[value] = frequency_dict.get(value, 0) + 1
            
            # Sort by frequency (descending)
            sorted_frequencies = sorted(frequency_dict.items(), key=lambda x: x[1], reverse=True)
            
            total_count = len(values)
            unique_categories = len(frequency_dict)
            
            # Calculate proportions
            proportions = {}
            for category, count in frequency_dict.items():
                proportions[category] = count / total_count
            
            # Calculate mode (most frequent category)
            mode_category = sorted_frequencies[0][0] if sorted_frequencies else None
            mode_count = sorted_frequencies[0][1] if sorted_frequencies else 0
            mode_proportion = mode_count / total_count if total_count > 0 else 0
            
            # Calculate entropy (measure of diversity)
            entropy = 0
            for count in frequency_dict.values():
                if count > 0:
                    p = count / total_count
                    entropy -= p * math.log2(p)
            
            return {
                "variable_name": variable_name,
                "analysis_type": "Frequency Distribution Analysis",
                "total_observations": total_count,
                "unique_categories": unique_categories,
                "frequencies": dict(sorted_frequencies),
                "proportions": {k: round(v, 3) for k, v in proportions.items()},
                "mode_category": mode_category,
                "mode_count": mode_count,
                "mode_proportion": round(mode_proportion, 3),
                "entropy": round(entropy, 3),
                "max_entropy": round(math.log2(unique_categories), 3) if unique_categories > 1 else 0,
                "entropy_ratio": round(entropy / math.log2(unique_categories), 3) if unique_categories > 1 else 0
            }
            
        except Exception as e:
            return {"error": f"Error calculating frequency distribution: {str(e)}"}
    
    def _calculate_correlation(self, var1: List[float], var2: List[float]) -> Dict:
        """Calculate correlation between two variables"""
        try:
            var1 = [float(v) for v in var1]
            var2 = [float(v) for v in var2]
            
            if len(var1) != len(var2):
                return {"error": "Variables must have equal length for correlation"}
            
            # Pearson correlation
            r, p_value = self._pearson_correlation(var1, var2)
            
            # Correlation strength categories (no interpretation)
            abs_r = abs(r)
            if abs_r < 0.1:
                strength_category = "Very weak"
            elif abs_r < 0.3:
                strength_category = "Weak"
            elif abs_r < 0.5:
                strength_category = "Moderate"
            elif abs_r < 0.7:
                strength_category = "Strong"
            else:
                strength_category = "Very strong"
            
            direction = "Positive" if r > 0 else "Negative"
            
            # P-value display without conclusions
            if p_value < 0.001:
                corr_p_display = "p < 0.001"
            elif p_value < 0.01:
                corr_p_display = "p < 0.01"
            elif p_value < 0.05:
                corr_p_display = "p < 0.05"
            else:
                corr_p_display = f"p = {p_value:.3f}"
            
            return {
                "correlation_coefficient": round(r, 3),
                "p_value": p_value,
                "p_value_display": corr_p_display,
                "strength_category": strength_category,
                "direction": direction,
                "r_squared": round(r**2, 3),
                "sample_size": len(var1)
            }
        except Exception as e:
            return {"error": f"Error calculating correlation: {str(e)}"}
    
    def analyze(self, conversation_id: str, workspace_id: str, data: Optional[Dict] = None, 
                groups: Optional[Dict] = None, analysis_type: str = "auto", 
                output_format: str = "json") -> dict:
        """Main analysis function"""
        self._ensure_workspace(conversation_id, workspace_id)
        
        # Auto-detect analysis type if needed
        if analysis_type == "auto":
            analysis_type = self._detect_analysis_type(data, groups)
        
        results = {}
        
        try:
            if analysis_type == "descriptive_analysis" and data:
                for key, values in data.items():
                    results[f"descriptive_{key}"] = self._calculate_descriptive_stats(values)
            
            elif analysis_type == "comprehensive_descriptive" and data:
                # Single variable comprehensive analysis
                for key, values in data.items():
                    results[f"distribution_{key}"] = self._perform_distribution_analysis(values, key)
            
            elif analysis_type == "paired_comparison" and data:
                if "before" in data and "after" in data:
                    results["descriptive_before"] = self._calculate_descriptive_stats(data["before"])
                    results["descriptive_after"] = self._calculate_descriptive_stats(data["after"])
                    results["t_test"] = self._perform_t_test(data["before"], data["after"], paired=True)
            
            elif analysis_type == "two_group_comparison" and groups:
                group_names = list(groups.keys())
                if len(group_names) >= 2:
                    for name, values in groups.items():
                        results[f"descriptive_{name}"] = self._calculate_descriptive_stats(values)
                    
                    group_values = list(groups.values())
                    results["t_test"] = self._perform_t_test(group_values[0], group_values[1], paired=False)
            
            elif analysis_type in ["anova_analysis", "multi_group_comparison"] and groups:
                for name, values in groups.items():
                    results[f"descriptive_{name}"] = self._calculate_descriptive_stats(values)
                results["anova"] = self._perform_anova(groups)
            
            elif analysis_type == "correlation_analysis" and data:
                data_keys = list(data.keys())
                if len(data_keys) >= 2:
                    for name, values in data.items():
                        results[f"descriptive_{name}"] = self._calculate_descriptive_stats(values)
                    
                    var1_values = list(data.values())[0]
                    var2_values = list(data.values())[1]
                    results["correlation"] = self._calculate_correlation(var1_values, var2_values)
            
            elif analysis_type == "chi_square_test" and data:
                data_keys = list(data.keys())
                if len(data_keys) >= 2:
                    var1_name, var2_name = data_keys[0], data_keys[1]
                    var1_values, var2_values = data[var1_name], data[var2_name]
                    
                    # Frequency analysis for each variable
                    results[f"frequency_{var1_name}"] = self._calculate_frequency_distribution(var1_values, var1_name)
                    results[f"frequency_{var2_name}"] = self._calculate_frequency_distribution(var2_values, var2_name)
                    
                    # Chi-square test
                    results["chi_square"] = self._perform_chi_square_test(var1_values, var2_values, var1_name, var2_name)
            
            elif analysis_type == "frequency_analysis" and data:
                # Handle frequency analysis for one or more categorical variables
                for var_name, var_values in data.items():
                    if isinstance(var_values, list):
                        results[f"frequency_{var_name}"] = self._calculate_frequency_distribution(var_values, var_name)
                        break  # Only analyze the first variable for frequency_analysis
            
            # Store analysis in workspace history
            analysis_record = {
                "analysis_type": analysis_type,
                "results": results,
                "data": data,
                "groups": groups,
                "workspace_id": workspace_id
            }
            self.conversations[conversation_id]["workspaces"][workspace_id]["analyses"].append(analysis_record)
            
            return self._format_output(results, analysis_type, output_format)
        
        except Exception as e:
            return {"error": f"Error in analysis: {str(e)}"}
    
    def _format_output(self, results: Dict, analysis_type: str, output_format: str) -> dict:
        """Format analysis results for output"""
        
        if not results:
            return {"error": "No results to display."}
        
        # Create structured JSON output
        output_data = {
            "analysis_report": {
                "title": "Statistical Analysis Report",
                "analysis_type": analysis_type,
                "output_format": output_format,
                "timestamp": None,  # Could be added if needed
                "results": {}
            }
        }
        
        # Process descriptive statistics
        for key, stats in results.items():
            if key.startswith("descriptive_"):
                var_name = key.replace("descriptive_", "")
                if "error" not in stats:
                    output_data["analysis_report"]["results"][f"descriptive_statistics_{var_name}"] = {
                        "variable_name": var_name,
                        "sample_size": stats.get('n', None),
                        "central_tendency": {
                            "mean": stats.get('mean', None),
                            "median": stats.get('median', None)
                        },
                        "variability": {
                            "standard_deviation": stats.get('std', None),
                            "variance": stats.get('variance', None),
                            "range": {
                                "value": stats.get('range', None),
                                "min": stats.get('min', None),
                                "max": stats.get('max', None)
                            }
                        },
                        "percentiles": {
                            "q1": stats.get('q1', stats.get('p25', None)),
                            "q3": stats.get('q3', stats.get('p75', None)),
                            "iqr": stats.get('iqr', None),
                            "all_percentiles": {
                                p: stats.get(p, None) for p in ['p5', 'p10', 'p25', 'p50', 'p75', 'p90', 'p95', 'p99']
                                if stats.get(p) is not None
                            }
                        },
                        "confidence_interval": {
                            "mean_95_ci_lower": stats.get('mean_ci_95_lower', None),
                            "mean_ci_95_upper": stats.get('mean_ci_95_upper', None),
                            "standard_error": stats.get('mean_se', None)
                        },
                        "outliers": {
                            "values": stats.get('outliers', []),
                            "count": len(stats.get('outliers', []))
                        },
                        "distribution_shape": {
                            "coefficient_of_variation": stats.get('coefficient_of_variation', None),
                            "skewness": stats.get('skewness', None)
                        }
                    }
                else:
                    output_data["analysis_report"]["results"][f"descriptive_statistics_{var_name}"] = {
                        "error": stats.get("error", "Unknown error")
                    }
        
        # Process t-test results
        if "t_test" in results:
            t_result = results["t_test"]
            if "error" not in t_result:
                output_data["analysis_report"]["results"]["t_test"] = {
                    "test_type": t_result.get('test_type', ''),
                    "t_statistic": t_result.get('t_statistic', None),
                    "degrees_of_freedom": t_result.get('degrees_of_freedom', None),
                    "p_value": t_result.get('p_value', None),
                    "p_value_display": t_result.get('p_value_display', ''),
                    "cohens_d": t_result.get('cohens_d', None),
                    "effect_size_category": t_result.get('effect_size_category', ''),
                    "mean_difference": t_result.get('mean_difference', None)
                }
            else:
                output_data["analysis_report"]["results"]["t_test"] = {
                    "error": t_result.get("error", "Unknown error")
                }
        
        # Process ANOVA results
        if "anova" in results:
            anova_result = results["anova"]
            if "error" not in anova_result:
                output_data["analysis_report"]["results"]["anova"] = {
                    "test_type": anova_result.get('test_type', 'One-way ANOVA'),
                    "f_statistic": anova_result.get('f_statistic', None),
                    "df_between": anova_result.get('df_between', None),
                    "df_within": anova_result.get('df_within', None),
                    "p_value": anova_result.get('p_value', None),
                    "p_value_display": anova_result.get('p_value_display', ''),
                    "eta_squared": anova_result.get('eta_squared', None),
                    "effect_size_category": anova_result.get('effect_size_category', ''),
                    "posthoc_comparisons": anova_result.get('posthoc_comparisons', [])
                }
            else:
                output_data["analysis_report"]["results"]["anova"] = {
                    "error": anova_result.get("error", "Unknown error")
                }
        
        # Process distribution analysis results
        for key, result in results.items():
            if key.startswith("distribution_") and "error" not in result:
                var_name = result.get("variable_name", key.replace("distribution_", ""))
                
                distribution_data = {
                    "variable_name": var_name,
                    "analysis_type": result.get("analysis_type", ""),
                    "descriptive_statistics": result.get("descriptive_statistics", {}),
                    "distribution_shape": result.get("distribution_shape", {}),
                    "normality_assessment": result.get("normality_assessment", {}),
                    "performance_metrics": result.get("performance_metrics", {}),
                    "data_quality": result.get("data_quality", {}),
                    "variability_analysis": result.get("variability_analysis", {})
                }
                
                output_data["analysis_report"]["results"][f"distribution_analysis_{var_name}"] = distribution_data
        
        # Process correlation results
        if "correlation" in results:
            corr_result = results["correlation"]
            if "error" not in corr_result:
                output_data["analysis_report"]["results"]["correlation"] = {
                    "correlation_coefficient": corr_result.get('correlation_coefficient', None),
                    "p_value": corr_result.get('p_value', None),
                    "p_value_display": corr_result.get('p_value_display', ''),
                    "r_squared": corr_result.get('r_squared', None),
                    "direction": corr_result.get('direction', ''),
                    "strength_category": corr_result.get('strength_category', ''),
                    "sample_size": corr_result.get('sample_size', None)
                }
            else:
                output_data["analysis_report"]["results"]["correlation"] = {
                    "error": corr_result.get("error", "Unknown error")
                }
        
        # Process frequency distribution results
        for key, result in results.items():
            if key.startswith("frequency_") and "error" not in result:
                var_name = result.get("variable_name", key.replace("frequency_", ""))
                
                frequency_data = {
                    "variable_name": var_name,
                    "total_observations": result.get('total_observations', None),
                    "unique_categories": result.get('unique_categories', None),
                    "mode_category": result.get('mode_category', None),
                    "mode_count": result.get('mode_count', None),
                    "mode_proportion": result.get('mode_proportion', None),
                    "frequencies": result.get('frequencies', {}),
                    "proportions": result.get('proportions', {}),
                    "shannon_entropy": result.get('entropy', None),
                    "max_entropy": result.get('max_entropy', None),
                    "entropy_ratio": result.get('entropy_ratio', None)
                }
                
                output_data["analysis_report"]["results"][f"frequency_analysis_{var_name}"] = frequency_data
        
        # Process chi-square test results
        if "chi_square" in results:
            chi_result = results["chi_square"]
            if "error" not in chi_result:
                output_data["analysis_report"]["results"]["chi_square"] = {
                    "test_type": chi_result.get('test_type', ''),
                    "variable_1": chi_result.get('variable_1', ''),
                    "variable_2": chi_result.get('variable_2', ''),
                    "chi_square_statistic": chi_result.get('chi_square_statistic', None),
                    "degrees_of_freedom": chi_result.get('degrees_of_freedom', None),
                    "p_value": chi_result.get('p_value', None),
                    "p_value_display": chi_result.get('p_value_display', ''),
                    "cramers_v": chi_result.get('cramers_v', None),
                    "effect_size_category": chi_result.get('effect_size_category', ''),
                    "sample_size": chi_result.get('sample_size', None),
                    "contingency_table": chi_result.get('contingency_table', []),
                    "categories_1": chi_result.get('categories_1', []),
                    "categories_2": chi_result.get('categories_2', [])
                }
            else:
                output_data["analysis_report"]["results"]["chi_square"] = {
                    "error": chi_result.get("error", "Unknown error")
                }
        
        # Add display recommendation and return as dictionary
        from tools.display_recommendations import DisplayRecommendations
        output_data.update(DisplayRecommendations.get_json_recommendation("stats", "analyze"))
        
        return output_data
    
    def get_analysis_report(self, conversation_id: str, workspace_id: str, report_type: str = "summary", output_format: str = "json") -> dict:
        """
        Generate a comprehensive statistical analysis report for agent processing.
        
        This method compiles all statistical analyses performed in a workspace into 
        a structured report that the agent can use to present findings to the user.
        The report includes:
        - Summary of all statistical tests performed
        - Detailed results with effect sizes and significance levels
        - Data overviews and group comparisons
        - Summary statistics across all analyses
        
        Args:
            conversation_id: Unique identifier for the conversation
            workspace_id: Unique identifier for the workspace
            report_type: Type of report to generate (default: "summary")
            output_format: Format of the output (default: "json")
            
        Returns:
            dict: Structured report data with display recommendations that the agent
            should use to present the statistical findings to the user in an appropriate format.
        """
        
        if conversation_id not in self.conversations or "workspaces" not in self.conversations[conversation_id]:
            return {"error": "No analyses found for this conversation."}
        
        if workspace_id not in self.conversations[conversation_id]["workspaces"]:
            return {"error": f"No analyses found for workspace '{workspace_id}' in this conversation."}
        
        analyses = self.conversations[conversation_id]["workspaces"][workspace_id]["analyses"]
        if not analyses:
            return {"error": f"No analyses found for workspace '{workspace_id}' in this conversation."}
        
        if output_format == "json":
            # Create comprehensive JSON report
            report_data = {
                "comprehensive_statistical_report": {
                    "title": "Comprehensive Statistical Analysis Report",
                    "conversation_id": conversation_id,
                    "workspace_id": workspace_id,
                    "report_type": report_type,
                    "total_analyses": len(analyses),
                    "statistical_summary": {
                        "t_tests": [],
                        "correlations": [],
                        "group_comparisons": [],
                        "categorical_analyses": []
                    },
                    "detailed_analyses": [],
                    "summary_statistics": {}
                }
            }
            
            # Extract statistical information
            for i, analysis in enumerate(analyses, 1):
                results = analysis.get('results', {})
                analysis_type = analysis.get('analysis_type', 'unknown')
                
                # Detailed analysis record
                detailed_analysis = {
                    "analysis_id": i,
                    "analysis_type": analysis_type,
                    "data_variables": list(analysis.get('data', {}).keys()) if analysis.get('data') else [],
                    "group_variables": list(analysis.get('groups', {}).keys()) if analysis.get('groups') else [],
                    "results": {}
                }
                
                # Add data overview
                if analysis.get('data'):
                    data_overview = {}
                    for var in analysis['data']:
                        var_data = analysis['data'][var]
                        if isinstance(var_data, list):
                            try:
                                numeric_data = [float(x) for x in var_data if x is not None]
                                if len(numeric_data) == len(var_data):
                                    data_overview[var] = {
                                        "type": "numerical",
                                        "sample_size": len(var_data),
                                        "range": {"min": min(numeric_data), "max": max(numeric_data)}
                                    }
                                else:
                                    data_overview[var] = {
                                        "type": "mixed_or_categorical",
                                        "sample_size": len(var_data),
                                        "unique_values": len(set(var_data))
                                    }
                            except (ValueError, TypeError):
                                data_overview[var] = {
                                    "type": "categorical",
                                    "sample_size": len(var_data),
                                    "unique_values": len(set(var_data))
                                }
                    detailed_analysis["data_overview"] = data_overview
                
                # Add group overview
                if analysis.get('groups'):
                    group_overview = {}
                    for group in analysis['groups']:
                        group_data = analysis['groups'][group]
                        if isinstance(group_data, list):
                            try:
                                numeric_data = [float(x) for x in group_data if x is not None]
                                if len(numeric_data) == len(group_data):
                                    group_overview[group] = {
                                        "type": "numerical",
                                        "sample_size": len(group_data),
                                        "mean": sum(numeric_data)/len(numeric_data) if numeric_data else None
                                    }
                                else:
                                    group_overview[group] = {
                                        "type": "mixed_or_categorical",
                                        "sample_size": len(group_data),
                                        "unique_values": len(set(group_data))
                                    }
                            except (ValueError, TypeError, ZeroDivisionError):
                                group_overview[group] = {
                                    "type": "categorical",
                                    "sample_size": len(group_data),
                                    "unique_values": len(set(group_data)) if group_data else 0
                                }
                    detailed_analysis["group_overview"] = group_overview
                
                # Extract statistical results
                if 't_test' in results and 'error' not in results['t_test']:
                    t_result = results['t_test']
                    t_test_data = {
                        "analysis_id": i,
                        "p_value": t_result.get('p_value', None),
                        "effect_size_category": t_result.get('effect_size_category', None),
                        "mean_difference": t_result.get('mean_difference', None),
                        "t_statistic": t_result.get('t_statistic', None),
                        "degrees_of_freedom": t_result.get('degrees_of_freedom', None),
                        "cohens_d": t_result.get('cohens_d', None)
                    }
                    report_data["comprehensive_statistical_report"]["statistical_summary"]["t_tests"].append(t_test_data)
                    detailed_analysis["results"]["t_test"] = t_test_data
                
                if 'anova' in results and 'error' not in results['anova']:
                    anova_result = results['anova']
                    posthoc = anova_result.get('posthoc_comparisons', [])
                    anova_data = {
                        "analysis_id": i,
                        "p_value": anova_result.get('p_value', None),
                        "effect_size_category": anova_result.get('effect_size_category', None),
                        "eta_squared": anova_result.get('eta_squared', None),
                        "f_statistic": anova_result.get('f_statistic', None),
                        "df_between": anova_result.get('df_between', None),
                        "df_within": anova_result.get('df_within', None),
                        "posthoc_comparisons_count": len(posthoc)
                    }
                    report_data["comprehensive_statistical_report"]["statistical_summary"]["group_comparisons"].append(anova_data)
                    detailed_analysis["results"]["anova"] = anova_data
                
                if 'correlation' in results and 'error' not in results['correlation']:
                    corr_result = results['correlation']
                    correlation_data = {
                        "analysis_id": i,
                        "correlation_coefficient": corr_result.get('correlation_coefficient', None),
                        "p_value": corr_result.get('p_value', None),
                        "strength_category": corr_result.get('strength_category', None),
                        "direction": corr_result.get('direction', None),
                        "r_squared": corr_result.get('r_squared', None),
                        "sample_size": corr_result.get('sample_size', None)
                    }
                    report_data["comprehensive_statistical_report"]["statistical_summary"]["correlations"].append(correlation_data)
                    detailed_analysis["results"]["correlation"] = correlation_data
                
                if 'chi_square' in results and 'error' not in results['chi_square']:
                    chi_result = results['chi_square']
                    chi_data = {
                        "analysis_id": i,
                        "chi_square_statistic": chi_result.get('chi_square_statistic', None),
                        "p_value": chi_result.get('p_value', None),
                        "cramers_v": chi_result.get('cramers_v', None),
                        "effect_size_category": chi_result.get('effect_size_category', None),
                        "sample_size": chi_result.get('sample_size', None),
                        "degrees_of_freedom": chi_result.get('degrees_of_freedom', None)
                    }
                    report_data["comprehensive_statistical_report"]["statistical_summary"]["categorical_analyses"].append(chi_data)
                    detailed_analysis["results"]["chi_square"] = chi_data
                
                if 'frequency' in results and 'error' not in results['frequency']:
                    freq_result = results['frequency']
                    frequency_data = {
                        "analysis_id": i,
                        "total_observations": freq_result.get('total_observations', None),
                        "unique_categories": freq_result.get('unique_categories', None),
                        "shannon_entropy": freq_result.get('shannon_entropy', None),
                        "diversity_ratio": freq_result.get('diversity_ratio', None),
                        "mode_category": freq_result.get('mode_category', None),
                        "mode_count": freq_result.get('mode_count', None)
                    }
                    report_data["comprehensive_statistical_report"]["statistical_summary"]["categorical_analyses"].append(frequency_data)
                    detailed_analysis["results"]["frequency"] = frequency_data
                
                # Handle frequency analysis with variable-specific keys (frequency_variablename)
                for key, value in results.items():
                    if key.startswith('frequency_') and 'error' not in value:
                        freq_result = value
                        frequency_data = {
                            "analysis_id": i,
                            "variable_name": freq_result.get('variable_name', key),
                            "total_observations": freq_result.get('total_observations', None),
                            "unique_categories": freq_result.get('unique_categories', None),
                            "shannon_entropy": freq_result.get('entropy', None),
                            "diversity_ratio": freq_result.get('entropy_ratio', None),
                            "mode_category": freq_result.get('mode_category', None),
                            "mode_count": freq_result.get('mode_count', None)
                        }
                        report_data["comprehensive_statistical_report"]["statistical_summary"]["categorical_analyses"].append(frequency_data)
                        detailed_analysis["results"][key] = frequency_data
                
                report_data["comprehensive_statistical_report"]["detailed_analyses"].append(detailed_analysis)
            
            # Summary statistics
            total_tests = (
                len(report_data["comprehensive_statistical_report"]["statistical_summary"]["t_tests"]) +
                len(report_data["comprehensive_statistical_report"]["statistical_summary"]["correlations"]) +
                len(report_data["comprehensive_statistical_report"]["statistical_summary"]["group_comparisons"]) +
                len(report_data["comprehensive_statistical_report"]["statistical_summary"]["categorical_analyses"])
            )
            
            effect_sizes_reported = sum(
                1 for analysis in analyses
                for results in [analysis.get('results', {})]
                if any(test_type in results and effect_size_field in results.get(test_type, {})
                      for test_type, effect_size_field in [('t_test', 'cohens_d'), ('anova', 'eta_squared'), ('chi_square', 'cramers_v')])
            )
            
            report_data["comprehensive_statistical_report"]["summary_statistics"] = {
                "total_analyses": len(analyses),
                "total_statistical_tests": total_tests,
                "t_tests_conducted": len(report_data["comprehensive_statistical_report"]["statistical_summary"]["t_tests"]),
                "correlations_calculated": len(report_data["comprehensive_statistical_report"]["statistical_summary"]["correlations"]),
                "group_comparisons_performed": len(report_data["comprehensive_statistical_report"]["statistical_summary"]["group_comparisons"]),
                "categorical_analyses_performed": len(report_data["comprehensive_statistical_report"]["statistical_summary"]["categorical_analyses"]),
                "effect_sizes_calculated": effect_sizes_reported,
                "note": "All p-values represent probability of observing results if null hypothesis is true"
            }
            
            # Add display recommendation to the report data
            report_data.update(DisplayRecommendations.get_json_recommendation("stats", "get_analysis_report"))
            return report_data