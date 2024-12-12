import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import openai  # Import the openai module

# Install missing libraries in Colab
!pip install pandas numpy matplotlib seaborn openai -q

# Set up your OpenAI API key
os.environ["OPENAI_API_KEY"] = "eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjIyZjMwMDA4OTJAZHMuc3R1ZHkuaWl0bS5hYy5pbiJ9.kLp1SnhJQmRTNrT4JWYCdTMy6S3peys4BdGlpY3aPhQ"  # Replace with your OpenAI API key

# Load dataset with multiple encoding attempts
def load_dataset(file_name):
    encodings_to_try = ['utf-8', 'latin1', 'ISO-8859-1', 'windows-1252']
    for encoding in encodings_to_try:
        try:
            data = pd.read_csv(file_name, encoding=encoding)
            print(f"Dataset '{file_name}' loaded successfully with encoding '{encoding}'.")
            return data
        except UnicodeDecodeError:
            print(f"Encoding issue detected with {file_name} using {encoding}. Trying next encoding.")
        except Exception as e:
            print(f"Error loading dataset: {e}")
            return None
    print(f"Failed to load {file_name} with all attempted encodings.")
    return None

# Basic data exploration
def explore_data(df):
    print("\n--- Dataset Overview ---")
    print(df.info())
    print("\n--- Descriptive Statistics ---")
    print(df.describe())
    print("\n--- First 5 Rows ---")
    print(df.head())
    return {
        "info": df.info(),
        "describe": df.describe(),
        "columns": df.columns.tolist(),
        "missing": df.isnull().sum().to_dict(),
    }

# Visualize data
def visualize_data(df, output_dir="charts"):
    os.makedirs(output_dir, exist_ok=True)
    chart_paths = []  # Initialize the list to store chart paths

    # Example: Correlation Heatmap
    plt.figure(figsize=(10, 8))
    corr = df.corr(numeric_only=True)
    sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f")
    heatmap_path = os.path.join(output_dir, "correlation_heatmap.png")
    plt.title("Correlation Heatmap")
    plt.savefig(heatmap_path)
    plt.close()
    print(f"Saved correlation heatmap to {heatmap_path}")
    chart_paths.append(heatmap_path)  # Add heatmap to chart_paths

    # Box Plot for numerical columns
    plt.figure(figsize=(10, 6))
    sns.boxplot(data=df.select_dtypes(include=[np.number]))
    plt.title("Box Plot for Numerical Features")
    boxplot_path = os.path.join(output_dir, "box_plot.png")
    plt.savefig(boxplot_path)
    plt.close()
    print(f"Saved box plot to {boxplot_path}")
    chart_paths.append(boxplot_path)  # Add boxplot to chart_paths

    # Pair Plot for selected numerical columns
    numerical_cols = df.select_dtypes(include=[np.number]).columns[:5]  # Limit to first 5 columns
    if len(numerical_cols) > 1:  # Only create if there are at least two numerical columns
        pairplot = sns.pairplot(df[numerical_cols])
        pairplot_path = os.path.join(output_dir, "pair_plot.png")
        pairplot.savefig(pairplot_path)
        plt.close()
        print(f"Saved pair plot to {pairplot_path}")
        chart_paths.append(pairplot_path)  # Add pair plot to chart_paths

    return chart_paths  # Return all chart paths

# Use OpenAI LLM to analyze and narrate
def narrate_analysis(df_summary, charts):
    try:
        prompt = (
            f"Analyze the following dataset summary and charts:\n\n"
            f"Summary: {df_summary}\n\n"
            f"Charts: {charts}\n\n"
            "Narrate a story describing the data, insights, and implications."
        )
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": "You are an analyst."},
                      {"role": "user", "content": prompt}]
        )
        print("\n--- Narrative ---")
        narrative = response['choices'][0]['message']['content']
        print(narrative)
        return narrative
    except Exception as e:
        print(f"Error with OpenAI API: {e}")
        return None

# Generate Markdown README
def generate_readme(df_summary, narrative, charts, output_path="README.md"):
    try:
        with open(output_path, "w") as f:
            f.write("# Analysis Report\n")
            f.write("\n## Dataset Summary\n")
            f.write(f"{df_summary}\n")
            f.write("\n## Insights and Narrative\n")
            f.write(f"{narrative}\n")
            f.write("\n## Charts\n")
            for chart in charts:
                f.write(f"![{chart}]({chart})\n")
        print(f"Saved README to {output_path}")
    except Exception as e:
        print(f"Error writing README: {e}")

# Main Function
def main():
    # File upload for Colab
    from google.colab import files  # Import files here
    uploaded = files.upload()
    if not uploaded:
        print("No file uploaded.")
        return

    file_name = list(uploaded.keys())[0]
    data = load_dataset(file_name)
    if data is None:
        return

    df_summary = explore_data(data)
    chart_paths = visualize_data(data)

    narrative = narrate_analysis(df_summary, chart_paths)
    generate_readme(df_summary, narrative, chart_paths)

# Run the script
if __name__ == "__main__":
    main()
