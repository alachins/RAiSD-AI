/*  
 *  RAiSD, Raised Accuracy in Sweep Detection
 *
 *  Copyright January 2017 by Nikolaos Alachiotis and Pavlos Pavlidis
 *
 *  This program is free software; you may redistribute it and/or modify its
 *  under the terms of the GNU General Public License as published by the Free
 *  Software Foundation; either version 2 of the License, or (at your option)
 *  any later version.
 *
 *  This program is distributed in the hope that it will be useful, but
 *  WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
 *  or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
 *  for more details.
 *
 *  For any other enquiries send an email to
 *  Nikolaos Alachiotis (n.alachiotis@gmail.com)
 *  Pavlos Pavlidis (pavlidisp@gmail.com)  
 *  
 */

#include "RAiSD.h"

void flagCheck (char ** argv, int i, int * flagVector, int flagIndex);

void RSDHelp (FILE * fp)
{
	fprintf(fp, " This is RAiSD version %d.%d, released in %s %d.\n\n", MAJOR_VERSION, MINOR_VERSION, RELEASE_MONTH, RELEASE_YEAR);

#ifdef _RSDAI
	fprintf(fp, " RAiSD-AI");
#else
	fprintf(fp, " RAiSD");
#endif

	fprintf(fp, "\n");
	fprintf(fp, "\t -n STRING\n");
	fprintf(fp, "\t -I STRING\n");

	fprintf(fp, "\n\t-- SNP and SAMPLE HANDLING\n\n");
	fprintf(fp, "\t[-L INTEGER]\n"); 	
	fprintf(fp, "\t[-S STRING]\n");
	fprintf(fp, "\t[-m FLOAT]\n");
	fprintf(fp, "\t[-M 0|1|2|3]\n");
	fprintf(fp, "\t[-y INTEGER]\n");
	fprintf(fp, "\t[-X STRING]\n");
	fprintf(fp, "\t[-B INTEGER INTEGER]\n");
	fprintf(fp, "\t[-o]\n");

	fprintf(fp, "\n\t-- SLIDING WINDOW and MU STATISTIC \n\n");
	fprintf(fp, "\t[-w INTEGER]\n");
	fprintf(fp, "\t[-c INTEGER]\n");
	fprintf(fp, "\t[-G INTEGER]\n");
	fprintf(fp, "\t[-VAREXP FLOAT]\n");
	fprintf(fp, "\t[-SFSEXP FLOAT]\n");
	fprintf(fp, "\t[-LDEXP FLOAT]\n");

	fprintf(fp, "\n\t-- STANDARD OUTPUT and REPORTS\n\n");
	fprintf(fp, "\t[-f]\n");
	fprintf(fp, "\t[-s]\n");
	fprintf(fp, "\t[-t]\n");
	fprintf(fp, "\t[-p]\n");
	fprintf(fp, "\t[-O]\n");
	fprintf(fp, "\t[-R]\n");
	fprintf(fp, "\t[-P]\n");
	fprintf(fp, "\t[-D]\n");
	fprintf(fp, "\t[-A FLOAT]\n");

	fprintf(fp, "\n\t-- ACCURACY and SENSITIVITY EVALUATION \n\n");	
	fprintf(fp, "\t[-T INTEGER]\n");
	fprintf(fp, "\t[-d INTEGER]\n");
	fprintf(fp, "\t[-k FLOAT]\n");
	fprintf(fp, "\t[-l FLOAT]\n");

	fprintf(fp, "\n\t-- FASTA-to-VCF CONVERSION \n\n");
	fprintf(fp, "\t[-C STRING]\n");
	fprintf(fp, "\t[-C2 STRING]\n");
	fprintf(fp, "\t[-H STRING]\n");
	fprintf(fp, "\t[-E STRING]\n");
	
	fprintf(fp, "\n\t-- VCF-to-MS CONVERSION \n\n");
	fprintf(fp, "\t[-Q INTEGER]\n");

	fprintf(fp, "\n\t-- COMMON-OUTLIER ANALYSIS \n\n");
	fprintf(fp, "\t[-CO STRING INTEGER INTEGER] or [-CO STRING INTEGER INTEGER STRING INTEGER INTEGER]\n");
	fprintf(fp, "\t[-COT FLOAT]\n");
	fprintf(fp, "\t[-COD INTEGER]\n");

#ifdef _RSDAI	
	fprintf(fp, "\n\t-- RAiSD-AI OPERATION MODES \n\n");
	fprintf(fp, "\t[-op IMG-GEN | MDL-GEN | MDL-TST | SWP-SCN]\n");
	
	fprintf(fp, "\n\t-- RAiSD-AI DATA GENERATION (MODE: IMG-GEN) \n\n");	
	fprintf(fp, "\t -icl STRING\n");
	fprintf(fp, "\t -its INTEGER\n");
	fprintf(fp, "\t[-poc]\n");
	fprintf(fp, "\t[-ips INTEGER]\n");
	fprintf(fp, "\t[-iws INTEGER]\n");
	fprintf(fp, "\t[-bin]\n");
	fprintf(fp, "\t[-typ 0|1|2]\n");
	//fprintf(fp, "\t[-det]\n");
	fprintf(fp, "\t[-w INTEGER]\n");
	
	fprintf(fp, "\n\t-- RAiSD-AI TRAINING (MODE: MDL-GEN) \n\n");
	fprintf(fp, "\t -I STRING\n");
	fprintf(fp, "\t[-arc SweepNet | FAST-NN | SweepNetRecomb]\n");
	fprintf(fp, "\t[-e INTEGER]\n");
	//fprintf(fp, "\t[-det]\n");
	
	fprintf(fp, "\n\t-- RAiSD-AI INFERENCE (MODE: MDL-TST) \n\n");
	fprintf(fp, "\t -mdl STRING\n");
	fprintf(fp, "\t -I STRING\n");
	fprintf(fp, "\t -clp INTEGER STRING=STRING STRING=STRING ...\n");

	fprintf(fp, "\n\t-- RAiSD-AI SWEEP SCAN (MODE: SWP-SCN) \n\n");
	fprintf(fp, "\t -pci INTEGER INTEGER ...\n");
	
	fprintf(fp, "\n\t-- RAiSD-AI ADDITIONAL PARAMETERS \n\n");
	fprintf(fp, "\t[-frm]\n"); 
	//fprintf(fp, "\t[-thr INTEGER]\n");
	fprintf(fp, "\t[-gpu]\n"); 
	fprintf(fp, "\t[-useTF]\n");
#endif	
	fprintf(fp, "\n\t-- MISCELLANEOUS PARAMETERS \n\n");
	fprintf(fp, "\t[-b]\n");
	fprintf(fp, "\t[-a INTEGER]\n");
	
	fprintf(fp, "\n\t-- HELP and VERSION NOTES \n\n");
	fprintf(fp, "\t[-h]\n");
	fprintf(fp, "\t[-v]\n");

	fprintf(fp, "\n\n");
	fprintf(fp, " PARAMETER DESCRIPTION\n\n");	
	fprintf(fp, "\t-n\tProvides a unique run ID that is used to name the output files, i.e., the info file and the report(s).\n");
	fprintf(fp, "\t-I\tProvides the path to the input file. Supported file formats: ms, vcf, fasta.\n");

	fprintf(fp, "\n\t-- SNP and SAMPLE HANDLING \n\n");
	fprintf(fp, "\t-L\tProvides the size of the region in basepairs for ms files. See -B option for vcf files.\n");
	fprintf(fp, "\t-S\tProvides the path to the list of samples to be processed (supported only with VCF).\n");
	fprintf(fp, "\t-m\tProvides the threshold value for excluding SNPs with minor allele frequency < threshold (0.0-1.0).\n");
	fprintf(fp, "\t-M\tIndicates the missing-data handling strategy (0: discards SNP (default), 1: imputes N per SNP,\n\t\t2: represents N through a mask, 3: ignores allele pairs with N).\n");
	fprintf(fp, "\t-y\tProvides the ploidy (integer value), used to correctly represent missing data.\n");
	fprintf(fp, "\t-X\tProvides the path to a tab-delimited file that contains regions per chromosome (one per line) to be\n\t\texcluded from the analysis (Format: chromosome [tab] regionStart [tab] regionStop).\n");
	fprintf(fp, "\t-B\tProvides the chromosome size in basepairs (first INTEGER) and SNPs (second INTEGER) for vcf files that\n\t\tcontain a single chromosome. If -B is not provided, or the input vcf file contains multiple chromosomes,\n\t\tRAiSD will determine the respective values by parsing each chromosome in its entirety before processing,\n\t\twhich will lead to slightly longer overall execution time.\n");
	fprintf(fp, "\t-o\tEnables dataset check and reordering of the input vcf file (only unzipped vcf files are supported).\n");

	fprintf(fp, "\n\t-- SLIDING WINDOW and MU STATISTIC \n\n");
	fprintf(fp, "\t-w\tProvides the window size (integer value). The default value is 50 (empirically determined).\n");
	fprintf(fp, "\t-c\tProvides the slack for the SFS edges to be used for the calculation of mu_SFS. The default value is 1\n\t\t(singletons and S-1 snp class, where S is the sample size).\n");
	fprintf(fp, "\t-G\tProvides the grid size to specify the total number of evaluation points across the data.\n\t\tWhen used, RAiSD reports mu statistic scores at equidistant locations between the first and last SNPs.\n");
	fprintf(fp, "\t-VAREXP\tProvides the exponent for the mu-var factor (default: 1.0).\n");
	fprintf(fp, "\t-SFSEXP\tProvides the exponent for the mu-sfs factor (default: 1.0).\n");
	fprintf(fp, "\t-LDEXP\tProvides the exponent for the mu-ld factor (default: 1.0).\n");

	fprintf(fp, "\n\t-- STANDARD OUTPUT and REPORTS \n\n");
	fprintf(fp, "\t-f\tOverwrites existing run files under the same run ID.\n");
	fprintf(fp, "\t-s\tGenerates a separate report file per set.\n");
	fprintf(fp, "\t-t\tRemoves the set separator symbol from the report(s).\n");
	fprintf(fp, "\t-p\tGenerates the output file RAiSD_Samples.STRING, where STRING is the run ID, comprising a list of samples\n\t\tin the input file (supported only with VCF).\n");
	fprintf(fp, "\t-O\tShows progress on the display device (at snp set granularity).\n");
	fprintf(fp, "\t-R\tIncludes additional information in the report file(s), i.e., window start and end, and the mu-statistic\n\t\tfactors for variation, SFS, and LD.\n");
	fprintf(fp, "\t-P\tGenerates four plots (for the three mu-statistic factors and the final score) in one PDF file per set of\n\t\tSNPs in the input file using Rscript (activates -s, -t, and -R).\n");
	fprintf(fp, "\t-D\tGenerates a site report, e.g., total, discarded, imputed etc.\n");
	fprintf(fp, "\t-A\tProvides a probability value to be used for the quantile function in R, and generates a Manhattan plot for\n\t\tthe final mu-statistic score using Rscript (activates -s, -t, and -R).\n");

	fprintf(fp, "\n\t-- ACCURACY and SENSITIVITY EVALUATION \n\n");
	fprintf(fp, "\t-T\tProvides the selection target (in basepairs) and calculates the average distance (over all datasets in the\n\t\tinput file) between the selection target and the reported locations.\n");
	fprintf(fp, "\t-d\tProvides a maximum distance from the selection target (in base pairs) to calculate success rates,\n\t\ti.e., reported locations in the proximity of the target of selection (provided via -T).\n");
	fprintf(fp, "\t-k\tProvides the false positive rate (e.g., 0.05) to report the corresponding reported score after sorting\n\t\tthe reported locations for all the datasets in the input file.\n");
	fprintf(fp, "\t-l\tProvides a threshold for each statistic, reported by a previous run using a false positive rate (e.g., 0.05, via -k)\n\
\t\tto report the true positive rate. Syntax: \"-l Number_of_Thresholds label1=thres1 label2=thres2 ...\", where\n\t\tlabel in {var, sfs, ld, mu, pcl0, pcl1}. Example: \"-l 6 var=0.1 sfs=0.2 ld=0.3 mu=0.4 pcl0=0.5 pcl1=0.6\".\n\t\tLabels pcl0 and pcl1 refer to CNN positive classes.\n");

	fprintf(fp, "\n\t-- FASTA-to-VCF CONVERSION \n\n");
	fprintf(fp, "\t-C\tProvides the outgroup to be used for the ancestral states (REF field in VCF). The first ingroup sequence\n\t\tis used if the outgroup is not given or found.\n");
	fprintf(fp, "\t-C2\tProvides a second outgroup to be used for the ancestral states (REF field in VCF).\n");
	fprintf(fp, "\t-H\tProvides the chromosome name (CHROM field in VCF) to overwrite default \"chrom\" string.\n");
	fprintf(fp, "\t-E\tConverts input FASTA to VCF and terminates execution without further processing.\n");
	
	fprintf(fp, "\n\t-- VCF-to-MS CONVERSION \n\n");
	fprintf(fp, "\t-Q\tConverts an input VCF to ms and provides the memory size (in MB) to be allocated for the conversion. Requires -L.\n");

	fprintf(fp, "\n\t-- COMMON-OUTLIER ANALYSIS \n\n");
	fprintf(fp, "\t-CO\tProvides the report name (and column indices for positions and scores) to be used for common-outlier analysis.\n\t\tTo perform a common-outlier analysis using RAiSD and SweeD, use -CO like this: \"-CO SweeD_Report.SweeD-Run-Name 1 2\".\n\t\tThe SweeD report must not contain a header. If you have already run RAiSD on your data and only want to perform a\n\t\tcommon-outlier analysis, use -CO like this: \"-CO SweeD_Report.SweeD-Run-Name 1 2 RAiSD_Report.RAiSD-Run-Name 1 X\",\n\t\twhere X is the index of the column you want to use depending on the RAiSD report.\n\t\tTo use the mu-statistic, set Y=2 if RAiSD was invoked with the default parameters, or set Y=7 if -R was explicitly\n\t\tprovided or implicitly activated through some other command-line parameter. Again, the RAiSD report must not contain\n\t\ta header.\n");
	fprintf(fp, "\t-COT\tProvides the cut-off threshold for identifying top outliers per report (default: 0.05, i.e., top 5%%). \n");
	fprintf(fp, "\t-COD\tProvides the maximum distance (in number of sites) between outlier points in the provided reports to identify\n\t\tmatching outlier positions reported by RAiSD and SweeD. Based on the accuracy of the implemented methods in SweeD\n\t\tand RAiSD, we typically set -COD to a value between 100 and 400 sites (default: 1, i.e., exact match).\n");

#ifdef _RSDAI
	fprintf(fp, "\n\t-- RAiSD-AI OPERATION MODES \n\n");
	fprintf(fp, "\t-op\tChanges the operation mode from RSD-DEF (RAiSD default) to: IMG-GEN | MDL-GEN | MDL-TST | SWP-SCN.\n\n\t\t\
IMG-GEN: Generates images (.png) that can be used for training (MDL-GEN) and/or inference (MDL-TST).\n\t\t\
         Output directory: RAiSD_Images.runID (runID is the run ID that is set with -n).\n\t\t\
MDL-GEN: Generates a neural network model (training).\n\t\t\
         Output directory: RAiSD_Model.runID (runID is the run ID that is set with -n).\n\t\t\
MDL-TST: Tests a neural network model (inference) and reports various metrics (accuracy, F1-score etc)\n\t\t\
	 in file RAiSD_Info.runID (runID is the run ID that is set with -n).\n\t\t\
SWP-SCN: Performs full scans for selective sweeps using a CNN generated by a previous MDL-GEN run. Requires: -G.\n\t\t\
         All generated images are stored in folder RAiSD_Grid.runID (runID is the run ID that is set with -n).\n\t\t\
RSD-DEF: Standard RAiSD execution using only the mu-statistic (no CNN)\n");

	fprintf(fp, "\n\t-- RAiSD-AI DATA GENERATION (MODE: IMG-GEN)\n\n");
	fprintf(fp, "\t-icl\tProvides the class label (Image Class Label). A folder with this name will be created in RAiSD_Images.runID.\n");
	fprintf(fp, "\t-its\tProvides the target site position for generating images (Image Target Site). This position corresponds to the center of\n\t\tthe first generated image. See next flag (-poc) for data-generation modes. If ips>1, additional images are positioned\n\t\ta number of SNPs before and after the first image.\n");
	fprintf(fp, "\t-poc\tChanges the data-generation mode from using SNP-driven windows (default) to constructing position-centered windows.\n\t\tWhen SNP-driven windows are used, the SNP located closest to the -its position (in bp) becomes the central SNP in the\n\t\twindow and an equal number of SNPs are placed on both sides. When position-centered windows are used, the -its position\n\t\t(in bp) is (as close as possible to) the midpoint between the leftmost and rightmost SNPs per window.\n");
	fprintf(fp, "\t-ips\tProvides the number of images to be created per simulation (Images Per Simulation) (default: 1).\n");
	fprintf(fp, "\t-iws\tProvides the window step for creating images (Image Window Step).\n");
	//fprintf(fp, "\t-ira\tEnables pixel rearrangement for both columns and rows (Image ReArrangement).\n");
	fprintf(fp, "\t-bin\tConverts image data to a custom binary format (.snp). Only supported by the PyTorch implementation. [PYTORCH-ONLY]\n");
	fprintf(fp, "\t-typ\tSpecifies the data type. When generating images (PNG) -> 0: raw data in all channels (default), 1: raw data in one channel\n\t\tand pairwise snp distances in the other channels, 2: raw data in one channel and mu-var-scaled values in the other channels.\n\t\tWhen generating data in custom binary format -> 0: raw snp data and positions (default), 1: derived allele frequencies and positions.\n");
	//fprintf(fp, "\t-det\tChanges the training objective from classification (default) to detection. When the objective is set for classification,\n\t\ttraining data is generated from one position (-its). When the objective is set for detection, training data is\n\t\tgenerated from multiple positions using a 1D grid (-G). This is only supported by the PyTorch implementation.\n\t\tRequires -G. [PYTORCH-ONLY]\n");
	fprintf(fp, "\t-w\tIn this mode (data generation), the window width provided via -w is used to generate images (image width) (default: 50).\n");
	
	fprintf(fp, "\n\t-- RAiSD-AI TRAINING (MODE: MDL-GEN) \n\n");
	fprintf(fp, "\t-I\tIn this mode (Training), -I provides the path to the directory where the training data is stored. This can be\n\t\tdirectory RAiSD_Images.some-runID, where some-runID is the run ID of some previous run in data generation mode.\n\t\tThe trained model will be stored in RAiSD_Model.runID, where runID is provided through -n.\n");
	fprintf(fp, "\t-arc\tSpecifies the neural network architecture: SweepNet (TF default) | FAST-NN (PyTorch default) | SweepNetRecomb (4-class model).\n");
	fprintf(fp, "\t-e\tProvides the number of epochs (default: 10).\n");
	fprintf(fp, "\t-cl4\tProvides four pairings (using '=') between class labels and corresponding folder names in the RAiSD_Images.some-runID\n\t\tdirectory (provided through -I). They are organized into two groups, 1 and 2, to carry out two simultaneous binary\n\t\tclassifications. This is only supported by SweepNetRecombination.\n\t\tSyntax: \"-cl4 label00=folderA label01=folderB label10=folderC label11=folderD\", where label00 through 11 are the label identifiers,\n\t\tand folderA through D are in the directory specified via -I. label00 and label01 are Group 0 while label10 and label11 are Group 1. \n");  
	//fprintf(fp, "\t-det\tIn this mode (Training), -det indicates that the CNN model to be trained will be used for detection. In this case,\n\t\tthe training data must have been created using -det in data-generation mode as well. This is only supported by the\n\t\tPyTorch implementation. [PYTORCH-ONLY]\n");
	
	fprintf(fp, "\n\t-- RAiSD-AI INFERENCE (MODE: MDL-TST) \n\n");
	fprintf(fp, "\t-mdl\tProvides a path to the directory where the trained CNN model is stored. This should be the RAiSD_Model.some-runID,\n\t\twhere some-runID is the run ID of some previous run in model generation mode (Training).\n");
	fprintf(fp, "\t-I\tIn this mode (model test), -I provides the path to the directory where the test data is stored. This can be\n\t\tdirectory RAiSD_Images.some-runID, where some-runID is the run ID of some previous run in data generation mode.\n\t\tThis directory should contain one folder with test data for each class.\n");	
	fprintf(fp, "\t-clp\tProvides the number of class tests followed by an equal number of pairings (using '=') between the class labels and\n\t\tthe corresponding folder names in the RAiSD_Images.some-runID directory (provided through -I).\n\t\tExample: \"-clp 2 label1=folderA label2=folderB\", where label1 and label2 are the label names, and folderA and folderB\n\t\tare in the directory specified via -I.\n");

	fprintf(fp, "\n\t-- RAiSD-AI SWEEP SCAN (MODE: SWP-SCN) \n\n");
	fprintf(fp, "\t-pci\tProvides the number of positive classes (1 for SweepNet and FAST-NN, 2 for SweepNetRecombination) followed\n\t\tby the positive class indices. The class index can be found in parentheses after the class label in file\n\t\tRAiSD_Model.some-runID/classLabels.txt, where some-runID is the run ID of the MDL-GEN run that generated the CNN model.\n\t\tExample: \"-pci 1 1\" for SweepNet/FAST-NN, \"-pci 2 1 3\" for SweepNetRecombination.\n");
	
	fprintf(fp, "\n\t-- RAiSD-AI ADDITIONAL PARAMETERS \n\n");
	fprintf(fp, "\t-frm\tRemoves the directories RAiSD_Images.runID (IMG-GEN) and RAiSD_Grid.runID (SWP-SCN), if they already exist.\n\t\trunID is provided through -n.\n");
	//fprintf(fp, "\t-thr\tProvides the number of CPU threads to be used for training (MDL-GEN) or inference for model testing (MDL-TST)\n\t\tand sweep scans (SWP-SCN).\n");
	fprintf(fp, "\t-gpu\tChanges the target hardware platform to be used for training (MDL-GEN) or inference for model testing (MDL-TST)\n\t\tand sweep scans (SWP-SCN) from CPU (default) to GPU (CUDA must be enabled).\n");
	fprintf(fp, "\t-useTF\tUses TensorFlow (default: PyTorch). Only SweepNet is currently implemented in TensorFlow. \n");
#endif

	fprintf(fp, "\n\t-- MISCELLANEOUS PARAMETERS \n\n");	
	fprintf(fp, "\t-b\tIndicates that the input file is in mbs format.\n");
	fprintf(fp, "\t-a\tProvides a seed for the random number generator.\n");
	
	fprintf(fp, "\n\t-- HELP and VERSION NOTES \n\n");
	fprintf(fp, "\t-h\tPrints this help message.\n");
	fprintf(fp, "\t-v\tPrints version information.\n");

	fprintf(fp, "\n");
}

void RSDVersions(FILE * fp)
{
	int releaseIndex = 0;
	int majorIndex = 1;
	int minorIndex = 0;
	
	int strlen = 2;

	fprintf(fp, " %*d. RAiSD v%d.%d (Jun  9, 2017): first release\n", strlen, releaseIndex++, majorIndex, minorIndex++);
	fprintf(fp, " %*d. RAiSD v%d.%d (Mar  7, 2018): -m to provide a MAF threshold\n", strlen, releaseIndex++, majorIndex, minorIndex++);
	fprintf(fp, " %*d. RAiSD v%d.%d (Mar 28, 2018): -b to suppoert the mbs format\n", strlen, releaseIndex++, majorIndex, minorIndex++);
	fprintf(fp, " %*d. RAiSD v%d.%d (Jul 18, 2018): -i to impute N per SNP, -a for rand seed\n", strlen, releaseIndex++, majorIndex, minorIndex++);
	fprintf(fp, " %*d. RAiSD v%d.%d (Aug  3, 2018): -M to handle missing data with 4 strategies (removed -i)\n", strlen, releaseIndex++, majorIndex, minorIndex++);
	fprintf(fp, " %*d. RAiSD v%d.%d (Aug  4, 2018): -R to include additional information in the report file\n", strlen, releaseIndex++, majorIndex, minorIndex++);
	fprintf(fp, " %*d. RAiSD v%d.%d (Sep  3, 2018): -P to create plots per set of SNPs with Rscript\n", strlen, releaseIndex++, majorIndex, minorIndex++);
	fprintf(fp, " %*d. RAiSD v%d.%d (Oct  2, 2018): -y for ploidy, -D for site report, fixed a bug in the plotting routine\n", strlen, releaseIndex++, majorIndex, minorIndex++);
	fprintf(fp, " %*d. RAiSD v%d.%d (Dec 31, 2018): MakefileZLIB to parse VCF files in gzip file format (requires the zlib library)\n", strlen, releaseIndex++, majorIndex, minorIndex++);
	fprintf(fp, " %*d. RAiSD v%d.%d (Apr 27, 2019): -w to set the window size (default 50), -c to set the SFS slack for the mu_SFS\n", strlen, releaseIndex++, majorIndex, minorIndex++);

	majorIndex++; minorIndex=0;

	fprintf(fp, " %*d. RAiSD v%d.%d (May 15, 2019): -A to create Manhattan plots, scale factors for muVar and muSFS to yield comparable scores among different chromosomes\n", strlen, releaseIndex++, majorIndex, minorIndex++);
	fprintf(fp, " %*d. RAiSD v%d.%d (Jan 21, 2020): Parser for unordered VCF files (e.g., extracted from DArTseq genotyping reports). The ordered VCF file is also created.\n", strlen, releaseIndex++, majorIndex, minorIndex++);
	fprintf(fp, " %*d. RAiSD v%d.%d (Jan 22, 2020): Added missing field (discarded monomorphic sites) in the site report (Dataset.c file) for missing-data strategies M=1,2, or 3.\n", strlen, releaseIndex++, majorIndex, minorIndex++);
	fprintf(fp, " %*d. RAiSD v%d.%d (Jan 23, 2020): -X to exclude regions per chromosome from the analysis\n", strlen, releaseIndex++, majorIndex, minorIndex++);
	fprintf(fp, " %*d. RAiSD v%d.%d (Jan 30, 2020): -B for chromosome length and SNP size. Fixed bug with the memory-reduction optimization for large chromosomes. -o to request vcf ordering and generation.\n", strlen, releaseIndex++, majorIndex, minorIndex++);
	fprintf(fp, " %*d. RAiSD v%d.%d (Feb  8, 2020): Fixed position bug due to typecasting. Some site positions were off by 1 bp.\n", strlen, releaseIndex++, majorIndex, minorIndex++);
	fprintf(fp, " %*d. RAiSD v%d.%d (Apr  2, 2020): Parses, converts to vcf, and analyzes fasta input files (-C/-C2 for outgroups, -H for chromosome name, -E for conversion-only mode).\n", strlen, releaseIndex++, majorIndex, minorIndex++);
	fprintf(fp, " %*d. RAiSD v%d.%d (Apr  8, 2020): -G parameter to specify the grid size\n", strlen, releaseIndex++, majorIndex, minorIndex++);
	fprintf(fp, " %*d. RAiSD v%d.%d (Apr 22, 2020): -CO, -COT, -COD parameters for common-outlier analysis between RAiSD and SweeD, install script for gsl\n", strlen, releaseIndex++, majorIndex, minorIndex++);
	fprintf(fp, " %*d. RAiSD v%d.%d (Aug  6, 2020): fixed bug in parsing one-character VCF sample names\n", strlen, releaseIndex++, majorIndex, minorIndex++);

	majorIndex++; minorIndex=0;
	
	fprintf(fp, " %*d. RAiSD v%d.%d (Jul 31, 2021): -Q for VCF to ms conversion\n", strlen, releaseIndex++, majorIndex, minorIndex++);
	fprintf(fp, " %*d. RAiSD v%d.%d (Aug  8, 2022): -VAREXP, -SFSEXP, -LDEXP for exponentiation of the mu-statistic factors\n", strlen, releaseIndex++, majorIndex, minorIndex++);
	
	majorIndex++; minorIndex=0;
		
	fprintf(fp, " %*d. RAiSD v%d.%d (Jul  1, 2024): RAiSD-AI release (data generation, CNN training and testing, and CNN-based scans)\n", strlen, releaseIndex++, majorIndex, minorIndex++);

}

RSDCommandLine_t * RSDCommandLine_new(void)
{
	RSDCommandLine_t * cl = NULL;
	cl = (RSDCommandLine_t *) rsd_malloc(sizeof(RSDCommandLine_t));
	assert(cl!=NULL);
	return cl;
}

void RSDCommandLine_free (RSDCommandLine_t * cl)
{
	assert(cl!=NULL);

#ifdef _RSDAI

	int i=0;
	
	if(cl->classLabelList!=NULL)
	{
		for(i=0;i<cl->numberOfClasses;i++)
		{
			if(cl->classLabelList[i]!=NULL)
				free(cl->classLabelList[i]);
		}
		
		free(cl->classLabelList);
	}
	
	if(cl->classPathList!=NULL)
	{
		for(i=0;i<cl->numberOfClasses;i++)
		{
			if(cl->classPathList[i]!=NULL)
				free(cl->classPathList[i]);
		}
		
		free(cl->classPathList);
	}
	
	if(cl->positiveClassIndex!=NULL)
		free(cl->positiveClassIndex);
					
#endif	
	free(cl);
}

void RSDCommandLine_init(RSDCommandLine_t * RSDCommandLine)
{
	strncpy(RSDCommandLine->runName, "\0", STRING_SIZE);
	strncpy(RSDCommandLine->inputFileName, "\0", STRING_SIZE);
	RSDCommandLine->regionLength = 0ull;
	RSDCommandLine->regionSNPs = 0ull;
	RSDCommandLine->overwriteOutput = 0;
	RSDCommandLine->splitOutput = 0;
	RSDCommandLine->setSeparator = 1;
	RSDCommandLine->printSampleList = 0;
	RSDCommandLine->maf = 0.0;
	strncpy(RSDCommandLine->sampleFileName, "\0", STRING_SIZE);
	RSDCommandLine->mbs = 0;
	RSDCommandLine->imputePerSNP = 0;
	RSDCommandLine->createPatternPoolMask = 0;
	RSDCommandLine->patternPoolMaskMode = 0;
	RSDCommandLine->displayProgress = 0;
	RSDCommandLine->fullReport = 0;
	RSDCommandLine->createPlot = 0;
	RSDCommandLine->createMPlot = 0;
	strncpy(RSDCommandLine->manhattanThreshold, "\0", STRING_SIZE);
	RSDCommandLine->muThreshold = 0.0;
	RSDCommandLine->ploidy = 2; // default
	RSDCommandLine->displayDiscardedReport = 0;
	RSDCommandLine->windowSize = DEFAULT_WINDOW_SIZE;
	RSDCommandLine->sfsSlack = 1; // singletons, and S-1 snp class (S is the sample size)
	strncpy(RSDCommandLine->excludeRegionsFile, "\0", STRING_SIZE);
	RSDCommandLine->orderVCF = 0;
	strncpy(RSDCommandLine->outgroupName, "\0", STRING_SIZE);
	strncpy(RSDCommandLine->outgroupName2, "\0", STRING_SIZE);
	strncpy(RSDCommandLine->chromNameVCF, "chrom", STRING_SIZE);
	RSDCommandLine->fasta2vcfMode = FASTA2VCF_CONVERT_n_PROCESS;
	RSDCommandLine->vcf2msExtra = 0;
	RSDCommandLine->vcf2msMemsize = PATTERNPOOL_SIZE;
	RSDCommandLine->gridSize = -1;
	RSDCommandLine->createCOPlot = 0;
	strncpy(RSDCommandLine->reportFilenameSweeD, "\0", STRING_SIZE);
	RSDCommandLine->positionIndexSweeD = -1;
	RSDCommandLine->scoreIndexSweeD = -1;
	strncpy(RSDCommandLine->reportFilenameRAiSD, "\0", STRING_SIZE);
	RSDCommandLine->positionIndexRAiSD = -1;
	RSDCommandLine->scoreIndexRAiSD = -1;
	strcpy(RSDCommandLine->commonOutliersThreshold, "0.05");
	RSDCommandLine->commonOutliersMaxDistance = 1.0;	
	RSDCommandLine->muVarExp = 1.0;
	RSDCommandLine->muSfsExp = 1.0;
	RSDCommandLine->muLdExp = 1.0;
	
	RSDCommandLine->selectionTarget = 0ull;
	RSDCommandLine->selectionTargetDThreshold = 0ull;
	RSDCommandLine->fprLoc = 0.0;
		
	RSDCommandLine->tprThresMuVar = 0.0;
	RSDCommandLine->tprThresMuSfs = 0.0;
	RSDCommandLine->tprThresMuLd = 0.0;
	RSDCommandLine->tprThresMu = 0.0;	
	
#ifdef _RSDAI	
	RSDCommandLine->opCode = OP_DEF;
	RSDCommandLine->enTF = 0; // default 0 -> Pytorch
	RSDCommandLine->threads = 1;
	RSDCommandLine->useGPU = 0;
	
	// IMG
	RSDCommandLine->imagesPerSimulation = 1;
	RSDCommandLine->imageTargetSite = 0;
	RSDCommandLine->imageWindowStep = 1;
	RSDCommandLine->imageReorderOpt = PIXEL_REORDERING_DISABLED;
	RSDCommandLine->imagePositionCenteredEn = 0;
	strncpy(RSDCommandLine->imageClassLabel, "\0", STRING_SIZE);
	RSDCommandLine->forceRemove = 0;
	strncpy(RSDCommandLine->modelPath, "\0", STRING_SIZE);
	RSDCommandLine->imgDataType = IMG_DATA_RAW;
	
	RSDCommandLine->numberOfClasses = 0 ;
	RSDCommandLine->classLabelList = NULL;
	RSDCommandLine->classPathList = NULL; 
	
	RSDCommandLine->imageHeight = 0;
	RSDCommandLine->imageWidth = 0;
	
	RSDCommandLine->epochs=10;
	RSDCommandLine->enBinFormat=0;
	RSDCommandLine->trnObjDetection=0;
	RSDCommandLine->gridRngLeBor=0;
	RSDCommandLine->gridRngRiBor=0;
	
	RSDCommandLine->numOfPositiveClasses=0;
	RSDCommandLine->positiveClassIndex=NULL;
	
	RSDCommandLine->userWindowSize=0;	
	strncpy(RSDCommandLine->networkArchitecture, ARC_SWEEPNET1D, STRING_SIZE); 
	
	//Evaluation
	RSDCommandLine->tprThresNnPositiveClass0 = 0.0;
	RSDCommandLine->tprThresNnPositiveClass1 = 0.0;	
	
	//Experimental
	RSDCommandLine->fullFrame = 0;
	RSDCommandLine->gridPointReductionMax = 0;	
#endif
}

void flagCheck (char ** argv, int i, int * flagVector, int flagIndex)
{
	if(flagVector[flagIndex]!=0)
	{
		fprintf(stderr, "\nERROR: Flag %s is given more than once!\n\n",argv[i]);
		exit(0);
	}

	flagVector[flagIndex]=1;
}

void RSDCommandLine_load(RSDCommandLine_t * RSDCommandLine, int argc, char ** argv)
{
	int i, j;
	int info_exists = 0;
	char tstring [STRING_SIZE], tstring2[STRING_SIZE];
	int * flagVector = (int*)calloc(MAX_COMMANDLINE_FLAGS, sizeof(int));
	assert(flagVector!=NULL);
	int co_mode = -1;

	for(i=1; i<argc; ++i)
	{
		if(!strcmp(argv[i], "-n")) 
		{ 
			flagCheck (argv, i, flagVector, 0);

			if (i!=argc-1 && argv[i+1][0]!='-')
				strcpy(RSDCommandLine->runName, argv[++i]);
			else
			{
				fprintf(stderr, "\nERROR: Missing argument after %s\n\n",argv[i]);
				exit(0);	
			}
			
#ifdef _RSDAI
			info_exists=-1;
#else		
			strcpy(tstring, "RAiSD_Info.");
			strcat(tstring, RSDCommandLine->runName);	
			RAiSD_Info_FP = fopen(tstring, "r");
			if(RAiSD_Info_FP!=NULL)
			{
				fclose(RAiSD_Info_FP);
				info_exists = 1;
			}
			else
			{
				RAiSD_Info_FP = fopen(tstring, "w");
				assert(RAiSD_Info_FP!=NULL);
			}
#endif
			continue;
		}

		if(!strcmp(argv[i], "-I")) 
		{ 
			flagCheck (argv, i, flagVector, 1);

			if (i!=argc-1 && argv[i+1][0]!='-')
				strcpy(RSDCommandLine->inputFileName, argv[++i]);
			else
			{
				fprintf(stderr, "\nERROR: Missing argument after %s\n\n",argv[i]);
				exit(0);	
			}

			continue;
		}

		if(!strcmp(argv[i], "-L")) 
		{ 
			flagCheck (argv, i, flagVector, 2);

			if(flagVector[B_FLAG_INDEX])
			{
				fprintf(stderr, "\nERROR: Argument %s cannot be used if -B is already provided!\n\n",argv[i]);
				exit(0);
			}

			if (i!=argc-1 && argv[i+1][0]!='-')
			{
				double len = atof(argv[++i]);
				RSDCommandLine->regionLength = (uint64_t) len;
			}
			else
			{
				fprintf(stderr, "\nERROR: Missing argument after %s\n\n",argv[i]);
				exit(0);	
			}

			continue;
		}

		if(!strcmp(argv[i], "-help") || !strcmp(argv[i], "help") || !strcmp(argv[i], "-h")) 
		{ 
			RSD_header(stdout);
			RSDHelp(stdout);
			exit(0);
		}

		if(!strcmp(argv[i], "-v")) // version information
		{ 
			RSDVersions(stdout);
			exit(0);
		}

		if(!strcmp(argv[i], "-f")) // Forces overwrite output report
		{ 
			RSDCommandLine->overwriteOutput = 1;
			continue;
		}

		if(!strcmp(argv[i], "-s")) // Splits output reports per set
		{ 
			RSDCommandLine->splitOutput = 1;
			continue;
		}

		if(!strcmp(argv[i], "-t")) // Removes separator symbol
		{ 
			RSDCommandLine->setSeparator = 0;
			continue;
		}

		if(!strcmp(argv[i], "-p")) // Prints sample list (only for VCF)
		{ 
			RSDCommandLine->printSampleList = 1;
			continue;
		}

		if(!strcmp(argv[i], "-S")) // Provides sample list (only for VCF)
		{ 
			flagCheck (argv, i, flagVector, 3);

			if (i!=argc-1 && argv[i+1][0]!='-')
				strcpy(RSDCommandLine->sampleFileName, argv[++i]);
			else
			{
				fprintf(stderr, "\nERROR: Missing argument after %s\n\n",argv[i]);
				exit(0);	
			}
			continue;
		}

		if(!strcmp(argv[i], "-m")) // Provide a MAF threshold
		{ 
			flagCheck (argv, i, flagVector, 4);

			if (i!=argc-1 && argv[i+1][0]!='-')
			{
				RSDCommandLine->maf = (double)atof(argv[++i]);
				if(RSDCommandLine->maf<0.0 || RSDCommandLine->maf>1.0)
				{
					fprintf(stderr, "\nERROR: Invalid MAF value (valid: 0.0-1.0)\n\n");
					exit(0);
				}
			}
			else
			{
				fprintf(stderr, "\nERROR: Missing argument after %s\n\n",argv[i]);
				exit(0);	
			}

			continue;
		}

		if(!strcmp(argv[i], "-b")) // To specify mbs format
		{ 
			RSDCommandLine->mbs = 1;
			continue;
		}

		if(!strcmp(argv[i], "-y")) 
		{ 
			flagCheck (argv, i, flagVector, 5);

			if (i!=argc-1 && argv[i+1][0]!='-')
			{
				int ploidy = atoi(argv[++i]);
				if(ploidy<=0)
				{
					fprintf(stderr, "\nERROR: Invalid argument after %s\n\n",argv[i-1]);
					exit(0);
				}
				RSDCommandLine->ploidy = ploidy;
			}
			else
			{
				fprintf(stderr, "\nERROR: Missing argument after %s\n\n",argv[i-1]);
				exit(0);	
			}
			continue;
		}	

		if(!strcmp(argv[i], "-M")) 
		{ 
			flagCheck (argv, i, flagVector, 6);

			if (i!=argc-1 && argv[i+1][0]!='-')
			{	
				if((strlen(argv[i+1])!=1) || ((strlen(argv[i+1])==1)&&(argv[i+1][0]!='0' && argv[i+1][0]!='1' && argv[i+1][0]!='2' && argv[i+1][0]!='3')))// && argv[i+1][0]!='3')
				{
					fprintf(stderr, "\nERROR: Invalid argument after %s\n\n",argv[i]);
					exit(0);	
				}

				int mode = atoi(argv[++i]);
				switch(mode)
				{
					case 1:
						RSDCommandLine->imputePerSNP = 1;
						RSDCommandLine->createPatternPoolMask = 0;
						RSDCommandLine->patternPoolMaskMode = 0;
					break;
					case 2:
						RSDCommandLine->imputePerSNP = 0;
						RSDCommandLine->createPatternPoolMask = 1;
						RSDCommandLine->patternPoolMaskMode = 0;
					break;
					case 3:
						RSDCommandLine->imputePerSNP = 0;
						RSDCommandLine->createPatternPoolMask = 1;
						RSDCommandLine->patternPoolMaskMode = 1;
					break;
					default:
						RSDCommandLine->imputePerSNP = 0;
						RSDCommandLine->createPatternPoolMask = 0;
						RSDCommandLine->patternPoolMaskMode = 0;
					break;
				}				
			}
			else
			{
				fprintf(stderr, "\nERROR: Missing argument after %s\n\n",argv[i]);
				exit(0);	
			}

			continue;
		}

		if(!strcmp(argv[i], "-O")) 
		{ 
			RSDCommandLine->displayProgress = 1;
			continue;
		}

		if(!strcmp(argv[i], "-R")) 
		{ 
			RSDCommandLine->fullReport = 1;
			continue;
		}

		if(!strcmp(argv[i], "-D")) 
		{ 
			flagCheck (argv, i, flagVector, 7);

			RSDCommandLine->displayDiscardedReport = 1;
			
			tstring2[0]='\0';
			strcpy(tstring2, "RAiSD_SiteReport.");
			strcat(tstring2, RSDCommandLine->runName);

			RAiSD_SiteReport_FP = fopen(tstring2, "w");
			assert(RAiSD_SiteReport_FP!=NULL);

			continue;
		}

		if(!strcmp(argv[i], "-a")) 
		{ 
			flagCheck (argv, i, flagVector, 8);

			if (i!=argc-1 && argv[i+1][0]!='-')
			{
				int seed = atoi(argv[++i]);
				srand((unsigned int)seed);
			}
			else
			{
				fprintf(stderr, "\nERROR: Missing argument after %s\n\n",argv[i]);
				exit(0);	
			}

			continue;
		}

		if(!strcmp(argv[i], "-P")) 
		{ 
			RSDCommandLine->createPlot = 1;
			RSDCommandLine->splitOutput = 1; // activating output splitting
			RSDCommandLine->fullReport = 1; // activating full report
			RSDCommandLine->setSeparator = 0; // remove separator symbol

			if(RSDPlot_checkRscript()!=0)
			{
				fprintf(stderr, "\nERROR: Rscript is not installed, required by %s for plotting with R\n\n",argv[i]);
				exit(0);
			}			
			
			continue;
		}

		if(!strcmp(argv[i], "-w")) 
		{ 
			flagCheck (argv, i, flagVector, 9);

			if (i!=argc-1 && argv[i+1][0]!='-')
			{
				double windowSize = atof(argv[++i]);
				int64_t windowSizeInt = (int64_t)windowSize;
				if((windowSize<MIN_WINDOW_SIZE) || ((windowSizeInt&1)==1))
				{
					fprintf(stderr, "\nERROR: Invalid window size (valid: even number >= %d)\n\n", MIN_WINDOW_SIZE);
					exit(0);
				}
				RSDCommandLine->windowSize = (int64_t)windowSize;
#ifdef _RSDAI
				RSDCommandLine->userWindowSize = 1;
#endif				
				
			}
			else
			{
				fprintf(stderr, "\nERROR: Missing argument after %s\n\n",argv[i]);
				exit(0);	
			}

			continue;
		}

		if(!strcmp(argv[i], "-c")) 
		{ 
			flagCheck (argv, i, flagVector, 10);

			if (i!=argc-1 && argv[i+1][0]!='-')
			{
				double sfsSlack = atof(argv[++i]);
				if(sfsSlack<1)
				{
					fprintf(stderr, "\nERROR: Invalid sfs slack value (valid: >= 1)\n\n");
					exit(0);
				}
				RSDCommandLine->sfsSlack = (int64_t)sfsSlack;
			}
			else
			{
				fprintf(stderr, "\nERROR: Missing argument after %s\n\n",argv[i]);
				exit(0);	
			}

			continue;
		}

		if(!strcmp(argv[i], "-A")) 
		{ 
			flagCheck (argv, i, flagVector, 11);

			double prob = 0.9999; // default

			if (i!=argc-1 && argv[i+1][0]!='-')
			{
				prob = (double)atof(argv[++i]);
				if(prob<0.0 || prob>1.0)
				{
					fprintf(stderr, "\nERROR: Invalid probability value (valid: 0.0-1.0)\n\n");
					exit(0);
				}
			}
			else
			{
				fprintf(stderr, "\nERROR: Missing argument after %s\n\n",argv[i]);
				exit(0);	
			}

			strcpy(RSDCommandLine->manhattanThreshold, argv[i]);

			RSDCommandLine->createMPlot = 1;
			RSDCommandLine->splitOutput = 1; // activates output splitting
			RSDCommandLine->fullReport = 1; // activates full report
			RSDCommandLine->setSeparator = 0; // removes separator symbol

			if(RSDPlot_checkRscript()!=0)
			{
				fprintf(stderr, "\nERROR: Rscript is not installed, required by %s for plotting with R\n\n",argv[i]);
				exit(0);
			}

			tstring2[0]='\0';
			strcpy(tstring2, "RAiSD_ReportList.txt"); 
			RSDPlot_createReportListName (RSDCommandLine, tstring2);

			RAiSD_ReportList_FP = fopen(tstring2, "w");
			assert(RAiSD_ReportList_FP!=NULL);	
			
			continue;
		}

		/* Testing */
		if(!strcmp(argv[i], "-T")) 
		{ 
			flagCheck (argv, i, flagVector, 12);

			if (i!=argc-1 && argv[i+1][0]!='-')
			{
				double tar = atof(argv[++i]);
				RSDCommandLine->selectionTarget = (uint64_t)tar;
			}			
			else
			{
				fprintf(stderr, "\nERROR: Missing argument after %s\n\n",argv[i]);
				exit(0);	
			}

			continue;
		}

		if(!strcmp(argv[i], "-d")) 
		{ 
			flagCheck (argv, i, flagVector, 13);

			if (i!=argc-1 && argv[i+1][0]!='-')
			{
				double dist = atof(argv[++i]);
				RSDCommandLine->selectionTargetDThreshold = (uint64_t)dist;
			}
			else
			{
				fprintf(stderr, "\nERROR: Missing argument after %s\n\n",argv[i]);
				exit(0);	
			}

			continue;
		}

		if(!strcmp(argv[i], "-k")) 
		{ 
			flagCheck (argv, i, flagVector, 14);

			if (i!=argc-1 && argv[i+1][0]!='-')
				RSDCommandLine->fprLoc = (double)atof(argv[++i]);
			else
			{
				fprintf(stderr, "\nERROR: Missing argument after %s\n\n",argv[i]);
				exit(0);	
			}

			continue;
		}

		if(!strcmp(argv[i], "-l")) 
		{ 
			flagCheck (argv, i, flagVector, 15);

			if (i!=argc-1 && argv[i+1][0]!='-')
			{
				int scoresTotal = (int)atoi(argv[++i]);
				
				if(scoresTotal>6 || scoresTotal<=0)
				{
					fprintf(stderr, "\nERROR: Invalid number of TPR threshold values (%s) after %s (valid: 1-6)\n\n", argv[i], argv[i-1]);
					exit(0);
				}
				
				if(i>=argc-scoresTotal)
				{
					fprintf(stderr, "\nERROR: Missing TPR threshold values after %s %s \n\n", argv[i-1], argv[i]);
					exit(0);
				}				
				
				for(j=0;j<scoresTotal;j++)
				{
					int slen = strlen(argv[++i]);
					
					memcpy(tstring2, argv[i], slen);
					tstring2[slen] = '\0'; 					
					
					char * tprThresID = strtok(tstring2, "=");					
					char * tprThres = strtok(NULL, "\0");					
					
  					if(!strcmp(tprThresID, "var"))
  						RSDCommandLine->tprThresMuVar = (double)atof(tprThres);
  					else
     					if(!strcmp(tprThresID, "sfs"))
  						RSDCommandLine->tprThresMuSfs = (double)atof(tprThres);
  					else
  					if(!strcmp(tprThresID, "ld"))
  						RSDCommandLine->tprThresMuLd = (double)atof(tprThres);
  					else
  					if(!strcmp(tprThresID, "mu"))
  						RSDCommandLine->tprThresMu = (double)atof(tprThres);
  					else
   					if(!strcmp(tprThresID, "pcl0"))
  						RSDCommandLine->tprThresNnPositiveClass0 = (double)atof(tprThres);
  					else
   					if(!strcmp(tprThresID, "pcl1"))
  						RSDCommandLine->tprThresNnPositiveClass1 = (double)atof(tprThres);
  					else 
  					{  
						fprintf(stderr, "\nERROR: Invalid TPR treshold label %s (valid: var, sfs, ld, mu, pcl0, pcl1) \n\n",argv[i]);
						exit(0);				
					}
				}				
			}	
			else
			{
				fprintf(stderr, "\nERROR: Missing argument after %s\n\n",argv[i]);
				exit(0);	
			}

			continue;
		}

		if(!strcmp(argv[i], "-X")) 
		{ 
			flagCheck (argv, i, flagVector, 16);

			if (i!=argc-1 && argv[i+1][0]!='-')
				strcpy(RSDCommandLine->excludeRegionsFile, argv[++i]);
			else
			{
				fprintf(stderr, "\nERROR: Missing argument after %s\n\n",argv[i]);
				exit(0);	
			}

			continue;
		}

		if(!strcmp(argv[i], "-B")) 
		{ 

			if(flagVector[L_FLAG_INDEX])
			{
				fprintf(stderr, "\nERROR: Argument %s cannot be used if -L is already provided!\n\n",argv[i]);
				exit(0);
			}
			
			flagCheck (argv, i, flagVector, 17);

			if ((i!=argc-1 && argv[i+1][0]!='-')&&(i!=argc-2 && argv[i+2][0]!='-'))
			{
				double len = atof(argv[++i]);
				RSDCommandLine->regionLength = (uint64_t) len;

				double snps = atof(argv[++i]);
				RSDCommandLine->regionSNPs = (uint64_t) snps;
			}
			else
			{
				fprintf(stderr, "\nERROR: Missing argument after %s\n\n",argv[i]);
				exit(0);	
			}

			continue;
		}

		if(!strcmp(argv[i], "-o")) 
		{ 
			RSDCommandLine->orderVCF = 1;
			continue;
		}

		if(!strcmp(argv[i], "-C")) 
		{ 
			flagCheck (argv, i, flagVector, 18);

			if (i!=argc-1 && argv[i+1][0]!='-')
				strcpy(RSDCommandLine->outgroupName, argv[++i]);
			else
			{
				fprintf(stderr, "\nERROR: Missing argument after %s\n\n",argv[i]);
				exit(0);	
			}

			continue;
		}

		if(!strcmp(argv[i], "-C2")) 
		{ 
			flagCheck (argv, i, flagVector, 19);

			if (i!=argc-1 && argv[i+1][0]!='-')
				strcpy(RSDCommandLine->outgroupName2, argv[++i]);
			else
			{
				fprintf(stderr, "\nERROR: Missing argument after %s\n\n",argv[i]);
				exit(0);	
			}

			continue;
		}

		if(!strcmp(argv[i], "-H")) 
		{ 
			flagCheck (argv, i, flagVector, 20);

			if (i!=argc-1 && argv[i+1][0]!='-')
				strcpy(RSDCommandLine->chromNameVCF, argv[++i]);
			else
			{
				fprintf(stderr, "\nERROR: Missing argument after %s\n\n",argv[i]);
				exit(0);	
			}

			continue;
		}

		if(!strcmp(argv[i], "-E")) 
		{ 
			RSDCommandLine->fasta2vcfMode = FASTA2VCF_CONVERT_n_EXIT;
			continue;
		}

		if(!strcmp(argv[i], "-G")) 
		{ 
			flagCheck (argv, i, flagVector, 21);

			if (i!=argc-1 && argv[i+1][0]!='-')
			{
				int64_t grid = (int64_t)atoi(argv[++i]);
				RSDCommandLine->gridSize = (int64_t) grid;

				if(RSDCommandLine->gridSize<3)
				{
					fprintf(stderr, "\nERROR: Invalid grid size (valid: >=3)\n\n");
					exit(0);
				}
			}
			else
			{
				fprintf(stderr, "\nERROR: Missing argument after %s\n\n",argv[i]);
				exit(0);	
			}

			continue;
		}

		if(!strcmp(argv[i], "-CO")) 
		{ 
			flagCheck (argv, i, flagVector, 22);

			if(i<=argc-7)
			{
				if(argv[i+1][0]!='-' && argv[i+2][0]!='-' && argv[i+3][0]!='-') // && argv[i+4][0]!='-' && argv[i+5][0]!='-' && argv[i+6][0]!='-')
				{
					if(argv[i+4][0]!='-' && argv[i+5][0]!='-' && argv[i+6][0]!='-')
					{
						co_mode = 1;
						RSDCommandLine->createCOPlot = 1;
					}
					else
					{
						if(argv[i+4][0]=='-')
						{
							co_mode = 0;
							RSDCommandLine->createCOPlot = 1;
						}
						else
						{

							fprintf(stderr, "\nERROR: Missing argument after %s\n\n",argv[i]);
							exit(0);
						}
					}
				}
				else
				{
					fprintf(stderr, "\nERROR: Missing argument after %s\n\n",argv[i]);
					exit(0);
				}
			}
			else
			{
				if(i<=argc-4)
				{
					if(argv[i+1][0]!='-' && argv[i+2][0]!='-' && argv[i+3][0]!='-')
					{
						if(i==argc-4)
						{
							co_mode = 0;
							RSDCommandLine->createCOPlot = 1;
						}
						else
						{
							if(argv[i+4][0]=='-')
							{
								co_mode = 0;
								RSDCommandLine->createCOPlot = 1;
							}
							else
							{
								fprintf(stderr, "\nERROR: Missing argument after %s\n\n",argv[i]);
								exit(0);
							}
						}
					}
					else
					{
						fprintf(stderr, "\nERROR: Missing argument after %s\n\n",argv[i]);
						exit(0);
					}
				}
				else
				{
					fprintf(stderr, "\nERROR: Missing argument after %s\n\n",argv[i]);
					exit(0);
				}
			}

			assert(co_mode==0 || co_mode==1);

			strcpy(RSDCommandLine->reportFilenameSweeD, argv[++i]);
			RSDCommandLine->positionIndexSweeD = (int)atoi(argv[++i]);
			RSDCommandLine->scoreIndexSweeD = (int)atoi(argv[++i]);

			if(co_mode)
			{
				strcpy(RSDCommandLine->reportFilenameRAiSD, argv[++i]);
				RSDCommandLine->positionIndexRAiSD = (int)atoi(argv[++i]);
				RSDCommandLine->scoreIndexRAiSD = (int)atoi(argv[++i]);
			}

			RSDCommandLine->splitOutput = 1; // activates output splitting
			RSDCommandLine->fullReport = 1; // activates full report
			RSDCommandLine->setSeparator = 0; // removes separator symbol

			continue;
		}

		if(!strcmp(argv[i], "-COT")) 
		{ 
			flagCheck (argv, i, flagVector, 23);

			if (i!=argc-1 && argv[i+1][0]!='-')
			{
				double threshold = (double)atof(argv[++i]);
				if(threshold<0.0 || threshold>1.0)
				{
					fprintf(stderr, "\nERROR: Invalid threshold value for common outliers (valid: 0.0-1.0)\n\n");
					exit(0);
				}
				strcpy(RSDCommandLine->commonOutliersThreshold, argv[i]);
			}
			else
			{
				fprintf(stderr, "\nERROR: Missing argument after %s\n\n",argv[i]);
				exit(0);	
			}

			continue;
		}

		if(!strcmp(argv[i], "-COD")) 
		{ 
			flagCheck (argv, i, flagVector, 24);

			if (i!=argc-1 && argv[i+1][0]!='-')
			{
				double maxdistance = (double)atof(argv[++i]);
				if(maxdistance<0.0)
				{
					fprintf(stderr, "\nERROR: Invalid maximum distance between common outliers (valid: 0.0>=0)\n\n");
					exit(0);
				}
				RSDCommandLine->commonOutliersMaxDistance = maxdistance;
			}
			else
			{
				fprintf(stderr, "\nERROR: Missing argument after %s\n\n",argv[i]);
				exit(0);	
			}

			continue;
		}

		if(!strcmp(argv[i], "-Q")) 
		{ 
			flagCheck (argv, i, flagVector, 25);

			RSDCommandLine->vcf2msExtra = VCF2MS_CONVERT;

			if (i!=argc-1 && argv[i+1][0]!='-')
			{
				int64_t memsz = (int64_t)atoi(argv[++i]);
				RSDCommandLine->vcf2msMemsize = (int64_t) memsz;

				if(RSDCommandLine->vcf2msMemsize<1)
				{
					fprintf(stderr, "\nERROR: Invalid memory size for VCF to ms conversion (valid: >=1 MB)\n\n");
					exit(0);
				}
			}
			else
			{
				fprintf(stderr, "\nERROR: Missing or invalid argument after %s\n\n",argv[i]);
				exit(0);	
			}

			continue;
		}
		
		if(!strcmp(argv[i], "-VAREXP")) 
		{ 
			flagCheck (argv, i, flagVector, 26);

			if (i!=argc-1 && argv[i+1][0]!='-')
			{
				RSDCommandLine->muVarExp = atof(argv[++i]);				

				if(RSDCommandLine->muVarExp<0.0 || RSDCommandLine->muVarExp>10.0)
				{
					fprintf(stderr, "\nERROR: You have given an exponent that is outside the valid range (0.0 < exp < 10.0, default: 1.0)\n\n");
					exit(0);
				}
			}
			else
			{
				fprintf(stderr, "\nERROR: Missing or invalid argument after %s\n\n",argv[i]);
				exit(0);	
			}

			continue;
		}
		
		if(!strcmp(argv[i], "-SFSEXP")) 
		{ 
			flagCheck (argv, i, flagVector, 27);

			if (i!=argc-1 && argv[i+1][0]!='-')
			{
				RSDCommandLine->muSfsExp = atof(argv[++i]);				

				if(RSDCommandLine->muVarExp<0.0 || RSDCommandLine->muVarExp>10.0)
				{
					fprintf(stderr, "\nERROR: You have given an exponent that is outside the valid range (0.0 < exp < 10.0, default: 1.0)\n\n");
					exit(0);
				}
			}
			else
			{
				fprintf(stderr, "\nERROR: Missing or invalid argument after %s\n\n",argv[i]);
				exit(0);	
			}

			continue;
		}
		
		if(!strcmp(argv[i], "-LDEXP")) 
		{ 
			flagCheck (argv, i, flagVector, 28);

			if (i!=argc-1 && argv[i+1][0]!='-')
			{
				RSDCommandLine->muLdExp = atof(argv[++i]);				

				if(RSDCommandLine->muVarExp<0.0 || RSDCommandLine->muVarExp>10.0)
				{
					fprintf(stderr, "\nERROR: You have given an exponent that is outside the valid range (0.0 < exp < 10.0, default: 1.0)\n\n");
					exit(0);
				}
			}
			else
			{
				fprintf(stderr, "\nERROR: Missing or invalid argument after %s\n\n",argv[i]);
				exit(0);	
			}

			continue;
		}
		
#ifdef _RSDAI		
		if(!strcmp(argv[i], "-op")) // operation
		{ 
			flagCheck (argv, i, flagVector, 29);

			if (i!=argc-1 && argv[i+1][0]!='-')
			{
				tstring2[0]='\0';
				strcpy(tstring2, argv[++i]);
				
				if(!strcmp(tstring2, "RSD-DEF")) // default RAiSD
				{
					RSDCommandLine->opCode = OP_DEF;
				}
				else
				{
					if(!strcmp(tstring2, "IMG-GEN")) 
					{
						RSDCommandLine->opCode = OP_CREATE_IMAGES;
					}
					else
					{
						if(!strcmp(tstring2, "SWP-SCN")) 
						{
							RSDCommandLine->opCode = OP_USE_CNN;
							RSDCommandLine->forceRemove = 1;
						}
						else
						{
							if(!strcmp(tstring2, "MDL-GEN")) 
							{
								RSDCommandLine->opCode = OP_TRAIN_CNN;
							}
							else
							{
								if(!strcmp(tstring2, "MDL-TST")) 
								{
									RSDCommandLine->opCode = OP_TEST_CNN;
								}
								else
								{
									fprintf(stderr, "\nERROR: Missing or invalid argument after %s\n\n",argv[i-1]);
									exit(0);
								}
							}
						}						
					}
				}
			}
			else
			{
				fprintf(stderr, "\nERROR: Missing or invalid argument after %s\n\n",argv[i]);
				exit(0);	
			}

			continue;
		}
		
		if(!strcmp(argv[i], "-bin")) // encodes snps as binary data, not images
		{ 
			RSDCommandLine->enBinFormat = 1; 
			continue;
		}		
		
		/*if(!strcmp(argv[i], "-det")) // generates snp data for detection, not classification (default)
		{ 
			RSDCommandLine->trnObjDetection = 0; // not supported 
			continue;
		}*/
		
		if(!strcmp(argv[i], "-useTF")) // TensorFlow - set default operation with image data
		{ 
			RSDCommandLine->enTF = 1;
			strncpy(RSDCommandLine->networkArchitecture, "SweepNet", STRING_SIZE);
			continue;
		}
		
		if(!strcmp(argv[i], "-gpu") || !strcmp(argv[i], "-GPU"))
		{ 
			RSDCommandLine->useGPU = 1; 
			continue;
		}		
		
		if(!strcmp(argv[i], "-ips")) 
		{ 
			flagCheck (argv, i, flagVector, 30);

			if (i!=argc-1 && argv[i+1][0]!='-')
			{
				double imagesPerSimulation = atof(argv[++i]);
				RSDCommandLine->imagesPerSimulation = (uint64_t) imagesPerSimulation;
			}
			else
			{
				fprintf(stderr, "\nERROR: Missing argument after %s\n\n",argv[i]);
				exit(0);	
			}

			continue;
		}		

		if(!strcmp(argv[i], "-its")) // (first) image target site 
		{ 
			flagCheck (argv, i, flagVector, 31); // IMG_TARGET_SITE_FLAG_INDEX = 31 

			if (i!=argc-1 && argv[i+1][0]!='-')
			{
				double imageTargetSite = atof(argv[++i]);
				RSDCommandLine->imageTargetSite = (uint64_t) imageTargetSite;
			}
			else
			{
				fprintf(stderr, "\nERROR: Missing argument after %s\n\n",argv[i]);
				exit(0);	
			}

			continue;
		}
		
		if(!strcmp(argv[i], "-iws")) // image window step
		{ 
			flagCheck (argv, i, flagVector, 32); 

			if (i!=argc-1 && argv[i+1][0]!='-')
			{
				double imageWindowStep = atof(argv[++i]);
				RSDCommandLine->imageWindowStep = (uint64_t) imageWindowStep;
				
				if(RSDCommandLine->imageWindowStep<1)
				{
					fprintf(stderr, "\nERROR: You have given an invalid window step with -iws (>= 1, default: 1)\n\n");
					exit(0);
				}
			}
			else
			{
				fprintf(stderr, "\nERROR: Missing argument after %s\n\n",argv[i]);
				exit(0);	
			}

			continue;
		}
		
		if(!strcmp(argv[i], "-icl")) 
		{ 
			flagCheck (argv, i, flagVector, 33); // IMG_CLASS_LABEL_FLAG_INDEX = 33

			if (i!=argc-1 && argv[i+1][0]!='-')
				strcpy(RSDCommandLine->imageClassLabel, argv[++i]);
			else
			{
				fprintf(stderr, "\nERROR: Missing argument after %s\n\n",argv[i]);
				exit(0);	
			}

			continue;
		}
		
		/*if(!strcmp(argv[i], "-ira")) //not supported yet 
		{ 
			RSDCommandLine->imageReorderOpt = PIXEL_REORDERING_ENABLED;
			continue;
		}*/
		
		if(!strcmp(argv[i], "-poc")) 
		{ 
			RSDCommandLine->imagePositionCenteredEn = 1;
			continue;
		}
		
		if(!strcmp(argv[i], "-frm")) 
		{ 
			RSDCommandLine->forceRemove = 1;
			continue;
		}
		
		if(!strcmp(argv[i], "-mdl")) 
		{ 
			flagCheck (argv, i, flagVector, 34);

			if (i!=argc-1 && argv[i+1][0]!='-')
			{
				strcpy(RSDCommandLine->modelPath, argv[++i]);
				
				if(RSDNeuralNetwork_modelExists(RSDCommandLine->modelPath)!=1)
				{
					fprintf(stderr, "\nERROR: Invalid model %s or directory not found!\n\n", RSDCommandLine->modelPath);
					exit(0);
				}			
			}
			else
			{
				fprintf(stderr, "\nERROR: Missing argument after %s\n\n",argv[i]);
				exit(0);	
			}

			continue;
		}
		
		if(!strcmp(argv[i], "-clp")) // provided class paths for testing 
		{ 
			flagCheck (argv, i, flagVector, 35); 

			if (i!=argc-1 && argv[i+1][0]!='-')
			{
				int numberOfClasses = (int)atof(argv[++i]);
				
				if(numberOfClasses<=0)
				{
					fprintf(stderr, "\nERROR: Invalid number of classes (>=1))\n\n");
					exit(0);
				}
				RSDCommandLine->numberOfClasses = numberOfClasses;
				
				RSDCommandLine->classLabelList = (char**)rsd_malloc(sizeof(char*)*RSDCommandLine->numberOfClasses); // this must be the true class
				assert(RSDCommandLine->classLabelList!=NULL);
				
				RSDCommandLine->classPathList = (char**)rsd_malloc(sizeof(char*)*RSDCommandLine->numberOfClasses);
				assert(RSDCommandLine->classPathList!=NULL);
				
				for(j=0;j<RSDCommandLine->numberOfClasses;j++)
				{
					if (i!=argc-1 && argv[i+1][0]!='-')
					{
						RSDCommandLine->classLabelList[j] = (char*)rsd_malloc(sizeof(char)*STRING_SIZE);
						assert(RSDCommandLine->classLabelList[j]!=NULL);
						
						RSDCommandLine->classPathList[j] = (char*)rsd_malloc(sizeof(char)*STRING_SIZE);
						assert(RSDCommandLine->classPathList[j]!=NULL);
						
						strcpy(tstring, argv[++i]);
						
						int suc = split_string (tstring, RSDCommandLine->classLabelList[j], RSDCommandLine->classPathList[j], '=');
						
						if(suc!=1)
						{
							fprintf(stderr, "\nERROR: Invalid format string \"%s\" (missing or wrong delimiter, '=')\n\n",argv[i]);
							exit(0);
						}					
					}
					else
					{
						fprintf(stderr, "\nERROR: Missing argument after %s\n\n",argv[i]);
						exit(0);
					}			
				}
			}
			else
			{
				fprintf(stderr, "\nERROR: Missing argument after %s\n\n",argv[i]);
				exit(0);	
			}

			continue;
		}		
		
		if(!strcmp(argv[i], "-ihe")) 
		{ 
			flagCheck (argv, i, flagVector, 36);

			if (i!=argc-1 && argv[i+1][0]!='-')
			{
				RSDCommandLine->imageHeight = (unsigned int)atoi(argv[++i]);
			}
			else
			{
				fprintf(stderr, "\nERROR: Missing argument after %s\n\n",argv[i]);
				exit(0);	
			}

			continue;
		}
		
		if(!strcmp(argv[i], "-iwi")) 
		{ 
			flagCheck (argv, i, flagVector, 37);

			if (i!=argc-1 && argv[i+1][0]!='-')
			{
				RSDCommandLine->imageWidth = (unsigned int)atoi(argv[++i]);
			}
			else
			{
				fprintf(stderr, "\nERROR: Missing argument after %s\n\n",argv[i]);
				exit(0);	
			}

			continue;
		}
		
		if(!strcmp(argv[i], "-e")) 
		{ 
			flagCheck (argv, i, flagVector, 38);

			if (i!=argc-1 && argv[i+1][0]!='-')
			{
				int epochs = atoi(argv[++i]);
				if(epochs<=0)
				{
					fprintf(stderr, "\nERROR: Invalid argument after %s\n\n",argv[i-1]);
					exit(0);
				}
				RSDCommandLine->epochs = epochs;
			}
			else
			{
				fprintf(stderr, "\nERROR: Missing argument after %s\n\n",argv[i-1]);
				exit(0);	
			}
			continue;
		}
				
		/*if(!strcmp(argv[i], "-thr")) 
		{ 
			flagCheck (argv, i, flagVector, 39);

			if (i!=argc-1 && argv[i+1][0]!='-')
				RSDCommandLine->threads = (int)atoi(argv[++i]);
				
			else
			{
				fprintf(stderr, "\nERROR: Missing argument after %s\n\n",argv[i]);
				exit(0);	
			}
			
			//assert(RSDCommandLine->threads==1);

			continue;
		}*/		
		
		if(!strcmp(argv[i], "-rng")) 
		{ 
			flagCheck (argv, i, flagVector, 40);

			if (i<argc-2 && i!=argc-1 && argv[i+1][0]!='-' && argv[i+2][0]!='-')
			{
				double bor = atof(argv[++i]);
				RSDCommandLine->gridRngLeBor = (uint64_t) bor;
				
				bor = atof(argv[++i]);
				RSDCommandLine->gridRngRiBor = (uint64_t) bor;
			}
			else
			{
				fprintf(stderr, "\nERROR: Missing argument(s) after %s\n\n",argv[i]);
				exit(0);	
			}

			continue;
		}
		if(!strcmp(argv[i], "-arc")) 
		{ 
			flagCheck (argv, i, flagVector, 41); // neural network architecture

			if (i!=argc-1 && argv[i+1][0]!='-')
			{
				strcpy(RSDCommandLine->networkArchitecture, argv[++i]);
				
				if(RSDCommandLine->enTF==1 && strcmp(RSDCommandLine->networkArchitecture, "SweepNet"))
				{
					fprintf(stderr, "\nERROR: %s is not implemented in TensorFlow. You can either remove \"-arc %s\" or \"-useTF\".\n\n", argv[i], argv[i]);
					exit(0);				
				}
				
				
				if(!is_valid_NN_architecture(RSDCommandLine->networkArchitecture))
				{
					fprintf(stderr, "\nERROR: Invalid argument after -arc (unknown neural network architecture %s)\n\n",argv[i]);
					exit(0);
				}				
			}
			else
			{
				fprintf(stderr, "\nERROR: Missing argument after %s\n\n",argv[i]);
				exit(0);	
			}
	
			continue;
		}
		
		if(!strcmp(argv[i], "-typ")) 
		{ 
			flagCheck (argv, i, flagVector, 42);

			if (i!=argc-1 && argv[i+1][0]!='-')
			{	
				if((strlen(argv[i+1])!=1) || ((strlen(argv[i+1])==1)&&(argv[i+1][0]!='0' && argv[i+1][0]!='1' && argv[i+1][0]!='2' && argv[i+1][0]!='3')))
				{
					fprintf(stderr, "\nERROR: Invalid argument after %s\n\n",argv[i]);
					exit(0);	
				}

				RSDCommandLine->imgDataType = atoi(argv[++i]);				
			}
			else
			{
				fprintf(stderr, "\nERROR: Missing argument after %s\n\n",argv[i]);
				exit(0);	
			}

			continue;
		}
		
		if(!strcmp(argv[i], "-pci")) 
		{ 
			flagCheck (argv, i, flagVector, 43);

			if (i!=argc-1 && argv[i+1][0]!='-')
			{	
				RSDCommandLine->numOfPositiveClasses = (int)atoi(argv[++i]);
				
				if(!(RSDCommandLine->numOfPositiveClasses>=1 && RSDCommandLine->numOfPositiveClasses<=2))
				{
					fprintf(stderr, "\nERROR: Unsupported number of positive classes (%s)!\n\n",argv[i]);
					exit(0);
				}
				else
				{
					RSDCommandLine->positiveClassIndex = (int*)rsd_malloc(sizeof(int)*RSDCommandLine->numOfPositiveClasses);
					assert(RSDCommandLine->positiveClassIndex!=NULL);
					
					for(j=0;j<RSDCommandLine->numOfPositiveClasses;j++)
					{
						if (i!=argc-1 && argv[i+1][0]!='-')
						{
							RSDCommandLine->positiveClassIndex[j] = (int)atoi(argv[++i]);
						}
						else
						{
							fprintf(stderr, "\nERROR: Missing argument after %s (-pci)\n\n",argv[i]);
							exit(0);						
						}
					}				
				}
			}	
			else
			{
				fprintf(stderr, "\nERROR: Missing argument after %s\n\n",argv[i]);
				exit(0);	
			}

			continue;
		}
		
		if(!strcmp(argv[i], "-cl4")) // class-pair associations for 2x2 model (SweepNetRecombination) 
		{ 
			flagCheck (argv, i, flagVector, 44); 

			if (i!=argc-1 && argv[i+1][0]!='-')
			{
				RSDCommandLine->numberOfClasses = 4;
				
				static const char * const validLabelList[] = {"label00", "label01", "label10", "label11"}; 
				
				RSDCommandLine->classLabelList = (char**)rsd_malloc(sizeof(char*)*RSDCommandLine->numberOfClasses); // this must be the true class
				assert(RSDCommandLine->classLabelList!=NULL);
				
				RSDCommandLine->classPathList = (char**)rsd_malloc(sizeof(char*)*RSDCommandLine->numberOfClasses);
				assert(RSDCommandLine->classPathList!=NULL);
				
				for(j=0;j<RSDCommandLine->numberOfClasses;j++)
				{
					if (i!=argc-1 && argv[i+1][0]!='-')
					{
						RSDCommandLine->classLabelList[j] = (char*)rsd_malloc(sizeof(char)*STRING_SIZE);
						assert(RSDCommandLine->classLabelList[j]!=NULL);
						
						RSDCommandLine->classPathList[j] = (char*)malloc(sizeof(char)*STRING_SIZE);
						assert(RSDCommandLine->classPathList[j]!=NULL);
						
						strcpy(tstring, argv[++i]);
						
						int suc = split_string (tstring, RSDCommandLine->classLabelList[j], RSDCommandLine->classPathList[j], '=');
											
						if(suc!=1)
						{
							fprintf(stderr, "\nERROR: Invalid format string \"%s\" (missing or wrong delimiter, '=')\n\n",argv[i]);
							exit(0);
						}
						
						if(strcmp(RSDCommandLine->classLabelList[j], validLabelList[j]))
						{
							fprintf(stderr, "\nERROR: Invalid label \"%s\" given with -cl4 (expected \"%s\", exepected label order: \"%s\", \"%s\", \"%s\", \"%s\")\n\n", RSDCommandLine->classLabelList[j], validLabelList[j], validLabelList[0], validLabelList[1], validLabelList[2], validLabelList[3]);
							exit(0);								
						}					
					}
					else
					{
						fprintf(stderr, "\nERROR: Missing argument after %s\n\n",argv[i]);
						exit(0);
					}			
				}
			}
			else
			{
				fprintf(stderr, "\nERROR: Missing argument after %s\n\n",argv[i]);
				exit(0);	
			}

			continue;
		}		
#endif
		/*if(!strcmp(argv[i], "-set")) 
		{ 
			if (i!=argc-1)
				setIndexValid = atoi(argv[++i]);
			else
			{
				fprintf(stderr, "ERROR: Missing argument after %s\n\n",argv[i]);
				exit(0);	
			}

			continue;
		}*/

		fprintf(stderr, "\nERROR: Unrecognized input parameter %s\n\n",argv[i]);
		exit(0);
	}
	
	// Checks

	if(!strcmp(RSDCommandLine->runName, "\0"))
	{
		fprintf(stderr, "\nERROR: Missing required input parameter -n\n\n");
		exit(0);	
	}
	
#ifdef _RSDAI
	assert(info_exists==-1);
#else	
	if(info_exists==1) 
	{
		strcpy(tstring, "RAiSD_Info.");
		strcat(tstring, RSDCommandLine->runName);
			
		if(RSDCommandLine->overwriteOutput==0)
		{
			fprintf(stderr, "\nERROR: Output info file %s exists. Use -f to overwrite it.\n\n", tstring); 
			exit(0);
		}
		else
		{
			RAiSD_Info_FP = fopen(tstring, "w");
			assert(RAiSD_Info_FP!=NULL);
		}
	}
#endif

	if(!flagVector[CO_FLAG_INDEX] || (flagVector[CO_FLAG_INDEX] && co_mode!=1))
	{
		if(!strcmp(RSDCommandLine->inputFileName, "\0"))
		{
			fprintf(stderr, "\nERROR: Missing required input parameter -I\n\n");
			exit(0);	
		}
		else
		{
#ifdef _RSDAI		
			if(RSDCommandLine->opCode==OP_CREATE_IMAGES || RSDCommandLine->opCode==OP_USE_CNN)
			{
				FILE * inputFileExists = fopen(RSDCommandLine->inputFileName, "r");
				
				if(inputFileExists==NULL)
				{
					fprintf(stderr, "\nERROR: Input file %s not found!\n\n", RSDCommandLine->inputFileName);
					exit(0);
				}
				
				assert(inputFileExists!=NULL); // file exists check
				fclose(inputFileExists);
			}
#else
			FILE * inputFileExists = fopen(RSDCommandLine->inputFileName, "r");
			
			if(inputFileExists==NULL)
			{
				fprintf(stderr, "\nERROR: Input file %s not found!\n\n", RSDCommandLine->inputFileName);
				exit(0);
			}
				
			assert(inputFileExists!=NULL); // file exists check
			fclose(inputFileExists);
#endif
		}
	}

	if(strcmp(RSDCommandLine->excludeRegionsFile, "\0"))
	{
		FILE * excludeRegionsFileExists = fopen(RSDCommandLine->excludeRegionsFile, "r");
		assert(excludeRegionsFileExists!=NULL); // file exists check
		fclose(excludeRegionsFileExists);
	}

	if(flagVector[M_FLAG_INDEX] && !(flagVector[Y_FLAG_INDEX]))
	{
		fprintf(stderr, "\nERROR: Missing input parameter -y that is required when -M is used.\n\n");
		exit(0);
	}

	if(RSDCommandLine->vcf2msExtra==VCF2MS_CONVERT && !(flagVector[L_FLAG_INDEX]))
	{
		fprintf(stderr, "\nERROR: Missing input parameter -L that is required when -Q is used.\n\n");
		exit(0);
	}

	if(RSDCommandLine->createPatternPoolMask==1)
		RSDCommandLine->imputePerSNP = 0;

	if(flagVector[CO_FLAG_INDEX])
	{
		assert(co_mode==0 || co_mode==1);

		FILE * commonOutlierFileExists = NULL;

		commonOutlierFileExists = fopen(RSDCommandLine->reportFilenameSweeD, "r");
		assert(commonOutlierFileExists!=NULL); // file exists check
		fclose(commonOutlierFileExists);

		if(RSDCommandLine->positionIndexSweeD<1)
		{
			fprintf(stderr, "\nERROR: Invalid position index after %s (valid: >=1)\n\n", RSDCommandLine->reportFilenameSweeD);
			exit(0);
		}

		if(RSDCommandLine->scoreIndexSweeD<1)
		{
			fprintf(stderr, "\nERROR: Invalid score index after %s (valid: >=1)\n\n", RSDCommandLine->reportFilenameSweeD);
			exit(0);
		}

		if(RSDCommandLine->positionIndexSweeD==RSDCommandLine->scoreIndexSweeD)
		{
			fprintf(stderr, "\nERROR: Same column indices for positions and scores after %s (valid: >=1)\n\n", RSDCommandLine->reportFilenameSweeD);
			exit(0);
		}

		if(co_mode)
		{
			commonOutlierFileExists = fopen(RSDCommandLine->reportFilenameRAiSD, "r");
			assert(commonOutlierFileExists!=NULL); // file exists check
			fclose(commonOutlierFileExists);

			if(RSDCommandLine->positionIndexRAiSD<1)
			{
				fprintf(stderr, "\nERROR: Invalid position index after %s (valid: >=1)\n\n", RSDCommandLine->reportFilenameRAiSD);
				exit(0);
			}

			if(RSDCommandLine->scoreIndexRAiSD<1)
			{
				fprintf(stderr, "\nERROR: Invalid score index after %s (valid: >=1)\n\n", RSDCommandLine->reportFilenameRAiSD);
				exit(0);
			}

			if(RSDCommandLine->positionIndexRAiSD==RSDCommandLine->scoreIndexRAiSD)
			{
				fprintf(stderr, "\nERROR: Same column indices for positions and scores after %s (valid: >=1)\n\n", RSDCommandLine->reportFilenameRAiSD);
				exit(0);
			}
		}
	}
	
#ifdef _RSDAI
	if (flagVector[NN_ARC_FLAG_INDEX] && RSDCommandLine->opCode!=OP_TRAIN_CNN)
	{
		fprintf(stderr, "\nERROR: Remove -arc. It is only used in MDL-GEN mode!\n\n");
		exit(0);	
	}

	if(flagVector[CLASS_PAIRINGS_4] && RSDCommandLine->opCode!=OP_TRAIN_CNN)
	{
		fprintf(stderr, "\nERROR: Remove -clp. It is only used in MDL-GEN mode!\n\n");
		exit(0);	
	}
	
	if(flagVector[CLASS_PAIRINGS_4] && strcmp(RSDCommandLine->networkArchitecture, ARC_SWEEPNETRECOMB))
	{
		fprintf(stderr, "\nERROR: -cl4 is only used with network architecture %s!\n\n", ARC_SWEEPNETRECOMB);
		exit(0);	
	}
	
	if(!flagVector[CLASS_PAIRINGS_4] && !strcmp(RSDCommandLine->networkArchitecture, ARC_SWEEPNETRECOMB))
	{
		fprintf(stderr, "\nERROR: -cl4 is required with network architecture %s!\n\n", ARC_SWEEPNETRECOMB);
		exit(0);	
	}

	if (flagVector[CL_TEST_PATH_FLAG_INDEX] && RSDCommandLine->opCode!=OP_TEST_CNN)
	{
		fprintf(stderr, "\nERROR: Remove -clp. It is only used in MDL-TST mode!\n\n");
		exit(0);	
	}	
	
	if(flagVector[DATA_TYPE_INDEX] && (RSDCommandLine->opCode!=OP_CREATE_IMAGES))
	{
		fprintf(stderr, "\nERROR: Remove -typ. It is only used in IMG-GEN mode for data generation!\n\n");
		exit(0);	
	}	
	
	if(RSDCommandLine->enBinFormat==1 && (RSDCommandLine->opCode!=OP_CREATE_IMAGES))
	{
		fprintf(stderr, "\nERROR: Remove -bin. It is only used in IMG-GEN mode for data generation!\n\n");
		exit(0);	
	}
	
	/*if(RSDCommandLine->trnObjDetection==1 && (RSDCommandLine->opCode!=OP_CREATE_IMAGES))
	{
		fprintf(stderr, "\nERROR: Remove -det. It is only used in IMG-GEN mode for data generation!\n\n");
		//exit(0);	
	}*/
	
	/*if(RSDCommandLine->trnObjDetection==1 && RSDCommandLine->enBinFormat==0)
	{
		fprintf(stderr, "\nERROR: Remove -det or add -bin. -det is only used with -bin to generate binary data to train for detection!\n\n");
		exit(0);	
	}*/
	
	/*if(RSDCommandLine->trnObjDetection==1 && (!(flagVector[GRID_FLAG_INDEX])))
	{
		fprintf(stderr, "\nERROR: Missing input parameter -G that is required when -det is used!\n\n");
		//exit(0);
	}*/
	
	if (flagVector[IMG_CLASS_LABEL_FLAG_INDEX] && (RSDCommandLine->opCode!=OP_CREATE_IMAGES))
	{
		fprintf(stderr, "\nERROR: Remove -icl. The class label (-icl %s) is only used in IMG-GEN mode!\n\n", RSDCommandLine->imageClassLabel);
		exit(0);	
	}
	
	if (flagVector[IMG_TARGET_SITE_FLAG_INDEX] && (RSDCommandLine->opCode!=OP_CREATE_IMAGES))
	{
		fprintf(stderr, "\nERROR: Remove -its. It is only used in IMG-GEN mode!\n\n");
		exit(0);	
	}	
	
	if ((!(flagVector[IMG_TARGET_SITE_FLAG_INDEX])) && (RSDCommandLine->opCode==OP_CREATE_IMAGES))
	{
		fprintf(stderr, "\nERROR: Missing input parameter -its that is required when \"-op IMG-GEN\" is used!\n\n");
		exit(0);	
	}
	
	if (((flagVector[IMG_TARGET_SITE_FLAG_INDEX])) && (RSDCommandLine->opCode==OP_CREATE_IMAGES))
	{
		if(RSDCommandLine->imageTargetSite<=0ull)
		{
			fprintf(stderr, "\nERROR: Invalid -its position (valid: >= 1)\n\n");
			exit(0);
		}
		if(RSDCommandLine->regionLength!=0ull && RSDCommandLine->imageTargetSite>=RSDCommandLine->regionLength)
		{
			fprintf(stderr, "\nERROR: Invalid -its position (valid: < region_length)\n\n");
			exit(0);
		}		
	}	
	
	if ((!(flagVector[IMG_CLASS_LABEL_FLAG_INDEX])) && (RSDCommandLine->opCode==OP_CREATE_IMAGES))
	{
		fprintf(stderr, "\nERROR: Missing input parameter -icl that is required when \"-op IMG-GEN\" is used!\n\n");
		exit(0);	
	}
	
	if ((!(flagVector[MDL_PATH_FLAG_INDEX])) && (RSDCommandLine->opCode==OP_TEST_CNN || RSDCommandLine->opCode==OP_USE_CNN))
	{
		fprintf(stderr, "\nERROR: Missing input parameter -mdl that is required when \"-op MDL-TST\" or \"-op SWP-SCN\" is used!\n\n");
		exit(0);	
	}
	
	if ((!(flagVector[CL_TEST_PATH_FLAG_INDEX])) && (RSDCommandLine->opCode==OP_TEST_CNN))
	{
		fprintf(stderr, "\nERROR: Missing input parameter -clp that is required when \"-op MDL-TST\" is used!\n\n");
		exit(0);	
	}
	
	if ((!(flagVector[GRID_FLAG_INDEX])) && (RSDCommandLine->opCode==OP_USE_CNN))
	{
		fprintf(stderr, "\nERROR: Missing input parameter -G that is required when \"-op SWP-SCN\" is used!\n\n");
		exit(0);	
	}	
	
	if(RSDCommandLine->opCode==OP_USE_CNN)
	{
		if(!(flagVector[POSITIVE_CLASS_FLAG_INDEX]) && !(flagVector[POSITIVE_CLASS_FLAG_INDEX2]))
		{
			fprintf(stderr, "\nERROR: Missing input parameter -pci or -pci2 that is required when \"-op SWP-SCN\" is used!\n\n");
			exit(0);
		}
		
		if((flagVector[POSITIVE_CLASS_FLAG_INDEX]) && (flagVector[POSITIVE_CLASS_FLAG_INDEX2]))
		{
			fprintf(stderr, "\nERROR: Use either -pci or -pci2 depending on the CNN architecture. Using both is not valid!\n\n");
			exit(0);
		}	
	}
	else
	{
		if(flagVector[POSITIVE_CLASS_FLAG_INDEX] || flagVector[POSITIVE_CLASS_FLAG_INDEX2])
		{
			fprintf(stderr, "\nERROR: Remove -pci. The positive class index command-line flag is only used in SWP-SCN mode!\n\n");
			exit(0);		
		}
	}	
	
	/* Info file check for RSDAI */
	
	strcpy(tstring, "RAiSD_Info.");
	strcat(tstring, RSDCommandLine->runName);
	
	if(RSDCommandLine->opCode==OP_CREATE_IMAGES)
	{		
		strcat(tstring, ".");
		strcat(tstring, RSDCommandLine->imageClassLabel);
	}
	
	RAiSD_Info_FP = fopen(tstring, "r");
	
	if(RAiSD_Info_FP!=NULL && RSDCommandLine->overwriteOutput==0)
	{
		fclose(RAiSD_Info_FP);
		fprintf(stderr, "\nERROR: Output info file %s exists. Use -f to overwrite it.\n\n", tstring); 
		exit(0);
	}
	else
	{
		if(RAiSD_Info_FP!=NULL)
			fclose(RAiSD_Info_FP);

		RAiSD_Info_FP = fopen(tstring, "w");
		assert(RAiSD_Info_FP!=NULL);
	}
#endif
	free(flagVector);
}

void RSDCommandLine_print(int argc, char ** argv, FILE * fpOut)
{
	if(fpOut==NULL)
		return;

	fprintf(fpOut, " Command line        :\t");
	int i;
	for(i=0; i<argc; ++i)
	{
		fprintf(fpOut, "%s ", argv[i]);
	}
	fprintf(fpOut, "\n");

	fflush(fpOut);
}

void RSDCommandLine_printInfo (RSDCommandLine_t * RSDCommandLine, FILE * fpOut)
{
	assert(RSDCommandLine!=NULL);
	
	if(fpOut==NULL)
		return;

#ifdef _RSDAI		
	switch (RSDCommandLine->opCode)
	{
		case OP_DEF:
			fprintf(fpOut, " Operation mode      :\tmu-statistic scan\n");
			fprintf(fpOut, " Window width        :\t%d\n", (int)RSDCommandLine->windowSize);
			break;
			
		case OP_CREATE_IMAGES:
			fprintf(fpOut, " Operation mode      :\tdata generation\n");
			fprintf(fpOut, " Window width        :\t%d (image width)\n", (int)RSDCommandLine->windowSize);
			break;
			
		case OP_TRAIN_CNN:
			fprintf(fpOut, " Operation mode      :\tmodel generation (training)\n");
			break;
			
		case OP_TEST_CNN:
			fprintf(fpOut, " Operation mode      :\tmodel testing (inference)\n");
			break;
			
		case OP_USE_CNN:
			fprintf(fpOut, " Operation mode      :\tCNN-based scan\n");
			break;
			
		default:
			assert(0);
			break;	
	}	
#else	
	fprintf(fpOut, " Window width        :\t%d\n", (int)RSDCommandLine->windowSize);
#endif	
	fflush(fpOut);
}

void RSDCommandLine_printWarnings (RSDCommandLine_t * RSDCommandLine, int argc, char ** argv, void * RSDDataset, FILE * fpOut)
{
	if(fpOut==NULL)
		return;

	assert(RSDCommandLine!=NULL);
	assert(RSDDataset!=NULL);

	RSDDataset_t * myRSDDataset = (RSDDataset_t *)RSDDataset;
	
	int i=0;

	for(i=1; i<argc; ++i)
	{
		if(!strcmp(argv[i], "-L") && !strcmp(myRSDDataset->inputFileFormat, "vcf.gz")) 
		{ 
			if(RSDCommandLine->vcf2msExtra!=VCF2MS_CONVERT) // -L is not used with VCF in regular exec. mode, it is required for vcf2ms conversion
			{
				fprintf(fpOut, "\n WARNING: Argument -L is not used with vcf.gz files and will be ignored!\n");
				fflush(fpOut);
			}
		}

		if(!strcmp(argv[i], "-L") && !strcmp(myRSDDataset->inputFileFormat, "vcf")) 
		{ 
			if(RSDCommandLine->vcf2msExtra!=VCF2MS_CONVERT) // -L is not used with VCF in regular exec. mode, it is required for vcf2ms conversion
			{
				fprintf(fpOut, "\n WARNING: Argument -L is not used with vcf files and will be ignored!\n");
				fflush(fpOut);
			}
		}

		if(!strcmp(argv[i], "-B") && !strcmp(myRSDDataset->inputFileFormat, "ms")) 
		{ 
			fprintf(fpOut, "\n WARNING: Argument -B is not used with ms files and will be ignored!\n");
			fflush(fpOut);
		}
	}
}

void RSDCommandLine_printExponents (RSDCommandLine_t * RSDCommandLine, FILE * fpOut)
{
	if(fpOut==NULL)
		return;

	assert(RSDCommandLine!=NULL);

#ifdef _RSDAI	
	if(RSDCommandLine->opCode==OP_DEF)
	{
		fprintf(fpOut, " var-exp             :\t%.1f\n", RSDCommandLine->muVarExp);
		fprintf(fpOut, " sfs-exp             :\t%.1f\n", RSDCommandLine->muSfsExp);
		fprintf(fpOut, " ld-exp              :\t%.1f\n", RSDCommandLine->muLdExp);
	}	
#else		
	fprintf(fpOut, " var-exp            :\t%.1f\n", RSDCommandLine->muVarExp);
	fprintf(fpOut, " sfs-exp            :\t%.1f\n", RSDCommandLine->muSfsExp);
	fprintf(fpOut, " ld-exp             :\t%.1f\n", RSDCommandLine->muLdExp);	
#endif	


}

