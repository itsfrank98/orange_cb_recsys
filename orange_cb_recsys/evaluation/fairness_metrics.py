from collections import Counter

import pandas as pd
import numpy as np
from orange_cb_recsys.evaluation.delta_gap import *
from orange_cb_recsys.evaluation.utils import *
import matplotlib.pyplot as plt


# fairness_metrics_results = pd.DataFrame(columns=["user", "gini-index", "delta-gaps", "pop_ratio_profile_vs_recs", "pop_recs_correlation", "recs_long_tail_distr"])


def perform_gini_index(score_frame: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate Gini index score for each user in the DataFrame
    Args:
        score_frame (pd.DataFrame): frame wich stores ('from_id', 'to_id', 'rating')

    Returns:
        results (pd.DataFrame): each row contains ('from_id', 'gini_index')
    """

    def gini(array: np.array):
        """Calculate the Gini coefficient of a numpy array."""

        array = array.flatten()  # all values are treated equally, arrays must be 1d
        if np.amin(array) < 0:
            array += 1
        array += 0.0000001  # values cannot be 0
        array = np.sort(array)  # values must be sorted
        index = np.arange(1, array.shape[0] + 1)  # index per array element
        n = array.shape[0]  # number of array elements
        return (np.sum((2 * index - n - 1) * array)) / (n * np.sum(array))  # Gini coefficient

    score_dict = {}
    # for each user extract a pd.DataFrame df
    for idx, df in score_frame.groupby('from_id'):
        # from the DataFrame exract the 'rating' column as a np.array and create a Gini_index
        # store the score in a dict
        score_dict[df['from_id'].iloc[0]] = gini(df['rating'].to_numpy())
    results = pd.DataFrame({'from': list(score_dict.keys()), 'gini-index': list(score_dict.values())})

    return results


def perform_delta_gap(score_frame: pd.DataFrame, truth_frame: pd.DataFrame,
                      users_groups: Dict[str, Set[str]]) -> pd.DataFrame:
    """
    Compute the Delta - GAP (Group Average Popularity) metric
    Args:
        truth_frame (pd.DataFrame): frame wich stores ('from_id', 'to_id', 'rating') of user profiles
        score_frame (pd.DataFrame): frame wich stores ('from_id', 'to_id', 'rating') recommended
        users_groups (Dict[str, Set[str]]): each key contains the name of the group and each value the set of 'from_id'
    Returns:
        results (pd.DataFrame): each row contains ('from_id', 'delta-gap')
    """

    items = score_frame[['to_id']].values.flatten()
    pop_by_items = Counter(items)
    avg_pop_by_users_profiles = get_avg_pop_by_users(truth_frame, pop_by_items)  # truth?
    recs_avg_pop_by_users = get_avg_pop_by_users(score_frame, pop_by_items)

    recommended_users = set(truth_frame[['from_id']].values.flatten())

    score_frame = pd.DataFrame(columns=['user_group', 'delta-gap'])
    for group_name in users_groups:
        recs_gap = calculate_gap(group=users_groups[group_name].intersection(recommended_users), avg_pop_by_users=recs_avg_pop_by_users)
        profile_gap = calculate_gap(group=users_groups[group_name], avg_pop_by_users=avg_pop_by_users_profiles)
        group_delta_gap = calculate_delta_gap(recs_gap=recs_gap, profile_gap=profile_gap)
        score_frame = score_frame.append(pd.DataFrame({'user_group': [group_name], 'delta-gap': [group_delta_gap]}),
                                         ignore_index=True)
    # plot
    return score_frame


def perform_pop_ratio_profile_vs_recs(user_groups: Dict[str, Set[str]], truth_frame: pd.DataFrame,
                                      most_popular_items: pd.Series, pop_ratio_by_users: pd.DataFrame,
                                      algorithm_name: str, out_dir: str, store_frame: bool = False) -> pd.DataFrame:
    """

    Args:
        store_frame:
        out_dir:
        algorithm_name:
        user_groups:
        truth_frame:
        most_popular_items:
        pop_ratio_by_users:

    Returns:

    """
    truth_frame = truth_frame[['from_id', 'to_id']]
    score_frame = pd.DataFrame(columns=['user_group', 'profile_pop_ratio', 'recs_pop_ratio'])
    for group_name in user_groups:
        profile_pop_ratios = get_profile_pop_ratios(user_groups[group_name], pop_ratio_by_users)
        recs_pop_ratios = get_recs_pop_ratios(user_groups[group_name], truth_frame, most_popular_items)
        score_frame = score_frame.append(pd.DataFrame({'user_group': [group_name],
                                                       'profile_pop_ratio': [profile_pop_ratios],
                                                       'recs_pop_ratio': [recs_pop_ratios]}), ignore_index=True)
    if store_frame:
        pass

    # plot

    return score_frame


def perform_pop_recs_correlation(recs: pd.DataFrame, algorithm_name: str, ratings: pd.DataFrame,
                                 plot_file_name: str = None):
    """

    Args:
        recs:
        algorithm_name:
        ratings:
        plot_file_name:

    Returns:

    """
    def build_plot(popularities, recommendations, algorithm_name, plot_file_name):
        """ """
        plt.scatter(popularities, recommendations, marker='o', s=20, c='orange', edgecolors='black', linewidths=0.05)
        plt.title('{}'.format(algorithm_name))
        plt.xlabel('Popularity')
        plt.ylabel('Recommendation frequency')
        plt.savefig('results/plots/pop-recs/{}.svg'.format(plot_file_name))
        plt.clf()

    ####################### Calculating popularity by item ########################
    items = ratings[['item']].values.flatten()
    pop_by_items = Counter(items)

    #################### Calculating num of recommendations by item ###############
    pop_by_items = pop_by_items.most_common()
    recs_by_item = Counter(recs[['item']].values.flatten())
    popularities = list()
    recommendations = list()
    popularities_no_zeros = list()
    recommendations_no_zeros = list()

    at_least_one_zero = False
    for item, pop in pop_by_items:
        num_of_recs = recs_by_item[item]

        popularities.append(pop)
        recommendations.append(num_of_recs)

        if num_of_recs != 0:
            popularities_no_zeros.append(pop)
            recommendations_no_zeros.append(num_of_recs)
        else:
            at_least_one_zero = True

    build_plot(popularities, recommendations,
               algorithm_name, plot_file_name)

    if at_least_one_zero:
        build_plot(popularities_no_zeros, recommendations_no_zeros,
                   algorithm_name, plot_file_name + '-no-zeros')


def perform_recs_long_tail_distr(recs: pd.DataFrame, algorithm_name: str, output_dir: str ,plot_file_name: str = None):
    """

    Args:
        recs:
        algorithm_name:
        output_dir:
        plot_file_name:

    Returns:

    """
    counts_by_item = Counter(recs[['item']].values.flatten())
    ordered_item_count_pairs = counts_by_item.most_common()

    ordered_counts = list()
    for item_count_pair in ordered_item_count_pairs:
        ordered_counts.append(item_count_pair[1])

    if plot_file_name is None:
        plot_file_name = algorithm_name

    plt.plot(ordered_counts)
    plt.title('{}'.format(algorithm_name))
    plt.ylabel('Num of recommendations')
    plt.xlabel('Recommended items')
    plt.savefig('{}/recs-long-tail-distr/{}.svg'.format(output_dir, plot_file_name))
    plt.clf()


# va aggiunto algorithm name a tutti
def catalog_coverage(score_frame: pd.DataFrame, truth_frame: pd.DataFrame):
    """

    Args:
        score_frame:
        truth_frame:

    Returns:

    """
    items = set(truth_frame[['to_id']].values.flatten())
    covered_items = set(score_frame[['to_id']].values.flatten())
    coverage_percentage = len(covered_items) / len(items) * 100

    print('Covered items: ', len(covered_items), ' ({}%)'.format(coverage_percentage))
    return coverage_percentage
