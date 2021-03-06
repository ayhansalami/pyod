# -*- coding: utf-8 -*-
"""Example of using LOF for outlier detection
"""
# Author: Yue Zhao <yuezhao@cs.toronto.edu>
# License: BSD 2 clause

from __future__ import division
from __future__ import print_function

import os
import sys

# temporary solution for relative imports in case pyod is not installed
# if pyod is installed, no need to use the following line
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname("__file__"), '..')))

import numpy as np

from sklearn.utils.validation import check_X_y
from sklearn.utils.validation import column_or_1d
from sklearn.utils.validation import check_consistent_length
import matplotlib.pyplot as plt

from pyod.models.lof import LOF
from pyod.utils.data import generate_data
from pyod.utils.data import evaluate_print


def _add_sub_plot(X_inliers, X_outliers, sub_plot_title,
                  inlier_color='blue', outlier_color='orange'):
    """Internal method to add subplot of inliers and outliers

    Parameters
    ----------
    X_inliers : numpy array of shape (n_samples, n_features)
        Outliers.

    X_outliers : numpy array of shape (n_samples, n_features)
        Inliers.

    sub_plot_title : str
        Subplot title.

    inlier_color : str, optional (default='blue')
        The color of inliers.

    outlier_color : str, optional (default='orange')
        The color of outliers.

    """
    plt.axis("equal")
    plt.scatter(X_inliers[:, 0], X_inliers[:, 1], label='inliers',
                color=inlier_color, s=40)
    plt.scatter(X_outliers[:, 0], X_outliers[:, 1],
                label='outliers', color=outlier_color, s=50, marker='^')
    plt.title(sub_plot_title, fontsize=15)
    plt.xticks([])
    plt.yticks([])
    plt.legend(loc=4, prop={'size': 10})


def _get_sample_indices(X, y):
    """Internal method to separate inliers from outliers.

    Parameters
    ----------
    X : numpy array of shape (n_samples, n_features)
        The input samples

    y : list or array of shape (n_samples,)
        The ground truth of input samples.

    Returns
    -------
    X_outliers : numpy array of shape (n_samples, n_features)
        Outliers.

    X_inliers : numpy array of shape (n_samples, n_features)
        Inliers.

    """
    X_outliers = X[np.where(y == 1)]
    X_inliers = X[np.where(y == 0)]
    return X_outliers, X_inliers


def visualize(clf_name, X_train, y_train, X_test, y_test, y_train_pred,
              y_test_pred, show_figure=True, save_figure=False):
    """Utility function for visualizing the results in examples.
    Internal use only.

    Parameters
    ----------
    clf_name : str
        The name of the detector.

    X_train : numpy array of shape (n_samples, n_features)
        The training samples.

    y_train : list or array of shape (n_samples,)
        The ground truth of training samples.

    X_test : numpy array of shape (n_samples, n_features)
        The test samples.

    y_test : list or array of shape (n_samples,)
        The ground truth of test samples.

    y_train_pred : numpy array of shape (n_samples, n_features)
        The predicted binary labels of the training samples.

    y_test_pred : numpy array of shape (n_samples, n_features)
        The predicted binary labels of the test samples.

    show_figure : bool, optional (default=True)
        If set to True, show the figure.

    save_figure : bool, optional (default=False)
        If set to True, save the figure to the local

    Returns
    -------

    """
    # check input data shapes are consistent
    X_train, y_train = check_X_y(X_train, y_train)
    X_test, y_test = check_X_y(X_test, y_test)

    y_test_pred = column_or_1d(y_test_pred)
    y_train_pred = column_or_1d(y_train_pred)

    if X_train.shape[1] != 2 or X_test.shape[1] != 2:
        raise ValueError("Input data has to be 2-d for visualization. The "
                         "input data has {shape}.".format(shape=X_train.shape))
    check_consistent_length(y_train, y_train_pred)
    check_consistent_length(y_test, y_test_pred)

    X_train_outliers, X_train_inliers = _get_sample_indices(X_train, y_train)
    X_train_outliers_pred, X_train_inliers_pred = _get_sample_indices(
        X_train, y_train_pred)

    X_test_outliers, X_test_inliers = _get_sample_indices(X_test, y_test)
    X_test_outliers_pred, X_test_inliers_pred = _get_sample_indices(
        X_test, y_test_pred)

    # plot ground truth vs. predicted results
    fig = plt.figure(figsize=(12, 10))
    plt.suptitle("Demo of {clf_name}".format(clf_name=clf_name), fontsize=15)

    fig.add_subplot(221)
    _add_sub_plot(X_train_inliers, X_train_outliers, 'Train set ground truth',
                  inlier_color='blue', outlier_color='orange')

    fig.add_subplot(222)
    _add_sub_plot(X_train_inliers_pred, X_train_outliers_pred,
                  'Train set prediction', inlier_color='blue',
                  outlier_color='orange')

    fig.add_subplot(223)
    _add_sub_plot(X_test_inliers, X_test_outliers, 'Test set ground truth',
                  inlier_color='green', outlier_color='red')

    fig.add_subplot(224)
    _add_sub_plot(X_test_inliers_pred, X_test_outliers_pred,
                  'Test set prediction', inlier_color='green',
                  outlier_color='red')

    if save_figure:
        plt.savefig('{clf_name}.png'.format(clf_name=clf_name), dpi=300)

    if show_figure:
        plt.show()

    return


if __name__ == "__main__":
    contamination = 0.1  # percentage of outliers
    n_train = 200  # number of training points
    n_test = 100  # number of testing points

    # Generate sample data
    X_train, y_train, X_test, y_test = \
        generate_data(n_train=n_train,
                      n_test=n_test,
                      n_features=2,
                      contamination=contamination,
                      random_state=42)

    # train LOF detector
    clf_name = 'LOF'
    clf = LOF()
    clf.fit(X_train)

    # get the prediction labels and outlier scores of the training data
    y_train_pred = clf.labels_  # binary labels (0: inliers, 1: outliers)
    y_train_scores = clf.decision_scores_  # raw outlier scores

    # get the prediction on the test data
    y_test_pred = clf.predict(X_test)  # outlier labels (0 or 1)
    y_test_scores = clf.decision_function(X_test)  # outlier scores

    # evaluate and print the results
    print("\nOn Training Data:")
    evaluate_print(clf_name, y_train, y_train_scores)
    print("\nOn Test Data:")
    evaluate_print(clf_name, y_test, y_test_scores)

    # visualize the results
    visualize(clf_name, X_train, y_train, X_test, y_test, y_train_pred,
              y_test_pred, show_figure=True, save_figure=True)
