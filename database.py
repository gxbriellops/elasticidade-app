import pandas as pd
from datetime import datetime
import os

# Define the CSV file path
DATA_FILE = "dados.csv"

def get_current_date():
    """Return current date and time formatted as string"""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def create_database():
    """Create the CSV database file if it doesn't exist"""
    if not os.path.exists(DATA_FILE):
        # Create empty DataFrame with the required columns
        df = pd.DataFrame(columns=[
            'id', 'data_adicionada', 'precoInicio', 'precoFinal', 
            'quantidadeInicio', 'quantidadeFinal', 'elasticidade'
        ])
        # Save empty DataFrame to CSV
        df.to_csv(DATA_FILE, index=False)
        print(f"✅ Database file '{DATA_FILE}' created successfully")
    return True

def insert_data(data_adicionada, precoInicio, precoFinal, quantidadeInicio, quantidadeFinal, elasticidade=None):
    """Insert new data into the CSV database"""
    # Read existing data
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
    else:
        # Create database if it doesn't exist
        create_database()
        df = pd.read_csv(DATA_FILE)
    
    # Generate a new ID (max existing ID + 1, or 1 if no records exist)
    new_id = 1 if df.empty else df['id'].max() + 1
    
    # Create new row as a dictionary
    new_row = {
        'id': new_id,
        'data_adicionada': data_adicionada,
        'precoInicio': precoInicio,
        'precoFinal': precoFinal,
        'quantidadeInicio': quantidadeInicio,
        'quantidadeFinal': quantidadeFinal,
        'elasticidade': elasticidade
    }
    
    # Append new row to DataFrame
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    
    # Save updated DataFrame to CSV
    df.to_csv(DATA_FILE, index=False)
    return new_id

def get_latest_data():
    """Fetch the latest data record from the CSV database"""
    if not os.path.exists(DATA_FILE):
        return None
    
    df = pd.read_csv(DATA_FILE)
    if df.empty:
        return None
    
    # Get the row with the maximum ID
    latest_row = df.loc[df['id'].idxmax()]
    
    return (
        latest_row['precoInicio'],
        latest_row['precoFinal'],
        latest_row['quantidadeInicio'],
        latest_row['quantidadeFinal'],
        latest_row['elasticidade']
    )

def update_elasticity(elasticidade):
    """Update the elasticity value for the latest record"""
    if not os.path.exists(DATA_FILE):
        return False
    
    df = pd.read_csv(DATA_FILE)
    if df.empty:
        return False
    
    # Find the index of the row with the maximum ID
    max_id_idx = df['id'].idxmax()
    
    # Update the elasticity value
    df.at[max_id_idx, 'elasticidade'] = elasticidade
    
    # Save updated DataFrame to CSV
    df.to_csv(DATA_FILE, index=False)
    return True

def get_filtered_data(days=None):
    """
    Get data filtered by a specific time period
    
    Args:
        days (int, optional): Number of days to filter by. None returns all data.
    
    Returns:
        pandas.DataFrame: Filtered data
    """
    if not os.path.exists(DATA_FILE):
        create_database()
        return pd.DataFrame()
    
    df = pd.read_csv(DATA_FILE)
    
    if df.empty:
        return df
    
    # Convert 'data_adicionada' to datetime
    df['data_adicionada'] = pd.to_datetime(df['data_adicionada'])
    
    if days is not None:
        # Filter by date range
        cutoff_date = datetime.now() - pd.Timedelta(days=days)
        df = df[df['data_adicionada'] >= cutoff_date]
    
    return df