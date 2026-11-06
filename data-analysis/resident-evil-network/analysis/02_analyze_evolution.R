# 02_analyze_evolution.R
# Eras, Louvain communities, centralities, evolution of centrality over snapshots,
# articulation points. Needs the files produced by 01_build_network.R.
# Interactive visNetwork graphs are rendered in report/*.html; here they are
# created as objects (open them in RStudio or save with htmlwidgets::saveWidget).
# Run from the project folder:  Rscript analysis/02_analyze_evolution.R

# Packages (reconstructed from the functions used in the report)
library(dplyr)
library(tidyr)
library(igraph)
library(ggplot2)
library(knitr)
library(kableExtra)
library(reshape2)
library(RColorBrewer)
library(scales)
library(visNetwork)

# === 3. Основной анализ: Эволюция сети ===


# === 3.1 Разделение на эпохи ===

era_table <- data.frame(
  Эпоха = c("Классическая", "Экшен", "Современная"),
  Игры = c(
    "RE0, RE1, RE2, RE3",
    "Code Veronica, RE4, RE5, RE6",
    "RE7, RE8, Shadow of Rose, RE9/Requiem"
  ),
  Снимки = c("1–4", "5–8", "9–12"),
  Основание = c(
    "Фиксированная камера, tank controls, Raccoon City (1998), Umbrella Corporation",
    "RE4 — поворотный момент серии (over-the-shoulder). Завершение арки Вескера",
    "Вид от первого лица, новый протагонист Итан Уинтерс, возврат к survival horror"
  ),
  stringsAsFactors = FALSE
)

kable(era_table, caption = "Разделение франшизы на нарративные эпохи") %>%
  kable_styling(bootstrap_options = c("striped", "hover", "condensed", "bordered"),
                full_width = TRUE) %>%
  column_spec(1, bold = TRUE, width = "12%") %>%
  column_spec(2, width = "28%") %>%
  column_spec(3, width = "10%") %>%
  column_spec(4, width = "50%")


# === 3.2 Дополнение таблицы метрик ===

snapshots  <- readRDS("data/networks_per_snapshot.rds")
nodes_df   <- read.csv("data/nodes_df.csv", stringsAsFactors = FALSE)
edges_df   <- read.csv("data/edges_df.csv", stringsAsFactors = FALSE)
metrics_df <- read.csv("data/snapshot_metrics.csv", stringsAsFactors = FALSE)

calc_avg_path_length <- function(g) {
  if (!is_connected(g)) {
    components <- decompose(g)
    largest_comp <- components[[which.max(sapply(components, vcount))]]
    return(average.path.length(largest_comp))
  } else {
    return(average.path.length(g))
  }
}

avg_path_lengths <- sapply(snapshots, calc_avg_path_length)

metrics_df$avg_path_length <- round(avg_path_lengths, 3)
metrics_df$delta_avg_path <- c(NA, round(diff(metrics_df$avg_path_length) / 
                                 head(metrics_df$avg_path_length, -1) * 100, 1))

write.csv(metrics_df, "data/snapshot_metrics_augmented.csv", row.names = FALSE)

metrics_display <- metrics_df %>%
  mutate(
    delta_density = c(NA, round(diff(плотность) / head(плотность, -1) * 100, 1)),
    delta_density = ifelse(is.na(delta_density), "—",
                           paste0(ifelse(delta_density > 0, "+", ""), delta_density, "%")),
    delta_avg_path = ifelse(is.na(delta_avg_path), "—",
                            paste0(ifelse(delta_avg_path > 0, "+", ""), delta_avg_path, "%"))
  ) %>%
  select(
    `Снимок` = snapshot,
    `Узлы` = узлы,
    `Рёбра` = рёбра,
    `Плотность` = плотность,
    `Δ Плотность` = delta_density,
    `Avg. Path Length` = avg_path_length,
    `Δ Avg Path` = delta_avg_path,
    `Кластеризация` = кластеризация,
    `Сообщества` = сообщества
  )

kable(metrics_display,
      caption = "Расширенная таблица метрик с avg path length и delta") %>%
  kable_styling(bootstrap_options = c("striped", "hover", "condensed", "bordered"),
                full_width = TRUE) %>%
  column_spec(1, bold = TRUE)


# === 3.2.1 Динамика сетевых метрик и связь с исследовательским вопросом ===


# === 3.3 Анализ сообществ по эпохам ===

# Определяем индексы снимков для каждой эпохи
# Классика: RE0, RE1, RE3, RE2 (снимки 1-4)
# Экшен: Code Veronica, RE4, RE5, RE6 (снимки 5-8)
# Современность: RE7, RE8, RE8 DLC, RE9 (снимки 9-12)

era_indices <- list(
  classic = 1:4,
  action = 5:8,
  modern = 9:12
)

era_labels <- c(
  "Классическая эпоха (RE0–RE2, сурвайвал-хоррор)",
  "Экшен-эпоха (Code Veronica–RE6)",
  "Современная эпоха (RE7–REquiem, возврат к хоррору)"
)

# Функция для анализа сообществ одной эпохи
analyze_communities <- function(snapshot_idx, era_label) {
  g <- snapshots[[snapshot_idx]]
  
  # Детектируем сообщества (Louvain)
  set.seed(42)
  comm <- cluster_louvain(g)
  
  # Получаем membership
  membership_vec <- membership(comm)
  
  # Создаём таблицу: персонаж -> сообщество
  comm_df <- data.frame(
    id = as.numeric(names(membership_vec)),
    community = as.numeric(membership_vec),
    stringsAsFactors = FALSE
  )
  
  # Добавляем имена и роли
  comm_df <- comm_df %>%
    left_join(nodes_df, by = "id") %>%
    arrange(community, name)
  
  # Список сообществ с персонажами
  communities_list <- split(comm_df, comm_df$community)
  
  # Выводим информацию
  cat(sprintf("\n### %s\n", era_label))
  cat(sprintf("Всего сообществ: %d\n\n", length(communities_list)))
  
  for (comm_id in names(communities_list)) {
    comm_members <- communities_list[[comm_id]]
    n_members <- nrow(comm_members)
    
    # Собираем ключевых персонажей (первые 5-7)
    key_chars <- paste(comm_members$name[1:min(7, n_members)], collapse = ", ")
    
    # Определяем нарративное название на основе персонажей
    char_names <- comm_members$name
    narrative_name <- "Неопределённая группа"
    
    # Логика для нарративных названий
    if (any(grepl("Chris|Jill|Barry|Rebecca|Wesker", char_names)) && 
        any(grepl("Mansion|Arklay", char_names))) {
      narrative_name <- "Выжившие в особняке / S.T.A.R.S. Alpha"
    } else if (any(grepl("Leon|Claire|Sherry|Ada|Birkin", char_names))) {
      narrative_name <- "Выжившие в Раккун-Сити / R.P.D."
    } else if (any(grepl("Leon|Ashley|Luis|Saddler|Salazar", char_names))) {
      narrative_name <- "Испанская деревня (Los Illuminados)"
    } else if (any(grepl("Chris|Sheva|Jill|Wesker|BSAA", char_names))) {
      narrative_name <- "BSAA / Африканская операция"
    } else if (any(grepl("Ethan|Mia|Jack|Lucas|Baker", char_names))) {
      narrative_name <- "Семья Бейкеров / Луизиана"
    } else if (any(grepl("Ethan|Rose|Miranda|Dimitrescu|Heisenberg", char_names))) {
      narrative_name <- "Деревня / Лорды-мутанты"
    } else if (any(grepl("Jake|Sherry|Helena|Piers", char_names))) {
      narrative_name <- "Глобальный кризис (RE6)"
    } else {
      narrative_name <- paste("Группа персонажей с общими сюжетными линиями")
    }
    
    cat(sprintf("**Сообщество %d** (%d персонажей): **%s**\n", 
                as.numeric(comm_id), n_members, narrative_name))
    cat(sprintf("Ключевые персонажи: %s\n", key_chars))
    cat("\n")
  }
  
  # Возвращаем таблицу для сохранения
  return(comm_df %>% mutate(era = era_label))
}

# Создаём список для результатов
communities_list <- list()

# Анализируем каждую эпоху
for (i in seq_along(era_indices)) {
  # Берём последний (финальный) снимок каждой эпохи
  last_snapshot_idx <- max(era_indices[[i]])
  comm_df <- analyze_communities(last_snapshot_idx, era_labels[i])
  communities_list[[i]] <- comm_df
}

# Объединяем и сохраняем
communities_all <- do.call(rbind, communities_list)
write.csv(communities_all, "data/communities_per_era.csv", row.names = FALSE)

cat("\n\n**Таблица сообществ по эпохам сохранена в 'data/communities_per_era.csv'**\n")


# === 3.4 Расчёт центральностей ===

# Берём финальную полную сеть (последний снимок)
g_final <- snapshots[[length(snapshots)]]

cat(sprintf("Анализ финальной сети: %d узлов, %d рёбер\n", 
            vcount(g_final), ecount(g_final)))

# 1. Degree Centrality (количество связей)
degree_raw <- degree(g_final)
degree_norm <- degree(g_final, normalized = TRUE)

# 2. Betweenness Centrality (с использованием weight_inv, как в ТЗ)
betweenness_raw <- betweenness(g_final, weights = E(g_final)$weight_inv, normalized = FALSE)
betweenness_norm <- betweenness(g_final, weights = E(g_final)$weight_inv, normalized = TRUE)

# 3. Closeness Centrality (обратная среднему расстоянию до всех остальных)
# Для больших графов может быть медленно, используем estimate
closeness_raw <- closeness(g_final, mode = "all", weights = NA, normalized = FALSE)
closeness_norm <- closeness(g_final, mode = "all", weights = NA, normalized = TRUE)

# 4. Eigenvector Centrality (учитывает важность соседей)
eigen_raw <- eigen_centrality(g_final, weights = NA)$vector
# Нормализация (делим на максимальное значение)
eigen_norm <- eigen_raw / max(eigen_raw)

# Собираем в таблицу
centrality_df <- data.frame(
  id = as.numeric(V(g_final)$name),
  name = nodes_df$name[match(as.numeric(V(g_final)$name), nodes_df$id)],
  role = nodes_df$role[match(as.numeric(V(g_final)$name), nodes_df$id)],
  degree = round(degree_raw, 2),
  degree_norm = round(degree_norm, 4),
  betweenness = round(betweenness_raw, 2),
  betweenness_norm = round(betweenness_norm, 4),
  closeness = round(closeness_raw, 4),
  closeness_norm = round(closeness_norm, 4),
  eigenvector = round(eigen_raw, 4),
  eigenvector_norm = round(eigen_norm, 4),
  stringsAsFactors = FALSE
)

# Сортируем по убыванию
centrality_df <- centrality_df[order(-centrality_df$degree), ]

# Сохраняем
write.csv(centrality_df, "data/centrality_final.csv", row.names = FALSE)

cat("\nЦентральности рассчитаны и сохранены в 'data/centrality_final.csv'\n")

kable(head(centrality_df[, 1:7], 10), caption = "Первые 10 строк таблицы центральностей") %>%
  kable_styling(bootstrap_options = c("striped", "hover", "condensed"), full_width = FALSE)

centrality_snapshots <- list()

for (i in seq_along(snapshots)) {
  g <- snapshots[[i]]
  centrality_snapshots[[i]] <- data.frame(
    snapshot    = names(snapshots)[i],
    name        = V(g)$name,
    degree      = degree(g, normalized = TRUE),
    betweenness = betweenness(g, 
                    weights = E(g)$weight_inv,
                    normalized = TRUE),
    closeness   = closeness(g, normalized = TRUE),
    eigenvector = eigen_centrality(g)$vector
  )
}

centrality_per_snapshot <- bind_rows(centrality_snapshots)
write.csv(centrality_per_snapshot, 
          "data/centrality_per_snapshot.csv",
          row.names = FALSE)


# === 3.5 Описание метрик центральности ===

metrics_description <- data.frame(
  Метрика = c(
    "Degree Centrality (Степень)",
    "Betweenness Centrality (Посредничество)",
    "Closeness Centrality (Близость)",
    "Eigenvector Centrality (Собственный вектор)"
  ),
  Определение = c(
    "Количество прямых связей персонажа (сколько других персонажей появлялись с ним в одной сцене).",
    "Количество кратчайших путей между другими парами, которые проходят через данного персонажа. Измеряет роль как 'моста'.",
    "Обратное среднее расстояние от персонажа до всех остальных. Показывает, насколько быстро персонаж может 'дотянуться' до других.",
    "Важность персонажа определяется важностью его соседей. 'Ты ценен, если твои друзья ценны'."
  ),
  Что.измеряет.в.мире.RE = c(
    "С кем чаще всего пересекается персонаж? Является ли он 'социальной бабочкой'?",
    "Кто является связующим звеном между разными сюжетными арками? Кто соединяет разные сообщества?",
    "Насколько быстро персонаж может быть вовлечён в любой сюжет?",
    "Является ли персонаж 'влиятельным', связан ли с другими важными героями/злодеями?"
  ),
  Почему.выбрана = c(
    "Базовая мера активности в сети. Показывает, сколько сцен разделяет персонаж с другими.",
    "Ключевая метрика для выявления 'шпионов', 'союзников' и 'антагонистов, взаимодействующих со всеми'.",
    "Характеризует 'доступность' персонажа — насколько быстро сюжет может его подключить.",
    "Выявляет персонажей, которые важны не столько сами по себе, сколько из-за связей с ключевыми фигурами."
  ),
  stringsAsFactors = FALSE
)

kable(metrics_description, caption = "Описание метрик центральности") %>%
  kable_styling(bootstrap_options = c("striped", "hover", "condensed", "bordered"),
                full_width = TRUE) %>%
  column_spec(1, bold = TRUE, width = "15%") %>%
  column_spec(2, width = "30%") %>%
  column_spec(3, width = "30%") %>%
  column_spec(4, width = "25%")


# === 3.6 Топ-10 персонажей по каждой метрике ===

# Функция для создания топ-10 таблицы
top10_table <- function(df, metric_col, metric_name) {
  df_sorted <- df[order(-df[[metric_col]]), ]
  top10 <- df_sorted[1:10, c("name", "role", metric_col)]
  colnames(top10)[3] <- metric_name
  return(top10)
}

# Создаём таблицы для нормализованных метрик
top10_degree <- top10_table(centrality_df, "degree_norm", "Degree (норм.)")
top10_betweenness <- top10_table(centrality_df, "betweenness_norm", "Betweenness (норм.)")
top10_closeness <- top10_table(centrality_df, "closeness_norm", "Closeness (норм.)")
top10_eigen <- top10_table(centrality_df, "eigenvector_norm", "Eigenvector (норм.)")

kable(top10_degree, caption = "Топ-10 персонажей по Degree Centrality") %>%
  kable_styling(bootstrap_options = c("striped", "hover", "condensed"), full_width = FALSE)

kable(top10_betweenness, caption = "Топ-10 персонажей по Betweenness Centrality") %>%
  kable_styling(bootstrap_options = c("striped", "hover", "condensed"), full_width = FALSE)

kable(top10_closeness, caption = "Топ-10 персонажей по Closeness Centrality") %>%
  kable_styling(bootstrap_options = c("striped", "hover", "condensed"), full_width = FALSE)

kable(top10_eigen, caption = "Топ-10 персонажей по Eigenvector Centrality") %>%
  kable_styling(bootstrap_options = c("striped", "hover", "condensed"), full_width = FALSE)

networks_snapshots <- readRDS("data/networks_per_snapshot.rds")
nodes_df <- read.csv("data/nodes_df.csv") 
edges_df <- read.csv("data/edges_df.csv") 
centrality_df  <- read.csv("data/centrality_final.csv",  stringsAsFactors = FALSE)
communities_df <- read.csv("data/communities_per_era.csv", stringsAsFactors = FALSE)


# === 3.7 Интерактивная сеть всей франшизы ===

# Словарь id -> name
id_to_name <- setNames(as.character(nodes_df$name), as.character(nodes_df$id))

# Берём последний снимок и переименовываем вершины
g_full <- networks_snapshots[[length(networks_snapshots)]]
V(g_full)$name <- id_to_name[V(g_full)$name]

# Подготовка узлов для visNetwork
vis_nodes <- data.frame(
  id    = V(g_full)$name,
  label = V(g_full)$name,
  value = degree(g_full),
  title = paste0("<b>", V(g_full)$name, "</b><br>Степень: ", degree(g_full))
)

# Подготовка рёбер
vis_edges <- igraph::as_data_frame(g_full, what = "edges")
colnames(vis_edges)[1:2] <- c("from", "to")
vis_edges$width <- rescale(vis_edges$weight, to = c(1, 8))

# Рендер
visNetwork(vis_nodes, vis_edges,
           main = "Вся франшиза Resident Evil — сеть совместных появлений") %>%
  visOptions(
    highlightNearest = list(enabled = TRUE, degree = 1),
    nodesIdSelection = list(enabled = TRUE, useLabels = TRUE)
  ) %>%
  visPhysics(solver = "forceAtlas2Based",
             forceAtlas2Based = list(gravitationalConstant = -60)) %>%
  visLayout(randomSeed = 42)


# === 3.8 Сети по эпохам ===

era_table <- data.frame(
  Эпоха = c("Классическая", "Экшен", "Современная"),
  Части = c(
    "RE0 – RE3",
    "RE4 – RE6",
    "RE7 – REquiem (RE9)"
  ),
  stringsAsFactors = FALSE
)

kable(era_table, caption = "Разделение франшизы на нарративные эпохи") %>%
  kable_styling(bootstrap_options = c("striped", "hover", "condensed", "bordered"),
                full_width = FALSE) %>%
  column_spec(1, bold = TRUE)

era_map <- list(
  classic = c("Resident Evil 0", "+Resident Evil", 
              "+Resident Evil 3: Nemesis", "+Resident Evil 2"),
  action  = c("+Resident Evil: Code – Veronica", 
              "+Resident Evil 4", "+Resident Evil 5", "+Resident Evil 6"),
  modern  = c("+Resident Evil 7: Biohazard", "+Resident Evil Village",
              "+Resident Evil Village – Shadow of Rose", "+Resident Evil Requiem")
)

make_era_graph <- function(era_games) {
  era_edges <- lapply(era_games, function(snap) {
    g <- networks_snapshots[[snap]]
    if (is.null(g)) return(NULL)
    igraph::as_data_frame(g, what = "edges")
  }) %>%
    bind_rows() %>%
    group_by(from, to) %>%
    summarise(weight = sum(weight, na.rm = TRUE), .groups = "drop")

  if (nrow(era_edges) == 0) return(NULL)

  # Создаём словарь id -> name
  id_to_name <- setNames(as.character(nodes_df$name), as.character(nodes_df$id))

  # Заменяем числовые id на имена в рёбрах
  era_edges$from <- id_to_name[as.character(era_edges$from)]
  era_edges$to   <- id_to_name[as.character(era_edges$to)]

  # Убираем рёбра где замена не нашлась
  era_edges <- era_edges %>% filter(!is.na(from), !is.na(to))

  g <- graph_from_data_frame(era_edges, directed = FALSE)
  g <- delete_vertices(g, degree(g) == 0)
  g
}

g_classic <- make_era_graph(era_map$classic)
g_action  <- make_era_graph(era_map$action)
g_modern  <- make_era_graph(era_map$modern)

# Вспомогательная функция для рендера сети эпохи
render_era_vis <- function(g, title_text, color_hex) {
  vis_n <- data.frame(
    id    = V(g)$name,   # <-- id должен быть именем, не числом
    label = V(g)$name,
    value = degree(g),
    color = color_hex,
    title = paste0("<b>", V(g)$name, "</b><br>Степень: ", degree(g))
  )
  vis_e <- igraph::as_data_frame(g, what = "edges")
  colnames(vis_e)[1:2] <- c("from", "to")
  vis_e$width <- rescale(vis_e$weight, to = c(1, 6))

  visNetwork(vis_n, vis_e, main = title_text) %>%
    visOptions(
      highlightNearest  = TRUE,
      nodesIdSelection  = list(enabled = TRUE, useLabels = TRUE)  # <-- показывает label вместо id
    ) %>%
    visPhysics(solver = "forceAtlas2Based",
               forceAtlas2Based = list(gravitationalConstant = -50)) %>%
    visLayout(randomSeed = 42)
}


# === 3.8.1 Классическая эпоха (RE0–RE3) ===

render_era_vis(g_classic,
               "Классическая эпоха (RE0–RE3)",
               color_hex = "#4E79A7")


# === 3.8.2 Эпоха экшна (RE4–RE6) ===

render_era_vis(g_action,
               "Эпоха экшна (RE4–RE6)",
               color_hex = "#F28E2B")


# === 3.8.3 Современная эпоха (RE7–RE9) ===

render_era_vis(g_modern,
               "Современная эпоха (RE7–REquiem)",
               color_hex = "#59A14F")


# === 3.9 Heatmap эволюции центральности и топ-15 персонажей по суммарной degree-центральности ===

top_chars <- centrality_df %>%
  slice_max(degree, n = 15) %>%
  pull(name)

top_df <- centrality_df %>%
  filter(name %in% top_chars)

ggplot(top_df, aes(x = reorder(name, degree), y = degree, fill = degree)) +
  geom_col() +
  scale_fill_gradient(low = "#c6dbef", high = "#08306b") +
  coord_flip() +
  labs(title = "Топ-15 персонажей по Degree Centrality",
       x = NULL, y = "Degree") +
  theme_minimal(base_size = 12) +
  theme(legend.position = "none")

heat_long <- top_df %>%
  select(name, degree_norm, betweenness_norm, closeness_norm, eigenvector_norm) %>%
  pivot_longer(-name, names_to = "metric", values_to = "value") %>%
  mutate(metric = recode(metric,
    degree_norm      = "Degree",
    betweenness_norm = "Betweenness",
    closeness_norm   = "Closeness",
    eigenvector_norm = "Eigenvector"
  ))

ggplot(heat_long, aes(x = metric, y = reorder(name, value), fill = value)) +
  geom_tile(color = "white", linewidth = 0.4) +
  geom_text(aes(label = round(value, 2)), size = 3.5) +
  scale_fill_gradientn(
    colours = c("#f7fbff", "#6baed6", "#08306b"),
    name    = "Норм. значение"
  ) +
  labs(title = "Только Крис доминирует по всем четырём метрикам одновременно",
       subtitle = "Нормализованные центральности топ-15 персонажей финальной сети | тёмный = высокое значение",
       x = NULL, y = NULL) +
  theme_minimal(base_size = 12) +
  theme(panel.grid = element_blank(),
        axis.text.x = element_text(face = "bold"))


# === 3.10 Топ-15 по Betweenness Centrality ===

# Фильтруем те же топ-15 персонажей
top_df <- centrality_df %>%
  slice_max(degree, n = 15)

# Палитра для персонажей
char_colors <- setNames(
  colorRampPalette(brewer.pal(8, "Set2"))(nrow(top_df)),
  top_df$name
)

ggplot(top_df, aes(x = reorder(name, betweenness), y = betweenness, fill = name)) +
  geom_col(show.legend = FALSE) +
  scale_fill_manual(values = char_colors) +
  scale_y_continuous(labels = comma) +
  coord_flip() +
  labs(title = "Крис Редфилд — абсолютный структурный мост франшизы", x = NULL, y = "Betweenness", subtitle = "Betweenness Centrality топ-15 персонажей финальной сети") +
  theme_minimal(base_size = 12)


# === 3.11 Эволюция центральностей по снимкам ===

centrality_snap <- read.csv(
  "data/centrality_per_snapshot.csv",
  stringsAsFactors = FALSE)

top_chars_snap <- centrality_snap %>%
  group_by(name) %>%
  summarise(mean_degree = mean(degree, na.rm = TRUE)) %>%
  slice_max(mean_degree, n = 10) %>%
  pull(name)

plot_snap <- centrality_snap %>%
  filter(name %in% top_chars_snap) %>%
  left_join(nodes_df %>% select(id, char_name = name), 
            by = c("name" = "id"))

snapshot_order <- c(
  "Resident Evil 0",
  "+Resident Evil",
  "+Resident Evil 2",
  "+Resident Evil 3: Nemesis",
  "+Resident Evil: Code – Veronica",
  "+Resident Evil 4",
  "+Resident Evil 5",
  "+Resident Evil 6",
  "+Resident Evil 7: Biohazard",
  "+Resident Evil Village",
  "+Resident Evil Village – Shadow of Rose",
  "+Resident Evil Requiem"
)

plot_snap <- plot_snap %>%
  mutate(snapshot = factor(snapshot, levels = snapshot_order))

char_palette <- setNames(
  colorRampPalette(c("#08306b", "#2171b5", "#6baed6", 
                     "#f16913", "#d94801", "#7f2704",
                     "#41ab5d", "#006d2c", "#54278f", "#3f007d"))(10),
  unique(plot_snap$char_name)
)

ggplot(plot_snap, aes(x = snapshot, y = degree,
                      color = char_name, group = char_name)) +
  geom_line(size = 1) +
  geom_point(size = 2) +
  scale_color_manual(values = char_palette) +
  theme_minimal(base_size = 11) +
  theme(axis.text.x = element_text(angle = 45, hjust = 1),
        legend.position = "right") +
  labs(title = "Ребекка Чемберс знала всех в RE0 — но исчезла из центра после",
       subtitle = "Degree Centrality топ-10 персонажей | нормализованные значения показывают долю персонажей, с которыми встречался герой",
       x = NULL, y = "Degree", color = "Персонаж")

ggplot(plot_snap, aes(x = snapshot, y = betweenness,
                      color = char_name, group = char_name)) +
  geom_line(size = 1) +
  geom_point(size = 2) +
  scale_color_manual(values = char_palette) +
  theme_minimal(base_size = 11) +
  theme(axis.text.x = element_text(angle = 45, hjust = 1),
        legend.position = "right") +
  labs(title = "Ада Вонг — нарративный связной, но не структурный мост",
       subtitle = "Betweenness Centrality топ-10 персонажей | несмотря на роль двойного агента, Ada Wong редко выступает посредником в сети",
       x = NULL, y = "Betweenness", color = "Персонаж")

ggplot(plot_snap, aes(x = snapshot, y = closeness,
                      color = char_name, group = char_name)) +
  geom_line(size = 1) +
  geom_point(size = 2) +
  scale_color_manual(values = char_palette) +
  theme_minimal(base_size = 11) +
  theme(axis.text.x = element_text(angle = 45, hjust = 1),
        legend.position = "right") +
  labs(title = "После RE4 ни один персонаж не доминирует в центре сети",
       subtitle = "Closeness Centrality топ-10 персонажей | классическая эпоха имела явных лидеров, эпоха экшена уравняла всех",
       x = NULL, y = "Closeness", color = "Персонаж")

ggplot(plot_snap, aes(x = snapshot, y = eigenvector,
                      color = char_name, group = char_name)) +
  geom_line(size = 1) +
  geom_point(size = 2) +
  scale_color_manual(values = char_palette) +
  theme_minimal(base_size = 11) +
  theme(axis.text.x = element_text(angle = 45, hjust = 1),
        legend.position = "right") +
  labs(title = "Влияние персонажей нестабильно — каждая часть меняет «важных» героев",
       subtitle = "Eigenvector Centrality топ-10 персонажей | резкие колебания указывают на смену ключевых групп в каждую эпоху",
       x = NULL, y = "Eigenvector", color = "Персонаж")


# === 3.12 Тепловая карта эволюции по снимкам ===

top_chars_names <- nodes_df$name[match(top_chars_snap, nodes_df$id)]

heat_snap <- centrality_snap %>%
  left_join(nodes_df %>% select(id, name), by = c("name" = "id")) %>%
  rename(char_name = name.y) %>%
  filter(char_name %in% top_chars_names) %>%
  select(char_name, snapshot, betweenness)

ggplot(heat_snap,
       aes(x = snapshot,
           y = reorder(char_name, betweenness),
           fill = betweenness)) +
  geom_tile(color = "white", linewidth = 0.4) +
  geom_text(aes(label = round(betweenness, 2)),
            size = 3, color = "black") +
  scale_fill_gradientn(
    colours = c("#f7fbff", "#6baed6", "#08306b"),
    na.value = "grey90",
    name = "Betweenness"
  ) +
  theme_minimal(base_size = 11) +
  theme(
    axis.text.x = element_text(angle = 45, hjust = 1),
    panel.grid  = element_blank()
  ) +
  labs(
    title = "Ребекка доминирует в классике, Крис — во всей франшизе",
    subtitle = "Betweenness Centrality топ-10 персонажей по снимкам | тёмный = высокая центральность, серый = персонаж отсутствует",
    x = "Снимок (хронологический порядок)",
    y = NULL
  )


# === 3.13 Корреляция метрик и сравнительная таблица ===

corr_data <- centrality_df %>%
  select(degree, betweenness, closeness, eigenvector) %>%
  cor(use = "complete.obs", method = "pearson")

corr_melt <- melt(corr_data)

ggplot(corr_melt, aes(x = Var1, y = Var2, fill = value)) +
  geom_tile(color = "white", linewidth = 0.5) +
  geom_text(aes(label = round(value, 2)), size = 4.5, fontface = "bold") +
  scale_fill_gradientn(
    colours = c("#d73027", "#fee08b", "#1a9850"),
    limits  = c(0.5, 1),
    name    = "Пирсон r"
  ) +
  labs(title = "Betweenness измеряет то, чего не видят остальные метрики",
       subtitle = "Корреляция Пирсона между четырьмя метриками центральности финальной сети",
       x = NULL, y = NULL) +
  theme_minimal(base_size = 12) +
  theme(axis.text = element_text(face = "bold"),
        panel.grid = element_blank())


# === 3.14 Сравнительная таблица нормализованных метрик ===

top_df %>%
  arrange(desc(degree)) %>%
  select(name, role, 
         degree, degree_norm,
         betweenness, betweenness_norm,
         closeness, closeness_norm,
         eigenvector, eigenvector_norm) %>%
  mutate(across(where(is.numeric), ~ round(.x, 3))) %>%
  kable(
    caption = "Центральности топ-15 персонажей финальной сети",
    col.names = c("Персонаж", "Роль",
                  "Degree", "Degree (норм.)",
                  "Betweenness", "Betweenness (норм.)",
                  "Closeness", "Closeness (норм.)",
                  "Eigenvector", "Eigenvector (норм.)")
  ) %>%
  kable_styling(bootstrap_options = c("striped", "hover", "condensed"),
                full_width = FALSE) %>%
  column_spec(c(4, 6, 8, 10), background = "#eaf4e8")


# === 3.15 Статистическая центральность и структурная незаменимость ===

g_final <- snapshots[[length(snapshots)]]

# Находим точки сочленения
ap <- articulation_points(g_final)
ap_ids <- as.numeric(V(g_final)$name[ap])

ap_df <- nodes_df %>%
  filter(id %in% ap_ids) %>%
  select(id, name, role)

kable(ap_df, caption = "Точки сочленения финальной сети (структурно незаменимые персонажи)") %>%
  kable_styling(bootstrap_options = c("striped", "hover", "condensed"), full_width = FALSE)


# === 4. Содержательные выводы ===
