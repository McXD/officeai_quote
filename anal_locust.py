import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import argparse

def load_data(file_path):
    """Load Locust benchmark results from CSV."""
    try:
        df = pd.read_csv(file_path)
        print(f"✅ Loaded {len(df)} requests from {file_path}")
        return df
    except Exception as e:
        print(f"❌ Error loading file: {e}")
        exit(1)

def calculate_statistics(df):
    """Compute summary statistics."""
    stats = {
        "Total Requests": len(df),
        "Avg Latency (s)": df["Total Latency (s)"].mean(),
        "Min Latency (s)": df["Total Latency (s)"].min(),
        "Max Latency (s)": df["Total Latency (s)"].max(),
        "Avg TTFT (s)": df["Time-To-First-Token (s)"].mean(),
        "Min TTFT (s)": df["Time-To-First-Token (s)"].min(),
        "Max TTFT (s)": df["Time-To-First-Token (s)"].max(),
        "Avg Token Speed (tokens/s)": df["Tokens Per Second"].mean(),
        "Min Token Speed (tokens/s)": df["Tokens Per Second"].min(),
        "Max Token Speed (tokens/s)": df["Tokens Per Second"].max(),
        "Avg Char Speed (chars/s)": df["Characters Per Second"].mean(),
        "Min Char Speed (chars/s)": df["Characters Per Second"].min(),
        "Max Char Speed (chars/s)": df["Characters Per Second"].max(),
        "Avg Latency Spike Ratio (LSR)": df["Latency Spike Ratio (LSR)"].mean(),
        "Min Latency Spike Ratio (LSR)": df["Latency Spike Ratio (LSR)"].min(),
        "Max Latency Spike Ratio (LSR)": df["Latency Spike Ratio (LSR)"].max(),
    }
    return stats

def detect_latency_spikes(df, threshold=2):
    """Identify requests where LSR exceeds the threshold."""
    spikes = df[df["Latency Spike Ratio (LSR)"] > threshold]
    print(f"\n⚠️ {len(spikes)} requests had LSR > {threshold}")
    return spikes

def plot_latency_distribution(df):
    """Plot latency and LSR distributions (ASCII-style summary)."""
    print("\n📊 **Latency Distribution** (approximate bins)")
    print(df["Total Latency (s)"].describe())

    print("\n📊 **Latency Spike Ratio (LSR) Distribution**")
    print(df["Latency Spike Ratio (LSR)"].describe())

def print_summary(stats):
    """Print summary statistics to stdout."""
    print("\n📊 **Summary Statistics** 📊")
    for key, value in stats.items():
        print(f"{key}: {value:.4f}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze Locust benchmark results.")
    parser.add_argument("file", type=str, help="Path to the Locust results CSV file")
    args = parser.parse_args()

    df = load_data(args.file)
    stats = calculate_statistics(df)
    
    print_summary(stats)
    detect_latency_spikes(df)
    plot_latency_distribution(df)
