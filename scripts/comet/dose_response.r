suppressPackageStartupMessages(library(optparse))

option_list <- list(
  make_option(c("--input"), type = "character", help = "Data table")
)

opt <- parse_args(OptionParser(option_list = option_list))

data <- read.csv(
    opt$input,
    sep=','
)
data$Dose <- suppressWarnings(as.numeric(data$Sample))
data$Dose[data$Sample == "Control"] <- 0
dose_data <- subset(data, Sample != "Positive_Control")

model <- lm(Mean ~ log10(Dose + 1), data = dose_data)
summary(model)