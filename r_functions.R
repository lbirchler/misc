# Libraries ----
libraries <- c(
  "tidyverse", "lubridate", "rvest", "glue", "openxlsx", "DT", "janitor", "DBI",
  "dbplyr"
)

lapply(
  libraries, suppressWarnings(suppressPackageStartupMessages(library)),
  character.only = TRUE
)



# Source Data ----

# ASCII Code Table of A to Z and a to z(Small and Upper cases)
ASCII_table <- rio::import("data/ASCII-Table.csv")


# Functions ----

# * Tools ----

# convert BINARY/OCTAL/DECIMAL/HEX to ASCII string
tools_base_to_ascii <- function(list, base = NA)
{

  if (base %in% c("BINARY", "OCTAL", "DECIMAL"))
  {

    table <- data.table::data.table(x1 = c(as.integer(list))) %>%
      left_join(ASCII_table, by = c(x1 = base))

  } else if (base == "HEX")
  {

    table <- data.table::data.table(x1 = c(as.character(list))) %>%
      left_join(ASCII_table, by = c(x1 = base))

  }

  ascii_list <- table$ASCII

  paste(ascii_list, collapse = "")

}


# IP Network
tools_ip_network <- function(CLIENT_IP)
{

  sub(
    "^([^.]*.[^.]*.[^.]*).*", "\\1", {
      CLIENT_IP
    }
  )

}

# Row Number
tools_row_num_fun <- function(x)
{

  x %>%
    mutate(row_num = seq.int(nrow(.)))

}

# Cap Col Names
tools_col_name_caps <- function(x)
{

  x %>%
    rename_all(
      . %>%
        toupper %>%
        gsub(" ", "_", .)
    )

}


# Remove non-alphanumeric characters from string
tools_strip_nonalpha <- function(col)
{

  str_replace_all(
    {
      col
    }, "[^[:alnum:]]", " "
  )


}

# Separate leading words before first number in string
tools_lead_words_pre_numeric <- function(col)
{

  str_extract(
    {
      col
    }, "\\D+(?= \\d+)"
  )

}


# Elapsed Months
tools_elapsed_months <- function(end_date, start_date)
{

  ed <- as.POSIXlt(end_date)
  sd <- as.POSIXlt(start_date)

  12 * (ed$year - sd$year) + (ed$mon - sd$mon)


}

# totals and percent totals summary table
tools_adorn_totals <- function(x)
{

  x %>%
    adorn_totals(c("row")) %>%
    adorn_percentages("col") %>%
    adorn_pct_formatting(digits = 2) %>%
    adorn_ns()

}

# Collapse / concatenate / aggregate multiple columns to a single comma
# separated string within each group
tools_collapse_comma <- function(x)
{

  x %>%
    summarise_all(~toString(na.omit(.)))

}

# gather - transpose
tools_gather <- function(x)
{

  x %>%
    mutate(across(everything(), ~as.character(.))) %>%
    gather(key = "ATTR", value = "VALUE")

}

# missing values in x are filled with matching values from y
tools_coalesce_join <- function(
  x, y, by = NULL, suffix = c(".x", ".y"),
  join = dplyr::full_join, ...
)
{
  joined <- join(x, y, by = by, suffix = suffix, ...)
  # names of desired output
  cols <- union(
    names(x),
    names(y)
  )

  to_coalesce <- names(joined)[!names(joined) %in%
                                 cols]
  suffix_used <- suffix[ifelse(
    endsWith(to_coalesce, suffix[1]),
    1, 2
  )]
  # remove suffixes and deduplicate
  to_coalesce <- unique(
    substr(
      to_coalesce, 1, nchar(to_coalesce) -
        nchar(suffix_used)
    )
  )

  coalesced <- purrr::map_dfc(
    to_coalesce, ~dplyr::coalesce(
      joined[[paste0(.x, suffix[1])]],
      joined[[paste0(.x, suffix[2])]]
    )
  )
  names(coalesced) <- to_coalesce

  dplyr::bind_cols(joined, coalesced)[cols]
}


# group by every 1000 rows
tools_group_1000 <- function(x)
{

  x %>%
    mutate(group = as.integer(gl(n(), 1000, n())))

}

# split-apply-combine every 1000 rows
tools_split_apply_combine <- function(x, fun)
{

  x %>%
    mutate(group = as.integer(gl(n(), 1000, n()))) %>%
    group_split(group) %>%
    map_dfr(fun)

}


# * Web Scraping ----

# IPinfo - db-ip.com
scrape_ip_scrape_detail <- function(IP)
{

  url <- glue("https://db-ip.com/{IP}")

  download.file(url, destfile = "scrapedpage.html", quiet = TRUE)

  ip <- data.table::data.table(
    X1 = c("IP Address"),
    X2 = c(
      {
        IP
      }
    )
  )

  ipInfo <- read_html("scrapedpage.html") %>%
    html_nodes(
      "body > div:nth-child(7) > div > div:nth-child(2) > div > div.card-body > table"
    ) %>%
    html_table() %>%
    purrr::flatten_df()
  ipInfo2 <- read_html("scrapedpage.html") %>%
    html_nodes(
      "body > div:nth-child(7) > div > div:nth-child(1) > div:nth-child(1) > div > table"
    ) %>%
    html_table() %>%
    purrr::flatten_df()
  ipInfo3 <- read_html("scrapedpage.html") %>%
    html_nodes(
      "body > div:nth-child(7) > div > div:nth-child(1) > div:nth-child(4) > div.card-body > table"
    ) %>%
    html_table() %>%
    purrr::flatten_df() %>%
    gather(X1, X2)

  ipDetail <- rbind(ip, ipInfo3, ipInfo, ipInfo2) %>%
    rename(Attr = X1, Value = X2)

  ipDetail

}

# IPinfo - db-ip.com (formatted wide)
scrape_ip_scrape_detail_wide <- function(IP)
{

  url <- glue("https://db-ip.com/{IP}")

  download.file(url, destfile = "scrapedpage.html", quiet = TRUE)

  ip <- data.table::data.table(
    X1 = c("IP Address"),
    X2 = c(
      {
        IP
      }
    )
  )

  ipInfo <- read_html("scrapedpage.html") %>%
    html_nodes(
      "body > div:nth-child(7) > div > div:nth-child(2) > div > div.card-body > table"
    ) %>%
    html_table() %>%
    purrr::flatten_df()
  ipInfo2 <- read_html("scrapedpage.html") %>%
    html_nodes(
      "body > div:nth-child(7) > div > div:nth-child(1) > div:nth-child(1) > div > table"
    ) %>%
    html_table() %>%
    purrr::flatten_df()
  ipInfo3 <- read_html("scrapedpage.html") %>%
    html_nodes(
      "body > div:nth-child(7) > div > div:nth-child(1) > div:nth-child(4) > div.card-body > table"
    ) %>%
    html_table() %>%
    purrr::flatten_df() %>%
    gather(X1, X2)

  ipDetail <- rbind(ip, ipInfo3, ipInfo, ipInfo2) %>%
    rename(Attr = X1, Value = X2)

  ipDetail %>%
    ungroup() %>%
    mutate(id = c(1)) %>%
    spread(Attr, Value) %>%
    select(
      `IP Address`, City, `District / County`, `State / Region`, Country, Proxy,
      `Attack source`, Crawler, `Address type`, `Connection type`, ISP, ASN,
      Timezone
    )

}

# IPinfo - geolocation.com
scrape_ip_scrape_quick <- function(IP)
{

  url <- glue("https://www.geolocation.com/?ip={IP}#ipresult")

  download.file(url, destfile = "scrapedpage.html", quiet = TRUE)

  ipInfo <- read_html("scrapedpage.html") %>%
    html_nodes("#ipresult > div.panel-body > table") %>%
    html_table()

  ipInfo


}

# IPInfo - whoisxmlapi
scrape_ip_whoISapi <- function(IP)
{

  url <- glue("https://ip-geolocation.whoisxmlapi.com/api/v1?apiKey=xxx={IP}")

  download.file(url, destfile = "scrapedpage.html", quiet = TRUE)

  data <- jsonlite::fromJSON("scrapedpage.html", simplifyDataFrame = T)

  data.frame(
    cbind(
      IP = data$ip, COUNTRY = data$location$country, REGION = data$location$region,
      CITY = data$location$city, POSTAL = data$location$postalCode, TYPE = data$as$type,
      ISP = data$isp, CONNECTION_TYPE = data$connectionType, TIME_ZONE = data$location$timezone,
      LAT = data$location$lat, LNG = data$location$lng, GEONAME_ID = data$location$geonameId,
      DOMAINS = data$domain, ASN = data$as$asn, NAME = data$as$name, ROUTE = data$as$route,
      DOMAIN = data$as$domain
    ),
    stringsAsFactors = F
  ) %>%
    gather()

}



# Email Reputation - emailrep.io
scrape_email_rep <- function(Email)
{

  url <- glue("https://emailrep.io/{Email}")

  download.file(url, destfile = "scrapedpage.html", quiet = TRUE)

  data <- jsonlite::fromJSON("scrapedpage.html")

  emailRep <- data.frame(
    cbind(
      email = data$email, reputation = data$reputation, suspicious = data$suspicious,
      references = data$references, blacklisted = data$details$blacklisted,
      malicious_activity = data$details$malicious_activity, malicious_activity_recent = data$details$malicious_activity_recent,
      credentials_leaked = data$details$credentials_leaked, credentials_leaked_recent = data$details$credentials_leaked_recent,
      data_breach = data$details$data_breach, first_seen = data$details$first_seen,
      last_seen = data$details$last_seen, domain_exists = data$details$domain_exists,
      domain_reputation = data$details$domain_reputation, details_new_domain = data$details$new_domain,
      days_since_domain_creation = data$details$days_since_domain_creation,
      suspicious_tld = data$details$suspicious_tld, spam = data$details$spam,
      free_provider = data$details$free_provider, disposable = data$details$disposable,
      deliverable = data$details$deliverable, accept_all = data$details$accept_all,
      valid_mx = data$details$valid_mx, spoofable = data$details$spoofable,
      spf_strict = data$details$spf_strict, dmarc_enforced = data$details$dmarc_enforced
    ),
    stringsAsFactors = F
  ) %>%
    gather()

  emailRep

}



# Bulk IP Lookup - ipapi.co https://app.ipapi.co/bulk/
scrape_bulk_ip <- function(path)
{

  d1 <- c(
    {
      path
    }
  )

  data <- readr::read_csv(
    d1, col_types = cols(
      continent_code = col_skip(), country_area = col_skip(), country_calling_code = col_skip(),
      country_capital = col_skip(), country_code = col_skip(), country_code_iso3 = col_skip(),
      country_name = col_skip(), country_population = col_skip(), country_tld = col_skip(),
      currency = col_skip(), currency_name = col_skip(), in_eu = col_skip(),
      languages = col_skip(), latitude = col_skip(), longitude = col_skip(),
      message = col_skip(), postal = col_skip(), utc_offset = col_skip()
    )
  ) %>%
    select(ip, city, region, region_code, country, timezone, asn, org) %>%
    unique()

  colnames(data) <- c(
    "IP_ADDRESS", "IP_CITY", "IP_STATE", "IP_STATE_ABBR", "IP_COUNTRY", "IP_TIMEZONE",
    "IP_ASN", "IP_ISP"
  )

  data

}

# * Visualization ----

# dt datatable - export buttons, scroll Y, filters
viz_dt_datatable <- function(df)
{

  data <- data.frame(
    lapply(
      {
        df
      }, as.character
    )
  )

  DT::datatable(
    data, extensions = c("Buttons", "Scroller", "Responsive"),
    rownames = F, escape = F, filter = "bottom", options = list(
      columnDefs = list(list(className = "dt-center", targets = c(0:0))),
      scroller = TRUE, deferRender = TRUE, scrollY = 500, dom = "Bfrtip", buttons = c("excel", "csv"),
      initComplete = JS(
        "function(settings, json) {", "$(this.api().table().header()).css({'background-color': '#14141f', 'color': '#fff'});",
        "}"
      )
    ),
    fillContainer = T, class = "display"
  )

}
