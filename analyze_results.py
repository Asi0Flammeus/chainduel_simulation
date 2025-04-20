#!/usr/bin/env python3
"""
Analyze batch simulation results: tables, heatmaps, and summary graphs.
"""
import os
import sys
import re
try:
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns
except ImportError as e:
    # Missing dependency
    module = e.name if hasattr(e, 'name') else str(e).split()[-1].strip("'")
    print(f"Error: required module '{module}' is not installed.")
    print("Please install analysis dependencies with: pip install -r requirements.txt")
    sys.exit(1)

def safe_filename(s: str) -> str:
    """Convert a string to a filesystem-safe filename."""
    return re.sub(r'[^A-Za-z0-9]+', '_', s).strip('_')

def main():
    csv_path = 'batch_results.csv'
    if not os.path.isfile(csv_path):
        print(f"Error: '{csv_path}' not found. Run batch simulations first.")
        sys.exit(1)

    # Load data
    df = pd.read_csv(csv_path)
    # Ensure numeric
    for col in ['win_rate1', 'win_rate2', 'avg_score1', 'avg_score2', 'max_length1', 'max_length2', 'avg_game_length']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Prepare output directory
    outdir = 'analysis_outputs'
    os.makedirs(outdir, exist_ok=True)
    sns.set(style='whitegrid')

    # Summary markdown
    md_path = os.path.join(outdir, 'RESULTS_SUMMARY.md')
    with open(md_path, 'w') as md:
        md.write('# Simulation Results Analysis\n\n')

        # Overall average win rate per strategy across all cases and opponents
        md.write('## Overall Average Win Rate per Strategy\n\n')
        overall = df.groupby('strategy1')['win_rate1'].mean().rename('avg_win_rate')
        md.write(overall.to_markdown() + '\n\n')

        # Generate bar chart for overall win rates
        fig, ax = plt.subplots(figsize=(6, 4))
        overall.plot.bar(ax=ax, color='skyblue')
        ax.set_ylabel('Average Win Rate')
        ax.set_ylim(0, 1)
        ax.set_title('Overall Average Win Rate per Strategy')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        barfile = os.path.join(outdir, 'overall_avg_win_rate.png')
        fig.savefig(barfile)
        plt.close(fig)
        md.write(f'![Overall Win Rate]({os.path.basename(barfile)})\n\n')

        # Per-case analyses
        cases = df['case'].unique()
        for case in cases:
            md.write(f'## Case: {case}\n\n')
            dfc = df[df['case'] == case]
            # Pivot table of win rates
            pivot = dfc.pivot(index='strategy1', columns='strategy2', values='win_rate1')
            md.write('### Win Rate Matrix (Strategy1 vs Strategy2)\n\n')
            md.write(pivot.to_markdown() + '\n\n')
            # Heatmap
            fig, ax = plt.subplots(figsize=(8, 6))
            sns.heatmap(pivot, annot=True, fmt='.2f', cmap='viridis', ax=ax)
            ax.set_title(f'Win Rate Heatmap: {case}')
            plt.yticks(rotation=0)
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            fname = f"heatmap_{safe_filename(case)}.png"
            fpath = os.path.join(outdir, fname)
            fig.savefig(fpath)
            plt.close(fig)
            md.write(f'![Heatmap {case}]({fname})\n\n')

    # Append comparison of win rates across cases to markdown and generate a plot
    with open(md_path, 'a') as md:
        md.write('## Strategy Win Rate Across Cases\n\n')
        # Average win rate of each strategy per case (averaged over opponents)
        case_pivot = df.groupby(['case','strategy1'])['win_rate1']\
                        .mean().unstack('strategy1')
        md.write(case_pivot.to_markdown() + '\n\n')
        # Plot comparison
        fig, ax = plt.subplots(figsize=(10, 6))
        case_pivot.plot(ax=ax, marker='o')
        ax.set_ylabel('Average Win Rate')
        ax.set_title('Strategy Win Rate Across Cases')
        ax.set_ylim(0, 1)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        cmp_file = os.path.join(outdir, 'comparison_win_rate_cases.png')
        fig.savefig(cmp_file)
        plt.close(fig)
        md.write(f'![Win Rate Across Cases](comparison_win_rate_cases.png)\n\n')
    print(f"Analysis complete. Outputs in '{outdir}/' (markdown and images).")

if __name__ == '__main__':
    main()