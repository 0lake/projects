# 01_build_network.R
# Loads the five Kaggle CSV files, cleans them, builds the co-appearance network
# and 12 cumulative chronological snapshots, and computes descriptive metrics.
# Input:  data/*.csv      Output: data/networks_per_snapshot.rds, data/*.csv
# Run from the project folder:  Rscript analysis/01_build_network.R

# Packages (reconstructed from the functions used in the report)
library(dplyr)
library(tidyr)
library(igraph)
library(ggplot2)
library(knitr)
library(kableExtra)

# === 1. Введение ===


# === 1.1 Контекст и мотивация ===


# === 1.2 Исследовательский вопрос ===


# === 1.3 Описание датасета ===


# === 1.4 Структура данных ===

games        <- read.csv("data/games.csv")
characters   <- read.csv("data/characters.csv")
appearance   <- read.csv("data/gameAppearance.csv")
scenes       <- read.csv("data/scenes.csv")
interactions <- read.csv("data/interactions.csv")

cat("games.csv")

kable(head(games), caption = "Первые строки games.csv") %>%
  kable_styling(bootstrap_options = c("striped", "hover", "condensed"), full_width = FALSE)

kable(head(characters), caption = "Первые строки characters.csv") %>%
  kable_styling(bootstrap_options = c("striped", "hover", "condensed"), full_width = FALSE)

kable(head(interactions), caption = "Первые строки interactions.csv") %>%
  kable_styling(bootstrap_options = c("striped", "hover", "condensed"), full_width = FALSE)

cat("Размеры датасетов:\n")

sizes <- data.frame(
  Файл        = c("games", "characters", "appearance", "scenes", "interactions"),
  Строк       = c(nrow(games), nrow(characters), nrow(appearance), nrow(scenes), nrow(interactions)),
  Колонок     = c(ncol(games), ncol(characters), ncol(appearance), ncol(scenes), ncol(interactions))
)
kable(sizes, caption = "Размеры исходных датасетов") %>%
  kable_styling(bootstrap_options = c("striped", "hover", "condensed"), full_width = FALSE)


# === 1.5 Распределение обязанностей ===


# === 2. Построение и описание сети ===


# === 2.1 Определение узлов и рёбер ===


# === 2.2 Решения по очистке данных ===


# === 2.2.1 Удаление игр серии Revelations ===

# Запоминаем, сколько игр было до удаления
n_games_before <- nrow(games)

games_filtered <- games %>%
  filter(!grepl("Revelations", title, ignore.case = TRUE))

n_games_after <- nrow(games_filtered)

cat(sprintf("Игр до очистки: %d\nИгр после удаления Revelations: %d\nУдалено: %d\n",
            n_games_before, n_games_after, n_games_before - n_games_after))

kable(games_filtered %>% arrange(chronology_order) %>% select(id, title, year, chronology_order),
      caption = "Игры, включённые в анализ (после удаления Revelations)") %>%
  kable_styling(bootstrap_options = c("striped", "hover", "condensed"), full_width = FALSE)

valid_games <- games_filtered$id

# Фильтруем все таблицы по оставшимся играм
n_inter_before <- nrow(interactions)
n_scenes_before <- nrow(scenes)

interactions <- interactions %>% filter(game_id %in% valid_games)
scenes       <- scenes       %>% filter(game_id %in% valid_games)
appearance   <- appearance   %>% filter(game_id %in% valid_games)

cat(sprintf("\nInteractions до: %d → после: %d (удалено: %d)\n",
            n_inter_before, nrow(interactions), n_inter_before - nrow(interactions)))

cat(sprintf("Scenes до: %d → после: %d (удалено: %d)\n",
            n_scenes_before, nrow(scenes), n_scenes_before - nrow(scenes)))


# === 2.2.2 Фильтрация сцен с одним персонажем ===

scene_chars <- interactions %>%
  group_by(game_id, scene_id) %>%
  summarise(
    chars   = list(unique(character_id)),
    n_chars = length(unique(character_id)),
    .groups = "drop"
  )

cat(sprintf("Всего сцен: %d\n", nrow(scene_chars)))

cat(sprintf("Сцен с 1 персонажем (будут отфильтрованы): %d\n", sum(scene_chars$n_chars < 2)))

cat(sprintf("Сцен с >= 2 персонажами (пойдут в анализ): %d\n", sum(scene_chars$n_chars >= 2)))

# Распределение числа персонажей в сценах
dist_table <- scene_chars %>%
  count(n_chars, name = "кол_во_сцен") %>%
  arrange(n_chars)

kable(dist_table, caption = "Распределение числа персонажей в сценах") %>%
  kable_styling(bootstrap_options = c("striped", "hover", "condensed"), full_width = FALSE)

# Оставляем только сцены с >= 2 персонажами
scene_chars <- scene_chars %>% filter(n_chars >= 2)


# === 2.3 Построение рёбер ===

edges_list <- lapply(seq_len(nrow(scene_chars)), function(i) {
  chars <- scene_chars$chars[[i]]
  if (length(chars) < 2) return(NULL)
  pairs <- t(combn(chars, 2))
  data.frame(from = pairs[, 1], to = pairs[, 2], stringsAsFactors = FALSE)
})

edges_list <- Filter(Negate(is.null), edges_list)
edges_raw  <- do.call(rbind, edges_list)

# Нормализуем порядок (from < to), чтобы не дублировать рёбра
edges_raw <- edges_raw %>%
  mutate(
    from_n = pmin(from, to),
    to_n   = pmax(from, to)
  ) %>%
  select(from = from_n, to = to_n)

# Считаем вес = количество совместных сцен
edges_df <- edges_raw %>%
  group_by(from, to) %>%
  summarise(weight = n(), .groups = "drop")

# Добавляем инверсный вес для расчёта betweenness
edges_df$weight_inv <- 1 / edges_df$weight

cat(sprintf("Всего уникальных рёбер: %d\n", nrow(edges_df)))

# Статистика по весам
weight_summary <- summary(edges_df$weight)
cat("\nСтатистика весов рёбер (количество совместных сцен):\n")

print(weight_summary)

kable(
  edges_df %>% arrange(desc(weight)) %>% head(20),
  caption = "Топ-20 самых тяжёлых рёбер (наибольшее число совместных сцен)"
) %>%
  kable_styling(bootstrap_options = c("striped", "hover", "condensed"), full_width = FALSE)


# === 2.4 Построение таблицы узлов ===

# Узлы — все персонажи, участвующие хотя бы в одном ребре
connected_nodes <- unique(c(edges_df$from, edges_df$to))

nodes_df <- data.frame(id = connected_nodes, stringsAsFactors = FALSE) %>%
  left_join(characters, by = c("id" = "id"))

n_isolated <- nrow(characters) - nrow(nodes_df)

cat(sprintf("Персонажей в characters.csv: %d\n", nrow(characters)))

cat(sprintf("Персонажей в сети (связанных): %d\n", nrow(nodes_df)))

cat(sprintf("Изолированных узлов удалено: %d\n", n_isolated))

# Состав по ролям
role_summary <- nodes_df %>%
  count(role, name = "количество") %>%
  mutate(доля = round(количество / sum(количество) * 100, 1))

kable(role_summary, caption = "Состав узлов по ролям персонажей") %>%
  kable_styling(bootstrap_options = c("striped", "hover", "condensed"), full_width = FALSE)

kable(head(nodes_df, 20), caption = "Первые 20 узлов (персонажей) сети") %>%
  kable_styling(bootstrap_options = c("striped", "hover", "condensed"), full_width = FALSE)


# === 2.5 Построение кумулятивных снимков сети ===

games_ordered <- games_filtered %>%
  arrange(chronology_order)

kable(games_ordered %>% select(id, title, year, chronology_order),
      caption = "Игры в хронологическом порядке (порядок снимков)") %>%
  kable_styling(bootstrap_options = c("striped", "hover", "condensed"), full_width = FALSE)

set.seed(42)

snapshots      <- list()
snapshot_names <- character(0)
metrics_list   <- list()

for (i in seq_len(nrow(games_ordered))) {
  
  current_games <- games_ordered$id[1:i]
  snapshot_name <- paste0("+", games_ordered$title[i])
  if (i == 1) snapshot_name <- games_ordered$title[i]
  
  # Фильтруем interactions для текущего набора игр
  current_interactions <- interactions %>%
    filter(game_id %in% current_games)
  
  # Сцены с >= 2 персонажами
  scene_chars_tmp <- current_interactions %>%
    group_by(game_id, scene_id) %>%
    summarise(
      chars   = list(unique(character_id)),
      n_chars = length(unique(character_id)),
      .groups = "drop"
    ) %>%
    filter(n_chars >= 2)
  
  if (nrow(scene_chars_tmp) == 0) next
  
  # Генерируем пары
  edges_list_tmp <- lapply(seq_len(nrow(scene_chars_tmp)), function(j) {
    chars <- scene_chars_tmp$chars[[j]]
    if (length(chars) < 2) return(NULL)
    pairs <- t(combn(chars, 2))
    data.frame(from = pairs[, 1], to = pairs[, 2], stringsAsFactors = FALSE)
  })
  edges_list_tmp <- Filter(Negate(is.null), edges_list_tmp)
  
  if (length(edges_list_tmp) == 0) next
  
  edges_tmp <- do.call(rbind, edges_list_tmp) %>%
    mutate(
      from_n = pmin(from, to),
      to_n   = pmax(from, to)
    ) %>%
    select(from = from_n, to = to_n) %>%
    group_by(from, to) %>%
    summarise(weight = n(), .groups = "drop")
  
  edges_tmp$weight_inv <- 1 / edges_tmp$weight
  
  # Строим граф
  g <- graph_from_data_frame(edges_tmp, directed = FALSE)
  E(g)$weight     <- edges_tmp$weight
  E(g)$weight_inv <- edges_tmp$weight_inv
  
  # Детектируем сообщества (Louvain)
  set.seed(42)
  comm <- cluster_louvain(g)
  
  # Метрики снимка
  n_nodes    <- vcount(g)
  n_edges    <- ecount(g)
  density    <- edge_density(g)
  avg_degree <- mean(degree(g))
  clust_coef <- transitivity(g, type = "global")
  n_comm     <- length(unique(membership(comm)))
  
  metrics_list[[i]] <- data.frame(
    snapshot     = snapshot_name,
    узлы         = n_nodes,
    рёбра        = n_edges,
    плотность    = round(density, 4),
    avg_degree   = round(avg_degree, 2),
    кластеризация = round(clust_coef, 4),
    сообщества   = n_comm,
    stringsAsFactors = FALSE
  )
  
  snapshots[[i]]    <- g
  snapshot_names[i] <- snapshot_name
}

names(snapshots) <- snapshot_names


# === 2.6 Таблица описательных метрик по снимкам ===

metrics_df <- do.call(rbind, metrics_list)

# Добавляем дельту плотности
metrics_df <- metrics_df %>%
  mutate(
    delta_density = c(NA, round(diff(плотность) / head(плотность, -1) * 100, 1))
  )

# Форматируем для вывода
metrics_display <- metrics_df %>%
  mutate(
    delta_density = ifelse(is.na(delta_density), "—",
                           paste0(ifelse(delta_density > 0, "+", ""), delta_density, "%"))
  ) %>%
  select(
    `Снимок`         = snapshot,
    `Узлы`           = узлы,
    `Рёбра`          = рёбра,
    `Плотность`      = плотность,
    `Δ Плотность`    = delta_density,
    `Avg Degree`     = avg_degree,
    `Кластеризация`  = кластеризация,
    `Сообщества`     = сообщества
  )

kable(metrics_display,
      caption = "Описательные метрики сети по кумулятивным снимкам") %>%
  kable_styling(bootstrap_options = c("striped", "hover", "condensed", "bordered"),
                full_width = TRUE) %>%
  column_spec(1, bold = TRUE) %>%
  column_spec(4, color = "white",
              background = spec_color(metrics_df$плотность, option = "plasma"))


# === 2.7 Итоговый лог очистки данных ===

# Собираем точные цифры для лога
n_revelations_removed     <- n_games_before - n_games_after
n_isolated_removed        <- nrow(characters) - nrow(nodes_df)
n_scenes_single_char      <- sum(scene_chars_tmp_log <- interactions %>%
  group_by(game_id, scene_id) %>%
  summarise(n = length(unique(character_id)), .groups = "drop") %>%
  pull(n) < 2)

cleaning_log <- data.frame(
  Решение = c(
    "Исключить Revelations 1 и 2",
    "Удалить изолированные узлы",
    "Фильтровать сцены с < 2 персонажами",
    "Нормализация порядка рёбер (pmin/pmax)",
    "Добавить weight_inv = 1/weight"
  ),
  Причина = c(
    "Данные interactions неполны для этих игр — включение исказило бы веса рёбер",
    "Изолированные узлы не вносят вклад в структуру сети и метрики",
    "Невозможно образовать ребро при одном персонаже в сцене",
    "Исключение дублирования рёбер (A-B = B-A) для ненаправленного графа",
    "Требуется для корректного расчёта betweenness при взвешенных рёбрах"
  ),
  Влияние = c(
    sprintf("Удалено %d игр и соответствующих interactions/scenes", n_revelations_removed),
    sprintf("Удалено %d изолированных персонажей из %d", n_isolated_removed, nrow(characters)),
    sprintf("Исключено %d сцен с одним персонажем", n_scenes_single_char),
    "Дублирующихся рёбер не осталось в edges_df",
    "Более точные результаты shortest-path betweenness"
  ),
  stringsAsFactors = FALSE
)

kable(cleaning_log, caption = "Лог решений по очистке и подготовке данных") %>%
  kable_styling(bootstrap_options = c("striped", "hover", "condensed", "bordered"),
                full_width = TRUE) %>%
  column_spec(1, bold = TRUE, width = "25%") %>%
  column_spec(2, width = "40%") %>%
  column_spec(3, width = "35%")

write.csv(cleaning_log, "data/cleaning_log.csv", row.names = FALSE)


# === 2.8 Сохранение результатов ===

saveRDS(snapshots, "data/networks_per_snapshot.rds")

write.csv(edges_df, "data/edges_df.csv", row.names = FALSE)
write.csv(nodes_df, "data/nodes_df.csv", row.names = FALSE)
write.csv(metrics_df, "data/snapshot_metrics.csv", row.names = FALSE)

cat("Сохранено:\n")

cat(sprintf("  networks_per_snapshot.rds  — %d снимков сети\n", length(snapshots)))

cat(sprintf("  edges_df.csv               — %d рёбер\n", nrow(edges_df)))

cat(sprintf("  nodes_df.csv               — %d узлов\n", nrow(nodes_df)))

cat(sprintf("  snapshot_metrics.csv       — %d строк метрик\n", nrow(metrics_df)))

cat(sprintf("  cleaning_log.csv           — %d решений по очистке\n", nrow(cleaning_log)))


# === 2.9 Краткое резюме результатов ===

cat(sprintf("Игр в анализе:          %d (из %d, исключены Revelations)\n",
            n_games_after, n_games_before))

cat(sprintf("Узлов в финальной сети: %d\n", nrow(nodes_df)))

cat(sprintf("Рёбер в финальной сети: %d\n", nrow(edges_df)))

cat(sprintf("Снимков построено:      %d\n", length(snapshots)))

cat(sprintf("Медиана веса ребра:     %.0f сцен\n", median(edges_df$weight)))

cat(sprintf("Максимальный вес ребра: %.0f сцен\n", max(edges_df$weight)))

cat("\nОбнаруженные сообщества по снимкам:\n")

print(metrics_df %>% select(snapshot, узлы, рёбра, сообщества))
