const page_section_id = "#metadata-recom-page";

// input elements for filters
const $top_n_input = document.querySelector(`${page_section_id} #top-n-input`);
const $top_n_label = document.querySelector(`${page_section_id} #top-n-label`);

const $published_date_input = document.querySelector(
  `${page_section_id} #published-date-input`
);
const $genre_input = document.querySelector(
  `${page_section_id} #top-genre-select`
);
const $duration_input = document.querySelector(
  `${page_section_id} #duration-select`
);

// form and its elements
const $form = document.querySelector(`${page_section_id} form`);
const $searched_movie_input = document.querySelector(
  `${page_section_id} #search-movie-input`
);

const $output_message_element = document.querySelector(
  `${page_section_id} #output-message`
);

// error messages
const filter_error_message =
  "Please provide valid filters to filter out recommended movies";
const genre_error_message = "Please provide valid genre to show you top movies";

// Variables required for slider
var slider = document.getElementById("top-n-input");
var output = document.getElementById("top-n-label");
output.innerHTML = slider.value;

// Changes on input to view the intial values
slider.oninput = function () {
  output.innerHTML = this.value;
};

// Checks the filter's value validity
function checkFilters() {
  // take all input values
  const top_n_value = $top_n_input.value;
  const published_date_filter = $published_date_input.value;
  const duration_filter = $duration_input.value;

  if (!top_n_value || !published_date_filter) {
    // either of them are not given
    return false; // invalid
  }

  if (top_n_value?.trim() !== "") {
    const top_n_int = parseInt(top_n_value);

    if (top_n_int < 1 || top_n_int > 20) {
      return false; // invalid
    }
  }

  const published_timeframes = ["Relevant", "Newest", "Mid", "Oldest"];
  if (!published_timeframes.includes(published_date_filter?.trim())) {
    return false; // invalid
  }

  const duration_filters_list = [
    "no-filter",
    "<100 Minutes",
    "100-200 Minutes",
    "200+ Minutes",
  ];
  if (!duration_filters_list.includes(duration_filter?.trim())) {
    return false; // invalid
  }

  return true; // all are valid params
}

// Inserts filter's name and value to form as a hidden input element
function insertFiltersToForm(element_name, element_value) {
  const $element = document.createElement("input");
  $element.type = "hidden"; // keep the element hidden
  $element.value = element_value;
  $element.name = element_name;
  $form.appendChild($element);
}

// Adds the filters to the form
function addFilterParamsToForm(genre_value = null) {
  const top_n_value = $top_n_input.value;
  const published_date_filter = $published_date_input.value;
  const duration_filter = $duration_input.value;

  insertFiltersToForm("top-n", parseInt(top_n_value));
  insertFiltersToForm("published-date-filter", published_date_filter);
  insertFiltersToForm("duration-filter", duration_filter);

  if (!!genre_value) {
    // if genre is inputted, then insert that to form
    insertFiltersToForm("genre-filter", genre_value);
  }
}

// Checks filter's values, adds filter's values to form, and
function inputChangeSubmitForm() {
  if (checkFilters()) {
    // if filter's values are correct, then check the form inputs

    // trim the input values if the value actually supports trimming (and not null or undefined)
    const searched_movie_value = $searched_movie_input.value?.trim();
    const genre_value = $genre_input.value?.trim();

    if (genre_value != "" && searched_movie_value != "") {
      // both are entered, then raise error message
      $output_message_element.textContent =
        "Either provide valid genre or search a movie, and not both";
      return false; // this means that form was not submitted properly
    }

    if (searched_movie_value != "") {
      // only movie is entered
      $output_message_element.textContent = "";
      addFilterParamsToForm();
      $form.requestSubmit();
      return true; // this means that form was submitted properly
    }

    // if no movie input, then check genre
    const genres_list = [
      "Comedy",
      "Animation",
      "Romance",
      "Crime",
      "Fantasy",
      "Horror",
      "Family",
      "Adventure",
      "Drama",
      "Thriller",
      "History",
      "Science Fiction",
      "Action",
      "War",
      "Mystery",
      "Foreign",
      "Music",
      "Documentary",
    ];

    // if genre is inputted correctly, then add all filters and recommend top movies of that genre
    if (genre_value != "" && genres_list.includes(genre_value)) {
      // only genre is entered
      $output_message_element.textContent = "";
      addFilterParamsToForm(genre_value);
      $form.requestSubmit();
      return true;
    } else {
      // neither movie nor genre is entered
      $output_message_element.textContent = genre_error_message;
      return false;
    }
  } else {
    $output_message_element.textContent = filter_error_message;
    return false;
  }
}

// on form submit, add all filters parameter to form and submit it
$form.onsubmit = (e) => {
  const form_submitted_properly = inputChangeSubmitForm();

  if (form_submitted_properly == false) {
    // if form was not submitted properly, then prevent default form submission
    e.preventDefault();
  }
};

$top_n_label.innerHTML = $top_n_input.value; // initialising label with default value of input slider of top n

// event fired when enter key is pressed or the element's focus is removed
$top_n_input.onchange = (e) => {
  $top_n_label.innerHTML = e.target.value; // changing label value with slider input changed value
  inputChangeSubmitForm();
};

$published_date_input.onchange = () => {
  inputChangeSubmitForm();
};

$genre_input.onchange = () => {
  inputChangeSubmitForm();
};

$duration_input.onchange = () => {
  inputChangeSubmitForm();
};
