import pandas as pd

# Assuming you have two dataframes df1 and df2 with columns 'timestamp' and 'value'
# Replace 'timestamp' and 'value' with the actual column names in your data

# Load your datasets into pandas dataframes
df1 = pd.read_csv("mr2251-178_optical", header=None)
df2 = pd.read_csv("mr2251-178_x-ray", header=None)

# Merge the two dataframes based on the first column (assuming you want to interpolate the second column from df2 to match df1)
merged_df = pd.merge(df1, df2, left_on=0, right_on=0, how='outer', suffixes=('_df1', '_df2'))

# Sort the merged dataframe by the first column
merged_df.sort_values(0, inplace=True)

# Interpolate missing values in the second column of df2
merged_df[1] = merged_df[1].interpolate()

# Now you have a dataframe with interpolated values from df2 that match the first column of df1
# The '1_df2' column contains the interpolated values

# If needed, you can drop unnecessary columns
final_df = merged_df[[0, '1_df1', '1_df2']]

# Print or save the final dataframe
print(final_df)
# final_df.to_csv('interpolated_data.csv', index=False)