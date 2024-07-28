#' 'quak' 'htmlwidget'
#'
#' <Add Description>
#'
#' @export
quak <- function(dat, width = "100%", height = NULL, elementId = NULL) {
  # save data as parquet in temporary location
  data_file <- tempfile(fileext = ".parquet")

  nanoparquet::write_parquet(dat, data_file)

  nm = deparse(substitute(dat))

  dep_data <- htmltools::htmlDependency(
    name = nm,
    version = "1",
    src = c(file = dirname(data_file)),
    attachment = basename(data_file),
    all_files = FALSE
  )

  # create widget
  htmlwidgets::createWidget(
    name = 'quak',
    list(name = nm),
    width = width,
    height = height,
    package = 'quak',
    elementId = elementId,
    dependencies = dep_data
  )
}

#' Shiny bindings for quak
#'
#' Output and render functions for using quak within Shiny
#' applications and interactive Rmd documents.
#'
#' @param outputId output variable to read from
#' @param width,height Must be a valid CSS unit (like \code{'100\%'},
#'   \code{'400px'}, \code{'auto'}) or a number, which will be coerced to a
#'   string and have \code{'px'} appended.
#' @param expr An expression that generates a quak
#' @param env The environment in which to evaluate \code{expr}.
#' @param quoted Is \code{expr} a quoted expression (with \code{quote()})? This
#'   is useful if you want to save an expression in a variable.
#'
#' @name quak-shiny
#'
#' @export
quakOutput <- function(outputId, width = '100%', height = '400px'){
  htmlwidgets::shinyWidgetOutput(outputId, 'quak', width, height, package = 'quak')
}

#' @rdname quak-shiny
#' @export
renderQuak <- function(expr, env = parent.frame(), quoted = FALSE) {
  if (!quoted) { expr <- substitute(expr) } # force quoted
  htmlwidgets::shinyRenderWidget(expr, quakOutput, env, quoted = TRUE)
}
