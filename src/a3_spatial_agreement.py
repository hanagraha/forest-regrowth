# -------------------------------------------------------------------------
# IMPORT PACKAGES AND CHECK DIRECTORY
# -------------------------------------------------------------------------
# Packages
from pathlib import Path
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
import matplotlib.colors as mcolors
from matplotlib_venn import venn3, venn3_circles

# Build color map and palette
blue_cmap = mcolors.LinearSegmentedColormap.from_list("muted_blue", ["#DEF4FF", "#332288"])
colors = {'100': '#999933', '010': '#88CCEE', '001': '#CC6677', 
    '110': '#B8DD88', '101': '#BBAA55', '011': '#AABBCC', '111': '#EEF9FF'}

# Create figures folders if needed
for sub in ("main", "supplementary"):
    folder = Path("data/figures", sub)
    if not folder.exists():
        folder.mkdir(parents=True)
        print(f"created folder {folder}")


# -------------------------------------------------------------------------
# CALCULATE SPATIAL AGREEMENT
# -------------------------------------------------------------------------
# Read agreement matrix
agreement_matrix = pd.read_csv("data/map/areaha_spatialagreement.csv").iloc[:, 1:-1]

# Define function to extract confusion matrix values
def agextract(df):
    extract = df.copy()
    extract['area'] = extract['area']/1e6
    extract['mapbiomas'] = extract['class'].astype(str).str[0].astype(int)
    extract['zhang'] = extract['class'].astype(str).str[1].astype(int)
    extract['potapov'] = extract['class'].astype(str).str[2].astype(int)
    return extract

# Extract agreement from matrix
agreement = agextract(agreement_matrix)

# Define function to extract class subsets
def agsubset(df, val):

    # Get subset
    subset = df[(df['mapbiomas'] == val) | (df['potapov'] == val) | (df['zhang'] == val)].copy()

    # Calculate area proportional to total in subset
    subset['perc'] = (subset['area'] / subset['area'].sum())*100

    return subset

# Calculate agreement per class
gain = agsubset(agreement, 1)
loss = agsubset(agreement, 2)
sf = agsubset(agreement, 3)
snf = agsubset(agreement, 4)

# Define label dictionary
labdict = {1: 'Gain', 2:'Loss', 3:'Stable\nForest', 4:'Stable Non-\nForest'}

# Map labels
agreement['potapov'] = agreement['potapov'].map(labdict)
agreement['zhang'] = agreement['zhang'].map(labdict)
agreement['mapbiomas'] = agreement['mapbiomas'].map(labdict)

# Define function to calcualte spatial agreement
def phi(df, a, b, value):
    union = df.loc[(df[a] == value) | (df[b] == value), 'area'].sum()
    inter = df.loc[(df[a] == value) & (df[b] == value), 'area'].sum()
    return (inter / union * 100).round(2)

# Define dataset pairs
pairs = [('mapbiomas', 'potapov'), ('mapbiomas', 'zhang'), ('potapov', 'zhang')]

# Calculate agreement for each pair and class
spatagreement = pd.DataFrame(
    {'gain': {f'{a}-{b}': phi(gain, a, b, 1) for a, b in pairs},
     'loss': {f'{a}-{b}': phi(loss, a, b, 2) for a, b in pairs},
     'sf': {f'{a}-{b}': phi(sf, a, b, 3) for a, b in pairs},
     'snf': {f'{a}-{b}': phi(snf, a, b, 4) for a, b in pairs}}
).T

# Export
spatagreement.to_csv('data/map/stats_spatialagreement.csv', index=True)
print('statistics saved to data/map/stats_spatialagreement.csv')


# -------------------------------------------------------------------------
# CONFUSION MATRICES (MAP AGREEMENT)
# -------------------------------------------------------------------------
# Define class order for plotting
class_order = ['Gain', 'Loss', 'Stable\nForest', 'Stable Non-\nForest']

# Define helper function for building cms
def build_cm(df, row_var, col_var, order):
    cm = df.groupby([row_var, col_var])['area'].sum().unstack(fill_value=0)
    return cm.reindex(index=order, columns=order, fill_value=0)

# Define helper function for plotting cms
def plot_cell(ax, cm, dfs='.2f', cmap=None):
    sns.heatmap(cm, annot=True, fmt=dfs, cmap=cmap, linewidths=0.5,
                ax=ax, cbar=False, annot_kws={"size": 12}, vmin=0)
    ax.tick_params(axis='x', rotation=0, labelsize=10)
    ax.tick_params(axis='y', rotation=0, labelsize=10)

# Initialize figure
fig, axes = plt.subplots(2, 2, figsize=(14, 14),
                          gridspec_kw={'wspace': 0.05, 'hspace': 0.05})

# Top-left: mapbiomas x zhang
cm_mz = build_cm(agreement, 'mapbiomas', 'zhang', class_order)
plot_cell(axes[0, 0], cm_mz, cmap=blue_cmap)
axes[0, 0].set_ylabel('Mapbiomas', fontsize=16)
axes[0, 0].set_xlabel('')
axes[0, 0].xaxis.tick_top()
axes[0, 0].xaxis.set_label_position('top')
axes[0, 0].set_xlabel('GLC_FCS30D', fontsize=16, labelpad=10)

# Top-right: mapbiomas x potapov
cm_mp = build_cm(agreement, 'mapbiomas', 'potapov', class_order)
plot_cell(axes[0, 1], cm_mp, cmap=blue_cmap)
axes[0, 1].set_ylabel('')
axes[0, 1].set_yticklabels([])
axes[0, 1].xaxis.tick_top()
axes[0, 1].xaxis.set_label_position('top')
axes[0, 1].set_xlabel('GLAD LC', fontsize=16, labelpad=10)

# Bottom-left: potapov x zhang
cm_pz = build_cm(agreement, 'potapov', 'zhang', class_order)
plot_cell(axes[1, 0], cm_pz, cmap=blue_cmap)
axes[1, 0].set_ylabel('GLAD LC', fontsize=16)
axes[1, 0].set_xlabel('')
axes[1, 0].set_xticklabels([])

# Bottom-right: blank
axes[1, 1].axis('off')

# Save figure
plt.savefig('data/figures/supplementary/spatialagreement_cm.png', dpi=300, bbox_inches='tight')
print('figure saved to data/figures/supplementary/spatialagreement_cm.png')
plt.close(fig)


# -------------------------------------------------------------------------
# FOREST GAIN VENN DIAGRAM
# -------------------------------------------------------------------------
# Create gain masks per dataset
gain['mapbiomas_gain'] = gain['mapbiomas'] == 1
gain['potapov_gain'] = gain['potapov'] == 1
gain['zhang_gain'] = gain['zhang'] == 1

# Calculate areas for each region of the venn diagram
m = gain['mapbiomas_gain']
p = gain['potapov_gain']
z = gain['zhang_gain']

# Format for venn3 (Abc, aBc, ABc, abC, AbC, aBC, ABC)
subsets = (
    gain[ m & ~p & ~z]['area'].sum(),  # mapbiomas only
    gain[~m &  p & ~z]['area'].sum(),  # potapov only
    gain[ m &  p & ~z]['area'].sum(),  # mapbiomas + potapov
    gain[~m & ~p &  z]['area'].sum(),  # zhang only
    gain[ m & ~p &  z]['area'].sum(),  # mapbiomas + zhang
    gain[~m &  p &  z]['area'].sum(),  # potapov + zhang
    gain[ m &  p &  z]['area'].sum(),  # all three
)

total = sum(subsets)

def nudge(label_id, dx=0, dy=0):
    lbl = v.get_label_by_id(label_id)
    x, y = lbl.get_position()
    lbl.set_position((x + dx, y + dy))

# Initialize figure
fig, ax = plt.subplots(figsize=(8, 8))
v = venn3(subsets=subsets, set_labels=('MapBiomas  ', \
    '  GLAD LC', 'GLC_FCS30D'), ax=ax)

nudge('A', dx=-0.1)   # MapBiomas: slightly left
nudge('B', dx=0.07)    # GLAD LC: slightly right

# Adjust venn colors
for patch_id, color in colors.items():
    patch = v.get_patch_by_id(patch_id)
    if patch:
        patch.set_facecolor(color)
        patch.set_alpha(0.95)

# Add venn circles
venn3_circles(subsets=subsets, ax=ax, linewidth=1.0, color='white')

# Adjust area labels
for patch_id, val in zip(['100','010','110','001','101','011','111'], subsets):
    lbl = v.get_label_by_id(patch_id)
    if lbl:
        pct = 100 * val / total
        lbl.set_text(f'{val:.2f} Mha\n({pct:.1f}%)')
        lbl.set_fontsize(11)
        lbl.set_ha('center')
        lbl.set_va('center')

# Adjust dataset labels
for lid in ['A', 'B', 'C']:
    lbl = v.get_label_by_id(lid)
    if lbl:
        lbl.set_fontsize(14)
        lbl.set_fontweight('bold')
        lbl.set_ha('center')

# Nudge labels
v.get_label_by_id('100').set_position((-0.30, 0.28)) # green big
v.get_label_by_id('010').set_position((0.25, 0.32)) # blue big
v.get_label_by_id('001').set_position((0.15, -0.33)) # red big
v.get_label_by_id('110').set_position((0.019, 0.310)) 
v.get_label_by_id('011').set_position((0.204, 0.08)) 

# Adjust fontsize
v.get_label_by_id('100').set_fontsize(13)
v.get_label_by_id('010').set_fontsize(13)
v.get_label_by_id('001').set_fontsize(13)

# Add total Mha
ax.text(0.02, 0.3, f'Total:\n{total:.2f} Mha', transform=ax.transAxes,
    fontsize=14, ha='center', va='bottom')

# Tight layout and save
plt.tight_layout()
plt.savefig('data/figures/supplementary/venn_gain.png', dpi=300, transparent=True)
print('figure saved to data/figures/supplementary/venn_gain.png')
plt.close(fig)


# -------------------------------------------------------------------------
# FOREST LOSS VENN DIAGRAM
# -------------------------------------------------------------------------
# Create loss masks per dataset
loss['mapbiomas_loss'] = loss['mapbiomas'] == 2
loss['potapov_loss'] = loss['potapov'] == 2
loss['zhang_loss'] = loss['zhang'] == 2

# Calculate areas for each region of the venn diagram
m = loss['mapbiomas_loss']
p = loss['potapov_loss']
z = loss['zhang_loss']

# Format for venn3 (Abc, aBc, ABc, abC, AbC, aBC, ABC)
subsets = (
    loss[ m & ~p & ~z]['area'].sum(),  # mapbiomas only
    loss[~m &  p & ~z]['area'].sum(),  # potapov only
    loss[ m &  p & ~z]['area'].sum(),  # mapbiomas + potapov
    loss[~m & ~p &  z]['area'].sum(),  # zhang only
    loss[ m & ~p &  z]['area'].sum(),  # mapbiomas + zhang
    loss[~m &  p &  z]['area'].sum(),  # potapov + zhang
    loss[ m &  p &  z]['area'].sum(),  # all three
)

total = sum(subsets)

# Initialize figure
fig, ax = plt.subplots(figsize=(8, 8))
v = venn3(subsets=subsets, set_labels=('MapBiomas  ', \
    '  GLAD LC', 'GLC_FCS30D'), ax=ax)

# Adjust venn colors
for patch_id, color in colors.items():
    patch = v.get_patch_by_id(patch_id)
    if patch:
        patch.set_facecolor(color)
        patch.set_alpha(0.95)

# Add venn circles
venn3_circles(subsets=subsets, ax=ax, linewidth=1.0, color='white')

# Adjust area labels
for patch_id, val in zip(['100','010','110','001','101','011','111'], subsets):
    lbl = v.get_label_by_id(patch_id)
    if lbl:
        pct = 100 * val / total
        lbl.set_text(f'{val:.2f} Mha\n({pct:.1f}%)')
        lbl.set_fontsize(11)
        lbl.set_ha('center')
        lbl.set_va('center')

# Adjust dataset labels
for lid in ['A', 'B', 'C']:
    lbl = v.get_label_by_id(lid)
    if lbl:
        lbl.set_fontsize(14)
        lbl.set_fontweight('bold')
        lbl.set_ha('center')

# Nudge labels
v.get_label_by_id('100').set_position((-0.375, 0.25)) # green big
v.get_label_by_id('010').set_position((0.317, 0.3)) # blue big
# v.get_label_by_id('001').set_position((0.15, -0.33)) # red big
v.get_label_by_id('110').set_position((0.0, 0.344)) # light green
v.get_label_by_id('011').set_position((0.335, -0.025)) # grey
v.get_label_by_id('101').set_position((-0.28, -0.11)) # brown

# Adjust fontsize
v.get_label_by_id('100').set_fontsize(13)
v.get_label_by_id('010').set_fontsize(13)
v.get_label_by_id('001').set_fontsize(13)

# Add total Mha
ax.text(0.02, 0.3, f'Total:\n{total:.2f} Mha', transform=ax.transAxes,
    fontsize=14, ha='center', va='bottom')

# Tight layout and save
plt.tight_layout()
plt.savefig('data/figures/supplementary/venn_loss.png', dpi=300, transparent=True)
print('figure saved to data/figures/supplementary/venn_loss.png')
plt.close(fig)

