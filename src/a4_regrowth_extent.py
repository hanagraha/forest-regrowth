# -------------------------------------------------------------------------
# IMPORT PACKAGES AND READ DATA
# -------------------------------------------------------------------------
# Packages
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
import matplotlib.colors as mcolors

# Read stehman output
zhang = pd.read_csv("data/stehman/trajectory/zhang_stats.csv")
potapov = pd.read_csv("data/stehman/trajectory/potapov_stats.csv")
mapbiomas = pd.read_csv("data/stehman/trajectory/mapbiomas_stats.csv")

# Combine statistics
stats = pd.concat([
    zhang.assign(product='GLC_FCS30D'),
    potapov.assign(product='GLAD LC'),
    mapbiomas.assign(product='MapBiomas'),
])

# Calculate error ratios
stats['error_ratio'] = stats['ce'] / stats['oe']
stats[stats['class']=='Forest Loss']['oe']

# Build color map
blue_cmap = mcolors.LinearSegmentedColormap.from_list("muted_blue", ["#DEF4FF", "#332288"])


# -------------------------------------------------------------------------
# DEFINE FUNCTIONS FOR PLOTTING
# -------------------------------------------------------------------------
# Define function to plot commission and omission errors
def comomplot(df, filename):

    # Get x locations
    x = np.arange(len(df))

    # Inialize figure
    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot commission error
    ax.errorbar(x - 0.1, df['ce'], yerr=df['se_uace'], fmt='o', capsize=4, 
        color='#882255', label="Commission Error", markersize=10, 
        linewidth=2, elinewidth=2)

    # Plot omission error
    ax.errorbar(x + 0.1, df['oe'], yerr=df['se_paoe'], fmt='o', capsize=4, 
        color='#88CCEE', label="Omission Error", markersize=10, 
        linewidth=2, elinewidth=2)

    # Adjust x ticks and axes
    ax.set_xticks(x)
    ax.set_xticklabels(df['product'], rotation=0, ha='center', fontsize=14)

    # Adust y ticks and axes
    ax.set_ylabel('Error', fontsize=14)
    ax.tick_params(axis='y', labelsize=14)

    # Add legend
    ax.legend(fontsize=14, loc='upper right')

    # Add gridlines
    ax.yaxis.grid(linestyle='--', alpha=0.6, zorder=0)

    # Remove spines
    for spine in ax.spines.values():
        spine.set_visible(False)

    # Tight layout and save
    plt.tight_layout()
    plt.savefig(f'data/figures/{filename}.png', dpi=300, bbox_inches='tight')
    print(f'figure saved to data/figures/{filename}.png')
    plt.close(fig)


# -------------------------------------------------------------------------
# PLOT TRAJECTORY ERRORS (SUPPLEMENTARY)
# -------------------------------------------------------------------------
# Define function to subset errors
def subset(df, label):

    # Subset based on class
    subset = df[df['class']==label][['product', 'ce', 'oe', 
    'se_uace', 'se_paoe']].reset_index(drop=True)

    return subset

# Plot forest gain results
gain = subset(stats, 'Forest Gain')
comomplot(gain, "supplementary/errors_forestgain")

# Plot forest loss results
loss = subset(stats, 'Forest Loss')
comomplot(loss, "supplementary/errors_forestloss")

# Plot stable forest results
sf = subset(stats, "Stable Forest")
comomplot(sf, "supplementary/errors_stableforest")

# Plot stable nonforest results
snf = subset(stats, "Stable Non-Forest")
comomplot(snf, "supplementary/errors_stablenonforest")


# -------------------------------------------------------------------------
# PLOT OVERALL ERRORS (MAIN)
# -------------------------------------------------------------------------
# Get overall accuracies
overall = stats[['product', 'oa', 'se_oa']].drop_duplicates().reset_index(drop=True)
overall['oa'] = 1 - overall['oa']

# Get x locations
x = np.arange(len(overall))

# Inialize figure
fig, ax = plt.subplots(figsize=(6, 6))

# Add overall accuracies
ax.errorbar(x - 0.1, overall['oa'], yerr=overall['se_oa'], fmt='o',
    capsize=4, color='#545454', label="Overall Error (1 - Overall Accuracy)", 
    markersize=10, linewidth=2, elinewidth=2)

# Adjust x ticks and axes
ax.set_xticks(x)
ax.set_xticklabels(overall['product'], rotation=0, ha='center', fontsize=14)

# Adust y ticks and axes
ax.set_ylabel('Error', fontsize=14)
ax.tick_params(axis='y', labelsize=14)

# Add legend
ax.legend(fontsize=12, loc='lower center', bbox_to_anchor=(0.5, 1.01), frameon=True)

# Add gridlines
ax.yaxis.grid(linestyle='--', alpha=0.6, zorder=0)

# Remove spines
for spine in ax.spines.values():
    spine.set_visible(False)

# Tight layout and save
plt.tight_layout()
plt.savefig('data/figures/main/overall_errors.png', dpi=300, bbox_inches='tight')
print('figure saved to data/figures/main/overall_errors.png')
plt.close(fig)


# -------------------------------------------------------------------------
# PLOT GAIN + LOSS ERRORS (MAIN)
# -------------------------------------------------------------------------
# Get x locations
x = np.arange(len(gain))

# Initialize figure
fig, ax = plt.subplots(figsize=(10, 6))

# Offsets: group CE pair and OE pair separately, tight within each pair
d = 0.06  # tight spacing within a gain/loss pair
gap = 0.1  # spacing between CE group and OE group

ce_gain_x = x - gap - d/2
ce_loss_x = x - gap + d/2
oe_gain_x = x + gap - d/2
oe_loss_x = x + gap + d/2

# Commission error (CE) - gain (filled) vs loss (open)
ax.errorbar(ce_gain_x, gain['ce'], yerr=gain['se_uace'], fmt='o',
    capsize=4, color='#88CCEE', label="Commission Error (Forest Gain)",
    markersize=10, linewidth=2, elinewidth=2)
ax.errorbar(ce_loss_x, loss['ce'], yerr=loss['se_uace'], fmt='o',
    capsize=4, color='#882255', markersize=10, linewidth=2, elinewidth=2,
    label="Commission Error (Forest Loss)")

# Omission error (OE) - gain (filled) vs loss (open)
ax.errorbar(oe_gain_x, gain['oe'], yerr=gain['se_paoe'], fmt='o',
    capsize=4, color='#88CCEE', label="Omission Error (Forest Gain)",
    markersize=10, linewidth=2, elinewidth=2, markerfacecolor='white',)
ax.errorbar(oe_loss_x, loss['oe'], yerr=loss['se_paoe'], fmt='o',
    capsize=4, color='#882255', markerfacecolor='white',
    label="Omission Error (Forest Loss)", markersize=10, linewidth=2, elinewidth=2)

# Adjust x ticks
ax.set_xticks(x)
ax.set_xticklabels(gain['product'], rotation=0, ha='center', fontsize=14)

# Adjust y ticks and labels
ax.set_ylabel('Error', fontsize=14)
ax.set_ylim(0.1, 0.8)
ax.set_yticks(np.arange(0.1, 0.81, 0.1))
ax.tick_params(axis='y', labelsize=14)

# Add legend
ax.legend(fontsize=12, loc='lower center', bbox_to_anchor=(0.5, 1.02),
          ncol=2, frameon=True, markerscale=0.7)

# Add gridlines
ax.yaxis.grid(linestyle='--', alpha=0.6, zorder=0)

# Remove spines
for spine in ax.spines.values():
    spine.set_visible(False)

# Tight layout and save
plt.tight_layout()
plt.savefig('data/figures/main/change_errors.png', dpi=300, bbox_inches='tight')
print('figure saved to data/figures/main/change_errors.png')
plt.close(fig)


# -------------------------------------------------------------------------
# PLOT AREA ESTIMATE CONFUSION MATRICES (SUPPLEMENTARY)
# -------------------------------------------------------------------------
# Read strata area (s america)
sa_strataarea = pd.read_csv("data/map/areaha_strata.csv").iloc[:, 1:3]
sa_strataarea = sa_strataarea.set_index("class")["area"]
sa_mha = sa_strataarea.sum() / 1e6

# Define function to read confusion matrices
def readcm(filename):

    # Read confusion matrix
    cm = pd.read_csv(f"data/stehman/trajectory/{filename}.csv").iloc[:-1, :-1]

    # Set index
    cm = cm.set_index(cm.columns[0])
    cm.index.name = None

    # Drop empty rows and columns
    cm = cm.dropna(axis=1, how='all').dropna(axis=0, how='all')

    # Convert to mha
    for col in cm.columns:
        cm[col] = cm[col] * sa_mha

    def replace_spaces(label):
        words = label.split(' ')
        result = words[0]
        for word in words[1:]:
            sep = ' ' if len(word) <= 3 else '\n'
            result += sep + word
        return result

    # Adjust labels for plotting
    cm.index = cm.index.map(replace_spaces)
    cm.columns = cm.columns.map(replace_spaces)

    return cm.sort_index(axis=0).sort_index(axis=1)

# Read confusion matrices with area estimates (matched labels)
zhang = readcm("zhang_cm")
potapov = readcm("potapov_cm")
mapbiomas = readcm("mapbiomas_cm")

# Define function to plot confusion matrices
def plotcm(cm, xlab, ylab, filename, size=(10, 10), dfs='.0f'):

    # Initialize figure
    fig, ax = plt.subplots(figsize=size)

    # Build masks: error rows and error columns
    error_rows = cm.index.str.contains('Error') | cm.index.str.contains('all', case=False)
    error_cols = cm.columns.str.contains('Error') | cm.columns.str.contains('all', case=False)
    error_mask = np.outer(error_rows, np.ones(len(cm.columns), dtype=bool)) | \
                 np.outer(np.ones(len(cm.index), dtype=bool), error_cols)

    # Plot main cells
    sns.heatmap(cm, annot=True, fmt=dfs, cmap=blue_cmap, linewidths=0.5,
        ax=ax, cbar=False, annot_kws={"size": 18}, mask=error_mask)

    # Format error cells
    grey_cmap = mcolors.LinearSegmentedColormap.from_list('grey', ['#d3d3d3', '#d3d3d3'])
    annot_error = cm.copy().astype(object)
    for i, row in enumerate(cm.index):
        for j, col in enumerate(cm.columns):
            if error_rows[i] or error_cols[j]:
                val = cm.iloc[i, j]
                annot_error.iloc[i, j] = f'{float(val):.2f}' if pd.notna(val) else ''
            else:
                annot_error.iloc[i, j] = ''

    # Plot error cells (if exists)
    if error_mask.any():
        sns.heatmap(cm, annot=annot_error, fmt='', cmap=grey_cmap, linewidths=0.5,
            ax=ax, cbar=False, annot_kws={"size": 18}, mask=~error_mask,
            vmin=0, vmax=1)

    # Adjust axis ticks and labels
    ax.xaxis.tick_top()
    ax.xaxis.set_label_position('top')
    ax.set_xlabel(xlab, fontsize=16, labelpad=10)
    ax.set_ylabel(ylab, fontsize=16)
    ax.tick_params(axis='x', rotation=0)
    ax.tick_params(axis='y', rotation=0)

    # Tight layout and save
    plt.tight_layout()
    plt.savefig(f'data/figures/supplementary/{filename}.png', dpi=300)
    print(f'figure saved to data/figures/supplementary/{filename}.png')
    plt.close(fig)

# Define function to calculate omission and commission errors
def comom(df):

    # Create copy and calculate errors
    df = df.copy()
    commission = df.apply(lambda row: (row.sum() - row[row.name]) / row.sum(), axis=1)
    omission = df.apply(lambda col: (col.sum() - col[col.name]) / col.sum(), axis=0)

    # Addign to dataframe
    df['Commission\nError'] = commission
    df.loc['Omission\nError'] = omission
    
    return df

# Calculate errors
zhang_comom = comom(zhang)
potapov_comom = comom(potapov)
mapbiomas_comom = comom(mapbiomas)

# Plot confusion matrices (matched labels + errors)
plotcm(zhang_comom, 'Trajectory', 'GLC_FCS30D', 'areacm_zhang_matched', size=(10, 6), dfs='.2f')
plotcm(potapov_comom, 'Trajectory', 'GLAD LC', 'areacm_potapov_matched', size=(10, 6), dfs='.2f')
plotcm(mapbiomas_comom, 'Trajectory', 'MapBiomas', 'areacm_mapbiomas_matched', size=(10, 6), dfs='.2f')


# -------------------------------------------------------------------------
# PLOT SAMPLE COUNT CONFUSION MATRICES (SUPPLEMENTARY)
# -------------------------------------------------------------------------
# Read samples
sampledata = pd.read_csv('data/samples/fd30ref_SA_labels.csv')

# Define function for exporting pivot tables
def pivotdata(df, index, column):

    # Create pivot table
    pivot = df.pivot_table(index=index, columns=column, values='FID', aggfunc='count')

    # Reorder index and columns
    pivot = pivot.reindex(columns=['Stable Forest', 'Stable Non-Forest', 
        'Degraded Forest', 'Deforested Land', 'Secondary Forest', 
        'Afforested Land', 'Forest Plantations'])

    def replace_spaces(label):
        words = label.split(' ')
        result = words[0]
        for word in words[1:]:
            sep = ' ' if len(word) <= 3 else '\n'
            result += sep + word
        return result
    
    # Adjust labels for plotting
    pivot.index = pivot.index.map(replace_spaces)
    pivot.columns = pivot.columns.map(replace_spaces)

    return pivot

# Pivot trajectories (original labels)
zhang_traj = pivotdata(sampledata, 'zhang', 'traj')
potapov_traj = pivotdata(sampledata, 'potapov', 'traj')
mapbiomas_traj = pivotdata(sampledata, 'mapbiomas', 'traj')

# Plot
plotcm(zhang_traj, 'Trajectory', 'GLC_FCS30D', 'samplecm_zhang', size=(10, 6))
plotcm(potapov_traj, 'Trajectory', 'GLAD LC', 'samplecm_potapov', size=(10, 6))
plotcm(mapbiomas_traj, 'Trajectory', 'MapBiomas', 'samplecm_mapbiomas', size=(10, 6))