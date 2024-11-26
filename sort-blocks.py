import argparse
import glob
import os
import pandas as pd

def generate_y_values(num):
    if num <= 10:
        # Center is 0.5, interval increases and decreases by 0.1
        step = 0.1
        start = 0.5 + step * (num - 1) / 2
        values = [round(start - step * i, 3) for i in range(num)]
    else:
        # Evenly spaced from 0.05 to 0.95
        values = [round(0.05 + (0.9 / (num - 1)) * i, 3) for i in range(num)]

    return sorted(values, reverse=True)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', required=True, help="Path to the input config file")
    parser.add_argument('-i', '--input', default="./", help="Path to the input blocks file")
    parser.add_argument('-o', '--output', default="output", help="Path to the output blocks file")
    args = parser.parse_args()

    config_file = args.config
    input_file = args.input
    output_file = args.output

    # Initialize each variable in the config
    start_gene = None
    end_gene = None
    exclude_genes = []
    highlight_color1 = None
    highlight_genes1 = []
    highlight_color2 = None
    highlight_genes2 = []

    with open(config_file, 'r') as file:
        lines = file.readlines()

    # Variables that manage the currently processed section
    current_section = None

    for line in lines:
        line = line.strip()

        # Identifying config sections
        if line.startswith('#start_gene'):
            current_section = 'start_gene'
        elif line.startswith('#end_gene'):
            current_section = 'end_gene'
        elif line.startswith('#exclude_genes'):
            current_section = 'exclude_genes'
        elif line.startswith('#highlight_color1'):
            current_section = 'highlight_color1'
        elif line.startswith('#highlight_genes1'):
            current_section = 'highlight_genes1'
        elif line.startswith('#highlight_color2'):
            current_section = 'highlight_color2'
        elif line.startswith('#highlight_genes2'):
            current_section = 'highlight_genes2'
        elif line.startswith('#input_files'):
            current_section = 'input_files'
        elif line.startswith('#') or not line:
            # Skip comments and blank lines
            continue
        else:
            # Data processing (update variables even if the value is empty)
            if current_section == 'start_gene':
                start_gene = line if line else None
            elif current_section == 'end_gene':
                end_gene = line if line else None
            elif current_section == 'exclude_genes':
                exclude_genes = [item.strip() for item in line.split(',')] if line else []
            elif current_section == 'highlight_color1':
                highlight_color1 = line if line else None
            elif current_section == 'highlight_genes1':
                highlight_genes1 = [item.strip() for item in line.split(',')] if line else []
            elif current_section == 'highlight_color2':
                highlight_color2 = line if line else None
            elif current_section == 'highlight_genes2':
                highlight_genes2 = [item.strip() for item in line.split(',')] if line else []
            elif current_section == 'input_files':
                input_files = [item.strip() for item in line.split(',')] if line else []

    #Input to create new blocks files
    input2_files = []

    # Create full path and list existing files
    full_paths = [path for file_name in input_files for path in glob.glob(f"{input_file}/{file_name}")]

    for input_blocks in full_paths:
        mid_out_name = input_blocks.split("/")
        mid_out_name = mid_out_name[-1].split(".blocks")
        mid_out_name = mid_out_name[0] + '.sorted.blocks'

        input2_files.append(mid_out_name)

        print(f"Processing file: {mid_out_name}")

        # A list to store the results
        filtered_lines = []

        # Open and filter blocks files
        with open(input_blocks, 'r', encoding='utf-8') as f:
            for line in f:
                # Check the beginning of each line and extract only the lines within the range
                columns = line.strip().split('\t')
                gene = columns[0]

                # Include only what is in the range and is not included in the exclusion gene
                if start_gene <= gene <= end_gene and gene not in exclude_genes:
                    filtered_lines.append(line.strip())

        # Output for new blocks files
        output = []

        # Process each line in filtered_lines
        for line in filtered_lines:
            # Split by tab delimiter
            columns = line.split("\t")

            # Use the first column as the key to get elements from the second column onwards
            key = columns[0]
            values = [col for col in columns[1:] if col != '.']  # '.' is ignored

            # Convert a specified number to a highlight
            if key in highlight_genes1:
                key = f"{highlight_color1}*{key}"

            if key in highlight_genes2:
                key = f"{highlight_color2}*{key}"

            # If there are elements in the second or subsequent columns, record each as a separate line
            if values:
                for value in values:
                    output.append(f"{key}\t{value}")
            # If there are no elements in the second or subsequent columns, record "."
            else:
                output.append(f"{key}\t.")

        # Write the results to the sorted.blocks file
        with open(mid_out_name, 'w', encoding='utf-8') as f_out:
            for line in output:
                f_out.write(line + '\n')

    # Empty the initial data frame
    merged_df = None

    # Read all sorted.blocks files sequentially and merge them
    for i, file in enumerate(input2_files):
        df = pd.read_csv(file, sep='\t', header=None, names=['key', f'value{i+1}'])

        if merged_df is None:
            # The first file is initialized as a single data frame
            merged_df = df
        else:
            # Subsequent files are outer joined with the existing data frame
            merged_df = pd.merge(merged_df, df, on='key', how='outer')

    # Replace missing values ​​with '.'
    merged_df = merged_df.fillna('.')

    # Write the results to a blocks file in tab-delimited format.
    output_blocks_name = output_file + '.blocks'
    merged_df.to_csv(output_blocks_name, sep='\t', index=False, header=False)

    num = len(input2_files)
    num += 1
    input2_files.insert(0, 'reference')
    output_layout_name = output_file + '.blocks.layout'

    with open(output_layout_name, 'w', encoding='utf-8') as f_out2:
        f_out2.write('# x, y, rotation, ha, va, color, ratio, label' + '\n')
        for (y, label) in zip(generate_y_values(num), input2_files):
            label2 = str(label).split('.sorted.')
            f_out2.write('0.5, ' + str(y) + ', 0, leftalign, center, , 1, ' + str(label2[0]) + '\n')
        f_out2.write('# edges' + '\n')
        for j in range(1,num):
            k = j - 1
            f_out2.write('e, ' + str(k) + ', ' + str(j) + '\n')

if __name__ == '__main__':
    main()
