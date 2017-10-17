# functions to use in the reports

mycat <- function(text){
    # print formatted text in Rmd
    cat(gsub(pattern = "\n", replacement = "  \n", x = text))
}

get_firstline <- function(my_file){
    # read the first line of a file, if present
    if(length(readLines(my_file)) >= 1){
        file_contents <- readLines(my_file)[1]
    } else {
        file_contents <- NA
    }
    return(file_contents)
}

read_ANNOVAR <- function(input_file, ANNOVAR_suffix = ".hg19_multianno.txt"){
    # read an annotation table from ANNOVAR
    # annot_df <- do.call(rbind, lapply(X = MuTect2_annot_files, FUN = read_ANNOVAR))
    
    # get sample ID from filename
    sampleID <- gsub(pattern = ANNOVAR_suffix, replacement = '', 
                     x = basename(input_file))
    df <- read.delim(file = input_file, header = TRUE, sep = '\t', 
                     check.names = FALSE, na.strings = c('.'))
    
    # add sample ID
    df[["Sample"]] <- sampleID
    
    # remove duplicated rows
    df <- df[which(! duplicated(df)), ]
    return(df)
}

vcf_header_lineno <- function(vcf_file){
    # find the position of the last header line in the VCF file
    # warning: needs to read the entire VCF into memory
    lineno <- 0
    lines <- readLines(vcf_file)
    lineno <- max(which(grepl("^##", lines)))
    return(lineno)
}

read_og_vcf <- function(vcf_file, file_suffix = '.vcf$'){
    # read a .VCF formatted file
    # from the sns pipeline output
    # vcf_df <- do.call(rbind, lapply(X = MuTect2_vcf_files, FUN = read_og_vcf))
    
    # get sample ID from filename
    sampleID <- gsub(pattern = file_suffix, replacement = '', x = basename(vcf_file))
    df <- read.delim(file = vcf_file, header = TRUE, sep = '\t', 
                     check.names = FALSE, skip = vcf_header_lineno(vcf_file))
    # add sample ID
    df[["Sample"]] <- sampleID
    
    # remove duplicated rows
    df <- df[which(! duplicated(df)), ]
    return(df)
}