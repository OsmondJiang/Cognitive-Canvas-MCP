import statistics
import math
from typing import Dict, List, Optional, Any, Union

class StatisticalEvidenceTool:
    """
    Statistical Evidence Tool for analyzing data and generating evidence-based conclusions.
    Provides automated statistical analysis with intelligent method selection.
    """
    
    def __init__(self):
        self.conversations = {}
    
    def _ensure_conv(self, conversation_id: str):
        """Ensure conversation exists in storage"""
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = {
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
                # Single variable analysis - comprehensive descriptive analysis
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
                "n_note": "Sample size (number of observations)",
                "mean": round(mean, 3),
                "mean_note": "Arithmetic mean (average value)",
                "median": round(median, 3),
                "median_note": "Middle value when data is sorted (50th percentile)",
                "std": round(std, 3),
                "std_note": "Standard deviation (measure of data spread)",
                "variance": round(std**2, 3) if n > 1 else 0,
                "variance_note": "Variance (squared standard deviation)",
                "min": round(min(values), 3),
                "min_note": "Minimum value in dataset",
                "max": round(max(values), 3),
                "max_note": "Maximum value in dataset",
                "range": round(max(values) - min(values), 3),
                "range_note": "Range (max - min)"
            }
            
            # Calculate percentiles for comprehensive analysis
            percentiles = [5, 10, 25, 50, 75, 90, 95, 99]
            percentile_results = {}
            for p in percentiles:
                if n >= 2:  # Need at least 2 data points for meaningful percentiles
                    pval = self._percentile(values, p)
                    percentile_results[f"p{p}"] = round(pval, 3)
            
            result.update(percentile_results)
            result["percentiles_note"] = "Percentiles: P5=5th percentile, P10=10th percentile, P25=25th percentile (Q1), P50=median, P75=75th percentile (Q3), P90=90th percentile, P95=95th percentile, P99=99th percentile"
            
            if n >= 4:
                q1 = percentile_results.get("p25", 0)
                q3 = percentile_results.get("p75", 0)
                iqr = q3 - q1
                result.update({
                    "q1": q1,
                    "q1_note": "First quartile (25th percentile)",
                    "q3": q3,
                    "q3_note": "Third quartile (75th percentile)",
                    "iqr": round(iqr, 3),
                    "iqr_note": "Interquartile range (Q3 - Q1, contains middle 50% of data)"
                })
                
                # Outlier detection using IQR method
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                outliers = [v for v in values if v < lower_bound or v > upper_bound]
                if outliers:
                    result["outliers"] = [round(o, 3) for o in outliers]
                    result["outliers_note"] = f"Outliers detected using IQR method (values outside [{round(lower_bound, 3)}, {round(upper_bound, 3)}])"
                else:
                    result["outliers"] = []
                    result["outliers_note"] = "No outliers detected using IQR method"
            
            # Calculate coefficient of variation
            if mean != 0:
                cv = (std / abs(mean)) * 100
                result["coefficient_of_variation"] = round(cv, 2)
                result["cv_note"] = "Coefficient of variation (CV = std/mean × 100%, measures relative variability)"
            
            # Calculate skewness (simplified)
            if n >= 3 and std > 0:
                skewness = sum((x - mean)**3 for x in values) / (n * std**3)
                result["skewness"] = round(skewness, 3)
                result["skewness_note"] = "Skewness (measure of asymmetry: 0=symmetric, >0=right-skewed, <0=left-skewed)"
            
            # Calculate confidence interval for the mean (95% by default)
            if n > 1:
                se_mean = std / math.sqrt(n)
                t_critical = self._t_critical(n - 1, 0.05)
                margin_error = t_critical * se_mean
                ci_lower = mean - margin_error
                ci_upper = mean + margin_error
                result.update({
                    "mean_se": round(se_mean, 3),
                    "mean_se_note": "Standard error of the mean (std/√n)",
                    "mean_ci_95_lower": round(ci_lower, 3),
                    "mean_ci_95_upper": round(ci_upper, 3),
                    "mean_ci_note": "95% confidence interval for the mean (we are 95% confident the true population mean lies within this range)"
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
            p_value_note = "p-value: probability of observing this result if null hypothesis is true"
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
                "p_value_note": p_value_note,
                "degrees_of_freedom": df,
                "cohens_d": round(cohens_d, 3),
                "cohens_d_note": "Cohen's d: standardized effect size measure",
                "effect_size_category": effect_interpretation,
                "effect_size_note": "Effect size categories: small (<0.2), medium (0.2-0.8), large (>0.8)",
                "mean_difference": round(statistics.mean(group1) - statistics.mean(group2), 3),
                "mean_difference_note": "Raw difference between group means"
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
            f_p_note = "F-test p-value: probability of observing this F-statistic if all groups have equal means"
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
                "f_statistic_note": "F-statistic: ratio of between-group to within-group variance",
                "p_value": p_value,
                "p_value_display": f_p_display,
                "p_value_note": f_p_note,
                "df_between": df_between,
                "df_within": df_within,
                "degrees_freedom_note": "Degrees of freedom: between groups, within groups",
                "eta_squared": round(eta_squared, 3),
                "eta_squared_note": "η² (eta-squared): proportion of total variance explained by group differences",
                "effect_size_category": effect_interpretation,
                "effect_size_note": "Effect size categories: small (<0.01), medium (0.01-0.06), large (>0.06)",
                "posthoc_comparisons": posthoc_results,
                "posthoc_note": "Post-hoc comparisons: pairwise group comparisons when overall F-test indicates differences"
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
                    "shape_description": shape_desc,
                    "skewness_note": "Skewness measures asymmetry: 0=symmetric, >0=right tail longer, <0=left tail longer"
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
                    "p95_p50_ratio": round(p95/p50, 2) if p50 > 0 else 0,
                    "performance_note": "P50 (median): typical performance. P95: 95% of values are below this. P99: 99% of values are below this."
                }
            
            # Data quality indicators
            if desc_stats.get("outliers"):
                outlier_pct = len(desc_stats["outliers"]) / n * 100
                result["data_quality"] = {
                    "outlier_count": len(desc_stats["outliers"]),
                    "outlier_percentage": round(outlier_pct, 1),
                    "outlier_values": desc_stats["outliers"],
                    "quality_note": f"Outliers: {len(desc_stats['outliers'])} values ({outlier_pct:.1f}%) detected using IQR method"
                }
            else:
                result["data_quality"] = {
                    "outlier_count": 0,
                    "outlier_percentage": 0.0,
                    "quality_note": "No outliers detected using IQR method - data appears clean"
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
                    "variability_category": variability_desc,
                    "variability_note": "CV categories: Low (<10%), Moderate (10-25%), High (25-50%), Very High (>50%)"
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
                "test_note": "Tests whether two categorical variables are independent",
                "variable_1": var1_name,
                "variable_2": var2_name,
                "chi_square_statistic": round(chi_square_stat, 3),
                "chi_square_note": "Chi-square statistic: measures deviation from expected frequencies if variables were independent",
                "degrees_of_freedom": df,
                "df_note": f"Degrees of freedom: (rows-1) × (columns-1) = ({len(categories1)}-1) × ({len(categories2)}-1)",
                "p_value": p_value,
                "p_value_display": p_display,
                "p_value_note": "p-value: probability of observing this association (or stronger) if variables were truly independent",
                "cramers_v": round(cramers_v, 3),
                "cramers_v_note": "Cramér's V: effect size measure for categorical associations (0 = no association, 1 = perfect association)",
                "effect_size_category": effect_interpretation,
                "effect_size_note": "Effect size categories: negligible (<0.1), small (0.1-0.3), medium (0.3-0.5), large (>0.5)",
                "sample_size": n,
                "contingency_table": contingency_table,
                "categories_1": categories1,
                "categories_2": categories2,
                "contingency_note": "Contingency table shows observed frequencies for each combination of categories",
                "expected_frequencies": chi_square_result.get("expected_frequencies", []),
                "expected_note": "Expected frequencies assuming independence (calculated from marginal totals)"
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
                "total_note": "Total number of observations in the dataset",
                "unique_categories": unique_categories,
                "unique_note": "Number of distinct categories found",
                "frequencies": dict(sorted_frequencies),
                "frequencies_note": "Count of each category (sorted by frequency)",
                "proportions": {k: round(v, 3) for k, v in proportions.items()},
                "proportions_note": "Proportion of each category (frequency/total)",
                "mode_category": mode_category,
                "mode_count": mode_count,
                "mode_proportion": round(mode_proportion, 3),
                "mode_note": f"Most frequent category: '{mode_category}' appears {mode_count} times ({mode_proportion:.1%})",
                "entropy": round(entropy, 3),
                "entropy_note": "Shannon entropy: measure of category diversity (higher = more diverse)",
                "max_entropy": round(math.log2(unique_categories), 3) if unique_categories > 1 else 0,
                "entropy_ratio": round(entropy / math.log2(unique_categories), 3) if unique_categories > 1 else 0,
                "diversity_note": "Entropy ratio: actual diversity / maximum possible diversity (1 = perfectly diverse)"
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
                "correlation_note": "Pearson r: linear relationship strength (-1 to +1)",
                "p_value": p_value,
                "p_value_display": corr_p_display,
                "p_value_note": "p-value: probability of observing this correlation if no true relationship exists",
                "strength_category": strength_category,
                "direction": direction,
                "strength_note": "Correlation strength categories: very weak (<0.1), weak (0.1-0.3), moderate (0.3-0.5), strong (0.5-0.7), very strong (>0.7)",
                "r_squared": round(r**2, 3),
                "r_squared_note": "R²: proportion of variance in one variable explained by the other",
                "sample_size": len(var1),
                "sample_size_note": "Sample size affects reliability of correlation estimate"
            }
        except Exception as e:
            return {"error": f"Error calculating correlation: {str(e)}"}
    
    def analyze(self, conversation_id: str, data: Optional[Dict] = None, 
                groups: Optional[Dict] = None, analysis_type: str = "auto", 
                output_format: str = "comprehensive") -> str:
        """Main analysis function"""
        self._ensure_conv(conversation_id)
        
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
            
            # Store analysis in conversation history
            analysis_record = {
                "analysis_type": analysis_type,
                "results": results,
                "data": data,
                "groups": groups
            }
            self.conversations[conversation_id]["analyses"].append(analysis_record)
            
            return self._format_output(results, analysis_type, output_format)
        
        except Exception as e:
            return f"Error in analysis: {str(e)}"
    
    def batch_analyze(self, conversation_id: str, data: Dict, 
                     batch_analyses: List[Dict], output_format: str = "comprehensive") -> str:
        """Perform multiple analyses in a single call"""
        self._ensure_conv(conversation_id)
        
        all_results = {}
        
        for analysis_config in batch_analyses:
            analysis_type = analysis_config.get("type", "auto")
            
            if analysis_type == "descriptive":
                variables = analysis_config.get("variables", list(data.keys()))
                for var in variables:
                    if var in data:
                        all_results[f"descriptive_{var}"] = self._calculate_descriptive_stats(data[var])
            
            elif analysis_type == "correlation":
                var1 = analysis_config.get("var1")
                var2 = analysis_config.get("var2")
                if var1 in data and var2 in data:
                    all_results[f"correlation_{var1}_{var2}"] = self._calculate_correlation(data[var1], data[var2])
            
            elif analysis_type == "outlier_detection":
                variable = analysis_config.get("variable")
                if variable in data:
                    desc_stats = self._calculate_descriptive_stats(data[variable])
                    if "outliers" in desc_stats:
                        all_results[f"outliers_{variable}"] = desc_stats["outliers"]
        
        return self._format_batch_output(all_results, output_format)
    
    def _format_output(self, results: Dict, analysis_type: str, output_format: str) -> str:
        """Format analysis results for output"""
        if not results:
            return "No results to display."
        
        output = []
        output.append("🔬 Statistical Analysis Report")
        output.append("━" * 50)
        
        # Format descriptive statistics
        for key, stats in results.items():
            if key.startswith("descriptive_"):
                var_name = key.replace("descriptive_", "")
                if "error" not in stats:
                    output.append(f"\n📊 {var_name} Descriptive Statistics:")
                    output.append(f"• Sample size: {stats.get('n', 'N/A')} ({stats.get('n_note', '')})")
                    output.append(f"• Mean: {stats.get('mean', 'N/A')} ({stats.get('mean_note', '')})")
                    output.append(f"• Median: {stats.get('median', 'N/A')} ({stats.get('median_note', '')})")
                    output.append(f"• Standard deviation: {stats.get('std', 'N/A')} ({stats.get('std_note', '')})")
                    output.append(f"• Range: {stats.get('range', 'N/A')} [{stats.get('min', 'N/A')} to {stats.get('max', 'N/A')}]")
                    
                    # Show percentiles if available
                    if stats.get('p25') is not None:
                        output.append(f"• Q1 (25th percentile): {stats.get('p25', 'N/A')}")
                        output.append(f"• Q3 (75th percentile): {stats.get('p75', 'N/A')}")
                        output.append(f"• IQR: {stats.get('iqr', 'N/A')} ({stats.get('iqr_note', '')})")
                    
                    # Show confidence interval if available
                    if stats.get('mean_ci_95_lower') is not None:
                        output.append(f"• 95% CI for mean: [{stats['mean_ci_95_lower']}, {stats['mean_ci_95_upper']}]")
                    
                    # Show outliers if any
                    if stats.get("outliers") and len(stats["outliers"]) > 0:
                        output.append(f"• Outliers: {stats['outliers']} ({stats.get('outliers_note', '')})")
                    elif stats.get("outliers_note"):
                        output.append(f"• {stats.get('outliers_note', '')}")
        
        # Format t-test results
        if "t_test" in results:
            t_result = results["t_test"]
            if "error" not in t_result:
                output.append(f"\n🧮 {t_result['test_type']} Results:")
                output.append(f"• t-statistic: {t_result['t_statistic']} (df = {t_result['degrees_of_freedom']})")
                output.append(f"• {t_result['p_value_display']} ({t_result['p_value_note']})")
                output.append(f"• Cohen's d: {t_result['cohens_d']} ({t_result['cohens_d_note']})")
                output.append(f"• Effect size category: {t_result['effect_size_category']} ({t_result['effect_size_note']})")
                output.append(f"• Mean difference: {t_result['mean_difference']} ({t_result['mean_difference_note']})")
        
        # Format ANOVA results
        if "anova" in results:
            anova_result = results["anova"]
            if "error" not in anova_result:
                output.append(f"\n🔬 Analysis of Variance (ANOVA) Results:")
                output.append(f"• F-statistic: {anova_result['f_statistic']} (df = {anova_result['df_between']}, {anova_result['df_within']})")
                output.append(f"• {anova_result['f_statistic_note']}")
                output.append(f"• {anova_result['p_value_display']} ({anova_result['p_value_note']})")
                output.append(f"• η² (eta-squared): {anova_result['eta_squared']} ({anova_result['eta_squared_note']})")
                output.append(f"• Effect size category: {anova_result['effect_size_category']} ({anova_result['effect_size_note']})")
                
                if anova_result.get("posthoc_comparisons"):
                    output.append(f"\n📈 Post-hoc Analysis ({anova_result['posthoc_note']}):")
                    for comp in anova_result["posthoc_comparisons"]:
                        p_status = f"p = {comp['p_value']:.3f}" if comp['p_value'] >= 0.05 else f"p < {comp['p_value']:.3f}"
                        output.append(f"  {comp['comparison']}: difference = {comp['mean_difference']:.3f}, {p_status}")
        
        # Format distribution analysis results
        for key, result in results.items():
            if key.startswith("distribution_") and "error" not in result:
                var_name = result.get("variable_name", key.replace("distribution_", ""))
                output.append(f"\n📊 Distribution Analysis: {var_name}")
                
                # Basic descriptive statistics
                desc_stats = result.get("descriptive_statistics", {})
                if desc_stats and "error" not in desc_stats:
                    output.append(f"\n📈 Descriptive Statistics:")
                    output.append(f"• Sample size: {desc_stats.get('n', 'N/A')} ({desc_stats.get('n_note', '')})")
                    output.append(f"• Mean: {desc_stats.get('mean', 'N/A')} ({desc_stats.get('mean_note', '')})")
                    output.append(f"• Median: {desc_stats.get('median', 'N/A')} ({desc_stats.get('median_note', '')})")
                    output.append(f"• Standard deviation: {desc_stats.get('std', 'N/A')} ({desc_stats.get('std_note', '')})")
                    output.append(f"• Range: {desc_stats.get('range', 'N/A')} [{desc_stats.get('min', 'N/A')} to {desc_stats.get('max', 'N/A')}]")
                    
                    # Percentiles
                    if desc_stats.get('p5') is not None:
                        output.append(f"\n📊 Percentiles ({desc_stats.get('percentiles_note', '')}):")
                        percentiles = ['p5', 'p10', 'p25', 'p50', 'p75', 'p90', 'p95', 'p99']
                        for p in percentiles:
                            if desc_stats.get(p) is not None:
                                output.append(f"  {p.upper()}: {desc_stats[p]}")
                    
                    # Confidence interval
                    if desc_stats.get('mean_ci_95_lower') is not None:
                        output.append(f"\n🎯 95% Confidence Interval for Mean:")
                        output.append(f"• [{desc_stats['mean_ci_95_lower']}, {desc_stats['mean_ci_95_upper']}]")
                        output.append(f"• {desc_stats.get('mean_ci_note', '')}")
                
                # Distribution shape
                if "distribution_shape" in result:
                    shape = result["distribution_shape"]
                    output.append(f"\n📐 Distribution Shape:")
                    output.append(f"• Skewness: {shape.get('skewness', 'N/A')} ({shape.get('skewness_note', '')})")
                    output.append(f"• Shape: {shape.get('shape_description', 'N/A')}")
                
                # Normality assessment
                if "normality_assessment" in result:
                    norm = result["normality_assessment"]
                    output.append(f"\n🔍 Normality Assessment:")
                    output.append(f"• Mean-median difference: {norm.get('mean_median_difference', 'N/A')}")
                    output.append(f"• Within 1 std: {norm.get('within_1_std_pct', 'N/A')}% (expected: {norm.get('expected_1std_pct', 'N/A')}%)")
                    output.append(f"• Within 2 std: {norm.get('within_2_std_pct', 'N/A')}% (expected: {norm.get('expected_2std_pct', 'N/A')}%)")
                    output.append(f"• {norm.get('normality_note', '')}")
                
                # Performance metrics
                if "performance_metrics" in result:
                    perf = result["performance_metrics"]
                    output.append(f"\n⚡ Performance Metrics:")
                    output.append(f"• P50 (median): {perf.get('p50_median', 'N/A')}")
                    output.append(f"• P95: {perf.get('p95', 'N/A')}")
                    output.append(f"• P99: {perf.get('p99', 'N/A')}")
                    output.append(f"• P95/P50 ratio: {perf.get('p95_p50_ratio', 'N/A')}")
                    output.append(f"• {perf.get('performance_note', '')}")
                
                # Data quality
                if "data_quality" in result:
                    quality = result["data_quality"]
                    output.append(f"\n🔍 Data Quality:")
                    output.append(f"• Outliers: {quality.get('outlier_count', 'N/A')} ({quality.get('outlier_percentage', 'N/A')}%)")
                    if quality.get("outlier_values") and len(quality["outlier_values"]) > 0:
                        output.append(f"• Outlier values: {quality['outlier_values']}")
                    output.append(f"• {quality.get('quality_note', '')}")
                
                # Variability
                if "variability_analysis" in result:
                    var_analysis = result["variability_analysis"]
                    output.append(f"\n📊 Variability Analysis:")
                    output.append(f"• Coefficient of variation: {var_analysis.get('coefficient_of_variation', 'N/A')}%")
                    output.append(f"• Category: {var_analysis.get('variability_category', 'N/A')}")
                    output.append(f"• {var_analysis.get('variability_note', '')}")
        
        # Format correlation results
        if "correlation" in results:
            corr_result = results["correlation"]
            if "error" not in corr_result:
                output.append(f"\n📈 Correlation Analysis:")
                output.append(f"• Pearson r: {corr_result['correlation_coefficient']} ({corr_result['correlation_note']})")
                output.append(f"• {corr_result['p_value_display']} ({corr_result['p_value_note']})")
                output.append(f"• Direction: {corr_result['direction']}")
                output.append(f"• Strength category: {corr_result['strength_category']} ({corr_result['strength_note']})")
                output.append(f"• R²: {corr_result['r_squared']} ({corr_result['r_squared_note']})")
                output.append(f"• Sample size: {corr_result['sample_size']} ({corr_result['sample_size_note']})")
        
        # Format frequency distribution results
        for key, result in results.items():
            if key.startswith("frequency_") and "error" not in result:
                var_name = result.get("variable_name", key.replace("frequency_", ""))
                output.append(f"\n📊 Frequency Distribution: {var_name}")
                output.append(f"• Total observations: {result.get('total_observations', 'N/A')} ({result.get('total_note', '')})")
                output.append(f"• Unique categories: {result.get('unique_categories', 'N/A')} ({result.get('unique_note', '')})")
                output.append(f"• Mode: {result.get('mode_category', 'N/A')} (count: {result.get('mode_count', 'N/A')}, {result.get('mode_proportion', 'N/A'):.1%})")
                
                # Show frequency table
                frequencies = result.get('frequencies', {})
                if frequencies:
                    output.append(f"\n📈 Category Frequencies:")
                    for category, count in list(frequencies.items())[:10]:  # Show top 10
                        proportion = result.get('proportions', {}).get(category, 0)
                        output.append(f"  {category}: {count} ({proportion:.1%})")
                    if len(frequencies) > 10:
                        output.append(f"  ... and {len(frequencies) - 10} more categories")
                
                # Diversity metrics
                output.append(f"\n🎯 Diversity Metrics:")
                output.append(f"• Shannon entropy: {result.get('entropy', 'N/A')} ({result.get('entropy_note', '')})")
                output.append(f"• Maximum entropy: {result.get('max_entropy', 'N/A')}")
                output.append(f"• Diversity ratio: {result.get('entropy_ratio', 'N/A')} ({result.get('diversity_note', '')})")
        
        # Format chi-square test results
        if "chi_square" in results:
            chi_result = results["chi_square"]
            if "error" not in chi_result:
                output.append(f"\n🔬 Chi-Square Test of Independence:")
                output.append(f"• Test: {chi_result.get('test_type', 'N/A')} ({chi_result.get('test_note', '')})")
                output.append(f"• Variables: {chi_result.get('variable_1', 'N/A')} vs {chi_result.get('variable_2', 'N/A')}")
                output.append(f"• χ² statistic: {chi_result.get('chi_square_statistic', 'N/A')} ({chi_result.get('chi_square_note', '')})")
                output.append(f"• Degrees of freedom: {chi_result.get('degrees_of_freedom', 'N/A')} ({chi_result.get('df_note', '')})")
                output.append(f"• {chi_result.get('p_value_display', 'N/A')} ({chi_result.get('p_value_note', '')})")
                output.append(f"• Effect size (Cramér's V): {chi_result.get('cramers_v', 'N/A')} ({chi_result.get('cramers_v_note', '')})")
                output.append(f"• Association strength: {chi_result.get('effect_size_category', 'N/A')} ({chi_result.get('effect_size_note', '')})")
                output.append(f"• Sample size: {chi_result.get('sample_size', 'N/A')}")
                
                # Show contingency table
                contingency_table = chi_result.get('contingency_table', [])
                categories1 = chi_result.get('categories_1', [])
                categories2 = chi_result.get('categories_2', [])
                
                if contingency_table and categories1 and categories2:
                    output.append(f"\n📋 Contingency Table ({chi_result.get('contingency_note', '')}):")
                    # Header row
                    header = "     " + " ".join(f"{cat:>8}" for cat in categories2)
                    output.append(header)
                    # Data rows
                    for i, cat1 in enumerate(categories1):
                        row_data = " ".join(f"{contingency_table[i][j]:>8}" for j in range(len(categories2)))
                        output.append(f"{cat1:>4} {row_data}")
                
                # Warning about low expected frequencies
                if chi_result.get('warning'):
                    output.append(f"\n⚠️  Warning: {chi_result['warning']}")
        
        # Add interpretation based on output format
        if output_format == "business":
            output.append("\n💼 Business Interpretation:")
            output.append("• Based on statistical analysis results, management should consider significant differences when making strategic decisions")
        elif output_format == "academic":
            output.append("\n🎓 Academic Conclusion:")
            output.append("• Results meet academic publication standards. Consider including effect sizes and confidence intervals in discussion")
        
        return "\n".join(output)
    
    def _format_batch_output(self, results: Dict, output_format: str) -> str:
        """Format batch analysis results with meaningful statistical information"""
        output = []
        output.append("🔬 Batch Statistical Analysis Report")
        output.append("━" * 50)
        
        analysis_count = 0
        
        for key, result in results.items():
            analysis_count += 1
            
            # Descriptive statistics
            if key.startswith("descriptive_"):
                var_name = key.replace("descriptive_", "")
                output.append(f"\n📊 Analysis #{analysis_count}: Descriptive Statistics - {var_name}")
                if isinstance(result, dict) and "error" not in result:
                    output.append(f"   • Sample size: n = {result.get('n', 'N/A')}")
                    output.append(f"   • Mean: {result.get('mean', 'N/A'):.2f}")
                    output.append(f"   • Standard deviation: {result.get('std', 'N/A'):.2f}")
                    output.append(f"   • Range: [{result.get('min', 'N/A'):.2f}, {result.get('max', 'N/A'):.2f}]")
                    if result.get('outliers'):
                        output.append(f"   • Outliers detected: {len(result['outliers'])} values")
                else:
                    output.append(f"   • Error: {result}")
            
            # Correlation analysis
            elif key.startswith("correlation_"):
                var_pair = key.replace("correlation_", "").replace("_", " vs ")
                output.append(f"\n🔗 Analysis #{analysis_count}: Correlation Analysis - {var_pair}")
                if isinstance(result, dict) and "error" not in result:
                    corr_coef = result.get('correlation_coefficient', 'N/A')
                    p_value = result.get('p_value', 'N/A')
                    p_display = result.get('p_value_display', 'N/A')
                    direction = result.get('direction', 'N/A')
                    strength = result.get('strength_category', 'N/A')
                    r_squared = result.get('r_squared', 0)
                    
                    output.append(f"   📊 Results: r = {corr_coef}, {p_display}")
                    output.append(f"   📈 Relationship: {direction}, {strength}")
                    output.append(f"   📏 Variance explained: R² = {r_squared:.3f} ({r_squared*100:.1f}%)")
                    output.append(f"   📋 Sample size: {result.get('sample_size', 'N/A')}")
                else:
                    output.append(f"   • Error: {result}")
            
            # T-test results
            elif key == "t_test":
                output.append(f"\n🧮 Analysis #{analysis_count}: T-Test Analysis")
                if isinstance(result, dict) and "error" not in result:
                    t_stat = result.get('t_statistic', 'N/A')
                    p_value = result.get('p_value', 'N/A')
                    p_display = result.get('p_value_display', f"p = {p_value:.4f}" if isinstance(p_value, (int, float)) else 'N/A')
                    df = result.get('degrees_of_freedom', 'N/A')
                    cohens_d = result.get('cohens_d', 'N/A')
                    effect_category = result.get('effect_size_category', 'N/A')
                    
                    output.append(f"   📊 Results: t({df}) = {t_stat}, {p_display}")
                    output.append(f"   📏 Effect size: Cohen's d = {cohens_d} ({effect_category})")
                    output.append(f"   📈 Mean difference: {result.get('mean_difference', 'N/A')}")
                else:
                    output.append(f"   • Error: {result}")
            
            # Outlier detection
            elif key.startswith("outliers_"):
                var_name = key.replace("outliers_", "")
                output.append(f"\n🎯 Analysis #{analysis_count}: Outlier Detection - {var_name}")
                if isinstance(result, list):
                    if result:
                        output.append(f"   📊 Outliers found: {len(result)} values")
                        output.append(f"   📈 Outlier values: {result}")
                    else:
                        output.append(f"   ✅ No outliers detected")
                else:
                    output.append(f"   • Result: {result}")
            
            # Generic handling for other result types
            else:
                output.append(f"\n📋 Analysis #{analysis_count}: {key}")
                if isinstance(result, dict):
                    for sub_key, sub_value in result.items():
                        output.append(f"   • {sub_key}: {sub_value}")
                else:
                    output.append(f"   • Result: {result}")
        
        # Add summary
        output.append(f"\n📈 BATCH ANALYSIS SUMMARY")
        output.append("─" * 25)
        output.append(f"📊 Total analyses completed: {analysis_count}")
        
        # Count analyses with p-values (without interpretation)
        p_value_count = 0
        for key, result in results.items():
            if isinstance(result, dict) and 'p_value' in result:
                p_value_count += 1
        
        if p_value_count > 0:
            output.append(f"📈 Analyses with p-values: {p_value_count}")
            output.append(f"� Note: p-values indicate probability of observing results if null hypothesis is true")
        
        return "\n".join(output)
    
    def render_report(self, conversation_id: str, report_type: str = "summary") -> str:
        """Generate a comprehensive report of all analyses in the conversation"""
        if conversation_id not in self.conversations:
            return "No analyses found for this conversation."
        
        analyses = self.conversations[conversation_id]["analyses"]
        if not analyses:
            return "No analyses found for this conversation."
        
        output = []
        output.append("📋 Comprehensive Statistical Analysis Report")
        output.append("━" * 60)
        output.append(f"Total analyses conducted: {len(analyses)}")
        output.append(f"Conversation ID: {conversation_id}")
        
        # Section 1: Statistical Summary
        output.append("\n🎯 STATISTICAL SUMMARY")
        output.append("─" * 30)
        
        statistical_findings = []
        correlations_found = []
        group_comparisons = []
        
        for i, analysis in enumerate(analyses, 1):
            results = analysis.get('results', {})
            analysis_type = analysis.get('analysis_type', 'unknown')
            
            # Extract statistical information without interpretation
            if 't_test' in results and 'error' not in results['t_test']:
                t_result = results['t_test']
                p_value = t_result.get('p_value', 1.0)
                effect_size = t_result.get('effect_size_category', 'unknown')
                mean_diff = t_result.get('mean_difference', 0)
                statistical_findings.append(
                    f"Analysis #{i}: t-test p = {p_value:.3f}, effect size = {effect_size}, mean diff = {mean_diff}"
                )
            
            if 'anova' in results and 'error' not in results['anova']:
                anova_result = results['anova']
                p_value = anova_result.get('p_value', 1.0)
                effect_size = anova_result.get('effect_size_category', 'unknown')
                posthoc = anova_result.get('posthoc_comparisons', [])
                group_comparisons.append(
                    f"Analysis #{i}: ANOVA p = {p_value:.3f}, η² category = {effect_size}, {len(posthoc)} pairwise comparisons"
                )
            
            if 'correlation' in results and 'error' not in results['correlation']:
                corr_result = results['correlation']
                r_value = corr_result.get('correlation_coefficient', 0)
                p_value = corr_result.get('p_value', 1.0)
                strength = corr_result.get('strength_category', 'unknown')
                direction = corr_result.get('direction', 'unknown')
                correlations_found.append(
                    f"Analysis #{i}: r = {r_value:.3f}, p = {p_value:.3f}, {direction.lower()} {strength.lower()}"
                )
        
        # Display statistical summary without conclusions
        if statistical_findings or correlations_found or group_comparisons:
            if statistical_findings:
                output.append("� T-test Results:")
                for finding in statistical_findings:
                    output.append(f"  • {finding}")
            
            if correlations_found:
                output.append("� Correlation Results:")
                for correlation in correlations_found:
                    output.append(f"  • {correlation}")
            
            if group_comparisons:
                output.append("👥 Group Comparison Results:")
                for comparison in group_comparisons:
                    output.append(f"  • {comparison}")
        else:
            output.append("• No statistical tests were performed across all analyses")
        
        # Section 2: Detailed Analysis Results
        output.append("\n📊 DETAILED ANALYSIS RESULTS")
        output.append("─" * 40)
        
        for i, analysis in enumerate(analyses, 1):
            output.append(f"\n🔍 Analysis #{i}: {analysis['analysis_type'].replace('_', ' ').title()}")
            
            # Show data overview
            if analysis.get('data'):
                data_vars = list(analysis['data'].keys())
                output.append(f"   Data variables: {', '.join(data_vars)}")
                
                # Show sample sizes
                for var in data_vars:
                    var_data = analysis['data'][var]
                    if isinstance(var_data, list):
                        output.append(f"   • {var}: n = {len(var_data)}, range = [{min(var_data):.2f}, {max(var_data):.2f}]")
            
            if analysis.get('groups'):
                group_names = list(analysis['groups'].keys())
                output.append(f"   Comparison groups: {', '.join(group_names)}")
                
                # Show group sample sizes
                for group in group_names:
                    group_data = analysis['groups'][group]
                    if isinstance(group_data, list):
                        output.append(f"   • {group}: n = {len(group_data)}, mean = {sum(group_data)/len(group_data):.2f}")
            
            # Show key statistical results
            results = analysis.get('results', {})
            
            if 't_test' in results and 'error' not in results['t_test']:
                t_result = results['t_test']
                output.append(f"   📊 Results: t = {t_result.get('t_statistic', 'N/A')}, {t_result.get('p_value_display', 'p = N/A')}")
                output.append(f"   📏 Effect size: {t_result.get('effect_size_category', 'N/A')} (Cohen's d = {t_result.get('cohens_d', 'N/A')})")
                output.append(f"   📈 Mean difference: {t_result.get('mean_difference', 'N/A')}")
            
            if 'anova' in results and 'error' not in results['anova']:
                anova_result = results['anova']
                output.append(f"   📊 Results: F({anova_result.get('df_between', 'N/A')}, {anova_result.get('df_within', 'N/A')}) = {anova_result.get('f_statistic', 'N/A')}")
                output.append(f"   📈 {anova_result.get('p_value_display', 'p = N/A')}")
                output.append(f"   📏 Effect size: {anova_result.get('effect_size_category', 'N/A')} (η² = {anova_result.get('eta_squared', 'N/A')})")
                
                posthoc = anova_result.get('posthoc_comparisons', [])
                if posthoc:
                    output.append(f"   🔍 Post-hoc: {len(posthoc)} pairwise comparisons performed")
            
            if 'correlation' in results and 'error' not in results['correlation']:
                corr_result = results['correlation']
                output.append(f"   📊 Results: r = {corr_result.get('correlation_coefficient', 'N/A')}, {corr_result.get('p_value_display', 'p = N/A')}")
                output.append(f"   📈 Relationship: {corr_result.get('direction', 'N/A')}, {corr_result.get('strength_category', 'N/A')}")
                output.append(f"   📏 Variance explained: R² = {corr_result.get('r_squared', 'N/A')} ({corr_result.get('r_squared', 0)*100:.1f}%)")
                output.append(f"   📋 Sample size: {corr_result.get('sample_size', 'N/A')}")
        
        # Section 3: Statistical Summary
        output.append("\n📈 STATISTICAL SUMMARY")
        output.append("─" * 25)
        
        total_tests = len(statistical_findings) + len(correlations_found) + len(group_comparisons)
        
        # Objective statistical facts only
        output.append(f"📊 Total analyses: {len(analyses)}")
        output.append(f"🧮 Statistical tests performed: {total_tests}")
        
        if statistical_findings:
            output.append(f"📈 T-tests conducted: {len(statistical_findings)}")
        if correlations_found:
            output.append(f"🔗 Correlations calculated: {len(correlations_found)}")
        if group_comparisons:
            output.append(f"👥 Group comparisons performed: {len(group_comparisons)}")
            
        # Effect size summary (without interpretation)
        effect_sizes_reported = 0
        for analysis in analyses:
            results = analysis.get('results', {})
            if 't_test' in results and 'cohens_d' in results.get('t_test', {}):
                effect_sizes_reported += 1
            if 'anova' in results and 'eta_squared' in results.get('anova', {}):
                effect_sizes_reported += 1
                    
        if effect_sizes_reported > 0:
            output.append(f"📏 Effect sizes calculated: {effect_sizes_reported}")
        
        output.append("\n" + "━" * 60)
        output.append("📊 End of Statistical Analysis Report")
        output.append("� Note: All p-values represent probability of observing results if null hypothesis is true")
        
        return "\n".join(output)
