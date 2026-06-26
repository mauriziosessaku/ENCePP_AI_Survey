#!/usr/bin/env Rscript
# =============================================================================
# analyse.R  --  ENCePP AI Survey: descriptive analysis (R replication)
# -----------------------------------------------------------------------------
# Mirrors python/02_analyse.py. Reads the tidy CSV produced by the cleaning
# step and reproduces all counts cited in the Results section, writing figures
# to figures/ and Table 1 to outputs/.
#
# Usage:  Rscript R/analyse.R
# Deps :  tidyverse, ggplot2, scales  (see renv.lock / DESCRIPTION)
# =============================================================================

suppressPackageStartupMessages({
  library(tidyverse)
  library(scales)
})

here   <- normalizePath(file.path(dirname(sys.frame(1)$ofile %||% "."), ".."))
if (!dir.exists(file.path(here, "data"))) here <- getwd()
clean  <- file.path(here, "data", "survey_clean.csv")
figdir <- file.path(here, "figures")
outdir <- file.path(here, "outputs")
dir.create(figdir, showWarnings = FALSE, recursive = TRUE)
dir.create(outdir, showWarnings = FALSE, recursive = TRUE)

# House style ----------------------------------------------------------------
NAVY <- "#1C3557"; MID <- "#2E6DA4"; TEAL <- "#1A8FA0"
GOLD <- "#C9852A"; PURPLE <- "#6C3483"
theme_encepp <- function() {
  theme_minimal(base_size = 11) +
    theme(
      plot.title    = element_text(face = "bold", colour = NAVY, size = 13),
      axis.title    = element_text(colour = NAVY),
      panel.grid.minor = element_blank(),
      panel.grid.major.y = element_blank(),
      legend.position = "bottom"
    )
}

df  <- readr::read_csv(clean, show_col_types = FALSE)
PE  <- dplyr::filter(df, track_code == "PE")
PV  <- dplyr::filter(df, track_code == "PV")
N   <- nrow(df); nPE <- nrow(PE); nPV <- nrow(PV)
message(sprintf("Loaded %d respondents (PE=%d, PV=%d)", N, nPE, nPV))

# --- Figure 1: adoption ------------------------------------------------------
adopt_lab <- c("yes-routine" = "Routine use", "yes-pilot" = "Pilot / evaluation",
               "no-planned" = "Planning (<2 yr)", "no-none" = "No plans",
               "dk" = "Don't know")
adopt <- df %>% count(adoption_code) %>%
  mutate(label = adopt_lab[adoption_code],
         label = factor(label, levels = rev(adopt_lab)))
p1 <- ggplot(adopt, aes(label, n)) +
  geom_col(fill = TEAL, width = 0.7) +
  geom_text(aes(label = n), hjust = -0.3, fontface = "bold", colour = NAVY) +
  coord_flip() +
  labs(title = sprintf("Figure 1. Organisational AI adoption status (N=%d)", N),
       x = NULL, y = "Number of respondents") +
  theme_encepp()
ggsave(file.path(figdir, "figure1_adoption_R.png"), p1, width = 7, height = 3.2, dpi = 140)

# --- Figure 5: barriers (I-1) ------------------------------------------------
bar_lab <- c(computing = "Computing resources", data = "Data access",
             expertise = "AI expertise", governance = "Governance/reg. clarity",
             funding = "Funding", maintenance = "System maintenance",
             leadership = "Leadership support", privacy = "Privacy/security/ethics",
             culture = "Organisational culture", none = "No barriers",
             "other-barrier" = "Other", dk = "Don't know")
barr <- df %>% filter(qi1 != "") %>% count(qi1) %>%
  mutate(label = bar_lab[qi1]) %>% arrange(n) %>%
  mutate(label = factor(label, levels = label))
p5 <- ggplot(barr, aes(label, n)) +
  geom_col(fill = NAVY, width = 0.7) +
  geom_text(aes(label = n), hjust = -0.3, fontface = "bold", colour = NAVY) +
  coord_flip() +
  labs(title = sprintf("Figure 5. Single most critical barrier (N=%d)", N),
       x = NULL, y = "Number of respondents") +
  theme_encepp()
ggsave(file.path(figdir, "figure5_barriers_R.png"), p5, width = 7, height = 4, dpi = 140)

# --- Figure 6: perceptions & terminology means by track ----------------------
perc_keys <- c("p_genai","p_ethics","p_jobs","p_reg","p_ready","p_trust")
perc_lab  <- c("GenAI potential","Ethics/transparency","Job security threat",
               "Regulatory clarity","Org. readiness","Trust in outputs")
mean_by_track <- function(data, keys, labs) {
  map2_dfr(keys, labs, function(k, l) {
    tibble(item = l,
           PE = mean(PE[[k]], na.rm = TRUE),
           PV = mean(PV[[k]], na.rm = TRUE))
  })
}
perc <- mean_by_track(df, perc_keys, perc_lab) %>%
  pivot_longer(c(PE, PV), names_to = "track", values_to = "mean")
p6 <- ggplot(perc, aes(reorder(item, mean), mean, fill = track)) +
  geom_col(position = position_dodge(0.8), width = 0.7) +
  scale_fill_manual(values = c(PE = TEAL, PV = PURPLE)) +
  coord_flip(ylim = c(0, 5)) +
  labs(title = "Figure 6a. Perceptions, by track (mean Likert 1-5)",
       x = NULL, y = "Mean score", fill = NULL) +
  theme_encepp()
ggsave(file.path(figdir, "figure6a_perceptions_R.png"), p6, width = 7, height = 4, dpi = 140)

# --- Table 1: respondent profile --------------------------------------------
profile_block <- function(field, name) {
  df %>% filter(.data[[field]] != "") %>%
    count(.data[[field]], name = "Overall") %>%
    rename(Level = 1) %>%
    mutate(Characteristic = name,
           `Overall %` = round(100 * Overall / N, 1)) %>%
    arrange(desc(Overall))
}
tab1 <- bind_rows(
  profile_block("role", "Role"),
  profile_block("organisation", "Organisation"),
  profile_block("country", "Country")
) %>% select(Characteristic, Level, Overall, `Overall %`)
readr::write_csv(tab1, file.path(outdir, "table1_respondent_profile_R.csv"))

message("R pipeline complete. Figures and Table 1 written.")
