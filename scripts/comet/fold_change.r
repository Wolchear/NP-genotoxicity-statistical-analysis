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

summary_by_sample <- aggregate(
  Mean ~ Sample + Dose,
  data = dose_data,
  FUN = function(x) c(mean = mean(x), sd = sd(x))
)

summary_by_sample <- do.call(data.frame, summary_by_sample)

control_mean <- mean(dose_data$Mean[dose_data$Sample == "Control"])

summary_by_sample$diff_vs_control <- summary_by_sample$Mean.mean - control_mean
summary_by_sample$fold_vs_control <- summary_by_sample$Mean.mean / control_mean

summary_by_sample