# sort-blocks : A support tool that automates the creation of input data for [jcvi MCscan][jcvi].

I have written a script to automate the process after generating the blocks file by running:  
```python -m jcvi.compara.synteny mcscan```

This script simplifies the workflow by creating both the blocks file and the blocks.layout file required to execute:  
```python -m jcvi.graphics.synteny```


The input file should be a blocks file mapped to the same reference. The --iter option to "python -m jcvi.compara.synteny mcscan" does not necessarily need to be set. Specify the name of the directory containing the input files in "-i" option.

Example: using the command "python -m jcvi.compara.catalog ortholog" to do a pairwise synteny search for sample3 and each samples.
```
./input/sample1.blocks
./input/sample2.blocks
./input/sample4.blocks
```

To run the program, specify the range you want and the genes to highlight in the config file. Execute the program with -c to specify the name of the config file. The blocks file and blocks.layout will be generated in the order specified in "#input_files". If some genes are mapped to different regions, it is recommended to exclude them with "#exclude_genes". Highlighting is supported up to two colors (highlight settings can be easily specified later).

Example: Create a configuration as follows to figure the synteny block regions of cds01 to cds20 in sample3. When you want to remove translocated cds08, cds09 and highlight cds14, cds15.
```
#input_files
sample1.blocks, sample2.blocks, sample4.blocks
#start_gene
cds01
#end_gene
cds20
#exclude_genes
cds08, cds09
#highlight_color1
red
#highlight_genes1
cds14, cds15
```

You can specify the names of the blocks and blocks.layout files with -o (default is output).
```
python sort-blocks.py -c config -i input 
```
When commanded as above, the output.blocks file will give the same result as "python -m jcvi.formats.base join". The output.blocks.layout file will automatically generate the following contents if the conditions shown in the example are followed.
```
# x, y, rotation, ha, va, color, ratio, label
0.5, 0.65, 0, leftalign, center, , 1, reference
0.5, 0.55, 0, leftalign, center, , 1, sample1
0.5, 0.45, 0, leftalign, center, , 1, sample2
0.5, 0.35, 0, leftalign, center, , 1, sample4
# edges
e, 0, 1
e, 1, 2
e, 2, 3
```
Although the minimum set is generate automatically, it may be cases where minor modifications are necessary. In particular, since the position of the reference is fixed, the following is a description of how to modify the layout file.

Example: When you want to rename the reference to sample3 and illustrate it with the number 3 from the top.
```
# x, y, rotation, ha, va, color, ratio, label
0.5, 0.45, 0, leftalign, center, , 1, sample3
0.5, 0.65, 0, leftalign, center, , 1, sample1
0.5, 0.55, 0, leftalign, center, , 1, sample2
0.5, 0.35, 0, leftalign, center, , 1, sample4
# edges
e, 1, 2
e, 2, 0
e, 0, 3
```


[jcvi]:https://github.com/tanghaibao/jcvi/wiki/Mcscan-(python-version)
