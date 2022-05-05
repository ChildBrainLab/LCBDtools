from os.path import join
import matplotlib
import matplotlib.pyplot as plt
plt.rcParams["figure.figsize"] = (12,8)
# matplotlib.use('TkAgg') # fix for chromebook
import numpy as np


def plot_xy_line(
    x,
    y,
    xlabel="Time",
    ylabel="Amplitude",
    logy=False,
    share=False,
    title=None,
    fig_fname=None,
    labels=None,
    plot_axis=False):
    """
    Inspect a handful of datapoints on a plot of data vs. features
    :param x: values along x-axis
    :type x: np.array with shape (num_features,)
    :param y: values or set of values along y-axis
    :type y: np.array with shape (num_samples, num_features)
    :param xlabel: (Default: Time) label to use on x-axis
    :type xlabel: str
    :param ylabel: (Default: Amplitude) label to use on y-axis
    :type ylabel: str
    :param logy: (Default: False) if True, uses semilogy
    :type logy: bool
    :param share: (Default: True) if True, doesn't use subplots
    :type share: bool
    :param title: (Default: "") Super plot title
    :type title: str
    :param fig_fname: (Default: None) If given value, saves as <fig_fname>.png
    :type fig_fname: str
    :param labels: (Default: None) If given, label for each sample in y
    :type labels: list or np.array with shape / len (num_samples,)
    """

    fig, axs = plt.subplots(
        nrows=(y.shape[0] if share is False and len(y.shape) >= 2 else 1),
        sharex=True,
        sharey=True,
        dpi=100,
        figsize=(12, 8))
    plt.suptitle(title)
    fig.text(0.5, 0.04, xlabel, ha='center')
    fig.text(0.04, 0.5, ylabel, va='center', rotation='vertical')

    for i in range(y.shape[0]):
        if (share is False) and len(y.shape) >= 2:
            obj = axs[i]
        else:
            obj = axs
        if logy is False:
            obj.plot(
                x,
                y[i] if len(y.shape) >= 2 else y,
                label=labels[i] if labels is not None else None)
            if plot_axis is not False:
                obj.plot(
                    plot_axis,
                    '--')

        else:
            obj.semilogy(
                x,
                y[i] if len(y.shape) >= 2 else y,
                label=labels[i] if labels is not None else None)
        if labels is not None:
            obj.legend() # add truth label to each
        if len(y.shape) < 2:
            break

    # plt.ylim([1e-7, 1e2])
    # plt.ylim()

    if fig_fname is not None:
        plt.savefig(
            join(fig_fname+'.png'),
            dpi=100)
        plt.close()
    else:
        plt.show()


def plot_colormesh(
    x,
    xlabel="",
    ylabel="Density",
    yticks=None,
    title="",
    fig_fname=None):
    """
    2D colormesh (e.g. rastor plot)

    :param x: 2D array of data with shape (num_samples, num_features)
    :type x: numpy.array
    :param xlabel: (Default: Time) label to use on x-axis
    :type xlabel: str
    :param ylabel: (Default: Amplitude) label to use on y-axis
    :type ylabel: str
    :param yticks: (Default: None) ticks to use to label individual y spots
    :type yticks: list of str
    :param title: (Default: "") Super plot title
    :type title: str
    :param fig_fname: (Default: None) If given value, saves as <fig_fname>.png
    :type fig_fname: str
    """
    fig, ax = plt.subplots()

    ax.pcolormesh(
        x*255, # make sure to scale it to rgb
        cmap='gray')

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.yticks(
        ticks=[i+1 for i in range(x.shape[0])],
        labels=yticks, rotation=-45)
    plt.title(title)

    if fig_fname is not None:
        plt.savefig(
            join('figures', fig_fname+'.png'),
            dpi=100)
        plt.close()
    else:
        plt.show()


def plot_outcome_hist(
    x,
    y,
    n_bins=20,
    density=True,
    xlabel="",
    ylabel="Density",
    title="",
    fig_fname=None):
    """
    Plot two overlaid histograms, one group with outcome=0, one with outcome=1
    :param x: 1D array of data
    :type x: np.array with shape (num_samples,)
    :param y: 1D array of corresponding outcomes
    :type y: np.array with shape (num_samples,)
    :param n_bins: number of bins to use
    :type n_bins: int
    :param density: (Default: True) Whether to use a density histogram or not
    :type density: bool
    :param xlabel: (Default: Time) label to use on x-axis
    :type xlabel: str
    :param ylabel: (Default: Amplitude) label to use on y-axis
    :type ylabel: str
    :param title: (Default: "") Super plot title
    :type title: str
    :param fig_fname: (Default: None) If given value, saves as <fig_fname>.png
    :type fig_fname: str
    """

    fig, ax = plt.subplots()

    range = (np.amin(x), np.amax(x))

    ax.hist(
        [point for i, point in enumerate(x) if y[i] == 0],
        bins=n_bins,
        range=range,
        color="blue",
        alpha=0.5,
        density=density,
        label="outcome=0")

    ax.hist(
        [point for i, point in enumerate(x) if y[i] == 1],
        bins=n_bins,
        range=range,
        color="red",
        alpha=0.5,
        density=density,
        label="outcome=1")

    plt.legend()
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)

    if fig_fname is not None:
        plt.savefig(
            join(fig_fname+'.png'),
            dpi=100)
        plt.close()
    else:
        plt.show()


def plot_block_diffs(
    blocks,
    truths,
    title=None,
    active_label=1,
    fig_fname=None):
    """
    Show percent of datapoints in each block where truth value is equal
    to active_label
    :param blocks: array of block or meta-values
    :type blocks: np.array with shape (num_samples,)
    :param truths: array of truth labels / ground truth data
    :type truths: np.array with shape (num_samples,)
    :param title: (Default: "") Super plot title
    :type title: str
    :param active_label: (Default: 1) truth_value being counted from truths
    :param fig_fname: (Default: None) If given value, saves as <fig_fname>.png
    :type fig_fname: str
    """

    acts = {}
    counts = {}
    for i, block in enumerate(blocks):
        # add to dicts if not yet encountered
        if block not in counts.keys():
            acts[block] = 0
            counts[block] = 0

        # increment acts if active
        if truths[i] == active_label:
            acts[block] += 1
        counts[block] += 1

    # percent of in each block where a datapoint's truth value
    # is equal to active_label
    activation_rates = [
        (acts[block] / counts[block]*100) \
        for block in counts.keys()]

    plt.bar(
        x=range(len(activation_rates)),
        height=activation_rates)
    plt.xlabel("Block")
    plt.ylabel("% Positive (1) Outcomes")
    plt.title(title)

    if fig_fname is not None:
        plt.savefig(
            join('figures', fig_fname+'.png'),
            dpi=100)
        plt.close()
    else:
        plt.show()

    return acts, counts


def plot_model_history(
    history,
    metric='loss',
    fig_fname=None,
    xlabel="Epoch",
    ylabel="Metric",
    title="",
    ):
    """
    Plots desired metric over course of training
    :param history: fitted model (TF keras)
    :type history: tensorflow.keras.Sequential.fit
    :param metric: metric which will be plotted over epochs
    :type metric: str {'loss', 'accuracy'}
    :param fig_fname: (Default: None) If given value, saves as <fig_fname>.png
    :type fig_fname: str
    :param xlabel: (Default: Time) label to use on x-axis
    :type xlabel: str
    :param ylabel: (Default: Amplitude) label to use on y-axis
    :type ylabel: str
    :param title: (Default: "") Super plot title
    :type title: str
    """
    plt.plot(history.history[metric], label='train '+metric)
    plt.plot(history.history['val_'+metric], label='val '+metric)
    plt.legend()
    plt.grid(True)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)

    if fig_fname is not None:
        plt.savefig(
            join('figures', fig_fname+'.png'),
            dpi=100)
        plt.close()
    else:
        plt.show()


def roc_curve(
    preds,
    truths,
    fig_fname=None):
    """
    Plot ROC curve for given predictions and truth array
    :param preds: list of numpy.array objects, each with a pack of predictions
    :type preds: list
    :param truths: list of truth (outcome) values of type binary classification
    :type truths: numpy.array
    :param fig_fname: (Default: None) If given value, saves as <fig_fname>.png
    :type fig_fname: str
    """
    from sklearn.metrics import roc_curve
    from sklearn.metrics import roc_auc_score

    for i, predset in enumerate(preds):
        fpr, tpr, thresholds = roc_curve(truths, predset)
        # calculate scores
        auc = roc_auc_score(truths, predset)
        # summarize scores
        print('Model: ROC AUC=%.3f' % (auc))
        # calculate roc curves
        fpr, tpr, _ = roc_curve(truths, predset)
        # plot the roc curve for the model
        plt.plot(fpr, tpr, linestyle='--', label="T"+str(i))
    # axis labels
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    # show the legend
    plt.legend()

    if fig_fname is not None:
        plt.savefig(
            join('figures', fig_fname+'.png'),
            dpi=100)
        plt.close()
    else:
        plt.show()
