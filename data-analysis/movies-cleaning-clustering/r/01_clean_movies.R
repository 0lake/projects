# Cleaning of the movies dataset (10 000 rows, 13 columns).
# Input : data/data.csv         (raw file from Kaggle, see data/README.md)
# Output: data/movies_clean.csv (input of the Python clustering step)
#
#   Rscript r/01_clean_movies.R

suppressPackageStartupMessages({
  library(dplyr)
  library(tidyr)
  library(ggplot2)
  library(viridis)
})

input_path  <- "data/data.csv"
output_path <- "data/movies_clean.csv"
numeric_cols <- c("Movie.Rating", "Votes", "MetaScore", "Gross", "Run.Time.in.minutes")

movies <- read.csv(input_path)
str(movies)
summary(movies)

# ---- 1. Missing values -------------------------------------------------------
# NA in numeric columns, but empty strings in text columns are NOT counted as NA
# by default, so Certification looks complete until "" is converted.
colSums(is.na(movies))
movies[movies == ""] <- NA
colSums(is.na(movies))   # MetaScore 2026, Gross 2915, Certification 369

df_miss <- data.frame(variable = names(movies), missing = sapply(movies, function(x) sum(is.na(x))))
ggplot(df_miss, aes(x = reorder(variable, missing), y = missing, fill = missing)) +
  geom_col(width = 0.7, show.legend = FALSE) +
  coord_flip() +
  scale_fill_viridis_c(option = "plasma") +
  geom_text(aes(label = missing), hjust = -0.1, size = 3.5) +
  labs(title = "Missing values by column", x = NULL, y = "NA count") +
  theme_minimal(base_size = 13)

# ---- 2. Outliers and duplicates ----------------------------------------------
par(mfrow = c(2, 3))
for (col in numeric_cols) boxplot(movies[[col]], main = paste("Boxplot:", col), ylab = col)
par(mfrow = c(1, 1))

nrow(movies[duplicated(movies), ])   # 0 fully duplicated rows

# ---- 3. Uninformative columns ------------------------------------------------
# X is a row index, Movie.Name is almost unique (9632 of 10000).
dominant_share <- function(x) max(table(x)) / sum(table(x))
sapply(movies, dominant_share)

movies_clean <- subset(movies, select = -c(X))

# ---- 4. Imputation -----------------------------------------------------------
# Median for numeric columns, "Unknown" for Certification.
# Note: this makes ~34% of Gross and ~24% of MetaScore equal to one constant.
movies_clean <- movies_clean %>%
  mutate(Certification = na_if(Certification, "")) %>%
  replace_na(list(
    MetaScore     = median(movies_clean$MetaScore, na.rm = TRUE),
    Gross         = median(movies_clean$Gross, na.rm = TRUE),
    Certification = "Unknown"
  ))
stopifnot(sum(is.na(movies_clean)) == 0)

# ---- 5. Outliers: 1.5 * IQR rule on every numeric column ---------------------
within_iqr <- function(x) {
  q <- quantile(x, c(0.25, 0.75))
  x >= q[1] - 1.5 * IQR(x) & x <= q[2] + 1.5 * IQR(x)
}
movies_clean <- movies_clean %>%
  filter(
    within_iqr(Movie.Rating), within_iqr(Votes), within_iqr(MetaScore),
    within_iqr(Gross), within_iqr(Run.Time.in.minutes)
  )
nrow(movies_clean)   # 7945 rows remain

par(mfrow = c(2, 3))
for (col in numeric_cols) boxplot(movies_clean[[col]], main = paste("Boxplot:", col), ylab = col)
par(mfrow = c(1, 1))

barplot(table(movies_clean$Certification), main = "Distribution of Movie Certification",
        col = "steelblue", ylab = "Count")

# ---- 6. Export ---------------------------------------------------------------
write.csv(movies_clean, file = output_path, row.names = FALSE)
file.exists(output_path)
