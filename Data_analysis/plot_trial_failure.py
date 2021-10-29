
import pickle
import statistics
import numpy as np
import csv

# Import packages
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.patches as mpatches
import matplotlib.lines as mlines

mpl.style.use('./aaai.mplstyle')

def trial_ratio_and_failure_ratio(cols, failure_log_pec, failure_log_comp, subtitles, output=None):
    
    # Load pec data
    failure_logs_pec_pkl = []
    for file in failure_log_pec:
        with open(file, "rb") as f:
            failure_logs_pec_pkl.append(pickle.load(f))

    # Load comp data
    failure_logs_comp_pkl = []
    for file in failure_log_comp:
        with open(file, "rb") as f:
            failure_logs_comp_pkl.append(pickle.load(f))

    failure_logs = failure_logs_pec_pkl + failure_logs_comp_pkl
    trial_ratios = np.zeros_like(failure_logs).tolist()
    failure_ratios = np.zeros_like(failure_logs).tolist()

    for i, log in enumerate(failure_logs):
        tries = [v[1] for v in list(failure_logs[i].values())]
        total_tries = sum(tries)
        trial_ratios[i] = [f / total_tries for f in tries]

        failures = [v[0] for v in list(failure_logs[i].values())]
        failure_ratios[i] = [f / t for f, t in zip(failures, tries)]

    avg_trial_ratio = [statistics.mean(trial_ratio) for trial_ratio in trial_ratios]
    std_trial_ratio = [statistics.stdev(trial_ratio) for trial_ratio in trial_ratios]

    avg_failure_ratio = [statistics.mean(failure_ratio) for failure_ratio in failure_ratios]
    std_failure_ratio = [statistics.stdev(failure_ratio) for failure_ratio in failure_ratios]

    #x = [f'({key})' for key in failure_logs[0].keys()]
    x = [f'$c_{{{i}}}$' for i, value in enumerate(failure_logs[0].keys())]

    fig, axes = plt.subplots(nrows=2, ncols=cols)
    #fig.tight_layout(pad=6)
    fig.set_size_inches((24, 8))
    
    ##legends = ['trial ratio (w/ pec)':'#6d904f', 'failure ratio (w/ pec)', ['trial ratio (w/o pec)', 'failure ratio (w/o pec)']]

    #colors = {'fruit':'red', 'veggie':'green'}         
    labels_with_pec = ['Trial Ratio (w/ PEC)', 'Failure Ratio (w/ PEC)']
    labels_without_pec = ['Trial Ratio (w/o PEC)', 'Failure Ratio (w/o PEC)']
    handles = [plt.Rectangle((0,0),1,1, color='#e5ae38'), mlines.Line2D([], [], color='#354885', marker='s', label='failure ratio (w/ pec)'), plt.Rectangle((0,0),1,1, color='#8b8b8b'), mlines.Line2D([], [], color='#810f7c', marker='s', label='failure ratio (w/ pec)')]

    
    for j in range(cols):
        axes[0, j].set_title(f'Iterations: {subtitles[j]}')
        axes[0, j].bar(x, trial_ratios[j], color='#e5ae38')
        ax0_sub = axes[0, j].twinx()
        ax0_sub.plot(x, failure_ratios[j], marker='s', color='#354885')
        ax0_sub.set_ylim([0, 1])

        if j == cols -1:
            ax0_sub.set_ylabel('Failure Ratio')
        else:
            ax0_sub.get_yaxis().set_visible(False)
        
        #axes[0, j].set_xlabel('Coordination Sets')
        if j == 0:
            axes[0, j].set_ylabel('Trial Ratio')
        else:
            axes[0, j].get_yaxis().set_visible(False)

        axes[0, j].set_ylim([0, 0.12])
        axes[0, j].xaxis.set_major_locator(ticker.FixedLocator(range(len(x))))
        axes[0, j].set_xticklabels(x, rotation=45, fontsize='small')
        axes[0, j].get_shared_y_axes().join(axes[0, j], ax0_sub)
        #axes[0, j].legend(handles[0], labels_with_pec)
        
        axes[1, j].bar(x, trial_ratios[j+cols], color='#8b8b8b')
        ax1_sub = axes[1, j].twinx()
        ax1_sub.plot(x, failure_ratios[j+cols], marker='s', color='#810f7c')
        ax1_sub.set_ylim([0, 1])
        if j == cols -1:
            ax1_sub.set_ylabel('Failure Ratio')
        else:
            ax1_sub.get_yaxis().set_visible(False)
        
        axes[1, j].set_xlabel('Coordinates')
        if j == 0:
            axes[1, j].set_ylabel('Trial Ratio')
        else:
            axes[1, j].get_yaxis().set_visible(False)
        axes[1, j].set_ylim([0, 0.12])
        axes[1, j].xaxis.set_major_locator(ticker.FixedLocator(range(len(x))))
        axes[1, j].set_xticklabels(x, rotation=45, fontsize='small')
        axes[1, j].get_shared_y_axes().join(axes[1, j], ax1_sub) 
        #axes[1, j].legend(handles[1], labels_without_pec)      

    
    #plt.suptitle("Trial Ratio and Failure Ratio")
    fig.legend(handles, labels_with_pec + labels_without_pec, loc='lower center',bbox_to_anchor=(0.5, -0.07), ncol=4)
    #plt.tight_layout()
    #plt.legend(fontsize=12, loc='best')
    # Show empty plot
    if not output:
        plt.show()
    else:
        plt.savefig(output, bbox_inches='tight')


def trial_ratio_and_failure_ratio_alpha(failure_log_pec, title, subtitles, output=None):
     # Load pec data
    failure_logs_pec_pkl = []
    cols = len(subtitles)
    for file in failure_log_pec:
        with open(file, "rb") as f:
            failure_logs_pec_pkl.append(pickle.load(f))

    failure_logs = failure_logs_pec_pkl 
    trial_ratios = np.zeros_like(failure_logs).tolist()
    failure_ratios = np.zeros_like(failure_logs).tolist()

    for i, log in enumerate(failure_logs):
        tries = [v[1] for v in list(failure_logs[i].values())]
        total_tries = sum(tries)
        trial_ratios[i] = [f / total_tries for f in tries]

        failures = [v[0] for v in list(failure_logs[i].values())]
        failure_ratios[i] = [f / t for f, t in zip(failures, tries)]

    avg_trial_ratio = [statistics.mean(trial_ratio) for trial_ratio in trial_ratios]
    std_trial_ratio = [statistics.stdev(trial_ratio) for trial_ratio in trial_ratios]

    avg_failure_ratio = [statistics.mean(failure_ratio) for failure_ratio in failure_ratios]
    std_failure_ratio = [statistics.stdev(failure_ratio) for failure_ratio in failure_ratios]

    x = [f'$c_{{{i}}}$' for i, value in enumerate(failure_logs[0].keys())]

    fig, axes = plt.subplots(nrows=1, ncols=cols)
    #fig.tight_layout(pad=6)
    fig.set_size_inches((24, 8))
    
    ##legends = ['trial ratio (w/ pec)':'#6d904f', 'failure ratio (w/ pec)', ['trial ratio (w/o pec)', 'failure ratio (w/o pec)']]

    #colors = {'fruit':'red', 'veggie':'green'}         
    labels_with_pec = ['Trial Ratio (w/ PEC)', 'Failure Ratio (w/ PEC)']
    handles = [plt.Rectangle((0,0),1,1, color='#e5ae38'), mlines.Line2D([], [], color='#354885', marker='s', label='Failure Ratio (w/ PEC)')]
    
    for j in range(cols):
        axes[j].set_title(f'Iterations: {subtitles[j]}', fontsize='small')
        axes[j].bar(x, trial_ratios[j], color='#e5ae38')
        ax0_sub = axes[j].twinx()
        ax0_sub.plot(x, failure_ratios[j], marker='s', color='#354885')
        ax0_sub.set_ylim([0, 1])
        if j == cols -1:
            ax0_sub.set_ylabel('Failure Ratio')
        else:
            ax0_sub.get_yaxis().set_visible(False)
            
        #axes[0, j].set_xlabel('Coordination Sets')
        if j == 0:
            axes[j].set_ylabel('Trial Ratio')
        else:
            axes[j].get_yaxis().set_visible(False)

        axes[j].set_ylim([0, 0.15])
        axes[j].xaxis.set_major_locator(ticker.FixedLocator(range(len(x))))
        axes[j].set_xticklabels(x, rotation=45, fontsize='small')
        axes[j].get_shared_y_axes().join(axes[j], ax0_sub)
        
    
    #plt.suptitle(title)
    fig.legend(handles, labels_with_pec, loc='lower center',bbox_to_anchor=(0.5, -0.07), ncol=4)
    #plt.tight_layout()
    #plt.legend(fontsize=12, loc='best')
    # Show empty plot
    if not output:
        plt.show()
    else:
        plt.savefig(output, bbox_inches='tight')

