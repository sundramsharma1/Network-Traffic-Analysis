import pandas as pd

def clean_csv(file_path, output_file_path):
    try:
        # Load the CSV file
        df = pd.read_csv(file_path)  # Ensure this points to the correct file path

        # List columns you want to keep (you can modify this list based on your needs)
        columns_to_keep = ['Time', 'Source', 'Destination', 'Protocol', 'Length', 'Info']

        # Check if all desired columns exist in the DataFrame
        missing_cols = [col for col in columns_to_keep if col not in df.columns]
        if missing_cols:
            print(f"Missing columns in the CSV: {missing_cols}")
            return  # Exit if there are missing columns

        # Filter the DataFrame to keep only the necessary columns
        df = df[columns_to_keep]

        # Convert Unix timestamps to readable date-time format
        # Assuming 'Time' column is in Unix epoch format
        df['Time'] = pd.to_datetime(df['Time'], unit='s')

        # Filter rows: example to keep only HTTP protocol packets
        df = df[df['Protocol'] == 'ICMP']

        # Remove duplicate rows if necessary
        df = df.drop_duplicates()

        # Save the cleaned data to a new CSV file
        df.to_csv(output_file_path, index=False)
        print("File has been cleaned and saved successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")

# Example file paths; replace with your actual file paths
input_file_path = 'Data2.csv'
output_file_path = 'CleanData.csv'
clean_csv(input_file_path, output_file_path)
