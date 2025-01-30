import pandas as pd
import os

def get_df():
    files = os.listdir('results')
    files = [f"results/{f}" for f in files]
    
    return pd.concat([pd.read_csv(f) for f in files])
    

def filter_user_friendly_reponse():
    df = get_df()
    df = df[df['Task'].str.contains('将以下用户手册调整为更友好的语气')]
    sample = df.groupby('Model').sample(n=1, random_state=42)
    
    # save response as files
    for i, row in sample.iterrows():
        with open(f"friendly/{row['Model'].replace('/', '_')}.txt", 'w') as f:
            f.write(row['Response'])
    
def average_token_speed():
    df = get_df()
    df["n_tokens"] = df["Response"].apply(len) * 0.5
    df["token_speed"] = df["n_tokens"] / df["Latency (s)"]
    print(
        df
        .groupby('run_id')[['token_speed', 'Model', "total_requests"]]
        .agg({'token_speed': 'mean', 'Model': 'first', 'total_requests': 'first'})
        .sort_values(['Model', 'total_requests'])[["Model", "total_requests", "token_speed"]]
        .reset_index(drop=True)
    )
    
if __name__ == '__main__':
    # each run's average latency
    # print(
    #   df
    #   .groupby('run_id')[['Latency (s)', 'Model', "total_requests"]]
    #   .agg({'Latency (s)': 'mean', 'Model': 'first', 'total_requests': 'first'})
    #   .sort_values(['Model', 'total_requests'])[["Model", "total_requests", "Latency (s)"]]
    #         .reset_index(drop=True)

    # )
    
    average_token_speed()
    
    