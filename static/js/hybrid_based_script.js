const page_section_id = "#hybrid-recom-page";

// form of the get request method
const $form = document.querySelector(`${page_section_id} #hybrid-recom-form`);

// input elements for filters in the get request form
const $top_n_input = document.querySelector(`${page_section_id} #top-n-input`);
const $top_n_label = document.querySelector(`${page_section_id} #top-n-label`);

const $published_date_input = document.querySelector(
  `${page_section_id} #published-date-input`
);
const $duration_input = document.querySelector(
  `${page_section_id} #duration-select`
);

const $output_message_element = document.querySelector(
  `${page_section_id} #output-message`
);

// error messages
const filter_error_message = "Please provide valid filters to filter out recommended movies";

// Variables required for slider
var slider = document.getElementById("top-n-input");
var output = document.getElementById("top-n-label");
output.innerHTML = slider.value;

// Function to open/close the account popup
function viewAccountPopUp() {
  if(document.getElementById("accountPopUp").style.display == "flex")
    document.getElementById("accountPopUp").style.display = "none";
  else
    document.getElementById("accountPopUp").style.display = "flex";
}

// Function to animate the 'Get Recommendations' button
document.getElementById("getrecom").onmouseover = function() {hoverIn()};
document.getElementById("getrecom").onmouseout = function() {hoverOut()};

function hoverIn(img_name, img_src) {
  document.getElementById("getrecom").src = "/static/images/GetRecom.gif";
}

function hoverOut(img_name, img_src) {
  document.getElementById("getrecom").src = "/static/images/GetRecom.png";
}

// Changes on input to view the initial values
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

// Checks filter's values, adds filter's values to form and submits form
function inputChangeSubmitForm() {
  if (checkFilters()) { // if filter's values are correct
    $output_message_element.textContent = "";

    insertFiltersToForm("list-movies", true); // this is added so that the form submit indication is sent to backend as the form has method: get request
    $form.requestSubmit();
    return true; // the form is submitted successfully
  } else {
    $output_message_element.textContent = filter_error_message;
    return false; // some error occurred, so prevent default form submission also
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

$duration_input.onchange = () => {
  inputChangeSubmitForm();
};
