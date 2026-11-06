# библиотеки

library(readr)
library(readxl)
library(dplyr)
library(tidyr)
library(ggplot2)
library(scales)

travel <- read_delim(
  "data/dano_dataset_travel.csv",
  delim = ";",
  locale = locale(decimal_mark = ","),
  show_col_types = FALSE
)



avia <- read_excel(
  "data/dano_dataset_avia_hashed_corrected_s-2.xlsx"
)

tbank_colors <- c(
  "Т-Премиум" = "#FFDD2D",
  "Другие" = "#222222"
)


theme_tbank <- function(){

theme_minimal(base_size = 14)+

theme(

panel.grid = element_blank(),

plot.background =
element_rect(
fill="white",
color=NA
),

plot.title =
element_text(
face="bold",
size=17,
color="#111111"
),

plot.subtitle =
element_text(
size=12,
color="#555555"
),

axis.text =
element_text(
color="#333333"
),

axis.title =
element_blank(),

axis.ticks =
element_blank()

)

}

travel <- travel %>%

mutate(

segment = case_when(

bundle_nm %in%

c(
"Premium",
"Private",
"Team Premium",
"Team Private",
"Tinkoff Premium"
)

~ "Т-Премиум",

TRUE ~ "Другие"

)

)


# 1. Размер аудитории

audience <- travel %>%

count(segment) %>%

mutate(

share =
round(
n/sum(n)*100,
1
)

)


print(audience)

ggplot(
audience,
aes(
x=segment,
y=share,
fill=segment
)
)+

geom_col(
width=.6
)+

geom_text(
aes(
label=paste0(share,"%")
),
vjust=-0.4,
fontface="bold",
size=5
)+

scale_fill_manual(
values=tbank_colors
)+

labs(
title="Каждый третий пользователь 'Т-Путшествия' — Т-Премиум",
subtitle="Распределение пользователей по сегментам"
)+

theme_tbank()

# 2. Средний чек


avg_check <- travel %>%

filter(
!is.na(nominal_price_rub_amt)
)%>%

group_by(segment)%>%

summarise(

orders=n(),

avg_price=
round(
mean(
nominal_price_rub_amt,
na.rm=TRUE
)
),

median_price=
round(
median(
nominal_price_rub_amt,
na.rm=TRUE
)
)

)



print(avg_check)

ggplot(
avg_check,
aes(
x=segment,
y=avg_price,
fill=segment
)
)+

geom_col(
width=.6
)+

geom_text(
aes(
label=paste0(
comma(avg_price),
" руб."
)
),
vjust=-0.4,
fontface="bold"
)+

scale_fill_manual(
values=tbank_colors
)+

labs(

title="Пользователи Т-Премиум выбирают более дорогие поездки",

subtitle="Средняя стоимость заказа"

)+

theme_tbank()

# 3. Доля дорогих поездок


price_structure <- travel %>%

filter(
!is.na(nominal_price_rub_amt)
)%>%

mutate(

price_group = case_when(

nominal_price_rub_amt < 10000
~ "До 10 тыс.",

nominal_price_rub_amt < 30000
~ "10–30 тыс.",

TRUE
~ "30 тыс.+"

)

)%>%

count(
segment,
price_group
)%>%

group_by(segment)%>%

mutate(

share =
round(
n/sum(n)*100,
1
)

)



print(price_structure)

ggplot(

price_structure,

aes(

x=price_group,
y=share,
fill=segment

)

)+

geom_col(
position="dodge",
width=.7
)+

geom_text(

aes(
label=paste0(share,"%")
),

position=
position_dodge(.7),

vjust=-0.4

)+

scale_fill_manual(
values=tbank_colors
)+


labs(

title="Пользователи Т-Премиум чаще совершает дорогие покупки",

subtitle="Распределение стоимости поездок"

)+

theme_tbank()

# 4. Повторные пользователи


repeat_users <- travel %>%

group_by(
segment,
client_rk
)%>%

summarise(

orders=n(),

.groups="drop"

)%>%

group_by(segment)%>%

summarise(

users=n(),

avg_orders=
round(
mean(orders),
2
),

median_orders=
median(orders)

)



print(repeat_users)

ggplot(

repeat_users,

aes(

x=segment,
y=avg_orders,
fill=segment

)

)+

geom_col(
width=.6
)+

geom_text(

aes(
label=avg_orders
),

vjust=-0.4,

fontface="bold"

)+

scale_fill_manual(
values=tbank_colors
)+


labs(

title="Пользователи Т-Премиум чаще возвращаются",

subtitle="Среднее количество заказов на пользователя"

)+

theme_tbank()
