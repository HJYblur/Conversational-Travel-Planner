from scipy.stats import ttest_rel, wilcoxon

# Data condition 1
condition_1_factor_2 = [
    5, 4.666666667, 4.333333333, 4.666666667, 4.333333333, 4, 3.666666667, 4.666666667, 4.333333333, 3.666666667, 4.333333333, 4.333333333, 5, 4.333333333, 3.666666667, 4.333333333, 4.333333333, 4.333333333, 4.333333333, 4, 3.666666667, 3, 3, 4.666666667, 3, 5, 4.666666667, 4.333333333, 4.666666667, 4.333333333
]
condition_1_factor_3 = [
    4.5, 3.5, 3.75, 3.75, 4, 3.25, 3.75, 4.5, 5, 3.75, 4, 4.75, 4.75, 4.25, 4, 5, 4.75, 4.25, 4.25, 4.75, 4, 2.25, 2.75, 4.5, 2.75, 3.5, 4.5, 4.5, 4, 4
]
condition_1_factor_5 = [
    3, 4, 4, 4, 5, 4, 4, 2, 4, 4, 3, 3, 2, 3, 2, 3, 5, 2, 2, 4, 3, 2, 3, 3, 3, 3, 5, 4, 3, 3
]

# Data condition 2
condition_2_factor_2 = [
    4.333333333, 3.666666667, 3.666666667, 4.333333333, 5, 4.333333333, 3.333333333, 4.333333333, 4.333333333, 4, 4.666666667, 2.666666667, 3.666666667, 4.333333333, 4.333333333, 4.666666667, 4.333333333, 2.666666667, 4, 2.666666667, 1.666666667, 3.666666667, 4.333333333, 4.666666667, 4.333333333, 4.666666667, 5, 4.666666667, 3.666666667, 3.333333333
]
condition_2_factor_3 = [
    4, 2, 3.25, 3, 4.75, 4, 3.25, 4.5, 4.75, 4, 4.25, 3.75, 4.25, 4, 4.5, 4.25, 3.25, 4.25, 2.25, 4.25, 2.5, 3.25, 2.5, 4.25, 3.25, 4, 4.75, 3, 2.75, 4.75
]
condition_2_factor_5 = [
    3, 5, 4, 4, 5, 3, 3, 3, 4, 4, 4, 4, 3, 4, 2, 4, 5, 2, 2, 4, 3, 3, 3, 4, 3, 3, 5, 4, 4, 2
]

# One-tailed paired t-test
print("Factor 2:")
t_stat, p_value = ttest_rel(condition_1_factor_2, condition_2_factor_2, alternative='greater')
print("t_stat:", t_stat)
print("p_value:", p_value)
print()

print("Factor 3:")
t_stat, p_value = ttest_rel(condition_1_factor_3, condition_2_factor_3, alternative='greater')
print("t_stat:", t_stat)
print("p_value:", p_value)
print()

# One-tailed Wilcoxon signed-rank test
print("Factor 5:")
res = wilcoxon(condition_1_factor_5, condition_2_factor_5, alternative='less')
print("stat:", res.statistic)
print("p-value:", res.pvalue)