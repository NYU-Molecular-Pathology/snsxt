#!/usr/bin/env Rscript

# functions to use in snsxt task R scripts

# ~~~~~ PACKAGES ~~~~~ # 
library("optparse")
library("tools")


timestamp <- format(Sys.time(), "%Y-%m-%d-%H-%M-%S")
logfile <- file.path(".", sprintf("report_log.%s.txt", timestamp))

# default value, overwrite in scripts after 'source' to enable logfile output
hard_log <- FALSE

# ~~~~~ FUNCTIONS ~~~~~ # 
tsprintf <- function(fmt, ...){
    # print a formatted message with timestamp
    # base message
    m <- sprintf(fmt, ...)
    # message with timestamp
    tm <- sprintf('[%s] %s', format(Sys.time(), "%H:%M:%S"), m)
    # emit message
    message(tm)
    # add to log file
    if(isTRUE(hard_log)) cat(sprintf("%s\n", tm), file = logfile, append = TRUE)
}

msprintf <- function(fmt, ...) {
    message(sprintf(fmt, ...))
}

mycat <- function(text){
    # print formatted text in Rmd
    cat(gsub(pattern = "\n", replacement = "  \n", x = text))
}


make_output_filename <- function(prefix, suffix, sep = '_'){
    # create an output filename, testing for conditional length of prefix
    if(nchar(prefix) > 0){
        return(paste(prefix, suffix, sep = sep))
    } else {
        return(suffix)
    }
}
