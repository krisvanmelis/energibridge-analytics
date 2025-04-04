
from typing import List, Dict, Any
from models.types.measurement_type import MeasurementType
from models.group import Group
import pandas as pd
import os
import json
from scipy.stats import ttest_ind, mannwhitneyu
import matplotlib.pyplot as plt
import seaborn as sns


class SignificanceTest:
    """
    Class for generating significance test visualizations and statistical comparisons.
    """

    @staticmethod
    def generate_panels(experiment_name: str, groups: List[Group], measurement_types: List[MeasurementType], y_pos: int = 0) -> List[Dict[str, Any]]:
        """
        Generate visualization panels for significance test experiment type.

        :param experiment_name: Name of the experiment
        :param groups: List of groups to visualize
        :param measurement_types: List of measurement types to visualize
        :param y_pos: Starting vertical position for panels
        :return: List of panel configurations
        """
        panels = []

        if len(groups) != 2:
            raise ValueError("Significance test requires exactly two groups.")
        group0 = groups[0]
        group1 = groups[1]
        SignificanceTest.generate_comparison_file(group0.name, group1.name)
        SignificanceTest.generate_aggregate_summary_file(group0.name, group1.name)


        x_pos = 0
        y_pos = 0
        panels = []

        for measurement_type in measurement_types:
            if measurement_type == MeasurementType.COMPARE_PEAK_POWER:
                base_column = "CPU_Peak_Power (W)"
                title_suffix = "Peak Power"
            elif measurement_type == MeasurementType.COMPARE_TOTAL_ENERGY:
                base_column = "CPU_Total_Energy (J)"
                title_suffix = "Total Energy"
            elif measurement_type == MeasurementType.COMPARE_POWER_OVER_TIME:
                panels.append(SignificanceTest.create_plot_over_time_2_groups(
                    group0.name, group1.name, y_pos, "CPU_POWER (W)_mean"
                ))
                y_pos += 4
                continue
            elif measurement_type == MeasurementType.COMPARE_MEMORY_OVER_TIME:
                panels.append(SignificanceTest.create_plot_over_time_2_groups(
                    group0.name, group1.name, y_pos, "TOTAL_MEMORY_mean"
                ))
                y_pos += 4
                continue
            elif measurement_type == MeasurementType.COMPARE_SWAP_OVER_TIME:
                panels.append(SignificanceTest.create_plot_over_time_2_groups(
                group0.name, group1.name, y_pos, "USED_SWAP_mean"
                ))
                y_pos += 4
                continue
            elif measurement_type == MeasurementType.COMPARE_ENERGY_VIOLIN_PLOT:
                SignificanceTest.create_comparison_violinplot(group0.name, group1.name,
                                                              metric_name="CPU_Total_Energy (J)")
                panels.append(SignificanceTest.create_violin_image_panel(group0.name, group1.name, "CPU_Total_Energy (J)", x_pos, y_pos))
                y_pos += 4
                continue
            elif measurement_type == MeasurementType.COMPARE_POWER_VIOLIN_PLOT:
                SignificanceTest.create_comparison_violinplot(group0.name, group1.name,
                                                              metric_name="CPU_Peak_Power (W)")
                panels.append(SignificanceTest.create_violin_image_panel(group0.name, group1.name, "CPU_Peak_Power (W)", x_pos, y_pos))
                y_pos += 4
                continue
            else:
                continue

            panels.append(SignificanceTest.generate_value_diff_panel(
                group0.name, group1.name, base_column, x_pos, y_pos
            ))
            y_pos += 4

            panels.append(SignificanceTest.generate_significance_panel(
                group0.name, group1.name, base_column, x_pos, y_pos
            ))
            y_pos += 4

        return panels

    @staticmethod
    def generate_comparison_file(group_name0, group_name1):
        summary_path0 = f"csv-data/output/{group_name0}/group_summary.csv"
        summary_path1 = f"csv-data/output/{group_name1}/group_summary.csv"
        trials_path0 = f"csv-data/output/{group_name0}/trial_summary.csv"
        trials_path1 = f"csv-data/output/{group_name1}/trial_summary.csv"

        df0 = pd.read_csv(summary_path0)
        df1 = pd.read_csv(summary_path1)
        trials0 = pd.read_csv(trials_path0)
        trials1 = pd.read_csv(trials_path1)

        mean_cols = [col for col in df0.columns if col.endswith("_mean")]
        comparison_data = {}

        for mean_col in mean_cols:
            val0 = df0.at[0, mean_col]
            val1 = df1.at[0, mean_col]

            abs_diff = abs(val1 - val0)
            rel_diff = abs_diff / abs(val0) if val0 != 0 else float("inf")

            base_col = mean_col.replace("_mean", "")
            normal_col = base_col + "_normally_distributed"

            normal0 = df0.at[0, normal_col] if normal_col in df0.columns else 0
            normal1 = df1.at[0, normal_col] if normal_col in df1.columns else 0
            normal = 1 if normal0 == 1 and normal1 == 1 else 0

            if base_col in trials0.columns and base_col in trials1.columns:
                sample0 = trials0[base_col].dropna()
                sample1 = trials1[base_col].dropna()
                if normal == 1:
                    _, pval = ttest_ind(sample0, sample1, equal_var=False, alternative='two-sided')
                else:
                    _, pval = mannwhitneyu(sample0, sample1, alternative='two-sided')
            else:
                pval = float("nan")

            significant = 1 if pval >= 0.05 else 0

            comparison_data[f"{base_col}_{group_name0}"] = [val0]
            comparison_data[f"{base_col}_{group_name1}"] = [val1]
            comparison_data[base_col + "_abs_diff"] = [abs_diff]
            comparison_data[base_col + "_rel_diff"] = [rel_diff]
            comparison_data[base_col + "_normal"] = [normal]
            comparison_data[base_col + "_pvalue"] = [pval]
            comparison_data[base_col + "_significant"] = [significant]

        comparison_df = pd.DataFrame(comparison_data)
        output_dir = f"csv-data/output/{group_name0}_vs_{group_name1}"
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "group_comparison.csv")
        comparison_df.to_csv(output_path, index=False)
        print(f"Comparison file saved to {output_path}")

    @staticmethod
    def generate_aggregate_summary_file(group_name0: str, group_name1: str):
        """
        Combines aggregate_data.csv from both groups. Renames the columns by appending the group name,
        and merges the dataframes side-by-side.
        """
        agg_path0 = f"csv-data/output/{group_name0}/aggregate_data.csv"
        agg_path1 = f"csv-data/output/{group_name1}/aggregate_data.csv"


        df0 = pd.read_csv(agg_path0)
        df1 = pd.read_csv(agg_path1)
        df0 = df0.drop(columns=["Time"])

        df0_renamed = df0.rename(columns={col: f"{col}_{group_name0}" for col in df0.columns if col != "Time"})
        df1_renamed = df1.rename(columns={col: f"{col}_{group_name1}" for col in df1.columns if col != "Time"})

        combined_df = pd.concat([df0_renamed, df1_renamed], axis=1)

        output_dir = f"csv-data/output/{group_name0}_vs_{group_name1}"
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "aggregate_summary.csv")
        combined_df.to_csv(output_path, index=False)
        print(f"Aggregate summary saved to {output_path}")


    @staticmethod
    def _load_template_with_placeholders(template_name: str, placeholders: Dict[str, str]) -> Dict[str, Any]:
        with open("csv-data/grafana-templates/" + template_name, 'r') as file:
            template = file.read()
            for key, value in placeholders.items():
                template = template.replace("PLACEHOLDER_" + key, value)
            return json.loads(template)

    @staticmethod
    def generate_value_diff_panel(group_name0: str, group_name1: str,
                                  base_column: str, x_pos: int, y_pos: int) -> Dict[str, Any]:
        """
        Creates a Grafana stat panel showing absolute and relative difference between two groups
        for a given base column.
        """
        output_group = f"{group_name0}_vs_{group_name1}"
        panel = SignificanceTest._load_template_with_placeholders("stat_panel_template.json", {
            "TITLE": f"{output_group} - {base_column} Value Differences",
            "GROUPNAME": output_group,
            "UNIT": "joule" if "Energy" in base_column else "watt"
        })

        panel["gridPos"]["x"] = x_pos
        panel["gridPos"]["y"] = y_pos
        panel["gridPos"]["w"] = 6
        panel["gridPos"]["h"] = 4

        columns = [
            {"selector": f"{base_column}_{group_name0}", "text": group_name0, "type": "number"},
            {"selector": f"{base_column}_{group_name1}", "text": group_name1, "type": "number"},
            {"selector": f"{base_column}_abs_diff", "text": "ABS DIFF", "type": "number"},
        ]

        panel["targets"][0]["columns"] = columns
        panel["targets"][0]["url"] = f"http://nginx/csv-data/output/{output_group}/group_comparison.csv"
        panel["targets"][0]["source"] = "url"
        panel["targets"][0]["type"] = "csv"
        panel["transformations"] = []

        return panel

    @staticmethod
    def generate_significance_panel(group_name0: str, group_name1: str,
                                    base_column: str, x_pos: int, y_pos: int) -> Dict[str, Any]:
        """
        Creates a Grafana stat panel showing significance test results (normality & p-value)
        for a given base column between two groups.
        """
        output_group = f"{group_name0}_vs_{group_name1}"
        panel = SignificanceTest._load_template_with_placeholders("stat_panel_template.json", {
            "TITLE": f"{output_group} - {base_column} Significance Test",
            "GROUPNAME": output_group,
            "UNIT": ""
        })

        panel["gridPos"]["x"] = x_pos
        panel["gridPos"]["y"] = y_pos
        panel["gridPos"]["w"] = 6
        panel["gridPos"]["h"] = 4

        columns = [
            {"selector": f"{base_column}_rel_diff", "text": "REL DIFF", "type": "number"},
            {"selector": f"{base_column}_pvalue", "text": "P-VALUE", "type": "number"},
            {"selector": f"{base_column}_significant", "text": "SIGNIFICANT?", "type": "number"},
        ]

        panel["targets"][0]["columns"] = columns
        panel["targets"][0]["url"] = f"http://nginx/csv-data/output/{output_group}/group_comparison.csv"
        panel["targets"][0]["source"] = "url"
        panel["targets"][0]["type"] = "csv"
        panel["transformations"] = []

        return panel

    @staticmethod
    def create_plot_over_time_2_groups(group_name0: str, group_name1: str, y_pos: int, metric_prefix: str) -> Dict[str, Any]:
        output_group = f"{group_name0}_vs_{group_name1}"

        metric_prefix_formatted = metric_prefix.replace("_", " ").title()

        panel = SignificanceTest._load_template_with_placeholders("panel_template.json", {
            "MEASUREMENTTYPE": f"CPU_{metric_prefix_formatted}_Raw",
            "GROUPNAME": output_group
        })

        panel["title"] = f"{group_name0} vs {group_name1} - CPU {metric_prefix_formatted} Comparison"
        panel["gridPos"]["y"] = y_pos
        panel["fieldConfig"]["defaults"]["unit"] = "watt"


        panel["targets"][0]["columns"] = [
            {"selector": "Time", "text": "Time", "type": "timestamp_epoch", "format": "unixtimestampms"},
            {"selector": f"{metric_prefix}_{group_name0}", "text": f"CPU {metric_prefix_formatted} {group_name0}", "type": "number"},
            {"selector": f"{metric_prefix}_{group_name1}", "text": f"CPU {metric_prefix_formatted} {group_name1}", "type": "number"}
        ]
        panel["targets"][0]["url"] = f"http://nginx/csv-data/output/{output_group}/aggregate_summary.csv"
        panel["targets"][0]["source"] = "url"
        panel["targets"][0]["type"] = "csv"
        panel["transformations"] = []
        panel["refresh"] = True

        return panel

    @staticmethod
    def create_comparison_violinplot(group_name0: str, group_name1: str, metric_name: str,
                                     output_folder: str = "csv-data/output/violin_plots") -> None:
        """
        Creates a violin plot comparing the distribution of a specified metric between two groups.

        :param group_name0: Name of the first group
        :param group_name1: Name of the second group
        :param metric_name: The column name of the metric to compare (must exist in trial_summary.csv)
        :param output_folder: Folder to save the violin plot image
        """
        path0 = f"csv-data/output/{group_name0}/trial_summary.csv"
        path1 = f"csv-data/output/{group_name1}/trial_summary.csv"

        if not os.path.exists(path0):
            raise FileNotFoundError(f"Trial summary not found for group {group_name0} at: {path0}")
        if not os.path.exists(path1):
            raise FileNotFoundError(f"Trial summary not found for group {group_name1} at: {path1}")

        df0 = pd.read_csv(path0)
        df1 = pd.read_csv(path1)

        if metric_name not in df0.columns or metric_name not in df1.columns:
            raise ValueError(f"Metric '{metric_name}' not found in trial summaries.")

        df0 = df0[[metric_name]].copy()
        df1 = df1[[metric_name]].copy()
        df0["Group"] = group_name0
        df1["Group"] = group_name1

        combined_df = pd.concat([df0, df1], ignore_index=True)

        plt.figure(figsize=(8, 6))
        sns.violinplot(data=combined_df, x="Group", y=metric_name)
        plt.title(f"Violin Plot of '{metric_name}' — {group_name0} vs {group_name1}")
        plt.ylabel(metric_name)
        plt.xlabel("Group")
        plt.tight_layout()

        os.makedirs(output_folder, exist_ok=True)
        safe_metric = metric_name.replace(" ", "_").replace("/", "_")
        output_path = os.path.join(output_folder, f"{safe_metric}_{group_name0}_vs_{group_name1}_violin.png")
        plt.savefig(output_path)
        plt.close()

    @staticmethod
    def create_violin_image_panel(group_name0: str, group_name1: str, metric_name: str, x_pos: int, y_pos: int) -> \
    Dict[str, Any]:
        """
        Loads and customizes an image panel for a violin plot comparing two groups on a specific metric.
        Uses the image_panel_template.json file.

        :param group_name0: Name of the first group
        :param group_name1: Name of the second group
        :param metric_name: The metric used for the violin plot
        :param x_pos: Horizontal position in the Grafana grid
        :param y_pos: Vertical position in the Grafana grid
        :return: Panel dictionary for Grafana dashboard
        """
        with open("csv-data/grafana-templates/image_panel_template.json", "r") as f:
            template = json.load(f)

        safe_metric = metric_name.replace(" ", "_").replace("/", "_")
        comparison_group = f"{group_name0}_vs_{group_name1}"
        image_filename = f"{safe_metric}_{comparison_group}_violin.png"
        base_url = "http://localhost:8080"

        # Set panel title and position
        template["title"] = f"{comparison_group} - {metric_name} Violin Plot"
        template["gridPos"]["x"] = x_pos
        template["gridPos"]["y"] = y_pos

        # Replace image URLs in elements and root background
        for element in template["options"].get("elements", []):
            if "url" in element:
                element["url"] = f"{base_url}/csv-data/output/violin_plots/{image_filename}"

        root_image = template["options"]["root"]["background"]["image"]
        root_image["fixed"] = f"{base_url}/csv-data/output/violin_plots/{image_filename}"

        return template

