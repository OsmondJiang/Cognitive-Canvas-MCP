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
                return "descriptive_analysis"
            elif len(data) >= 2:
                return "correlation_analysis"
        
        return "descriptive_analysis"
    
    def _calculate_descriptive_stats(self, values: List[float]) -> Dict:
        """Calculate descriptive statistics for a dataset"""
        if not values:
            return {"error": "No data provided"}
        
        try:
            values = [float(v) for v in values]
            n = len(values)
            mean = statistics.mean(values)
            
            result = {
                "n": n,
                "mean": round(mean, 2),
                "median": round(statistics.median(values), 2),
                "std": round(statistics.stdev(values), 2) if n > 1 else 0,
                "min": min(values),
                "max": max(values)
            }
            
            if n >= 4:
                q1 = self._percentile(values, 25)
                q3 = self._percentile(values, 75)
                iqr = q3 - q1
                result.update({
                    "q1": round(q1, 2),
                    "q3": round(q3, 2),
                    "iqr": round(iqr, 2)
                })
                
                # Outlier detection using IQR method
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                outliers = [v for v in values if v < lower_bound or v > upper_bound]
                if outliers:
                    result["outliers"] = outliers
            
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
                    output.append(f"• Sample size: {stats['n']}")
                    output.append(f"• Mean: {stats['mean']}")
                    output.append(f"• Median: {stats['median']}")
                    output.append(f"• Standard deviation: {stats['std']}")
                    output.append(f"• Range: [{stats['min']}, {stats['max']}]")
                    
                    if "outliers" in stats:
                        output.append(f"• Outliers: {stats['outliers']}")
        
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
